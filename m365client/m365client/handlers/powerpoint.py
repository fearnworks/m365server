## m365client/handlers/powerpoint.py

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
from unstructured.partition.pptx import partition_pptx
import tempfile
import os
from m365client.handlers.blob_handler import BlobFileHandler


class PowerpointBlobFileHandler(BlobFileHandler):
    def extract_text(self, file_bytes: BytesIO, filename: str) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as temp_file:
            temp_file.write(file_bytes.getvalue())
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