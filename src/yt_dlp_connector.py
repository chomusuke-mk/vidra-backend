"""High-level integration layer around yt_dlp consumption.

This module centralices every direct call to :mod:`yt_dlp` so the rest of the
codebase can rely on a stable, application-tailored contract.  All functions in
this module accept plain dictionaries/lists and optional hooks so callers can
re-use their existing handlers without dealing with yt-dlp specific details.
"""

from typing import (
    Optional,
    Callable,
    Any,
    Dict,
)
from logging import Logger
import time
from utils import (
    to_int,
    to_float,
    bytes_to_human_readable,
    get_logs_messages,
    seconds_to_human_readable,
)
from threading import Lock, Event
from yt_dlp_parser import options_parser
from yt_dlp_parser_types import VidraOptions
from descarga_hija import Descarga_Hija_dict
from tipos import State, Info, YTDLPLoggerAdapter
import os
import tldextract
from pathlib import Path
from collections.abc import Iterable


class YTDLPConnector:
    """
    set_state, set_info  deben ser thread-safe
    """

    def __init__(
        self,
        id: str,
        options: VidraOptions,
        logger: Logger,
        info: Info,
        state: State,
        set_state: Callable[[State, Optional[str]], None],
        set_info: Callable[[Info, Optional[str]], None],
        sub_descargas: Iterable[Descarga_Hija_dict],
        set_entries_to_select: Callable[[Iterable[Descarga_Hija_dict]], None],
        get_selected_entry_ids: Callable[[], Iterable[str]],
        select_entries_event: Event,
        handle_requests: Callable[[], None],
        get_logs: Callable[[], str],
    ):
        self.id = id
        self.options = options
        self.logger = logger
        self._set_state = set_state
        self._set_info = set_info
        self._set_entries_to_select = set_entries_to_select
        self.get_selected_entry_ids = get_selected_entry_ids
        self.event = select_entries_event
        self.handle_requests = handle_requests
        self.get_logs = get_logs

        self.state: Dict[Optional[str], State] = {None: state.copy()}
        self.info: Dict[Optional[str], Info] = {None: info.copy()}

        self.time_start: Dict[Optional[str], float] = {None: time.time()}

        self.state_lock: Dict[Optional[str], Lock] = {None: Lock()}
        self.info_lock: Dict[Optional[str], Lock] = {None: Lock()}

        self._m_state_lock = Lock()
        self._m_info_lock = Lock()

        for d in sub_descargas:
            sub_id = d["sub_id"]
            self.state[sub_id] = d["state"].copy()
            self.info[sub_id] = d["info"].copy()
            self.state_lock[sub_id] = Lock()
            self.info_lock[sub_id] = Lock()

    def emit_state(self, sub_id: Optional[str] = None):
        self._set_state(self.state[sub_id], sub_id)

    def emit_info(self, sub_id: Optional[str] = None):
        self._set_info(self.info[sub_id], sub_id)

    def _assert_state(self, sub_id: Optional[str]):
        with self._m_state_lock:
            if sub_id not in self.state_lock:
                self.state_lock[sub_id] = Lock()
            if sub_id not in self.state:
                self.state[sub_id] = {"value": "pending"}

    def _assert_info(self, sub_id: Optional[str]):
        with self._m_info_lock:
            if sub_id not in self.info_lock:
                self.info_lock[sub_id] = Lock()
            if sub_id not in self.info:
                self.info[sub_id] = {
                    "url": None,
                    "image": None,
                    "file": None,
                    "title": None,
                    "platform": None,
                    "type": "video",
                    "autor": None,
                    "creation_date": None,
                    "duration": None,
                }

    def _info_hook(
        self, d: Any, sub_id: Optional[str], emit=True, handle=True, is_first=False
    ):
        # d es el info_json tanto de progress_hook como de postprocessor_hook
        # completa solo la información faltante
        if handle:
            self.handle_requests()
        if not isinstance(d, dict):
            return
        self._assert_info(sub_id)
        with self.info_lock[sub_id]:
            any_change = False
            if (self.info[sub_id]["url"] is None or is_first) and (
                (d.get("url") and isinstance(d.get("url"), str))
                or (d.get("webpage_url") and isinstance(d.get("webpage_url"), str))
            ):
                self.info[sub_id]["url"] = (
                    d.get("url")
                    if d.get("url") and isinstance(d["url"], str)
                    else d.get("webpage_url")
                )
                any_change = True
            if self.info[sub_id]["image"] is None:
                thumbnail = d.get("thumbnail", d.get("thumbnails", [{}])[-1].get("url"))
                if thumbnail and isinstance(thumbnail, str):
                    self.info[sub_id]["image"] = thumbnail
                    any_change = True
            if (
                self.info[sub_id]["file"] is None
                and d.get("filename")
                and isinstance(d["filename"], str)
            ):
                self.info[sub_id]["file"] = os.path.basename(d["filename"])
                any_change = True
            if (
                self.info[sub_id]["title"] is None
                and d.get("title")
                and isinstance(d["title"], str)
            ):
                self.info[sub_id]["title"] = d["title"]
                any_change = True
            if self.info[sub_id]["platform"] is None and self.info[sub_id]["url"]:
                self.info[sub_id]["platform"] = tldextract.extract(
                    self.info[sub_id]["url"] or ""
                ).domain
                any_change = True
            if self.info[sub_id]["type"] == "unknown":
                media_type = str(d.get("media_type", d.get("_type"))).lower()
                if isinstance(d.get("entries"), Iterable):
                    self.info[sub_id]["type"] = "list"
                    any_change = True
                elif media_type in [
                    "video",
                    "audio",
                    "short",
                    "livestream",
                    "clip",
                    "episode",
                    "segment",
                    "movie",
                    "sound",
                    "live",
                    "track",
                ]:
                    self.info[sub_id]["type"] = "video"
                    any_change = True
            if (
                self.info[sub_id]["autor"] is None
                and d.get("uploader")
                and isinstance(d["uploader"], str)
            ):
                self.info[sub_id]["autor"] = d["uploader"]
                any_change = True
            if (
                self.info[sub_id]["creation_date"] is None
                and d.get("timestamp")
                and isinstance(d["timestamp"], int)
            ):
                self.info[sub_id]["creation_date"] = time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(d["timestamp"])
                )
                any_change = True
            if (
                self.info[sub_id]["duration"] is None
                and d.get("duration")
                and isinstance(d["duration"], (int, float))
            ):
                self.info[sub_id]["duration"] = seconds_to_human_readable(d["duration"])
                any_change = True
            if any_change and emit:
                self.emit_info(sub_id)

    def _progress_hook(self, d: Any, emit=True, handle=True):
        if handle:
            self.handle_requests()
        if (
            not isinstance(d, dict)
            or "info_dict" not in d
            or not isinstance(d["info_dict"], dict)
            or "status" not in d
            or not isinstance(d["status"], str)
            or d["status"] not in ["downloading", "finished", "error"]
        ):
            return

        sub_id = (
            d["info_dict"].get("id")
            if d["info_dict"].get("playlist_index") is not None
            else None
        )
        self._info_hook(d["info_dict"], sub_id, emit=emit, handle=handle)
        self._assert_state(sub_id)

        time_spent = time.time() - self.time_start.setdefault(sub_id, time.time())
        if d["status"] == "downloading" or d["status"] == "finished":
            downloaded_bytes = to_int(d.get("downloaded_bytes"))
            downloaded_bytes_str = bytes_to_human_readable(downloaded_bytes)
            total_bytes = to_int(d.get("total_bytes", d.get("total_bytes_estimate")))
            total_bytes_str = bytes_to_human_readable(total_bytes)
            speed = to_float(d.get("speed"))
            eta = to_float(d.get("eta"))
            speed_str = bytes_to_human_readable(speed, suffix="/s")

            with self.state_lock[sub_id]:
                self.state[sub_id]["value"] = "in_progress"
                self.state[sub_id]["progress_label"] = (
                    f"{downloaded_bytes_str}/{total_bytes_str}"
                )
                self.state[sub_id]["progress_value"] = (
                    (downloaded_bytes / total_bytes)
                    if downloaded_bytes is not None
                    and total_bytes is not None
                    and total_bytes > 0
                    else None
                )
                self.state[sub_id]["progress_color"] = "blue"
                self.state[sub_id]["speed"] = speed_str if speed is not None else None
                self.state[sub_id]["time_spent"] = time.strftime(
                    "%H:%M:%S", time.gmtime(time_spent)
                )
                self.state[sub_id]["time_total"] = time.strftime(
                    "%H:%M:%S",
                    time.gmtime(time_spent + (eta if eta is not None else 0)),
                )
                self.state[sub_id]["time_left"] = (
                    time.strftime("%H:%M:%S", time.gmtime(eta))
                    if eta is not None
                    else None
                )
                if emit:
                    self.emit_state(sub_id)
        elif d["status"] == "error":
            with self.state_lock[sub_id]:
                self.state[sub_id]["value"] = "failed"
                self.state[sub_id]["progress_color"] = "red"
                self.state[sub_id]["sub_state_color"] = "red"
                if emit:
                    self.emit_state(sub_id)

    def _postprocessor_hook(self, d: Any, emit=True, handle=True):
        if handle:
            self.handle_requests()
        if (
            not isinstance(d, dict)
            or "info_dict" not in d
            or not isinstance(d["info_dict"], dict)
            or "status" not in d
            or not isinstance(d["status"], str)
            or d["status"] not in ["started", "finished"]
        ):
            return
        sub_id = (
            d["info_dict"].get("id")
            if d["info_dict"].get("playlist_index") is not None
            else None
        )
        self._info_hook(d["info_dict"], sub_id, emit=emit, handle=handle)
        self._assert_state(sub_id)

        with self.state_lock[sub_id]:
            self.state[sub_id] = {
                "value": "in_progress",
                "sub_state": d.get("postprocessor", ""),
            }
            self.time_start.setdefault(sub_id, time.time())
            if emit:
                self.emit_state(sub_id)

    def _post_hook(self, filepath: Optional[str]):
        if not filepath:
            return
        file = Path(filepath).stem
        with self._m_state_lock:
            state_snapshot = self.state.copy()
        with self._m_info_lock:
            info_snapshot = self.info.copy()
        if self.info[None]["type"] == "list":
            # completar el estado a completed del sub_id cuyo file sea filepath
            for sub_id, state in state_snapshot.items():
                if (
                    sub_id is not None
                    and state["value"] == "in_progress"
                    and sub_id in info_snapshot
                    and info_snapshot[sub_id].get("file")
                ):
                    current_file = Path(info_snapshot[sub_id]["file"] or "").stem
                    if current_file == file:
                        self._mark_as_completed(sub_id, filepath)
        elif self.info[None]["type"] == "video":
            self._mark_as_completed(None, filepath)

    def _mark_as_completed(self, sub_id: Optional[str], filepath: Optional[str]):
        self._assert_state(sub_id)
        self._assert_info(sub_id)
        time_spent = time.time() - self.time_start.setdefault(sub_id, time.time())
        if filepath:
            with self.info_lock[sub_id]:
                self.info[sub_id]["file"] = os.path.abspath(filepath)
                self.emit_info(sub_id)
        with self.state_lock[sub_id]:
            self.state[sub_id]["value"] = "completed"
            self.state[sub_id]["progress_value"] = 1.0
            self.state[sub_id]["progress_color"] = "green"
            self.state[sub_id]["sub_state"] = ""
            self.state[sub_id]["sub_state_color"] = "green"
            self.state[sub_id]["error_message"] = ""
            self.state[sub_id]["time_left"] = "00:00:00"
            self.state[sub_id]["time_total"] = time.strftime(
                "%H:%M:%S", time.gmtime(time_spent)
            )
            self.emit_state(sub_id)
        if self.info[None]["type"] == "list":
            with self._m_state_lock:
                state_snapshot = self.state.copy()
            time_spent = time.time() - self.time_start.setdefault(None, time.time())
            completed_count = sum(
                1
                for other_sub_id, state in state_snapshot.items()
                if state["value"] == "completed" and other_sub_id is not None
            )
            total_count = sum(
                1
                for other_sub_id, state in state_snapshot.items()
                if state["value"] != "requested" and other_sub_id is not None
            )
            self.state[None]["progress_label"] = f"{completed_count}/{total_count}"
            self.state[None]["progress_value"] = (
                (completed_count / total_count) if total_count > 0 else None
            )
            self.state[None]["time_spent"] = time.strftime(
                "%H:%M:%S", time.gmtime(time_spent)
            )
            # cantidad de elementos por segundo
            self.state[None]["speed"] = (
                f"{(completed_count / time_spent):.2f}e/s" if time_spent > 0 else None
            )
            self.state[None]["time_total"] = (
                time.strftime(
                    "%H:%M:%S", time.gmtime(time_spent * total_count / completed_count)
                )
                if completed_count > 0
                else None
            )
            self.state[None]["time_left"] = (
                time.strftime(
                    "%H:%M:%S",
                    time.gmtime(
                        time_spent * (total_count - completed_count) / completed_count
                    ),
                )
                if completed_count > 0
                else None
            )
            if sub_id is None:
                is_completed = completed_count == total_count and total_count > 0
                self.state[None]["value"] = (
                    "completed" if is_completed else "completed_with_errors"
                )
                self.state[None]["sub_state"] = ""
                self.state[None]["sub_state_color"] = (
                    "green" if is_completed else "orange"
                )
                self.state[None]["error_message"] = ""
                self.state[None]["progress_color"] = (
                    "green" if is_completed else "orange"
                )
                self.state[None]["time_left"] = "00:00:00"
            self.emit_state(None)

    def _get_last_log_error(self, id: Optional[str]) -> Optional[str]:
        message = "Unknown error"
        for msg in get_logs_messages(self.get_logs(), level="ERROR"):
            if id is None or id in msg:
                message = msg
        return message

    def _mark_as_failed(self, sub_id: Optional[str]):
        self._assert_state(sub_id)
        with self.state_lock[sub_id]:
            self.state[sub_id]["value"] = "failed"
            self.state[sub_id]["progress_color"] = "red"
            self.state[sub_id]["time_left"] = None
            self.state[sub_id]["time_total"] = None
            self.state[sub_id]["speed"] = None
            self.state[sub_id]["sub_state_color"] = "red"
            self.state[sub_id]["sub_state"] = None
            self.state[sub_id]["error_message"] = self._get_last_log_error(sub_id)
            self.emit_state(sub_id)

    def download(self, url: Optional[str]):
        if not url:
            raise ValueError("URL is required for download")
        # Lazy import to reduce startup time
        from yt_dlp import YoutubeDL, parse_options

        # Obtener información ================================================================
        if self.info[None]["type"] == "unknown":
            self.logger.info(f"Extracting information for {url}")
            command = options_parser(self.options)
            self.logger.info(f"YDL options: {command}")
            parsed = parse_options(command)
            ydl_opts = parsed.ydl_opts
            ydl_opts["logger"] = YTDLPLoggerAdapter(logger=self.logger)
            ydl_opts["progress_hooks"] = []
            ydl_opts["postprocessor_hooks"] = []
            ydl_opts["post_hooks"] = []
            self._assert_state(None)
            self.state[None]["value"] = "extracting_information"
            self.state[None]["sub_state"] = "Extracting Information"
            self.state[None]["sub_state_color"] = "cyan"
            self.state[None]["progress_color"] = "cyan"
            self.emit_state()
            with YoutubeDL(ydl_opts) as ytdlp:
                info = ytdlp.extract_info(url, download=False, process=False)
                if not isinstance(info, dict):
                    self._mark_as_failed(None)
                    raise ValueError("Failed to extract information")
                self.info[None]["type"] = "unknown"
                self._info_hook(info, None, handle=False, is_first=True)
                # Inferencia adicional del tipo------------
                if self.info[None]["type"] == "unknown":
                    if self.info[None]["url"] != url:
                        self.logger.info("Reintentando extracción de información...")
                        url = self.info[None]["url"] or url
                        info = ytdlp.extract_info(url, download=False, process=False)
                        self._info_hook(info, None, handle=False, is_first=True)
                    if self.info[None]["type"] == "unknown":
                        self.info[None]["type"] = "video"
                # Procesar entradas -------------------------------------------
                entries: Iterable = []
                if self.info[None]["type"] == "list":
                    if "entries" in info and isinstance(info["entries"], Iterable):
                        entries = info["entries"]
                        self.state[None]["sub_state"] = "Collecting Entries"
                    else:
                        self._mark_as_failed(None)
                        raise ValueError("Failed to extract entries from playlist")
                total = to_int(info.get("playlist_count"))
                for index, entry in enumerate(entries):
                    if (
                        not isinstance(entry, dict)
                        or not entry.get("id")
                        or not isinstance(entry["id"], str)
                        or entry["id"] in self.state
                    ):
                        total = total - 1 if total is not None and total > 0 else None
                    else:
                        self._info_hook(entry, entry["id"], emit=False, handle=False)
                        self._assert_state(entry["id"])
                        self.state[entry["id"]]["value"] = "requested"

                    self.state[None]["progress_label"] = (
                        f"{index + 1}/{total if total is not None else '?'}"
                    )
                    self.state[None]["progress_value"] = (
                        (index + 1) / total if total is not None and total > 0 else None
                    )
                    self.emit_state()
        # Manejar selección de entradas ======================================================
        selected_ids: Iterable[str]
        if sum(1 for v in self.state.values() if v["value"] != "completed") > 2:
            # Si hay más de 2 elementos en values (1 es root), esperar a que el usuario seleccione cuáles descargar
            self._set_entries_to_select(
                [
                    {
                        "sub_id": entry_id,
                        "parent_id": self.id,
                        "info": self.info[entry_id],
                        "state": self.state[entry_id],
                    }
                    for entry_id in self.state.keys()
                    if entry_id is not None
                    and self.state[entry_id]["value"] != "completed"
                ]
            )
            self.logger.info(f"Waiting for user selection of entries for {url}")
            self.state[None]["value"] = "awaiting_selection"
            self.state[None]["sub_state"] = "Waiting for Selection"
            self.state[None]["sub_state_color"] = "purple"
            self.state[None]["progress_color"] = "purple"
            self.emit_state()
            # Esperar a que el usuario seleccione las entradas a descargar
            self.event.wait()
            # Obtener las entradas seleccionadas
            self.handle_requests()
            selected_ids = [
                entry_id
                for entry_id in self.state.keys()
                if entry_id is not None and entry_id in self.get_selected_entry_ids()
            ]
            self.state[None]["value"] = "extracting_information"
            self.emit_state()
        else:
            selected_ids = [
                entry_id
                for entry_id in self.state.keys()
                if entry_id is not None and self.state[entry_id]["value"] != "completed"
            ]

        total_matched = len(selected_ids)
        if selected_ids:
            # Emitir las entradas seleccionadas
            for id in selected_ids:
                self._assert_state(id)
                self._assert_info(id)
                self.state[id]["value"] = "pending"
                self.emit_state(id)
                self.emit_info(id)
            self.options["playlist_ids"] = selected_ids
            download_archive = self.options.get("download_archive")
            if not download_archive:
                temp_path = self.options.get("paths", {}).get("temp") or ""
                self.options["download_archive"] = os.path.join(
                    temp_path, f"{self.id}_download_archive.txt"
                )
            self.state[None]["progress_label"] = f"0/{total_matched}"
            self.state[None]["progress_value"] = 0.0 if total_matched > 0 else None
            self.emit_state()

        # Descargar ==========================================================================
        self.options["playlist"] = True if self.info[None]["type"] == "list" else False
        command = options_parser(self.options)
        parsed = parse_options(command)
        ydl_opts = parsed.ydl_opts
        ydl_opts["logger"] = YTDLPLoggerAdapter(logger=self.logger)
        ydl_opts["progress_hooks"] = [self._progress_hook]
        ydl_opts["postprocessor_hooks"] = [self._postprocessor_hook]
        ydl_opts["post_hooks"] = [self._post_hook]
        with YoutubeDL(ydl_opts) as ytdlp:
            self.logger.info(f"Starting download of {url}")
            self.state[None]["value"] = "in_progress"
            self.state[None]["sub_state"] = "Downloading"
            self.state[None]["sub_state_color"] = "blue"
            self.state[None]["progress_color"] = "blue"
            self.time_start[None] = time.time()
            self.emit_state()
            self.handle_requests()
            error_code = ytdlp.download(url)
            self.handle_requests()

            for sub_id, state in self.state.items():
                if sub_id is None:
                    continue
                if state["value"] == "pending" or state["value"] == "in_progress":
                    if not error_code:
                        self._mark_as_completed(sub_id, None)
                    else:
                        self._mark_as_failed(sub_id)

            if self.info[None]["type"] == "list" or not error_code:
                self._mark_as_completed(None, None)
            elif self.state[None]["value"] != "completed":
                self._mark_as_failed(None)
