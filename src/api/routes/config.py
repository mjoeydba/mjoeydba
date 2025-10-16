"""API routes for managing application configuration."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.common.config import config_to_dict
from src.common.config_manager import ConfigManager

router = APIRouter()


def get_config_manager() -> ConfigManager:  # pragma: no cover - dependency override in app factory
    raise RuntimeError("Dependency override not configured")


class ElasticConfigModel(BaseModel):
    url: Optional[str] = None
    metrics_index: Optional[str] = Field(default=None, alias="metricsIndex")
    logs_index: Optional[str] = Field(default=None, alias="logsIndex")
    username: Optional[str] = None
    password: Optional[str] = None
    ca_cert: Optional[str] = Field(default=None, alias="caCert")
    insecure: Optional[bool] = None
    request_timeout: Optional[int] = Field(default=None, alias="requestTimeout")

    class Config:
        populate_by_name = True


class OllamaConfigModel(BaseModel):
    host: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = Field(default=None, alias="maxTokens")

    class Config:
        populate_by_name = True


class SQLConfigModel(BaseModel):
    dsn: Optional[str] = None
    server: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    encrypt: Optional[bool] = None
    trust_server_certificate: Optional[bool] = Field(default=None, alias="trustServerCertificate")

    class Config:
        populate_by_name = True


class ConfigUpdateModel(BaseModel):
    elastic: Optional[ElasticConfigModel] = None
    ollama: Optional[OllamaConfigModel] = None
    sqlserver: Optional[SQLConfigModel] = Field(default=None, alias="sqlServer")

    class Config:
        populate_by_name = True


@router.get("", response_model=dict)
def read_config(manager: ConfigManager = Depends(get_config_manager)) -> dict:
    config = manager.get_config()
    return config_to_dict(config)


@router.put("", response_model=dict)
def update_config(payload: ConfigUpdateModel, manager: ConfigManager = Depends(get_config_manager)) -> dict:
    data = payload.dict(by_alias=True, exclude_unset=True)
    # Map camelCase keys back to snake_case for persistence
    def _normalise(section: str, values: Optional[dict]) -> Optional[dict]:
        if values is None:
            return None
        mapping = {
            "metricsIndex": "metrics_index",
            "logsIndex": "logs_index",
            "caCert": "ca_cert",
            "requestTimeout": "request_timeout",
            "maxTokens": "max_tokens",
            "trustServerCertificate": "trust_server_certificate",
        }
        return {mapping.get(k, k): v for k, v in values.items()}

    updates = {}
    if "elastic" in data:
        updates["elastic"] = _normalise("elastic", data["elastic"])
    if "ollama" in data:
        updates["ollama"] = _normalise("ollama", data["ollama"])
    if "sqlServer" in data:
        updates["sqlserver"] = _normalise("sqlserver", data["sqlServer"])

    updated = manager.update(updates)
    return config_to_dict(updated)
