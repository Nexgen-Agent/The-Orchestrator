from fastapi import APIRouter, HTTPException, BackgroundTasks
from fog.models.task import TaskPacket, AgentConfig, ProjectInput
from fog.core.connector import agent_registry, HttpAgentConnector, MockAgentConnector
from fog.core.engine import orchestration_engine
from fog.core.state import state_store
from fog.core.backup import backup_manager
from fog.core.mapper import DependencyMapper
from typing import Dict, Any, List

router = APIRouter()
mapper = DependencyMapper()

@router.post("/register-agent")
async def register_agent(config: AgentConfig):
    if config.handler_type == "mock":
        connector = MockAgentConnector(config.name, config.endpoint)
    else:
        connector = HttpAgentConnector(config.name, config.endpoint)

    agent_registry.register_agent(connector)
    state_store.add_agent(config.name, config.model_dump(mode='json'))
    return {"status": "success", "agent_name": config.name}

@router.post("/submit-project")
async def submit_project(project: ProjectInput):
    # This might initiate a full project scan or backup
    backup_id = backup_manager.create_backup(project.project_path, project.description or "Initial project submission")
    return {"status": "success", "backup_id": backup_id}

@router.post("/submit-task")
async def submit_task(task: TaskPacket):
    await orchestration_engine.submit_task(task)
    return {"status": "success", "task_id": task.task_id}

@router.post("/task-update/{task_id}")
async def update_task_status(task_id: str, update: Dict[str, Any]):
    task_data = state_store.get_task(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data.update(update)
    state_store.update_task(task_id, task_data)
    return {"status": "success"}

@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    task = state_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/rollback/{backup_id}")
async def rollback(backup_id: str):
    try:
        backup_manager.rollback(backup_id)
        return {"status": "success", "message": f"Rolled back to {backup_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/dependency-map")
async def get_dependency_map(project_path: str):
    try:
        graph = await asyncio.to_thread(mapper.scan_project, project_path)
        return graph
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/system-state")
async def get_system_state():
    return state_store.get_state()
