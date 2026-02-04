import asyncio
from typing import Dict, Any
from agents.deployment_automation.automation import DeploymentAutomation
from agents.deployment_automation.models import DeploymentManifest
from fog.models.task import TaskPacket

async def handle_task(task_packet_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for Deployment Automation Agent.
    """
    payload = task_packet_dict.get("payload", {})
    project_path = payload.get("project_path")

    if not project_path:
        return {"status": "error", "message": "Missing project_path in payload"}

    automation = DeploymentAutomation(project_path)
    action = payload.get("action", "deploy")

    try:
        if action == "deploy":
            manifest_data = payload.get("manifest")
            if manifest_data:
                manifest = DeploymentManifest(**manifest_data)
            else:
                service_name = payload.get("service_name", "unknown-service")
                image_tag = payload.get("image_tag", "latest")
                manifest = automation.generate_manifest(service_name, image_tag)

            report = await automation.run_deployment(manifest)
            return {
                "status": "success",
                "result": report.model_dump(mode='json')
            }

        elif action == "rollback":
            deployment_id = payload.get("deployment_id")
            if not deployment_id:
                return {"status": "error", "message": "Missing deployment_id for rollback"}
            report = await automation.rollback(deployment_id)
            return {
                "status": "success",
                "result": report.model_dump(mode='json')
            }

        elif action == "generate_manifest":
            service_name = payload.get("service_name", "unknown-service")
            image_tag = payload.get("image_tag", "latest")
            manifest = automation.generate_manifest(service_name, image_tag)
            return {
                "status": "success",
                "result": manifest.model_dump(mode='json')
            }
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
