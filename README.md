# Bazarr Embedded Translator

Docker service for extracting embedded subtitle tracks from MKV files.

Designed to integrate with Bazarr and subtitle translation workflows.

## Features

- FastAPI web server
- MKV subtitle track detection
- ASS/SSA/SRT extraction
- HTTP API
- Docker support
- GitHub Container Registry
- GitHub Actions automated builds

## API

### Health check

GET /health

Example:

curl http://localhost:9870/health

### List subtitle tracks

GET /tracks?file=/movies/movie.mkv

### Extract subtitle

POST /extract

Example:

{
  "file": "/movie/movie.mkv",
  "track_info": '{"id":3, "codec":"SubStationAlpha", "language":"eng", "language_ietf":"en", "track_name":"Dialog - ENG", "default":true, "forced":true}'
}

Response:

{
  "status": "success",
  "input": "/movie/movie.mkv",
  "track_id": '{"id":3, "codec":"SubStationAlpha", "language":"eng", "language_ietf":"en", "track_name":"Dialog - ENG", "default":true, "forced":true}',
  "output": "/movie/movie.en.ass"
}

## Docker

docker pull ghcr.io/alfilipe/bazarr-embedded-translator:latest
