from m365server.azure_interface.blob_operations import IBlobDownloadStrategy
from azure.storage.blob import ContainerClient
from azure.core.exceptions import ResourceNotFoundError
from typing import Union
from io import BytesIO
from loguru import logger


class BlobDownloadStrategy(IBlobDownloadStrategy):
    def download_blob(self, container_client: ContainerClient, blob_name: str) -> bytes:
        logger.info(f'Downloading blob {blob_name}')
        try:
            blob_client = container_client.get_blob_client(blob_name)
            blob_data = blob_client.download_blob()
            return blob_data.content_as_bytes()
        except ResourceNotFoundError as e:
            logger.error(f"Blob '{blob_name}' not found: {e}")
            raise
        except Exception as ex:
            logger.error(f"Failed to download blob '{blob_name}': {ex}")
            raise
