import pytest
import asyncio
import os
import json
from agents.shooting_star_intelligence.intelligence import ShootingStarIntelligence
from agents.shooting_star_intelligence.models import CapabilityProgress, IntelligenceReport

@pytest.mark.asyncio
async def test_track_progress():
    engine = ShootingStarIntelligence()
    progress = await engine.track_progress("test_agent", 80.0)

    assert progress.agent_name == "test_agent"
    assert progress.capability_percentage == 80.0
    assert progress.deployment_probability == 80.0 / 98.0
    assert engine.readiness.overall_readiness == 80.0

@pytest.mark.asyncio
async def test_gather_intelligence():
    engine = ShootingStarIntelligence()
    intel = await engine.gather_intelligence("python")

    assert len(intel) > 0
    assert intel[0].topic_tags[0] == "python"

@pytest.mark.asyncio
async def test_perform_readiness_audit(tmp_path):
    project_path = str(tmp_path)
    # Create a dummy python file
    with open(os.path.join(project_path, "dummy.py"), "w") as f:
        f.write("import os")

    engine = ShootingStarIntelligence(data_path=str(tmp_path / "readiness.json"))
    report = await engine.perform_readiness_audit("test_agent", project_path)

    assert isinstance(report, IntelligenceReport)
    assert report.agent_name == "test_agent"
    assert len(report.learning_sources) > 0
    assert report.status == "not_ready" # Cap defaults to 50 if not tracked
