from io import BytesIO
from typing import Dict, List, Union, Optional
from loguru import logger
import m365server.azure_interface as AzureInterface
import pandas as pd
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.identity import ClientSecretCredential

from m365server.azure_interface.configuration import AzureBlobStorageConfig, ServicePrincipalConfig
from m365server.azure_interface.blob_client import BlobServiceClientFactory
import m365server.azure_interface.blob_operations as BlobOperations
from m365server.azure_interface.container_manager import ContainerManager

class AzureBlobStorageManager:
    """
    A class that manages interactions with Azure Blob Storage.
    """

    def __init__(self, config: AzureBlobStorageConfig) -> None:
        """
        Initialize the AzureBlobStorageManager.

        Args:
            config (AzureBlobStorageConfig): Configuration for Azure Blob Storage.
        """
        logger.info("Initializing AzureBlobStorageManager")
        self.blob_service_client = BlobServiceClientFactory.create_client(config)
        self.container_manager = ContainerManager(self.blob_service_client)

        self.upload_strategy = BlobOperations.BlobUploadStrategy()
        self.download_strategy = BlobOperations.BlobDownloadStrategy()
        self.delete_strategy = BlobOperations.BlobDeleteStrategy()

    def upload_blob(self, container_name: str, blob_name: str, file_data: Union[str, BytesIO]):
        container_client = self.container_clients.get(container_name)
        self.upload_strategy.upload_blob(container_client, blob_name, file_data)

    def download_blob(self, container_name: str, blob_name: str) -> bytes:
        container_client = self.container_clients.get(container_name)
        return self.download_strategy.download_blob(container_client, blob_name)

    def delete_blob(self, container_name: str, blob_name: str):
        container_client = self.container_clients.get(container_name)
        self.delete_strategy.delete_blob(container_client, blob_name)

    def set_upload_strategy(self, new_strategy: BlobOperations.IBlobUploadStrategy):
        self.upload_strategy = new_strategy

    def set_download_strategy(self, new_strategy: BlobOperations.IBlobDownloadStrategy):
        self.download_strategy = new_strategy

    def set_delete_strategy(self, new_strategy: BlobOperations.IBlobDeleteStrategy):
        self.delete_strategy = new_strategy

    def list_blobs(self, container_name: str) -> List[str]:
        return self.container_manager.list_blobs(container_name)
        
    def list_containers(self) -> List[str]:
        return self.container_manager.list_containers()
    
    def log_container_info(self) -> None:
        self.container_manager.log_container_info()
