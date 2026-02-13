import pytest
from agents.website_insight_scout.scout import WebsiteScout
from agents.website_insight_scout.multi_scout import MultiWebsiteScout
from agents.website_insight_scout.connector import MockAIInsightConnector
from agents.website_insight_scout.scoring import score_element, rank_elements, compare_sites
from agents.website_insight_scout.models import UIElement

@pytest.mark.asyncio
async def test_multi_scout_batch():
    connector = MockAIInsightConnector()
    scout = WebsiteScout(connector)
    multi_scout = MultiWebsiteScout(scout)

    urls = ["https://example.com", "https://google.com"]
    results = await multi_scout.analyze_batch(urls)

    assert len(results) == 2
    assert results[0].url == "https://example.com"
    assert results[1].url == "https://google.com"

def test_element_scoring():
    el = UIElement(
        tag="button",
        text="Click Me",
        bounding_box={"width": 150, "height": 50},
        styles={"color": "white", "backgroundColor": "blue"}
    )
    score = score_element(el)
    assert score.overall >= 80
    assert score.efficiency == 80.0

def test_rank_elements():
    elements = [
        UIElement(tag="p", text="Just text"),
        UIElement(tag="button", text="Action", styles={"color": "red"})
    ]
    ranked = rank_elements(elements)
    assert len(ranked) == 2
    assert ranked[0].element.tag == "button"
    assert ranked[0].priority >= 7

def test_compare_sites_logic():
    from agents.website_insight_scout.models import WebsiteAnalysisResult, UIHierarchy

    res1 = WebsiteAnalysisResult(
        url="site1.com",
        ui_hierarchy=UIHierarchy(elements=[UIElement(tag="button", text="B1")])
    )
    res2 = WebsiteAnalysisResult(
        url="site2.com",
        ui_hierarchy=UIHierarchy(elements=[UIElement(tag="p", text="P1")])
    )

    comparison = compare_sites([res1, res2])
    assert comparison.rankings["site1.com"] > comparison.rankings["site2.com"]
    assert len(comparison.top_elements) > 0
