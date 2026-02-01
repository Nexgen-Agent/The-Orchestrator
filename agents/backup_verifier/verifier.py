import hashlib
import zipfile
import os
from typing import Dict, List, Optional
from agents.backup_verifier.models import VerificationReport

class BackupVerifier:
    def __init__(self):
        pass

    def calculate_sha256(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def verify_archive(self, archive_path: str, backup_id: str = "unknown") -> VerificationReport:
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"Archive not found: {archive_path}")

        is_corrupt = False
        corruption_details = None

        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                corruption = zipf.testzip()
                if corruption:
                    is_corrupt = True
                    corruption_details = f"CRC check failed for file: {corruption}"
        except Exception as e:
            is_corrupt = True
            corruption_details = str(e)

        if is_corrupt:
            return VerificationReport(
                backup_id=backup_id,
                archive_path=archive_path,
                is_archive_corrupt=True,
                corruption_details=corruption_details,
                files_verified=0,
                status="Corrupt"
            )

        # If not corrupt, we can't really "verify" against original project
        # unless we have the project path or stored hashes.
        # This basic method just checks zip integrity.

        with zipfile.ZipFile(archive_path, 'r') as zipf:
            count = len(zipf.namelist())

        return VerificationReport(
            backup_id=backup_id,
            archive_path=archive_path,
            is_archive_corrupt=False,
            files_verified=count,
            status="Verified"
        )

    def compare_with_project(self, archive_path: str, project_path: str, backup_id: str) -> VerificationReport:
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"Archive not found: {archive_path}")
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"Project path not found: {project_path}")

        mismatched = []
        missing_in_project = []
        verified_count = 0

        with zipfile.ZipFile(archive_path, 'r') as zipf:
            for member in zipf.namelist():
                if member.endswith('/'): # Skip directories
                    continue

                # Check if file exists in project
                project_file_path = os.path.join(project_path, member)
                if not os.path.exists(project_file_path):
                    missing_in_project.append(member)
                    continue

                # Compare hashes
                with zipf.open(member) as f:
                    archive_hash = hashlib.sha256(f.read()).hexdigest()

                project_hash = self.calculate_sha256(project_file_path)

                if archive_hash != project_hash:
                    mismatched.append(member)
                else:
                    verified_count += 1

        status = "Verified"
        if mismatched or missing_in_project:
            status = "Mismatched"

        return VerificationReport(
            backup_id=backup_id,
            archive_path=archive_path,
            is_archive_corrupt=False,
            files_verified=verified_count,
            mismatched_files=mismatched,
            missing_files=missing_in_project,
            status=status
        )
