import os
from typing import Optional
from agents.semantic_tagger.connector import AIModelConnector
from agents.semantic_tagger.models import SemanticAnalysis

class SemanticTagger:
    def __init__(self, connector: AIModelConnector):
        self.connector = connector

    async def tag_file(self, file_path: str) -> SemanticAnalysis:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        analysis = await self.connector.analyze_intent(text)
        analysis.file_path = file_path
        return analysis

    async def tag_text(self, text: str) -> SemanticAnalysis:
        return await self.connector.analyze_intent(text)
