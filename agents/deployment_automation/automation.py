import asyncio
import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from agents.deployment_automation.models import (
    DeploymentReport, DeploymentStatus, DeploymentAction, DeploymentManifest
)
from fog.core.state import state_store
from fog.core.logging import logger

class DeploymentAutomation:
    def __init__(self, project_path: str):
        self.project_path = os.path.abspath(project_path)
        self._ensure_state_keys()

    def _ensure_state_keys(self):
        state = state_store.get_state()
        if "deployments" not in state:
            state["deployments"] = {}
        state_store._save()

    async def run_deployment(self, manifest: DeploymentManifest) -> DeploymentReport:
        report = DeploymentReport(
            project_path=self.project_path,
            status=DeploymentStatus.BUILDING,
            manifest=manifest
        )
        self._save_report(report)

        try:
            # 1. Build Image
            build_action = await self._run_action("build", f"docker build -t {manifest.service_name}:{manifest.image_tag} {self.project_path}")
            report.actions.append(build_action)
            if build_action.status == "Failed":
                report.status = DeploymentStatus.FAILED
                report.error_message = "Build failed"
                self._save_report(report)
                return report

            # 2. Push Image (Mock)
            report.status = DeploymentStatus.PUSHING
            push_action = await self._run_action("push", f"docker push {manifest.service_name}:{manifest.image_tag}")
            report.actions.append(push_action)
            if push_action.status == "Failed":
                report.status = DeploymentStatus.FAILED
                report.error_message = "Push failed"
                self._save_report(report)
                return report

            # 3. Deploy Service (Mock)
            report.status = DeploymentStatus.DEPLOYING
            deploy_action = await self._run_action("deploy", f"kubectl apply -f manifest.yaml") # Simulating
            report.actions.append(deploy_action)
            if deploy_action.status == "Failed":
                report.status = DeploymentStatus.FAILED
                report.error_message = "Deployment failed"
                self._save_report(report)
                return report

            report.status = DeploymentStatus.SUCCESS
            logger.info("DEPLOYMENT_SUCCESSFUL", {"deployment_id": report.deployment_id, "service": manifest.service_name})

        except Exception as e:
            report.status = DeploymentStatus.FAILED
            report.error_message = str(e)
            logger.error("DEPLOYMENT_FATAL_ERROR", {"deployment_id": report.deployment_id, "error": str(e)})

        self._save_report(report)
        return report

    async def rollback(self, deployment_id: str) -> DeploymentReport:
        state = state_store.get_state()
        report_data = state.get("deployments", {}).get(deployment_id)
        if not report_data:
            raise ValueError(f"Deployment {deployment_id} not found")

        report = DeploymentReport(**report_data)
        logger.info("ROLLBACK_STARTED", {"deployment_id": deployment_id})

        rollback_action = await self._run_action("rollback", f"kubectl rollout undo deployment/{report.manifest.service_name}")
        report.actions.append(rollback_action)

        if rollback_action.status == "Completed":
            report.status = DeploymentStatus.ROLLED_BACK
        else:
            report.status = DeploymentStatus.FAILED # Rollback failed

        self._save_report(report)
        return report

    async def _run_action(self, action_type: str, command: str) -> DeploymentAction:
        action = DeploymentAction(action_type=action_type, status="InProgress")
        action.logs.append(f"Running command: {command}")

        # Simulate execution for sandbox environment compatibility
        await asyncio.sleep(1)

        # In a real environment, we'd use:
        # process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        # stdout, stderr = await process.communicate()

        # Simulating success
        action.status = "Completed"
        action.logs.append("Action completed successfully (simulated).")

        return action

    def _save_report(self, report: DeploymentReport):
        state = state_store.get_state()
        state["deployments"][report.deployment_id] = report.model_dump(mode='json')
        state_store._save()

    def generate_manifest(self, service_name: str, image_tag: str) -> DeploymentManifest:
        # Heuristic to generate a default manifest
        return DeploymentManifest(
            service_name=service_name,
            image_tag=image_tag,
            env_vars={"ENV": "production", "LOG_LEVEL": "info"}
        )
