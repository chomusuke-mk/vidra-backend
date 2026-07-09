from typing import TypedDict, Literal, Optional, NotRequired, Any
import logging


type Color = Literal[
    "green",  # completado
    "yellow",  # pausado
    "red",  # error
    "blue",  # en proceso
    "gray",  # cancelado
    "orange",  # error parcial
    "purple",  # esperando selección
    "cyan",  # extrayendo información
    "magenta",  # requested
]


class DownloadCancelled(Exception):
    """Excepción personalizada para indicar que la descarga ha sido cancelada"""


class DownloadPaused(Exception):
    """Excepción personalizada para indicar que la descarga ha sido pausada"""

class DownloadDeleted(Exception):
    """Excepción personalizada para indicar que la descarga ha sido eliminada"""

class YTDLPLoggerAdapter:
    """
    Clase que envuelve un logging.Logger estándar para que cumpla
    estrictamente con la interfaz _LoggerProtocol de yt-dlp.
    """

    def __init__(
        self, ydl: Optional[Any] = None, logger: Optional[logging.Logger] = None
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
        "extracting_information",
        "awaiting_selection",
        "in_progress",
        "completed",
        "completed_with_errors",
        "failed",
        "cancelled",
        "paused",
        "deleted",
    ]
    # sub_state de yt-dlp y "Getting Info", "Collecting Entries"
    sub_state: NotRequired[Optional[str]]
    sub_state_color: NotRequired[Optional[Color]]
    # para un video progress es un string con 4.3MB/5MB, para una lista es un string con "x/y"
    progress_label: NotRequired[Optional[str]]
    # `progress_value` número entre 0 y 1 que representa el progreso,
    # para un video es el porcentaje dividido por 100,
    # para una lista es el número de videos descargados dividido por el total
    progress_value: NotRequired[Optional[float]]
    progress_color: NotRequired[Optional[Color]]
    # para un video speed es un string con la velocidad MB/s KB/s, para una lista es un string con "x"e/s
    speed: NotRequired[Optional[str]]
    time_spent: NotRequired[Optional[str]]
    time_total: NotRequired[Optional[str]]
    time_left: NotRequired[Optional[str]]


class Info(TypedDict):
    url: Optional[str]
    image: Optional[str]
    file: Optional[str]
    title: Optional[str]
    platform: Optional[str]
    type: Literal["video", "list", "unknown"]
    autor: Optional[str]
    creation_date: Optional[str]
    duration: Optional[str]
