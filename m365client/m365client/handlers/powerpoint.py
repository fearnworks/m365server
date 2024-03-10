""" Example usage 

pptx_bytes = await download_powerpoint(config)
filename = os.path.basename(config.blob_name)
pptx_content = extract_text_from_powerpoint(pptx_bytes, filename)

text_chunks = [pptx_content]  # Assuming you have a single chunk of text
embeddings = generate_embeddings(text_chunks)

embeddings_safetensors = embeddings_to_safetensors(embeddings)

upload_config = ServerInterface.StorageConfig(
    base_url=BASE_URL,
    container_name="file.pptx",
    blob_name="embeddings/embedding_powerpoint.safetensors",
)
upload_url = ServerInterface.build_connection_string(
    upload_config.base_url,
    ServerInterface.build_blob_download_string,
    upload_config.container_name,
    upload_config.blob_name,
)
await ServerInterface.upload_blob(upload_config, embeddings_safetensors)

"""


from io import BytesIO
import m365client.server_interface as ServerInterface
import httpx
from unstructured.partition.pptx import partition_pptx
import tempfile
import os


async def download_powerpoint(config: ServerInterface.StorageConfig) -> BytesIO:
    try:
        blob_url = ServerInterface.build_connection_string(
            config.base_url,
            ServerInterface.build_blob_download_string,
            config.container_name,
            config.blob_name,
        )
        pptx_bytes = await ServerInterface.download_blob(
            blob_url, ServerInterface.async_download_blob, httpx.AsyncClient(timeout=30.0),
        )
        return pptx_bytes
    except httpx.HTTPError as http_error:
        print(f"HTTP error occurred: {http_error}")
    except ValueError as value_error:
        print(f"Document format error: {value_error}")
    except Exception as general_error:
        print(f"An unexpected error occurred: {general_error}")

def extract_text_from_powerpoint(pptx_bytes: BytesIO, filename: str):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as temp_file:
        temp_file.write(pptx_bytes.getvalue())
        temp_file_path = temp_file.name

    elements = partition_pptx(
        filename=temp_file_path,
        include_page_breaks=True,
        metadata_filename=filename,
        include_metadata=True,
    )
    text = "\n".join([element.text for element in elements])
    
    os.unlink(temp_file_path)  # Remove the temporary file
    
    return text