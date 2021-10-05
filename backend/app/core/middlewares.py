import sentry_sdk
import os
import asyncio
from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import logger

import dotenv
dotenv.load_dotenv()


class HTTPRequestLoggerMiddleware(BaseHTTPMiddleware):
    """" Troubleshoot incoming requests by logging them as HTTP request blocks """
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        f_h = await HTTPRequestLoggerMiddleware.filter_headers(request.headers.raw)
        request_wall = f"{request.method} {request.scope['path']} {str(request.get('type', 'HTTP')).upper()}/{request.get('http_version')}\n"
        for header in f_h:
            request_wall += f"{header[0]}: {header[1]}\n"
        logger.debug(request_wall)
        return response

    @staticmethod
    async def filter_headers(headers: list[tuple]) -> list[tuple]:
        excluded_headers = [
            "pragma",
            "cache-control",
            "sec-ch-ua",
            "sec-ch-ua-platform",
            "sec-ch-ua-mobile",
            "sec-fetch-site",
            "sec-fetch-mode",
            "sec-fetch-user",
            "sec-fetch-dest",
            "accept-encoding",
            "accept-language",
            "user-agent"
        ]

        logged_headers = []
        for (header, value) in headers:
            if header.decode('utf-8') not in excluded_headers:
                logged_headers.append((
                        str(header.decode('utf-8')).title(), str(value.decode('utf-8')).title()
                ))
        return logged_headers


class HTTPRoundRobinMiddleware(BaseHTTPMiddleware):
    """ Drops requests which exceed a time threshold. Mitigates some DOS and large-payload attacks.
    Concept loosely adapted from ZionStage @ https://github.com/tiangolo/fastapi/issues/1752#issuecomment-682579845 """
    async def dispatch(self, request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=15)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="The request has timed out."
            )


# Load Sentry
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("STAGE")
)
