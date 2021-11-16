# Pull ASGI Server and FastAPI
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

# Load settings
from app.core.config import logger, settings

# Load custom middlewares
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.core.middlewares import (
    HTTPRequestLoggerMiddleware,
    HerokuRedirectMiddleware,
    HTTPRoundRobinLimiterMiddleware
)

# Load routers
from app.api.auth import router as AUTH_ROUTER
from app.api.model import router as MODEL_ROUTER

# Main application
app = FastAPI(openapi_url=settings.OPENAPI_URL)

# Load middlewares
app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.SITE_HOST,
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.add_middleware(HTTPRequestLoggerMiddleware)
app.add_middleware(HerokuRedirectMiddleware)
app.add_middleware(HTTPRoundRobinLimiterMiddleware)

# Routers
app.include_router(AUTH_ROUTER)
app.include_router(MODEL_ROUTER)

# Mount static directory to serve directly within html
app.mount("/assets", StaticFiles(directory=str(settings.STATIC_PATH)), name="assets")
templates = Jinja2Templates(directory=str(settings.FRONTEND_PATH))


@app.get('/', response_class=HTMLResponse)
async def index(
        req: Request,
        origin: str = settings.SITE_HOST
):
    """ Main entry point of SPA with index.html as the response. """
    return templates.TemplateResponse(
        name="index.html",
        context={
            "request": req,
            "origin": origin
        }
    )

# DEBUG: Running module directly through uvicorn
if __name__ == "__main__":
    logger.debug("Server started by script.")
    uvicorn.run("main:app", port=5000, reload=True, log_level='debug', access_log=True)
