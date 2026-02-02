import uuid
from typing import List, Dict, Any
from agents.improvement_planner.models import (
    ImprovementPlan, WeakArea, ImprovementStrategy, AgentUpgrade
)

class ImprovementPlanner:
    def __init__(self, thresholds: Dict[str, float] = None):
        self.thresholds = thresholds or {
            "success_rate": 0.9,
            "avg_latency": 2.0 # seconds
        }

    def generate_plan(self, optimization_report: Dict[str, Any]) -> ImprovementPlan:
        weak_areas = []
        strategies = []
        upgrades = []

        # 1. Detect Weak Areas based on performance
        agent_perf = optimization_report.get("agent_performance", [])
        for perf in agent_perf:
            name = perf.get("agent_name", "unknown")
            success_rate = perf.get("success_rate", 1.0)
            avg_latency = perf.get("avg_execution_time_seconds", 0.0)

            if success_rate < self.thresholds["success_rate"]:
                weak_areas.append(WeakArea(
                    target_agent=name,
                    metric="success_rate",
                    current_value=success_rate,
                    threshold=self.thresholds["success_rate"],
                    reason=f"Agent '{name}' is failing too frequently."
                ))
                strategies.append(ImprovementStrategy(
                    id=str(uuid.uuid4()),
                    type="Refactor",
                    description=f"Investigate and fix failure points in '{name}'.",
                    expected_outcome="Increase success rate to > 90%",
                    priority=9
                ))
                upgrades.append(AgentUpgrade(
                    agent_name=name,
                    change_description="Bug fixes and error handling improvements."
                ))

            if avg_latency > self.thresholds["avg_latency"]:
                 weak_areas.append(WeakArea(
                    target_agent=name,
                    metric="avg_latency",
                    current_value=avg_latency,
                    threshold=self.thresholds["avg_latency"],
                    reason=f"Agent '{name}' is slower than the threshold."
                ))
                 strategies.append(ImprovementStrategy(
                    id=str(uuid.uuid4()),
                    type="Scaling",
                    description=f"Optimize resource allocation or logic for '{name}'.",
                    expected_outcome=f"Reduce latency below {self.thresholds['avg_latency']}s",
                    priority=7
                ))

        # 2. Analyze failure patterns
        failure_patterns = optimization_report.get("failure_patterns", [])
        for pattern in failure_patterns:
            desc = pattern.get("error_type", "Generic error")
            count = pattern.get("occurrence_count", 0)
            if count > 5:
                strategies.append(ImprovementStrategy(
                    id=str(uuid.uuid4()),
                    type="Training/Config",
                    description=f"Address recurring error pattern: {desc}",
                    expected_outcome=f"Decrease frequency of {desc} errors.",
                    priority=8
                ))

        summary = f"Detected {len(weak_areas)} weak areas. Proposed {len(strategies)} strategies for improvement."

        return ImprovementPlan(
            plan_id=str(uuid.uuid4()),
            weak_areas=weak_areas,
            strategies=strategies,
            suggested_upgrades=upgrades,
            summary=summary
        )
