from abc import ABC, abstractmethod
from typing import Dict, Any, List
from agents.semantic_tagger.models import SemanticAnalysis, IntentTag, TagCategory

class AIModelConnector(ABC):
    @abstractmethod
    async def analyze_intent(self, text: str) -> SemanticAnalysis:
        """
        Analyzes the intent of the provided text and returns SemanticAnalysis.
        """
        pass

class MockAIModelConnector(AIModelConnector):
    async def analyze_intent(self, text: str) -> SemanticAnalysis:
        # Simulate AI analysis based on keywords in the text
        tags = []
        decision_rules = []
        persuasion_logic = []
        business_flows = []
        behavioral_triggers = []

        text_lower = text.lower()

        if "if" in text_lower or "else" in text_lower or "switch" in text_lower:
            tags.append(IntentTag(
                category=TagCategory.BUSINESS,
                tag_name="Decision Logic",
                confidence=0.9,
                description="Detected conditional logic which may represent business decision rules."
            ))
            decision_rules.append("Conditional logic block detected.")

        if "buy" in text_lower or "click" in text_lower or "offer" in text_lower:
            tags.append(IntentTag(
                category=TagCategory.PSYCHOLOGY,
                tag_name="Persuasion",
                confidence=0.85,
                description="Detected keywords often used in persuasive or marketing context."
            ))
            persuasion_logic.append("Incentive-based language detected.")

        if "transaction" in text_lower or "payment" in text_lower or "order" in text_lower:
            tags.append(IntentTag(
                category=TagCategory.BUSINESS,
                tag_name="Financial Flow",
                confidence=0.95,
                description="Detected terms related to financial business flows."
            ))
            business_flows.append("Payment processing flow detected.")

        if "alert" in text_lower or "notif" in text_lower or "urg" in text_lower:
            tags.append(IntentTag(
                category=TagCategory.PSYCHOLOGY,
                tag_name="Urgency Trigger",
                confidence=0.8,
                description="Detected urgency cues that may trigger user behavior."
            ))
            behavioral_triggers.append("Urgency signal detected.")

        if "truth" in text_lower or "ethic" in text_lower or "logic" in text_lower:
            tags.append(IntentTag(
                category=TagCategory.PHILOSOPHY,
                tag_name="Ethical Logic",
                confidence=0.75,
                description="Detected terms related to ethical or logical reasoning."
            ))

        return SemanticAnalysis(
            tags=tags,
            decision_rules_detected=decision_rules,
            persuasion_logic_detected=persuasion_logic,
            business_flows_detected=business_flows,
            behavioral_triggers_detected=behavioral_triggers
        )
