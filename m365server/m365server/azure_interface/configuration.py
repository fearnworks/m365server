import os
from typing import Optional
from dataclasses import dataclass, field


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

def get_default_config()-> AzureBlobStorageConfig:
        storage_account_key: str = os.getenv("STORAGE_ACCOUNT_KEY")
        storage_account_name: str = os.getenv("STORAGE_ACCOUNT_NAME")
        azure_suffix: str = os.getenv('AZURE_ENDPOINT_SUFFIX')
        config = AzureBlobStorageConfig(storage_account_key=storage_account_key, storage_account_name=storage_account_name, storage_account_suffix=azure_suffix)
        return config