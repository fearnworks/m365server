from m365server.azure_interface.azure_blob_storage_manager import AzureBlobStorageManager, AzureBlobStorageConfig, build_connection_string
import pytest 
from unittest.mock import Mock

@pytest.fixture
def az_mgr() -> AzureBlobStorageManager:
    storage_account_name = "myaccount"
    storage_account_key = "mykey"
    config = AzureBlobStorageConfig(storage_account_name=storage_account_name, storage_account_key=storage_account_key)
    manager = AzureBlobStorageManager(config=config)
    return manager

def test_build_connection_string():
    """
    GIVEN a storage account name and key
    WHEN the build_connection_string method is called with the storage account name and key
    THEN it should return the expected connection string
    """

    # Arrange
    storage_account_name = "myaccount"
    storage_account_key = "mykey"
    storage_account_suffix = "core.windows.net"

    # Act
    conn_string = build_connection_string(storage_account_name, storage_account_key, suffix=storage_account_suffix)

    # Assert
    expected_conn_string = "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey==;EndpointSuffix=core.windows.net"
    assert conn_string == expected_conn_string

def test_build_connection_string_alternate_endpoint():
    """
    GIVEN a storage account name, key, and an alternate endpoint suffix
    WHEN the build_connection_string method is called with the storage account name, key, and alternate endpoint suffix
    THEN it should return the expected connection string with the alternate endpoint suffix
    """

    # Arrange
    storage_account_name = "myaccount"
    storage_account_key = "mykey"
    endpoint_suffix = "myendpoint"

    # Act
    conn_string = build_connection_string(storage_account_name, storage_account_key, endpoint_suffix)

    # Assert
    expected_conn_string = "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=mykey==;EndpointSuffix=myendpoint"
    assert conn_string == expected_conn_string

