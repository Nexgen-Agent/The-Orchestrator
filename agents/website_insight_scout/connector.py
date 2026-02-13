from abc import ABC, abstractmethod
from typing import Dict, Any, List

class InsightConnector(ABC):
    @abstractmethod
    async def analyze_website_data(self, url: str, html_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the collected website data (HTML, metadata, screenshots)
        and returns structured insights.
        """
        pass

class MockAIInsightConnector(InsightConnector):
    async def analyze_website_data(self, url: str, html_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate AI analysis based on the URL and extracted styles
        elements = metadata.get("elements", [])
        html_content_lower = html_content.lower()
        is_ecommerce = any(kw in html_content_lower for kw in ["cart", "shop", "price", "buy", "product"])

        # Try to extract real colors and fonts from metadata
        detected_colors = set()
        detected_fonts = set()
        for el in elements:
            styles = el.get("styles", {})
            if styles.get("color"):
                detected_colors.add(styles["color"])
            if styles.get("fontFamily"):
                detected_fonts.add(styles["fontFamily"].split(",")[0].strip('"').strip("'"))

        # Fallback if none detected
        colors = list(detected_colors)[:5] if detected_colors else ["#ffffff", "#000000", "#3b82f6"]
        fonts = list(detected_fonts)[:3] if detected_fonts else ["Inter", "sans-serif"]

        return {
            "ui_hierarchy": {
                "elements": elements[:20]
            },
            "design_patterns": {
                "colors": colors,
                "typography": fonts,
                "spacing": ["4px", "8px", "16px", "32px"]
            },
            "marketing_psychology": {
                "ctas": ["Sign Up", "Get Started"] if not is_ecommerce else ["Add to Cart", "Checkout"],
                "persuasion_techniques": ["Social Proof", "Scarcity"] if is_ecommerce else ["Value Proposition"],
                "engagement_loops": ["Newsletter signup"],
                "attention_hierarchy": ["Hero section", "Feature list"]
            },
            "architectural_insights": {
                "logic_patterns": ["Client-side routing", "State management detected"],
                "reusable_components": ["Navbar", "Footer", "Button", "Card"],
                "optimizations": ["Lazy load images", "Minify CSS"]
            }
        }
