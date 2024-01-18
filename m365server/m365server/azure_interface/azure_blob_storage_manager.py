from io import BytesIO
from typing import Dict, List, Union, Optional
from loguru import logger
import m365server.azure_interface as AzureInterface
import pandas as pd
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.identity import ClientSecretCredential

from m365server.azure_interface.configuration import AzureBlobStorageConfig, ServicePrincipalConfig
from m365server.azure_interface.blob_client import BlobServiceClientFactory
import m365server.azure_interface.blob_operations as BlobOperations

class AzureBlobStorageManager:
    """
    A class that manages interactions with Azure Blob Storage.
    """

    def __init__(self, config: AzureBlobStorageConfig) -> None:
        """
        Initialize the AzureBlobStorageManager.

        Args:
            config (AzureBlobStorageConfig): Configuration for Azure Blob Storage.
        """
        logger.info("Initializing AzureBlobStorageManager")
        self.blob_service_client = BlobServiceClientFactory.create_client(config)

        # Dynamically pull the list of container names from the storage account
        self.container_names: List[str] = [
            container.name for container in self.blob_service_client.list_containers()
        ]
        logger.info(f"Container names: {self.container_names}")

        # Initialize a dictionary of ContainerClients for the specified containers
        self.container_clients : Dict[str, ContainerClient] = {
            container_name: self.blob_service_client.get_container_client(container_name)
            for container_name in self.container_names
        }
        logger.info(f"Container clients initialized")

        self.upload_strategy = BlobOperations.BlobUploadStrategy()
        self.download_strategy = BlobOperations.BlobDownloadStrategy()
        self.delete_strategy = BlobOperations.BlobDeleteStrategy()


    # def _build_connection_string(self, config: AzureBlobStorageConfig) -> str:
    #     """
    #     Builds the connection string for Azure Blob Storage.

    #     Args:
    #         config (AzureBlobStorageConfig): The storage configuration.

    #     Returns:
    #         str: The connection string.
    #     """
    #     # Handle cases where service principal is used
    #     if config.service_principal_config:
    #         return f"https://{config.storage_account_name}.{config.storage_account_suffix}"
        
    #     # Handle key-based authentication
    #     return f"DefaultEndpointsProtocol=https;AccountName={config.storage_account_name};AccountKey={config.storage_account_key};EndpointSuffix={config.storage_account_suffix}"


    # def _use_service_principal(self, sp_config: ServicePrincipalConfig) -> BlobServiceClient:
    #     """
    #     Authenticate using a service principal and create a BlobServiceClient.

    #     Args:
    #         sp_config (ServicePrincipalConfig): The service principal configuration.

    #     Returns:
    #         BlobServiceClient: A client authenticated with the service principal.
    #     """
    #     credential = ClientSecretCredential(
    #         tenant_id=sp_config.tenant_id,
    #         client_id=sp_config.client_id,
    #         client_secret=sp_config.client_secret
    #     )
    #     blob_service_client = BlobServiceClient(
    #         account_url=f"https://{sp_config.storage_account_name}.{sp_config.storage_account_suffix}",
    #         credential=credential
    #     )
    #     return blob_service_client
    
    # def _validate_config(self, config: AzureBlobStorageConfig):
    #     if config.service_principal_config:
    #         if not all([config.service_principal_config.client_id, config.service_principal_config.client_secret, config.service_principal_config.tenant_id]):
    #             raise ValueError("Incomplete service principal configuration")
    #     elif not config.storage_account_key:
    #         raise ValueError("Storage account key is required for key-based authentication")

    # def _build_account_url(self, config: AzureBlobStorageConfig) -> str:
    #     return f"https://{config.storage_account_name}.{config.storage_account_suffix}"

        
    def upload_blob(self, container_name: str, blob_name: str, file_data: Union[str, BytesIO]):
        container_client = self.container_clients.get(container_name)
        self.upload_strategy.upload_blob(container_client, blob_name, file_data)

    def download_blob(self, container_name: str, blob_name: str) -> bytes:
        container_client = self.container_clients.get(container_name)
        return self.download_strategy.download_blob(container_client, blob_name)

    def delete_blob(self, container_name: str, blob_name: str):
        container_client = self.container_clients.get(container_name)
        self.delete_strategy.delete_blob(container_client, blob_name)


    def list_blobs(self, container_name: str) -> List[str]:
        """
        List all blobs in the container.
        Args:
            container_name (str): The name of the container to list blobs from.

        Returns:
            List[str]: A list of blob names in the container.
        """
        container_client = self.container_clients.get(container_name)
        if container_client:
            logger.info(f'Listing blobs in container "{container_name}"')
            blobs = [blob.name for blob in container_client.list_blobs()]
            logger.info(blobs)
            logger.info(
                f'Found {len(blobs)} blob(s) in container "{container_name}"'
            )
            return blobs
        else:
            logger.error(f'Container "{container_name}" not found')
            return []
        
    def list_containers(self) -> List[str]:
            """
            List all containers in the storage account.

            Returns:
                List[str]: A list of container names in the storage account.
            """
            return self.container_names   
            
    def log_container_info(self) -> None:
        """
        Log information about each container in the storage account for data discovery.
        """
        # Iterate through each container in the storage account
        for container_name in self.container_names:
            try:
                container_client = self.container_clients[container_name]
                blobs = list(container_client.list_blobs())
                num_blobs = len(blobs)
                total_size = sum(blob.size for blob in blobs)
                last_modified_times = [blob.last_modified for blob in blobs]
                earliest_modified_time = min(last_modified_times) if last_modified_times else None
                latest_modified_time = max(last_modified_times) if last_modified_times else None
                
                # Log container information
                logger.info(f"Container name: {container_name}")
                logger.info(f"Number of blobs: {num_blobs}")
                logger.info(f"Total size of blobs (bytes): {total_size}")
                logger.info(f"Earliest blob modification time: {earliest_modified_time}")
                logger.info(f"Latest blob modification time: {latest_modified_time}")

                # Log information about each blob within the container
                for blob in blobs:
                    logger.info(f"  Blob name: {blob.name}")
                    logger.info(f"  Blob size (bytes): {blob.size}")
                    logger.info(f"  Blob content type: {blob.content_settings.content_type}")
                    logger.info(f"  Blob last modified: {blob.last_modified}")

            except ResourceNotFoundError:
                logger.error(f"Container '{container_name}' not found")
            except Exception as ex:
                logger.error(f"Failed to retrieve information for container '{container_name}' - {str(ex)}")                

    def load_blob_to_dataframe(self, container_name: str, blob_name: str) -> pd.DataFrame:
        """
        Load a single blob to a pandas DataFrame.

        Args:
            container_name (str): The name of the container where the blob is located.
            blob_name (str): The name of the blob to load.

        Returns:
            pd.DataFrame: A DataFrame containing the data from the blob. 
                        If an error occurs, it logs the error and returns None.
        """
        container_client = self.container_clients.get(container_name)
        if container_client:
            try:
                blob_client = container_client.get_blob_client(blob_name)
                content_type = blob_client.get_blob_properties().content_settings.content_type
                blob_data = AzureInterface.BlobDataLoader.load_blob_content(container_client, blob_name)
                return AzureInterface.BlobDataLoader.load_blob_to_dataframe(blob_data, content_type)
            except Exception as ex:
                logger.error(f"Failed to load blob '{blob_name}' from container '{container_name}' - {str(ex)}")
                return None
        else:
            logger.error(f"Container '{container_name}' not found")
            return None
        
    def load_blob_sheet_to_dataframe(self, container_name: str, blob_name: str, sheet_name: str = None) -> pd.DataFrame:
        """
        Load a single sheet of an Excel blob to a pandas DataFrame.

        Args:
            container_name (str): The name of the container where the blob is located.
            blob_name (str): The name of the blob to load.
            sheet_name (str): The name of the sheet to load from the Excel file. If None, loads the first sheet.

        Raises:
            ValueError: If the container does not exist or if the blob's content type is not an Excel content type.
            Exception: If any other error occurs during the loading process.

        Returns:
            pd.DataFrame: A DataFrame containing the data from the blob's sheet.
        """
        container_client = self.container_clients.get(container_name)
        if container_client is None:
            raise ValueError(f"Container '{container_name}' not found")

        blob_client = container_client.get_blob_client(blob_name)
        content_type = blob_client.get_blob_properties().content_settings.content_type
        blob_data = AzureInterface.BlobDataLoader.load_blob_content(container_client, blob_name)

        if content_type not in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            raise ValueError(f"Content type '{content_type}' is not supported. This function only supports Excel content types.")

        try:
            with BytesIO(blob_data) as data:
                df = pd.read_excel(data, sheet_name=sheet_name)
                return df
        except Exception as ex:
            raise Exception(f"Failed to load blob '{blob_name}' into a DataFrame") from ex


    def load_blobs_to_dataframes(self, container_name: str) -> Dict[str, pd.DataFrame]:
        """
        Load all blobs from a container to pandas DataFrames.

        Args:
            container_name (str): The name of the container where the blobs are located.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary where keys are blob names, and values are 
                                    pandas DataFrames containing the data from the corresponding blob. 
                                    If an error occurs during the loading of a particular blob, 
                                    it logs the error and excludes the blob from the returned dictionary.
        """
        dataframes = {}
        container_client = self.container_clients.get(container_name)
        if container_client:
            blobs = container_client.list_blobs()
            for blob in blobs:
                logger.info(f"Loading blob '{blob.name}' from container '{container_name}'")
                df = self.load_blob_to_dataframe(container_name, blob.name)
                if df is not None:
                    logger.info(f"Successfully loaded blob '{blob.name}' from container '{container_name}'")
                    if isinstance(df, dict):
                        for sheet_name, sheet_df in df.items():
                            dataframes[f"{blob.name} - {sheet_name}"] = sheet_df
                    else:
                        dataframes[blob.name] = df
                else:
                    logger.error(f"Failed to load blob '{blob.name}' from container '{container_name}'")
            return dataframes
        else:
            logger.error(f"Container '{container_name}' not found")
            return {}


