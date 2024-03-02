from dotenv import load_dotenv, find_dotenv
import httpx
from loguru import logger
import httpx
import pandas as pd
import io
from typing import Callable, List, Dict
import os
load_dotenv(find_dotenv())
from dataclasses import dataclass



@dataclass
class StorageConfig:
    base_url: str
    container_name: str
    blob_name: str


def list_containers(base_url: str) -> dict[str, List[str]]:
    """
    Lists all containers in Azure Blob Storage.
    """
    # Send the request to get the containers using httpx
    response = httpx.get(f"{base_url}/blob_storage/list_containers")
    containers = response.json().get("containers", [])

    return {"containers": containers}

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


def build_blob_download_string(container: str, blob: str):
    command = f"blob_storage/download_blob/{container}?blob_name={blob}"
    logger.info(command)
    return command


def build_connection_string(
    base_url: str, endpoint_strat: Callable[..., str], container: str, blob: str
) -> str:
    command = endpoint_strat(container, blob)
    return f"{base_url}/{command}"


def download_blob(
    connection_string: str,
    request: Callable[..., bytes],
    client: httpx.AsyncClient | httpx.Client,
):
    logger.info(connection_string)
    return request(connection_string, client)


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


async def write_to_parquet(
    df: pd.DataFrame, parquet_path: str, engine: str = "pyarrow"
):
    df.to_parquet(parquet_path, engine=engine)  # type: ignore


async def read_file_as_bytes(file_path: str) -> bytes:
    with open(file_path, "rb") as file:
        file_bytes = file.read()
    return file_bytes


async def upload_blob(config: StorageConfig, file_bytes: bytes, timeout=60) -> httpx.Response:
    upload_url = f"{config.base_url}/blob_storage/upload_blob/{config.container_name}?blob_name={config.blob_name}"
    data = {
        "blob_name": (None, config.blob_name),
        "file": (config.blob_name, file_bytes, "application/octet-stream"),
    }
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(upload_url, files=data)
    return response


def load_blob_sheet_to_dataframe(
    blob_data: io.BytesIO, sheet_name: str = "Sheet1"
) -> pd.DataFrame:
    try:
        df = pd.read_excel(blob_data, sheet_name=sheet_name)  # type: ignore
        return df
    except Exception as ex:
        raise Exception(f"Failed to load blob into a DataFrame") from ex

def load_all_sheets_from_blob(blob_data: io.BytesIO) -> Dict[str, pd.DataFrame]:
    # Read Excel file without loading any specific sheet to get the sheet names
    xls = pd.ExcelFile(blob_data, engine="openpyxl")
    sheet_names = xls.sheet_names

    # Dictionary to store DataFrames for each sheet
    sheets_data = {}

    for sheet_name in sheet_names:
        # Reset the pointer to the beginning of the blob data for each read
        blob_data.seek(0)

        # Load each sheet using the provided function
        df = load_blob_sheet_to_dataframe(blob_data, sheet_name=sheet_name)
        sheets_data[sheet_name] = df

    return sheets_data


async def upload_parquet(
    df: pd.DataFrame, config: StorageConfig, artifacts_dir: str = "/artifacts"
):
    # Create the artifacts directory if it doesn't exist
    os.makedirs(artifacts_dir, exist_ok=True)

    # Define the path to the Parquet file in the artifacts directory
    parquet_path = os.path.join(artifacts_dir, config.blob_name)

    # Write the goals DataFrame to a Parquet file in the artifacts directory
    await write_to_parquet(df, parquet_path)

    # Read the Parquet file as bytes
    file_bytes = await read_file_as_bytes(parquet_path)

    # Upload the blob
    response = await upload_blob(config, file_bytes)

    if response.status_code == 200:
        logger.info(response.json()["message"])
    else:
        logger.error(
            f"Failed to upload file to blob '{config.blob_name}' in container '{config.container_name}' - {response.text}"
        )
