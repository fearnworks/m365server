from loguru import logger 
from typing import Callable

def build_blob_download_string(container: str, blob: str):
    command = f"blob_storage/download_blob/{container}?blob_name={blob}"
    logger.info(command)
    return command

def build_connection_string(
    base_url: str, endpoint_strat: Callable[..., str], container: str, blob: str
) -> str:
    command = endpoint_strat(container, blob)
    return f"{base_url}/{command}"

