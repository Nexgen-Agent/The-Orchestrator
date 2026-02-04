import pytest
import os
import json
from agents.personality_engine.analyzer import InteractionAnalyzer
from agents.personality_engine.engine import FingerprintManager, StyleAdaptor
from agents.personality_engine.models import StyleFingerprint

def test_analyzer_formal():
    analyzer = InteractionAnalyzer()
    text = "Please appreciate the formal nature of this request. Furthermore, I sincerely thank you."
    analysis = analyzer.analyze_text(text)
    assert analysis.tone == "formal"
    assert analysis.energy.energy_level >= 0.5
    assert analysis.rhythm["avg_sentence_length"] > 5

def test_analyzer_casual_energy():
    analyzer = InteractionAnalyzer()
    text = "Yo sup!!! lol this is cool ASAP!!!!"
    analysis = analyzer.analyze_text(text)
    assert analysis.tone == "casual"
    assert analysis.energy.energy_level > 0.7
    assert analysis.energy.urgency is True
    assert "lol" in analysis.learned_slang

def test_fingerprint_manager(tmp_path):
    storage = tmp_path / "test_profiles.json"
    manager = FingerprintManager(storage_path=str(storage))

    analyzer = InteractionAnalyzer()
    analysis = analyzer.analyze_text("Yo sup lol")
    manager.update_profile("user1", analysis)

    profile = manager.get_profile("user1")
    assert profile.user_id == "user1"
    assert profile.formal_score < 0.5
    assert "lol" in profile.slang_list

    # Reload
    manager2 = FingerprintManager(storage_path=str(storage))
    profile2 = manager2.get_profile("user1")
    assert profile2.formal_score == profile.formal_score

def test_style_adaptor():
    profile = StyleFingerprint(user_id="test", formal_score=0.9, sentence_length_avg=25)
    params = StyleAdaptor.generate_adaptation(profile)
    assert params.target_tone == "formal"
    assert params.verbosity_target == "high"
    assert params.humor_allowed is False

    profile_casual = StyleFingerprint(user_id="test2", formal_score=0.1, sentence_length_avg=5)
    params_casual = StyleAdaptor.generate_adaptation(profile_casual)
    assert params_casual.target_tone == "casual"
    assert params_casual.verbosity_target == "low"
    assert params_casual.humor_allowed is True
