from abc import ABC, abstractmethod
from typing import Union
from io import BytesIO

from azure.storage.blob import ContainerClient

class IBlobUploadStrategy(ABC):
    @abstractmethod
    def upload_blob(self, container_client: ContainerClient, blob_name: str, file_data: Union[str, BytesIO]):
        pass

class IBlobDownloadStrategy(ABC):
    @abstractmethod
    def download_blob(self, container_client: ContainerClient, blob_name: str) -> bytes:
        pass

class IBlobDeleteStrategy(ABC):
    @abstractmethod
    def delete_blob(self, container_client: ContainerClient, blob_name: str):
        pass
