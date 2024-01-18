from fastapi import APIRouter, File, UploadFile, Path, Query
import io
from fastapi.responses import StreamingResponse
from fastapi.exceptions import HTTPException
from m365server.azure_interface.azure_blob_storage_manager import AzureBlobStorageManager,  ResourceNotFoundError
from m365server.azure_interface.configuration import get_default_config
from m365server.deps import get_cache

from loguru import logger
import tempfile

router = APIRouter()

@router.post("/upload_blob/{container_name}")
async def upload_blob_bytes(container_name: str, blob_name: str, file: UploadFile = File(...)):
    """
    Uploads a file to a blob in Azure Blob Storage.
    """
    logger.info('Upload blob')
    storage_manager = AzureBlobStorageManager(get_default_config())
    file_data = io.BytesIO(await file.read())
    storage_manager.upload_blob(container_name, blob_name, file_data)
    return {"message": f"File uploaded to blob '{blob_name}' in container '{container_name}'"}

@router.get("/download_blob/{container_name}")
async def download_blob(container_name: str = Path(..., description="The name of the container where the blob is located."),
                         blob_name: str = Query(..., description="The name of the blob to download the data from.")):
    """
    Downloads data from a blob and returns it as a stream.
    """
    logger.info(f"Downloading blob {blob_name} from container {container_name}")
    storage_manager = AzureBlobStorageManager(get_default_config())
    try:
        blob_data = storage_manager.download_blob(container_name, blob_name)
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail=f"Blob '{blob_name}' not found in container '{container_name}'.")
    return StreamingResponse(io.BytesIO(blob_data), media_type="application/octet-stream")


def delete_blob(self, container_name: str, blob_name: str) -> None:
        """
        Deletes a blob from a specified container.
        
        Args:
            container_name (str): The name of the container where the blob is located.
            blob_name (str): The name of the blob to be deleted.
        """
        storage_manager = AzureBlobStorageManager(get_default_config())
        container_client = self.container_clients.get(container_name)
        if container_client:
            logger.info(f'Deleting blob "{blob_name}"')
            container_client.delete_blob(blob_name)
            logger.info(f'Successfully deleted blob "{blob_name}"')
        else:
            logger.error(f"Container '{container_name}' not found")

@router.get("/list_blobs/{container_name}")
async def list_blobs(container_name: str = Path(..., description="The name of the container to list the blobs from.")):
    """
    Lists the blobs in a specified container.
    """
    storage_manager = AzureBlobStorageManager(get_default_config())
    blobs = storage_manager.list_blobs(container_name)
    blob_names = [blob for blob in blobs]
    return {"blobs": blob_names}

@router.get("/list_containers")
async def list_containers():
    """
    Lists all containers in the storage account.
    """
    storage_manager = AzureBlobStorageManager(get_default_config())
    containers = storage_manager.list_containers()
    container_names = [container for container in containers]
    logger.info(container_names)
    return {"containers": container_names}

@router.get("/list_container_info")
async def list_container_info():
    """
    Retrieves information about a specified container.
    """
    storage_manager = AzureBlobStorageManager(get_default_config())
    container_info = storage_manager.log_container_info()
    return {"container_info": container_info}