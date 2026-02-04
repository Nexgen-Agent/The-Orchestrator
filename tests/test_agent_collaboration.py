import unittest
import os
import json
from agents.agent_collaboration.collaboration import CollaborationManager
from agents.agent_collaboration.models import CollaborationType
from fog.core.state import state_store
from fog.models.task import TaskPacket, TaskType, TaskStatus

class TestAgentCollaboration(unittest.TestCase):
    def setUp(self):
        # Reset state
        if os.path.exists("storage/state_collab_test.json"):
            os.remove("storage/state_collab_test.json")
        state_store.storage_path = "storage/state_collab_test.json"
        state_store._state = {
            "tasks": {},
            "agents": {},
            "backups": [],
            "runs": [],
            "collaboration_requests": {},
            "task_conflicts": {},
            "workflows": {}
        }
        state_store._save()
        self.manager = CollaborationManager()

    def tearDown(self):
        if os.path.exists("storage/state_collab_test.json"):
            os.remove("storage/state_collab_test.json")

    def test_request_help(self):
        request = self.manager.request_help("task1", "agentA", "agentB", {"need": "data"})
        self.assertEqual(request.requester_agent, "agentA")
        self.assertEqual(request.target_agent, "agentB")
        self.assertEqual(request.collaboration_type, CollaborationType.HELP_REQUEST)

        state = state_store.get_state()
        self.assertIn(request.request_id, state["collaboration_requests"])

    def test_detect_conflicts(self):
        # Add two tasks modifying the same file
        state_store._state["tasks"] = {
            "t1": {
                "task_id": "t1",
                "system_name": "agent1",
                "status": "pending",
                "payload": {"file_path": "code.py"}
            },
            "t2": {
                "task_id": "t2",
                "system_name": "agent2",
                "status": "pending",
                "payload": {"file_path": "code.py"}
            }
        }
        state_store._save()

        conflicts = self.manager.detect_conflicts()
        self.assertEqual(len(conflicts), 1)
        self.assertIn("t1", conflicts[0].task_ids)
        self.assertIn("t2", conflicts[0].task_ids)

    def test_create_workflow(self):
        t1 = TaskPacket(task_id="t1", system_name="a", module_name="m", task_type=TaskType.ANALYSIS)
        t2 = TaskPacket(task_id="t2", system_name="b", module_name="m", task_type=TaskType.ANALYSIS, dependencies=["t1"])
        t3 = TaskPacket(task_id="t3", system_name="c", module_name="m", task_type=TaskType.ANALYSIS, dependencies=["t1"])
        t4 = TaskPacket(task_id="t4", system_name="d", module_name="m", task_type=TaskType.ANALYSIS, dependencies=["t2", "t3"])

        workflow = self.manager.create_workflow("MyWorkflow", [t1, t2, t3, t4])

        self.assertEqual(len(workflow.sequence), 3)
        self.assertEqual(workflow.sequence[0], ["t1"])
        self.assertCountEqual(workflow.sequence[1], ["t2", "t3"])
        self.assertEqual(workflow.sequence[2], ["t4"])

    def test_merge_outputs(self):
        state_store._state["tasks"] = {
            "t1": {
                "task_id": "t1",
                "status": "completed",
                "result": {"analysis": "good"}
            },
            "t2": {
                "task_id": "t2",
                "status": "completed",
                "result": {"quality": 90}
            }
        }
        state_store._save()

        merged = self.manager.merge_outputs(["t1", "t2"])
        self.assertEqual(merged["analysis"], "good")
        self.assertEqual(merged["quality"], 90)

if __name__ == "__main__":
    unittest.main()
