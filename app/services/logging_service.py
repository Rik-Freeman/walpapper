"""
Logging service for Semantic Wallpaper application.
Configures application logging with file and console handlers.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class LoggingService:
    """Service for configuring and managing application logging."""

    def __init__(self, log_path: Optional[str] = None, level: int = logging.INFO):
        """
        Initialize logging service.
        
        Args:
            log_path: Path to log file. Defaults to ~/.semantic_wallpaper/logs/app.log
            level: Logging level (default: INFO)
        """
        if log_path:
            self.log_path = Path(log_path)
        else:
            log_dir = Path.home() / ".semantic_wallpaper" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d")
            self.log_path = log_dir / f"app_{timestamp}.log"

        self.logger = logging.getLogger("semantic_wallpaper")
        self.logger.setLevel(level)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File handler
        try:
            file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except IOError as e:
            print(f"Warning: Could not create log file handler: {e}")

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger

    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str, exc_info: bool = False):
        """Log an error message with optional exception info."""
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = False):
        """Log a critical message with optional exception info."""
        self.logger.critical(message, exc_info=exc_info)

    def get_last_error(self, lines: int = 50) -> str:
        """
        Get the last error messages from the log file.
        
        Args:
            lines: Number of lines to read from end of file
            
        Returns:
            String containing recent log entries
        """
        if not self.log_path.exists():
            return "No log file found."
        
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                error_lines = [l for l in all_lines if "ERROR" in l or "CRITICAL" in l]
                
                if error_lines:
                    return "".join(error_lines[-lines:])
                elif all_lines:
                    return "".join(all_lines[-lines:])
                else:
                    return "Log file is empty."
        except IOError as e:
            return f"Could not read log file: {e}"

    def clear_old_logs(self, days_to_keep: int = 7):
        """
        Remove log files older than specified days.
        
        Args:
            days_to_keep: Number of days to keep logs
        """
        log_dir = self.log_path.parent
        if not log_dir.exists():
            return
        
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for log_file in log_dir.glob("app_*.log"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    self.info(f"Removed old log file: {log_file}")
            except (IOError, OSError) as e:
                self.warning(f"Could not remove old log file {log_file}: {e}")
