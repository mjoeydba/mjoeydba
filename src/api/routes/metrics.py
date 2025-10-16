"""Telemetry endpoints."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query

from src.collector_bridge.service import TelemetryService

router = APIRouter()


def get_telemetry_service() -> TelemetryService:  # pragma: no cover - overridden in app factory
    raise RuntimeError("Dependency override not configured")


@router.get("/wait-stats")
def wait_stats(
    instance: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    service: TelemetryService = Depends(get_telemetry_service),
) -> List[dict]:
    return service.latest_waits(instance=instance, limit=limit)


@router.get("/blocking")
def blocking(
    instance: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    service: TelemetryService = Depends(get_telemetry_service),
) -> List[dict]:
    return service.blocking_sessions(instance=instance, limit=limit)


@router.get("/logs")
def logs(
    q: str = Query(default="*"),
    limit: int = Query(default=100, ge=1, le=1000),
    service: TelemetryService = Depends(get_telemetry_service),
) -> List[dict]:
    return service.raw_logs(search=q, limit=limit)
