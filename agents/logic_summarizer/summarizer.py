import os
from typing import List, Optional
from agents.logic_summarizer.connector import LLMConnector
from agents.logic_summarizer.models import LogicAnalysis, SummarizationOutput
from agents.logic_summarizer.utils import chunk_text

class LogicSummarizer:
    def __init__(self, connector: LLMConnector):
        self.connector = connector

    async def summarize_file(self, file_path: str) -> SummarizationOutput:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found.")

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)
        analysis_dict = await self.connector.analyze_code(chunks)
        analysis = LogicAnalysis(**analysis_dict)

        return SummarizationOutput(
            file_path=file_path,
            analysis=analysis
        )

    async def summarize_text(self, text: str, label: str = "custom_text") -> SummarizationOutput:
        chunks = chunk_text(text)
        analysis_dict = await self.connector.analyze_code(chunks)
        analysis = LogicAnalysis(**analysis_dict)

        return SummarizationOutput(
            file_path=label,
            analysis=analysis
        )
