from __future__ import annotations

from unittest.mock import patch

from src.collector_bridge.elastic_client import ElasticTelemetryClient
from src.common.config import ElasticSettings


def _settings(**overrides):
    params = {
        "url": "http://localhost:9200",
        "metrics_index": "metric-*",
        "logs_index": "log-*",
        "username": None,
        "password": None,
        "ca_cert": None,
        "insecure": False,
        "request_timeout": 60,
        "compatibility_version": 7,
    }
    params.update(overrides)
    return ElasticSettings(**params)


@patch("src.collector_bridge.elastic_client.Elasticsearch")
def test_client_sets_compatibility_headers(mock_es) -> None:
    ElasticTelemetryClient(_settings())
    assert mock_es.called
    _, kwargs = mock_es.call_args
    headers = kwargs.get("headers")
    assert headers is not None
    assert headers["Accept"].endswith("=7")
    assert headers["Content-Type"].endswith("=7")


@patch("src.collector_bridge.elastic_client.Elasticsearch")
def test_client_omits_headers_when_not_configured(mock_es) -> None:
    ElasticTelemetryClient(_settings(compatibility_version=0))
    _, kwargs = mock_es.call_args
    assert "headers" not in kwargs
