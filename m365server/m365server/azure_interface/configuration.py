import os
from typing import Optional
from dataclasses import dataclass, field
from loguru import logger 
@dataclass
class ServicePrincipalConfig:
    client_id: str
    client_secret: str
    tenant_id: str

@dataclass
class AzureBlobStorageConfig:
    storage_account_key: str
    storage_account_name: str
    storage_account_suffix: str = "core.windows.net"
    service_principal_config: Optional[ServicePrincipalConfig] = field(default=None)

    def should_use_service_principal(self) -> bool:
        """
        Determines if the service principal should be used for authentication.

        Returns:
            bool: True if service principal should be used, False otherwise.
        """
        return self.service_principal_config is not None

def get_default_config() -> AzureBlobStorageConfig:
    storage_account_key: str = os.getenv("STORAGE_ACCOUNT_KEY")
    storage_account_name: str = os.getenv("STORAGE_ACCOUNT_NAME")
    azure_suffix: str = os.getenv('AZURE_ENDPOINT_SUFFIX')

    # Check if service principal environment variables are set
    if all([os.getenv("AZURE_CLIENT_ID"), os.getenv("AZURE_CLIENT_SECRET"), os.getenv("AZURE_TENANT_ID")]):
        logger.info("Using service principal for authentication")
        service_principal_config = ServicePrincipalConfig(
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
            tenant_id=os.getenv("AZURE_TENANT_ID")
        )
        
        return AzureBlobStorageConfig(
            storage_account_key=storage_account_key,
            storage_account_name=storage_account_name,
            storage_account_suffix=azure_suffix,
            service_principal_config=service_principal_config
        )
    else:
        logger.info("Using storage account key for authentication")
        return AzureBlobStorageConfig(
            storage_account_key=storage_account_key,
            storage_account_name=storage_account_name,
            storage_account_suffix=azure_suffix
        )
