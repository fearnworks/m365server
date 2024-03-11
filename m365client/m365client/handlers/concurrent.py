"""
# Usage example
configs = [
    ServerInterface.StorageConfig(...),  # Configuration for file 1
    ServerInterface.StorageConfig(...),  # Configuration for file 2
    # ... (Add more configurations for different files)
]

texts = await process_files_in_parallel(configs)
"""

from m365client.handlers import DocxBlobFileHandler, PdfBlobFileHandler, ExcelBlobFileHandler, MarkdownBlobFileHandler, PowerpointBlobFileHandler
import httpx 
import concurrent
from loguru import logger 


async def process_file(handler, config):
    file_bytes = await handler.download_file(config)
    text = handler.extract_text(file_bytes)
    return text

async def process_files_in_parallel(configs, max_workers=5):
    handlers = {
        ".docx": DocxBlobFileHandler,
        ".pdf": PdfBlobFileHandler,
        ".xlsx": ExcelBlobFileHandler,
        ".md": MarkdownBlobFileHandler,
        ".pptx": PowerpointBlobFileHandler,
    }

    async with httpx.AsyncClient() as client:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for config in configs:
                file_extension = os.path.splitext(config.blob_name)[1].lower()
                handler_class = handlers.get(file_extension)
                if handler_class:
                    handler = handler_class()
                    future = executor.submit(process_file, handler, config)
                    futures.append(future)
                else:
                    logger.warning(f"Unsupported file type: {file_extension}")

            results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.exception(f"An error occurred during file processing: {e}")

    return results