from __future__ import annotations

import os
from pathlib import Path

from src.common import config as config_module


def test_load_config_env_resolution(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("ES_USER", "elastic_user")
    monkeypatch.setenv("ES_PASS", "elastic_pass")
    yaml = tmp_path / "settings.yaml"
    yaml.write_text(
        """
        elastic:
          url: http://localhost:9200
          metrics_index: metric-*
          logs_index: log-*
          username: "${ES_USER}"
          password: "${ES_PASS}"
        ollama:
          host: http://ollama
          model: test
        sqlserver:
          server: sql1
          database: msdb
        """,
        encoding="utf-8",
    )

    cfg = config_module.load_config(yaml)
    assert cfg.elastic.username == "elastic_user"
    assert cfg.elastic.password == "elastic_pass"
    assert cfg.sqlserver.database == "msdb"
    assert cfg.sqlserver.server == "sql1"
    assert cfg.elastic.compatibility_version == 8


def test_config_to_dict_roundtrip(tmp_path: Path) -> None:
    yaml = tmp_path / "settings.yaml"
    yaml.write_text(
        """
        elastic:
          url: http://localhost:9200
          metrics_index: metric-*
          logs_index: log-*
          insecure: true
          request_timeout: 90
        ollama:
          host: http://ollama
          model: llama3
          temperature: 0.2
        sqlserver:
          server: sql1
          encrypt: false
        """,
        encoding="utf-8",
    )

    cfg = config_module.load_config(yaml)
    as_dict = config_module.config_to_dict(cfg)
    assert as_dict["elastic"]["request_timeout"] == 90
    assert "password" not in as_dict["elastic"]
    assert as_dict["sqlserver"]["encrypt"] is False
    assert as_dict["elastic"]["compatibility_version"] == 8
