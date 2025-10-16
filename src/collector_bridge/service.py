"""Service layer for Elastic-backed telemetry access."""
from __future__ import annotations

from typing import Dict, List

from src.collector_bridge.elastic_client import ElasticTelemetryClient


class TelemetryService:
    def __init__(self, client: ElasticTelemetryClient):
        self._client = client

    def latest_waits(self, instance: str | None = None, limit: int = 50) -> List[Dict]:
        query = "mssql_instance:\"{}\"".format(instance) if instance else "*"
        documents = self._client.fetch_metrics(query=query, size=limit)
        return self._client.normalize_wait_stats(documents)

    def blocking_sessions(self, instance: str | None = None, limit: int = 50) -> List[Dict]:
        query = "blocking.session_id:*"
        if instance:
            query += f" AND mssql_instance:\"{instance}\""
        documents = self._client.fetch_metrics(query=query, size=limit)
        return self._client.normalize_blocking(documents)

    def raw_logs(self, search: str, limit: int = 100) -> List[Dict]:
        return self._client.fetch_logs(query=search, size=limit)


__all__ = ["TelemetryService"]
