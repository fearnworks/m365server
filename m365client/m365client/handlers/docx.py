## m365client.handlers.docx.py

from m365client.handlers.blob_handler import BlobFileHandler

from io import BytesIO

import httpx
from unstructured.partition.docx import partition_docx

class DocxBlobFileHandler(BlobFileHandler):
    def extract_text(self, file_bytes: BytesIO) -> str:
        elements = partition_docx(file=file_bytes)
        text = "\n".join([element.text for element in elements])
        return text