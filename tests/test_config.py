"""Tests for configuration loading."""

from pathlib import Path

import pytest
import yaml

from src.utils.config import Config, LLMConfig, load_config


@pytest.fixture()
def config_file(tmp_path: Path) -> Path:
    """Create a temporary config YAML file."""
    config_data = {
        "llm": {
            "provider": "openai",
            "model": "gpt-4",
            "temperature": 0.0,
            "max_tokens": 4096,
        },
        "max_pages": 50,
    }
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.dump(config_data))
    return config_path


def test_load_config(config_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading configuration from YAML file."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-ant-key")

    config = load_config(str(config_file))

    assert config.openai_api_key == "test-key"
    assert config.anthropic_api_key == "test-ant-key"
    assert config.llm.provider == "openai"
    assert config.llm.model == "gpt-4"
    assert config.llm.temperature == 0.0
    assert config.llm.max_tokens == 4096
    assert config.max_pages == 50


def test_load_config_missing_file() -> None:
    """Test that missing config file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.yaml")


def test_config_dataclass() -> None:
    """Test Config dataclass instantiation."""
    llm = LLMConfig(provider="openai", model="gpt-4")
    config = Config(
        openai_api_key="key1",
        anthropic_api_key="key2",
        llm=llm,
    )
    assert config.max_pages == 50
    assert config.llm.temperature == 0.0


def test_llm_config_defaults() -> None:
    """Test LLMConfig default values."""
    llm = LLMConfig(provider="anthropic", model="claude-3-opus")
    assert llm.temperature == 0.0
    assert llm.max_tokens == 4096
