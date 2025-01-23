import os


class CONSTS:
    HOST = "0.0.0.0"
    PORT = 1060
    LISTENER_LIMIT = 5
    MAX_WORKERS = 2 * os.cpu_count() + 1
