#!/usr/bin/env python3
# SecureScout - Tool Integration Base Adapter Module

import os
import json
import logging
import subprocess
import tempfile
import abc
import uuid
import shutil
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, field

# Configure logging
logger = logging.getLogger("securescout.integrations")

@dataclass
class ToolResult:
    """
    Base class for storing tool execution results in a standardized format.
    """
    tool_name: str
    command: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed
    result_data: Dict[str, Any] = field(default_factory=dict)
    raw_output: str = ""
    parsed_findings: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    result_files: List[str] = field(default_factory=list)
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a serializable dictionary."""
        return {
            "tool_name": self.tool_name,
            "command": self.command,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "result_data": self.result_data,
            "raw_output_length": len(self.raw_output) if self.raw_output else 0,
            "parsed_findings_count": len(self.parsed_findings),
            "error_message": self.error_message,
            "result_files": self.result_files,
            "execution_id": self.execution_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolResult':
        """Create a ToolResult instance from a dictionary."""
        # Convert ISO format strings back to datetime objects
        start_time = datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None
        end_time = datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None
        
        # Create a new instance with the data
        return cls(
            tool_name=data["tool_name"],
            command=data["command"],
            start_time=start_time,
            end_time=end_time,
            status=data["status"],
            result_data=data.get("result_data", {}),
            raw_output=data.get("raw_output", ""),
            parsed_findings=data.get("parsed_findings", []),
            error_message=data.get("error_message"),
            result_files=data.get("result_files", []),
            execution_id=data.get("execution_id", str(uuid.uuid4()))
        )
    
    def mark_completed(self, status: str = "completed") -> None:
        """Mark the tool execution as completed."""
        self.end_time = datetime.now()
        self.status = status
    
    def add_finding(self, finding: Dict[str, Any]) -> None:
        """Add a parsed finding to the results."""
        self.parsed_findings.append(finding)
    
    def add_result_file(self, file_path: str) -> None:
        """Add a result file to the results."""
        if os.path.exists(file_path):
            self.result_files.append(file_path)
    
    def set_error(self, error_message: str) -> None:
        """Set an error message and mark the tool execution as failed."""
        self.error_message = error_message
        self.mark_completed(status="failed")


class BaseToolAdapter(abc.ABC):
    """
    Abstract base class for tool adapters.
    
    This class defines the interface for all tool adapters and provides
    common functionality for executing and managing security tools.
    """
    
    def __init__(self, tool_name: str, executable_path: Optional[str] = None):
        """
        Initialize the tool adapter.
        
        Args:
            tool_name: The name of the tool
            executable_path: Path to the tool executable (if applicable)
        """
        self.tool_name = tool_name
        self.executable_path = executable_path or self._find_executable()
        self.temp_dir = None
        self.result = None
    
    def _find_executable(self) -> Optional[str]:
        """
        Find the tool executable in the system PATH.
        
        Returns:
            Path to the executable or None if not found
        """
        try:
            # Try to find the executable in the system PATH
            result = subprocess.run(
                ["which", self.tool_name], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            
            # Try common installation locations
            common_locations = [
                f"/usr/bin/{self.tool_name}",
                f"/usr/local/bin/{self.tool_name}",
                f"/opt/{self.tool_name}/bin/{self.tool_name}",
                f"/snap/bin/{self.tool_name}"
            ]
            
            for location in common_locations:
                if os.path.exists(location) and os.access(location, os.X_OK):
                    return location
            
            return None
        except Exception as e:
            logger.error(f"Error finding executable for {self.tool_name}: {e}")
            return None
    
    @abc.abstractmethod
    def prepare_command(self, options: Dict[str, Any]) -> str:
        """
        Prepare the command to execute the tool with the given options.
        
        Args:
            options: Tool-specific options
            
        Returns:
            Command string to execute
        """
        pass
    
    @abc.abstractmethod
    def parse_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse the tool output and extract findings.
        
        Args:
            output: Raw tool output
            
        Returns:
            List of parsed findings
        """
        pass
    
    def create_temp_directory(self) -> str:
        """
        Create a temporary directory for tool execution.
        
        Returns:
            Path to the temporary directory
        """
        self.temp_dir = tempfile.mkdtemp(prefix=f"securescout_{self.tool_name}_")
        return self.temp_dir
    
    def cleanup_temp_directory(self) -> None:
        """Clean up the temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
    
    def execute(self, options: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with the given options.
        
        Args:
            options: Tool-specific options
            
        Returns:
            ToolResult object with execution results
        """
        # Ensure the tool is available
        if not self.executable_path:
            raise FileNotFoundError(f"Tool executable not found: {self.tool_name}")
        
        # Create a temporary directory if needed
        if not self.temp_dir:
            self.create_temp_directory()
        
        # Prepare the command
        command = self.prepare_command(options)
        
        # Initialize the result object
        self.result = ToolResult(
            tool_name=self.tool_name,
            command=command,
            start_time=datetime.now()
        )
        
        try:
            # Execute the command
            logger.info(f"Executing {self.tool_name}: {command}")
            
            self.result.status = "running"
            
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.temp_dir
            )
            
            # Capture output
            stdout, stderr = process.communicate()
            
            # Set raw output
            self.result.raw_output = stdout
            
            # Check exit code
            if process.returncode != 0:
                self.result.set_error(f"Tool execution failed with exit code {process.returncode}: {stderr}")
                return self.result
            
            # Parse the output
            self.result.parsed_findings = self.parse_output(stdout)
            
            # Mark as completed
            self.result.mark_completed()
            
            logger.info(f"Completed {self.tool_name} execution: found {len(self.result.parsed_findings)} issues")
            
            return self.result
            
        except Exception as e:
            logger.error(f"Error executing {self.tool_name}: {str(e)}")
            self.result.set_error(f"Error executing tool: {str(e)}")
            return self.result
        finally:
            # Always return a result, even if an exception occurred
            if not self.result.end_time:
                self.result.mark_completed(status="failed")
    
    def save_results_to_file(self, file_path: str) -> None:
        """
        Save the tool execution results to a file.
        
        Args:
            file_path: Path to save the results to
        """
        if not self.result:
            raise ValueError("No results to save")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(self.result.to_dict(), f, indent=2)
            
            logger.info(f"Saved {self.tool_name} results to {file_path}")
        except Exception as e:
            logger.error(f"Error saving results to file: {str(e)}")
    
    def __del__(self):
        """Clean up resources when the adapter is garbage collected."""
        self.cleanup_temp_directory()


# Base finding severity classification
class Severity:
    """Constants for severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
    UNKNOWN = "unknown"
    
    @staticmethod
    def normalize(severity: str) -> str:
        """
        Normalize severity strings from different tools to a standard format.
        
        Args:
            severity: The severity string to normalize
            
        Returns:
            Normalized severity string
        """
        severity = severity.lower().strip()
        
        # Critical severity mapping
        if severity in ("critical", "crit", "p0", "0", "s0", "severity:critical"):
            return Severity.CRITICAL
        
        # High severity mapping
        if severity in ("high", "important", "p1", "1", "s1", "severity:high"):
            return Severity.HIGH
        
        # Medium severity mapping
        if severity in ("medium", "moderate", "warning", "p2", "2", "s2", "severity:medium"):
            return Severity.MEDIUM
        
        # Low severity mapping
        if severity in ("low", "minor", "p3", "3", "s3", "severity:low"):
            return Severity.LOW
        
        # Info severity mapping
        if severity in ("info", "informational", "information", "p4", "4", "s4", "severity:info"):
            return Severity.INFO
        
        # If no match, return unknown
        return Severity.UNKNOWN


# Tool execution status tracking
class ExecutionStatus:
    """Constants for execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # This example won't run since BaseToolAdapter is abstract
    # It's here to illustrate the intended usage
    
    # Example adapter implementation
    class ExampleAdapter(BaseToolAdapter):
        def prepare_command(self, options: Dict[str, Any]) -> str:
            target = options.get("target", "localhost")
            return f"{self.executable_path} -v {target}"
        
        def parse_output(self, output: str) -> List[Dict[str, Any]]:
            # Simple example parsing
            findings = []
            for line in output.strip().split("\n"):
                if "vulnerability" in line.lower():
                    findings.append({
                        "title": line,
                        "severity": Severity.normalize("high"),
                        "description": "Example vulnerability",
                        "raw": line
                    })
            return findings
    
    # Initialize the adapter
    # adapter = ExampleAdapter("example-tool")
    
    # Execute the tool
    # result = adapter.execute({"target": "example.com"})
    
    # Print results
    # print(json.dumps(result.to_dict(), indent=2))