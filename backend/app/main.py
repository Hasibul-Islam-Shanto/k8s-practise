from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.core.logging import configure_logging
from app.middleware.request_logging import RequestLoggingMiddleware
from app.routes import auth, comments, likes, posts, users

configure_logging(settings.log_level)

API_PREFIX = "/api/v1"

app = FastAPI(
    title="TechBlog API",
    description="A simple technology blogging platform.",
    version="1.0.0",
)

# Last middleware added runs first. Logging is registered before CORS so a
# request hits CORS, then request logging, then the route.
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(posts.router, prefix=API_PREFIX)
app.include_router(likes.router, prefix=API_PREFIX)
app.include_router(comments.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)

Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=False,
    excluded_handlers=["/metrics", "/health"],
).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
