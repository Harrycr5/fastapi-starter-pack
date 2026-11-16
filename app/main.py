from fastapi import FastAPI

from .api.router import api_router
from .core.config import get_settings
from .lifespan import lifespan
from app.core.exception_handlers import register_exception_handlers

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "tryItOutEnabled": True,
        "docExpansion": "list",
        "filter": True,
    },
)

register_exception_handlers(app)
app.include_router(api_router)

