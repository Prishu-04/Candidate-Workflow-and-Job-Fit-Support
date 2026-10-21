import json
import logging
import sys
from datetime import datetime, timezone

# Field names that may hold document or user text. Their values are never logged.
HIDDEN_FIELDS = {
    "text",
    "content",
    "document",
    "resume",
    "prompt",
    "query",
    "question",
    "answer",
}


def clean_fields(fields: dict) -> dict:
    cleaned = {}
    for key, value in fields.items():
        if key.lower() in HIDDEN_FIELDS:
            cleaned[key] = "[omitted]"
        else:
            cleaned[key] = value
    return cleaned


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data = {
            "time": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        data.update(getattr(record, "fields", {}))
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
        return json.dumps(data, default=str)


def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    # Remove only the handler added by an earlier call, so this is safe to repeat.
    for handler in list(root.handlers):
        if getattr(handler, "is_json_handler", False):
            root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.is_json_handler = True
    root.addHandler(handler)
    root.setLevel(level)


def log_event(logger: logging.Logger, event: str, **fields) -> None:
    logger.info(event, extra={"fields": clean_fields(fields)})
