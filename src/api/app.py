"""FastAPI application factory."""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI

from src.analytics.llm_analyzer import LLMAnalyzer
from src.api.routes import analysis, live_monitor, metrics
from src.collector_bridge.elastic_client import ElasticTelemetryClient
from src.collector_bridge.service import TelemetryService
from src.common.config import AppConfig, load_config
from src.live_monitor.connection import SQLServerConnectionManager
from src.live_monitor.dmv_queries import DMVCollector

LOGGER = logging.getLogger(__name__)


@lru_cache
def _get_config() -> AppConfig:
    cfg = load_config()
    LOGGER.info("Configuration loaded for API")
    return cfg


def get_telemetry_service(cfg: Annotated[AppConfig, Depends(_get_config)]) -> TelemetryService:
    client = ElasticTelemetryClient(cfg.elastic)
    return TelemetryService(client)


def get_llm_analyzer(cfg: Annotated[AppConfig, Depends(_get_config)]) -> LLMAnalyzer:
    return LLMAnalyzer(cfg.ollama)


def get_dmv_collector(cfg: Annotated[AppConfig, Depends(_get_config)]) -> DMVCollector:
    manager = SQLServerConnectionManager(cfg.sqlserver)
    return DMVCollector(manager)


def create_app() -> FastAPI:
    app = FastAPI(title="SQL Server Observability API", version="0.1.0")

    app.dependency_overrides[analysis.get_llm_analyzer] = get_llm_analyzer
    app.dependency_overrides[metrics.get_telemetry_service] = get_telemetry_service
    app.dependency_overrides[live_monitor.get_dmv_collector] = get_dmv_collector

    app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
    app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
    app.include_router(live_monitor.router, prefix="/live", tags=["live-monitor"])

    return app


app = create_app()
