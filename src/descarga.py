from typing import Dict, List, Optional
import os
import shutil
import io
from logging import Logger
from threading import Lock, Event
from utils import configure_logger, close_logger
from tipos import State, Info, DownloadCancelled, DownloadPaused
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
        delta_manager: DeltaManager,
    ):
        # Archivos temporales de descarga en temp/{id}/
        options.setdefault("paths", {})["temp"] = os.path.join(temp_path, id)
        self.id = id
        self.info = info
        self.state = state
        self.options = options

        # Dynamic properties
        self.delta_manager = delta_manager
        self.log_file = os.path.join(logs_path, f"{self.id}.log")
        self.logger: Optional[Logger] = None
        self.log_stream: Optional[io.StringIO] = None
        self.sub_descargas: List[Descarga_Hija] = []
        for d in sub_descargas:
            descarga_hija = Descarga_Hija.from_dict(d)
            if descarga_hija.state["value"] != "deleted":
                self.sub_descargas.append(descarga_hija)
        self.lock = Lock()
        # Lista de ID's de elementos de playlist a descargar
        self.select_entries_event = Event()
        self.selected_entries: List[str] = []
        # Lista de sub_descargas que esperan selección de entradas
        self.entries_to_select: List[Descarga_Hija_dict] = []
        # Solicitudes
        self.cancel_requested = False
        self.pause_requested = False

        # controles
        self._download_in_progress = False

    def set_selected_entries(self, entries: List[str]):
        if self.state.get("value") != "wait_for_selection":
            raise ValueError(
                "No se pueden seleccionar entradas si no se esta esperando una selección"
            )
        if self.select_entries_event.is_set():
            raise ValueError("Ya se han seleccionado las entradas")
        self.selected_entries = entries
        self.select_entries_event.set()

    def get_selected_entries(self) -> List[str]:
        return self.selected_entries

    def set_entries_to_select(self, entries: List[Descarga_Hija_dict]):
        self.entries_to_select = entries

    def get_entries_to_select(self) -> List[Descarga_Hija_dict]:
        if self.state.get("value") != "wait_for_selection":
            raise ValueError(
                "No se pueden obtener las entradas si no se esta esperando una selección"
            )
        return self.entries_to_select

    def handle_requests(self):
        if self.cancel_requested:
            raise DownloadCancelled("La descarga ha sido cancelada por el usuario")
        if self.pause_requested:
            raise DownloadPaused("La descarga ha sido pausada por el usuario")

    def _init_logger(self):
        self.logger, self.log_stream = configure_logger(
            log_file=self.log_file, logger_name=self.id
        )

    def _close_logger(self):
        if self.logger:
            close_logger(self.logger)
            self.logger = None
            self.log_stream = None

    def get_logs(self, limit: int = 100) -> str:
        if self.log_stream is not None:
            logs = self.log_stream.getvalue()
            return "\n".join(logs.split("\n")[-limit:][::-1]).strip() if logs else ""
        if not os.path.exists(self.log_file):
            return ""
        with open(self.log_file, "r", encoding="utf-8") as f:
            logs = f.read()
            f.close()
            return "\n".join(logs.split("\n")[-limit:][::-1]).strip() if logs else ""

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
        data: Dict, logs_path: str, temp_path: str, delta_manager: DeltaManager
    ):
        return Descarga(
            id=data["id"],
            info=data["info"],
            state=data["state"],
            options=data["options"],
            sub_descargas=data["sub_descargas"],
            logs_path=logs_path,
            temp_path=temp_path,
            delta_manager=delta_manager,
        )

    def _set_state(self, state: State, sub_id: Optional[str]):
        if sub_id is None:
            self.state = state
        else:
            with self.lock:
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
        self.delta_manager.update_status(self.id, sub_id, state)

    def _set_info(self, info: Info, sub_id: Optional[str]):
        if sub_id is None:
            self.info = info
        else:
            with self.lock:
                sub_descarga: Optional[Descarga_Hija] = next(
                    (d for d in self.sub_descargas if d.sub_id == sub_id), None
                )
                if sub_descarga is None:
                    sub_descarga = Descarga_Hija(
                        sub_id=sub_id,
                        parent_id=self.id,
                        state={
                            "value": "pending",
                            "sub_state": None,
                        },
                        info=info,
                    )
                    self.sub_descargas.append(sub_descarga)
            if sub_descarga is not None:
                sub_descarga.info = info
        self.delta_manager.update_info(self.id, sub_id, info)

    def iniciar_descarga(self):
        if self._download_in_progress:
            if self.logger:
                self.logger.warning(
                    f"Descarga {self.id} ya esta en progreso, ignorando solicitud de inicio"
                )
            return
        self._download_in_progress = True
        self._init_logger()
        assert self.logger is not None, "Logger no inicializado"
        for path in self.options.get("paths", {}).values():
            os.makedirs(path, exist_ok=True)
        self.logger.info(
            f"Iniciando descarga de {self.info['url']} con opciones {self.options}"
        )
        ytdlp_connector = YTDLPConnector(
            id=self.id,
            options=self.options,
            logger=self.logger,
            info=self.info,
            state=self.state,
            set_state=self._set_state,
            set_info=self._set_info,
            set_entries_to_select=self.set_entries_to_select,
            get_selected_entries=self.get_selected_entries,
            sub_descargas=[d.to_dict() for d in self.sub_descargas],
            select_entries_event=self.select_entries_event,
            handle_requests=self.handle_requests,
            get_logs=lambda: self.get_logs(0),
        )
        try:
            self.select_entries_event.clear()
            ytdlp_connector.download(self.info["url"])
            self.logger.info(f"Descarga de {self.info['url']} terminada")
        except DownloadPaused:
            self._pausar_descarga()
        except DownloadCancelled:
            self._cancelar_descarga()
        except Exception as e:
            self._set_state(
                {**self.state, "value": "failed", "sub_state": str(e)[:100]}, None
            )
            self.logger.error(f"Error al descargar {self.info['url']}: {e}")
            self.logger.error(traceback.format_exc())
        finally:
            self._close_logger()
            self._download_in_progress = False

    def pausar_descarga(self):
        self.pause_requested = True
        # Desbloquea la espera de selección si es necesario
        self.select_entries_event.set()
        if not self._download_in_progress:
            self._pausar_descarga()

    def _pausar_descarga(self):
        if self.state["value"] in ["wait_for_selection", "identifying"]:
            if self.logger:
                self.logger.error(
                    f"Estado no valido para {self.id} eliminando {self.state['value']}"
                )
            self._set_state({**self.state, "value": "deleted"}, None)
            return
        if self.state["value"] == "in_progress":
            if self.logger:
                self.logger.info(f"Descarga {self.id} pausada por el usuario")
            self._set_state({**self.state, "value": "paused"}, None)
            for sub_descarga in self.sub_descargas:
                if sub_descarga.state["value"] == "in_progress":
                    self._set_state(
                        {**sub_descarga.state, "value": "paused"}, sub_descarga.sub_id
                    )

    def continuar_descarga(self, sub_ids: Optional[List[str]] = None):
        # TODO: esto sirve para continuar pausado(YT-DLP guarda estado)
        # TODO: también sirve para reintentar después de un error desconocido

        # SI ES LISTA y sub_ids es None, reintentar todos los que no están en "completed"
        # SI ES LISTA y sub_ids no es None, reintentar solo los sub_id que no están en "completed"

        # SI NO ES LISTA, reintentar toda la descarga
        pass

    def cancelar_descarga(self):
        self.cancel_requested = True
        # Desbloquea la espera de selección si es necesario
        self.select_entries_event.set()

    def _cancelar_descarga(self):
        if "paths" in self.options and "temp" in self.options["paths"]:
            temp_path = self.options["paths"]["temp"]
            # assert temp path is inside the temp directory for security
            if (
                os.path.commonpath([temp_path, self.options["paths"]["temp"]])
                != self.options["paths"]["temp"]
            ):
                if self.logger:
                    self.logger.error(
                        f"Temp path {temp_path} is not inside the temp directory {self.options['paths']['temp']}"
                    )
            elif os.path.exists(temp_path):
                shutil.rmtree(temp_path, ignore_errors=True)
        if self.state["value"] in ["wait_for_selection", "identifying"]:
            if self.logger:
                self.logger.error(
                    f"Estado no valido para {self.id} eliminando {self.state['value']}"
                )
            self._set_state({**self.state, "value": "deleted"}, None)
            return
        if self.logger:
            self.logger.info(f"Descarga {self.id} cancelada por el usuario")
        self._set_state({**self.state, "value": "canceled"}, None)
