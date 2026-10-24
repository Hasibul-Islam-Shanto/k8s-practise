import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import request_id_ctx

logger = logging.getLogger("app")

_MAX_REQUEST_ID_LENGTH = 128


def _request_id_from_header(request: Request) -> str:
    incoming = request.headers.get("x-request-id", "").strip()
    if (
        incoming
        and len(incoming) <= _MAX_REQUEST_ID_LENGTH
        and incoming.isascii()
        and incoming.isprintable()
    ):
        return incoming
    return str(uuid.uuid4())


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = _request_id_from_header(request)
        token = request_id_ctx.set(request_id)
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            if request.url.path != "/metrics":
                client = request.client
                logger.info(
                    "http_request",
                    extra={
                        "event": "http_request",
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                        "request_id": request_id,
                        "client_ip": client.host if client else None,
                    },
                )
            request_id_ctx.reset(token)
