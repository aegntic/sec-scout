# SecureScout API Reference

This document provides detailed information about the SecureScout API endpoints, request/response formats, and usage examples.

## Table of Contents

1. [Authentication](#authentication)
2. [Workflow Management](#workflow-management)
3. [Security Tool Integration](#security-tool-integration)
4. [Results and Reporting](#results-and-reporting)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

## Authentication

All API endpoints require authentication (except health check and some demo endpoints). Authentication is done using JWT tokens.

### Get Authentication Token

Obtain a token for API access.

**Endpoint:** `POST /api/auth/login`

**Request:**
```json
{
  "username": "user@example.com",
  "password": "password"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2025-05-23T10:00:00Z",
    "user": {
      "id": "user123",
      "email": "user@example.com",
      "name": "User Name"
    }
  }
}
```

### Use Authentication Token

Include the token in the Authorization header for all authenticated requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Workflow Management

Endpoints for creating, managing, and executing security testing workflows.

### List Workflows

Get a list of all workflows.

**Endpoint:** `GET /api/v1/workflows/`

**Response:**
```json
{
  "status": "success",
  "data": {
    "workflows": [
      {
        "id": "wf_123",
        "name": "Web Application Scan",
        "description": "Comprehensive web app scan",
        "status": "completed",
        "target": "https://example.com",
        "created_by": "user@example.com",
        "tags": ["web", "appsec"],
        "start_time": "2025-05-22T08:00:00Z",
        "end_time": "2025-05-22T08:30:00Z",
        "task_count": 4,
        "completed_tasks": 4,
        "failed_tasks": 0
      },
      {
        "id": "wf_124",
        "name": "Network Scan",
        "description": "Network security scan",
        "status": "running",
        "target": "192.168.1.0/24",
        "created_by": "user@example.com",
        "tags": ["network"],
        "start_time": "2025-05-22T09:00:00Z",
        "end_time": null,
        "task_count": 2,
        "completed_tasks": 1,
        "failed_tasks": 0
      }
    ],
    "count": 2
  }
}
```

### Create Workflow

Create a new security testing workflow.

**Endpoint:** `POST /api/v1/workflows/`

**Request:**
```json
{
  "name": "Custom Security Scan",
  "description": "Custom security testing workflow",
  "target": "https://example.com",
  "created_by": "user@example.com",
  "tags": ["custom", "security"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "workflow": {
      "workflow_id": "wf_125",
      "name": "Custom Security Scan",
      "description": "Custom security testing workflow",
      "status": "pending",
      "start_time": null,
      "end_time": null,
      "target": "https://example.com",
      "created_by": "user@example.com",
      "tags": ["custom", "security"],
      "tasks": [],
      "task_count": 0,
      "completed_tasks": 0,
      "failed_tasks": 0
    },
    "message": "Workflow created successfully"
  }
}
```

### List Workflow Templates

Get available workflow templates.

**Endpoint:** `GET /api/v1/workflows/templates`

**Response:**
```json
{
  "status": "success",
  "data": {
    "templates": [
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
    ],
    "count": 4
  }
}
```

### Create Workflow from Template

Create a workflow using a predefined template.

**Endpoint:** `POST /api/v1/workflows/from-template`

**Request:**
```json
{
  "template_id": "web_application_scan",
  "target": "https://example.com",
  "created_by": "user@example.com",
  "options": {
    "nikto_tuning": "1234abc",
    "nuclei_tags": "cve,oast",
    "sqlmap_level": 2
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "workflow": {
      "workflow_id": "wf_126",
      "name": "Web Application Security Scan",
      "description": "Comprehensive web application security testing workflow",
      "status": "pending",
      "start_time": null,
      "end_time": null,
      "target": "https://example.com",
      "created_by": "user@example.com",
      "tags": ["web", "appsec"],
      "tasks": [
        {
          "task_id": "task_1",
          "task_name": "Basic Web Server Scan",
          "adapter_name": "nikto",
          "status": "pending",
          "depends_on": []
        },
        {
          "task_id": "task_2",
          "task_name": "Template-based Vulnerability Scan",
          "adapter_name": "nuclei",
          "status": "pending",
          "depends_on": []
        },
        {
          "task_id": "task_3",
          "task_name": "Active Application Scan",
          "adapter_name": "zap",
          "status": "pending",
          "depends_on": ["task_1", "task_2"]
        },
        {
          "task_id": "task_4",
          "task_name": "SQL Injection Scan",
          "adapter_name": "sqlmap",
          "status": "pending",
          "depends_on": ["task_3"]
        }
      ],
      "task_count": 4,
      "completed_tasks": 0,
      "failed_tasks": 0
    },
    "message": "Workflow created successfully from template"
  }
}
```

### Get Workflow Details

Get detailed information about a specific workflow.

**Endpoint:** `GET /api/v1/workflows/{workflow_id}`

**Response:**
```json
{
  "status": "success",
  "data": {
    "workflow": {
      "workflow_id": "wf_126",
      "name": "Web Application Security Scan",
      "description": "Comprehensive web application security testing workflow",
      "status": "running",
      "start_time": "2025-05-22T10:00:00Z",
      "end_time": null,
      "target": "https://example.com",
      "created_by": "user@example.com",
      "tags": ["web", "appsec"],
      "tasks": [
        {
          "task_id": "task_1",
          "task_name": "Basic Web Server Scan",
          "adapter_name": "nikto",
          "status": "completed",
          "depends_on": [],
          "start_time": "2025-05-22T10:00:00Z",
          "end_time": "2025-05-22T10:05:00Z",
          "error_message": null,
          "result_summary": {
            "tool_name": "nikto",
            "status": "completed",
            "parsed_findings_count": 12
          }
        },
        {
          "task_id": "task_2",
          "task_name": "Template-based Vulnerability Scan",
          "adapter_name": "nuclei",
          "status": "running",
          "depends_on": [],
          "start_time": "2025-05-22T10:00:00Z",
          "end_time": null,
          "error_message": null,
          "result_summary": null
        }
      ],
      "task_count": 4,
      "completed_tasks": 1,
      "failed_tasks": 0
    }
  }
}
```

### Delete Workflow

Delete a workflow.

**Endpoint:** `DELETE /api/v1/workflows/{workflow_id}`

**Response:**
```json
{
  "status": "success",
  "message": "Workflow wf_126 deleted successfully"
}
```

### Add Task to Workflow

Add a new task to an existing workflow.

**Endpoint:** `POST /api/v1/workflows/{workflow_id}/tasks`

**Request:**
```json
{
  "adapter_name": "zap",
  "adapter_options": {
    "target": "https://example.com",
    "scan_mode": "active"
  },
  "task_name": "ZAP Active Scan",
  "depends_on": ["task_1", "task_2"]
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "task": {
      "task_id": "task_5",
      "task_name": "ZAP Active Scan",
      "adapter_name": "zap",
      "status": "pending",
      "depends_on": ["task_1", "task_2"]
    },
    "message": "Task added successfully"
  }
}
```

### Execute Workflow

Start workflow execution.

**Endpoint:** `POST /api/v1/workflows/{workflow_id}/execute`

**Response:**
```json
{
  "status": "success",
  "message": "Workflow wf_126 execution started"
}
```

### Cancel Workflow

Cancel a running workflow.

**Endpoint:** `POST /api/v1/workflows/{workflow_id}/cancel`

**Response:**
```json
{
  "status": "success",
  "message": "Workflow wf_126 cancelled successfully"
}
```

### Get Workflow Status

Check the current status of a workflow.

**Endpoint:** `GET /api/v1/workflows/{workflow_id}/status`

**Response:**
```json
{
  "status": "success",
  "data": {
    "workflow_status": {
      "workflow_id": "wf_126",
      "name": "Web Application Security Scan",
      "status": "running",
      "start_time": "2025-05-22T10:00:00Z",
      "end_time": null,
      "task_count": 4,
      "completed_tasks": 2,
      "failed_tasks": 0,
      "running_tasks": 1,
      "pending_tasks": 1
    }
  }
}
```

### Get Workflow Results

Get summary of workflow execution results.

**Endpoint:** `GET /api/v1/workflows/{workflow_id}/results`

**Response:**
```json
{
  "status": "success",
  "data": {
    "workflow_id": "wf_126",
    "name": "Web Application Security Scan",
    "target": "https://example.com",
    "start_time": "2025-05-22T10:00:00Z",
    "end_time": "2025-05-22T10:30:00Z",
    "finding_count": 15,
    "severity_counts": {
      "critical": 1,
      "high": 3,
      "medium": 6,
      "low": 4,
      "info": 1,
      "unknown": 0
    },
    "task_results": [
      {
        "task_id": "task_1",
        "task_name": "Basic Web Server Scan",
        "adapter_name": "nikto",
        "status": "completed",
        "finding_count": 5
      },
      {
        "task_id": "task_2",
        "task_name": "Template-based Vulnerability Scan",
        "adapter_name": "nuclei",
        "status": "completed",
        "finding_count": 4
      },
      {
        "task_id": "task_3",
        "task_name": "Active Application Scan",
        "adapter_name": "zap",
        "status": "completed",
        "finding_count": 4
      },
      {
        "task_id": "task_4",
        "task_name": "SQL Injection Scan",
        "adapter_name": "sqlmap",
        "status": "completed",
        "finding_count": 2
      }
    ]
  }
}
```

### Get Workflow Findings

Get detailed findings from a workflow.

**Endpoint:** `GET /api/v1/workflows/{workflow_id}/findings`

**Query Parameters:**
- `severity`: Filter by severity (comma-separated values)
- `adapter`: Filter by adapter (comma-separated values)
- `limit`: Limit the number of findings (default: 100)
- `offset`: Offset for pagination (default: 0)

**Response:**
```json
{
  "status": "success",
  "data": {
    "findings": [
      {
        "title": "SQL Injection in parameter 'id'",
        "severity": "high",
        "description": "SQL Injection vulnerability detected in parameter 'id' using UNION technique.",
        "evidence": {
          "parameter": "id",
          "injection_type": "UNION query",
          "database_type": "MySQL"
        },
        "remediation": "Implement proper input validation and parameterized queries to prevent SQL injection attacks.",
        "task_id": "task_4",
        "task_name": "SQL Injection Scan",
        "adapter_name": "sqlmap"
      },
      {
        "title": "Cross-site Scripting (XSS) in search parameter",
        "severity": "medium",
        "description": "Reflected XSS vulnerability detected in search parameter.",
        "evidence": {
          "url": "https://example.com/search?q=test",
          "payload": "<script>alert(1)</script>",
          "response": "...contains unfiltered payload..."
        },
        "remediation": "Implement output encoding and content security policy.",
        "task_id": "task_3",
        "task_name": "Active Application Scan",
        "adapter_name": "zap"
      }
    ],
    "total_count": 15,
    "returned_count": 2,
    "limit": 2,
    "offset": 0
  }
}
```

### Export Workflow Results

Export workflow results to a file.

**Endpoint:** `GET /api/v1/workflows/{workflow_id}/export`

**Query Parameters:**
- `format`: Export format (json, html, csv, pdf) (default: json)

**Response:**
```json
{
  "status": "success",
  "data": {
    "export_path": "/tmp/securescout_results/wf_126",
    "format": "json",
    "message": "Workflow results exported successfully to /tmp/securescout_results/wf_126"
  }
}
```

## Security Tool Integration

Endpoints for interacting with security tool adapters.

### List Available Adapters

Get a list of available security tool adapters.

**Endpoint:** `GET /api/v1/workflows/adapters`

**Response:**
```json
{
  "status": "success",
  "data": {
    "adapters": [
      {
        "name": "zap",
        "display_name": "ZAP",
        "description": "Adapter for OWASP ZAP (Zed Attack Proxy)"
      },
      {
        "name": "nmap",
        "display_name": "Nmap",
        "description": "Adapter for Nmap network scanner"
      },
      {
        "name": "trivy",
        "display_name": "Trivy",
        "description": "Adapter for Trivy container vulnerability scanner"
      },
      {
        "name": "sqlmap",
        "display_name": "SQLMap",
        "description": "Adapter for SQLMap SQL injection scanner"
      },
      {
        "name": "nuclei",
        "display_name": "Nuclei",
        "description": "Adapter for Nuclei vulnerability scanner"
      },
      {
        "name": "nikto",
        "display_name": "Nikto",
        "description": "Adapter for Nikto web server scanner"
      }
    ],
    "count": 6
  }
}
```

## Results and Reporting

The following endpoints from the existing API are used for accessing scan results and reports:

- `GET /api/report/list`: List all scan reports
- `GET /api/report/{report_id}`: Get a specific scan report
- `GET /api/report/{report_id}/download/{format}`: Download a report in a specific format

## Error Handling

All API endpoints return standardized error responses when errors occur:

```json
{
  "status": "error",
  "message": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Not authorized to access the resource
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

## Examples

### Creating and Executing a Web Application Scan

1. Create a workflow from template:

```bash
curl -X POST http://localhost:8001/api/v1/workflows/from-template \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "web_application_scan",
    "target": "https://example.com",
    "created_by": "user@example.com",
    "options": {
      "nikto_tuning": "1234abc",
      "nuclei_tags": "cve,oast"
    }
  }'
```

2. Execute the workflow:

```bash
curl -X POST http://localhost:8001/api/v1/workflows/YOUR_WORKFLOW_ID/execute \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. Check workflow status:

```bash
curl -X GET http://localhost:8001/api/v1/workflows/YOUR_WORKFLOW_ID/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

4. Get results when completed:

```bash
curl -X GET http://localhost:8001/api/v1/workflows/YOUR_WORKFLOW_ID/findings \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Creating a Custom Workflow

1. Create a workflow:

```bash
curl -X POST http://localhost:8001/api/v1/workflows/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Custom Security Scan",
    "description": "Custom security testing workflow",
    "target": "https://example.com",
    "created_by": "user@example.com",
    "tags": ["custom", "security"]
  }'
```

2. Add tasks to the workflow:

```bash
curl -X POST http://localhost:8001/api/v1/workflows/YOUR_WORKFLOW_ID/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "adapter_name": "nmap",
    "adapter_options": {
      "target": "example.com",
      "ports": "1-1000",
      "scan_type": "SV"
    },
    "task_name": "Network Discovery Scan"
  }'
```

```bash
curl -X POST http://localhost:8001/api/v1/workflows/YOUR_WORKFLOW_ID/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "adapter_name": "zap",
    "adapter_options": {
      "target": "https://example.com",
      "scan_mode": "active",
      "spider": true
    },
    "task_name": "ZAP Active Scan",
    "depends_on": ["PREVIOUS_TASK_ID"]
  }'
```

3. Execute the workflow:

```bash
curl -X POST http://localhost:8001/api/v1/workflows/YOUR_WORKFLOW_ID/execute \
  -H "Authorization: Bearer YOUR_TOKEN"
```