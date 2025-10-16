"""FastAPI application factory."""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.analytics.llm_analyzer import LLMAnalyzer
from src.api.routes import analysis, config as config_routes, live_monitor, metrics
from src.collector_bridge.elastic_client import ElasticTelemetryClient
from src.collector_bridge.service import TelemetryService
from src.common.config import AppConfig
from src.common.config_manager import ConfigManager
from src.live_monitor.connection import SQLServerConnectionManager
from src.live_monitor.dmv_queries import DMVCollector

LOGGER = logging.getLogger(__name__)


def create_app(config_path: str | None = None) -> FastAPI:
    app = FastAPI(title="SQL Server Observability API", version="0.1.0")
    manager = ConfigManager(config_path)

    def get_config() -> AppConfig:
        cfg = manager.get_config()
        LOGGER.debug("Configuration retrieved for request")
        return cfg

    def get_telemetry_service(cfg: AppConfig = Depends(get_config)) -> TelemetryService:
        client = ElasticTelemetryClient(cfg.elastic)
        return TelemetryService(client)

    def get_llm_analyzer(cfg: AppConfig = Depends(get_config)) -> LLMAnalyzer:
        return LLMAnalyzer(cfg.ollama)

    def get_dmv_collector(cfg: AppConfig = Depends(get_config)) -> DMVCollector:
        manager_conn = SQLServerConnectionManager(cfg.sqlserver)
        return DMVCollector(manager_conn)

    def get_manager() -> ConfigManager:
        return manager

    app.dependency_overrides[analysis.get_llm_analyzer] = get_llm_analyzer
    app.dependency_overrides[metrics.get_telemetry_service] = get_telemetry_service
    app.dependency_overrides[live_monitor.get_dmv_collector] = get_dmv_collector
    app.dependency_overrides[config_routes.get_config_manager] = get_manager

    app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
    app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
    app.include_router(live_monitor.router, prefix="/live", tags=["live-monitor"])
    app.include_router(config_routes.router, prefix="/config", tags=["config"])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    static_dir = Path(__file__).resolve().parents[2] / "frontend"
    if static_dir.exists():
        app.mount("/app", StaticFiles(directory=static_dir, html=True), name="frontend")

        @app.get("/", include_in_schema=False)
        async def serve_index() -> FileResponse:
            return FileResponse(static_dir / "index.html")

    return app


app = create_app()
