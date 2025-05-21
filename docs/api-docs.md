# SecureScout API Documentation

This document provides a comprehensive reference for the SecureScout REST API, allowing you to integrate security scanning capabilities into your own applications and workflows.

## Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Endpoint Reference](#endpoint-reference)
   - [Authentication Endpoints](#authentication-endpoints)
   - [Scan Endpoints](#scan-endpoints)
   - [Report Endpoints](#report-endpoints)
   - [Configuration Endpoints](#configuration-endpoints)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Examples](#examples)

## API Overview

The SecureScout API is a RESTful API that uses JSON for request and response data. All API requests should be made to the base URL of your SecureScout installation, typically:

```
http://your-securescout-server:8001/api
```

### API Versions

The current API version is v1, which is implicitly used in all endpoints. Future versions may be specified with a version prefix.

### Content Type

All requests should use `application/json` as the Content-Type header.

## Authentication

The API supports two authentication methods:

### JWT Authentication

For interactive applications, use JWT authentication:

1. Obtain access and refresh tokens using the `/api/auth/login` endpoint
2. Include the access token in the `Authorization` header of subsequent requests:
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
3. When the access token expires, use the refresh token to obtain a new one via `/api/auth/refresh`

### API Key Authentication

For automated scripts and integrations, use API key authentication:

1. Generate an API key from the user interface
2. Include the API key in the `X-API-Key` header:
   ```
   X-API-Key: sct_12345abcdef67890...
   ```

## Endpoint Reference

### Authentication Endpoints

#### POST /api/auth/login

Authenticate a user and get access and refresh tokens.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "your-password",
  "mfa_code": "123456"  // Optional, required if MFA is enabled
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "user-uuid",
    "username": "user@example.com",
    "email": "user@example.com",
    "role": "ANALYST"
  }
}
```

#### POST /api/auth/refresh

Refresh an expired access token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST /api/auth/logout

Revoke a refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

#### GET /api/auth/profile

Get the current user's profile.

**Response:**
```json
{
  "id": "user-uuid",
  "username": "user@example.com",
  "email": "user@example.com",
  "role": "ANALYST",
  "active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### Scan Endpoints

#### POST /api/scan/start

Start a new security scan.

**Request Body:**
```json
{
  "target_url": "https://example.com",
  "scan_type": "comprehensive",
  "modules": ["discovery", "authentication", "injection", "xss", "csrf"],
  "max_depth": 3,
  "max_pages": 100,
  "threads": 10,
  "request_delay": 0.5,
  "jitter": 0.2,
  "user_agent_rotation": true,
  "ip_rotation": false,
  "custom_headers": {
    "X-Custom-Header": "value"
  },
  "custom_cookies": {
    "session": "value"
  },
  "authentication": {
    "type": "form",
    "url": "https://example.com/login",
    "username_field": "username",
    "password_field": "password",
    "username": "test_user",
    "password": "test_password"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Scan initiated successfully",
  "scan_id": "scan-uuid",
  "config": {
    "id": "scan-uuid",
    "target_url": "https://example.com",
    "scan_type": "comprehensive",
    "start_time": "2023-01-01T00:00:00Z",
    "status": "queued",
    "progress": 0
  }
}
```

#### GET /api/scan/status/{scan_id}

Get the status of a running scan.

**Response:**
```json
{
  "scan_id": "scan-uuid",
  "status": "running",
  "progress": 45,
  "target_url": "https://example.com",
  "start_time": "2023-01-01T00:00:00Z",
  "elapsed_time": "00:10:30",
  "findings_count": 12
}
```

#### GET /api/scan/list

List all scans (active and historical).

**Response:**
```json
{
  "active_scans": [
    {
      "id": "scan-uuid-1",
      "target_url": "https://example.com",
      "scan_type": "comprehensive",
      "start_time": "2023-01-01T00:00:00Z",
      "status": "running",
      "progress": 45
    }
  ],
  "scan_history": [
    {
      "id": "scan-uuid-2",
      "target_url": "https://example2.com",
      "scan_type": "quick",
      "start_time": "2022-12-31T00:00:00Z",
      "status": "completed"
    }
  ]
}
```

#### POST /api/scan/stop/{scan_id}

Stop a running scan.

**Response:**
```json
{
  "status": "success",
  "message": "Scan scan-uuid is being stopped"
}
```

#### DELETE /api/scan/delete/{scan_id}

Delete scan data and results.

**Response:**
```json
{
  "status": "success",
  "message": "Scan scan-uuid deleted successfully"
}
```

### Report Endpoints

#### POST /api/report/generate/{scan_id}

Generate a report for a completed scan.

**Request Body:**
```json
{
  "format": "pdf",
  "include_executive_summary": true,
  "include_technical_details": true,
  "include_remediation": true,
  "include_evidence": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Report generation started",
  "report_id": "report-uuid",
  "estimated_completion": "2023-01-01T00:05:00Z"
}
```

#### GET /api/report/list

List all generated reports.

**Response:**
```json
{
  "reports": [
    {
      "id": "report-uuid",
      "scan_id": "scan-uuid",
      "format": "pdf",
      "created_at": "2023-01-01T00:05:00Z",
      "file_size": 1024,
      "target_url": "https://example.com"
    }
  ]
}
```

#### GET /api/report/download/{filename}

Download a generated report.

**Response:**
The report file with appropriate Content-Type header.

#### DELETE /api/report/delete/{filename}

Delete a report.

**Response:**
```json
{
  "status": "success",
  "message": "Report deleted successfully"
}
```

### Configuration Endpoints

#### GET /api/config/profiles

Get all scan profiles.

**Response:**
```json
{
  "profiles": [
    {
      "id": "profile-uuid",
      "name": "Standard Web Application",
      "description": "Standard profile for web applications",
      "scan_type": "standard",
      "modules": ["discovery", "authentication", "injection", "xss", "csrf"],
      "created_at": "2023-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /api/config/profiles/{profile_id}

Get a specific scan profile.

**Response:**
```json
{
  "id": "profile-uuid",
  "name": "Standard Web Application",
  "description": "Standard profile for web applications",
  "scan_type": "standard",
  "modules": ["discovery", "authentication", "injection", "xss", "csrf"],
  "max_depth": 3,
  "max_pages": 100,
  "threads": 10,
  "request_delay": 0.5,
  "jitter": 0.2,
  "user_agent_rotation": true,
  "ip_rotation": false,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### POST /api/config/profiles

Create a new scan profile.

**Request Body:**
```json
{
  "name": "Custom Profile",
  "description": "Custom profile for e-commerce applications",
  "scan_type": "comprehensive",
  "modules": ["discovery", "authentication", "injection", "xss", "csrf"],
  "max_depth": 5,
  "max_pages": 200,
  "threads": 15,
  "request_delay": 0.3,
  "jitter": 0.1,
  "user_agent_rotation": true,
  "ip_rotation": false
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Profile created successfully",
  "profile": {
    "id": "profile-uuid",
    "name": "Custom Profile",
    "description": "Custom profile for e-commerce applications",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

#### PUT /api/config/profiles/{profile_id}

Update a scan profile.

**Request Body:**
```json
{
  "name": "Updated Profile",
  "description": "Updated description",
  "scan_type": "standard"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Profile updated successfully",
  "profile": {
    "id": "profile-uuid",
    "name": "Updated Profile",
    "description": "Updated description",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

#### DELETE /api/config/profiles/{profile_id}

Delete a scan profile.

**Response:**
```json
{
  "status": "success",
  "message": "Profile deleted successfully"
}
```

#### GET /api/config/modules

Get all available security testing modules.

**Response:**
```json
{
  "modules": [
    {
      "id": "discovery",
      "name": "Discovery & Enumeration",
      "description": "Crawls the target and discovers its structure",
      "enabled": true
    },
    {
      "id": "authentication",
      "name": "Authentication Testing",
      "description": "Tests authentication mechanisms for weaknesses",
      "enabled": true
    }
  ]
}
```

## Error Handling

The API uses standard HTTP status codes to indicate success or failure:

- 200 OK: Request succeeded
- 201 Created: Resource created successfully
- 400 Bad Request: Invalid request parameters
- 401 Unauthorized: Authentication failed
- 403 Forbidden: Permission denied
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server-side error

Error responses have the following format:

```json
{
  "error": "Error message describing the issue"
}
```

## Rate Limiting

API requests are subject to rate limiting to prevent abuse. The current limits are:

- 60 requests per minute for authenticated users
- 10 requests per minute for unauthenticated requests

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1609459200
```

When a rate limit is exceeded, a 429 Too Many Requests response is returned.

## Examples

### Starting a Scan with cURL

```bash
curl -X POST http://localhost:8001/api/scan/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "target_url": "https://example.com",
    "scan_type": "standard",
    "modules": ["discovery", "authentication", "injection", "xss"]
  }'
```

### Starting a Scan with Python

```python
import requests
import json

url = "http://localhost:8001/api/scan/start"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
}
data = {
    "target_url": "https://example.com",
    "scan_type": "standard",
    "modules": ["discovery", "authentication", "injection", "xss"]
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print(response.json())
```

### Integration with CI/CD Pipeline

Example GitHub Actions workflow:

```yaml
name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  securescout-scan:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v2
    
    - name: Deploy test environment
      run: ./deploy-test-env.sh
    
    - name: Run SecureScout Scan
      run: |
        curl -X POST http://your-securescout-server:8001/api/scan/start \
          -H "Content-Type: application/json" \
          -H "X-API-Key: YOUR_API_KEY" \
          -d '{
            "target_url": "http://test-env:8080",
            "scan_type": "standard"
          }' > scan_result.json
        
        # Extract scan_id from response
        SCAN_ID=$(jq -r '.scan_id' scan_result.json)
        
        # Poll for scan completion
        while true; do
          STATUS=$(curl -s -H "X-API-Key: YOUR_API_KEY" \
            http://your-securescout-server:8001/api/scan/status/$SCAN_ID | jq -r '.status')
          
          if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
            break
          fi
          
          sleep 30
        done
        
        # Generate report
        curl -X POST \
          -H "Content-Type: application/json" \
          -H "X-API-Key: YOUR_API_KEY" \
          http://your-securescout-server:8001/api/report/generate/$SCAN_ID \
          -d '{"format": "json"}' > report_info.json
        
        # Fail if critical vulnerabilities found
        CRITICAL_COUNT=$(curl -s -H "X-API-Key: YOUR_API_KEY" \
          http://your-securescout-server:8001/api/scan/status/$SCAN_ID | \
          jq -r '.vulnerabilities.critical')
        
        if [ "$CRITICAL_COUNT" -gt 0 ]; then
          echo "Critical vulnerabilities detected!"
          exit 1
        fi
```