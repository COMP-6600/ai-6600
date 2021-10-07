# Pull ASGI Server and FastAPI
import uvicorn
import mimetypes
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, Response

# Load settings
from app.core.config import logger, settings

# Load custom middlewares
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from app.core.middlewares import HTTPRequestLoggerMiddleware
from fastapi.middleware.cors import CORSMiddleware

# Load routers
from app.api.auth import router as AUTH_ROUTER
from app.api.model import router as MODEL_ROUTER

# Main application
app = FastAPI()

# Load custom middlewares
app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(HTTPRequestLoggerMiddleware)
app.add_middleware(CORSMiddleware)

# Routers
app.include_router(AUTH_ROUTER)
app.include_router(MODEL_ROUTER)

# Mount static directory to serve directly within html
app.mount("/static", StaticFiles(directory=str(settings.STATIC_PATH)), name="static")
templates = Jinja2Templates(directory=str(settings.FRONTEND_PATH))


# TODO: Temporary solution, rely on aiofiles next time
@app.get('/', response_class=HTMLResponse)
async def index(req: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": req}
    )

# DEBUG: Running module directly through uvicorn
if __name__ == "__main__":
    logger.debug("Server started by uvicorn import within Heroku.")
    uvicorn.run("main:app", port=5000, reload=True, log_level='debug', access_log=True)
elif __name__ == "__mp_main__":
    logger.debug("Multiprocessing thread started.")
elif __name__ == "main":
    logger.debug("Server started from script.")
else:
    # Debug unknown module __name__
    logger.debug("Server started in an unknown manner.")
    logger.debug(f"{__name__=}")
