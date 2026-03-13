from forgepilot.config import get_settings


def test_settings_load_defaults() -> None:
    settings = get_settings()
    assert settings.default_provider
    assert settings.default_model
    assert settings.execution_mode in {"confirm", "auto"}
