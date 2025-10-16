from __future__ import annotations

from pathlib import Path

import pytest

from src.common.config_manager import ConfigManager


def test_config_manager_update(tmp_path: Path) -> None:
    config_file = tmp_path / "settings.yaml"
    config_file.write_text(
        """
        elastic:
          url: http://localhost:9200
          metrics_index: metric-*
          logs_index: log-*
        ollama:
          host: http://ollama
          model: llama3
        sqlserver:
          server: sql1
          encrypt: true
        """,
        encoding="utf-8",
    )

    manager = ConfigManager(config_file)
    updated = manager.update(
        {
            "elastic": {"url": "http://elastic:9200", "request_timeout": 120},
            "sqlserver": {"encrypt": False},
        }
    )

    assert updated.elastic.url == "http://elastic:9200"
    assert updated.elastic.request_timeout == 120
    assert updated.sqlserver.encrypt is False
    assert updated.elastic.compatibility_version == 8

    reload = manager.reload()
    assert reload.elastic.url == "http://elastic:9200"
    assert reload.elastic.compatibility_version == 8


def test_config_manager_requires_yaml(tmp_path: Path) -> None:
    config_file = tmp_path / "settings.yaml"
    config_file.write_text("{}", encoding="utf-8")

    manager = ConfigManager(config_file)

    from src.common import config_manager as module

    original_yaml = module.yaml
    module.yaml = None
    try:
        with pytest.raises(RuntimeError):
            manager.update({"elastic": {"url": "http://example"}})
    finally:
        module.yaml = original_yaml
