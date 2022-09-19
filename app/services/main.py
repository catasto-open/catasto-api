from app.config.client import MinioClient, LocalStorageClient


class StorageClientSessionContext:
    def __init__(
        self, 
        client: MinioClient,
        local_client: LocalStorageClient
    ):
        self.client = client
        self.local_client = local_client


class LocalStorageClientSessionContext:
    def __init__(
        self, 
        client: LocalStorageClient
    ):
        self.client = client


class AppService(StorageClientSessionContext):
    pass


class AppValidation(LocalStorageClientSessionContext):
    pass