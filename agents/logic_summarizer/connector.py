from abc import ABC, abstractmethod
from typing import Dict, Any, List

class LLMConnector(ABC):
    @abstractmethod
    async def complete(self, prompt: str) -> str:
        """
        Sends a prompt to the LLM and returns the text response.
        """
        pass

    @abstractmethod
    async def analyze_code(self, code_chunks: List[str]) -> Dict[str, Any]:
        """
        Analyzes code chunks and returns a structured dictionary matching LogicAnalysis model.
        """
        pass

class MockLLMConnector(LLMConnector):
    async def complete(self, prompt: str) -> str:
        return f"Mock response to: {prompt[:50]}..."

    async def analyze_code(self, code_chunks: List[str]) -> Dict[str, Any]:
        # Simulate LLM logic analysis
        combined_code = "\n".join(code_chunks)
        return {
            "summary": f"This is a mock summary of a module with {len(combined_code)} characters.",
            "purpose": "To provide a placeholder for testing the Logic Summarizer Agent.",
            "role": "utility",
            "risk_complexity_score": 3,
            "key_logic_points": [
                "Mock point 1: Input received correctly.",
                "Mock point 2: Processing simulated successfully."
            ]
        }
