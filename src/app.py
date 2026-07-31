import atexit
import json
import os
import sqlite3
from threading import Event, Lock, Thread
from typing import Any, Literal

from descarga import DeltaManager, Descarga, Descarga_Hija
from utils import close_logger, configure_logger
from yt_dlp_parser_types import is_valid_options


class App:
    def __init__(
        self,
        logs_path: str,
        data_path: str,
        temp_path: str,
        ffmpeg_path: str,
        quickjs_path: str,
    ):
        # Config
        self.logs_path = logs_path
        self.data_path = data_path
        self.temp_path = temp_path
        self.ffmpeg_path = ffmpeg_path
        self.quickjs_path = quickjs_path
        os.makedirs(self.logs_path, exist_ok=True)
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)
        self.lock = Lock()
        self.save_lock = Lock()

        # Evento para controlar el hilo guardián
        self._stop_event = Event()

        # Data en RAM
        self.descargas: list[Descarga] = []

        # Logs
        self.logger, self.log_stream = configure_logger(
            log_file=os.path.join(self.logs_path, "app.log"),
            logger_name="app",
        )
        self.delta_manager = DeltaManager(self.logger)

        # Restore State (SQLite)
        self.db_path = os.path.join(self.data_path, "data.db")
        self._init_db()
        self._load_state()

        for d in self.descargas:
            if d.state["value"] == "in_progress" or d.state["value"] == "pausing":
                d.pausar_descarga()
            elif (
                d.state["value"] == "requested"
                or d.state["value"] == "extracting_information"
                or d.state["value"] == "awaiting_selection"
                or d.state["value"] == "deleting"
            ):
                d.eliminar_descarga()
            elif d.state["value"] == "cancelling":
                d.cancelar_descarga()

        # Iniciar el Hilo Guardian (escucha deltas y persiste cambios)
        self._db_thread = Thread(target=self._background_save, daemon=True)
        self._db_thread.start()

        # Forzar guardado si se cierra la aplicación
        self._shutdown_called = False
        atexit.register(self.shutdown)

        self.logger.info("Aplicación iniciada con Gestor Persistente SQLite")

    def _init_db(self):
        """Crea las tablas si no existen."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS descargas (
                    id TEXT PRIMARY KEY,
                    info TEXT,
                    state TEXT,
                    options TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sub_descargas (
                    sub_id TEXT,
                    parent_id TEXT,
                    info TEXT,
                    state TEXT,
                    PRIMARY KEY (sub_id, parent_id),
                    FOREIGN KEY(parent_id) REFERENCES descargas(id) ON DELETE CASCADE
                )
            """)

    def _load_state(self):
        """Carga el estado desde SQLite a la memoria RAM al iniciar."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM descargas")
            filas_descargas = cursor.fetchall()

            for fila in filas_descargas:
                d_id = fila["id"]
                # Buscar sub-descargas asociadas
                sub_cursor = conn.execute(
                    "SELECT * FROM sub_descargas WHERE parent_id=?", (d_id,)
                )
                filas_subs = sub_cursor.fetchall()

                sub_descargas_list = []
                for sub_fila in filas_subs:
                    sub_descargas_list.append(
                        {
                            "sub_id": sub_fila["sub_id"],
                            "info": json.loads(sub_fila["info"]),
                            "state": json.loads(sub_fila["state"]),
                            "parent_id": sub_fila["parent_id"],
                        }
                    )

                descarga = Descarga(
                    id=d_id,
                    info=json.loads(fila["info"]),
                    state=json.loads(fila["state"]),
                    options=json.loads(fila["options"]),
                    sub_descargas=sub_descargas_list,
                    logs_path=self.logs_path,
                    temp_path=self.temp_path,
                    ffmpeg_path=self.ffmpeg_path,
                    quickjs_path=self.quickjs_path,
                    delta_manager=self.delta_manager,
                )
                if descarga.state["value"] != "deleted":
                    self.descargas.append(descarga)

    def _background_save(self):
        """Bucle del hilo guardián."""
        subscription = self.delta_manager.subscribe(
            id=None,
            everything=True,
        )
        try:
            for message in subscription:
                if self._stop_event.is_set():
                    break
                deltas = self._parse_delta_message(message)
                if deltas:
                    self._apply_deltas(deltas)
        except Exception as e:
            self.logger.error(f"Error en _background_save: {e}")
        finally:
            try:
                subscription.close()
            except Exception as exc:
                self.logger.warning(f"No se pudo cerrar la suscripción: {exc}")

    def _parse_delta_message(self, message: str) -> list[dict[str, Any]]:
        if not message.startswith("data: "):
            return []
        payload = message[len("data: ") :].strip()
        if not payload:
            return []
        try:
            data = json.loads(payload)
        except json.JSONDecodeError as e:
            self.logger.warning(f"Delta invalido: {e}")
            return []
        return data if isinstance(data, list) else []

    def _apply_deltas(self, deltas: list[dict[str, Any]]):
        if not deltas:
            return

        with self.lock:
            descargas_by_id = {d.id: d for d in self.descargas}
            prepared = []
            for delta in deltas:
                descarga_id = delta.get("id")
                if not descarga_id:
                    continue
                sub_id = delta.get("sub_id")
                descarga = descargas_by_id.get(descarga_id)
                sub_descarga = None
                if descarga is not None and sub_id is not None:
                    sub_descarga = next(
                        (sd for sd in descarga.sub_descargas if sd.sub_id == sub_id),
                        None,
                    )
                prepared.append((delta, descarga, sub_descarga))

        with self.save_lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    for delta, descarga, sub_descarga in prepared:
                        self._persist_delta(conn, delta, descarga, sub_descarga)
            except Exception as e:
                self.logger.error(f"Error al aplicar deltas: {e}")

    def _persist_delta(
        self,
        conn: sqlite3.Connection,
        delta: dict[str, Any],
        descarga: Descarga | None,
        sub_descarga: Descarga_Hija | None,
    ):
        info = delta.get("info")
        status = delta.get("status")
        id = delta.get("id")
        sub_id = delta.get("sub_id")
        if id is None:
            return
        cursor = conn.cursor()
        if descarga is not None and descarga.state["value"] != "deleted":
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM descargas WHERE id=?)", (descarga.id,)
            )
            if cursor.fetchone()[0] == 0:
                conn.execute(
                    """
                        INSERT OR IGNORE INTO descargas (id, info, state, options)
                        VALUES (?, ?, ?, ?)
                    """,
                    (
                        descarga.id,
                        json.dumps(descarga.info),
                        json.dumps(descarga.state),
                        json.dumps(descarga.options),
                    ),
                )
        if sub_descarga is not None and sub_descarga.state["value"] != "deleted":
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM sub_descargas WHERE sub_id=? AND parent_id=?)",
                (sub_descarga.sub_id, sub_descarga.parent_id),
            )
            if cursor.fetchone()[0] == 0:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO sub_descargas (sub_id, parent_id, info, state)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        sub_descarga.sub_id,
                        sub_descarga.parent_id,
                        json.dumps(sub_descarga.info),
                        json.dumps(sub_descarga.state),
                    ),
                )

        if sub_id is None:
            updates = []
            params = []
            if info is not None:
                updates.append("info = ?")
                params.append(json.dumps(info))
            if status is not None:
                updates.append("state = ?")
                params.append(json.dumps(status))

            if updates and not (status and status.get("value") == "deleted"):
                params.append(id)
                conn.execute(
                    f"UPDATE descargas SET {', '.join(updates)} WHERE id = ?",
                    params,
                )
            elif status and status.get("value") == "deleted":
                conn.execute("DELETE FROM descargas WHERE id = ?", (id,))
        elif sub_id is not None:
            updates = []
            params = []
            if info is not None:
                updates.append("info = ?")
                params.append(json.dumps(info))
            if status is not None:
                updates.append("state = ?")
                params.append(json.dumps(status))

            if updates and not (status and status.get("value") == "deleted"):
                params.append(sub_id)
                params.append(id)
                conn.execute(
                    f"UPDATE sub_descargas SET {', '.join(updates)} WHERE sub_id = ? AND parent_id = ?",
                    params,
                )
            elif status and status.get("value") == "deleted":
                conn.execute(
                    "DELETE FROM sub_descargas WHERE sub_id = ? AND parent_id = ?",
                    (sub_id, id),
                )

    def _save_state(self):
        """Sincroniza masivamente la RAM con la base de datos SQLite."""
        if not self.descargas:
            return

        with self.save_lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    datos_descargas = []
                    datos_subs = []

                    # Preparamos los datos iterando sobre la RAM
                    for d in self.descargas:
                        datos_descargas.append(
                            (
                                d.id,
                                json.dumps(d.info),
                                json.dumps(d.state),
                                json.dumps(d.options),
                            )
                        )
                        for sd in d.sub_descargas:
                            datos_subs.append(
                                (
                                    sd.sub_id,
                                    sd.parent_id,
                                    json.dumps(sd.info),
                                    json.dumps(sd.state),
                                )
                            )

                    # Escritura masiva eficiente
                    conn.executemany(
                        """
                        INSERT OR REPLACE INTO descargas (id, info, state, options)
                        VALUES (?, ?, ?, ?)
                    """,
                        datos_descargas,
                    )

                    if datos_subs:
                        conn.executemany(
                            """
                            INSERT OR REPLACE INTO sub_descargas (sub_id, parent_id, info, state)
                            VALUES (?, ?, ?, ?)
                        """,
                            datos_subs,
                        )
            except Exception as e:
                self.logger.error(f"Error al sincronizar con SQLite: {e}")

    def get_logs(self, id: str | None = None) -> str:
        logs = ""
        if id is not None:
            descarga = next((d for d in self.descargas if d.id == id), None)
            if descarga is not None:
                logs = descarga.get_logs()
            else:
                raise ValueError("Descarga no encontrada")
        else:
            logs = self.log_stream.getvalue()
        return "---TRUNCATED---\n" + logs[-50000:] if len(logs) > 50000 else logs

    def get_downloads(
        self,
        id: str | None = None,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        with self.lock:
            descargas_snapshot = [
                d for d in self.descargas if d.state["value"] != "deleted"
            ]
        if id is None:
            # datos generales de las descargas
            response = []
            for d in descargas_snapshot:
                info = {
                    "id": d.id,
                    "info": d.info,
                    "state": d.state,
                }
                response.append(info)
            return response[::-1]  # mostrar primero las descargas mas recientes
        else:
            # datos de una elemento + descargas hijas
            element = next((d for d in descargas_snapshot if d.id == id), None)
            if element is None:
                raise ValueError(f"Descarga con id {id} no encontrada")
            return {
                "id": element.id,
                "info": element.info,
                "state": element.state,
                "options": element.options,
                "sub_descargas": [
                    {
                        "sub_id": sd.sub_id,
                        "parent_id": sd.parent_id,
                        "info": sd.info,
                        "state": sd.state,
                    }
                    for sd in element.sub_descargas
                ][::-1],  # mostrar primero las sub-descargas mas recientes
            }

    def add_download(self, url: str, options: dict):
        if not is_valid_options(options):
            raise ValueError("Opciones de descarga no válidas")
        with self.lock:
            descarga_id = str(max([int(d.id) for d in self.descargas], default=0) + 1)
        descarga = Descarga(
            id=descarga_id,
            info={
                "url": url,
                "image": None,
                "file": None,
                "title": None,
                "platform": None,
                "type": "unknown",
                "autor": None,
                "creation_date": None,
                "duration": None,
            },
            options=options,
            logs_path=self.logs_path,
            temp_path=self.temp_path,
            ffmpeg_path=self.ffmpeg_path,
            quickjs_path=self.quickjs_path,
            state={
                "value": "requested",
            },
            sub_descargas=[],
            delta_manager=self.delta_manager,
        )
        with self.lock:
            self.descargas.append(descarga)
        self.logger.info(f"Descarga {descarga_id} agregada: {url}")

        def run_descarga():
            descarga.descargar()

        Thread(target=run_descarga, daemon=True).start()
        return descarga_id

    def update_download(
        self, id: str, action: Literal["pause", "resume", "cancel", "delete", "retry"]
    ):
        with self.lock:
            descarga = next((d for d in self.descargas if d.id == id), None)
        if descarga is None:
            raise ValueError(f"Descarga con id {id} no encontrada")

        def run_descarga():
            descarga.descargar()

        if action == "pause":
            descarga.pausar_descarga()
        elif action == "resume":
            Thread(target=run_descarga, daemon=True).start()
        elif action == "cancel":
            descarga.cancelar_descarga()
        elif action == "delete":
            descarga.eliminar_descarga()
        elif action == "retry":
            Thread(target=run_descarga, daemon=True).start()

    def get_entries_to_select(self, id: str):
        with self.lock:
            descarga = next((d for d in self.descargas if d.id == id), None)
        if descarga is None:
            raise ValueError(f"Descarga con id {id} no encontrada")
        if descarga.info["type"] != "list":
            raise ValueError("La descarga no es una lista")
        return descarga.entries_to_select

    def select_entries(self, id: str, entries: list[str]):
        with self.lock:
            descarga = next((d for d in self.descargas if d.id == id), None)
        if descarga is None:
            raise ValueError(f"Descarga con id {id} no encontrada")
        descarga.set_selected_entry_ids(entries)

    def subscribe_to_deltas(self, id: str | None, everything: bool):
        return self.delta_manager.subscribe(id=id, everything=everything)

    def shutdown(self):
        """Detiene el hilo guardián de forma segura."""
        if self._shutdown_called:
            return
        self._shutdown_called = True
        print("Gracefully shutting down...\n\n")
        self._stop_event.set()
        for d in self.descargas:
            if d.state["value"] == "in_progress":
                d.pausar_descarga()
            elif (
                d.state["value"] == "requested"
                or d.state["value"] == "extracting_information"
                or d.state["value"] == "awaiting_selection"
            ):
                d.eliminar_descarga()
        if self._db_thread.is_alive():
            self._db_thread.join()
        self._save_state()
        close_logger(self.logger)
