import json
import os
import subprocess
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="Bazarr Embedded Subtitle Extractor",
    version="1.0.0"
)


class WebhookRequest(BaseModel):
    file: str


def run_command(command):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(command)}\n"
            f"{result.stderr}"
        )

    return result.stdout


def get_tracks(mkv_file):
    output = run_command([
        "mkvmerge",
        "-J",
        mkv_file
    ])

    return json.loads(output)


def find_english_subtitles(data):
    subtitles = []

    for track in data.get("tracks", []):

        if track.get("type") != "subtitles":
            continue

        properties = track.get("properties", {})

        language = (
            properties.get("language") or ""
        ).lower()

        language_ietf = (
            properties.get("language_ietf") or ""
        ).lower()

        if not (
            language == "eng"
            or language == "en"
            or language_ietf.startswith("en")
        ):
            continue

        codec = (
            track.get("codec") or ""
        ).lower()

        name = (
            properties.get("track_name") or ""
        ).lower()

        # Ignorar commentary
        if "commentary" in name:
            continue

        # Prioridade:
        # 1 - ASS/SSA normal
        # 2 - SRT
        # 3 - outros
        if "ass" in codec or "ssa" in codec:
            priority = 1
        elif "subrip" in codec or "srt" in codec:
            priority = 2
        else:
            priority = 3

        # Evitar preferir SDH quando existe uma normal
        if "sdh" in name:
            priority += 1

        subtitles.append({
            "id": track.get("id"),
            "codec": codec,
            "name": name,
            "language": language,
            "language_ietf": language_ietf,
            "priority": priority
        })

    subtitles.sort(key=lambda x: x["priority"])

    return subtitles


def extract_subtitle(mkv_file, subtitle):
    directory = os.path.dirname(mkv_file)
    filename = os.path.splitext(
        os.path.basename(mkv_file)
    )[0]

    codec = subtitle["codec"]

    if "ass" in codec or "ssa" in codec:
        extension = ".en.ass"

    elif "subrip" in codec or "srt" in codec:
        extension = ".en.srt"

    else:
        raise RuntimeError(
            f"Unsupported subtitle codec: {codec}"
        )

    output_file = os.path.join(
        directory,
        filename + extension
    )

    # Já existe
    if os.path.exists(output_file):
        return {
            "status": "already_exists",
            "file": output_file,
            "track_id": subtitle["id"]
        }

    run_command([
        "mkvextract",
        "tracks",
        mkv_file,
        f"{subtitle['id']}:{output_file}"
    ])

    return {
        "status": "extracted",
        "file": output_file,
        "track_id": subtitle["id"]
    }


@app.get("/")
def root():
    return {
        "service": "bazarr-embedded-translator",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/webhook")
def webhook(request: WebhookRequest):

    mkv_file = request.file

    if not mkv_file:
        raise HTTPException(
            status_code=400,
            detail="Missing 'file'"
        )

    if not os.path.isfile(mkv_file):
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {mkv_file}"
        )

    if not mkv_file.lower().endswith(".mkv"):
        raise HTTPException(
            status_code=400,
            detail="File is not an MKV"
        )

    try:
        data = get_tracks(mkv_file)

        subtitles = find_english_subtitles(data)

        if not subtitles:
            return {
                "status": "no_english_subtitle",
                "file": mkv_file
            }

        selected = subtitles[0]

        result = extract_subtitle(
            mkv_file,
            selected
        )

        return {
            **result,
            "source_mkv": mkv_file,
            "language": "en",
            "codec": selected["codec"],
            "track_name": selected["name"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
