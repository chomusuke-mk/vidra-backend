from threading import Lock
import logging
import io
import os
from typing import Tuple, Any, Optional, List, Literal
import re


class StringIOHandler(logging.Handler):
    def __init__(self, log_stream: io.StringIO, lock: Lock):
        super().__init__()
        self.log_stream = log_stream
        self._lock = lock

    def emit(self, record):
        try:
            msg = self.format(record)
            with self._lock:
                self.log_stream.write(msg + "\n")
        except Exception:
            self.handleError(record)


class SinColoresFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style="%"):
        super().__init__(fmt, datefmt, style)  # type: ignore
        self.patron_ansi = re.compile(r"\x1b\[[0-9;]*m")

    def format(self, record):
        mensaje_original = super().format(record)
        return self.patron_ansi.sub("", mensaje_original)


def configure_logger(
    log_file: str, logger_name: str
) -> Tuple[logging.Logger, io.StringIO]:
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            contenido = f.read()
            f.close()
        log_stream = io.StringIO(contenido)
    else:
        log_stream = io.StringIO()
    log_stream.seek(0, io.SEEK_END)
    log_stream_handler = StringIOHandler(log_stream, Lock())
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    formatter = SinColoresFormatter(
        "%(asctime)s|%(levelname)s|%(message)s", datefmt="%Y/%m/%d %H:%M"
    )
    file_handler.setFormatter(formatter)
    log_stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(log_stream_handler)
    return logger, log_stream

def close_logger(logger: logging.Logger):
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)

def clean_string(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or ""

def get_logs_messages(
    logs: str,
    level: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]] = None,
) -> List[str]:
    if not logs:
        return []
    lines = logs.split("\n")
    if level is not None:
        lines = []
        for line in logs.split("\n"):
            if f"|{level}|" in line:
                parts = line.split(f"|{level}|", 1)
                if len(parts) > 1 and parts[1].strip():
                    lines.append(parts[1].strip())
    return lines


def to_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return int(text)
        except ValueError:
            return None
    return None


def to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def to_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
    return None


def bytes_to_human_readable(num_bytes: Optional[int | float], suffix: str = "") -> str:
    if num_bytes is None:
        return "--"

    # Lista de unidades de medida
    unidades = ["B", "KB", "MB", "GB", "TB", "PB"]

    # Vamos dividiendo por 1024 hasta que el número sea menor a 1024
    # o lleguemos a la unidad más grande (Petabytes)
    for unidad in unidades:
        if num_bytes < 1024.0:
            return f"{num_bytes:.0f}{unidad}{suffix}"
        num_bytes /= 1024.0

    # Si el archivo es ridículamente grande (más de 1024 PB), se queda en PB
    return f"{num_bytes:.0f}PB{suffix}"
