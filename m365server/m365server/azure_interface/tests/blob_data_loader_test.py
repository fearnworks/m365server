from m365server.azure_interface.blob_data_loader import BlobDataLoader, ContainerClient
import pytest
import pandas as pd
from io import BytesIO

def test_should_get_csv_loader():
    content_type = 'text/csv'
    expected_loader = 'read_csv'
    loader = BlobDataLoader.get_pandas_loader(content_type)
    assert loader == expected_loader

def test_should_get_excel_loader():
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    expected_loader = 'read_excel'
    loader = BlobDataLoader.get_pandas_loader(content_type)
    assert loader == expected_loader

def test_should_get_json_loader():
    content_type = 'application/json'
    expected_loader = 'read_json'
    loader = BlobDataLoader.get_pandas_loader(content_type)
    assert loader == expected_loader

def test_should_get_parquet_loader():
    content_type = 'application/octet-stream'
    expected_loader = 'read_parquet'
    loader = BlobDataLoader.get_pandas_loader(content_type)
    assert loader == expected_loader

def test_should_get_html_loader():
    content_type = 'text/html'
    expected_loader = 'read_html'
    loader = BlobDataLoader.get_pandas_loader(content_type)
    assert loader == expected_loader

def test_should_get_xml_loader():
    content_type = 'text/xml'
    expected_loader = 'read_xml'
    loader = BlobDataLoader.get_pandas_loader(content_type)
    assert loader == expected_loader

def test_should_load_csv_blob_to_dataframe():
    blob_data = b'id,name\n1,Alice\n2,Bob\n3,Charlie\n'
    content_type = 'text/csv'
    expected_df = pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']})
    df = BlobDataLoader.load_blob_to_dataframe(blob_data, content_type)
    assert df.equals(expected_df)

def test_should_load_json_blob_to_dataframe():
    blob_data = b'{"id": [1, 2, 3], "name": ["Alice", "Bob", "Charlie"]}'
    content_type = 'application/json'
    expected_df = pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']})
    df = BlobDataLoader.load_blob_to_dataframe(blob_data, content_type)
    assert df.equals(expected_df)

def test_should_load_parquet_blob_to_dataframe(tmp_path):
    # Create a DataFrame
    df = pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']})
    
    # Save DataFrame to a Parquet file
    parquet_file = tmp_path / "data.parquet"
    df.to_parquet(parquet_file)

    # Read the file as bytes
    blob_data = parquet_file.read_bytes()
    content_type = 'application/octet-stream'

    # Load the blob data to a DataFrame and compare with the original DataFrame
    loaded_df = BlobDataLoader.load_blob_to_dataframe(blob_data, content_type)
    assert loaded_df.equals(df)

def test_should_load_excel_blob_to_dataframe(tmp_path):
    # Create a DataFrame
    df = pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']})
    
    # Save DataFrame to an Excel file
    excel_file = tmp_path / "data.xlsx"
    df.to_excel(excel_file, index=False)

    # Read the file as bytes
    blob_data = excel_file.read_bytes()
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    # Load the blob data to a DataFrame and compare with the original DataFrame
    loaded_df = BlobDataLoader.load_blob_to_dataframe(blob_data, content_type)
    assert loaded_df['Sheet1'].equals(df)


def test_should_load_html_blob_to_dataframe():
    blob_data = b'<table><tr><th>id</th><th>name</th></tr><tr><td>1</td><td>Alice</td></tr><tr><td>2</td><td>Bob</td></tr><tr><td>3</td><td>Charlie</td></tr></table>'
    content_type = 'text/html'
    expected_df = pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']})
    df = BlobDataLoader.load_blob_to_dataframe(blob_data, content_type)
    assert df[0].equals(expected_df)

def test_should_load_xml_blob_to_dataframe():
    blob_data = b'<root><row><id>1</id><name>Alice</name></row><row><id>2</id><name>Bob</name></row><row><id>3</id><name>Charlie</name></row></root>'
    content_type = 'text/xml'
    expected_df = pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']})
    df = BlobDataLoader.load_blob_to_dataframe(blob_data, content_type)
    assert df.equals(expected_df)
