import asyncio
from typing import List, Dict, Any
from agents.website_insight_scout.scout import WebsiteScout
from agents.website_insight_scout.models import WebsiteAnalysisResult

class MultiWebsiteScout:
    def __init__(self, scout: WebsiteScout):
        self.scout = scout

    async def analyze_batch(self, urls: List[str], **kwargs) -> List[WebsiteAnalysisResult]:
        """
        Analyzes multiple websites in parallel.
        """
        tasks = [self.scout.analyze(url, **kwargs) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error analyzing {urls[i]}: {result}")
            else:
                valid_results.append(result)

        return valid_results
