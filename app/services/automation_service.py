"""
Automation service for Semantic Wallpaper application.
Manages Windows Task Scheduler integration for automatic wallpaper changes.
"""

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class AutomationService:
    """Service for managing automated wallpaper changes via Windows Task Scheduler."""

    def __init__(self, config_service=None):
        """
        Initialize automation service.
        
        Args:
            config_service: Optional ConfigService instance for configuration
        """
        self.config_service = config_service
        self.task_name_login = "SemanticWallpaper_Login"
        self.task_name_interval = "SemanticWallpaper_Interval"
        self.task_name_weekly = "SemanticWallpaper_Weekly"

    def get_task_scheduler_path(self) -> Optional[str]:
        """
        Get the path to schtasks.exe.
        
        Returns:
            Path to schtasks.exe or None if not found
        """
        if sys.platform != "win32":
            return None
        
        schtasks_path = Path(r"C:\Windows\System32\schtasks.exe")
        if schtasks_path.exists():
            return str(schtasks_path)
        return None

    def is_windows(self) -> bool:
        """Check if running on Windows."""
        return sys.platform == "win32"

    def install_login_task(self, script_path: str) -> Dict[str, Any]:
        """
        Install a task to change wallpaper on user login.
        
        Args:
            script_path: Path to the script to execute
            
        Returns:
            Dictionary with success status and message
        """
        if not self.is_windows():
            return {
                "success": False,
                "message": "Task Scheduler is only available on Windows"
            }

        schtasks = self.get_task_scheduler_path()
        if not schtasks:
            return {
                "success": False,
                "message": "Could not find schtasks.exe"
            }

        # Remove existing task first
        self.remove_task(self.task_name_login)

        # Build command
        cmd = [
            schtasks,
            "/Create",
            "/TN", self.task_name_login,
            "/TR", f'python "{script_path}"',
            "/SC", "ONLOGON",
            "/RL", "HIGHEST",
            "/F"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Login task installed successfully"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to install task: {result.stderr}"
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Command timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error installing task: {str(e)}"
            }

    def install_interval_task(
        self, 
        script_path: str, 
        interval_minutes: int = 30
    ) -> Dict[str, Any]:
        """
        Install a task to change wallpaper at regular intervals.
        
        Args:
            script_path: Path to the script to execute
            interval_minutes: Interval between wallpaper changes
            
        Returns:
            Dictionary with success status and message
        """
        if not self.is_windows():
            return {
                "success": False,
                "message": "Task Scheduler is only available on Windows"
            }

        schtasks = self.get_task_scheduler_path()
        if not schtasks:
            return {
                "success": False,
                "message": "Could not find schtasks.exe"
            }

        # Remove existing task first
        self.remove_task(self.task_name_interval)

        # Build command
        cmd = [
            schtasks,
            "/Create",
            "/TN", self.task_name_interval,
            "/TR", f'python "{script_path}"',
            "/SC", "MINUTE",
            "/MO", str(interval_minutes),
            "/RL", "HIGHEST",
            "/F"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Interval task installed (every {interval_minutes} minutes)"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to install task: {result.stderr}"
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Command timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error installing task: {str(e)}"
            }

    def install_weekly_task(
        self, 
        script_path: str,
        day_of_week: str = "MON",
        time_of_day: str = "09:00"
    ) -> Dict[str, Any]:
        """
        Install a task to update wallpapers weekly.
        
        Args:
            script_path: Path to the script to execute
            day_of_week: Day of week (MON, TUE, WED, THU, FRI, SAT, SUN)
            time_of_day: Time to run (HH:MM format)
            
        Returns:
            Dictionary with success status and message
        """
        if not self.is_windows():
            return {
                "success": False,
                "message": "Task Scheduler is only available on Windows"
            }

        schtasks = self.get_task_scheduler_path()
        if not schtasks:
            return {
                "success": False,
                "message": "Could not find schtasks.exe"
            }

        # Remove existing task first
        self.remove_task(self.task_name_weekly)

        # Build command
        cmd = [
            schtasks,
            "/Create",
            "/TN", self.task_name_weekly,
            "/TR", f'python "{script_path}"',
            "/SC", "WEEKLY",
            "/D", day_of_week,
            "/ST", time_of_day,
            "/RL", "HIGHEST",
            "/F"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Weekly task installed ({day_of_week} at {time_of_day})"
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to install task: {result.stderr}"
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Command timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error installing task: {str(e)}"
            }

    def remove_task(self, task_name: str) -> Dict[str, Any]:
        """
        Remove a scheduled task.
        
        Args:
            task_name: Name of the task to remove
            
        Returns:
            Dictionary with success status and message
        """
        if not self.is_windows():
            return {
                "success": False,
                "message": "Task Scheduler is only available on Windows"
            }

        schtasks = self.get_task_scheduler_path()
        if not schtasks:
            return {
                "success": False,
                "message": "Could not find schtasks.exe"
            }

        cmd = [
            schtasks,
            "/Delete",
            "/TN", task_name,
            "/F"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Task '{task_name}' removed successfully"
                }
            else:
                # Task might not exist, which is fine
                if "ERROR" in result.stderr and "not exist" in result.stderr.lower():
                    return {
                        "success": True,
                        "message": f"Task '{task_name}' did not exist"
                    }
                return {
                    "success": False,
                    "message": f"Failed to remove task: {result.stderr}"
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Command timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error removing task: {str(e)}"
            }

    def check_task_status(self, task_name: str) -> Dict[str, Any]:
        """
        Check if a scheduled task exists and its status.
        
        Args:
            task_name: Name of the task to check
            
        Returns:
            Dictionary with task status information
        """
        if not self.is_windows():
            return {
                "exists": False,
                "message": "Task Scheduler is only available on Windows"
            }

        schtasks = self.get_task_scheduler_path()
        if not schtasks:
            return {
                "exists": False,
                "message": "Could not find schtasks.exe"
            }

        cmd = [
            schtasks,
            "/Query",
            "/TN", task_name
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "exists": True,
                    "message": "Task exists",
                    "details": result.stdout
                }
            else:
                return {
                    "exists": False,
                    "message": "Task does not exist"
                }
        except subprocess.TimeoutExpired:
            return {
                "exists": False,
                "message": "Command timed out"
            }
        except Exception as e:
            return {
                "exists": False,
                "message": f"Error checking task: {str(e)}"
            }

    def get_all_tasks_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all Semantic Wallpaper tasks.
        
        Returns:
            Dictionary with status of each task
        """
        return {
            "login": self.check_task_status(self.task_name_login),
            "interval": self.check_task_status(self.task_name_interval),
            "weekly": self.check_task_status(self.task_name_weekly)
        }

    def run_manual_test(self, script_path: str) -> Dict[str, Any]:
        """
        Run a manual test of the wallpaper change script.
        
        Args:
            script_path: Path to the script to test
            
        Returns:
            Dictionary with test results
        """
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Manual test completed successfully",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "message": "Manual test failed",
                    "error": result.stderr
                }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "Test timed out after 60 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error running test: {str(e)}"
            }

    def enable_automation(self, script_path: str) -> Dict[str, Any]:
        """
        Enable full automation based on config settings.
        
        Args:
            script_path: Path to the wallpaper change script
            
        Returns:
            Dictionary with results of automation setup
        """
        if not self.config_service:
            return {
                "success": False,
                "message": "Config service not available"
            }

        results = []
        
        # Install login task
        login_result = self.install_login_task(script_path)
        results.append(("login", login_result))

        # Install interval task if enabled
        if self.config_service.get("auto_change_enabled", False):
            interval = self.config_service.get("auto_change_interval_minutes", 30)
            interval_result = self.install_interval_task(script_path, interval)
            results.append(("interval", interval_result))

        # Determine overall success
        all_success = all(r[1].get("success", False) for r in results)
        
        return {
            "success": all_success,
            "message": "Automation setup completed",
            "details": dict(results)
        }

    def disable_automation(self) -> Dict[str, Any]:
        """
        Disable all automation tasks.
        
        Returns:
            Dictionary with results of task removal
        """
        results = []
        
        # Remove all tasks
        for task_name in [self.task_name_login, self.task_name_interval, self.task_name_weekly]:
            result = self.remove_task(task_name)
            results.append((task_name, result))

        all_success = all(r[1].get("success", False) for r in results)
        
        return {
            "success": all_success,
            "message": "All automation tasks removed",
            "details": dict(results)
        }
