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


class MinioClient(Minio):
    """
    Minio client Georoma
    """

    def __init__(self):
        super().__init__(
            cfg.MINIO_BASEURL,
            access_key=cfg.MINIO_ACCESS_KEY, # "e5NDexDVLlhTIvCd",
            secret_key=cfg.MINIO_SECRET_KEY, # "xjnSuoApCzXQP4XLVFecULO4KoqOAduv",
            secure=False  # http for False, https for True,
        )


class LocalStorageClient():
    """
    Local base directory client
    """

    def __init__(self, path: str = None):
        base_path = Path(cfg.LOCAL_STORAGE_BASEPATH)
        if path:
            base_path = base_path / path
        if not base_path.exists():
            base_path.mkdir()
        self.base_path = base_path


def get_storage_clients():
    minio = MinioClient()
    local = LocalStorageClient(path="geofeeder")
    return {"client": minio, "local_storage": local}
