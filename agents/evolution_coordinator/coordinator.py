import json
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from agents.evolution_coordinator.models import EvolutionStep, ImprovementCycle, EvolutionReport
from fog.core.state import state_store
from fog.core.logging import logger
from fog.core.backup import backup_manager
import asyncio

class EvolutionCoordinator:
    def __init__(self, log_file_path: str = "storage/audit.log"):
        self.log_file_path = log_file_path
        self.active_cycles = []
        self.evolution_history = []

    def monitor_agent_performance(self) -> Dict[str, Dict[str, Any]]:
        """
        Assesses agent health and performance from system state and logs.
        Returns a map of agent_name -> metrics.
        """
        state = state_store.get_state()
        tasks = state.get("tasks", {})

        agent_metrics = {}
        for tid, task in tasks.items():
            agent = task.get("system_name")
            if not agent: continue

            if agent not in agent_metrics:
                agent_metrics[agent] = {"total": 0, "completed": 0, "failed": 0, "retries": 0}

            agent_metrics[agent]["total"] += 1
            status = task.get("status")
            if status == "completed":
                agent_metrics[agent]["completed"] += 1
            elif status == "failed":
                agent_metrics[agent]["failed"] += 1

            agent_metrics[agent]["retries"] += task.get("retries", 0)

        for agent, metrics in agent_metrics.items():
            total = metrics["total"]
            metrics["success_rate"] = metrics["completed"] / total if total > 0 else 1.0
            metrics["avg_retries"] = metrics["retries"] / total if total > 0 else 0.0

        return agent_metrics

    def trigger_improvement_cycle(self) -> Optional[ImprovementCycle]:
        """
        Identifies agents requiring upgrades and creates an improvement cycle.
        """
        metrics = self.monitor_agent_performance()
        steps = []

        for agent, data in metrics.items():
            if data["success_rate"] < 0.9 or data["avg_retries"] > 0.5:
                steps.append(EvolutionStep(
                    step_id=str(uuid.uuid4()),
                    target_agent=agent,
                    improvement_type="Performance" if data["success_rate"] < 0.9 else "Stability",
                    description=f"Improve {agent} due to low success rate ({data['success_rate']:.2f}) or high retries ({data['avg_retries']:.2f}).",
                    status="Pending"
                ))

        if not steps:
            return None

        cycle = ImprovementCycle(
            cycle_id=str(uuid.uuid4()),
            analysis_period_start=datetime.now() - timedelta(days=1),
            analysis_period_end=datetime.now(),
            steps=steps,
            overall_status="InProgress"
        )
        self.active_cycles.append(cycle)
        return cycle

    async def apply_evolution_step(self, step: EvolutionStep, project_path: str):
        """
        Applies an evolution step with safety backups.
        """
        logger.info("APPLYING_EVOLUTION_STEP", {"step_id": step.step_id, "agent": step.target_agent})

        # 1. Mandatory Backup
        try:
            step.backup_id = await asyncio.to_thread(
                backup_manager.create_backup,
                project_path,
                f"Backup before evolution step {step.step_id} for {step.target_agent}"
            )
        except Exception as e:
            step.status = "Failed"
            logger.error("EVOLUTION_BACKUP_FAILED", {"step_id": step.step_id, "error": str(e)})
            return

        # 2. Apply "Upgrades" (In a real system, this might modify code or config)
        # For now, we simulate success
        await asyncio.sleep(1)

        step.status = "Applied"
        step.applied_at = datetime.now()
        self.evolution_history.append(step)
        logger.info("EVOLUTION_STEP_APPLIED", {"step_id": step.step_id})
