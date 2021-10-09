import sentry_sdk
import asyncio
from fastapi import HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
import dotenv
from os import environ as env

# Import global logger
from app.core.config import logger

# Retrieve subset of local keys
if env.get("DYNO"):
    # Heroku deployment
    SENTRY_DSN = env.get("SENTRY_DSN")
    SENTRY_STAGE = env.get("STAGE")
    HEROKU_HOST = env.get("HEROKU_HOST")
    SITE_HOST = env.get("SITE_HOST")
else:
    # Local deployment
    SENTRY_DSN = dotenv.get_key(".env", "SENTRY_DSN")
    SENTRY_STAGE = dotenv.get_key(".env", 'STAGE')
    HEROKU_HOST = dotenv.get_key(".env", 'HEROKU_HOST')
    SITE_HOST = dotenv.get_key(".env", "SITE_HOST")


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
            "user-agent",
            "connection",
            "upgrade-insecure-requests"
        ]

        logged_headers = []
        for (header, value) in headers:
            if header.decode('utf-8') not in excluded_headers:
                logged_headers.append((
                        str(header.decode('utf-8')).title(), str(value.decode('utf-8')).title()
                ))
        return logged_headers


class HTTPRoundRobinLimiterMiddleware(BaseHTTPMiddleware):
    """ Drops requests which exceed a time threshold. Mitigates some DOS and large-payload attacks.
    Concept loosely adapted from ZionStage @ https://github.com/tiangolo/fastapi/issues/1752#issuecomment-682579845 """
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            return await asyncio.wait_for(call_next(request), timeout=15)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="The request has timed out."
            )


class HerokuRedirectMiddleware(BaseHTTPMiddleware):
    """ All requests to the unproxied Heroku endpoint should be refused to avoid confusion and take advantage of SSL and other Cloudflare protections.
        This middleware will proxy all said requests to new application instance. Local requests are ignored. """
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            response = await call_next(request)
            if HEROKU_HOST is None:
                logger.critical("HEROKU_HOST env variable missing. For security, the app will refuse all requests to this endpoint.")
                response.status_code = 500
            elif HEROKU_HOST.lower() in request.headers['Host'].lower():
                # Manually set a redirect response that the browser can follow
                logger.warning("For security, a request to the Heroku endpoint has been refused and a permanent redirect was sent to the client.")
                response.status_code = 301
                response.headers.append('Location', SITE_HOST)
            return response
        except (KeyError, AttributeError):
            # Handles both a missing and an invalid Host header
            logger.critical("[Middlewares.HerokuRedirectMiddleware] - The middleware could not process the provided HOST header.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="The application ran into an issue while processing a request."
            )


# Load Sentry
sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment=SENTRY_STAGE
)
