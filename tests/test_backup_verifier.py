import unittest
import os
import shutil
import zipfile
from agents.backup_verifier.verifier import BackupVerifier

class TestBackupVerifier(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/test_verifier_tmp"
        os.makedirs(self.test_dir, exist_ok=True)
        self.project_path = os.path.join(self.test_dir, "project")
        os.makedirs(self.project_path, exist_ok=True)

        self.file1 = os.path.join(self.project_path, "file1.txt")
        with open(self.file1, "w") as f:
            f.write("content1")

        self.archive_path = os.path.join(self.test_dir, "backup.zip")
        with zipfile.ZipFile(self.archive_path, 'w') as zipf:
            zipf.write(self.file1, "file1.txt")

        self.verifier = BackupVerifier()

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_calculate_sha256(self):
        h = self.verifier.calculate_sha256(self.file1)
        self.assertEqual(len(h), 64)

    def test_verify_archive(self):
        report = self.verifier.verify_archive(self.archive_path)
        self.assertFalse(report.is_archive_corrupt)
        self.assertEqual(report.files_verified, 1)
        self.assertEqual(report.status, "Verified")

    def test_compare_with_project_success(self):
        report = self.verifier.compare_with_project(self.archive_path, self.project_path, "test-id")
        self.assertEqual(report.status, "Verified")
        self.assertEqual(report.files_verified, 1)
        self.assertEqual(len(report.mismatched_files), 0)

    def test_compare_with_project_mismatch(self):
        # Modify project file
        with open(self.file1, "w") as f:
            f.write("modified content")

        report = self.verifier.compare_with_project(self.archive_path, self.project_path, "test-id")
        self.assertEqual(report.status, "Mismatched")
        self.assertIn("file1.txt", report.mismatched_files)

    def test_compare_with_project_missing(self):
        # Remove project file
        os.remove(self.file1)

        report = self.verifier.compare_with_project(self.archive_path, self.project_path, "test-id")
        self.assertEqual(report.status, "Mismatched")
        self.assertIn("file1.txt", report.missing_files)

if __name__ == "__main__":
    unittest.main()
