from typing import Any, Dict, Iterable, List, Optional, TypeGuard
import os
import shutil
import io
from logging import Logger
from threading import Lock, Event
from utils import configure_logger, close_logger
from tipos import DownloadDeleted, State, Info, DownloadCancelled, DownloadPaused
from yt_dlp_connector import YTDLPConnector
from yt_dlp_parser_types import VidraOptions
from delta import DeltaManager
import traceback
from descarga_hija import Descarga_Hija, Descarga_Hija_dict


class Descarga:
    def __init__(
        self,
        id: str,
        info: Info,
        state: State,
        options: VidraOptions,
        sub_descargas: List[Dict],
        logs_path: str,
        temp_path: str,
        ffmpeg_path: str,
        quickjs_path: str,
        delta_manager: DeltaManager,
    ):
        # Archivos temporales de descarga en temp/{id}/
        options.setdefault("paths", {})["temp"] = os.path.join(temp_path, id)
        # Ubicación de ffmpeg y quickjs para yt-dlp
        options["ffmpeg_location"] = ffmpeg_path
        options.setdefault("js_runtimes", {})["quickjs"] = quickjs_path
        self.id = id
        self.info = info
        self.state = state
        self.options = options

        # Dynamic properties
        self._delta_manager = delta_manager
        self._log_file = os.path.join(logs_path, f"{self.id}.log")
        self._logger: Optional[Logger] = None
        self._log_stream: Optional[io.StringIO] = None
        self.sub_descargas: List[Descarga_Hija] = []
        for d in sub_descargas:
            descarga_hija = Descarga_Hija.from_dict(d)
            if descarga_hija.state["value"] != "deleted":
                self.sub_descargas.append(descarga_hija)
        self._lock = Lock()
        # Lista de ID's de elementos de playlist a descargar
        self._select_entries_event = Event()
        self._selected_entry_ids: Optional[List[str]] = None
        # Lista de sub_descargas que esperan selección de entradas
        self._entries_to_select: Optional[List[Descarga_Hija_dict]] = None

        # Flags de control de la descarga
        self._download_in_progress = False
        self.pause_requested = False
        self.cancel_requested = False
        self.delete_requested = False

    def _get_selected_entry_ids(self) -> List[str]:
        if self.state["value"] != "awaiting_selection":
            raise ValueError(
                "No se pueden obtener las entradas seleccionadas si no se esta esperando una selección"
            )
        if self._selected_entry_ids is None:
            raise ValueError("No se han seleccionado entradas")
        return self._selected_entry_ids

    def set_selected_entry_ids(self, entry_ids: Iterable[str]):
        if self.state["value"] != "awaiting_selection":
            raise ValueError(
                "No se pueden seleccionar entradas si no se esta esperando una selección"
            )
        if self._select_entries_event.is_set():
            raise ValueError("Ya se han seleccionado las entradas")
        self._selected_entry_ids = list(entry_ids)
        self._select_entries_event.set()

    @property
    def entries_to_select(self) -> List[Descarga_Hija_dict]:
        if self.state["value"] != "awaiting_selection":
            raise ValueError(
                "No se pueden obtener las entradas si no se esta esperando una selección"
            )
        if self._entries_to_select is None:
            raise ValueError("No hay entradas para seleccionar")
        return self._entries_to_select

    def _set_entries_to_select(self, entries: Iterable[Descarga_Hija_dict]):
        self._entries_to_select = list(entries)

    def handle_requests(self):
        if self.cancel_requested:
            raise DownloadCancelled("La descarga ha sido cancelada por el usuario")
        if self.pause_requested:
            raise DownloadPaused("La descarga ha sido pausada por el usuario")
        if self.delete_requested:
            raise DownloadDeleted("La descarga ha sido eliminada por el usuario")

    def _init_logger(self, check: Any) -> TypeGuard[Logger]:
        if self._logger is not None:
            return True
        self._logger, self._log_stream = configure_logger(
            log_file=self._log_file, logger_name=self.id
        )
        return True

    def _close_logger(self):
        if self._logger:
            close_logger(self._logger)
            self._logger = None
            self._log_stream = None

    def get_logs(self) -> str:
        if self._log_stream is not None:
            return self._log_stream.getvalue()
        if not os.path.exists(self._log_file):
            return ""
        with open(self._log_file, "r", encoding="utf-8") as f:
            logs = f.read()
            f.close()
            return logs

    def to_dict(self):
        return {
            "id": self.id,
            "info": self.info,
            "state": self.state,
            "options": self.options,
            "sub_descargas": [d.to_dict() for d in self.sub_descargas],
        }

    @staticmethod
    def from_dict(
        data: Dict,
        logs_path: str,
        temp_path: str,
        ffmpeg_path: str,
        quickjs_path: str,
        delta_manager: DeltaManager,
    ):
        return Descarga(
            id=data["id"],
            info=data["info"],
            state=data["state"],
            options=data["options"],
            sub_descargas=data["sub_descargas"],
            logs_path=logs_path,
            temp_path=temp_path,
            ffmpeg_path=ffmpeg_path,
            quickjs_path=quickjs_path,
            delta_manager=delta_manager,
        )

    def _set_state(self, state: State, sub_id: Optional[str]):
        if sub_id is None:
            self.state = state
        else:
            with self._lock:
                sub_descarga: Optional[Descarga_Hija] = next(
                    (d for d in self.sub_descargas if d.sub_id == sub_id), None
                )
                if sub_descarga is not None and state["value"] == "deleted":
                    self.sub_descargas.remove(sub_descarga)
                elif sub_descarga is None and state["value"] != "deleted":
                    sub_descarga = Descarga_Hija(
                        sub_id=sub_id,
                        parent_id=self.id,
                        state=state,
                        info={
                            "url": None,
                            "image": None,
                            "file": None,
                            "title": None,
                            "platform": None,
                            "type": "unknown",
                            "autor": None,
                            "creation_date": None,
                            "duration": None,
                        },
                    )
                    self.sub_descargas.append(sub_descarga)
            if sub_descarga is not None:
                sub_descarga.state = state
        self._delta_manager.update_status(self.id, sub_id, state)

    def _set_info(self, info: Info, sub_id: Optional[str]):
        if sub_id is None:
            self.info = info
        else:
            with self._lock:
                sub_descarga: Optional[Descarga_Hija] = next(
                    (d for d in self.sub_descargas if d.sub_id == sub_id), None
                )
                if sub_descarga is None:
                    sub_descarga = Descarga_Hija(
                        sub_id=sub_id,
                        parent_id=self.id,
                        state={
                            "value": "requested",
                            "sub_state": None,
                        },
                        info=info,
                    )
                    self.sub_descargas.append(sub_descarga)
            if sub_descarga is not None:
                sub_descarga.info = info
        self._delta_manager.update_info(self.id, sub_id, info)

    def descargar(self):
        with self._lock:
            if self._download_in_progress:
                raise ValueError("La descarga ya esta en progreso")
            self._download_in_progress = True
        try:
            if (
                self.state["value"] != "requested"
                and self.state["value"] != "failed"
                and self.state["value"] != "paused"
                and self.state["value"] != "cancelled"
            ):
                raise ValueError(
                    "No se puede iniciar la descarga si no esta en estado 'requested', "
                    f"'failed', 'paused' o 'cancelled', estado actual: {self.state['value']}"
                )
            if not self._init_logger(self._logger):
                raise ValueError("Error al inicializar el logger")

            for path in self.options.get("paths", {}).values():
                os.makedirs(path, exist_ok=True)

            ytdlp_connector = YTDLPConnector(
                id=self.id,
                options=self.options,
                logger=self._logger,
                info=self.info,
                state=self.state,
                set_state=self._set_state,
                set_info=self._set_info,
                set_entries_to_select=self._set_entries_to_select,
                get_selected_entry_ids=self._get_selected_entry_ids,
                sub_descargas=[d.to_dict() for d in self.sub_descargas],
                select_entries_event=self._select_entries_event,
                handle_requests=self.handle_requests,
                get_logs=self.get_logs,
            )
            self._select_entries_event.clear()
            ytdlp_connector.download(self.info["url"])
            if self.state["value"] == "completed":
                self._clear_temp_files()
            self._logger.info(f"Descarga de {self.info['url']} terminada")
        except DownloadPaused:
            self._pausar_descarga()
        except DownloadCancelled:
            self._cancelar_descarga()
        except DownloadDeleted:
            self._eliminar_descarga()
        except Exception as e:
            self._set_state(
                {**self.state, "value": "failed", "sub_state": str(e)[:100]}, None
            )
            if self._logger:
                self._logger.error(f"Error al descargar {self.info['url']}: {e}")
                self._logger.error(traceback.format_exc())
        finally:
            self._close_logger()
            self._download_in_progress = False

    def pausar_descarga(self):
        with self._lock:
            if self.state["value"] != "in_progress":
                raise ValueError(
                    f"No se puede pausar la descarga {self.id} si no esta en progreso"
                )
            if self.pause_requested:
                raise ValueError(f"La descarga {self.id} ya esta siendo pausada")
            if self.cancel_requested:
                raise ValueError(
                    f"No se puede pausar la descarga {self.id} si esta siendo cancelada"
                )
            if self.delete_requested:
                raise ValueError(
                    f"No se puede pausar la descarga {self.id} si esta siendo eliminada"
                )
            self.pause_requested = True
        if not self._download_in_progress:
            self._pausar_descarga()

    def _pausar_descarga(self):
        self._select_entries_event.set()
        self._set_state({**self.state, "value": "paused"}, None)
        for sub_descarga in self.sub_descargas:
            if sub_descarga.state["value"] == "in_progress":
                self._set_state(
                    {**sub_descarga.state, "value": "paused"}, sub_descarga.sub_id
                )
        if self._logger:
            self._logger.info(f"Descarga {self.id} pausada")
        self.pause_requested = False

    def cancelar_descarga(self):
        with self._lock:
            if (
                self.state["value"] != "in_progress"
                and self.state["value"] != "pending"
                and self.state["value"] != "paused"
            ):
                raise ValueError(
                    f"No se puede cancelar la descarga {self.id} si no esta en estado 'requested', ",
                    "'pending', 'extracting_information', 'awaiting_selection' o 'paused'",
                )
            if self.cancel_requested:
                raise ValueError(f"La descarga {self.id} ya esta siendo cancelada")
            if self.pause_requested:
                raise ValueError(
                    f"No se puede cancelar la descarga {self.id} si esta siendo pausada"
                )
            if self.delete_requested:
                raise ValueError(
                    f"No se puede cancelar la descarga {self.id} si esta siendo eliminada"
                )
            self.cancel_requested = True
        if not self._download_in_progress:
            self._cancelar_descarga()

    def _cancelar_descarga(self):
        self._select_entries_event.set()
        self._clear_temp_files()
        self._set_state({**self.state, "value": "cancelled"}, None)
        if self._logger:
            self._logger.info(f"Descarga {self.id} cancelada por el usuario")

    def eliminar_descarga(self):
        with self._lock:
            if (
                self.state["value"] != "requested"
                and self.state["value"] != "pending"
                and self.state["value"] != "extracting_information"
                and self.state["value"] != "awaiting_selection"
                and self.state["value"] != "in_progress"
                and self.state["value"] != "completed"
                and self.state["value"] != "completed_with_errors"
                and self.state["value"] != "failed"
                and self.state["value"] != "cancelled"
                and self.state["value"] != "paused"
            ):
                raise ValueError(
                    f"No se puede eliminar la descarga {self.id} si no esta en estado 'requested', ",
                    "'pending', 'extracting_information', 'awaiting_selection', 'in_progress', ",
                    "'completed', 'completed_with_errors', 'failed', 'cancelled' o 'paused'",
                )
            if self.cancel_requested:
                raise ValueError(f"La descarga {self.id} ya esta siendo cancelada")
            if self.pause_requested:
                raise ValueError(
                    f"No se puede cancelar la descarga {self.id} si esta siendo pausada"
                )
            self.delete_requested = True
        if not self._download_in_progress:
            self._eliminar_descarga()

    def _eliminar_descarga(self):
        self._select_entries_event.set()
        self._clear_temp_files()
        self._set_state({**self.state, "value": "deleted"}, None)
        if self._logger:
            self._logger.info(f"Descarga {self.id} eliminada por el usuario")
            self._close_logger()
        if os.path.exists(self._log_file):
            os.remove(self._log_file)

    def _clear_temp_files(self):
        if "paths" in self.options and "temp" in self.options["paths"]:
            temp_path = self.options["paths"]["temp"]
            if os.path.exists(temp_path):
                shutil.rmtree(temp_path, ignore_errors=True)
