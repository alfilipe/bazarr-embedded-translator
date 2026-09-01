from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from .api.routes import router
from .core.config import settings


templates = Jinja2Templates(
    directory="/app/app/templates"
)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


app.state.templates = templates

app.include_router(router)
