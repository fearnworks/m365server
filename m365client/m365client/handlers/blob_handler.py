from abc import ABC, abstractmethod
from io import BytesIO
import m365client.server_interface as ServerInterface
import httpx
from loguru import logger 
class BlobFileHandler(ABC):
    async def download_file(self, config: ServerInterface.StorageConfig) -> BytesIO:
        try:
            logger.info(f"Downloading file from: {blob_url}")

            blob_url = ServerInterface.build_connection_string(
                config.base_url,
                ServerInterface.build_blob_download_string,
                config.container_name,
                config.blob_name,
            )
            file_bytes = await ServerInterface.download_blob(
                blob_url, ServerInterface.async_download_blob, httpx.AsyncClient(timeout=30.0),
            )
            logger.info(f"File downloaded successfully: {config.blob_name}")

            return file_bytes
        except httpx.HTTPError as http_error:
            logger.error(f"HTTP error occurred: {http_error}")
        except ValueError as value_error:
            logger.error(f"File format error: {value_error}")
        except Exception as general_error:
            logger.error(f"An unexpected error occurred: {general_error}")
    
    @abstractmethod
    def extract_text(self, file_bytes: BytesIO) -> str:
        pass




