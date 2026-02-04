import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from agents.system_resilience.models import ResilienceAction, ResilienceActionType, ResilienceReport
from fog.core.state import state_store
from fog.core.logging import logger
from fog.models.task import TaskPacket, TaskStatus
from agents.human_control_interface.control import HumanControlInterface

class ResilienceManager:
    def __init__(self):
        self._ensure_state_keys()
        self.hci = HumanControlInterface()

    def _ensure_state_keys(self):
        state = state_store.get_state()
        if "resilience_actions" not in state:
            state["resilience_actions"] = []
        if "safe_mode" not in state:
            state["safe_mode"] = False
        state_store._save()

    async def detect_and_fix(self) -> ResilienceReport:
        state = state_store.get_state()
        tasks = state.get("tasks", {})

        failing_patterns = []
        actions = []
        recovered_count = 0

        # 1. Detect Failing Tasks and Try Recovery
        failed_tasks = [t for t in tasks.values() if t.get("status") == TaskStatus.FAILED]

        for task_dict in failed_tasks:
            task_id = task_dict.get("task_id")
            result_dict = task_dict.get("result", {})
            error = str(result_dict.get("error", ""))

            # Simple heuristic for recovery: if it's a timeout or network error, retry once more if retries < max + 1
            if "timeout" in error.lower() or "timed out" in error.lower() or "failed to send" in error.lower():
                action = ResilienceAction(
                    action_type=ResilienceActionType.RECOVER_TASK,
                    target=task_id,
                    reason=f"Attempting recovery for task {task_id} due to transient error: {error}"
                )

                success = await self._recover_task(task_dict)
                if success:
                    action.status = "Completed"
                    recovered_count += 1
                else:
                    action.status = "Failed"

                actions.append(action)
                self._record_action(action)

        # 2. Detect Agent Instability
        agent_failures = {}
        for task in tasks.values():
            if task.get("status") == TaskStatus.FAILED:
                agent = task.get("system_name")
                agent_failures[agent] = agent_failures.get(agent, 0) + 1

        for agent, count in agent_failures.items():
            if count > 5:
                failing_patterns.append(f"Agent '{agent}' has high failure rate ({count} failures)")

                # Restart Agent Action (Mock)
                action = ResilienceAction(
                    action_type=ResilienceActionType.RESTART_AGENT,
                    target=agent,
                    reason=f"Agent {agent} exceeding failure threshold."
                )

                # In a mock environment, we might just toggle it off and on or send a 'restart' signal
                logger.info("RESTARTING_AGENT_MOCK", {"agent": agent})
                action.status = "Completed"
                actions.append(action)
                self._record_action(action)

        # 3. Trigger Safe Mode if things are really bad
        safe_mode_active = state.get("safe_mode", False)
        if len(failing_patterns) > 2 and not safe_mode_active:
            action = ResilienceAction(
                action_type=ResilienceActionType.TRIGGER_SAFE_MODE,
                target="system",
                reason="Multiple agent failures detected. Activating Safe Mode."
            )
            self.set_safe_mode(True)
            action.status = "Completed"
            actions.append(action)
            self._record_action(action)
            safe_mode_active = True

        report = ResilienceReport(
            failing_patterns=failing_patterns,
            actions_taken=actions,
            recovered_tasks_count=recovered_count,
            system_status="Critical" if safe_mode_active else "Degraded" if actions else "Nominal",
            safe_mode_active=safe_mode_active
        )

        return report

    async def _recover_task(self, task_dict: Dict[str, Any]) -> bool:
        from fog.core.engine import orchestration_engine
        try:
            task = TaskPacket(**task_dict)
            task.status = TaskStatus.PENDING
            task.retries = 0
            await orchestration_engine.submit_task(task)
            logger.info("TASK_RECOVERY_INITIATED", {"task_id": task.task_id})
            return True
        except Exception as e:
            logger.error("TASK_RECOVERY_FAILED", {"task_id": task_dict.get("task_id"), "error": str(e)})
            return False

    def _record_action(self, action: ResilienceAction):
        state = state_store.get_state()
        state["resilience_actions"].append(action.model_dump(mode='json'))
        state_store._save()

    def set_safe_mode(self, active: bool):
        state = state_store.get_state()
        state["safe_mode"] = active
        state_store._save()

        # When safe mode is activated, we might want to pause orchestration
        if active:
            self.hci.set_pause(True)
            logger.warning("SAFE_MODE_ACTIVATED_ORCHESTRATION_PAUSED")
        else:
            self.hci.set_pause(False)
            logger.info("SAFE_MODE_DEACTIVATED")

    def get_resilience_history(self) -> List[ResilienceAction]:
        state = state_store.get_state()
        return [ResilienceAction(**a) for a in state.get("resilience_actions", [])]
