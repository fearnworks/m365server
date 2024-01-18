from typing import List
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError
from loguru import logger

class ContainerManager:
    def __init__(self, blob_service_client: BlobServiceClient):
        try:
            self.blob_service_client = blob_service_client
            self.container_clients = {
                container.name: blob_service_client.get_container_client(container.name) 
                for container in self.blob_service_client.list_containers()
            }
        except Exception as e:
            logger.error(f"Failed to initialize ContainerManager: {e}")
            raise
        
    def get_container_client(self, container_name: str) -> ContainerClient:
        """
        Retrieves the ContainerClient for the specified container name.

        Args:
            container_name (str): The name of the container.

        Returns:
            ContainerClient: The client for the specified container.
        """
        if container_name not in self.container_clients:
            logger.info(f"ContainerClient for '{container_name}' not found, creating new one.")
            self.container_clients[container_name] = self.blob_service_client.get_container_client(container_name)
        return self.container_clients[container_name]
    
    def list_blobs(self, container_name: str) -> List[str]:
        if container_name not in self.container_clients:
            logger.error(f'Container "{container_name}" not found')
            return []

        container_client = self.container_clients[container_name]
        logger.info(f'Listing blobs in container "{container_name}"')
        blobs = [blob.name for blob in container_client.list_blobs()]
        logger.info(blobs)
        logger.info(f'Found {len(blobs)} blob(s) in container "{container_name}"')
        return blobs
    
    def list_containers(self) -> List[str]:
        return list(self.container_clients.keys())

    def log_container_info(self):
        for container_name in self.container_clients.keys():
            try:
                container_client = self.container_clients[container_name]
                blobs = list(container_client.list_blobs())
                num_blobs = len(blobs)
                total_size = sum(blob.size for blob in blobs)
                last_modified_times = [blob.last_modified for blob in blobs]
                earliest_modified_time = min(last_modified_times) if last_modified_times else None
                latest_modified_time = max(last_modified_times) if last_modified_times else None

                logger.info(f"Container name: {container_name}")
                logger.info(f"Number of blobs: {num_blobs}")
                logger.info(f"Total size of blobs (bytes): {total_size}")
                logger.info(f"Earliest blob modification time: {earliest_modified_time}")
                logger.info(f"Latest blob modification time: {latest_modified_time}")

                for blob in blobs:
                    logger.info(f"  Blob name: {blob.name}")
                    logger.info(f"  Blob size (bytes): {blob.size}")
                    logger.info(f"  Blob content type: {blob.content_settings.content_type}")
                    logger.info(f"  Blob last modified: {blob.last_modified}")

            except ResourceNotFoundError:
                logger.error(f"Container '{container_name}' not found")
                
            except Exception as ex:
                logger.error(f"Failed to retrieve information for container '{container_name}': {ex}")