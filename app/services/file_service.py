from pathlib import Path

from fastapi import HTTPException

from ..core.config import settings


class FileService:
    """
    Handles filesystem access inside the TV library.
    """

    def __init__(self):
        self.root = Path(
            settings.TV_ROOT
        ).resolve()

    def resolve_path(
        self,
        relative_path: str = "",
    ) -> Path:
        """
        Resolve a relative path while preventing
        access outside the configured root.
        """

        candidate = (
            self.root / relative_path
        ).resolve()

        try:
            candidate.relative_to(
                self.root
            )

        except ValueError:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Access outside the TV "
                    "library is not allowed."
                ),
            )

        return candidate

    def exists(
        self,
        relative_path: str,
    ) -> bool:
        return self.resolve_path(
            relative_path
        ).exists()

    def is_directory(
        self,
        relative_path: str,
    ) -> bool:
        return self.resolve_path(
            relative_path
        ).is_dir()

    def list_directory(
        self,
        relative_path: str = "",
    ) -> list[dict]:

        directory = self.resolve_path(
            relative_path
        )

        if not directory.exists():
            raise HTTPException(
                status_code=404,
                detail="Directory not found.",
            )

        if not directory.is_dir():
            raise HTTPException(
                status_code=400,
                detail="Path is not a directory.",
            )

        entries = []

        for item in directory.iterdir():

            if item.is_dir():

                entries.append({
                    "name": item.name,
                    "path": self.relative_path(
                        item
                    ),
                    "is_directory": True,
                    "extension": None,
                })

                continue

            if not item.is_file():
                continue

            extension = (
                item.suffix.lower()
            )

            supported = {
                ".mkv",
                ".ass",
                ".ssa",
                ".srt",
                ".sub",
                ".vtt",
            }

            if extension not in supported:
                continue

            entries.append({
                "name": item.name,
                "path": self.relative_path(
                    item
                ),
                "is_directory": False,
                "extension": extension,
            })

        entries.sort(
            key=lambda item: (
                not item["is_directory"],
                item["name"].lower(),
            )
        )

        return entries

    def relative_path(
        self,
        path: Path,
    ) -> str:

        return str(
            path.resolve().relative_to(
                self.root
            )
        )

    def get_parent_path(
        self,
        relative_path: str,
    ) -> str | None:

        current = self.resolve_path(
            relative_path
        )

        if current == self.root:
            return None

        return self.relative_path(
            current.parent
        )

    def get_breadcrumbs(
        self,
        relative_path: str,
    ) -> list[dict]:

        breadcrumbs = [{
            "name": "TV Shows",
            "path": "",
        }]

        if not relative_path:
            return breadcrumbs

        current = ""

        for part in Path(
            relative_path
        ).parts:

            current = (
                f"{current}/{part}"
                if current
                else part
            )

            breadcrumbs.append({
                "name": part,
                "path": current,
            })

        return breadcrumbs
