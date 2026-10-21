import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def test_defaults_are_valid():
    settings = Settings(_env_file=None)
    assert settings.app_env in ("development", "test", "production")


def test_unknown_app_env_is_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="staging")


def test_log_level_is_case_insensitive():
    settings = Settings(_env_file=None, log_level="debug")
    assert settings.log_level == "DEBUG"


def test_bad_log_level_is_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, log_level="LOUD")


def test_wildcard_origin_is_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, frontend_origin="*")


def test_origin_needs_http_scheme():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, frontend_origin="localhost:3000")


def test_production_needs_https_origin():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            app_env="production",
            frontend_origin="http://example.com",
        )


def test_bad_database_url_is_rejected():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url="mysql://user:pw@host/db")


def test_api_key_is_hidden_when_printed():
    settings = Settings(_env_file=None, llm_api_key="fake-key-for-test")
    assert "fake-key-for-test" not in repr(settings)
