from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .extractor import SubtitleExtractor


app = FastAPI(
    title="Bazarr Embedded Translator",
    version="1.0.0"
)

extractor = SubtitleExtractor()


class ExtractRequest(BaseModel):
    file: str
    track_id: int
    output_file: str | None = None


@app.get("/")
def root():
    return {
        "service": "bazarr-embedded-translator",
        "status": "ok"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/tracks")
def tracks(file: str):
    """
    List subtitle tracks inside an MKV.
    """

    if not Path(file).exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file}"
        )

    try:
        return {
            "file": file,
            "tracks": extractor.get_subtitle_tracks(file)
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )


@app.post("/extract")
def extract(request: ExtractRequest):
    """
    Extract a subtitle track from an MKV.
    """

    if not Path(request.file).exists():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {request.file}"
        )

    try:
        output = extractor.extract(
            mkv_file=request.file,
            track_id=request.track_id,
            output_file=request.output_file
        )

        return {
            "status": "success",
            "input": request.file,
            "track_id": request.track_id,
            "output": output
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )
