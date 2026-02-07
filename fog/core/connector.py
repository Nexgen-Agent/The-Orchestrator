from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from fog.models.task import TaskPacket, TaskStatus
import asyncio
from fog.core.logging import logger

class AgentConnector(ABC):
    def __init__(self, name: str, endpoint: str):
        self.name = name
        self.endpoint = endpoint

    @abstractmethod
    async def send_task(self, task: TaskPacket) -> bool:
        """Send a task to the agent."""
        pass

    @abstractmethod
    async def receive_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Receive the result of a task from the agent."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the agent is healthy."""
        pass

class HttpAgentConnector(AgentConnector):
    async def send_task(self, task: TaskPacket) -> bool:
        # In a real implementation, this would make an HTTP POST request
        logger.info("SENDING_TASK_HTTP", {"agent": self.name, "task_id": task.task_id, "endpoint": self.endpoint})
        # Simulate success
        return True

    async def receive_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        # In a real implementation, this would poll or receive a webhook
        return None

    async def health_check(self) -> bool:
        return True

class LocalAgentConnector(AgentConnector):
    async def send_task(self, task: TaskPacket) -> bool:
        logger.info("SENDING_TASK_LOCAL", {"agent": self.name, "task_id": task.task_id})
        asyncio.create_task(self._run_local_handler(task))
        return True

    async def _run_local_handler(self, task: TaskPacket):
        from fog.core.state import state_store
        import importlib
        import os

        # Derive directory name from PascalCase name (e.g., FrictionSolver -> friction_solver)
        agent_dir = ""
        for i, char in enumerate(self.name):
            if char.isupper() and i > 0:
                agent_dir += "_"
            agent_dir += char.lower()

        # Fallback to direct name if directory doesn't exist
        if not os.path.exists(os.path.join("agents", agent_dir)):
            agent_dir = self.name.lower()

        try:
            module = importlib.import_module(f"agents.{agent_dir}.handler")
            result = await module.handle_task(task.model_dump(mode='json'))

            if result.get("status") == "success":
                task.status = TaskStatus.COMPLETED
                task.result = result.get("result") or result
            else:
                task.status = TaskStatus.FAILED
                task.result = {"error": result.get("message", "Unknown error")}

        except Exception as e:
            logger.error("LOCAL_HANDLER_ERROR", {"agent": self.name, "error": str(e)})
            task.status = TaskStatus.FAILED
            task.result = {"error": str(e)}

        state_store.update_task(task.task_id, task.model_dump(mode='json'))

    async def receive_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        return None

    async def health_check(self) -> bool:
        return True

class MockAgentConnector(AgentConnector):
    async def send_task(self, task: TaskPacket) -> bool:
        logger.info("SENDING_TASK_MOCK", {"agent": self.name, "task_id": task.task_id})
        # Simulate background processing
        asyncio.create_task(self._simulate_processing(task))
        return True

    async def _simulate_processing(self, task: TaskPacket):
        await asyncio.sleep(2)
        task.status = TaskStatus.COMPLETED
        task.result = {"message": f"Task {task.task_id} completed by mock agent {self.name}"}
        from fog.core.state import state_store
        state_store.update_task(task.task_id, task.model_dump(mode='json'))
        logger.info("TASK_COMPLETED_MOCK", {"agent": self.name, "task_id": task.task_id})

    async def receive_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        return None

    async def health_check(self) -> bool:
        return True

class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, AgentConnector] = {}

    def register_agent(self, agent: AgentConnector):
        self.agents[agent.name] = agent
        logger.info("AGENT_REGISTERED", {"name": agent.name, "endpoint": agent.endpoint})

    def get_agent(self, name: str) -> Optional[AgentConnector]:
        return self.agents.get(name)

# Global registry instance
agent_registry = AgentRegistry()
