#!/usr/bin/env python3
# SecureScout - Workflow API Controller

import os
import sys
import json
import logging
import uuid
from typing import Dict, List, Any, Optional, Union
from flask import Blueprint, request, jsonify, current_app

# Add parent directory to path to allow importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import workflow orchestrator
from modules.integrations.workflow_orchestrator import (
    WorkflowOrchestrator,
    WorkflowTemplates,
    Workflow,
    WorkflowTask
)

# Configure logging
logger = logging.getLogger("securescout.api.workflow")

# Create blueprint
workflow_bp = Blueprint("workflow", __name__, url_prefix="/api/v1/workflows")

# Create workflow orchestrator
orchestrator = WorkflowOrchestrator()

# Initialize orchestrator
def init_workflow_orchestrator(app):
    """
    Initialize the workflow orchestrator with application config.
    
    Args:
        app: Flask application instance
    """
    result_dir = app.config.get("WORKFLOW_RESULT_DIR", "/tmp/securescout_results")
    orchestrator.set_result_directory(result_dir)
    logger.info(f"Initialized workflow orchestrator with result directory: {result_dir}")


# Workflow routes
@workflow_bp.route("/", methods=["GET"])
def list_workflows():
    """
    List all workflows.
    
    Returns:
        JSON response with list of workflows
    """
    try:
        workflows = [
            {
                "id": wf_id,
                "name": wf.name,
                "description": wf.description,
                "status": wf.status,
                "target": wf.target,
                "created_by": wf.created_by,
                "tags": wf.tags,
                "start_time": wf.start_time.isoformat() if wf.start_time else None,
                "end_time": wf.end_time.isoformat() if wf.end_time else None,
                "task_count": len(wf.tasks),
                "completed_tasks": sum(1 for task in wf.tasks if task.status == "completed"),
                "failed_tasks": sum(1 for task in wf.tasks if task.status == "failed")
            }
            for wf_id, wf in orchestrator.workflows.items()
        ]
        
        return jsonify({
            "status": "success",
            "data": {
                "workflows": workflows,
                "count": len(workflows)
            }
        })
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error listing workflows: {str(e)}"
        }), 500


@workflow_bp.route("/", methods=["POST"])
def create_workflow():
    """
    Create a new workflow.
    
    Expected request body:
    {
        "name": "Workflow Name",
        "description": "Workflow Description",
        "target": "https://example.com",
        "created_by": "username",
        "tags": ["tag1", "tag2"]
    }
    
    Returns:
        JSON response with created workflow
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Create workflow
        workflow = orchestrator.create_workflow(
            name=data["name"],
            description=data["description"],
            target=data.get("target"),
            created_by=data.get("created_by"),
            tags=data.get("tags", [])
        )
        
        return jsonify({
            "status": "success",
            "data": {
                "workflow": workflow.to_dict(),
                "message": "Workflow created successfully"
            }
        }), 201
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error creating workflow: {str(e)}"
        }), 500


@workflow_bp.route("/templates", methods=["GET"])
def list_workflow_templates():
    """
    List available workflow templates.
    
    Returns:
        JSON response with list of templates
    """
    try:
        # Define available templates
        templates = [
            {
                "id": "web_application_scan",
                "name": "Web Application Security Scan",
                "description": "Comprehensive web application security testing workflow",
                "target_type": "url",
                "tags": ["web", "appsec"]
            },
            {
                "id": "network_infrastructure_scan",
                "name": "Network Infrastructure Security Scan",
                "description": "Comprehensive network infrastructure security testing workflow",
                "target_type": "ip_or_hostname",
                "tags": ["network", "infrastructure"]
            },
            {
                "id": "container_security_scan",
                "name": "Container Security Scan",
                "description": "Comprehensive container and Kubernetes security testing workflow",
                "target_type": "container_image",
                "tags": ["container", "kubernetes"]
            },
            {
                "id": "full_stack_security_scan",
                "name": "Full Stack Security Scan",
                "description": "Comprehensive security testing across web, network, and container layers",
                "target_type": "url",
                "tags": ["fullstack", "comprehensive"]
            }
        ]
        
        return jsonify({
            "status": "success",
            "data": {
                "templates": templates,
                "count": len(templates)
            }
        })
    except Exception as e:
        logger.error(f"Error listing workflow templates: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error listing workflow templates: {str(e)}"
        }), 500


@workflow_bp.route("/from-template", methods=["POST"])
def create_workflow_from_template():
    """
    Create a new workflow from a template.
    
    Expected request body:
    {
        "template_id": "web_application_scan",
        "target": "https://example.com",
        "created_by": "username",
        "options": {
            "nikto_tuning": "1234abc",
            "nuclei_tags": "cve,oast",
            "sqlmap_level": 2
        }
    }
    
    Returns:
        JSON response with created workflow
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ["template_id", "target"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Get template
        template_id = data["template_id"]
        target = data["target"]
        options = data.get("options", {})
        
        template_func = None
        if template_id == "web_application_scan":
            template_func = WorkflowTemplates.web_application_scan
        elif template_id == "network_infrastructure_scan":
            template_func = WorkflowTemplates.network_infrastructure_scan
        elif template_id == "container_security_scan":
            template_func = WorkflowTemplates.container_security_scan
        elif template_id == "full_stack_security_scan":
            template_func = WorkflowTemplates.full_stack_security_scan
        else:
            return jsonify({
                "status": "error",
                "message": f"Unknown template ID: {template_id}"
            }), 400
        
        # Create workflow from template
        template = template_func(target, options)
        
        # Create workflow
        workflow = orchestrator.create_workflow(
            name=template["name"],
            description=template["description"],
            target=template["target"],
            created_by=data.get("created_by"),
            tags=template["tags"]
        )
        
        # Add tasks
        for task_def in template["tasks"]:
            # Get depends_on from task definition
            depends_on = task_def.get("depends_on", [])
            
            # Add task to workflow
            task_id = orchestrator.add_task(
                workflow_id=workflow.workflow_id,
                adapter_name=task_def["adapter_name"],
                adapter_options=task_def["adapter_options"],
                task_name=task_def.get("task_name"),
                depends_on=depends_on
            )
        
        return jsonify({
            "status": "success",
            "data": {
                "workflow": workflow.to_dict(),
                "message": "Workflow created successfully from template"
            }
        }), 201
    except Exception as e:
        logger.error(f"Error creating workflow from template: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error creating workflow from template: {str(e)}"
        }), 500


@workflow_bp.route("/<workflow_id>", methods=["GET"])
def get_workflow(workflow_id):
    """
    Get a workflow by ID.
    
    Args:
        workflow_id: ID of the workflow
        
    Returns:
        JSON response with workflow details
    """
    try:
        workflow = orchestrator.get_workflow(workflow_id)
        if not workflow:
            return jsonify({
                "status": "error",
                "message": f"Workflow not found: {workflow_id}"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": {
                "workflow": workflow.to_dict()
            }
        })
    except Exception as e:
        logger.error(f"Error getting workflow {workflow_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error getting workflow: {str(e)}"
        }), 500


@workflow_bp.route("/<workflow_id>", methods=["DELETE"])
def delete_workflow(workflow_id):
    """
    Delete a workflow by ID.
    
    Args:
        workflow_id: ID of the workflow
        
    Returns:
        JSON response indicating success or failure
    """
    try:
        if orchestrator.delete_workflow(workflow_id):
            return jsonify({
                "status": "success",
                "message": f"Workflow {workflow_id} deleted successfully"
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Workflow not found or could not be deleted: {workflow_id}"
            }), 404
    except Exception as e:
        logger.error(f"Error deleting workflow {workflow_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error deleting workflow: {str(e)}"
        }), 500


@workflow_bp.route("/<workflow_id>/tasks", methods=["POST"])
def add_task(workflow_id):
    """
    Add a task to a workflow.
    
    Args:
        workflow_id: ID of the workflow
        
    Expected request body:
    {
        "adapter_name": "zap",
        "adapter_options": {
            "target": "https://example.com",
            "scan_mode": "active"
        },
        "task_name": "ZAP Scan",
        "depends_on": ["task1_id", "task2_id"]
    }
    
    Returns:
        JSON response with added task
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = ["adapter_name", "adapter_options"]
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Add task to workflow
        task_id = orchestrator.add_task(
            workflow_id=workflow_id,
            adapter_name=data["adapter_name"],
            adapter_options=data["adapter_options"],
            task_name=data.get("task_name"),
            depends_on=data.get("depends_on", [])
        )
        
        if not task_id:
            return jsonify({
                "status": "error",
                "message": f"Failed to add task to workflow {workflow_id}"
            }), 400
        
        # Get task details
        task = orchestrator.get_task(workflow_id, task_id)
        
        return jsonify({
            "status": "success",
            "data": {
                "task": {
                    "task_id": task.task_id,
                    "task_name": task.task_name,
                    "adapter_name": task.adapter_name,
                    "status": task.status,
                    "depends_on": task.depends_on
                },
                "message": "Task added successfully"
            }
        }), 201
    except Exception as e:
        logger.error(f"Error adding task to workflow {workflow_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error adding task: {str(e)}"
        }), 500


@workflow_bp.route("/<workflow_id>/execute", methods=["POST"])
def execute_workflow(workflow_id):
    """
    Execute a workflow.
    
    Args:
        workflow_id: ID of the workflow
        
    Returns:
        JSON response indicating success or failure
    """
    try:
        if orchestrator.execute_workflow(workflow_id):
            return jsonify({
                "status": "success",
                "message": f"Workflow {workflow_id} execution started"
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Failed to execute workflow {workflow_id}"
            }), 400
    except Exception as e:
        logger.error(f"Error executing workflow {workflow_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error executing workflow: {str(e)}"
        }), 500


@workflow_bp.route("/<workflow_id>/cancel", methods=["POST"])
def cancel_workflow(workflow_id):
    """
    Cancel a running workflow.
    
    Args:
        workflow_id: ID of the workflow
        
    Returns:
        JSON response indicating success or failure
    """
    try:
        if orchestrator.cancel_workflow(workflow_id):
            return jsonify({
                "status": "success",
                "message": f"Workflow {workflow_id} cancelled successfully"
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Workflow not found or not running: {workflow_id}"
            }), 400
    except Exception as e:
        logger.error(f"Error cancelling workflow {workflow_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error cancelling workflow: {str(e)}"
        }), 500


@workflow_bp.route("/<workflow_id>/status", methods=["GET"])
def get_workflow_status(workflow_id):
    """
    Get the status of a workflow.
    
    Args:
        workflow_id: ID of the workflow
        
    Returns:
        JSON response with workflow status
    """
    try:
        status = orchestrator.get_workflow_status(workflow_id)
        if not status:
            return jsonify({
                "status": "error",
                "message": f"Workflow not found: {workflow_id}"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": {
                "workflow_status": status
            }
        })
    except Exception as e:
        logger.error(f"Error getting workflow status {workflow_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error getting workflow status: {str(e)}"
        }), 500


@workflow_bp.route("/<workflow_id>/results", methods=["GET"])
def get_workflow_results(workflow_id):
    """
    Get the results of a workflow.
    
    Args:
        workflow_id: ID of the workflow
        
    Returns:
        JSON response with workflow results
    """
    try:
        workflow = orchestrator.get_workflow(workflow_id)
        if not workflow:
            return jsonify({
                "status": "error",
                "message": f"Workflow not found: {workflow_id}"
            }), 404
        
        # Check if workflow is completed
        if workflow.status != "completed":
            return jsonify({
                "status": "error",
                "message": f"Workflow not completed: {workflow_id}, current status: {workflow.status}"
            }), 400
        
        # Get findings count
        finding_count = 0
        for task in workflow.tasks:
            if task.result:
                finding_count += len(task.result.parsed_findings)
        
        # Get severity counts
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
            "unknown": 0
        }
        
        for task in workflow.tasks:
            if task.result:
                for finding in task.result.parsed_findings:
                    severity = finding.get("severity", "unknown").lower()
                    if severity in severity_counts:
                        severity_counts[severity] += 1
        
        # Get task results
        task_results = []
        for task in workflow.tasks:
            task_result = {
                "task_id": task.task_id,
                "task_name": task.task_name,
                "adapter_name": task.adapter_name,
                "status": task.status,
                "finding_count": len(task.result.parsed_findings) if task.result else 0
            }
            task_results.append(task_result)
        
        # Return results summary
        return jsonify({
            "status": "success",
            "data": {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "target": workflow.target,
                "start_time": workflow.start_time.isoformat() if workflow.start_time else None,
                "end_time": workflow.end_time.isoformat() if workflow.end_time else None,
                "finding_count": finding_count,
                "severity_counts": severity_counts,
                "task_results": task_results
            }
        })
    except Exception as e:
        logger.error(f"Error getting workflow results {workflow_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error getting workflow results: {str(e)}"
        }), 500


@workflow_bp.route("/<workflow_id>/findings", methods=["GET"])
def get_workflow_findings(workflow_id):
    """
    Get the findings from a workflow.
    
    Args:
        workflow_id: ID of the workflow
        
    Query parameters:
        - severity: Filter by severity (comma-separated values)
        - adapter: Filter by adapter (comma-separated values)
        - limit: Limit the number of findings (default: 100)
        - offset: Offset for pagination (default: 0)
        
    Returns:
        JSON response with workflow findings
    """
    try:
        workflow = orchestrator.get_workflow(workflow_id)
        if not workflow:
            return jsonify({
                "status": "error",
                "message": f"Workflow not found: {workflow_id}"
            }), 404
        
        # Parse query parameters
        severity_filter = request.args.get("severity", "").lower().split(",")
        adapter_filter = request.args.get("adapter", "").lower().split(",")
        limit = int(request.args.get("limit", 100))
        offset = int(request.args.get("offset", 0))
        
        # Clean up empty filters
        severity_filter = [s for s in severity_filter if s]
        adapter_filter = [a for a in adapter_filter if a]
        
        # Collect findings from all tasks
        all_findings = []
        for task in workflow.tasks:
            if not task.result:
                continue
                
            if adapter_filter and task.adapter_name.lower() not in adapter_filter:
                continue
                
            for finding in task.result.parsed_findings:
                # Apply severity filter
                if severity_filter and finding.get("severity", "").lower() not in severity_filter:
                    continue
                    
                # Add task and adapter info to finding
                enriched_finding = finding.copy()
                enriched_finding["task_id"] = task.task_id
                enriched_finding["task_name"] = task.task_name
                enriched_finding["adapter_name"] = task.adapter_name
                
                all_findings.append(enriched_finding)
        
        # Apply pagination
        paginated_findings = all_findings[offset:offset+limit]
        
        return jsonify({
            "status": "success",
            "data": {
                "findings": paginated_findings,
                "total_count": len(all_findings),
                "returned_count": len(paginated_findings),
                "limit": limit,
                "offset": offset
            }
        })
    except Exception as e:
        logger.error(f"Error getting workflow findings {workflow_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error getting workflow findings: {str(e)}"
        }), 500


@workflow_bp.route("/<workflow_id>/export", methods=["GET"])
def export_workflow_results(workflow_id):
    """
    Export workflow results to a file.
    
    Args:
        workflow_id: ID of the workflow
        
    Query parameters:
        - format: Export format (json, html, csv, pdf) (default: json)
        
    Returns:
        JSON response with export status and file path
    """
    try:
        export_format = request.args.get("format", "json").lower()
        
        if export_format not in ["json", "html", "csv", "pdf"]:
            return jsonify({
                "status": "error",
                "message": f"Unsupported export format: {export_format}"
            }), 400
        
        # For now, we only support JSON export
        if export_format != "json":
            return jsonify({
                "status": "error",
                "message": f"Export format {export_format} not implemented yet"
            }), 501
        
        # Export workflow results
        result_path = orchestrator.save_workflow_results(workflow_id)
        
        if not result_path:
            return jsonify({
                "status": "error",
                "message": f"Failed to export workflow results: {workflow_id}"
            }), 500
        
        return jsonify({
            "status": "success",
            "data": {
                "export_path": result_path,
                "format": export_format,
                "message": f"Workflow results exported successfully to {result_path}"
            }
        })
    except Exception as e:
        logger.error(f"Error exporting workflow results {workflow_id}: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error exporting workflow results: {str(e)}"
        }), 500


# Adapter routes
@workflow_bp.route("/adapters", methods=["GET"])
def list_adapters():
    """
    List available adapters.
    
    Returns:
        JSON response with list of adapters
    """
    try:
        adapters = []
        
        for adapter_name, adapter_class in orchestrator.adapters.items():
            adapter_info = {
                "name": adapter_name,
                "display_name": adapter_name.capitalize(),
                "description": getattr(adapter_class, "__doc__", "").strip() or f"{adapter_name.capitalize()} security tool adapter"
            }
            adapters.append(adapter_info)
        
        return jsonify({
            "status": "success",
            "data": {
                "adapters": adapters,
                "count": len(adapters)
            }
        })
    except Exception as e:
        logger.error(f"Error listing adapters: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error listing adapters: {str(e)}"
        }), 500


# Register blueprint to app
def register_workflow_blueprint(app):
    """
    Register workflow blueprint to Flask app.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(workflow_bp)
    init_workflow_orchestrator(app)
    logger.info("Registered workflow blueprint")