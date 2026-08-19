import logging
from typing import Any, Literal, NotRequired, TypedDict

type Color = Literal[
    "green",  # completado
    "yellow",  # pausado
    "red",  # error
    "blue",  # en proceso
    "gray",  # cancelado
    "orange",  # error parcial
    "purple",  # esperando selección
    "cyan",  # extrayendo información
    "magenta",  # pending
]


class DownloadCancelled(KeyboardInterrupt):
    """Excepción personalizada para indicar que la descarga ha sido cancelada"""


class DownloadPaused(KeyboardInterrupt):
    """Excepción personalizada para indicar que la descarga ha sido pausada"""


class DownloadDeleted(KeyboardInterrupt):
    """Excepción personalizada para indicar que la descarga ha sido eliminada"""


class YTDLPLoggerAdapter:
    """
    Clase que envuelve un logging.Logger estándar para que cumpla
    estrictamente con la interfaz _LoggerProtocol de yt-dlp.
    """

    def __init__(
        self, ydl: Any | None = None, logger: logging.Logger | None = None
    ) -> None:
        self.logger = logger

    def debug(self, message: str) -> None:
        if not self.logger:
            return
        self.logger.debug(message)

    def info(self, message: str) -> None:
        if not self.logger:
            return
        if message.startswith("[debug]"):
            return
        self.logger.info(message)

    def warning(
        self, message: str, *, once: bool = False, only_once: bool = False
    ) -> None:
        if not self.logger:
            return
        self.logger.warning(message)

    def error(self, message: str) -> None:
        if not self.logger:
            return
        self.logger.error(message)

    def stdout(self, message: str) -> None:
        pass

    def stderr(self, message: str) -> None:
        pass


class State(TypedDict):
    value: Literal[
        "requested",
        "pending",
        "awaiting_selection",
        "in_progress",
        "completed",
        "completed_with_errors",
        "failed",
        "cancelled",
        "cancelling",
        "paused",
        "pausing",
        "deleted",
        "deleting",
    ]
    # sub_state de yt-dlp y "Getting Info", "Collecting Entries"
    sub_state: NotRequired[str | None]
    sub_state_color: NotRequired[Color | None]
    # para un video progress es un string con 4.3MB/5MB, para una lista es un string con "x/y"
    progress_label: NotRequired[str | None]
    # `progress_value` número entre 0 y 1 que representa el progreso,
    # para un video es el porcentaje dividido por 100,
    # para una lista es el número de videos descargados dividido por el total
    progress_value: NotRequired[float | None]
    progress_color: NotRequired[Color | None]
    # para un video speed es un string con la velocidad MB/s KB/s, para una lista es un string con "x"e/s
    speed: NotRequired[str | None]
    time_spent: NotRequired[str | None]
    time_total: NotRequired[str | None]
    time_left: NotRequired[str | None]
    error_message: NotRequired[str | None]


class Info(TypedDict):
    url: str | None
    image: str | None
    file: str | None
    title: str | None
    platform: str | None
    type: Literal["video", "list", "unknown"]
    autor: str | None
    creation_date: str | None
    duration: str | None
