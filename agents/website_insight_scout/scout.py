import asyncio
import os
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright
from agents.website_insight_scout.models import WebsiteAnalysisResult, UIElement, UIHierarchy
from agents.website_insight_scout.connector import InsightConnector

class WebsiteScout:
    def __init__(self, connector: InsightConnector):
        self.connector = connector

    async def analyze(self, url: str, analyze_ui: bool = True, analyze_ux: bool = True) -> WebsiteAnalysisResult:
        """
        Analyzes a website by fetching its content, taking a screenshot,
        and using an AI connector for deep insights.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={'width': 1280, 'height': 720})
            page = await context.new_page()

            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
            except Exception as e:
                try:
                    await page.goto(url, wait_until="load", timeout=30000)
                except Exception as e2:
                    await browser.close()
                    raise Exception(f"Failed to load {url}: {str(e2)}")

            html_content = await page.content()

            # Take screenshot
            screenshot_dir = "storage/scout/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            safe_url = url.replace("https://", "").replace("http://", "").replace("/", "_").replace("?", "_").replace("&", "_")
            screenshot_path = f"{screenshot_dir}/{safe_url}.png"
            await page.screenshot(path=screenshot_path)

            metadata = {
                "title": await page.title(),
                "url": page.url,
                "elements": [],
                "screenshot_path": screenshot_path
            }

            # Extract UI elements with computed styles
            elements_data = await page.evaluate('''() => {
                const results = [];
                const allElements = document.querySelectorAll('h1, h2, h3, p, button, a, img');
                allElements.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    if (rect.width > 0 && rect.height > 0) {
                        results.push({
                            tag: el.tagName.toLowerCase(),
                            id: el.id || null,
                            classes: Array.from(el.classList),
                            text: el.innerText || (el.tagName === 'IMG' ? el.alt : "") || "",
                            attributes: {
                                href: el.href || "",
                                src: el.src || ""
                            },
                            bounding_box: {
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height
                            },
                            styles: {
                                color: style.color,
                                backgroundColor: style.backgroundColor,
                                fontFamily: style.fontFamily,
                                fontSize: style.fontSize,
                                fontWeight: style.fontWeight
                            }
                        });
                    }
                });
                return results.slice(0, 100);
            }''')

            metadata["elements"] = [UIElement(**el) for el in elements_data]

            # Use connector for AI analysis
            simplified_elements = [el.model_dump() for el in metadata["elements"]]
            analysis_data = await self.connector.analyze_website_data(
                url,
                html_content,
                {
                    "elements": simplified_elements,
                    "title": metadata["title"],
                    "screenshot_path": screenshot_path
                }
            )

            heatmap_path = screenshot_path.replace(".png", "_heatmap.png")
            ui_graph_path = screenshot_path.replace(".png", "_graph.json")

            # Mock heatmap and graph generation
            with open(heatmap_path, "wb") as f:
                with open(screenshot_path, "rb") as sf:
                    f.write(sf.read()) # Just copy the screenshot for mock heatmap

            import json
            with open(ui_graph_path, "w") as f:
                json.dump({"nodes": [el.tag for el in metadata["elements"]], "edges": []}, f)

            result = WebsiteAnalysisResult(
                url=url,
                screenshots=[screenshot_path],
                heatmap_path=heatmap_path,
                ui_graph_path=ui_graph_path,
                **analysis_data
            )

            # In a real implementation, we would assign the extracted UI hierarchy
            if analyze_ui and not result.ui_hierarchy:
                result.ui_hierarchy = UIHierarchy(elements=metadata["elements"])

            await browser.close()
            return result
