from io import BytesIO
import m365client.server_interface as ServerInterface
import httpx
from unstructured.partition.pdf import partition_pdf


async def download_pdf(config: ServerInterface.StorageConfig) -> bytes:
    try:
        blob_url = ServerInterface.build_connection_string(
            config.base_url,
            ServerInterface.build_blob_download_string,
            config.container_name,
            config.blob_name,
        )
        pdf_bytes = await ServerInterface.download_blob(
            blob_url, ServerInterface.async_download_blob, httpx.AsyncClient(timeout=30.0),
        )
        return pdf_bytes
    except httpx.HTTPError as http_error:
        print(f"HTTP error occurred: {http_error}")
    except ValueError as value_error:
        print(f"Document format error: {value_error}")
    except Exception as general_error:
        print(f"An unexpected error occurred: {general_error}")

def extract_text_from_pdf(pdf_bytes: BytesIO):
    pdf_file = pdf_bytes
    elements = partition_pdf(file=pdf_file)
    text = "\n".join([element.text for element in elements])
    return text