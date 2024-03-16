## m365client/handlers/excel.py

import io 
from typing import Dict 
import pandas as pd
from io import BytesIO
from m365client.handlers.blob_handler import BlobFileHandler
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


class ExcelBlobFileHandler(BlobFileHandler):
    def extract_text(self, file_bytes: BytesIO) -> str:
        elements = partition_xlsx(file=file_bytes)
        text = "\n".join([element.text for element in elements])
        return text
