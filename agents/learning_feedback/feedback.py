import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from agents.learning_feedback.models import (
    LearningInsight, RuleUpdateSuggestion, LearningMemory, FeedbackReport
)
from fog.core.state import state_store
from fog.core.logging import logger

class LearningFeedbackAgent:
    def __init__(self, memory_path: str = "storage/learning_memory.json", evaluations_path: str = "storage/self_evaluations.json"):
        self.memory_path = memory_path
        self.evaluations_path = evaluations_path
        self.memory = self._load_memory()

    def _load_memory(self) -> LearningMemory:
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, 'r') as f:
                    return LearningMemory(**json.load(f))
            except Exception:
                pass
        return LearningMemory()

    def _save_memory(self):
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        with open(self.memory_path, 'w') as f:
            json.dump(self.memory.model_dump(mode='json'), f, indent=4)

    def _load_evaluations(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.evaluations_path):
            try:
                with open(self.evaluations_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def analyze_performance(self) -> FeedbackReport:
        evaluations = self._load_evaluations()
        state = state_store.get_state()

        insights = []
        suggestions = []

        # 1. Detect Latency Inefficiencies
        agent_latency = {}
        for eval_entry in evaluations:
            name = eval_entry.get("agent_name")
            metrics = eval_entry.get("metrics", {})
            avg_time = metrics.get("avg_execution_time", 0)
            if name and avg_time > 10.0: # Threshold of 10 seconds
                agent_latency[name] = avg_time

        for name, latency in agent_latency.items():
            insight = LearningInsight(
                category="latency",
                description=f"Agent '{name}' consistently exhibits high latency (avg {latency:.2f}s).",
                evidence={"avg_latency": latency},
                impact_score=6
            )
            insights.append(insight)
            suggestions.append(RuleUpdateSuggestion(
                suggested_update=f"Increase timeout for {name} to {latency * 1.5:.0f}s",
                rationale="Avoid premature timeouts for slow but successful processes.",
                affected_components=[name]
            ))

        # 2. Detect Failure Patterns
        agent_failures = {}
        for eval_entry in evaluations:
            name = eval_entry.get("agent_name")
            metrics = eval_entry.get("metrics", {})
            success_rate = metrics.get("success_rate", 1.0)
            patterns = metrics.get("failure_patterns", [])
            if name and success_rate < 0.8:
                agent_failures[name] = {"rate": success_rate, "patterns": patterns}

        for name, data in agent_failures.items():
            insight = LearningInsight(
                category="failure_pattern",
                description=f"Agent '{name}' has a low success rate ({data['rate']:.1%}).",
                evidence=data,
                impact_score=8
            )
            insights.append(insight)
            if data["rate"] < 0.5:
                suggestions.append(RuleUpdateSuggestion(
                    suggested_update=f"Route complex tasks away from {name} until reliability improves.",
                    rationale="Critical failure threshold reached.",
                    affected_components=[name, "OrchestrationEngine"]
                ))

        # Update memory
        self.memory.insights.extend(insights)
        self.memory.insights = self.memory.insights[-100:] # Keep last 100
        self.memory.last_updated = datetime.now(timezone.utc)
        self._save_memory()

        summary = f"Analysis complete. Generated {len(insights)} insights and {len(suggestions)} suggestions."

        return FeedbackReport(
            insights=insights,
            suggestions=suggestions,
            summary=summary
        )

    def feed_to_evolution_coordinator(self, report: FeedbackReport):
        """
        In a real system, this would submit a task or call an API.
        For now, we log the feed action.
        """
        logger.info("FEEDING_TO_EVOLUTION_COORDINATOR", {
            "report_id": report.report_id,
            "suggestions_count": len(report.suggestions)
        })
        # Mock logic: update a specific state key that the coordinator might look at
        state = state_store.get_state()
        if "evolution_proposals" not in state:
            state["evolution_proposals"] = []

        for s in report.suggestions:
            state["evolution_proposals"].append({
                "source": "LearningFeedbackAgent",
                "suggestion": s.model_dump(mode='json'),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        state_store._save()
