"""Helpers for managing persistent application configuration."""
from __future__ import annotations

import os
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Optional

try:  # pragma: no cover - PyYAML import guard
    import yaml
except Exception:  # pragma: no cover
    yaml = None

from .config import AppConfig, config_to_dict, load_config


def _default_config_path(path: Optional[os.PathLike[str] | str] = None) -> Path:
    if path:
        return Path(path)
    env_path = os.getenv("APP_CONFIG_FILE")
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parents[2] / "config" / "settings.yaml"


def _deep_merge(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _deep_merge(dict(base[key]), value)
        elif value is None:
            base.pop(key, None)
        else:
            base[key] = value
    return base


class ConfigManager:
    """Manage loading and persistence of :class:`AppConfig`."""

    def __init__(self, path: Optional[os.PathLike[str] | str] = None):
        self._path = _default_config_path(path)
        self._lock = RLock()
        self._config = load_config(self._path)

    @property
    def path(self) -> Path:
        return self._path

    def get_config(self) -> AppConfig:
        with self._lock:
            return self._config

    def reload(self) -> AppConfig:
        with self._lock:
            self._config = load_config(self._path)
            return self._config

    def update(self, payload: Dict[str, Any]) -> AppConfig:
        if yaml is None:
            raise RuntimeError(
                "PyYAML is required to persist configuration updates. Install it with 'pip install pyyaml'."
            )

        with self._lock:
            current_dict = config_to_dict(self._config)
            merged = _deep_merge(current_dict, payload)
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("w", encoding="utf-8") as fh:
                yaml.safe_dump(merged, fh, sort_keys=False)
            self._config = load_config(self._path)
            return self._config


__all__ = ["ConfigManager"]
