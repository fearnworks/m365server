from dataclasses import dataclass
import httpx
from typing import List

@dataclass
class StorageConfig:
    base_url: str
    container_name: str
    blob_name: str
    
    
@dataclass
class StorageSheetConfig(StorageConfig):
    sheet_name: str


def list_containers(base_url: str) -> dict[str, List[str]]:
    """
    Lists all containers in Azure Blob Storage.
    """
    # Send the request to get the containers using httpx
    response = httpx.get(f"{base_url}/blob_storage/list_containers")
    containers = response.json().get("containers", [])

    return {"containers": containers}