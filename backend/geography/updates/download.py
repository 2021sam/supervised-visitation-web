"""Download geographic source files."""

from pathlib import Path
from urllib.request import urlopen
from shutil import copyfileobj


def download_file(url, destination, timeout=60):
    """Download a file to a new destination."""

    if not url.startswith("https://"):
        raise ValueError("HTTPS download URL required")

    destination = Path(destination)

    with destination.open("xb") as output:
        try:
            with urlopen(url, timeout=timeout) as response:
                copyfileobj(response, output)
        except BaseException:
            output.close()
            destination.unlink(missing_ok=True)
            raise

    return destination
