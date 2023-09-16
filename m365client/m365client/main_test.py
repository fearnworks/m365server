from m365client.server_interface import build_connection_string, list_blobs, download_blob, build_blob_download_string, async_download_blob, upload_blob, read_file_as_bytes, write_to_parquet, StorageConfig
import os
from typing import AsyncIterator
import httpx
from io import BytesIO
import pytest 
import pandas as pd
from pytest_httpx import HTTPXMock, IteratorStream

def get_mock_blob(conn_str: str, client):
    # Create a BytesIO object with some test data
    data = b"Hello, world!"
    return BytesIO(data)


@pytest.fixture
def sample_df():
    data = {
        "A": [1, 2, 3],
        "B": ["a", "b", "c"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_storage_config():
    base_url = "http://m365-adapter:72000"
    container_name = "test-goals"
    mock_config = StorageConfig(
        base_url=base_url,
        container_name=container_name,
        blob_name="part-00000-fa61f12f-4e00-4861-8228-f2a0f86f97b9-c000.snappy.parquet",
    )
    return mock_config


def test_should_build_connection_string_from_variables():
    base_url = "http://localhost:72000"
    command = build_blob_download_string
    container = "test-finance"
    blob = "DateTable.parquet"
    assert (
        build_connection_string(base_url, command, container, blob)
        == "http://localhost:72000/blob_storage/download_blob/test-finance?blob_name=DateTable.parquet"
    )


def test_should_build_download_string_from_variables():
    command = "download_blob"
    container = "test-finance"
    blob = "DateTable.parquet"
    expected_str = (
        "blob_storage/download_blob/test-finance?blob_name=DateTable.parquet"
    )
    assert build_blob_download_string(container, blob) == expected_str


def test_should_stream_bytesio_object():
    conn_str = "http://localhost:72000/test-finance/DateTable.parquet"
    client = httpx.AsyncClient()
    # Call download_blob with the mock get_blob function
    result = download_blob(conn_str, get_mock_blob, client)
    # Assert that the returned data matches the test data
    assert result.getvalue() == b"Hello, world!"


@pytest.mark.anyio
async def test_async_download_should_return_dataframe(httpx_mock: HTTPXMock):
    blob_url = "http://localhost:72000/blob_storage/download_blob/test-finance?blob_name=DateTable.parquet"
    httpx_mock.add_response(stream=IteratorStream([b"part 1", b"part 2"]))
    async with httpx.AsyncClient() as client:
        response = await async_download_blob(blob_url, httpx.AsyncClient())
    # Assert that the returned data matches the test data
    assert isinstance(response, BytesIO)


@pytest.mark.anyio
async def test_bad_blob_should_raise_404_error(httpx_mock: HTTPXMock):
    blob_url = "http://localhost:72000/blob_storage/download_blob/test-finance?blob_name=NonExistentBlob.parquet"
    httpx_mock.add_exception(
        httpx.HTTPStatusError(
            message="404 Blob Not Found",
            request=httpx.Request(
                "GET",
                "http://localhost:72000/download_blob/test-finance?blob_name=NonExistentBlob.parquet",
            ),
            response=httpx.Response(404, content=b"Not Found"),
        )
    )
    async with httpx.AsyncClient() as client:
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await async_download_blob(blob_url, client)
    assert "404" in str(exc_info.value)


def test_timeout(httpx_mock: HTTPXMock):
    with httpx.Client() as client:
        with pytest.raises(httpx.TimeoutException):
            client.get("https://test_url")


@pytest.mark.anyio
async def test_upload_blob_should_return_200_response(
    httpx_mock: HTTPXMock, mock_storage_config: StorageConfig
):
    mock_storage_config.blob_name = "CleanedGoals.parquet"
    file_bytes = b"some test data"
    httpx_mock.add_response(status_code=200, json={"message": "Upload successful"})
    response = await upload_blob(mock_storage_config, file_bytes)
    # Assert that the returned response has status code 200
    assert response.status_code == 200


@pytest.mark.anyio
async def test_upload_blob_should_raise_error_for_bad_url(
    httpx_mock: HTTPXMock, mock_storage_config: StorageConfig
):
    mock_storage_config.blob_name = "NonExistentBlob.parquet"

    blob_url = "http://localhost:72000/blob_storage/upload_blob/test-goals?blob_name=NonExistentBlob.parquet"
    file_bytes = b"some test data"
    httpx_mock.add_exception(
        httpx.HTTPStatusError(
            message="404 Blob Not Found",
            request=httpx.Request("POST", blob_url),
            response=httpx.Response(404, content=b"Not Found"),
        )
    )
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await upload_blob(mock_storage_config, file_bytes)
    assert "404" in str(exc_info.value)


import tempfile


@pytest.mark.anyio
async def test_read_file_as_bytes(sample_df):
    # Define path to write to
    path = "test.parquet"

    # Write DataFrame to Parquet
    sample_df.to_parquet(path)

    # Read the file as bytes
    file_bytes = await read_file_as_bytes(path)

    # Write bytes to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=True) as temp:
        temp.write(file_bytes)
        temp.flush()

        # Read the Parquet file back as a DataFrame
        df_from_bytes = pd.read_parquet(temp.name)

    # Check that the DataFrame matches the original
    pd.testing.assert_frame_equal(df_from_bytes, sample_df)

    # Cleanup
    os.remove(path)


@pytest.mark.anyio
async def test_list_blobs_with_filter(httpx_mock: HTTPXMock):
    base_url = "http://localhost:72000"
    container_name = "test-container"
    path_filter = "folder/"

    # Mock response for the blob listing
    mock_response = {"blobs": ["folder/file1.xlsx", "folder/file2.xlsx", "file3.xlsx"]}
    httpx_mock.add_response(
        url=f"{base_url}/blob_storage/list_blobs/{container_name}", json=mock_response
    )

    # Test without filtering
    result_without_filter = list_blobs(base_url, container_name)
    assert result_without_filter == {
        "blobs": ["folder/file1.xlsx", "folder/file2.xlsx", "file3.xlsx"]
    }

    # Test with filtering
    result_with_filter = list_blobs(base_url, container_name, path_filter)
    assert result_with_filter == {"blobs": ["folder/file1.xlsx", "folder/file2.xlsx"]}
