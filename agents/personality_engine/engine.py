import os
import json
from typing import Dict, Optional, List
from datetime import datetime, timezone
from agents.personality_engine.models import StyleFingerprint, InteractionAnalysis, AdaptationParams

class FingerprintManager:
    def __init__(self, storage_path: str = "storage/personality/profiles.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.profiles: Dict[str, StyleFingerprint] = self._load_profiles()

    def _load_profiles(self) -> Dict[str, StyleFingerprint]:
        if not os.path.exists(self.storage_path):
            return {}
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                return {uid: StyleFingerprint(**prof) for uid, prof in data.items()}
        except Exception:
            return {}

    def save_profiles(self):
        with open(self.storage_path, "w") as f:
            json.dump({uid: prof.model_dump(mode='json') for uid, prof in self.profiles.items()}, f, indent=2)

    def get_profile(self, user_id: str) -> StyleFingerprint:
        if user_id not in self.profiles:
            self.profiles[user_id] = StyleFingerprint(user_id=user_id)
        return self.profiles[user_id]

    def update_profile(self, user_id: str, analysis: InteractionAnalysis):
        profile = self.get_profile(user_id)

        # Incremental update (moving average)
        alpha = 0.3

        formal_val = 1.0 if analysis.tone == "formal" else (0.0 if analysis.tone == "casual" else 0.5)
        profile.formal_score = (1 - alpha) * profile.formal_score + alpha * formal_val
        profile.energy_level_avg = (1 - alpha) * profile.energy_level_avg + alpha * analysis.energy.energy_level

        if profile.sentence_length_avg == 0:
            profile.sentence_length_avg = analysis.rhythm["avg_sentence_length"]
        else:
            profile.sentence_length_avg = (1 - alpha) * profile.sentence_length_avg + alpha * analysis.rhythm["avg_sentence_length"]

        profile.punctuation_density = (1 - alpha) * profile.punctuation_density + alpha * analysis.rhythm.get("punctuation_density", 0)

        # Update slang list
        for slang in analysis.learned_slang:
            if slang not in profile.slang_list:
                profile.slang_list.append(slang)

        profile.last_updated = datetime.now(timezone.utc)
        self.save_profiles()

class StyleAdaptor:
    @staticmethod
    def generate_adaptation(profile: StyleFingerprint) -> AdaptationParams:
        target_tone = "neutral"
        if profile.formal_score > 0.7:
            target_tone = "formal"
        elif profile.formal_score < 0.3:
            target_tone = "casual"

        verbosity = "medium"
        if profile.sentence_length_avg > 20:
            verbosity = "high"
        elif profile.sentence_length_avg < 8:
            verbosity = "low"

        return AdaptationParams(
            target_tone=target_tone,
            mirroring_ratio=0.8,
            verbosity_target=verbosity,
            complexity_target=profile.formal_score,
            humor_allowed=profile.formal_score < 0.8
        )
