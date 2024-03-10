## m365client/handlers/parquet.py

import os 
import pandas as pd 
from loguru import logger 
from m365client.schemas.storage_config import StorageConfig
from m365client.handlers import upload_blob, read_file_as_bytes

def filter_parquet_part_files(file_names):
    logger.info(file_names)
    parts = [file_name for file_name in file_names if file_name.startswith('part') and file_name.endswith('.parquet')]
    logger.info(parts)  
    return parts


async def write_to_parquet(
    df: pd.DataFrame, parquet_path: str, engine: str = "pyarrow"
):
    dir_name = os.path.dirname(parquet_path)

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    df.to_parquet(parquet_path, engine=engine)  # type: ignore



async def upload_parquet(
    df: pd.DataFrame, config: StorageConfig, artifacts_dir: str = "/artifacts", timeout=120
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
