# SecureScout Troubleshooting Guide

This guide provides solutions for common issues you might encounter when using SecureScout.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Docker Deployment Issues](#docker-deployment-issues)
3. [Authentication Issues](#authentication-issues)
4. [Scanning Issues](#scanning-issues)
5. [Reporting Issues](#reporting-issues)
6. [Performance Issues](#performance-issues)
7. [Integration Issues](#integration-issues)
8. [Log Analysis](#log-analysis)
9. [Contacting Support](#contacting-support)

## Installation Issues

### Backend Installation Fails

**Symptoms:** Python dependency installation errors or backend fails to start.

**Potential Solutions:**

1. **Dependency conflicts:**
   ```bash
   # Create a fresh virtual environment
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Missing system packages:**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev
   
   # On CentOS/RHEL
   sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel
   ```

3. **Python version incompatibility:**
   - Ensure you're using Python 3.10 or newer
   - Check version with `python --version`

### Frontend Installation Fails

**Symptoms:** Node.js dependency installation errors or frontend fails to start.

**Potential Solutions:**

1. **Clear npm cache:**
   ```bash
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Node.js version issues:**
   - Ensure you're using Node.js 16 or newer
   - Consider using NVM to manage Node.js versions:
     ```bash
     nvm install 16
     nvm use 16
     ```

3. **Build errors:**
   - Check for specific error messages in the console
   - Try running with verbose logging:
     ```bash
     npm run build --verbose
     ```

## Docker Deployment Issues

### Containers Fail to Start

**Symptoms:** Docker containers don't start or exit immediately after starting.

**Potential Solutions:**

1. **Check Docker logs:**
   ```bash
   docker-compose logs
   # For a specific service
   docker-compose logs backend
   ```

2. **Permission issues:**
   - Ensure the data/logs/reports directories have correct permissions:
     ```bash
     mkdir -p data logs reports
     chmod 755 data logs reports
     ```

3. **Port conflicts:**
   - Check if ports 80 and 8001 are already in use:
     ```bash
     netstat -tulpn | grep -E '8001|80'
     # If ports are in use, modify docker-compose.yml to use different ports
     ```

4. **Memory issues:**
   - Check available memory:
     ```bash
     free -m
     ```
   - If low on memory, increase swap space or allocate more memory to Docker

### Docker Volume Issues

**Symptoms:** Data persistence issues between container restarts.

**Potential Solutions:**

1. **Check volume mounts:**
   ```bash
   docker-compose config
   # Look for the 'volumes:' section to ensure paths are correct
   ```

2. **Clean and recreate volumes:**
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

## Authentication Issues

### Login Failures

**Symptoms:** Unable to log in with correct credentials.

**Potential Solutions:**

1. **Check default admin credentials:**
   - Default username: admin
   - Default password: Check your .env file for DEFAULT_ADMIN_PASSWORD

2. **Reset admin password:**
   ```bash
   docker exec -it securescout-backend python -c "from modules.auth.auth_manager import get_memory_manager; m = get_memory_manager(); user_manager = m.user_manager; user_manager.reset_password('admin', 'NewPassword123!')"
   ```

3. **JWT secret key issues:**
   - Ensure JWT_SECRET_KEY is properly set in your .env file
   - If changed, you'll need to log in again as existing tokens will be invalid

### Token Refresh Issues

**Symptoms:** Constantly being logged out or redirected to login page.

**Potential Solutions:**

1. **Check browser cookies and localStorage:**
   - Clear browser storage and try again
   - Check browser console for related errors

2. **Check time synchronization:**
   - Ensure server time is correct, as JWT validation is time-sensitive
   - Synchronize NTP on your server:
     ```bash
     sudo apt-get install ntp
     sudo systemctl restart ntp
     ```

## Scanning Issues

### Scan Doesn't Start

**Symptoms:** Scan creation appears successful but scan doesn't start processing.

**Potential Solutions:**

1. **Check target accessibility:**
   - Ensure the target URL is accessible from the SecureScout server
   - Test with a simple curl request:
     ```bash
     curl -I https://target-url.com
     ```

2. **Check scan queue:**
   - Verify Redis is running:
     ```bash
     docker-compose exec redis redis-cli ping
     ```
   - Check scan queue status:
     ```bash
     docker-compose exec redis redis-cli LLEN scan_queue
     ```

3. **Review backend logs:**
   ```bash
   docker-compose logs --tail=100 backend
   ```

### Scan Stalls or Gets Stuck

**Symptoms:** Scan progress stops advancing but scan hasn't completed or failed.

**Potential Solutions:**

1. **Adjust scan rate limitations:**
   - Reduce concurrency settings
   - Increase request delay
   - Try again with a smaller scope

2. **Check target website performance:**
   - The target site might be throttling or blocking requests
   - Try enabling stealth mode options
   - Add delays between requests

3. **Restart the scan:**
   - Stop the current scan
   - Configure a new scan with more conservative settings

### False Positives

**Symptoms:** Scan reports vulnerabilities that don't actually exist.

**Potential Solutions:**

1. **Review vulnerability details carefully:**
   - Check the evidence provided
   - Test manually to confirm

2. **Adjust vulnerability detection thresholds:**
   - Edit scan configuration to increase confidence thresholds
   - Select more specific testing modules

3. **Mark as false positive in the UI:**
   - This helps the system learn and improve over time

## Reporting Issues

### Report Generation Fails

**Symptoms:** Unable to generate reports from completed scans.

**Potential Solutions:**

1. **Check disk space:**
   ```bash
   df -h
   ```

2. **Verify report directory permissions:**
   ```bash
   ls -la reports/
   # Should show write permissions for the user running the container
   ```

3. **Check backend logs for specific errors:**
   ```bash
   docker-compose logs --tail=100 backend | grep -i "report"
   ```

### Missing Information in Reports

**Symptoms:** Generated reports are missing expected information or sections.

**Potential Solutions:**

1. **Check report configuration:**
   - Ensure all needed sections are enabled during report generation

2. **Verify scan completion:**
   - Make sure the scan fully completed and didn't terminate early
   - Check scan status shows 100% completion

3. **Try different report format:**
   - If one format has issues, try generating in a different format

## Performance Issues

### Slow Web Interface

**Symptoms:** Dashboard and UI elements load slowly or time out.

**Potential Solutions:**

1. **Check system resources:**
   ```bash
   top
   # Look for high CPU or memory usage
   ```

2. **Optimize browser:**
   - Clear browser cache
   - Disable unnecessary extensions
   - Try a different browser

3. **Check network latency:**
   - Ensure good connectivity between your browser and the server
   - If accessing remotely, consider using SSH tunneling:
     ```bash
     ssh -L 8080:localhost:80 user@securescout-server
     # Then access through http://localhost:8080
     ```

### Slow Scanning Performance

**Symptoms:** Scans take longer than expected to complete.

**Potential Solutions:**

1. **Optimize scan configuration:**
   - Reduce scan scope (max pages, max depth)
   - Focus on specific vulnerability types
   - Use a faster scan profile

2. **Allocate more resources:**
   - If using Docker, increase container resource limits
   - Upgrade server hardware if possible

3. **Check network conditions:**
   - Verify bandwidth between scanner and target
   - Rule out network congestion or throttling

## Integration Issues

### API Request Failures

**Symptoms:** API requests return errors or unexpected results.

**Potential Solutions:**

1. **Verify authentication:**
   - Check that your API key or JWT token is valid
   - Ensure correct permissions are associated with the token/key

2. **Check request format:**
   - Ensure correct HTTP method (GET, POST, etc.)
   - Validate request headers, especially Content-Type
   - Verify JSON payload format

3. **Review API documentation:**
   - Confirm endpoint paths and required parameters
   - Check for any recent API changes in the changelog

### CI/CD Integration Issues

**Symptoms:** SecureScout fails to integrate with CI/CD pipelines.

**Potential Solutions:**

1. **Verify API key permissions:**
   - API key needs appropriate scan permissions

2. **Check SecureScout server accessibility:**
   - CI/CD server needs network access to SecureScout

3. **Debug CI/CD pipeline:**
   - Add verbose logging to integration scripts
   - Test API calls manually before CI/CD integration

## Log Analysis

Understanding SecureScout logs is crucial for troubleshooting:

### Backend Logs

Backend logs are located in the `/logs` directory or can be viewed with:

```bash
docker-compose logs backend
```

Common log patterns:

- `ERROR` messages indicate serious issues that need attention
- `WARNING` messages highlight potential problems
- `INFO` messages provide status information

### Frontend Console Logs

Check your browser's developer console for frontend errors:

1. Open browser developer tools (F12 or Ctrl+Shift+I)
2. Navigate to the Console tab
3. Look for errors or warnings related to SecureScout

## Contacting Support

If you can't resolve an issue using this guide:

1. **Create a GitHub Issue:**
   - Provide detailed system information
   - Include relevant logs
   - Describe steps to reproduce the issue
   - Specify SecureScout version

2. **Community Support:**
   - Search existing issues for similar problems
   - Check the project wiki for emerging solutions
   - Ask in the community forum or discussion area

3. **For Security Issues:**
   - Do not post potential security vulnerabilities publicly
   - Follow the responsible disclosure process in SECURITY.md