from pydantic import BaseModel
from typing import Optional


class SubtitleTrack(BaseModel):
    id: int

    language: str = ""

    language_ietf: str = ""

    codec: str = ""

    codec_id: str = ""

    name: str = ""

    default: bool = False

    forced: bool = False

    hearing_impaired: bool = False


class FileEntry(BaseModel):
    name: str

    path: str

    is_directory: bool

    extension: Optional[str] = None


class ExtractionResult(BaseModel):
    status: str

    source_file: str

    output_file: Optional[str] = None

    track_id: Optional[int] = None
