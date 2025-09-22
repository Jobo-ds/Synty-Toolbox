import bpy
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ProcessingResult:
    """Represents the result of a processing operation"""
    def __init__(self, success: bool, message: str = "", data: Dict[str, Any] = None):
        self.success = success
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now()

class BatchProcessor:
    """Handles batch processing with error recovery"""
    def __init__(self, continue_on_error: bool = True):
        self.continue_on_error = continue_on_error
        self.results: List[ProcessingResult] = []
        self.failed_files: List[str] = []
        self.processed_files: List[str] = []

    def add_result(self, result: ProcessingResult, file_path: str = ""):
        self.results.append(result)
        if result.success:
            self.processed_files.append(file_path)
        else:
            self.failed_files.append(file_path)

    def get_summary(self) -> Dict[str, Any]:
        return {
            'total_processed': len(self.results),
            'successful': len(self.processed_files),
            'failed': len(self.failed_files),
            'success_rate': len(self.processed_files) / len(self.results) if self.results else 0,
            'failed_files': self.failed_files
        }

class Logger:
    """Enhanced logging system for Synty Toolbox"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logs = []
            cls._instance.start_time = time.time()
        return cls._instance

    def log(self, level: LogLevel, message: str, context: str = "", data: Dict[str, Any] = None):
        """Log a message with timestamp and context"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'level': level.value,
            'message': message,
            'context': context,
            'data': data or {}
        }
        self.logs.append(log_entry)

        # Print to console with formatting
        prefix = f"[{timestamp}] [{level.value}]"
        if context:
            prefix += f" [{context}]"
        print(f"{prefix} {message}")

        # Note: bpy.ops.wm.report can't be called from within operator execution
        # Blender UI reporting is handled by the operators themselves

    def info(self, message: str, context: str = "", data: Dict[str, Any] = None):
        self.log(LogLevel.INFO, message, context, data)

    def warning(self, message: str, context: str = "", data: Dict[str, Any] = None):
        self.log(LogLevel.WARNING, message, context, data)

    def error(self, message: str, context: str = "", data: Dict[str, Any] = None):
        self.log(LogLevel.ERROR, message, context, data)

    def debug(self, message: str, context: str = "", data: Dict[str, Any] = None):
        self.log(LogLevel.DEBUG, message, context, data)

    def get_logs(self, level: Optional[LogLevel] = None) -> List[Dict[str, Any]]:
        """Get logs, optionally filtered by level"""
        if level:
            return [log for log in self.logs if log['level'] == level.value]
        return self.logs.copy()

    def clear_logs(self):
        """Clear all logs"""
        self.logs.clear()
        self.start_time = time.time()

    def get_session_duration(self) -> float:
        """Get duration of current session in seconds"""
        return time.time() - self.start_time

# Singleton instance
logger = Logger()