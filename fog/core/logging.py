import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict

class StructuredLogger:
    def __init__(self, name: str, log_file: str = "storage/audit.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(console_handler)

        # File handler for audit trail
        file_handler = logging.FileHandler(log_file)
        self.logger.addHandler(file_handler)

    def _log(self, level: str, event: str, data: Dict[str, Any] = None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "event": event,
            "data": data or {}
        }
        message = json.dumps(log_entry)
        if level == "INFO":
            self.logger.info(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)

    def info(self, event: str, data: Dict[str, Any] = None):
        self._log("INFO", event, data)

    def error(self, event: str, data: Dict[str, Any] = None):
        self._log("ERROR", event, data)

    def warning(self, event: str, data: Dict[str, Any] = None):
        self._log("WARNING", event, data)

# Global logger instance
logger = StructuredLogger("FOG")
