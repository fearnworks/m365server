## m365client/handlers/pdf.py

from io import BytesIO
from m365client.handlers import BlobFileHandler
from unstructured.partition.pdf import partition_pdf

class PdfBlobFileHandler(BlobFileHandler):
    def extract_text(self, file_bytes: BytesIO) -> str:
        elements = partition_pdf(file=file_bytes)
        text = "\n".join([element.text for element in elements])
        return text