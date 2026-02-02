import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from agents.self_evaluator.models import (
    EvaluationInput, AgentMetrics, EvaluationReport
)

class SelfEvaluator:
    def __init__(self, storage_path: str = "storage/self_evaluations.json"):
        self.storage_path = storage_path
        self._ensure_storage_exists()
        self.data: Dict[str, List[Dict[str, Any]]] = self._load_data()

    def _ensure_storage_exists(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w") as f:
                json.dump({}, f)

    def _load_data(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            with open(self.storage_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return {}

    def _save_data(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.data, f, indent=2, default=str)

    def add_task_result(self, result: EvaluationInput):
        agent_name = result.agent_name
        if agent_name not in self.data:
            self.data[agent_name] = []

        self.data[agent_name].append(result.model_dump(mode='json'))

        # Keep only last 100 entries per agent
        if len(self.data[agent_name]) > 100:
            self.data[agent_name] = self.data[agent_name][-100:]

        self._save_data()

    def evaluate_agent(self, agent_name: str) -> Optional[EvaluationReport]:
        history = self.data.get(agent_name, [])
        if not history:
            return None

        total_tasks = len(history)
        successes = [h for h in history if h.get("success")]
        success_rate = len(successes) / total_tasks

        latencies = [h.get("execution_time_seconds", 0) for h in history]
        avg_latency = sum(latencies) / total_tasks

        errors = [h.get("error_message") for h in history if h.get("error_message")]
        failure_patterns = self._detect_patterns(errors)

        metrics = AgentMetrics(
            total_tasks=total_tasks,
            success_rate=success_rate,
            avg_execution_time=avg_latency,
            failure_patterns=failure_patterns
        )

        score = self._calculate_score(success_rate, avg_latency)
        suggestions = self._generate_suggestions(metrics)

        return EvaluationReport(
            agent_name=agent_name,
            metrics=metrics,
            performance_score=score,
            improvement_suggestions=suggestions,
            history_depth=total_tasks
        )

    def _detect_patterns(self, errors: List[str]) -> List[str]:
        # Simple frequency analysis for recurring error substrings
        if not errors: return []
        patterns = {}
        for err in errors:
            # Take first 50 chars as a rough pattern
            p = err[:50]
            patterns[p] = patterns.get(p, 0) + 1

        return [p for p, count in patterns.items() if count > 1]

    def _calculate_score(self, success_rate: float, avg_latency: float) -> int:
        # Success rate is 80% of score, latency 20%
        # Latency normalized against 5 seconds max acceptable average
        norm_latency = max(0, 1.0 - (avg_latency / 5.0))
        score = (success_rate * 80) + (norm_latency * 20)
        return int(score)

    def _generate_suggestions(self, metrics: AgentMetrics) -> List[str]:
        suggestions = []
        if metrics.success_rate < 0.9:
            suggestions.append("High failure rate detected. Implement more robust error handling and retry logic.")

        if metrics.avg_execution_time > 2.0:
            suggestions.append("Execution time is high. Consider optimizing internal processing or offloading I/O.")

        if metrics.failure_patterns:
            suggestions.append(f"Investigate recurring error patterns: {', '.join(metrics.failure_patterns[:3])}")

        if not suggestions:
            suggestions.append("Performance is excellent. Continue monitoring.")

        return suggestions
