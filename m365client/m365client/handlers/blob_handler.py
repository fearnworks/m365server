## m365client/handlers/blob.py

import io 
from typing import Callable, List

from loguru import logger 
from m365client.schemas.storage_config import StorageConfig
import httpx 



from abc import ABC, abstractmethod
from io import BytesIO
from typing import Callable
from m365client.schemas import StorageConfig
import httpx
from loguru import logger 

def build_blob_download_string(container: str, blob: str):
    command = f"blob_storage/download_blob/{container}?blob_name={blob}"
    logger.info(command)
    return command


def build_connection_string(
    base_url: str, endpoint_strat: Callable[..., str], container: str, blob: str
) -> str:
    command = endpoint_strat(container, blob)
    return f"{base_url}/{command}"

async def upload_blob(config: StorageConfig, file_bytes: bytes, timeout=120) -> httpx.Response:
    upload_url = f"{config.base_url}/blob_storage/upload_blob/{config.container_name}?blob_name={config.blob_name}"
    data = {
        "blob_name": (None, config.blob_name),
        "file": (config.blob_name, file_bytes, "application/octet-stream"),
    }
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(upload_url, files=data)
    return response

async def async_download_blob(
    blob_url: str, client: httpx.AsyncClient = httpx.AsyncClient()
) -> io.BytesIO:
    logger.info(blob_url)
    data = io.BytesIO()
    async with client.stream("GET", blob_url) as response:
        response.raise_for_status()
        async for chunk in response.aiter_bytes():
            data.write(chunk)
    data.seek(0)
    return data

def download_blob(
    connection_string: str,
    request: Callable[..., bytes],
    client: httpx.AsyncClient | httpx.Client,
):
    logger.info(connection_string)
    return request(connection_string, client)

def list_blobs(
    base_url: str, container_name: str, path_filter: str | None = None
) -> dict[str, List[str]]:
    """
    Lists all blobs in Azure Blob Container.
    If path_filter is provided, only blobs matching the path_filter will be returned.
    """
    # Send the request to get the blobs using httpx
    response = httpx.get(f"{base_url}/blob_storage/list_blobs/{container_name}")
    blobs = response.json().get("blobs", [])

    # If a path_filter is provided, filter the blobs accordingly
    if path_filter:
        filtered_blobs = [blob for blob in blobs if blob.startswith(path_filter)]
    else:
        filtered_blobs = blobs

    return {"blobs": filtered_blobs}



class BlobFileHandler(ABC):
    async def download_file(self, config: StorageConfig) -> BytesIO:
        try:
            logger.info(f"Downloading file from: {blob_url}")

            blob_url = build_connection_string(
                config.base_url,
                build_blob_download_string,
                config.container_name,
                config.blob_name,
            )
            file_bytes = await download_blob(
                blob_url, async_download_blob, httpx.AsyncClient(timeout=30.0),
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




