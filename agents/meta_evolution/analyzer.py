from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from agents.meta_evolution.models import (
    EcosystemSnapshot, StructuralUpgrade, AgentMergeSplitSuggestion,
    TrendAnalysis, EvolutionStrategy
)
from fog.core.state import state_store
from fog.core.logging import logger

class MetaEvolutionAnalyzer:
    def __init__(self):
        self._ensure_state_keys()

    def _ensure_state_keys(self):
        state = state_store.get_state()
        if "ecosystem_snapshots" not in state:
            state["ecosystem_snapshots"] = []
        state_store._save()

    def take_snapshot(self) -> EcosystemSnapshot:
        state = state_store.get_state()
        agents = state.get("agents", {})
        tasks = state.get("tasks", {})

        agent_distribution = {}
        completed = 0
        failed = 0

        for task in tasks.values():
            agent = task.get("system_name")
            if agent:
                agent_distribution[agent] = agent_distribution.get(agent, 0) + 1

            status = task.get("status")
            if status == "completed":
                completed += 1
            elif status == "failed":
                failed += 1

        total_finished = completed + failed
        success_rate = completed / total_finished if total_finished > 0 else 1.0

        snapshot = EcosystemSnapshot(
            num_agents=len(agents),
            num_tasks=len(tasks),
            agent_distribution=agent_distribution,
            total_success_rate=success_rate
        )

        state["ecosystem_snapshots"].append(snapshot.model_dump(mode='json'))
        state_store._save()
        logger.info("ECOSYSTEM_SNAPSHOT_TAKEN", {"snapshot_id": snapshot.snapshot_id})
        return snapshot

    def analyze_trends(self) -> List[TrendAnalysis]:
        state = state_store.get_state()
        snapshots_data = state.get("ecosystem_snapshots", [])
        if len(snapshots_data) < 2:
            return [TrendAnalysis(
                metric="Ecosystem Data",
                growth_rate=0.0,
                trend_direction="Stable",
                observation="Not enough historical data for trend analysis."
            )]

        snapshots = [EcosystemSnapshot(**s) for s in snapshots_data]
        latest = snapshots[-1]
        previous = snapshots[-2]

        trends = []

        # Task Growth
        task_growth = (latest.num_tasks - previous.num_tasks) / previous.num_tasks if previous.num_tasks > 0 else 0.0
        trends.append(TrendAnalysis(
            metric="Task Volume",
            growth_rate=task_growth,
            trend_direction="Increasing" if task_growth > 0.05 else "Decreasing" if task_growth < -0.05 else "Stable",
            observation=f"Task volume has changed by {task_growth:.1%} compared to the last snapshot."
        ))

        # Agent Growth
        agent_growth = latest.num_agents - previous.num_agents
        trends.append(TrendAnalysis(
            metric="Agent Count",
            growth_rate=float(agent_growth),
            trend_direction="Increasing" if agent_growth > 0 else "Decreasing" if agent_growth < 0 else "Stable",
            observation=f"Ecosystem now has {latest.num_agents} agents ({'+' if agent_growth >= 0 else ''}{agent_growth} change)."
        ))

        return trends

    def propose_evolution(self) -> EvolutionStrategy:
        snapshot = self.take_snapshot()
        trends = self.analyze_trends()

        upgrades = []
        agent_changes = []

        # Logic for upgrades
        if snapshot.num_tasks > 100:
            upgrades.append(StructuralUpgrade(
                title="Implement Task Caching Layer",
                description="Ecosystem is handling significant volume. A caching layer for repetitive analysis tasks could reduce latency.",
                rationale="High task volume detected.",
                estimated_impact="High"
            ))

        # Logic for agent merges/splits
        for agent, count in snapshot.agent_distribution.items():
            if count > 50:
                agent_changes.append(AgentMergeSplitSuggestion(
                    suggestion_type="Split",
                    target_agents=[agent],
                    reason=f"Agent '{agent}' is handling a disproportionate number of tasks ({count}).",
                    proposed_action=f"Consider splitting '{agent}' into specialized sub-agents to improve parallelization and maintainability."
                ))
            elif count < 2 and snapshot.num_tasks > 20:
                agent_changes.append(AgentMergeSplitSuggestion(
                    suggestion_type="Merge",
                    target_agents=[agent],
                    reason=f"Agent '{agent}' has very low utilization ({count} tasks).",
                    proposed_action=f"Consider merging '{agent}' with a related agent to reduce ecosystem overhead."
                ))

        if snapshot.num_agents > 10:
             upgrades.append(StructuralUpgrade(
                title="Introduce Centralized Message Broker",
                description="Large number of agents detected. Direct HTTP communication may become brittle.",
                rationale="Agent count exceeding optimal direct-connect threshold.",
                estimated_impact="Medium"
            ))

        summary = f"Ecosystem currently consists of {snapshot.num_agents} agents handling {snapshot.num_tasks} tasks. "
        summary += f"Identified {len(upgrades)} structural upgrades and {len(agent_changes)} agent reorganization opportunities."

        return EvolutionStrategy(
            trends=trends,
            upgrades=upgrades,
            agent_changes=agent_changes,
            summary=summary
        )
