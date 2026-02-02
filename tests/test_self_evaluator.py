import pytest
import os
import json
from agents.self_evaluator.evaluator import SelfEvaluator
from agents.self_evaluator.models import EvaluationInput

@pytest.fixture
def temp_storage(tmp_path):
    storage_file = tmp_path / "test_evals.json"
    return str(storage_file)

def test_add_and_evaluate(temp_storage):
    evaluator = SelfEvaluator(storage_path=temp_storage)

    # Add some results
    evaluator.add_task_result(EvaluationInput(
        agent_name="test_agent",
        task_id="t1",
        success=True,
        execution_time_seconds=1.0
    ))
    evaluator.add_task_result(EvaluationInput(
        agent_name="test_agent",
        task_id="t2",
        success=False,
        execution_time_seconds=2.0,
        error_message="Timeout error occurred"
    ))
    evaluator.add_task_result(EvaluationInput(
        agent_name="test_agent",
        task_id="t3",
        success=False,
        execution_time_seconds=2.1,
        error_message="Timeout error occurred"
    ))

    report = evaluator.evaluate_agent("test_agent")

    assert report.agent_name == "test_agent"
    assert report.metrics.total_tasks == 3
    assert report.metrics.success_rate == pytest.approx(0.333, 0.01)
    assert report.metrics.avg_execution_time == pytest.approx(1.7, 0.1)
    # Pattern should be detected since it appeared twice
    assert any("Timeout error" in p for p in report.metrics.failure_patterns)
    assert report.performance_score < 50 # Low success rate

def test_suggestions(temp_storage):
    evaluator = SelfEvaluator(storage_path=temp_storage)

    # Excellent performance
    evaluator.add_task_result(EvaluationInput(
        agent_name="pro_agent",
        task_id="p1",
        success=True,
        execution_time_seconds=0.1
    ))

    report = evaluator.evaluate_agent("pro_agent")
    assert "Performance is excellent" in report.improvement_suggestions[0]
    assert report.performance_score > 90

@pytest.mark.asyncio
async def test_handler_integration(temp_storage, monkeypatch):
    from agents.self_evaluator import handler

    # Patch SelfEvaluator to use temp_storage
    monkeypatch.setattr(handler, "SelfEvaluator", lambda: SelfEvaluator(storage_path=temp_storage))

    # Test log_task
    log_task = {
        "payload": {
            "action": "log_task",
            "agent_name": "agent_x",
            "task_id": "x1",
            "success": True,
            "execution_time_seconds": 0.5
        }
    }
    resp = await handler.handle_task(log_task)
    assert resp["status"] == "success"

    # Test evaluate
    eval_task = {
        "payload": {
            "action": "evaluate",
            "agent_name": "agent_x"
        }
    }
    resp = await handler.handle_task(eval_task)
    assert resp["status"] == "success"
    assert resp["result"]["agent_name"] == "agent_x"
    assert resp["result"]["performance_score"] > 80
