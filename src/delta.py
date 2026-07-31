## en frontend el manager se conectara a esto si existen descargas activas
# get_deltas __ text/event-stream
# [{id,sub_id,status,info}]
# | sin ID -> deltas generales, sin sub_id & conectar siempre que haya descargas activas
# | id -> sub_deltas de una descarga específica & conectar si esta en pantalla de detalle de una lista y se esta descargando

import json
import time
from collections.abc import Generator
from logging import Logger
from threading import Lock
from typing import TypedDict

from tipos import Info, State


class Delta(TypedDict):
    id: str
    sub_id: str | None
    status: State | None
    info: Info | None


class Subscriber(TypedDict):
    lock: Lock
    everything: bool
    id: str | None
    deltas: dict[tuple[str, str | None], Delta]


# se reciben los updates de los delta si están suscritos a ellos
class DeltaManager:
    def __init__(self, logger: Logger | None):
        self.logger = logger
        self.lock = Lock()
        self.subscribers: list[Subscriber] = []

    def subscribe(
        self, id: str | None, everything: bool = False
    ) -> Generator[str, None, None]:
        with self.lock:
            subscriber = Subscriber(
                lock=Lock(), id=id, deltas={}, everything=everything
            )
            self.subscribers.append(subscriber)
        try:
            while True:
                if subscriber["deltas"]:
                    with subscriber["lock"]:
                        deltas = list(subscriber["deltas"].values())
                        subscriber["deltas"].clear()
                    yield f"data: {json.dumps(deltas)}\n\n"
                else:
                    yield ": ping (keep-alive)\n\n"
                time.sleep(1)  # para evitar busy waiting
        except GeneratorExit:
            # el cliente se desconectó, limpiamos las suscripciones
            with self.lock:
                if subscriber in self.subscribers:
                    self.subscribers.remove(subscriber)
                else:
                    if self.logger:
                        self.logger.warning(
                            "Subscriber no encontrado al intentar eliminarlo"
                        )
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error en subscribe: {e}")

    def update_status(self, id: str, sub_id: str | None, status: State):
        with self.lock:
            subscribers_snapshot = list(self.subscribers)
        for subscriber in subscribers_snapshot:
            if (
                subscriber["everything"]
                or (subscriber["id"] is None and sub_id is None)
                or (
                    subscriber["id"] is not None
                    and id == subscriber["id"]
                    and sub_id is not None
                )
            ):
                # si el subscriber no tiene id escucha updates principales, no sub-updates
                # si el subscriber tiene id escucha solo los sub-updates de esa id
                with subscriber["lock"]:
                    if (id, sub_id) in subscriber["deltas"]:
                        subscriber["deltas"][(id, sub_id)]["status"] = status
                    else:
                        subscriber["deltas"][(id, sub_id)] = {
                            "id": id,
                            "sub_id": sub_id,
                            "status": status,
                            "info": None,
                        }

    def update_info(self, id: str, sub_id: str | None, info: Info):
        with self.lock:
            subscribers_snapshot = list(self.subscribers)
        for subscriber in subscribers_snapshot:
            if (
                subscriber["everything"]
                or (subscriber["id"] is None and sub_id is None)
                or (
                    subscriber["id"] is not None
                    and id == subscriber["id"]
                    and sub_id is not None
                )
            ):
                with subscriber["lock"]:
                    if (id, sub_id) in subscriber["deltas"]:
                        subscriber["deltas"][(id, sub_id)]["info"] = info
                    else:
                        subscriber["deltas"][(id, sub_id)] = {
                            "id": id,
                            "sub_id": sub_id,
                            "status": None,
                            "info": info,
                        }
