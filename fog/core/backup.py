import os
import shutil
import zipfile
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from fog.core.logging import logger
from fog.core.state import state_store

class BackupManager:
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = backup_dir
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, project_path: str, description: str = "") -> str:
        if not os.path.exists(project_path):
            raise ValueError(f"Project path {project_path} does not exist")

        backup_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}_{backup_id}.zip"
        backup_path = os.path.join(self.backup_dir, backup_filename)

        logger.info("CREATING_BACKUP", {"project_path": project_path, "backup_id": backup_id})

        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, arcname)

        backup_metadata = {
            "backup_id": backup_id,
            "timestamp": datetime.now().isoformat(),
            "project_path": os.path.abspath(project_path),
            "backup_path": os.path.abspath(backup_path),
            "description": description
        }
        state_store.add_backup(backup_metadata)

        return backup_id

    def rollback(self, backup_id: str):
        backups = state_store.get_backups()
        backup_metadata = next((b for b in backups if b["backup_id"] == backup_id), None)

        if not backup_metadata:
            raise ValueError(f"Backup ID {backup_id} not found")

        project_path = backup_metadata["project_path"]
        backup_path = backup_metadata["backup_path"]

        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file {backup_path} not found")

        logger.info("ROLLING_BACKUP", {"backup_id": backup_id, "project_path": project_path})

        # Clear existing project path
        if os.path.exists(project_path):
            if os.path.isdir(project_path):
                shutil.rmtree(project_path)
            else:
                os.remove(project_path)

        os.makedirs(project_path, exist_ok=True)

        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(project_path)

        logger.info("ROLLBACK_COMPLETE", {"backup_id": backup_id})

# Global backup manager instance
backup_manager = BackupManager()
