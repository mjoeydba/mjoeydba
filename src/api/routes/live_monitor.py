"""Live SQL Server monitoring endpoints."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query

from src.live_monitor.dmv_queries import DMVCollector

router = APIRouter()


def get_dmv_collector() -> DMVCollector:  # pragma: no cover - overridden in app factory
    raise RuntimeError("Dependency override not configured")


@router.get("/waits")
def waits(limit: int = Query(default=25, ge=1, le=500), collector: DMVCollector = Depends(get_dmv_collector)) -> List[dict]:
    return collector.wait_stats(limit=limit)


@router.get("/blocking")
def blocking(limit: int = Query(default=25, ge=1, le=500), collector: DMVCollector = Depends(get_dmv_collector)) -> List[dict]:
    return collector.blocking(limit=limit)


@router.get("/sessions")
def sessions(limit: int = Query(default=50, ge=1, le=500), collector: DMVCollector = Depends(get_dmv_collector)) -> List[dict]:
    return collector.active_sessions(limit=limit)
