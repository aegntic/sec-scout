#!/usr/bin/env python3
# SecureScout - Workflow Orchestration Module

import os
import json
import logging
import tempfile
import time
import uuid
import threading
import queue
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from datetime import datetime
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, Future

# Import adapters
from .adapter_base import BaseToolAdapter, ToolResult, Severity
from .zap_adapter import ZAPAdapter
from .nmap_adapter import NmapAdapter
from .trivy_adapter import TrivyAdapter
from .sqlmap_adapter import SQLMapAdapter
from .nuclei_adapter import NucleiAdapter
from .nikto_adapter import NiktoAdapter

# Configure logging
logger = logging.getLogger("securescout.integrations.orchestrator")

@dataclass
class WorkflowTask:
    """
    Representation of a task in a workflow.
    """
    adapter_name: str
    adapter_options: Dict[str, Any]
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_name: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed, cancelled
    depends_on: List[str] = field(default_factory=list)
    result: Optional[ToolResult] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a serializable dictionary."""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name or f"{self.adapter_name} Task",
            "adapter_name": self.adapter_name,
            "status": self.status,
            "depends_on": self.depends_on,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "error_message": self.error_message,
            "result_summary": self.result.to_dict() if self.result else None
        }


@dataclass
class Workflow:
    """
    Representation of a security testing workflow.
    """
    name: str
    description: str
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tasks: List[WorkflowTask] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed, cancelled
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    target: Optional[str] = None
    created_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow to a serializable dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "target": self.target,
            "created_by": self.created_by,
            "tags": self.tags,
            "tasks": [task.to_dict() for task in self.tasks],
            "task_count": len(self.tasks),
            "completed_tasks": sum(1 for task in self.tasks if task.status == "completed"),
            "failed_tasks": sum(1 for task in self.tasks if task.status == "failed")
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        """Create a Workflow instance from a dictionary."""
        workflow = cls(
            name=data["name"],
            description=data["description"],
            workflow_id=data.get("workflow_id", str(uuid.uuid4())),
            status=data.get("status", "pending"),
            target=data.get("target"),
            created_by=data.get("created_by"),
            tags=data.get("tags", [])
        )
        
        # Convert time strings to datetime objects
        if data.get("start_time"):
            workflow.start_time = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            workflow.end_time = datetime.fromisoformat(data["end_time"])
        
        # Add tasks
        for task_data in data.get("tasks", []):
            task = WorkflowTask(
                adapter_name=task_data["adapter_name"],
                adapter_options=task_data.get("adapter_options", {}),
                task_id=task_data.get("task_id", str(uuid.uuid4())),
                task_name=task_data.get("task_name"),
                status=task_data.get("status", "pending"),
                depends_on=task_data.get("depends_on", [])
            )
            
            # Convert time strings to datetime objects
            if task_data.get("start_time"):
                task.start_time = datetime.fromisoformat(task_data["start_time"])
            if task_data.get("end_time"):
                task.end_time = datetime.fromisoformat(task_data["end_time"])
            
            workflow.tasks.append(task)
        
        return workflow


class WorkflowOrchestrator:
    """
    Orchestrator for security testing workflows.
    
    This class provides functionality to create, manage, and execute
    security testing workflows using multiple security tools.
    """
    
    def __init__(self):
        """Initialize the workflow orchestrator."""
        self.workflows: Dict[str, Workflow] = {}
        self.adapters: Dict[str, type] = self._register_adapters()
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.running_workflows: Dict[str, Tuple[Workflow, Dict[str, Future]]] = {}
        self.result_dir: Optional[str] = None
    
    def _register_adapters(self) -> Dict[str, type]:
        """
        Register all available adapters.
        
        Returns:
            Dictionary mapping adapter names to adapter classes
        """
        return {
            "zap": ZAPAdapter,
            "nmap": NmapAdapter,
            "trivy": TrivyAdapter,
            "sqlmap": SQLMapAdapter,
            "nuclei": NucleiAdapter,
            "nikto": NiktoAdapter
        }
    
    def set_result_directory(self, directory: str) -> None:
        """
        Set the directory for storing workflow results.
        
        Args:
            directory: Path to the results directory
        """
        self.result_dir = directory
        os.makedirs(directory, exist_ok=True)
    
    def create_workflow(self, name: str, description: str, target: Optional[str] = None, 
                      created_by: Optional[str] = None, tags: Optional[List[str]] = None) -> Workflow:
        """
        Create a new workflow.
        
        Args:
            name: Name of the workflow
            description: Description of the workflow
            target: Target for the workflow
            created_by: Creator of the workflow
            tags: Tags for the workflow
            
        Returns:
            Created workflow
        """
        workflow = Workflow(
            name=name,
            description=description,
            target=target,
            created_by=created_by,
            tags=tags or []
        )
        
        self.workflows[workflow.workflow_id] = workflow
        logger.info(f"Created workflow {workflow.workflow_id}: {name}")
        
        return workflow
    
    def add_task(self, workflow_id: str, adapter_name: str, adapter_options: Dict[str, Any],
               task_name: Optional[str] = None, depends_on: Optional[List[str]] = None) -> Optional[str]:
        """
        Add a task to a workflow.
        
        Args:
            workflow_id: ID of the workflow
            adapter_name: Name of the adapter to use
            adapter_options: Options for the adapter
            task_name: Name of the task
            depends_on: IDs of tasks this task depends on
            
        Returns:
            ID of the created task or None if the workflow doesn't exist
        """
        if workflow_id not in self.workflows:
            logger.error(f"Workflow {workflow_id} not found")
            return None
        
        # Normalize adapter name
        adapter_name = adapter_name.lower()
        
        # Check if adapter exists
        if adapter_name not in self.adapters:
            logger.error(f"Adapter {adapter_name} not found")
            return None
        
        # Create task
        task = WorkflowTask(
            adapter_name=adapter_name,
            adapter_options=adapter_options,
            task_name=task_name or f"{adapter_name.capitalize()} Task",
            depends_on=depends_on or []
        )
        
        # Add to workflow
        self.workflows[workflow_id].tasks.append(task)
        logger.info(f"Added task {task.task_id} to workflow {workflow_id}")
        
        return task.task_id
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Workflow object or None if not found
        """
        return self.workflows.get(workflow_id)
    
    def get_task(self, workflow_id: str, task_id: str) -> Optional[WorkflowTask]:
        """
        Get a task from a workflow.
        
        Args:
            workflow_id: ID of the workflow
            task_id: ID of the task
            
        Returns:
            Task object or None if not found
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None
            
        for task in workflow.tasks:
            if task.task_id == task_id:
                return task
                
        return None
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            True if deleted, False otherwise
        """
        if workflow_id in self.workflows:
            # Check if workflow is running
            if workflow_id in self.running_workflows:
                logger.error(f"Cannot delete workflow {workflow_id} because it is running")
                return False
                
            del self.workflows[workflow_id]
            logger.info(f"Deleted workflow {workflow_id}")
            return True
            
        return False
    
    def execute_workflow(self, workflow_id: str, callback: Optional[Callable[[str, str], None]] = None) -> bool:
        """
        Execute a workflow.
        
        Args:
            workflow_id: ID of the workflow to execute
            callback: Optional callback function to notify about task status changes
            
        Returns:
            True if execution started, False otherwise
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            return False
        
        # Check if workflow is already running
        if workflow_id in self.running_workflows:
            logger.error(f"Workflow {workflow_id} is already running")
            return False
        
        # Start workflow execution
        workflow.status = "running"
        workflow.start_time = datetime.now()
        
        # Create futures dict to track running tasks
        futures: Dict[str, Future] = {}
        
        # Start execution thread
        future = self.executor.submit(
            self._execute_workflow_tasks,
            workflow,
            futures,
            callback
        )
        
        # Store running workflow
        self.running_workflows[workflow_id] = (workflow, futures)
        
        logger.info(f"Started execution of workflow {workflow_id}")
        return True
    
    def _execute_workflow_tasks(self, workflow: Workflow, futures: Dict[str, Future], 
                             callback: Optional[Callable[[str, str], None]]) -> None:
        """
        Execute the tasks in a workflow.
        
        Args:
            workflow: Workflow to execute
            futures: Dictionary to track running tasks
            callback: Optional callback function
        """
        try:
            # Build dependency graph
            depends_on: Dict[str, List[str]] = {}
            dependents: Dict[str, List[str]] = {}
            
            for task in workflow.tasks:
                depends_on[task.task_id] = task.depends_on.copy()
                
                for dep_id in task.depends_on:
                    if dep_id not in dependents:
                        dependents[dep_id] = []
                    dependents[dep_id].append(task.task_id)
            
            # Queue of tasks ready to execute
            ready_queue: List[str] = []
            
            # Find tasks with no dependencies
            for task in workflow.tasks:
                if not task.depends_on:
                    ready_queue.append(task.task_id)
            
            # Execute tasks in dependency order
            while ready_queue:
                task_id = ready_queue.pop(0)
                task = self.get_task(workflow.workflow_id, task_id)
                
                if not task:
                    logger.error(f"Task {task_id} not found in workflow {workflow.workflow_id}")
                    continue
                
                # Skip tasks that are already completed or failed
                if task.status in ["completed", "failed", "cancelled"]:
                    continue
                
                # Check if dependencies are met
                deps_met = True
                for dep_id in task.depends_on:
                    dep_task = self.get_task(workflow.workflow_id, dep_id)
                    if not dep_task or dep_task.status != "completed":
                        deps_met = False
                        break
                
                if not deps_met:
                    logger.warning(f"Dependencies not met for task {task_id}, skipping")
                    continue
                
                # Execute task
                logger.info(f"Executing task {task_id} in workflow {workflow.workflow_id}")
                
                # Update task status
                task.status = "running"
                task.start_time = datetime.now()
                
                # Notify callback if provided
                if callback:
                    callback(workflow.workflow_id, task_id)
                
                # Submit task for execution
                future = self.executor.submit(
                    self._execute_task,
                    workflow.workflow_id,
                    task_id
                )
                
                # Store future
                futures[task_id] = future
                
                # Wait for task to complete
                result = future.result()
                
                # Process result
                if result:
                    # Task completed successfully
                    task.status = "completed"
                    task.end_time = datetime.now()
                    
                    # Add dependent tasks to ready queue
                    for dep_task_id in dependents.get(task_id, []):
                        # Check if all dependencies are met
                        dep_task = self.get_task(workflow.workflow_id, dep_task_id)
                        if not dep_task:
                            continue
                            
                        all_deps_met = True
                        for dep_id in dep_task.depends_on:
                            dep = self.get_task(workflow.workflow_id, dep_id)
                            if not dep or dep.status != "completed":
                                all_deps_met = False
                                break
                        
                        if all_deps_met:
                            ready_queue.append(dep_task_id)
                else:
                    # Task failed
                    task.status = "failed"
                    task.end_time = datetime.now()
                    
                    # Notify callback if provided
                    if callback:
                        callback(workflow.workflow_id, task_id)
            
            # Check if all tasks are completed
            all_completed = True
            for task in workflow.tasks:
                if task.status not in ["completed", "cancelled"]:
                    all_completed = False
                    break
            
            # Update workflow status
            if all_completed:
                workflow.status = "completed"
            else:
                workflow.status = "failed"
            
            workflow.end_time = datetime.now()
            
            # Save workflow results
            if self.result_dir:
                self.save_workflow_results(workflow.workflow_id)
                
        except Exception as e:
            logger.error(f"Error executing workflow {workflow.workflow_id}: {e}")
            workflow.status = "failed"
            workflow.end_time = datetime.now()
            
        finally:
            # Clean up running workflow
            if workflow.workflow_id in self.running_workflows:
                del self.running_workflows[workflow.workflow_id]
    
    def _execute_task(self, workflow_id: str, task_id: str) -> bool:
        """
        Execute a single task.
        
        Args:
            workflow_id: ID of the workflow
            task_id: ID of the task
            
        Returns:
            True if successful, False otherwise
        """
        task = self.get_task(workflow_id, task_id)
        if not task:
            logger.error(f"Task {task_id} not found in workflow {workflow_id}")
            return False
        
        try:
            # Create adapter instance
            adapter_class = self.adapters.get(task.adapter_name.lower())
            if not adapter_class:
                raise ValueError(f"Adapter {task.adapter_name} not found")
                
            adapter = adapter_class()
            
            # Execute adapter
            result = adapter.execute(task.adapter_options)
            
            # Store result
            task.result = result
            
            # Check result status
            if result.status == "completed":
                logger.info(f"Task {task_id} completed successfully")
                return True
            else:
                logger.error(f"Task {task_id} failed: {result.error_message}")
                task.error_message = result.error_message
                return False
                
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            task.error_message = str(e)
            return False
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a running workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            True if cancelled, False otherwise
        """
        if workflow_id not in self.running_workflows:
            logger.error(f"Workflow {workflow_id} is not running")
            return False
        
        workflow, futures = self.running_workflows[workflow_id]
        
        # Cancel all running tasks
        for task_id, future in futures.items():
            if not future.done():
                future.cancel()
                
                # Update task status
                task = self.get_task(workflow_id, task_id)
                if task and task.status == "running":
                    task.status = "cancelled"
                    task.end_time = datetime.now()
        
        # Update workflow status
        workflow.status = "cancelled"
        workflow.end_time = datetime.now()
        
        # Clean up running workflow
        del self.running_workflows[workflow_id]
        
        logger.info(f"Cancelled workflow {workflow_id}")
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Dictionary with workflow status or None if not found
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return None
            
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "status": workflow.status,
            "start_time": workflow.start_time.isoformat() if workflow.start_time else None,
            "end_time": workflow.end_time.isoformat() if workflow.end_time else None,
            "task_count": len(workflow.tasks),
            "completed_tasks": sum(1 for task in workflow.tasks if task.status == "completed"),
            "failed_tasks": sum(1 for task in workflow.tasks if task.status == "failed"),
            "running_tasks": sum(1 for task in workflow.tasks if task.status == "running"),
            "pending_tasks": sum(1 for task in workflow.tasks if task.status == "pending"),
        }
    
    def save_workflow_results(self, workflow_id: str) -> Optional[str]:
        """
        Save workflow results to a file.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Path to the results file or None if not saved
        """
        if not self.result_dir:
            logger.error("Result directory not set")
            return None
            
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            logger.error(f"Workflow {workflow_id} not found")
            return None
        
        try:
            # Create workflow directory
            workflow_dir = os.path.join(self.result_dir, workflow_id)
            os.makedirs(workflow_dir, exist_ok=True)
            
            # Save workflow summary
            summary_file = os.path.join(workflow_dir, "workflow_summary.json")
            with open(summary_file, 'w') as f:
                json.dump(workflow.to_dict(), f, indent=2)
            
            # Save task results
            for task in workflow.tasks:
                if task.result:
                    task_dir = os.path.join(workflow_dir, task.task_id)
                    os.makedirs(task_dir, exist_ok=True)
                    
                    # Save task result
                    result_file = os.path.join(task_dir, "result.json")
                    with open(result_file, 'w') as f:
                        json.dump(task.result.to_dict(), f, indent=2)
                    
                    # Copy result files if any
                    for file_path in task.result.result_files:
                        if os.path.exists(file_path):
                            dest_path = os.path.join(task_dir, os.path.basename(file_path))
                            with open(file_path, 'rb') as src, open(dest_path, 'wb') as dest:
                                dest.write(src.read())
            
            logger.info(f"Saved workflow results to {workflow_dir}")
            return workflow_dir
            
        except Exception as e:
            logger.error(f"Error saving workflow results: {e}")
            return None


# Predefined workflow templates
class WorkflowTemplates:
    """
    Predefined security testing workflow templates.
    """
    
    @staticmethod
    def web_application_scan(target: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a web application security testing workflow.
        
        Args:
            target: Target URL
            options: Additional options
            
        Returns:
            Workflow definition dictionary
        """
        opts = options or {}
        
        return {
            "name": "Web Application Security Scan",
            "description": "Comprehensive web application security testing workflow",
            "target": target,
            "tags": ["web", "appsec"],
            "tasks": [
                {
                    "adapter_name": "nikto",
                    "task_name": "Basic Web Server Scan",
                    "adapter_options": {
                        "host": target,
                        "tuning": opts.get("nikto_tuning", "1234abc")
                    }
                },
                {
                    "adapter_name": "nuclei",
                    "task_name": "Template-based Vulnerability Scan",
                    "adapter_options": {
                        "url": target,
                        "tags": opts.get("nuclei_tags", "cve,oast"),
                        "severity": opts.get("nuclei_severity", ["critical", "high", "medium"])
                    }
                },
                {
                    "adapter_name": "zap",
                    "task_name": "Active Application Scan",
                    "adapter_options": {
                        "target": target,
                        "scan_mode": "active",
                        "spider": True
                    },
                    "depends_on": ["1", "2"]  # Depends on Nikto and Nuclei tasks
                },
                {
                    "adapter_name": "sqlmap",
                    "task_name": "SQL Injection Scan",
                    "adapter_options": {
                        "url": target,
                        "level": opts.get("sqlmap_level", 1),
                        "risk": opts.get("sqlmap_risk", 1),
                        "forms": True
                    },
                    "depends_on": ["3"]  # Depends on ZAP task
                }
            ]
        }
    
    @staticmethod
    def network_infrastructure_scan(target: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a network infrastructure security testing workflow.
        
        Args:
            target: Target IP or hostname
            options: Additional options
            
        Returns:
            Workflow definition dictionary
        """
        opts = options or {}
        
        return {
            "name": "Network Infrastructure Security Scan",
            "description": "Comprehensive network infrastructure security testing workflow",
            "target": target,
            "tags": ["network", "infrastructure"],
            "tasks": [
                {
                    "adapter_name": "nmap",
                    "task_name": "Network Discovery Scan",
                    "adapter_options": {
                        "target": target,
                        "scan_type": opts.get("nmap_scan_type", "SV"),
                        "ports": opts.get("nmap_ports", "1-10000")
                    }
                },
                {
                    "adapter_name": "nmap",
                    "task_name": "Vulnerability Detection Scan",
                    "adapter_options": {
                        "target": target,
                        "scan_type": "A",
                        "script": "vuln",
                        "ports": opts.get("nmap_vuln_ports", "1-65535")
                    },
                    "depends_on": ["1"]  # Depends on first Nmap task
                }
            ]
        }
    
    @staticmethod
    def container_security_scan(target: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a container security testing workflow.
        
        Args:
            target: Target container image or Kubernetes context
            options: Additional options
            
        Returns:
            Workflow definition dictionary
        """
        opts = options or {}
        
        return {
            "name": "Container Security Scan",
            "description": "Comprehensive container and Kubernetes security testing workflow",
            "target": target,
            "tags": ["container", "kubernetes"],
            "tasks": [
                {
                    "adapter_name": "trivy",
                    "task_name": "Container Image Vulnerability Scan",
                    "adapter_options": {
                        "target": target,
                        "scan_type": "image",
                        "severity": opts.get("trivy_severity", ["HIGH", "CRITICAL"])
                    }
                },
                {
                    "adapter_name": "trivy",
                    "task_name": "Container Configuration Scan",
                    "adapter_options": {
                        "target": target,
                        "scan_type": "config",
                        "scan_path": opts.get("config_path", "./"),
                        "severity": opts.get("trivy_config_severity", ["HIGH", "CRITICAL"])
                    }
                }
            ]
        }
    
    @staticmethod
    def full_stack_security_scan(target: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a full stack security testing workflow.
        
        Args:
            target: Target URL or application
            options: Additional options
            
        Returns:
            Workflow definition dictionary
        """
        opts = options or {}
        
        web_workflow = WorkflowTemplates.web_application_scan(target, opts)
        network_target = opts.get("network_target", target.replace("https://", "").replace("http://", "").split("/")[0])
        network_workflow = WorkflowTemplates.network_infrastructure_scan(network_target, opts)
        container_target = opts.get("container_target", "")
        
        # Combine workflows
        workflow = {
            "name": "Full Stack Security Scan",
            "description": "Comprehensive security testing across web, network, and container layers",
            "target": target,
            "tags": ["fullstack", "comprehensive"],
            "tasks": []
        }
        
        # Add web tasks
        for i, task in enumerate(web_workflow["tasks"]):
            task["task_id"] = f"web_{i+1}"
            workflow["tasks"].append(task)
        
        # Add network tasks
        for i, task in enumerate(network_workflow["tasks"]):
            task["task_id"] = f"network_{i+1}"
            workflow["tasks"].append(task)
        
        # Add container tasks if target is specified
        if container_target:
            container_workflow = WorkflowTemplates.container_security_scan(container_target, opts)
            for i, task in enumerate(container_workflow["tasks"]):
                task["task_id"] = f"container_{i+1}"
                workflow["tasks"].append(task)
        
        return workflow


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create orchestrator
    orchestrator = WorkflowOrchestrator()
    
    # Set result directory
    orchestrator.set_result_directory("/tmp/securescout_results")
    
    # Create workflow from template
    web_workflow = WorkflowTemplates.web_application_scan("https://example.com")
    
    # Create workflow
    workflow = orchestrator.create_workflow(
        name=web_workflow["name"],
        description=web_workflow["description"],
        target=web_workflow["target"],
        tags=web_workflow["tags"]
    )
    
    # Add tasks
    for task_def in web_workflow["tasks"]:
        task_id = orchestrator.add_task(
            workflow_id=workflow.workflow_id,
            adapter_name=task_def["adapter_name"],
            adapter_options=task_def["adapter_options"],
            task_name=task_def.get("task_name"),
            depends_on=task_def.get("depends_on", [])
        )
    
    # Execute workflow
    # orchestrator.execute_workflow(workflow.workflow_id)
    
    # Print workflow definition
    print(json.dumps(workflow.to_dict(), indent=2))