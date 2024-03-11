## m365client/handlers/markdown.py
from io import BytesIO
from m365client.handlers import BlobFileHandler
from unstructured.partition.md import partition_md

class MarkdownBlobFileHandler(BlobFileHandler):
    def extract_text(self, file_bytes: BytesIO) -> str:
        markdown_text = file_bytes.read().decode("utf-8")
        elements = partition_md(text=markdown_text)
        text = "\n".join([element.text for element in elements])
        return text