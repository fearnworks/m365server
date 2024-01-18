from m365server.azure_interface.blob_operations import IBlobUploadStrategy
from azure.storage.blob import ContainerClient
from typing import Union
from io import BytesIO
from loguru import logger

class BlobUploadStrategy(IBlobUploadStrategy):
    def upload_blob(self, container_client: ContainerClient, blob_name: str, file_data: Union[str, BytesIO]):
        logger.info(f"Uploading data to blob '{blob_name}'")
        try:
            if isinstance(file_data, str):
                logger.info(f"Detected file data as string, attempting to open file at path: {file_data}")
                with open(file_data, "rb") as file:
                    container_client.upload_blob(name=blob_name, data=file, overwrite=True)
            elif isinstance(file_data, BytesIO):
                logger.info(f"Detected file data as BytesIO, uploading directly.")
                container_client.upload_blob(name=blob_name, data=file_data.getvalue(), overwrite=True)
            else:
                logger.error(f"Unsupported data type for file_data: {type(file_data).__name__}")
                return

            logger.info(f"Successfully uploaded data to blob '{blob_name}'")
        except azure.core.exceptions.HttpResponseError as e:
            logger.error(f"HTTP error during blob upload: {e}")
            raise
        except azure.core.exceptions.AzureError as e:
            logger.error(f"Azure error during blob upload: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during blob upload: {e}")
            raise
