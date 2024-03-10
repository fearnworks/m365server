import io 
from typing import Dict 
import pandas as pd
from io import BytesIO
import m365client.server_interface as ServerInterface
import httpx
from unstructured.partition.xlsx import partition_xlsx


def load_blob_sheet_to_dataframe(
    blob_data: io.BytesIO, sheet_name: str = "Sheet1"
) -> pd.DataFrame:
    try:
        df = pd.read_excel(blob_data, sheet_name=sheet_name)  # type: ignore
        return df
    except Exception as ex:
        raise Exception(f"Failed to load blob into a DataFrame") from ex

def load_all_sheets_from_blob(blob_data: io.BytesIO) -> Dict[str, pd.DataFrame]:
    # Read Excel file without loading any specific sheet to get the sheet names
    xls = pd.ExcelFile(blob_data, engine="openpyxl")
    sheet_names = xls.sheet_names

    # Dictionary to store DataFrames for each sheet
    sheets_data = {}

    for sheet_name in sheet_names:
        # Reset the pointer to the beginning of the blob data for each read
        blob_data.seek(0)

        # Load each sheet using the provided function
        df = load_blob_sheet_to_dataframe(blob_data, sheet_name=sheet_name)
        sheets_data[sheet_name] = df

    return sheets_data

def extract_text_from_excel(excel_bytes: BytesIO):
    elements = partition_xlsx(file=excel_bytes)
    text = "\n".join([element.text for element in elements])
    return text

async def download_excel(config: ServerInterface.StorageConfig) -> BytesIO:
    try:
        blob_url = ServerInterface.build_connection_string(
            config.base_url,
            ServerInterface.build_blob_download_string,
            config.container_name,
            config.blob_name,
        )
        excel_bytes = await ServerInterface.download_blob(
            blob_url, ServerInterface.async_download_blob, httpx.AsyncClient(timeout=30.0),
        )
        return excel_bytes
    except httpx.HTTPError as http_error:
        print(f"HTTP error occurred: {http_error}")
    except ValueError as value_error:
        print(f"Document format error: {value_error}")
    except Exception as general_error:
        print(f"An unexpected error occurred: {general_error}")