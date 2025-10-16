"""Analysis endpoints using the LLM."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from src.analytics.llm_analyzer import LLMAnalyzer

router = APIRouter()


def get_llm_analyzer() -> LLMAnalyzer:  # pragma: no cover - overridden in app factory
    raise RuntimeError("Dependency override not configured")


@router.post("/insights")
def generate_insights(payload: dict, analyzer: LLMAnalyzer = Depends(get_llm_analyzer)) -> dict:
    title = payload.get("title", "SQL Server Health Report")
    metrics: List[dict] = payload.get("metrics", [])
    issues = payload.get("issues")
    return analyzer.analyze(title=title, metrics=metrics, issues=issues)
