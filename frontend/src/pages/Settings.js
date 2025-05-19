import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Grid, 
  TextField, 
  Button, 
  Switch, 
  FormControlLabel, 
  Divider, 
  Alert, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails,
  Tabs,
  Tab,
  Card,
  CardContent,
  CardActions,
  MenuItem,
  CircularProgress,
  Slider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  InputAdornment,
  Tooltip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import LockIcon from '@mui/icons-material/Lock';
import SecurityIcon from '@mui/icons-material/Security';
import BuildIcon from '@mui/icons-material/Build';
import NotificationsIcon from '@mui/icons-material/Notifications';
import StorageIcon from '@mui/icons-material/Storage';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

// Tab panel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
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
    id: `settings-tab-${index}`,
    'aria-controls': `settings-tabpanel-${index}`,
  };
}

// Mock data for scan profiles
const mockProfiles = [
  {
    id: 'passive',
    name: 'Passive Scan',
    description: 'Non-intrusive information gathering only',
    isBuiltIn: true,
    settings: {
      modules: ['discovery', 'ssl_tls', 'headers', 'cookies'],
      max_depth: 2,
      max_pages: 100,
      threads: 5,
      request_delay: 1.0,
      user_agent_rotation: true,
      ip_rotation: false,
      stealth_level: 'high'
    }
  },
  {
    id: 'standard',
    name: 'Standard Scan',
    description: 'Balanced security testing with moderate intrusiveness',
    isBuiltIn: true,
    settings: {
      modules: ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 'headers', 'cookies', 'sensitive_data'],
      max_depth: 3,
      max_pages: 200,
      threads: 10,
      request_delay: 0.5,
      user_agent_rotation: true,
      ip_rotation: false,
      stealth_level: 'medium'
    }
  },
  {
    id: 'aggressive',
    name: 'Aggressive Scan',
    description: 'Comprehensive security testing with high intrusiveness',
    isBuiltIn: true,
    settings: {
      modules: ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 'headers', 'cookies', 'sensitive_data', 'brute_force', 'dos_simulation', 'file_inclusion', 'command_injection', 'deserialization'],
      max_depth: 5,
      max_pages: 500,
      threads: 20,
      request_delay: 0.1,
      user_agent_rotation: true,
      ip_rotation: true,
      stealth_level: 'low'
    }
  },
  {
    id: 'stealth',
    name: 'Stealth Scan',
    description: 'Maximum evasion techniques with balanced testing',
    isBuiltIn: true,
    settings: {
      modules: ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 'headers', 'cookies', 'sensitive_data'],
      max_depth: 3,
      max_pages: 200,
      threads: 3,
      request_delay: 3.0,
      user_agent_rotation: true,
      ip_rotation: true,
      stealth_level: 'maximum'
    }
  },
  {
    id: 'custom-api',
    name: 'API Security Testing',
    description: 'Custom profile for API security testing',
    isBuiltIn: false,
    settings: {
      modules: ['discovery', 'authentication', 'injection', 'sensitive_data'],
      max_depth: 2,
      max_pages: 150,
      threads: 8,
      request_delay: 0.3,
      user_agent_rotation: true,
      ip_rotation: false,
      stealth_level: 'medium'
    }
  }
];

// Mock data for available modules
const availableModules = [
  { id: 'discovery', name: 'Discovery & Enumeration', description: 'Identifies application structure, endpoints, and technologies' },
  { id: 'authentication', name: 'Authentication Testing', description: 'Tests for authentication vulnerabilities like weak passwords, session management issues' },
  { id: 'injection', name: 'Injection Vulnerabilities', description: 'Tests for SQL, NoSQL, and other injection attacks' },
  { id: 'xss', name: 'Cross-Site Scripting (XSS)', description: 'Tests for reflected, stored, and DOM-based XSS vulnerabilities' },
  { id: 'csrf', name: 'Cross-Site Request Forgery', description: 'Tests for CSRF vulnerabilities in forms and state-changing operations' },
  { id: 'ssl_tls', name: 'SSL/TLS Analysis', description: 'Analyzes SSL/TLS configuration and identifies weaknesses' },
  { id: 'headers', name: 'HTTP Headers Analysis', description: 'Tests for missing or misconfigured security headers' },
  { id: 'cookies', name: 'Cookie Analysis', description: 'Tests for insecure cookie configurations' },
  { id: 'sensitive_data', name: 'Sensitive Data Exposure', description: 'Identifies potentially exposed sensitive information' },
  { id: 'brute_force', name: 'Brute Force Testing', description: 'Tests resistance to brute force attacks on login and other forms' },
  { id: 'dos_simulation', name: 'DoS Simulation', description: 'Limited simulation of denial of service vulnerabilities' },
  { id: 'file_inclusion', name: 'File Inclusion', description: 'Tests for local and remote file inclusion vulnerabilities' },
  { id: 'command_injection', name: 'Command Injection', description: 'Tests for OS command injection vulnerabilities' },
  { id: 'deserialization', name: 'Insecure Deserialization', description: 'Tests for insecure deserialization vulnerabilities' }
];

// Mock app settings
const mockAppSettings = {
  general: {
    theme: 'dark',
    maxReportsToKeep: 50,
    concurrentScans: 3,
    defaultReportFormat: 'JSON',
    autoStartScans: true,
    enableNotifications: true
  },
  integration: {
    zapApiKey: '',
    burpApiKey: '',
    enableBurpIntegration: false,
    enableZapIntegration: false,
    enableJiraIntegration: false,
    jiraUrl: '',
    jiraUsername: '',
    jiraToken: ''
  },
  storage: {
    databasePath: '/data/securescout.db',
    reportsPath: '/reports',
    logsPath: '/logs',
    enableLogRotation: true,
    logRotationDays: 7,
    enableCompression: true
  },
  notifications: {
    criticalFindings: true,
    highFindings: true,
    scanCompletion: true,
    scanFailure: true,
    emailNotifications: false,
    emailRecipients: '',
    emailServer: '',
    emailPort: 587,
    emailUsername: '',
    emailPassword: '',
    slackIntegration: false,
    slackWebhook: ''
  },
  performance: {
    defaultThreads: 10,
    maxThreads: 30,
    defaultRequestDelay: 0.5,
    defaultTimeout: 30,
    connectionPoolSize: 50,
    maxMemoryUsage: 80
  }
};

const Settings = () => {
  const [tabValue, setTabValue] = useState(0);
  const [profiles, setProfiles] = useState([]);
  const [appSettings, setAppSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [editingProfileId, setEditingProfileId] = useState(null);
  const [editingProfile, setEditingProfile] = useState(null);
  const [profileDialogOpen, setProfileDialogOpen] = useState(false);
  const [deleteProfileDialog, setDeleteProfileDialog] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  
  // Fetch settings and profiles
  useEffect(() => {
    // Simulate API call
    setLoading(true);
    setTimeout(() => {
      setProfiles(mockProfiles);
      setAppSettings(mockAppSettings);
      setLoading(false);
    }, 1000);
  }, []);
  
  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  // App settings handlers
  const handleAppSettingChange = (section, setting, value) => {
    setAppSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [setting]: value
      }
    }));
  };
  
  const handleSaveAppSettings = () => {
    // In a real app, this would make an API call to save settings
    console.log('Saving app settings:', appSettings);
    setSaveSuccess(true);
    
    // Hide success message after 3 seconds
    setTimeout(() => {
      setSaveSuccess(false);
    }, 3000);
  };
  
  // Profile handlers
  const handleEditProfile = (profileId) => {
    const profile = profiles.find(p => p.id === profileId);
    if (profile) {
      setEditingProfileId(profileId);
      setEditingProfile({...profile});
      setProfileDialogOpen(true);
    }
  };
  
  const handleNewProfile = () => {
    setEditingProfileId(null);
    setEditingProfile({
      id: '',
      name: '',
      description: '',
      isBuiltIn: false,
      settings: {
        modules: ['discovery'],
        max_depth: 3,
        max_pages: 200,
        threads: 10,
        request_delay: 0.5,
        user_agent_rotation: true,
        ip_rotation: false,
        stealth_level: 'medium'
      }
    });
    setProfileDialogOpen(true);
  };
  
  const handleDeleteProfile = (profileId) => {
    const profile = profiles.find(p => p.id === profileId);
    if (profile) {
      setEditingProfileId(profileId);
      setEditingProfile(profile);
      setDeleteProfileDialog(true);
    }
  };
  
  const handleConfirmDeleteProfile = () => {
    // In a real app, this would make an API call to delete the profile
    setProfiles(profiles.filter(p => p.id !== editingProfileId));
    setDeleteProfileDialog(false);
  };
  
  const handleSaveProfile = () => {
    if (editingProfileId) {
      // Update existing profile
      setProfiles(profiles.map(p => p.id === editingProfileId ? editingProfile : p));
    } else {
      // Add new profile
      // Generate ID from name
      const profileId = editingProfile.name.toLowerCase().replace(/\s+/g, '-');
      setProfiles([...profiles, {...editingProfile, id: profileId}]);
    }
    setProfileDialogOpen(false);
  };
  
  // Profile form handlers
  const handleProfileChange = (field, value) => {
    setEditingProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  const handleProfileSettingChange = (setting, value) => {
    setEditingProfile(prev => ({
      ...prev,
      settings: {
        ...prev.settings,
        [setting]: value
      }
    }));
  };
  
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading settings...
        </Typography>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Settings
        </Typography>
        {tabValue !== 1 && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<SaveIcon />}
            onClick={handleSaveAppSettings}
          >
            Save Settings
          </Button>
        )}
      </Box>
      
      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}
      
      <Paper elevation={3} sx={{ mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="settings tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab icon={<BuildIcon />} label="General" {...tabProps(0)} />
            <Tab icon={<SecurityIcon />} label="Scan Profiles" {...tabProps(1)} />
            <Tab icon={<NotificationsIcon />} label="Notifications" {...tabProps(2)} />
            <Tab icon={<StorageIcon />} label="Storage & Integration" {...tabProps(3)} />
          </Tabs>
        </Box>
        
        {/* General Settings */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Application Settings
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                select
                fullWidth
                label="Theme"
                value={appSettings.general.theme}
                onChange={(e) => handleAppSettingChange('general', 'theme', e.target.value)}
              >
                <MenuItem value="light">Light</MenuItem>
                <MenuItem value="dark">Dark</MenuItem>
                <MenuItem value="system">System Default</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                select
                fullWidth
                label="Default Report Format"
                value={appSettings.general.defaultReportFormat}
                onChange={(e) => handleAppSettingChange('general', 'defaultReportFormat', e.target.value)}
              >
                <MenuItem value="JSON">JSON</MenuItem>
                <MenuItem value="HTML">HTML</MenuItem>
                <MenuItem value="PDF">PDF</MenuItem>
              </TextField>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Maximum Reports to Keep"
                value={appSettings.general.maxReportsToKeep}
                onChange={(e) => handleAppSettingChange('general', 'maxReportsToKeep', parseInt(e.target.value))}
                InputProps={{
                  endAdornment: (
                    <Tooltip title="Number of reports to keep in storage before older ones are deleted">
                      <InputAdornment position="end">
                        <HelpOutlineIcon fontSize="small" />
                      </InputAdornment>
                    </Tooltip>
                  )
                }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Maximum Concurrent Scans"
                value={appSettings.general.concurrentScans}
                onChange={(e) => handleAppSettingChange('general', 'concurrentScans', parseInt(e.target.value))}
                InputProps={{
                  endAdornment: (
                    <Tooltip title="Maximum number of scans that can run simultaneously">
                      <InputAdornment position="end">
                        <HelpOutlineIcon fontSize="small" />
                      </InputAdornment>
                    </Tooltip>
                  )
                }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={appSettings.general.autoStartScans}
                    onChange={(e) => handleAppSettingChange('general', 'autoStartScans', e.target.checked)}
                  />
                }
                label="Automatically start scans when created"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Performance Settings
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Default Thread Count: {appSettings.performance.defaultThreads}
              </Typography>
              <Slider
                value={appSettings.performance.defaultThreads}
                onChange={(e, newValue) => handleAppSettingChange('performance', 'defaultThreads', newValue)}
                min={1}
                max={30}
                step={1}
                marks={[
                  { value: 1, label: '1' },
                  { value: 15, label: '15' },
                  { value: 30, label: '30' }
                ]}
                valueLabelDisplay="auto"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>
                Default Request Delay (seconds): {appSettings.performance.defaultRequestDelay}
              </Typography>
              <Slider
                value={appSettings.performance.defaultRequestDelay}
                onChange={(e, newValue) => handleAppSettingChange('performance', 'defaultRequestDelay', newValue)}
                min={0}
                max={3}
                step={0.1}
                marks={[
                  { value: 0, label: '0' },
                  { value: 1.5, label: '1.5' },
                  { value: 3, label: '3' }
                ]}
                valueLabelDisplay="auto"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Connection Timeout (seconds)"
                value={appSettings.performance.defaultTimeout}
                onChange={(e) => handleAppSettingChange('performance', 'defaultTimeout', parseInt(e.target.value))}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Connection Pool Size"
                value={appSettings.performance.connectionPoolSize}
                onChange={(e) => handleAppSettingChange('performance', 'connectionPoolSize', parseInt(e.target.value))}
              />
            </Grid>
          </Grid>
        </TabPanel>
        
        {/* Scan Profiles */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Scan Profiles
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={handleNewProfile}
            >
              New Profile
            </Button>
          </Box>
          
          <Grid container spacing={3}>
            {profiles.map((profile) => (
              <Grid item xs={12} md={6} key={profile.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Typography variant="h6">
                        {profile.name}
                        {profile.isBuiltIn && (
                          <Tooltip title="Built-in profile">
                            <LockIcon fontSize="small" sx={{ ml: 1, verticalAlign: 'middle', color: 'text.secondary' }} />
                          </Tooltip>
                        )}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {profile.description}
                    </Typography>
                    
                    <Accordion sx={{ mt: 2 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>Profile Settings</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" gutterBottom>
                          <strong>Modules:</strong> {profile.settings.modules.length} modules selected
                        </Typography>
                        <Typography variant="body2" gutterBottom>
                          <strong>Max Depth:</strong> {profile.settings.max_depth}
                        </Typography>
                        <Typography variant="body2" gutterBottom>
                          <strong>Max Pages:</strong> {profile.settings.max_pages}
                        </Typography>
                        <Typography variant="body2" gutterBottom>
                          <strong>Threads:</strong> {profile.settings.threads}
                        </Typography>
                        <Typography variant="body2" gutterBottom>
                          <strong>Request Delay:</strong> {profile.settings.request_delay}s
                        </Typography>
                        <Typography variant="body2" gutterBottom>
                          <strong>Stealth Level:</strong> {profile.settings.stealth_level}
                        </Typography>
                        <Typography variant="body2" gutterBottom>
                          <strong>User Agent Rotation:</strong> {profile.settings.user_agent_rotation ? 'Yes' : 'No'}
                        </Typography>
                        <Typography variant="body2">
                          <strong>IP Rotation:</strong> {profile.settings.ip_rotation ? 'Yes' : 'No'}
                        </Typography>
                      </AccordionDetails>
                    </Accordion>
                  </CardContent>
                  <CardActions>
                    <Button
                      startIcon={<EditIcon />}
                      onClick={() => handleEditProfile(profile.id)}
                      disabled={profile.isBuiltIn}
                    >
                      Edit
                    </Button>
                    <Button
                      startIcon={<DeleteIcon />}
                      color="error"
                      onClick={() => handleDeleteProfile(profile.id)}
                      disabled={profile.isBuiltIn}
                    >
                      Delete
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>
        
        {/* Notifications */}
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Notification Settings
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={appSettings.notifications.criticalFindings}
                    onChange={(e) => handleAppSettingChange('notifications', 'criticalFindings', e.target.checked)}
                  />
                }
                label="Notify on Critical Findings"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={appSettings.notifications.highFindings}
                    onChange={(e) => handleAppSettingChange('notifications', 'highFindings', e.target.checked)}
                  />
                }
                label="Notify on High Severity Findings"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={appSettings.notifications.scanCompletion}
                    onChange={(e) => handleAppSettingChange('notifications', 'scanCompletion', e.target.checked)}
                  />
                }
                label="Notify on Scan Completion"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={appSettings.notifications.scanFailure}
                    onChange={(e) => handleAppSettingChange('notifications', 'scanFailure', e.target.checked)}
                  />
                }
                label="Notify on Scan Failure"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Email Notifications
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={appSettings.notifications.emailNotifications}
                    onChange={(e) => handleAppSettingChange('notifications', 'emailNotifications', e.target.checked)}
                  />
                }
                label="Enable Email Notifications"
              />
            </Grid>
            
            {appSettings.notifications.emailNotifications && (
              <>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Email Recipients (comma separated)"
                    value={appSettings.notifications.emailRecipients}
                    onChange={(e) => handleAppSettingChange('notifications', 'emailRecipients', e.target.value)}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="SMTP Server"
                    value={appSettings.notifications.emailServer}
                    onChange={(e) => handleAppSettingChange('notifications', 'emailServer', e.target.value)}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="SMTP Port"
                    value={appSettings.notifications.emailPort}
                    onChange={(e) => handleAppSettingChange('notifications', 'emailPort', parseInt(e.target.value))}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="SMTP Username"
                    value={appSettings.notifications.emailUsername}
                    onChange={(e) => handleAppSettingChange('notifications', 'emailUsername', e.target.value)}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    type="password"
                    label="SMTP Password"
                    value={appSettings.notifications.emailPassword}
                    onChange={(e) => handleAppSettingChange('notifications', 'emailPassword', e.target.value)}
                  />
                </Grid>
              </>
            )}
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Slack Integration
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={appSettings.notifications.slackIntegration}
                    onChange={(e) => handleAppSettingChange('notifications', 'slackIntegration', e.target.checked)}
                  />
                }
                label="Enable Slack Notifications"
              />
            </Grid>
            
            {appSettings.notifications.slackIntegration && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Slack Webhook URL"
                  value={appSettings.notifications.slackWebhook}
                  onChange={(e) => handleAppSettingChange('notifications', 'slackWebhook', e.target.value)}
                />
              </Grid>
            )}
          </Grid>
        </TabPanel>
        
        {/* Storage & Integration */}
        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Storage Settings
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Database Path"
                value={appSettings.storage.databasePath}
                onChange={(e) => handleAppSettingChange('storage', 'databasePath', e.target.value)}
                InputProps={{
                  readOnly: true,
                  startAdornment: (
                    <InputAdornment position="start">
                      <StorageIcon />
                    </InputAdornment>
                  )
                }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Reports Path"
                value={appSettings.storage.reportsPath}
                onChange={(e) => handleAppSettingChange('storage', 'reportsPath', e.target.value)}
                InputProps={{
                  readOnly: true,
                  startAdornment: (
                    <InputAdornment position="start">
                      <StorageIcon />
                    </InputAdornment>
                  )
                }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Logs Path"
                value={appSettings.storage.logsPath}
                onChange={(e) => handleAppSettingChange('storage', 'logsPath', e.target.value)}
                InputProps={{
                  readOnly: true,
                  startAdornment: (
                    <InputAdornment position="start">
                      <StorageIcon />
                    </InputAdornment>
                  )
                }}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={appSettings.storage.enableLogRotation}
                    onChange={(e) => handleAppSettingChange('storage', 'enableLogRotation', e.target.checked)}
                  />
                }
                label="Enable Log Rotation"
              />
            </Grid>
            
            {appSettings.storage.enableLogRotation && (
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Log Rotation Days"
                  value={appSettings.storage.logRotationDays}
                  onChange={(e) => handleAppSettingChange('storage', 'logRotationDays', parseInt(e.target.value))}
                />
              </Grid>
            )}
            
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={appSettings.storage.enableCompression}
                    onChange={(e) => handleAppSettingChange('storage', 'enableCompression', e.target.checked)}
                  />
                }
                label="Enable Report Compression"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Tool Integration
              </Typography>
            </Grid>
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={appSettings.integration.enableZapIntegration}
                    onChange={(e) => handleAppSettingChange('integration', 'enableZapIntegration', e.target.checked)}
                  />
                }
                label="Enable OWASP ZAP Integration"
              />
            </Grid>
            
            {appSettings.integration.enableZapIntegration && (
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="ZAP API Key"
                  value={appSettings.integration.zapApiKey}
                  onChange={(e) => handleAppSettingChange('integration', 'zapApiKey', e.target.value)}
                />
              </Grid>
            )}
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={appSettings.integration.enableBurpIntegration}
                    onChange={(e) => handleAppSettingChange('integration', 'enableBurpIntegration', e.target.checked)}
                  />
                }
                label="Enable Burp Suite Integration"
              />
            </Grid>
            
            {appSettings.integration.enableBurpIntegration && (
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Burp API Key"
                  value={appSettings.integration.burpApiKey}
                  onChange={(e) => handleAppSettingChange('integration', 'burpApiKey', e.target.value)}
                />
              </Grid>
            )}
            
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={appSettings.integration.enableJiraIntegration}
                    onChange={(e) => handleAppSettingChange('integration', 'enableJiraIntegration', e.target.checked)}
                  />
                }
                label="Enable Jira Integration"
              />
            </Grid>
            
            {appSettings.integration.enableJiraIntegration && (
              <>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Jira URL"
                    value={appSettings.integration.jiraUrl}
                    onChange={(e) => handleAppSettingChange('integration', 'jiraUrl', e.target.value)}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Jira Username"
                    value={appSettings.integration.jiraUsername}
                    onChange={(e) => handleAppSettingChange('integration', 'jiraUsername', e.target.value)}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Jira API Token"
                    type="password"
                    value={appSettings.integration.jiraToken}
                    onChange={(e) => handleAppSettingChange('integration', 'jiraToken', e.target.value)}
                  />
                </Grid>
              </>
            )}
          </Grid>
        </TabPanel>
      </Paper>
      
      {/* Edit Profile Dialog */}
      <Dialog 
        open={profileDialogOpen} 
        onClose={() => setProfileDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingProfileId ? 'Edit Profile' : 'New Profile'}
        </DialogTitle>
        <DialogContent dividers>
          {editingProfile && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Profile Name"
                  value={editingProfile.name}
                  onChange={(e) => handleProfileChange('name', e.target.value)}
                  required
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Description"
                  value={editingProfile.description}
                  onChange={(e) => handleProfileChange('description', e.target.value)}
                />
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Profile Settings
                </Typography>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography gutterBottom>
                  Maximum Crawl Depth: {editingProfile.settings.max_depth}
                </Typography>
                <Slider
                  value={editingProfile.settings.max_depth}
                  onChange={(e, newValue) => handleProfileSettingChange('max_depth', newValue)}
                  min={1}
                  max={10}
                  step={1}
                  marks
                  valueLabelDisplay="auto"
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography gutterBottom>
                  Maximum Pages: {editingProfile.settings.max_pages}
                </Typography>
                <Slider
                  value={editingProfile.settings.max_pages}
                  onChange={(e, newValue) => handleProfileSettingChange('max_pages', newValue)}
                  min={50}
                  max={1000}
                  step={50}
                  marks={[
                    { value: 50, label: '50' },
                    { value: 500, label: '500' },
                    { value: 1000, label: '1000' }
                  ]}
                  valueLabelDisplay="auto"
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography gutterBottom>
                  Concurrent Threads: {editingProfile.settings.threads}
                </Typography>
                <Slider
                  value={editingProfile.settings.threads}
                  onChange={(e, newValue) => handleProfileSettingChange('threads', newValue)}
                  min={1}
                  max={30}
                  step={1}
                  marks={[
                    { value: 1, label: '1' },
                    { value: 15, label: '15' },
                    { value: 30, label: '30' }
                  ]}
                  valueLabelDisplay="auto"
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography gutterBottom>
                  Request Delay (seconds): {editingProfile.settings.request_delay}
                </Typography>
                <Slider
                  value={editingProfile.settings.request_delay}
                  onChange={(e, newValue) => handleProfileSettingChange('request_delay', newValue)}
                  min={0}
                  max={3}
                  step={0.1}
                  marks={[
                    { value: 0, label: '0' },
                    { value: 1.5, label: '1.5' },
                    { value: 3, label: '3' }
                  ]}
                  valueLabelDisplay="auto"
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <TextField
                  select
                  fullWidth
                  label="Stealth Level"
                  value={editingProfile.settings.stealth_level}
                  onChange={(e) => handleProfileSettingChange('stealth_level', e.target.value)}
                >
                  <MenuItem value="low">Low - Fast but Detectable</MenuItem>
                  <MenuItem value="medium">Medium - Balanced Approach</MenuItem>
                  <MenuItem value="high">High - More Evasive</MenuItem>
                  <MenuItem value="maximum">Maximum - Ultra Stealthy</MenuItem>
                </TextField>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={editingProfile.settings.user_agent_rotation}
                      onChange={(e) => handleProfileSettingChange('user_agent_rotation', e.target.checked)}
                    />
                  }
                  label="Rotate User Agents"
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={editingProfile.settings.ip_rotation}
                      onChange={(e) => handleProfileSettingChange('ip_rotation', e.target.checked)}
                    />
                  }
                  label="IP Rotation (if available)"
                />
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="subtitle1" gutterBottom>
                  Testing Modules
                </Typography>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Select the security testing modules to include in this profile.
                </Alert>
                
                <Grid container spacing={1}>
                  {availableModules.map((module) => (
                    <Grid item xs={12} sm={6} md={4} key={module.id}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={editingProfile.settings.modules.includes(module.id)}
                            onChange={(e) => {
                              const modules = e.target.checked
                                ? [...editingProfile.settings.modules, module.id]
                                : editingProfile.settings.modules.filter(id => id !== module.id);
                              handleProfileSettingChange('modules', modules);
                            }}
                          />
                        }
                        label={
                          <Tooltip title={module.description}>
                            <Typography variant="body2">{module.name}</Typography>
                          </Tooltip>
                        }
                      />
                    </Grid>
                  ))}
                </Grid>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProfileDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveProfile} variant="contained" color="primary">
            Save Profile
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Delete Profile Dialog */}
      <Dialog
        open={deleteProfileDialog}
        onClose={() => setDeleteProfileDialog(false)}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the profile "{editingProfile?.name}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteProfileDialog(false)} color="primary">
            Cancel
          </Button>
          <Button onClick={handleConfirmDeleteProfile} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Settings;