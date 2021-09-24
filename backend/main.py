import logging
import uvicorn
from fastapi import FastAPI
from app.core.config import settings, logger
from app.core.security import generate_token

app = FastAPI()


@app.get('/')
def index():
    return {'status': 'success', 'detail': 'Hello World!'}


if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, reload=True, log_level='debug', access_log=True)
