from pathlib import Path

from .mkv_service import MkvService


class SubtitleService:
    """
    Handles subtitle-related business logic.
    """

    SUPPORTED_CODECS = {
        "S_TEXT/ASS": ".ass",
        "S_TEXT/SSA": ".ssa",
        "S_TEXT/UTF8": ".srt",
    }

    def __init__(
        self,
        mkv_service: MkvService,
    ):
        self.mkv_service = (
            mkv_service
        )

    def get_subtitles(
        self,
        mkv_path: Path,
    ) -> list[dict]:

        return self.mkv_service.get_subtitle_tracks(
            mkv_path
        )

    def is_english(
        self,
        track: dict,
    ) -> bool:

        language = (
            track.get(
                "language",
                "",
            )
            or ""
        ).lower()

        language_ietf = (
            track.get(
                "language_ietf",
                "",
            )
            or ""
        ).lower()

        return (
            language in {
                "en",
                "eng",
            }
            or language_ietf.startswith(
                "en"
            )
        )

    def get_extension(
        self,
        track: dict,
    ) -> str:

        codec_id = (
            track.get(
                "codec_id",
                "",
            )
            or ""
        ).upper()

        if codec_id in self.SUPPORTED_CODECS:

            return self.SUPPORTED_CODECS[
                codec_id
            ]

        codec = (
            track.get(
                "codec",
                "",
            )
            or ""
        ).lower()

        if "ass" in codec:
            return ".ass"

        if "ssa" in codec:
            return ".ssa"

        if (
            "subrip" in codec
            or "srt" in codec
        ):
            return ".srt"

        raise ValueError(
            "Unsupported subtitle codec: "
            f"{track.get('codec', '')}"
        )

    def build_output_path(
        self,
        mkv_path: Path,
        track: dict,
    ) -> Path:

        extension = self.get_extension(
            track
        )

        return (
            mkv_path.parent
            / f"{mkv_path.stem}.en{extension}"
        )

    def extract(
        self,
        mkv_path: Path,
        track_id: int,
    ) -> Path:

        subtitles = self.get_subtitles(
            mkv_path
        )

        selected = None

        for subtitle in subtitles:

            if subtitle["id"] == track_id:

                selected = subtitle
                break

        if selected is None:

            raise ValueError(
                f"Subtitle track "
                f"{track_id} not found."
            )

        output_path = (
            self.build_output_path(
                mkv_path,
                selected,
            )
        )

        return self.mkv_service.extract_track(
            mkv_path,
            track_id,
            output_path,
        )
