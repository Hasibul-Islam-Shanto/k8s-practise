import json
import logging
from contextvars import ContextVar
from datetime import datetime, timezone

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)

# Attributes set by the logging module itself. Anything else on the record is
# treated as an extra field (for example the access-log keys).
_STANDARD_LOG_RECORD_ATTRS = frozenset(
    {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "taskName",
        "thread",
        "threadName",
    }
)


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True


class JsonStdoutFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }
        for key, value in record.__dict__.items():
            if key in _STANDARD_LOG_RECORD_ATTRS or key == "request_id":
                continue
            payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(log_level: str) -> None:
    """Attach a JSON stdout handler to the root logger. Safe to call more than once."""
    root = logging.getLogger()
    root.setLevel(log_level.upper())
    if any(getattr(handler, "_techblog_json", False) for handler in root.handlers):
        return

    handler = logging.StreamHandler()
    handler._techblog_json = True  # type: ignore[attr-defined]
    handler.setFormatter(JsonStdoutFormatter())
    handler.addFilter(RequestContextFilter())
    root.addHandler(handler)
