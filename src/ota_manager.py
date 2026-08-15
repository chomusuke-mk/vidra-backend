"""OTA Hot-Reload Engine for Vidra.

Manages the dynamic loading and unloading of yt-dlp and yt-dlp-ejs
from a fixed directory (temp/yt-dlp/current) using sys.path injection
and snapshot-based module eviction.

Assumptions:
- snapshot() MUST be called before any load/unload. Error otherwise.
- load() assumes packages in current_dir are correct and won't fail.
- The critical path is load → unload → load (dirty environment).
- The calling app replaces the current_dir contents before calling load.
- The path to current_dir never changes.
"""

from __future__ import annotations

import gc
import importlib
import linecache
import os
import re
import sys
import threading
from typing import Any, Literal


class OTAManager:
    """Manages runtime loading and unloading of yt-dlp & yt-dlp-ejs."""

    def __init__(self, ota_path: str) -> None:
        self._lock = threading.RLock()
        self._status: Literal["preparing", "load", "unload"] = "preparing"

        # Snapshot state
        self._snapshot_modules: set[str] = set()
        self._snapshot_meta_path: list[Any] = []
        self._has_snapshot: bool = False

        self.ota_path = ota_path

    # ─── Snapshot ───────────────────────────────────────────────────────

    def snapshot(self) -> None:
        """Captures the clean baseline state of sys.modules and sys.meta_path.

        MUST be called once before any load() or unload().
        """
        with self._lock:
            self._snapshot_modules = set(sys.modules.keys())
            self._snapshot_meta_path = list(sys.meta_path)
            self._has_snapshot = True
            self._status = "unload"
            print(f"OTA snapshot captured: {len(self._snapshot_modules)} modules.")

    def _require_snapshot(self) -> None:
        """Raises RuntimeError if snapshot() has not been called."""
        if not self._has_snapshot:
            raise RuntimeError(
                "OTAManager.snapshot() must be called before load/unload. "
                "This is a programming error."
            )

    # ─── Status ─────────────────────────────────────────────────────────

    def get_status(self):
        """Returns 'load' or 'unload'."""
        with self._lock:
            return self._status

    # ─── Load ───────────────────────────────────────────────────────────

    def load(self) -> bool:
        """Loads yt-dlp and yt-dlp-ejs from current_dir via sys.path injection.

        Assumes the packages exist and are correct in current_dir.
        Returns True on success, False if packages are missing.
        """
        with self._lock:
            self._require_snapshot()

            if self._status == "load":
                print("OTA already loaded, skipping.")
                return True

            # Inject current_dir at the beginning of sys.path
            if self.ota_path in sys.path:
                sys.path.remove(self.ota_path)
            sys.path.insert(0, self.ota_path)

            # Verify packages exist on disk
            has_ydl = os.path.isdir(os.path.join(self.ota_path, "yt_dlp"))
            has_ejs = os.path.isdir(os.path.join(self.ota_path, "yt_dlp_ejs"))
            if not (has_ydl and has_ejs):
                print(f"yt_dlp or yt_dlp_ejs not found in {self.ota_path}")
                # Remove the path we just added
                if self.ota_path in sys.path:
                    sys.path.remove(self.ota_path)
                return False

            importlib.invalidate_caches()

            self._status = "load"
            print("OTA load succeeded.")
            return True

    # ─── Unload ─────────────────────────────────────────────────────────

    @staticmethod
    def _is_ota_module(mod_name: str) -> bool:
        """Checks if a module name belongs to the OTA packages."""
        ota_roots = ("yt_dlp", "yt_dlp_ejs", "yt_dlp_plugins", "ytdlp_plugins")
        for root in ota_roots:
            if mod_name == root or mod_name.startswith(f"{root}."):
                return True
        return False

    def unload(self) -> bool:
        """Evicts yt-dlp and yt-dlp-ejs from memory using snapshot diff.

        Returns True always (idempotent — returns True if already unloaded).
        """
        with self._lock:
            self._require_snapshot()

            if self._status == "unload":
                return True

            # ── 1. Identify modules to remove ──────────────────────────
            # Hybrid: snapshot diff filtered by OTA name or file path.
            # Protects stdlib/server modules lazily imported after snapshot.
            current_keys = set(sys.modules.keys())
            new_keys = current_keys - self._snapshot_modules

            modules_to_clear = []
            for mod_name in new_keys:
                mod = sys.modules.get(mod_name)

                should_evict = self._is_ota_module(mod_name)

                if not should_evict and mod is not None:
                    mod_file = getattr(mod, "__file__", None) or ""
                    if mod_file.startswith(self.ota_path):
                        should_evict = True

                if should_evict:
                    popped = sys.modules.pop(mod_name, None)
                    if popped is not None:
                        modules_to_clear.append(popped)

            # ── 2. Break references in evicted modules ─────────────────
            for mod in modules_to_clear:
                try:
                    mod.__dict__.clear()
                except Exception:
                    print(f"Failed to clear module {mod.__name__} __dict__")
            del modules_to_clear

            # ── 3. Restore sys.meta_path from snapshot ─────────────────
            sys.meta_path[:] = list(self._snapshot_meta_path)

            # ── 4. Remove current_dir from sys.path ────────────────────
            while self.ota_path in sys.path:
                sys.path.remove(self.ota_path)

            # ── 5. Clear Python internal caches ────────────────────────
            # Regex cache (yt-dlp compiles hundreds of patterns)
            re.purge()

            # Source line cache (used by inspect/tracebacks)
            linecache.clearcache()

            # Selectively clear path importer cache for OTA dir
            for p in list(sys.path_importer_cache.keys()):
                if p.startswith(self.ota_path):
                    del sys.path_importer_cache[p]

            # Importlib caches
            importlib.invalidate_caches()

            # ── 6. Garbage collection (3 generations) ──────────────────
            gc.collect(0)
            gc.collect(1)
            gc.collect(2)

            self._status = "unload"
            print("OTA unload complete.")
            return True
