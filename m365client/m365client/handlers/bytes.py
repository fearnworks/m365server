async def read_file_as_bytes(file_path: str) -> bytes:
    with open(file_path, "rb") as file:
        file_bytes = file.read()
    return file_bytes
