import pytest
import asyncio
from agents.website_insight_scout.scout import WebsiteScout
from agents.website_insight_scout.connector import MockAIInsightConnector
from agents.website_insight_scout.models import WebsiteAnalysisResult

@pytest.mark.asyncio
async def test_scout_analyze_mock():
    connector = MockAIInsightConnector()
    scout = WebsiteScout(connector)

    # Using example.com for a real-ish test that should be fast
    url = "https://example.com"
    result = await scout.analyze(url)

    assert isinstance(result, WebsiteAnalysisResult)
    assert result.url == url
    assert len(result.screenshots) > 0
    assert result.ui_hierarchy is not None
    assert len(result.ui_hierarchy.elements) > 0
    assert result.design_patterns is not None
    assert result.marketing_psychology is not None
    assert result.architectural_insights is not None

@pytest.mark.asyncio
async def test_handler_task():
    from agents.website_insight_scout.handler import handle_task

    task_packet = {
        "payload": {
            "url": "https://example.com",
            "analyze_ui": True
        }
    }

    response = await handle_task(task_packet)
    assert response["status"] == "success"
    assert "result" in response
    assert response["result"]["url"] == "https://example.com"

@pytest.mark.asyncio
async def test_handler_missing_url():
    from agents.website_insight_scout.handler import handle_task

    task_packet = {
        "payload": {}
    }

    response = await handle_task(task_packet)
    assert response["status"] == "error"
    assert "Missing 'url'" in response["message"]
