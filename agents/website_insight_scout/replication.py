from typing import List, Dict, Any
from agents.website_insight_scout.models import WebsiteAnalysisResult, ReplicationManifest, RankedElement
from agents.website_insight_scout.scoring import rank_elements

def generate_replication_manifest(result: WebsiteAnalysisResult) -> ReplicationManifest:
    """
    Generates a replication manifest from a website analysis result.
    Focuses on top-ranked core components.
    """
    elements = result.ui_hierarchy.elements if result.ui_hierarchy else []
    ranked = rank_elements(elements)
    core_components = [r for r in ranked if r.is_core]

    # Extract styling rules from top components
    styling_rules = {}
    for comp in core_components[:10]:
        for key, val in comp.element.styles.items():
            if key not in styling_rules:
                styling_rules[key] = val

    return ReplicationManifest(
        source_url=result.url,
        components=core_components[:20],
        styling_rules=styling_rules,
        logic_hints=[
            f"Component {c.element.tag} has text '{c.element.text}'"
            for c in core_components[:5]
        ],
        multi_language_support=True,
        language_schema={
            "default": "en",
            "extracted_text": [c.element.text for c in core_components if c.element.text]
        }
    )
