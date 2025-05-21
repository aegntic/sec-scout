# SecureScout Integration Framework Guide

This guide provides documentation for the SecureScout integration framework, which allows for seamless integration of various security testing tools and workflows.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Tool Adapters](#tool-adapters)
   - [Base Adapter](#base-adapter)
   - [Available Adapters](#available-adapters)
   - [Adapter Usage](#adapter-usage)
3. [Workflow Orchestration](#workflow-orchestration)
   - [Creating Workflows](#creating-workflows)
   - [Predefined Workflow Templates](#predefined-workflow-templates)
   - [Executing Workflows](#executing-workflows)
4. [API Reference](#api-reference)
   - [Workflow API Endpoints](#workflow-api-endpoints)
   - [Adapter API Endpoints](#adapter-api-endpoints)
5. [Testing and Validation](#testing-and-validation)
   - [Adapter Tester](#adapter-tester)
   - [Workflow Testing](#workflow-testing)
6. [Extending the Framework](#extending-the-framework)
   - [Creating New Adapters](#creating-new-adapters)
   - [Custom Workflow Templates](#custom-workflow-templates)

## Architecture Overview

The SecureScout integration framework is designed with a modular architecture that separates tool-specific code from the core orchestration logic. The key components are:

- **Tool Adapters**: Wrappers around security tools that provide a standardized interface
- **Workflow Orchestrator**: Manages the execution of multiple tools in defined sequences
- **API Layer**: Provides RESTful endpoints for interacting with the framework

The architecture follows these principles:
- **Tool Independence**: Each security tool is wrapped in its own adapter
- **Standardized Interface**: All adapters share a common interface for execution and result handling
- **Flexible Orchestration**: Workflows can be defined with dependencies between tasks
- **Extensibility**: New tools can be easily integrated by creating new adapters

## Tool Adapters

### Base Adapter

All tool adapters inherit from the `BaseToolAdapter` class, which provides common functionality:

```python
from backend.modules.integrations.adapter_base import BaseToolAdapter, ToolResult, Severity

class MyToolAdapter(BaseToolAdapter):
    def __init__(self, executable_path=None):
        super().__init__("my-tool", executable_path)
    
    def prepare_command(self, options):
        # Implement command preparation
        pass
    
    def parse_output(self, output):
        # Implement output parsing
        pass
```

The base adapter handles:
- Tool executable discovery
- Command execution
- Result storage
- Error handling
- Severity normalization

### Available Adapters

The following tool adapters are currently available:

| Adapter | Tool | Purpose | Key Features |
|---------|------|---------|-------------|
| `ZAPAdapter` | OWASP ZAP | Web application security | Spider crawling, active scanning |
| `NmapAdapter` | Nmap | Network discovery and vulnerability | Port scanning, service detection |
| `TrivyAdapter` | Trivy | Container security | Image scanning, misconfiguration detection |
| `SQLMapAdapter` | SQLMap | SQL injection | Parameter testing, database extraction |
| `NucleiAdapter` | Nuclei | Template-based scanning | Custom template support, template management |
| `NiktoAdapter` | Nikto | Web server scanning | Configuration testing, known vulnerabilities |

### Adapter Usage

Each adapter is used in a similar way:

```python
from backend.modules.integrations.sqlmap_adapter import SQLMapAdapter

# Create adapter instance
adapter = SQLMapAdapter()

# Define options
options = {
    "url": "http://example.com/page.php?id=1",
    "level": 1,
    "risk": 1
}

# Execute the tool
result = adapter.execute(options)

# Access results
if result.status == "completed":
    print(f"Found {len(result.parsed_findings)} issues")
    for finding in result.parsed_findings:
        print(f"- {finding['title']} ({finding['severity']})")
```

## Workflow Orchestration

The `WorkflowOrchestrator` class manages the execution of multiple tools in a defined sequence. It supports:

- Task dependencies
- Parallel execution
- Status tracking
- Result aggregation

### Creating Workflows

```python
from backend.modules.integrations.workflow_orchestrator import WorkflowOrchestrator

# Create orchestrator
orchestrator = WorkflowOrchestrator()

# Create workflow
workflow = orchestrator.create_workflow(
    name="Web Security Scan",
    description="Comprehensive web application scan",
    target="https://example.com"
)

# Add tasks
task1_id = orchestrator.add_task(
    workflow_id=workflow.workflow_id,
    adapter_name="nikto",
    adapter_options={
        "host": "https://example.com",
        "tuning": "1234abc"
    }
)

task2_id = orchestrator.add_task(
    workflow_id=workflow.workflow_id,
    adapter_name="zap",
    adapter_options={
        "target": "https://example.com",
        "scan_mode": "active"
    },
    depends_on=[task1_id]  # This task depends on task1
)
```

### Predefined Workflow Templates

The framework includes several predefined workflow templates:

- `web_application_scan`: Comprehensive web application security testing
- `network_infrastructure_scan`: Network discovery and vulnerability assessment
- `container_security_scan`: Container image and configuration scanning
- `full_stack_security_scan`: Combined web, network, and container security testing

Example:

```python
from backend.modules.integrations.workflow_orchestrator import WorkflowTemplates

# Get workflow template definition
template = WorkflowTemplates.web_application_scan(
    target="https://example.com",
    options={
        "nikto_tuning": "1234abc",
        "nuclei_tags": "cve,oast"
    }
)

# Create workflow from template
workflow = orchestrator.create_workflow(
    name=template["name"],
    description=template["description"],
    target=template["target"]
)

# Add tasks from template
for task_def in template["tasks"]:
    orchestrator.add_task(
        workflow_id=workflow.workflow_id,
        adapter_name=task_def["adapter_name"],
        adapter_options=task_def["adapter_options"],
        task_name=task_def.get("task_name"),
        depends_on=task_def.get("depends_on", [])
    )
```

### Executing Workflows

```python
# Execute workflow
orchestrator.execute_workflow(workflow.workflow_id)

# Check status
status = orchestrator.get_workflow_status(workflow.workflow_id)
print(f"Status: {status['status']}")
print(f"Completed tasks: {status['completed_tasks']}/{status['task_count']}")

# Save results
results_dir = orchestrator.save_workflow_results(workflow.workflow_id)
print(f"Results saved to: {results_dir}")
```

## API Reference

### Workflow API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/workflows/` | GET | List all workflows |
| `/api/v1/workflows/` | POST | Create a new workflow |
| `/api/v1/workflows/templates` | GET | List available workflow templates |
| `/api/v1/workflows/from-template` | POST | Create a workflow from a template |
| `/api/v1/workflows/{workflow_id}` | GET | Get workflow details |
| `/api/v1/workflows/{workflow_id}` | DELETE | Delete a workflow |
| `/api/v1/workflows/{workflow_id}/tasks` | POST | Add a task to a workflow |
| `/api/v1/workflows/{workflow_id}/execute` | POST | Execute a workflow |
| `/api/v1/workflows/{workflow_id}/cancel` | POST | Cancel a running workflow |
| `/api/v1/workflows/{workflow_id}/status` | GET | Get workflow execution status |
| `/api/v1/workflows/{workflow_id}/results` | GET | Get workflow results summary |
| `/api/v1/workflows/{workflow_id}/findings` | GET | Get findings from a workflow |
| `/api/v1/workflows/{workflow_id}/export` | GET | Export workflow results |

### Adapter API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/workflows/adapters` | GET | List available adapters |

## Testing and Validation

### Adapter Tester

The `AdapterTest` class provides automated testing for tool adapters. It tests:

- Adapter initialization
- Command generation
- Output parsing
- Execution flow

```python
from backend.modules.integrations.adapter_tester import IntegrationTester

# Create and run tester
tester = IntegrationTester()
tester.run_tests()
tester.print_results()

# Test a specific adapter
tester.run_tests("sqlmap")
tester.print_results()

# Export results
tester.export_results("/path/to/results.json")
```

### Workflow Testing

Workflows can be tested using the `execute_workflow` method with mocked adapters:

```python
# Create test workflow
workflow = orchestrator.create_workflow(
    name="Test Workflow",
    description="Workflow for testing",
    target="test-target"
)

# Add tasks with mock options
orchestrator.add_task(
    workflow_id=workflow.workflow_id,
    adapter_name="nmap",
    adapter_options={"target": "test-target"}
)

# Execute with mock mode
orchestrator.execute_workflow(workflow.workflow_id, mock=True)
```

## Extending the Framework

### Creating New Adapters

To create a new adapter:

1. Create a new Python module in `backend/modules/integrations/`
2. Implement a class that inherits from `BaseToolAdapter`
3. Implement the required methods:
   - `prepare_command(self, options)`
   - `parse_output(self, output)`
4. Register the adapter in `WorkflowOrchestrator._register_adapters()`

Example:

```python
# my_tool_adapter.py
from backend.modules.integrations.adapter_base import BaseToolAdapter, Severity

class MyToolAdapter(BaseToolAdapter):
    def __init__(self, executable_path=None):
        super().__init__("my-tool", executable_path)
    
    def prepare_command(self, options):
        command = f"{self.executable_path}"
        if "target" in options:
            command += f" --target {options['target']}"
        return command
    
    def parse_output(self, output):
        findings = []
        # Parse output into findings
        return findings
```

### Custom Workflow Templates

To create a custom workflow template:

1. Add a new static method to the `WorkflowTemplates` class
2. Define the workflow structure and tasks
3. Return a dictionary with the workflow definition

Example:

```python
@staticmethod
def my_custom_scan(target, options=None):
    opts = options or {}
    
    return {
        "name": "My Custom Security Scan",
        "description": "Custom security testing workflow",
        "target": target,
        "tags": ["custom", "security"],
        "tasks": [
            {
                "adapter_name": "nmap",
                "task_name": "Network Scan",
                "adapter_options": {
                    "target": target,
                    "ports": opts.get("ports", "1-1000")
                }
            },
            # Additional tasks...
        ]
    }
```

## Conclusion

The SecureScout integration framework provides a powerful and flexible way to integrate and orchestrate security testing tools. By following this guide, you can effectively use the existing adapters, create workflows, and extend the framework with new capabilities.