from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)

from ..core.config import settings
from ..services.file_service import (
    FileService,
)
from ..services.mkv_service import (
    MkvService,
)
from ..services.subtitle_service import (
    SubtitleService,
)


router = APIRouter()


file_service = FileService()

mkv_service = MkvService()

subtitle_service = SubtitleService(
    mkv_service
)


@router.get(
    "/",
    response_class=HTMLResponse,
)
def browse(
    request: Request,
    path: str = "",
):

    entries = (
        file_service.list_directory(
            path
        )
    )

    breadcrumbs = (
        file_service.get_breadcrumbs(
            path
        )
    )

    parent = (
        file_service.get_parent_path(
            path
        )
    )

    return request.app.state.templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME,
            "path": path,
            "entries": entries,
            "breadcrumbs": breadcrumbs,
            "parent": parent,
        },
    )


@router.get(
    "/mkv",
    response_class=HTMLResponse,
)
def mkv_details(
    request: Request,
    path: str,
):

    mkv_path = (
        file_service.resolve_path(
            path
        )
    )

    if not mkv_path.exists():

        raise HTTPException(
            status_code=404,
            detail="MKV not found.",
        )

    if (
        not mkv_path.is_file()
        or mkv_path.suffix.lower() != ".mkv"
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid MKV file.",
        )

    tracks = (
        mkv_service.get_tracks(
            mkv_path
        )
    )

    subtitles = (
        subtitle_service.get_subtitles(
            mkv_path
        )
    )

    external_subtitles = []

    for item in mkv_path.parent.iterdir():

        if not item.is_file():
            continue

        if item.suffix.lower() not in {
            ".ass",
            ".ssa",
            ".srt",
            ".sub",
            ".vtt",
        }:
            continue

        external_subtitles.append({
            "name": item.name,
            "path": file_service.relative_path(
                item
            ),
        })

    return request.app.state.templates.TemplateResponse(
        request=request,
        name="mkv.html",
        context={
            "app_name": settings.APP_NAME,
            "mkv": mkv_path.name,
            "mkv_path": path,
            "tracks": tracks,
            "subtitles": subtitles,
            "external_subtitles":
                sorted(
                    external_subtitles,
                    key=lambda item:
                    item["name"].lower(),
                ),
        },
    )


@router.post("/extract")
def extract_subtitle(
    path: str,
    track_id: int = Form(...),
    forced: bool = Form(...),
):

    mkv_path = (
        file_service.resolve_path(
            path
        )
    )

    if not mkv_path.exists():

        raise HTTPException(
            status_code=404,
            detail="MKV not found.",
        )

    try:

        subtitle_service.extract(
            mkv_path,
            track_id,
            forced,
        )

    except FileExistsError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except RuntimeError as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    return RedirectResponse(
        url=f"/mkv?path={path}",
        status_code=303,
    )


@router.get("/health")
def health():

    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }
