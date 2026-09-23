from __future__ import annotations

from pathlib import Path

from django.conf import settings
from PIL import Image, UnidentifiedImageError
from rest_framework.exceptions import ValidationError

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".m4a", ".aac", ".wav", ".ogg"}
ALLOWED_NOTE_EXTENSIONS = ALLOWED_AUDIO_EXTENSIONS | {".webm", ".mp4", ".mov"}


def validate_image_file(file) -> None:
    name = getattr(file, "name", "") or ""
    suffix = Path(name).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Please upload a JPG, PNG, WEBP, or GIF image.")

    size = getattr(file, "size", 0) or 0
    if size > settings.MAX_IMAGE_BYTES:
        raise ValidationError("Images must be 5 MB or smaller.")

    try:
        file.seek(0)
        with Image.open(file) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError("That file does not look like a valid image.") from exc
    finally:
        file.seek(0)


def validate_audio_file(file) -> None:
    name = getattr(file, "name", "") or ""
    suffix = Path(name).suffix.lower()
    if suffix not in ALLOWED_AUDIO_EXTENSIONS:
        raise ValidationError("Please upload an MP3, M4A, AAC, WAV, or OGG file.")

    size = getattr(file, "size", 0) or 0
    if size > settings.MAX_AUDIO_BYTES:
        raise ValidationError("Audio must be 10 MB or smaller.")


def validate_note_media(file) -> None:
    name = getattr(file, "name", "") or ""
    suffix = Path(name).suffix.lower()
    if suffix not in ALLOWED_NOTE_EXTENSIONS:
        raise ValidationError("Please send an audio or video note.")
    size = getattr(file, "size", 0) or 0
    if size > settings.MAX_NOTE_BYTES:
        raise ValidationError("Notes must be 15 MB or smaller.")
