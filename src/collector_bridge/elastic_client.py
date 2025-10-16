"""Thin client for querying Elastic MSSQL telemetry."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterable, List

from elasticsearch import Elasticsearch

from src.common.config import ElasticSettings

LOGGER = logging.getLogger(__name__)


class ElasticTelemetryClient:
    """Wrapper around :class:`elasticsearch.Elasticsearch` tailored for telemetry queries."""

    def __init__(self, settings: ElasticSettings):
        self._settings = settings
        self._client = self._build_client(settings)

    @staticmethod
    def _build_client(settings: ElasticSettings) -> Elasticsearch:
        opts: Dict[str, Any] = {
            "basic_auth": (settings.username, settings.password)
            if settings.username and settings.password
            else None,
            "ca_certs": settings.ca_cert if settings.ca_cert and not settings.insecure else None,
            "verify_certs": not settings.insecure,
            "request_timeout": settings.request_timeout,
        }
        # Remove None values to avoid validation warnings
        opts = {k: v for k, v in opts.items() if v is not None}

        LOGGER.debug("Initializing Elasticsearch client with options %s", json.dumps(opts, default=str))
        return Elasticsearch(settings.url, **opts)

    def raw_search(self, index: str, query: str, size: int = 100) -> Dict[str, Any]:
        LOGGER.debug("Executing Elastic search", extra={"index": index, "query": query, "size": size})
        return self._client.search(index=index, q=query, size=size)

    def fetch_metrics(self, query: str, size: int = 200) -> List[Dict[str, Any]]:
        response = self.raw_search(self._settings.metrics_index, query=query, size=size)
        return [hit["_source"] for hit in response.get("hits", {}).get("hits", [])]

    def fetch_logs(self, query: str, size: int = 200) -> List[Dict[str, Any]]:
        response = self.raw_search(self._settings.logs_index, query=query, size=size)
        return [hit["_source"] for hit in response.get("hits", {}).get("hits", [])]

    def normalize_wait_stats(self, documents: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for doc in documents:
            waits = doc.get("wait_stats") or {}
            normalized.append(
                {
                    "timestamp": doc.get("@timestamp") or doc.get("timestamp"),
                    "instance": doc.get("mssql_instance"),
                    "wait_type": waits.get("type"),
                    "wait_time_ms": waits.get("time_ms"),
                    "waiting_tasks": waits.get("tasks"),
                }
            )
        return normalized

    def normalize_blocking(self, documents: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for doc in documents:
            blocking = doc.get("blocking") or {}
            results.append(
                {
                    "timestamp": doc.get("@timestamp") or doc.get("timestamp"),
                    "session_id": blocking.get("session_id"),
                    "blocking_session_id": blocking.get("blocking_session_id"),
                    "wait_type": blocking.get("wait_type"),
                    "duration_ms": blocking.get("duration_ms"),
                    "query_text": blocking.get("query_text"),
                }
            )
        return results


__all__ = ["ElasticTelemetryClient"]
