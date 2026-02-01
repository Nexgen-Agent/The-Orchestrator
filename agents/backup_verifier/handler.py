import asyncio
from typing import Dict, Any
from agents.backup_verifier.verifier import BackupVerifier

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'archive_path', 'backup_id', and optionally 'project_path' in payload.
    """
    payload = task_packet.get("payload", {})
    archive_path = payload.get("archive_path")
    backup_id = payload.get("backup_id", "unknown")
    project_path = payload.get("project_path")

    if not archive_path:
        return {"status": "error", "message": "Missing archive_path in payload"}

    verifier = BackupVerifier()

    try:
        if project_path:
            # Full verification against project
            report = await asyncio.to_thread(verifier.compare_with_project, archive_path, project_path, backup_id)
        else:
            # Just integrity check
            report = await asyncio.to_thread(verifier.verify_archive, archive_path, backup_id)

        return {
            "status": "success",
            "result": report.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
