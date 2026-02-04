import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from agents.agent_collaboration.models import (
    CollaborationRequest, CollaborationType, TaskConflict, MultiAgentWorkflow
)
from fog.core.state import state_store
from fog.core.logging import logger
from fog.models.task import TaskPacket, TaskStatus

class CollaborationManager:
    def __init__(self):
        self._ensure_state_keys()

    def _ensure_state_keys(self):
        state = state_store.get_state()
        if "collaboration_requests" not in state:
            state["collaboration_requests"] = {}
        if "task_conflicts" not in state:
            state["task_conflicts"] = {}
        if "workflows" not in state:
            state["workflows"] = {}
        state_store._save()

    def request_help(self, task_id: str, requester: str, target: str, payload: Dict[str, Any]) -> CollaborationRequest:
        request = CollaborationRequest(
            requester_agent=requester,
            target_agent=target,
            task_id=task_id,
            collaboration_type=CollaborationType.HELP_REQUEST,
            payload=payload
        )
        state = state_store.get_state()
        state["collaboration_requests"][request.request_id] = request.model_dump(mode='json')
        state_store._save()
        logger.info("COLLABORATION_REQUESTED", {"request_id": request.request_id, "task_id": task_id})
        return request

    def detect_conflicts(self) -> List[TaskConflict]:
        state = state_store.get_state()
        tasks = state.get("tasks", {})

        # Simple resource detection: looking for overlapping project_path or file_path in payload
        resource_map = {} # resource -> list of task_ids

        pending_tasks = [t for t in tasks.values() if t.get("status") == TaskStatus.PENDING]

        for task in pending_tasks:
            payload = task.get("payload", {})
            resources = []
            if "project_path" in payload:
                resources.append(f"project:{payload['project_path']}")
            if "file_path" in payload:
                resources.append(f"file:{payload['file_path']}")

            for res in resources:
                if res not in resource_map:
                    resource_map[res] = []
                resource_map[res].append(task["task_id"])

        conflicts = []
        for res, tids in resource_map.items():
            if len(tids) > 1:
                conflict = TaskConflict(
                    task_ids=tids,
                    resource=res,
                    conflict_type="CONCURRENT_ACCESS"
                )
                conflicts.append(conflict)
                state["task_conflicts"][conflict.conflict_id] = conflict.model_dump(mode='json')

        if conflicts:
            state_store._save()
            logger.warning("TASK_CONFLICTS_DETECTED", {"count": len(conflicts)})

        return conflicts

    def create_workflow(self, name: str, task_packets: List[TaskPacket]) -> MultiAgentWorkflow:
        # Simple workflow: sequential based on dependencies
        # In a real system, we'd do topological sort
        task_ids = [t.task_id for t in task_packets]

        # For now, just group them by their dependency level
        # Level 0: no dependencies
        # Level 1: depends on Level 0
        # ...

        levels = []
        remaining_tasks = list(task_packets)
        processed_ids = set()

        while remaining_tasks:
            current_level = []
            next_remaining = []
            for task in remaining_tasks:
                deps = set(task.dependencies)
                if deps.issubset(processed_ids):
                    current_level.append(task.task_id)
                else:
                    next_remaining.append(task)

            if not current_level:
                # Circular dependency or missing dependency
                # Just add the rest as one level or fail
                current_level = [t.task_id for t in next_remaining]
                levels.append(current_level)
                break

            levels.append(current_level)
            processed_ids.update(current_level)
            remaining_tasks = next_remaining

        workflow = MultiAgentWorkflow(
            name=name,
            tasks=task_ids,
            sequence=levels
        )

        state = state_store.get_state()
        state["workflows"][workflow.workflow_id] = workflow.model_dump(mode='json')
        state_store._save()
        logger.info("WORKFLOW_CREATED", {"workflow_id": workflow.workflow_id, "name": name})
        return workflow

    def merge_outputs(self, task_ids: List[str]) -> Dict[str, Any]:
        state = state_store.get_state()
        tasks = state.get("tasks", {})

        merged_result = {}
        for tid in task_ids:
            task = tasks.get(tid)
            if task and task.get("status") == TaskStatus.COMPLETED:
                result = task.get("result", {})
                # Simple merge logic: deep merge or just key update
                merged_result.update(result)

        return merged_result
