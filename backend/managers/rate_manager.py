import threading
import time


class RateLimitedManager:
    def __init__(self, interval=1.0):
        self.interval = interval  # Time in seconds
        self._last_run = 0
        self._lock = threading.Lock()

    def __enter__(self):
        with self._lock:
            current_time = time.time()
            if current_time - self._last_run < self.interval:
                return None
            self._last_run = current_time
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
