"""Configuration management for the contract review application.

Loads settings from YAML config files and environment variables.
"""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """LLM provider configuration."""

    provider: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 4096


@dataclass
class Config:
    """Application configuration."""

    openai_api_key: str
    anthropic_api_key: str
    llm: LLMConfig
    max_pages: int = 50


def load_config(config_path: str = "configs/config.yaml") -> Config:
    """Load application configuration from YAML file and environment.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Populated Config dataclass instance.

    Raises:
        FileNotFoundError: If config file does not exist.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path) as f:
        cfg = yaml.safe_load(f)

    return Config(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        llm=LLMConfig(**cfg.get("llm", {})),
        max_pages=cfg.get("max_pages", 50),
    )
