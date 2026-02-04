import asyncio
from typing import List, Dict, Any, Optional
from fog.models.task import TaskPacket, TaskStatus, TaskType
from fog.core.connector import agent_registry
from fog.core.queue import task_queue
from fog.core.state import state_store
from fog.core.backup import backup_manager
from fog.core.logging import logger
from agents.human_control_interface.control import HumanControlInterface
from agents.human_control_interface.models import ApprovalStatus

class OrchestrationEngine:
    def __init__(self):
        self.running = False
        self._workers = []

    async def start(self, num_workers: int = 5):
        self.running = True
        self._workers = [asyncio.create_task(self._worker()) for _ in range(num_workers)]
        logger.info("ENGINE_STARTED", {"num_workers": num_workers})

    async def stop(self):
        self.running = False
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        logger.info("ENGINE_STOPPED")

    async def submit_task(self, task: TaskPacket):
        # Safety rule: backup before modification
        if task.task_type == TaskType.MODIFICATION and not task.backup_id:
            project_path = task.payload.get("project_path")
            if project_path:
                try:
                    task.backup_id = await asyncio.to_thread(
                        backup_manager.create_backup,
                        project_path,
                        f"Auto-backup before {task.task_id}"
                    )
                except Exception as e:
                    logger.error("BACKUP_FAILED_MODIFICATION_ABORTED", {"task_id": task.task_id, "error": str(e)})
                    task.status = TaskStatus.FAILED
                    task.result = {"error": f"Backup failed: {str(e)}"}
                    state_store.update_task(task.task_id, task.model_dump(mode='json'))
                    return
            else:
                logger.error("MODIFICATION_TASK_WITHOUT_PROJECT_PATH", {"task_id": task.task_id})
                task.status = TaskStatus.FAILED
                task.result = {"error": "Modification task requires project_path in payload for safety backup"}
                state_store.update_task(task.task_id, task.model_dump(mode='json'))
                return

        state_store.update_task(task.task_id, task.model_dump(mode='json'))
        await task_queue.enqueue(task)

    async def _worker(self):
        hci = HumanControlInterface()
        while self.running:
            controls = hci.get_controls()
            if controls.get("emergency_stop"):
                logger.warning("ENGINE_PAUSED_EMERGENCY_STOP")
                await asyncio.sleep(5)
                continue

            if controls.get("is_paused"):
                await asyncio.sleep(2)
                continue

            task = await task_queue.dequeue()
            try:
                await self._process_task(task)
            except Exception as e:
                logger.error("TASK_PROCESSING_ERROR", {"task_id": task.task_id, "error": str(e)})
            finally:
                task_queue.task_done()

    async def _process_task(self, task: TaskPacket):
        hci = HumanControlInterface()

        # Check if agent is enabled
        toggles = hci.get_agent_toggles()
        if toggles.get(task.system_name) is False:
            logger.warning("AGENT_DISABLED_TASK_REJECTED", {"task_id": task.task_id, "agent": task.system_name})
            await self._handle_failure(task, f"Agent {task.system_name} is currently disabled")
            return

        # Human approval check for high-risk tasks
        if task.task_type in [TaskType.MODIFICATION, TaskType.DEPLOYMENT]:
            state = state_store.get_state()
            approvals = state.get("approvals", {})

            # Find if there is an approval for this task
            approval = next((ApprovalStatus(a["status"]) for a in approvals.values() if a["task_id"] == task.task_id), None)

            if approval != ApprovalStatus.APPROVED:
                if approval is None:
                    hci.request_approval(task, requester="OrchestrationEngine")
                    logger.info("APPROVAL_REQUESTED_FOR_TASK", {"task_id": task.task_id})
                elif approval == ApprovalStatus.REJECTED:
                    logger.warning("TASK_REJECTED_BY_HUMAN", {"task_id": task.task_id})
                    await self._handle_failure(task, "Task rejected by human approval")
                    return

                # Re-enqueue and wait
                logger.info("TASK_AWAITING_APPROVAL", {"task_id": task.task_id})
                task.status = TaskStatus.PENDING
                state_store.update_task(task.task_id, task.model_dump(mode='json'))
                await asyncio.sleep(5)
                await task_queue.enqueue(task)
                return

        task.status = TaskStatus.RUNNING
        state_store.update_task(task.task_id, task.model_dump(mode='json'))
        logger.info("PROCESSING_TASK", {"task_id": task.task_id, "agent": task.system_name})

        agent = agent_registry.get_agent(task.system_name)
        if not agent:
            task.status = TaskStatus.FAILED
            task.result = {"error": f"Agent {task.system_name} not found"}
            state_store.update_task(task.task_id, task.model_dump(mode='json'))
            logger.error("AGENT_NOT_FOUND", {"task_id": task.task_id, "agent": task.system_name})
            return

        success = await agent.send_task(task)
        if not success:
            await self._handle_failure(task, "Failed to send task to agent")
            return

        # Wait for result (polling or status update)
        timeout = 300 # 5 minutes timeout
        start_time = asyncio.get_event_loop().time()

        while True:
            # Re-fetch task state from store to see if it was updated by an external callback
            current_task_state = state_store.get_task(task.task_id)
            if current_task_state:
                if current_task_state["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task.status = TaskStatus(current_task_state["status"])
                    task.result = current_task_state.get("result")
                    break

            # Also check if agent has the result (polling)
            agent_result = await agent.receive_result(task.task_id)
            if agent_result:
                task.status = TaskStatus.COMPLETED
                task.result = agent_result
                state_store.update_task(task.task_id, task.model_dump(mode='json'))
                break

            if asyncio.get_event_loop().time() - start_time > timeout:
                await self._handle_failure(task, "Task timed out")
                return

            await asyncio.sleep(2)

        state_store.update_task(task.task_id, task.model_dump(mode='json'))
        logger.info("TASK_FINISHED", {"task_id": task.task_id, "status": task.status})

    async def _handle_failure(self, task: TaskPacket, error_message: str):
        task.retries += 1
        if task.retries < task.max_retries:
            logger.warning("TASK_RETRYING", {"task_id": task.task_id, "retry": task.retries, "error": error_message})
            task.status = TaskStatus.PENDING
            state_store.update_task(task.task_id, task.model_dump(mode='json'))
            await task_queue.enqueue(task)
        else:
            task.status = TaskStatus.FAILED
            task.result = {"error": error_message}
            state_store.update_task(task.task_id, task.model_dump(mode='json'))
            logger.error("TASK_MAX_RETRIES_REACHED", {"task_id": task.task_id, "error": error_message})

# Global engine instance
orchestration_engine = OrchestrationEngine()
