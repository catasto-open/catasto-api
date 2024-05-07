from pathlib import Path

from pydantic import BaseModel


class LoggingBase(BaseModel):
    path: Path
    level: str
    enqueue: bool
    retention: str
    rotation: str
    format_: str


class LoggerModel(BaseModel):
    logger: LoggingBase
