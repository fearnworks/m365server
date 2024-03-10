from io import BytesIO
import m365client.server_interface as ServerInterface
import httpx
from unstructured.partition.md import partition_md

async def download_markdown(config: ServerInterface.StorageConfig) -> BytesIO:
    try:
        blob_url = ServerInterface.build_connection_string(
            config.base_url,
            ServerInterface.build_blob_download_string,
            config.container_name,
            config.blob_name,
        )
        markdown_bytes = await ServerInterface.download_blob(
            blob_url, ServerInterface.async_download_blob, httpx.AsyncClient(timeout=30.0),
        )
        return markdown_bytes
    except httpx.HTTPError as http_error:
        print(f"HTTP error occurred: {http_error}")
    except ValueError as value_error:
        print(f"Document format error: {value_error}")
    except Exception as general_error:
        print(f"An unexpected error occurred: {general_error}")

def extract_text_from_markdown(markdown_bytes: BytesIO):
    markdown_text = markdown_bytes.read().decode("utf-8")
    elements = partition_md(text=markdown_text)
    text = "\n".join([element.text for element in elements])
    return text