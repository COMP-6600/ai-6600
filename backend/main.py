# Pull ASGI Server and FastAPI
import fastapi.routing
import uvicorn
from fastapi import FastAPI

# Load settings
from app.core.config import logger

# Load routers
from app.api.auth import router as AUTH_ROUTER

# Main application
app = FastAPI()

# Routers
app.include_router(AUTH_ROUTER)

# DEBUG: Display Routes that were loaded
for route in app.routes:
    if type(route) == fastapi.routing.APIRoute:
        logger.debug(f"Route loaded: {route.path}")


# DEBUG: Index Route
@app.get('/')
def index():
    return {'status': 'success', 'detail': 'Hello World!'}


# DEBUG: Running module directly through uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True, log_level='debug', access_log=True)
