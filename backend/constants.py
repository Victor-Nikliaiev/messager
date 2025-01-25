import os


class CONSTS:
    HOST = "0.0.0.0"
    PORT = 1060
    LISTENER_LIMIT = 5
    MAX_WORKERS = 2 * os.cpu_count() + 1
    ENCRYPTED_CHUNK_SIZE = 32 * 1024  # 32 KB chunks
    ORIGINAL_CHUNK_SIZE = 32_740
    EOF_MARKER = b"<~+!EOF!+~>"
    EMPTY_VALUE = b""
