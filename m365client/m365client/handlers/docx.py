import m365client.server_interface as ServerInterface
import httpx
from unstructured.partition.docx import partition_docx

async def download_and_partition_docx(config: ServerInterface.StorageConfig):
    try:
        blob_url = ServerInterface.build_connection_string(
            config.base_url,
            ServerInterface.build_blob_download_string,
            config.container_name,
            config.blob_name,
        )
        doc_bytes = await ServerInterface.download_blob(
            blob_url, ServerInterface.async_download_blob, httpx.AsyncClient(timeout=30.0)
        )
        elements = partition_docx(file=doc_bytes)
        return elements
    except httpx.HTTPError as http_error:
        print(f"HTTP error occurred: {http_error}")
    except ValueError as value_error:
        print(f"Document format error: {value_error}")
    except Exception as general_error:
        print(f"An unexpected error occurred: {general_error}")

def extract_text_from_elements(elements):
    text = "\n".join([element.text for element in elements])
    return text