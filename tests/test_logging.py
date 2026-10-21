import json
import logging

from app import __version__
from app.core.logging_setup import JsonFormatter, clean_fields


def test_version_is_set():
    assert __version__ == "0.1.0"


def test_text_fields_are_hidden():
    fields = clean_fields({"doc_id": "job-001", "text": "Jane Doe, 12 Main Street"})
    assert fields["doc_id"] == "job-001"
    assert fields["text"] == "[omitted]"


def test_hidden_field_check_ignores_case():
    fields = clean_fields({"Query": "who knows Python"})
    assert fields["Query"] == "[omitted]"


def test_json_formatter_writes_valid_json():
    record = logging.LogRecord("app", logging.INFO, "file.py", 1, "request", None, None)
    record.fields = {"status": 200}

    line = JsonFormatter().format(record)
    data = json.loads(line)

    assert data["message"] == "request"
    assert data["level"] == "INFO"
    assert data["status"] == 200
