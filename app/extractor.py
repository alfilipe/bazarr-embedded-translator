import json
import subprocess
from pathlib import Path


class SubtitleExtractor:
    def __init__(self, output_dir="/data/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def inspect(self, mkv_file: str):
        """
        Get information about all tracks in the MKV file.
        """

        command = [
            "mkvmerge",
            "-J",
            mkv_file
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        return json.loads(result.stdout)

    def get_subtitle_tracks(self, mkv_file: str):
        """
        Return subtitle tracks from the MKV.
        """

        info = self.inspect(mkv_file)

        tracks = []

        for track in info.get("tracks", []):
            if track.get("type") != "subtitles":
                continue

            properties = track.get("properties", {})

            tracks.append({
                "id": track.get("id"),
                "codec": track.get("codec"),
                "language": properties.get("language"),
                "language_ietf": properties.get("language_ietf"),
                "track_name": properties.get("track_name"),
                "default": properties.get("default_track"),
                "forced": properties.get("forced_track"),
            })

        return tracks

    def extract(
        self,
        mkv_file: str,
        track_id: int,
        output_file: str | None = None
    ):
        """
        Extract a subtitle track from the MKV.
        """

        mkv_path = Path(mkv_file)

        if not mkv_path.exists():
            raise FileNotFoundError(
                f"MKV file not found: {mkv_file}"
            )

        if output_file is None:
            output_file = (
                self.output_dir
                / f"{mkv_path.stem}.track-{track_id}.ass"
            )
        else:
            output_file = Path(output_file)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        command = [
            "mkvextract",
            str(mkv_path),
            "tracks",
            f"{track_id}:{output_file}"
        ]

        subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        return str(output_file)
