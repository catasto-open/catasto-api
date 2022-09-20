from dataclasses import dataclass
from httpx import AsyncClient
from pathlib import Path
from miniopy_async import Minio

from app.config.config import configuration as cfg
from app.config.logging import create_logger


logger = create_logger(name="app.config.client")


class HttpClient(AsyncClient):
    """
    HTTP Client
    """

    pass
