from typing import TypedDict, Literal, Optional, NotRequired


type Color = Literal["green", "yellow", "red", "blue", "gray"]


class DownloadCancelled(Exception):
    """Excepción personalizada para indicar que la descarga ha sido cancelada"""


class DownloadPaused(Exception):
    """Excepción personalizada para indicar que la descarga ha sido pausada"""


class State(TypedDict):
    value: Literal[
        "requested",
        "pending",
        "identifying",
        "wait_for_selection",
        "in_progress",
        "completed",
        "failed",
        "canceled",
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
