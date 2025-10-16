from __future__ import annotations

from typing import Dict, List

import pytest

from src.collector_bridge.service import TelemetryService


class DummyClient:
    def __init__(self, wait_docs: List[Dict[str, object]], blocking_docs: List[Dict[str, object]]):
        self.wait_docs = wait_docs
        self.blocking_docs = blocking_docs

    def fetch_metrics(self, query: str, size: int = 200):  # pragma: no cover - simple forwarding
        if "blocking" in query:
            return self.blocking_docs
        return self.wait_docs

    def fetch_logs(self, query: str, size: int = 200):  # pragma: no cover
        return self.wait_docs

    def normalize_wait_stats(self, documents):
        return documents

    def normalize_blocking(self, documents):
        return documents


@pytest.fixture
def service() -> TelemetryService:
    waits = [{"wait_type": "LCK_M_S"}]
    blocking = [{"blocking_session_id": 55}]
    return TelemetryService(DummyClient(waits, blocking))


def test_latest_waits(service: TelemetryService) -> None:
    data = service.latest_waits(limit=1)
    assert data[0]["wait_type"] == "LCK_M_S"


def test_blocking_sessions(service: TelemetryService) -> None:
    data = service.blocking_sessions(limit=1)
    assert data[0]["blocking_session_id"] == 55
