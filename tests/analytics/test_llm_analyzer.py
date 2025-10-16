from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.analytics.llm_analyzer import LLMAnalyzer
from src.common.config import OllamaSettings


@pytest.fixture
def settings() -> OllamaSettings:
    return OllamaSettings(host="http://ollama", model="test-model", temperature=0.5, max_tokens=256)


def test_analyze_success(settings: OllamaSettings) -> None:
    analyzer = LLMAnalyzer(settings)
    fake_response = {"response": "Insightful analysis"}
    with patch("requests.post") as post:
        post.return_value = MagicMock(status_code=200, json=lambda: fake_response)
        post.return_value.raise_for_status = MagicMock()
        result = analyzer.analyze("Blocking", metrics=[{"wait_type": "LCK_M_S"}], issues="Blocking detected")

    assert result["response"] == "Insightful analysis"
    assert result["model"] == "test-model"
    assert "Blocking" in result["prompt"]


def test_analyze_http_error(settings: OllamaSettings) -> None:
    analyzer = LLMAnalyzer(settings)
    with patch("requests.post") as post:
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = RuntimeError("boom")
        post.return_value = mock_resp
        with pytest.raises(RuntimeError):
            analyzer.analyze("Blocking", metrics=[])
        post.assert_called_once()
