"""Serialize directory publication across processes."""

import fcntl

from contextlib import contextmanager
from pathlib import Path


@contextmanager
def publication_lock(destination_path):
    destination = Path(destination_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)

    lock_path = destination.with_suffix(".lock")

    with lock_path.open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
