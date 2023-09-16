from loguru import logger 

def filter_parquet_part_files(file_names):
    logger.info(file_names)
    parts = [file_name for file_name in file_names if file_name.startswith('part') and file_name.endswith('.parquet')]
    logger.info(parts)  
    return parts