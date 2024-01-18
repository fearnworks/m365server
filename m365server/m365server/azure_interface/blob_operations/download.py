from m365server.azure_interface.blob_operations import IBlobDownloadStrategy
from azure.storage.blob import ContainerClient
from azure.core.exceptions import ResourceNotFoundError
from typing import Union
from io import BytesIO
from loguru import logger


class BlobDownloadStrategy(IBlobDownloadStrategy):
    def download_blob(self, container_client: ContainerClient, blob_name: str) -> bytes:
        if not container_client or not blob_name:
            logger.error("Invalid input arguments for blob download")
            raise ValueError("Invalid input arguments for blob download")

        logger.info(f"Initiating download of blob '{blob_name}'")
        try:
            blob_client = container_client.get_blob_client(blob_name)
            blob_data = blob_client.download_blob()
            content_length = blob_data.size
            content_type = blob_client.get_blob_properties().content_settings.content_type

            logger.info(f"Downloading blob '{blob_name}' of size {content_length} bytes and content type '{content_type}'")
            downloaded_data = blob_data.content_as_bytes()
            logger.info(f"Successfully downloaded blob '{blob_name}' with size {len(downloaded_data)} bytes")

            return downloaded_data
        except ResourceNotFoundError as e:
            logger.error(f"Blob '{blob_name}' not found in container: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to download blob '{blob_name}': {e}")
            raise