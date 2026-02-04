import re
from typing import List, Dict, Any
from agents.personality_engine.models import InteractionAnalysis, EnergyMapping

class InteractionAnalyzer:
    def __init__(self):
        self.formal_keywords = {"please", "thank you", "sincerely", "regards", "appreciate", "furthermore", "consequently"}
        self.casual_keywords = {"yo", "hey", "sup", "lol", "lmao", "thanks", "gonna", "wanna", "cool", "awesome"}
        self.urgent_keywords = {"asap", "urgent", "immediately", "quick", "fast", "now", "hurry"}

    def analyze_text(self, text: str) -> InteractionAnalysis:
        words = re.findall(r'\w+', text.lower())
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

        if not words:
            return InteractionAnalysis(
                text_sample=text,
                tone="neutral",
                energy=EnergyMapping(energy_level=0.5, emotion="neutral", urgency=False),
                rhythm={"avg_sentence_length": 0.0, "avg_word_length": 0.0}
            )

        # Tone analysis
        formal_count = sum(1 for w in words if w in self.formal_keywords)
        casual_count = sum(1 for w in words if w in self.casual_keywords)

        tone = "neutral"
        if formal_count > casual_count:
            tone = "formal"
        elif casual_count > formal_count:
            tone = "casual"

        # Energy and Urgency
        punctuation_count = len(re.findall(r'[!]', text))
        energy_level = 0.5
        if punctuation_count > 0:
            energy_level += 0.2
        if any(w in words for w in self.urgent_keywords):
            energy_level += 0.2

        urgency = any(w in words for w in self.urgent_keywords)

        # Rhythm
        avg_sentence_length = len(words) / len(sentences) if sentences else len(words)
        avg_word_length = sum(len(w) for w in words) / len(words)

        return InteractionAnalysis(
            text_sample=text,
            tone=tone,
            energy=EnergyMapping(
                energy_level=min(energy_level, 1.0),
                emotion="positive" if casual_count > 0 else "neutral",
                urgency=urgency
            ),
            rhythm={
                "avg_sentence_length": avg_sentence_length,
                "avg_word_length": avg_word_length,
                "punctuation_density": punctuation_count / len(text) if text else 0
            },
            learned_slang=[w for w in words if w in self.casual_keywords]
        )
