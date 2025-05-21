# Getting Started with SecureScout

This guide will help you get started with SecureScout, from installation to running your first security scan.

## Table of Contents

1. [Installation](#installation)
   - [Docker Installation](#docker-installation)
   - [Manual Installation](#manual-installation)
2. [Initial Configuration](#initial-configuration)
3. [Creating Your First Scan](#creating-your-first-scan)
4. [Understanding Scan Results](#understanding-scan-results)
5. [Generating Reports](#generating-reports)
6. [Next Steps](#next-steps)

## Installation

### Docker Installation

The easiest way to get started with SecureScout is using Docker and Docker Compose.

#### Prerequisites

- Docker 20.10+ 
- Docker Compose 2.0+
- 2GB RAM minimum (4GB recommended)
- 10GB disk space

#### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/aegntic/sec-scout.git
   cd sec-scout
   ```

2. Create a `.env` file from the template:
   ```bash
   cp .env.template .env
   ```

3. Edit the `.env` file with your desired configurations (at minimum, change the default admin password)

4. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

5. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost:8001

### Manual Installation

If you prefer to run the services individually without Docker, follow these steps:

#### Prerequisites

- Python 3.10+
- Node.js 16+
- Redis (for task queue)
- 2GB RAM minimum
- Modern web browser

#### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/aegntic/sec-scout.git
   cd sec-scout
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create necessary directories:
   ```bash
   mkdir -p logs reports data
   ```

5. Start the backend server:
   ```bash
   python -m backend.app
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Start the frontend development server:
   ```bash
   npm start
   ```

## Initial Configuration

After installation, you'll need to set up your initial admin account and configure the system.

### Setting Up Admin Account

1. Access the application at http://localhost (or http://localhost:3000 if using manual installation)
2. You'll be redirected to the setup page if no admin account exists
3. Create your admin account with a strong password
4. Log in with your new admin credentials

### Configuring System Settings

1. Navigate to the Settings page
2. Configure the following settings:
   - **General Settings**: Application name, default scan options
   - **Security Settings**: Password policy, session timeouts
   - **Scan Settings**: Default rate limits, user agent rotation
   - **Notification Settings**: Email alerts, in-app notifications

## Creating Your First Scan

Now that you have SecureScout set up, let's create your first security scan.

1. Navigate to the "New Scan" page
2. Enter the target URL (e.g., https://example.com)
3. Configure scan options:
   - **Scan Type**: Choose between Quick, Standard, or Comprehensive
   - **Modules**: Select which security testing modules to include
   - **Authentication**: Configure authentication if the target requires login
   - **Advanced Options**: Configure request rates, headers, and other options

4. Click "Start Scan" to begin the security assessment
5. You'll be redirected to the Scan Active page to monitor progress

## Understanding Scan Results

As the scan progresses, SecureScout will identify potential vulnerabilities and security issues.

1. The "Active Scan" page shows real-time results as they're discovered
2. Each vulnerability includes:
   - Severity rating (Critical, High, Medium, Low, Info)
   - Vulnerability type and description
   - Affected URL or component
   - Evidence of the vulnerability
   - Remediation suggestions

3. You can filter results by severity, type, or status
4. Click on any vulnerability to see detailed information and evidence

## Generating Reports

Once your scan is complete, you can generate comprehensive security reports.

1. Navigate to the scan results page
2. Click "Generate Report"
3. Select the report format:
   - **HTML**: Interactive web-based report
   - **PDF**: Printable document report
   - **CSV**: Data-friendly format for further analysis
   - **JSON**: Machine-readable format for integrations

4. Choose report options:
   - Include executive summary
   - Include technical details
   - Include remediation recommendations
   - Include evidence screenshots

5. Click "Generate" to create the report
6. Access the report from the Reports page

## Next Steps

Now that you've completed your first scan, here are some next steps to explore:

1. **Configure Regular Scans**: Set up scheduled scans for continuous monitoring
2. **Explore Advanced Features**: Try different scan types and modules
3. **API Integration**: Use the REST API to integrate with your CI/CD pipeline
4. **User Management**: Add additional users with appropriate roles
5. **Custom Scan Profiles**: Create reusable scan configurations for different targets

For more detailed information, refer to the [User Guide](user-guide.md) and [API Documentation](api-docs.md).