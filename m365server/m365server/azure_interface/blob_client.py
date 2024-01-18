import os
from azure.storage.blob import BlobServiceClient
from azure.identity import ClientSecretCredential, AzureAuthorityHosts
from loguru import logger
from m365server.azure_interface.configuration import AzureBlobStorageConfig


class BlobServiceClientFactory:
    @staticmethod
    def create_client(config: AzureBlobStorageConfig) -> BlobServiceClient:
        """
        Creates and returns a BlobServiceClient based on the provided configuration.

        Args:
            config (AzureBlobStorageConfig): The configuration for the Azure Blob Storage.

        Returns:
            BlobServiceClient: The client to interact with Azure Blob Storage.
        """
        if config.service_principal_config:
            return BlobServiceClientFactory._create_client_with_service_principal(config)
        else:
            return BlobServiceClientFactory._create_client_with_connection_string(config)

    @staticmethod
    def _create_client_with_service_principal(config: AzureBlobStorageConfig) -> BlobServiceClient:
        """
        Creates a BlobServiceClient using service principal credentials.

        Args:
            config (AzureBlobStorageConfig): The configuration for the Azure Blob Storage.

        Returns:
            BlobServiceClient: The client to interact with Azure Blob Storage.
        """
        logger.info("Creating client with service principal credentials")
        authority_host = os.getenv("AZURE_AUTHORITY_HOST", AzureAuthorityHosts.AZURE_PUBLIC_CLOUD)
        logger.info(f"Using authority host: {authority_host}")
        credential = ClientSecretCredential(
            tenant_id=config.service_principal_config.tenant_id,
            client_id=config.service_principal_config.client_id,
            client_secret=config.service_principal_config.client_secret,
            authority=authority_host
        )
        account_url = f"https://{config.storage_account_name}.{config.storage_account_suffix}"
        logger.info(f"Using account url: {account_url}")
        client = BlobServiceClient(account_url=account_url, credential=credential)
        logger.info("Successfully created client with service principal credentials")
        return client
    
    @staticmethod
    def _create_client_with_connection_string(config: AzureBlobStorageConfig) -> BlobServiceClient:
        """
        Creates a BlobServiceClient using a connection string.

        Args:
            config (AzureBlobStorageConfig): The configuration for the Azure Blob Storage.

        Returns:
            BlobServiceClient: The client to interact with Azure Blob Storage.
        """
        logger.info("Creating client with user credentials")
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={config.storage_account_name};AccountKey={config.storage_account_key};EndpointSuffix={config.storage_account_suffix}"
        return BlobServiceClient.from_connection_string(connection_string)
