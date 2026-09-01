import json
import subprocess
from pathlib import Path


class MkvService:
    """
    Handles MKV inspection and subtitle extraction
    using MKVToolNix.
    """

    def _run_command(
        self,
        command: list[str],
    ) -> str:

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:

            raise RuntimeError(
                "Command failed:\n"
                f"{' '.join(command)}\n\n"
                f"{result.stderr.strip()}"
            )

        return result.stdout

    def analyze(
        self,
        mkv_path: Path,
    ) -> dict:

        output = self._run_command([
            "mkvmerge",
            "-J",
            str(mkv_path),
        ])

        try:
            return json.loads(output)

        except json.JSONDecodeError as exc:

            raise RuntimeError(
                "Invalid JSON returned by mkvmerge."
            ) from exc

    def get_tracks(
        self,
        mkv_path: Path,
    ) -> list[dict]:

        data = self.analyze(
            mkv_path
        )

        tracks = []

        for track in data.get(
            "tracks",
            [],
        ):

            properties = track.get(
                "properties",
                {},
            )

            tracks.append({
                "id": track.get("id"),
                "type": track.get(
                    "type",
                    "",
                ),
                "codec": track.get(
                    "codec",
                    "",
                ),
                "codec_id": properties.get(
                    "codec_id",
                    "",
                ),
                "language": properties.get(
                    "language",
                    "",
                ),
                "language_ietf": properties.get(
                    "language_ietf",
                    "",
                ),
                "name": properties.get(
                    "track_name",
                    "",
                ),
                "default": properties.get(
                    "default_track",
                    False,
                ),
                "forced": properties.get(
                    "forced_track",
                    False,
                ),
                "hearing_impaired": properties.get(
                    "hearing_impaired",
                    False,
                ),
            })

        return tracks

    def get_subtitle_tracks(
        self,
        mkv_path: Path,
    ) -> list[dict]:

        return [
            track
            for track in self.get_tracks(
                mkv_path
            )
            if track["type"] == "subtitles"
        ]

    def extract_track(
        self,
        mkv_path: Path,
        track_id: int,
        output_path: Path,
    ) -> Path:

        if output_path.exists():

            raise FileExistsError(
                f"File already exists: "
                f"{output_path}"
            )

        self._run_command([
            "mkvextract",
            "tracks",
            str(mkv_path),
            f"{track_id}:{output_path}",
        ])

        if not output_path.exists():

            raise RuntimeError(
                "mkvextract completed but "
                "the output file was not created."
            )

        return output_path
