"""Configuration loader for the monitoring platform."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

try:  # pragma: no cover - import guard exercised implicitly
    import yaml
except Exception:  # pragma: no cover - surface a clear message when PyYAML is absent
    yaml = None


@dataclass
class ElasticSettings:
    url: str
    metrics_index: str
    logs_index: str
    username: Optional[str]
    password: Optional[str]
    ca_cert: Optional[str]
    insecure: bool = False
    request_timeout: int = 60


@dataclass
class OllamaSettings:
    host: str
    model: str
    temperature: float = 0.1
    max_tokens: int = 512


@dataclass
class SQLServerSettings:
    dsn: Optional[str] = None
    server: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: str = "master"
    encrypt: bool = True
    trust_server_certificate: bool = False


@dataclass
class AppConfig:
    elastic: ElasticSettings
    ollama: OllamaSettings
    sqlserver: SQLServerSettings


def _resolve_env(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if value.startswith("${") and value.endswith("}"):
        env_name = value[2:-1]
        return os.getenv(env_name)
    return value


def _parse_settings(raw: Dict[str, Any]) -> AppConfig:
    elastic_raw = raw.get("elastic", {})
    ollama_raw = raw.get("ollama", {})
    sql_raw = raw.get("sqlserver", {})

    elastic = ElasticSettings(
        url=elastic_raw.get("url", "http://localhost:9200"),
        metrics_index=elastic_raw.get("metrics_index", "mssql-metrics-*"),
        logs_index=elastic_raw.get("logs_index", "mssql-logs-*"),
        username=_resolve_env(elastic_raw.get("username")),
        password=_resolve_env(elastic_raw.get("password")),
        ca_cert=_resolve_env(elastic_raw.get("ca_cert")),
        insecure=bool(elastic_raw.get("insecure", False)),
        request_timeout=int(elastic_raw.get("request_timeout", 60)),
    )

    ollama = OllamaSettings(
        host=ollama_raw.get("host", "http://localhost:11434"),
        model=ollama_raw.get("model", "llama3"),
        temperature=float(ollama_raw.get("temperature", 0.1)),
        max_tokens=int(ollama_raw.get("max_tokens", 512)),
    )

    sqlserver = SQLServerSettings(
        dsn=_resolve_env(sql_raw.get("dsn")),
        server=_resolve_env(sql_raw.get("server")),
        username=_resolve_env(sql_raw.get("username")),
        password=_resolve_env(sql_raw.get("password")),
        database=sql_raw.get("database", "master"),
        encrypt=bool(sql_raw.get("encrypt", True)),
        trust_server_certificate=bool(sql_raw.get("trust_server_certificate", False)),
    )

    return AppConfig(elastic=elastic, ollama=ollama, sqlserver=sqlserver)


def load_config(path: Optional[os.PathLike[str] | str] = None) -> AppConfig:
    """Load configuration from a YAML file.

    Parameters
    ----------
    path:
        Optional explicit configuration path. Defaults to ``APP_CONFIG_FILE`` or
        ``config/settings.yaml`` relative to the repository root.
    """

    if yaml is None:
        raise RuntimeError(
            "PyYAML is required to load configuration. Install it with 'pip install pyyaml'."
        )

    config_path = (
        Path(path)
        if path
        else Path(os.getenv("APP_CONFIG_FILE", Path(__file__).resolve().parents[2] / "config/settings.yaml"))
    )
    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    return _parse_settings(raw)


__all__ = [
    "AppConfig",
    "ElasticSettings",
    "OllamaSettings",
    "SQLServerSettings",
    "load_config",
]
