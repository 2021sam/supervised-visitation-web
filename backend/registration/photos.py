"""Validate and normalize provider profile photos."""

import base64
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 25_000_000
MAX_DIMENSIONS = (512, 512)
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def process_photo(data: bytes) -> str:
    if not data or len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("Photo must be between 1 byte and 5 MB.")

    try:
        with Image.open(BytesIO(data)) as image:
            if image.format not in ALLOWED_FORMATS:
                raise ValueError("Use a JPEG, PNG or WebP image.")

            if image.width * image.height > MAX_PIXELS:
                raise ValueError("Image dimensions are too large.")

            image = ImageOps.exif_transpose(image)
            image.thumbnail(MAX_DIMENSIONS)

            rgba = image.convert("RGBA")
            clean = Image.new("RGB", rgba.size, "white")
            clean.paste(rgba, mask=rgba.getchannel("A"))

            output = BytesIO()
            clean.save(output, format="JPEG", quality=85)

    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        OSError,
    ) as exc:
        raise ValueError("Invalid image file.") from exc

    encoded = base64.b64encode(output.getvalue()).decode("ascii")

    return f"data:image/jpeg;base64,{encoded}"
