import os
import shutil
import unittest
from fog.core.backup import BackupManager
from fog.core.state import state_store

class TestBackupManager(unittest.TestCase):
    def setUp(self):
        self.backup_dir = "tests/test_backups"
        self.project_path = "tests/test_project"
        self.backup_mgr = BackupManager(self.backup_dir)

        os.makedirs(self.project_path, exist_ok=True)
        with open(os.path.join(self.project_path, "file1.txt"), "w") as f:
            f.write("content1")

    def tearDown(self):
        if os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)
        if os.path.exists(self.project_path):
            shutil.rmtree(self.project_path)

    def test_create_backup_and_rollback(self):
        backup_id = self.backup_mgr.create_backup(self.project_path, "test backup")
        self.assertIsNotNone(backup_id)

        # Modify project
        with open(os.path.join(self.project_path, "file1.txt"), "w") as f:
            f.write("modified content")

        # Rollback
        self.backup_mgr.rollback(backup_id)

        with open(os.path.join(self.project_path, "file1.txt"), "r") as f:
            content = f.read()
        self.assertEqual(content, "content1")

if __name__ == "__main__":
    unittest.main()
