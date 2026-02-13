from typing import List, Dict
from agents.website_insight_scout.models import UIElement, RankedElement, PerformanceScore, WebsiteAnalysisResult, MultiSiteComparison

def score_element(element: UIElement) -> PerformanceScore:
    """
    Scores an element based on its properties.
    Heuristic model:
    - visual_appeal: Based on having styles and proper bounding box.
    - efficiency: Based on tag type (buttons/links are efficient for UX if clear).
    - ux_flow: Based on text presence and clarity.
    """
    visual = 50.0
    if element.styles:
        visual += 20.0
    if element.bounding_box.get("width", 0) > 100:
        visual += 10.0

    efficiency = 50.0
    if element.tag in ["button", "a"]:
        efficiency += 30.0

    ux_flow = 50.0
    if element.text and len(element.text.strip()) > 0:
        ux_flow += 20.0
        if len(element.text) < 50: # Short clear text is better for flow usually
            ux_flow += 10.0

    overall = (visual + efficiency + ux_flow) / 3.0

    return PerformanceScore(
        visual_appeal=min(visual, 100.0),
        efficiency=min(efficiency, 100.0),
        ux_flow=min(ux_flow, 100.0),
        overall=overall
    )

def rank_elements(elements: List[UIElement]) -> List[RankedElement]:
    ranked = []
    for el in elements:
        score = score_element(el)
        priority = 5
        if score.overall > 80:
            priority = 10
        elif score.overall > 60:
            priority = 7

        ranked.append(RankedElement(
            element=el,
            score=score,
            priority=priority,
            is_core=priority >= 7
        ))

    # Sort by score
    ranked.sort(key=lambda x: x.score.overall, reverse=True)
    return ranked

def compare_sites(results: List[WebsiteAnalysisResult]) -> MultiSiteComparison:
    rankings = {}
    all_ranked_elements = []

    for res in results:
        elements = res.ui_hierarchy.elements if res.ui_hierarchy else []
        ranked = rank_elements(elements)
        all_ranked_elements.extend(ranked[:5]) # Top 5 from each

        # Site score is average of top elements
        if ranked:
            avg_score = sum(r.score.overall for r in ranked[:10]) / min(len(ranked), 10)
        else:
            avg_score = 0.0
        rankings[res.url] = avg_score

    all_ranked_elements.sort(key=lambda x: x.score.overall, reverse=True)

    return MultiSiteComparison(
        urls=[res.url for res in results],
        rankings=rankings,
        top_elements=all_ranked_elements[:15],
        common_patterns=["Responsive Layout", "Clean Typography"] # Mock common patterns
    )
