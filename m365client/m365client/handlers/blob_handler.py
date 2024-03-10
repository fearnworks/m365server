from abc import ABC, abstractmethod
from io import BytesIO
import m365client.server_interface as ServerInterface
import httpx

class BlobFileHandler(ABC):
    async def download_file(self, config: ServerInterface.StorageConfig) -> BytesIO:
        try:
            blob_url = ServerInterface.build_connection_string(
                config.base_url,
                ServerInterface.build_blob_download_string,
                config.container_name,
                config.blob_name,
            )
            file_bytes = await ServerInterface.download_blob(
                blob_url, ServerInterface.async_download_blob, httpx.AsyncClient(timeout=30.0),
            )
            return file_bytes
        except httpx.HTTPError as http_error:
            print(f"HTTP error occurred: {http_error}")
        except ValueError as value_error:
            print(f"File format error: {value_error}")
        except Exception as general_error:
            print(f"An unexpected error occurred: {general_error}")
    
    @abstractmethod
    def extract_text(self, file_bytes: BytesIO) -> str:
        pass



