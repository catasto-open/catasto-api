from pathlib import Path

from pydantic import BaseModel


class LoggingBase(BaseModel):
    path: Path
    level: str
    retention: str
    rotation: str
    format_: str


class LoggerModel(BaseModel):
    logger: LoggingBase
