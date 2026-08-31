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

curl http://localhost:9877/health

### List subtitle tracks

GET /tracks?file=/media/movie/movie.mkv

### Extract subtitle

POST /extract

Example:

{
  "file": "/media/movie/movie.mkv",
  "track_id": 3
}

Response:

{
  "status": "success",
  "input": "/media/movie/movie.mkv",
  "track_id": 3,
  "output": "/data/output/movie.track-3.ass"
}

## Docker

docker pull ghcr.io/USERNAME/bazarr-embedded-translator:latest
