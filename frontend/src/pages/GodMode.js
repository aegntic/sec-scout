import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Chip,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Switch,
  FormControlLabel,
  Tooltip,
  IconButton,
  Badge,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import {
  Security,
  BugReport,
  Psychology,
  Memory,
  Dns,
  Lock,
  Speed,
  Timeline,
  Warning,
  Error,
  CheckCircle,
  Cancel,
  Visibility,
  VisibilityOff,
  PlayArrow,
  Stop,
  Refresh,
  Assessment,
  TrendingUp,
  Shield,
  Code,
  NetworkCheck,
  Storage,
  CloudSync,
  ExpandMore
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';

function GodMode() {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [selectedOperation, setSelectedOperation] = useState('');
  const [operationRunning, setOperationRunning] = useState(false);
  const [operationResults, setOperationResults] = useState(null);
  const [clientTierAssessment, setClientTierAssessment] = useState(null);
  const [stealthLevel, setStealthLevel] = useState('ghost_tier');
  const [testingProfile, setTestingProfile] = useState('red_team_exercise');
  const [targetUrl, setTargetUrl] = useState('');
  const [targetIndustry, setTargetIndustry] = useState('technology');
  const [operationalConfig, setOperationalConfig] = useState(null);
  const [threatIntelligence, setThreatIntelligence] = useState(null);
  const [toolResults, setToolResults] = useState([]);
  const [fuzzingResults, setFuzzingResults] = useState([]);
  const [operationSteps, setOperationSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState(null);

  const operationTypes = [
    {
      id: 'elite_assessment',
      name: 'Elite Security Assessment',
      description: 'Comprehensive elite-level security assessment with all real components',
      icon: <Security />,
      severity: 'high'
    },
    {
      id: 'threat_intelligence',
      name: 'Threat Intelligence Analysis',
      description: 'Real APT attack pattern analysis based on MITRE ATT&CK',
      icon: <Psychology />,
      severity: 'medium'
    },
    {
      id: 'advanced_fuzzing',
      name: 'Advanced Fuzzing Campaign',
      description: 'Genetic algorithm fuzzing with real mutations',
      icon: <BugReport />,
      severity: 'medium'
    },
    {
      id: 'stealth_assessment',
      name: 'Stealth Capability Test',
      description: 'Ghost-tier stealth and evasion testing',
      icon: <Visibility />,
      severity: 'high'
    },
    {
      id: 'tool_integration',
      name: 'Multi-Tool Assessment',
      description: 'Real security tool integration (Nmap, Nikto, Nuclei, SQLMap)',
      icon: <NetworkCheck />,
      severity: 'medium'
    }
  ];

  const stealthLevels = [
    { value: 'overt', label: 'Overt', description: 'Open testing, no evasion' },
    { value: 'covert', label: 'Covert', description: 'Basic evasion techniques' },
    { value: 'stealth', label: 'Stealth', description: 'Advanced evasion techniques' },
    { value: 'ghost', label: 'Ghost', description: 'Maximum stealth, nation-state level' }
  ];

  const testingProfiles = [
    { value: 'compliance_audit', label: 'Compliance Audit' },
    { value: 'vulnerability_assessment', label: 'Vulnerability Assessment' },
    { value: 'penetration_test', label: 'Penetration Test' },
    { value: 'red_team_exercise', label: 'Red Team Exercise' },
    { value: 'threat_hunting', label: 'Threat Hunting' }
  ];

  const industries = [
    'technology', 'financial', 'healthcare', 'government', 'defense',
    'retail', 'manufacturing', 'education', 'energy', 'telecommunications'
  ];

  const executeOperation = async () => {
    if (!targetUrl || !selectedOperation) {
      setError('Please provide target URL and select an operation');
      return;
    }

    setOperationRunning(true);
    setError(null);
    setOperationResults(null);
    setCurrentStep(0);

    const targetInfo = {
      target_url: targetUrl,
      domain: new URL(targetUrl).hostname,
      industry: targetIndustry,
      infrastructure_indicators: ['cloud_native', 'cdn_usage'],
      security_indicators: ['hsts_enabled', 'security_headers']
    };

    try {
      let response;
      
      if (selectedOperation === 'elite_assessment') {
        setOperationSteps([
          'Client Tier Assessment',
          'TLS Reconnaissance', 
          'Threat Intelligence Analysis',
          'Multi-Tool Assessment',
          'Advanced Fuzzing',
          'Stealth Assessment',
          'Final Analysis'
        ]);

        response = await fetch('/api/godmode/execute-elite-assessment', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ target_info: targetInfo })
        });
      } else {
        // Handle other operation types
        response = await fetch(`/api/godmode/${selectedOperation}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            target_info: targetInfo,
            stealth_level: stealthLevel,
            testing_profile: testingProfile
          })
        });
      }

      if (!response.ok) {
        throw new Error(`Operation failed: ${response.statusText}`);
      }

      const results = await response.json();
      setOperationResults(results);
      
      // Extract specific result types
      if (results.client_tier_assessment) {
        setClientTierAssessment(results.client_tier_assessment);
      }
      if (results.operational_parameters) {
        setOperationalConfig(results.operational_parameters);
      }
      if (results.threat_modeling) {
        setThreatIntelligence(results.threat_modeling);
      }
      if (results.tool_integration_results) {
        setToolResults(Object.entries(results.tool_integration_results));
      }
      if (results.advanced_fuzzing_results) {
        setFuzzingResults(Object.entries(results.advanced_fuzzing_results));
      }

    } catch (err) {
      setError(`Operation failed: ${err.message}`);
    } finally {
      setOperationRunning(false);
    }
  };

  const getOperationIcon = (operationId) => {
    const operation = operationTypes.find(op => op.id === operationId);
    return operation ? operation.icon : <Security />;
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return theme.palette.error.main;
      case 'high': return theme.palette.warning.main;
      case 'medium': return theme.palette.info.main;
      case 'low': return theme.palette.success.main;
      default: return theme.palette.grey[500];
    }
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`godmode-tabpanel-${index}`}
      aria-labelledby={`godmode-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Shield sx={{ fontSize: 40, mr: 2, color: theme.palette.primary.main }} />
          <Box>
            <Typography variant="h4" component="h1" sx={{ color: theme.palette.primary.main, fontWeight: 'bold' }}>
              GODMODE - Elite Security Testing
            </Typography>
            <Typography variant="subtitle1" sx={{ color: theme.palette.text.secondary }}>
              Real components, professional-grade testing, zero simulations
            </Typography>
          </Box>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          <Typography variant="body2">{error}</Typography>
        </Alert>
      )}

      <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Configuration" icon={<Speed />} />
        <Tab label="Operations" icon={<Security />} />
        <Tab label="Results" icon={<Assessment />} />
        <Tab label="Intelligence" icon={<Psychology />} />
      </Tabs>

      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <NetworkCheck sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Target Configuration
                </Typography>
                <TextField
                  fullWidth
                  label="Target URL"
                  value={targetUrl}
                  onChange={(e) => setTargetUrl(e.target.value)}
                  placeholder="https://example.com"
                  sx={{ mb: 2 }}
                  error={!targetUrl && operationRunning}
                  helperText={!targetUrl && operationRunning ? "Target URL is required" : ""}
                />
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Industry</InputLabel>
                  <Select
                    value={targetIndustry}
                    onChange={(e) => setTargetIndustry(e.target.value)}
                  >
                    {industries.map(industry => (
                      <MenuItem key={industry} value={industry}>
                        {industry.charAt(0).toUpperCase() + industry.slice(1)}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Lock sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Operational Parameters
                </Typography>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Stealth Level</InputLabel>
                  <Select
                    value={stealthLevel}
                    onChange={(e) => setStealthLevel(e.target.value)}
                  >
                    {stealthLevels.map(level => (
                      <MenuItem key={level.value} value={level.value}>
                        <Tooltip title={level.description} placement="right">
                          <span>{level.label}</span>
                        </Tooltip>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <FormControl fullWidth>
                  <InputLabel>Testing Profile</InputLabel>
                  <Select
                    value={testingProfile}
                    onChange={(e) => setTestingProfile(e.target.value)}
                  >
                    {testingProfiles.map(profile => (
                      <MenuItem key={profile.value} value={profile.value}>
                        {profile.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>

          {clientTierAssessment && (
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <TrendingUp sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Client Tier Assessment
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Chip
                        label={`Tier: ${clientTierAssessment.tier}`}
                        color="primary"
                        variant="outlined"
                        icon={<Shield />}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Chip
                        label={`Sophistication: ${(clientTierAssessment.technical_sophistication * 100).toFixed(0)}%`}
                        color="info"
                        variant="outlined"
                        icon={<Code />}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Chip
                        label={`Security Maturity: ${(clientTierAssessment.security_maturity * 100).toFixed(0)}%`}
                        color="success"
                        variant="outlined"
                        icon={<Security />}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Chip
                        label={clientTierAssessment.threat_landscape}
                        color="warning"
                        variant="outlined"
                        icon={<Warning />}
                      />
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          {operationTypes.map((operation) => (
            <Grid item xs={12} sm={6} md={4} key={operation.id}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  border: selectedOperation === operation.id ? 2 : 1,
                  borderColor: selectedOperation === operation.id ? theme.palette.primary.main : 'transparent',
                  '&:hover': { boxShadow: 6 }
                }}
                onClick={() => setSelectedOperation(operation.id)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {operation.icon}
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      {operation.name}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    {operation.description}
                  </Typography>
                  <Chip
                    size="small"
                    label={operation.severity}
                    sx={{ 
                      mt: 1,
                      backgroundColor: getSeverityColor(operation.severity),
                      color: 'white'
                    }}
                  />
                </CardContent>
              </Card>
            </Grid>
          ))}

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6">
                    Execute Operation
                  </Typography>
                  <Button
                    variant="contained"
                    onClick={executeOperation}
                    disabled={operationRunning || !selectedOperation || !targetUrl}
                    startIcon={operationRunning ? <CircularProgress size={20} /> : <PlayArrow />}
                    sx={{ minWidth: 120 }}
                  >
                    {operationRunning ? 'Running...' : 'Execute'}
                  </Button>
                </Box>

                {operationRunning && operationSteps.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Operation Progress:
                    </Typography>
                    <Stepper activeStep={currentStep} orientation="vertical">
                      {operationSteps.map((step, index) => (
                        <Step key={step}>
                          <StepLabel>{step}</StepLabel>
                        </Step>
                      ))}
                    </Stepper>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={activeTab} index={2}>
        {operationResults ? (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <CheckCircle sx={{ mr: 1, verticalAlign: 'middle', color: 'success.main' }} />
                    Operation Complete
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Operation ID: {operationResults.operation_id}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Duration: {operationResults.duration || 'N/A'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {toolResults.length > 0 && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <NetworkCheck sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Security Tool Results
                    </Typography>
                    <TableContainer>
                      <Table>
                        <TableHead>
                          <TableRow>
                            <TableCell>Tool</TableCell>
                            <TableCell>Findings</TableCell>
                            <TableCell>Severity Distribution</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {toolResults.map(([tool, findings]) => (
                            <TableRow key={tool}>
                              <TableCell>
                                <Chip label={tool.toUpperCase()} variant="outlined" />
                              </TableCell>
                              <TableCell>{findings.length}</TableCell>
                              <TableCell>
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                  {[4, 3, 2, 1].map(severity => {
                                    const count = findings.filter(f => f.severity === severity).length;
                                    return count > 0 ? (
                                      <Chip
                                        key={severity}
                                        size="small"
                                        label={count}
                                        sx={{ 
                                          backgroundColor: getSeverityColor(['info', 'low', 'medium', 'high', 'critical'][severity]),
                                          color: 'white'
                                        }}
                                      />
                                    ) : null;
                                  })}
                                </Box>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {fuzzingResults.length > 0 && (
              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      <BugReport sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Advanced Fuzzing Results
                    </Typography>
                    {fuzzingResults.map(([strategy, results]) => (
                      <Accordion key={strategy}>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Typography>{strategy.replace(/_/g, ' ').toUpperCase()}</Typography>
                          <Chip 
                            size="small" 
                            label={`${results.length} payloads`} 
                            sx={{ ml: 2 }}
                          />
                        </AccordionSummary>
                        <AccordionDetails>
                          <List>
                            {results.slice(0, 5).map((result, index) => (
                              <ListItem key={index}>
                                <ListItemText
                                  primary={`Payload: ${result.payload.substring(0, 50)}...`}
                                  secondary={`Success Probability: ${(result.success_probability * 100).toFixed(1)}%`}
                                />
                                <Chip
                                  size="small"
                                  label={`${result.response_code}`}
                                  color={result.response_code === 200 ? 'success' : 'error'}
                                />
                              </ListItem>
                            ))}
                          </List>
                        </AccordionDetails>
                      </Accordion>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        ) : (
          <Alert severity="info">
            No operation results available. Run an operation to see results here.
          </Alert>
        )}
      </TabPanel>

      <TabPanel value={activeTab} index={3}>
        {threatIntelligence ? (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <Psychology sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Attack Pattern Analysis
                  </Typography>
                  {threatIntelligence.attack_pattern && (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Threat Actor: {threatIntelligence.attack_pattern.actor}
                      </Typography>
                      <Typography variant="body2" color="textSecondary" gutterBottom>
                        Target Type: {threatIntelligence.attack_pattern.target_type}
                      </Typography>
                      <List>
                        {threatIntelligence.attack_pattern.attack_chain?.slice(0, 3).map((phase, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              <Timeline />
                            </ListItemIcon>
                            <ListItemText
                              primary={phase.phase}
                              secondary={`${phase.technique} - ${phase.method}`}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    <Memory sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Technique Implementation
                  </Typography>
                  {threatIntelligence.technique_implementation && (
                    <List>
                      {Object.entries(threatIntelligence.technique_implementation).map(([technique, result]) => (
                        <ListItem key={technique}>
                          <ListItemText
                            primary={technique.replace(/_/g, ' ').toUpperCase()}
                            secondary={`Attempts: ${result.payloads_tested || result.exploitation_attempts?.length || 0}`}
                          />
                          <Chip
                            size="small"
                            label={result.vulnerable ? 'Vulnerable' : 'Secure'}
                            color={result.vulnerable ? 'error' : 'success'}
                          />
                        </ListItem>
                      ))}
                    </List>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        ) : (
          <Alert severity="info">
            No threat intelligence data available. Run a threat intelligence analysis to see data here.
          </Alert>
        )}
      </TabPanel>
    </Box>
  );
}

export default GodMode;