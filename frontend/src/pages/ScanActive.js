import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Grid, 
  Button,
  LinearProgress,
  Divider,
  Chip,
  IconButton,
  Card,
  CardContent,
  Alert,
  Tabs,
  Tab,
  CircularProgress
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import StopIcon from '@mui/icons-material/Stop';
import BugReportIcon from '@mui/icons-material/BugReport';
import AssessmentIcon from '@mui/icons-material/Assessment';
import DownloadIcon from '@mui/icons-material/Download';
import { useParams } from 'react-router-dom';
import Terminal from '../components/Terminal';
import VulnerabilityCard from '../components/VulnerabilityCard';

// Mock active scan data
const mockActiveScan = {
  id: 'scan123',
  status: 'running',
  progress: 37,
  target_url: 'https://example.com',
  start_time: '2025-05-18T09:30:15',
  elapsed_time: '00:45:23',
  current_module: 'injection',
  findings: [
    {
      id: 'vuln1',
      title: 'SQL Injection Vulnerability',
      description: 'A SQL injection vulnerability was detected in the search parameter that could allow an attacker to extract data from the database.',
      severity: 'high',
      category: 'Injection',
      location: 'https://example.com/search?q=test',
      cvss: '8.5',
      cwe: '89',
      evidence: "search?q=test' OR 1=1 --",
      evidenceType: 'http',
      impact: 'An attacker could exploit this vulnerability to access, modify, or delete data from the database. This could lead to unauthorized access to sensitive information or complete system compromise.',
      recommendation: 'Use parameterized queries or prepared statements instead of dynamically building SQL queries. Additionally, implement input validation and sanitize user inputs before processing.',
      references: [
        { title: 'OWASP SQL Injection', url: 'https://owasp.org/www-community/attacks/SQL_Injection' },
        { title: 'CWE-89', url: 'https://cwe.mitre.org/data/definitions/89.html' }
      ],
      detectionMethod: 'Automated SQL Injection Testing'
    },
    {
      id: 'vuln2',
      title: 'Missing CSRF Protection',
      description: 'The application does not implement proper Cross-Site Request Forgery (CSRF) protections on state-changing operations.',
      severity: 'medium',
      category: 'CSRF',
      location: 'https://example.com/profile/update',
      cvss: '6.1',
      cwe: '352',
      evidence: "<form method=\"POST\" action=\"/profile/update\">\n  <input type=\"text\" name=\"email\" />\n  <input type=\"submit\" />\n</form>",
      evidenceType: 'html',
      impact: 'An attacker could trick a user into making unwanted state changes to their account or data while they are authenticated. This could lead to account compromise or data manipulation.',
      recommendation: 'Implement proper CSRF token validation for all state-changing operations. Include a unique, secret token with each request and validate it on the server side.',
      references: [
        { title: 'OWASP CSRF Prevention', url: 'https://owasp.org/www-community/attacks/csrf' },
        { title: 'CWE-352', url: 'https://cwe.mitre.org/data/definitions/352.html' }
      ],
      detectionMethod: 'Form Analysis'
    }
  ],
  logs: "[INFO] 2025-05-18 09:30:15 - Starting scan for target: https://example.com\n[INFO] 2025-05-18 09:30:16 - Initializing modules: discovery, authentication, injection, xss, csrf, ssl_tls, headers, cookies\n[INFO] 2025-05-18 09:30:17 - Starting discovery module\n[INFO] 2025-05-18 09:32:45 - Discovered 32 endpoints\n[INFO] 2025-05-18 09:32:46 - Identified technologies: Apache 2.4.41, PHP 7.4, MySQL 5.7, jQuery 3.5.1\n[SUCCESS] 2025-05-18 09:35:21 - Discovery module completed\n[INFO] 2025-05-18 09:35:22 - Starting authentication module\n[INFO] 2025-05-18 09:37:55 - Testing login functionality at /login\n[WARNING] 2025-05-18 09:38:12 - No account lockout detected after 10 failed attempts\n[WARNING] 2025-05-18 09:40:03 - Session cookies missing 'secure' and 'httponly' flags\n[SUCCESS] 2025-05-18 09:45:30 - Authentication module completed\n[INFO] 2025-05-18 09:45:31 - Starting injection module\n[WARNING] 2025-05-18 09:52:17 - Potential SQL injection point detected at /search?q=\n[ERROR] 2025-05-18 09:55:43 - Confirmed SQL injection vulnerability at /search?q=\n[INFO] 2025-05-18 10:12:22 - Testing for NoSQL injection vulnerabilities\n[INFO] 2025-05-18 10:15:38 - Current progress: 37%"
};

// Tab panel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`scan-tabpanel-${index}`}
      aria-labelledby={`scan-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

// Tab props
function tabProps(index) {
  return {
    id: `scan-tab-${index}`,
    'aria-controls': `scan-tabpanel-${index}`,
  };
}

const ScanActive = () => {
  const { scanId } = useParams();
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  
  // Severity counts for summary
  const [severityCounts, setSeverityCounts] = useState({
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    info: 0,
    total: 0
  });
  
  // Terminal log state
  const [logs, setLogs] = useState("");
  const [isRunning, setIsRunning] = useState(true);
  
  // Fetch scan data
  useEffect(() => {
    // Simulate fetching data
    setLoading(true);
    setTimeout(() => {
      setScan(mockActiveScan);
      setLogs(mockActiveScan.logs);
      setIsRunning(mockActiveScan.status === 'running');
      
      // Calculate severity counts
      const counts = {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
        info: 0,
        total: mockActiveScan.findings.length
      };
      
      mockActiveScan.findings.forEach(finding => {
        const severity = finding.severity.toLowerCase();
        if (counts[severity] !== undefined) {
          counts[severity]++;
        }
      });
      
      setSeverityCounts(counts);
      setLoading(false);
    }, 1000);
  }, [scanId]);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // Mock terminal actions
  const handleStartScan = () => {
    setIsRunning(true);
    // In a real app, this would make an API call to resume the scan
  };
  
  const handleStopScan = () => {
    setIsRunning(false);
    // In a real app, this would make an API call to pause the scan
  };
  
  const handleClearLogs = () => {
    setLogs("");
  };
  
  // Simulate log updates
  useEffect(() => {
    let interval;
    if (isRunning) {
      interval = setInterval(() => {
        // Simulate real-time log updates
        setLogs(prevLogs => {
          const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
          return `${prevLogs}\n[INFO] ${timestamp} - Scanning in progress... ${Math.floor(Math.random() * 100) + 1}%`;
        });
      }, 3000);
    }
    
    return () => clearInterval(interval);
  }, [isRunning]);
  
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading scan information...
        </Typography>
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }
  
  if (!scan) {
    return (
      <Container maxWidth="lg" sx={{ mt: 3 }}>
        <Alert severity="info">No scan found with ID: {scanId}</Alert>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Active Scan
        </Typography>
        <Box>
          {scan.status === 'running' ? (
            <Button
              variant="outlined"
              color="warning"
              startIcon={<StopIcon />}
              onClick={handleStopScan}
              sx={{ mr: 2 }}
            >
              Stop Scan
            </Button>
          ) : (
            <Button
              variant="outlined"
              color="primary"
              startIcon={<RefreshIcon />}
              onClick={handleStartScan}
              sx={{ mr: 2 }}
            >
              Resume Scan
            </Button>
          )}
          <Button
            variant="contained"
            color="primary"
            startIcon={<AssessmentIcon />}
          >
            Generate Report
          </Button>
        </Box>
      </Box>
      
      {/* Scan information card */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Target: {scan.target_url}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Scan ID: {scan.id}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Started: {new Date(scan.start_time).toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Elapsed: {scan.elapsed_time}
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body1" sx={{ mr: 1 }}>
                Status:
              </Typography>
              <Chip 
                label={scan.status === 'running' ? 'Running' : 'Paused'} 
                color={scan.status === 'running' ? 'success' : 'warning'} 
                size="small"
              />
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body1" sx={{ mr: 1 }}>
                Current module:
              </Typography>
              <Chip 
                label={scan.current_module}
                color="primary" 
                size="small"
              />
            </Box>
            <Box sx={{ width: '100%', mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Progress: {scan.progress}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={scan.progress} 
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Findings summary */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          <BugReportIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
          Findings Summary
        </Typography>
        
        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={4} sm={2}>
            <Card sx={{ backgroundColor: '#e74c3c', color: 'white', textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h4">{severityCounts.critical}</Typography>
                <Typography variant="body2">Critical</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={4} sm={2}>
            <Card sx={{ backgroundColor: '#e67e22', color: 'white', textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h4">{severityCounts.high}</Typography>
                <Typography variant="body2">High</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={4} sm={2}>
            <Card sx={{ backgroundColor: '#f39c12', color: 'white', textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h4">{severityCounts.medium}</Typography>
                <Typography variant="body2">Medium</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={4} sm={2}>
            <Card sx={{ backgroundColor: '#3498db', color: 'white', textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h4">{severityCounts.low}</Typography>
                <Typography variant="body2">Low</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={4} sm={2}>
            <Card sx={{ backgroundColor: '#95a5a6', color: 'white', textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h4">{severityCounts.info}</Typography>
                <Typography variant="body2">Info</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={4} sm={2}>
            <Card sx={{ backgroundColor: '#2c3e50', color: 'white', textAlign: 'center' }}>
              <CardContent>
                <Typography variant="h4">{severityCounts.total}</Typography>
                <Typography variant="body2">Total</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>
      
      {/* Tabs section */}
      <Paper elevation={3} sx={{ mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="scan detail tabs"
            variant="fullWidth"
          >
            <Tab label="Findings" icon={<BugReportIcon />} iconPosition="start" {...tabProps(0)} />
            <Tab label="Live Terminal" icon={<AssessmentIcon />} iconPosition="start" {...tabProps(1)} />
          </Tabs>
        </Box>
        
        <TabPanel value={tabValue} index={0}>
          {scan.findings.length > 0 ? (
            <Box>
              {scan.findings.map((finding) => (
                <VulnerabilityCard key={finding.id} finding={finding} />
              ))}
            </Box>
          ) : (
            <Alert severity="info">
              No vulnerabilities have been detected yet. Scanning is still in progress.
            </Alert>
          )}
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          <Terminal 
            title="Security Scan Live Terminal"
            logs={logs}
            isRunning={isRunning}
            onStart={handleStartScan}
            onStop={handleStopScan}
            onClear={handleClearLogs}
          />
          
          <Alert severity="info" sx={{ mt: 3 }}>
            <strong>Info:</strong> The terminal displays real-time scanning activity and findings as they're discovered.
          </Alert>
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default ScanActive;