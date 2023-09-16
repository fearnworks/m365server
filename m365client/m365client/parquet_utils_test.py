from m365client.parquet_utils import filter_parquet_part_files

def test_should_return_empty_list_for_empty_input():
    assert filter_parquet_part_files([]) == []

def test_should_return_empty_list_for_no_parquet_files():
    assert filter_parquet_part_files(['file1.txt', 'file2.csv']) == []

def test_should_return_list_of_parquet_files():
    assert filter_parquet_part_files(['file1.txt', 'part-00000.parquet', 'file2.csv', 'part-00001.parquet']) == ['part-00000.parquet', 'part-00001.parquet']

def test_should_return_list_of_all_parquet_files():
    assert filter_parquet_part_files(['part-00000.parquet', 'part-00001.parquet']) == ['part-00000.parquet', 'part-00001.parquet']

def test_should_return_list_of_parquet_files_with_similar_names():
    assert filter_parquet_part_files(['part-00000.parquet', 'part-00001.parquet', 'part-00000.csv', 'part-00001.txt']) == ['part-00000.parquet', 'part-00001.parquet']