import pytest
from agents.improvement_planner.planner import ImprovementPlanner

def test_planner_detects_low_success_rate():
    planner = ImprovementPlanner(thresholds={"success_rate": 0.9, "avg_latency": 2.0})
    report = {
        "agent_performance": [
            {
                "agent_name": "faulty_agent",
                "success_rate": 0.5,
                "avg_execution_time_seconds": 1.0
            }
        ],
        "failure_patterns": []
    }

    plan = planner.generate_plan(report)

    assert len(plan.weak_areas) == 1
    assert plan.weak_areas[0].target_agent == "faulty_agent"
    assert plan.weak_areas[0].metric == "success_rate"
    assert any(s.type == "Refactor" for s in plan.strategies)
    assert any(u.agent_name == "faulty_agent" for u in plan.suggested_upgrades)

def test_planner_detects_high_latency():
    planner = ImprovementPlanner(thresholds={"success_rate": 0.9, "avg_latency": 2.0})
    report = {
        "agent_performance": [
            {
                "agent_name": "slow_agent",
                "success_rate": 0.95,
                "avg_execution_time_seconds": 5.0
            }
        ],
        "failure_patterns": []
    }

    plan = planner.generate_plan(report)

    assert len(plan.weak_areas) == 1
    assert plan.weak_areas[0].target_agent == "slow_agent"
    assert plan.weak_areas[0].metric == "avg_latency"
    assert any(s.type == "Scaling" for s in plan.strategies)

def test_planner_detects_failure_patterns():
    planner = ImprovementPlanner()
    report = {
        "agent_performance": [],
        "failure_patterns": [
            {
                "error_type": "TimeoutError",
                "occurrence_count": 10
            }
        ]
    }

    plan = planner.generate_plan(report)
    assert any("TimeoutError" in s.description for s in plan.strategies)
