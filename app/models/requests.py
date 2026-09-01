from pydantic import BaseModel, Field


class ExtractSubtitleRequest(BaseModel):
    """
    Request used to extract a subtitle track
    from an MKV file.
    """

    track_id: int = Field(
        ...,
        description="MKV subtitle track ID",
    )
