from m365server.azure_interface.blob_operations import IBlobDeleteStrategy
from azure.storage.blob import ContainerClient
from azure.core.exceptions import ResourceNotFoundError

from loguru import logger

class BlobDeleteStrategy(IBlobDeleteStrategy):
    def delete_blob(self, container_client: ContainerClient, blob_name: str):
        logger.info(f'Deleting blob "{blob_name}"')
        try:
            container_client.delete_blob(blob_name)
            logger.info(f"Successfully deleted blob '{blob_name}'")
        except Exception as ex:
            logger.error(f"Failed to delete blob '{blob_name}': {ex}")
            raise
