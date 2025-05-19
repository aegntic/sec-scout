import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  TextField, 
  Button, 
  Stepper, 
  Step, 
  StepLabel,
  Grid,
  FormControlLabel,
  Checkbox,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  OutlinedInput,
  ListItemText,
  Divider,
  Alert,
  IconButton,
  Tooltip,
  Card,
  CardContent,
  CardHeader
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import InfoIcon from '@mui/icons-material/Info';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { useNavigate } from 'react-router-dom';

// Mock data for available scan modules
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

// Mock data for scan profiles
const scanProfiles = [
  { id: 'passive', name: 'Passive Scan', description: 'Non-intrusive information gathering only' },
  { id: 'standard', name: 'Standard Scan', description: 'Balanced security testing with moderate intrusiveness' },
  { id: 'aggressive', name: 'Aggressive Scan', description: 'Comprehensive security testing with high intrusiveness' },
  { id: 'stealth', name: 'Stealth Scan', description: 'Maximum evasion techniques with balanced testing' }
];

// Steps in the scan configuration wizard
const steps = ['Target Information', 'Scan Configuration', 'Authentication', 'Review & Launch'];

const ScanNew = () => {
  const navigate = useNavigate();
  
  // Stepper state
  const [activeStep, setActiveStep] = useState(0);
  
  // Form state
  const [scanConfig, setScanConfig] = useState({
    target_url: '',
    target_name: '',
    scan_profile: 'standard',
    custom_profile: false,
    modules: ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 'headers', 'cookies'],
    max_depth: 3,
    max_pages: 200,
    request_delay: 0.5,
    threads: 10,
    user_agent_rotation: true,
    ip_rotation: false,
    stealth_level: 'medium',
    auth_required: false,
    auth_type: 'form',
    auth_url: '',
    username: '',
    password: '',
    token: '',
    custom_headers: {},
    custom_cookies: {}
  });
  
  // Form validation
  const [errors, setErrors] = useState({});
  
  // Handler for form field changes
  const handleChange = (event) => {
    const { name, value, checked, type } = event.target;
    setScanConfig((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear error when field is updated
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };
  
  // Handler for slider changes
  const handleSliderChange = (name) => (event, newValue) => {
    setScanConfig((prev) => ({
      ...prev,
      [name]: newValue
    }));
  };
  
  // Handler for multi-select changes
  const handleMultiSelectChange = (event) => {
    const { value } = event.target;
    setScanConfig((prev) => ({
      ...prev,
      modules: value
    }));
  };
  
  // Profile selection handler
  const handleProfileSelect = (profileId) => {
    setScanConfig((prev) => ({
      ...prev,
      scan_profile: profileId,
      custom_profile: false
    }));
    
    // Update modules and settings based on profile (in a real app, this would fetch from API)
    if (profileId === 'passive') {
      setScanConfig((prev) => ({
        ...prev,
        modules: ['discovery', 'ssl_tls', 'headers', 'cookies'],
        max_depth: 2,
        max_pages: 100,
        threads: 5,
        request_delay: 1.0,
        user_agent_rotation: true,
        ip_rotation: false,
        stealth_level: 'high'
      }));
    } else if (profileId === 'standard') {
      setScanConfig((prev) => ({
        ...prev,
        modules: ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 'headers', 'cookies', 'sensitive_data'],
        max_depth: 3,
        max_pages: 200,
        threads: 10,
        request_delay: 0.5,
        user_agent_rotation: true,
        ip_rotation: false,
        stealth_level: 'medium'
      }));
    } else if (profileId === 'aggressive') {
      setScanConfig((prev) => ({
        ...prev,
        modules: ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 'headers', 'cookies', 'sensitive_data', 'brute_force', 'dos_simulation', 'file_inclusion', 'command_injection', 'deserialization'],
        max_depth: 5,
        max_pages: 500,
        threads: 20,
        request_delay: 0.1,
        user_agent_rotation: true,
        ip_rotation: true,
        stealth_level: 'low'
      }));
    } else if (profileId === 'stealth') {
      setScanConfig((prev) => ({
        ...prev,
        modules: ['discovery', 'authentication', 'injection', 'xss', 'csrf', 'ssl_tls', 'headers', 'cookies', 'sensitive_data'],
        max_depth: 3,
        max_pages: 200,
        threads: 3,
        request_delay: 3.0,
        user_agent_rotation: true,
        ip_rotation: true,
        stealth_level: 'maximum'
      }));
    }
  };
  
  // Enable custom profile editing
  const handleCustomProfile = () => {
    setScanConfig((prev) => ({
      ...prev,
      custom_profile: true,
      scan_profile: 'custom'
    }));
  };
  
  // Validate current step
  const validateStep = () => {
    const newErrors = {};
    
    if (activeStep === 0) {
      if (!scanConfig.target_url) {
        newErrors.target_url = 'Target URL is required';
      } else if (!/^https?:\/\/.+/.test(scanConfig.target_url)) {
        newErrors.target_url = 'Must be a valid URL starting with http:// or https://';
      }
    } else if (activeStep === 1) {
      if (scanConfig.modules.length === 0) {
        newErrors.modules = 'Select at least one module';
      }
    } else if (activeStep === 2 && scanConfig.auth_required) {
      if (scanConfig.auth_type === 'form') {
        if (!scanConfig.auth_url) {
          newErrors.auth_url = 'Authentication URL is required';
        }
        if (!scanConfig.username) {
          newErrors.username = 'Username is required';
        }
        if (!scanConfig.password) {
          newErrors.password = 'Password is required';
        }
      } else if (scanConfig.auth_type === 'token' && !scanConfig.token) {
        newErrors.token = 'Token is required';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  // Handle next step
  const handleNext = () => {
    if (validateStep()) {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };
  
  // Handle back step
  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };
  
  // Handle scan launch
  const handleLaunch = () => {
    if (validateStep()) {
      // In a real app, you would send the scan configuration to the API
      console.log('Launching scan with configuration:', scanConfig);
      
      // Navigate to the active scans page (in a real app, you would navigate to the specific scan)
      navigate('/scan/active');
    }
  };
  
  // Render step content
  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Target Information
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Target URL"
                  name="target_url"
                  value={scanConfig.target_url}
                  onChange={handleChange}
                  error={!!errors.target_url}
                  helperText={errors.target_url || 'Enter the full URL of the target application (e.g., https://example.com)'}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Target Name (Optional)"
                  name="target_name"
                  value={scanConfig.target_name}
                  onChange={handleChange}
                  helperText="A friendly name to identify this scan"
                />
              </Grid>
              <Grid item xs={12}>
                <Alert severity="info" sx={{ mt: 2 }}>
                  <strong>Important:</strong> Only scan applications you own or have explicit permission to test.
                </Alert>
              </Grid>
            </Grid>
          </Box>
        );
      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Scan Configuration
            </Typography>
            
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 3 }}>
              Select Scan Profile
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 4 }}>
              {scanProfiles.map((profile) => (
                <Grid item xs={12} sm={6} md={3} key={profile.id}>
                  <Card 
                    variant="outlined" 
                    sx={{ 
                      cursor: 'pointer',
                      border: scanConfig.scan_profile === profile.id && !scanConfig.custom_profile ? '2px solid #3f88c5' : '',
                      backgroundColor: scanConfig.scan_profile === profile.id && !scanConfig.custom_profile ? 'rgba(63, 136, 197, 0.1)' : ''
                    }}
                    onClick={() => handleProfileSelect(profile.id)}
                  >
                    <CardContent>
                      <Typography variant="h6" component="div">{profile.name}</Typography>
                      <Typography variant="body2" color="text.secondary">{profile.description}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1">
                Custom Configuration
              </Typography>
              <Button 
                variant={scanConfig.custom_profile ? "contained" : "outlined"} 
                color="primary"
                size="small"
                onClick={handleCustomProfile}
              >
                {scanConfig.custom_profile ? "Customizing" : "Customize"}
              </Button>
            </Box>
            
            <Divider sx={{ mb: 3 }} />
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControl fullWidth error={!!errors.modules}>
                  <InputLabel id="modules-label">Testing Modules</InputLabel>
                  <Select
                    labelId="modules-label"
                    multiple
                    value={scanConfig.modules}
                    onChange={handleMultiSelectChange}
                    input={<OutlinedInput label="Testing Modules" />}
                    renderValue={(selected) => (
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selected.map((value) => (
                          <Chip key={value} label={availableModules.find(m => m.id === value)?.name || value} />
                        ))}
                      </Box>
                    )}
                    disabled={!scanConfig.custom_profile}
                  >
                    {availableModules.map((module) => (
                      <MenuItem key={module.id} value={module.id}>
                        <Checkbox checked={scanConfig.modules.indexOf(module.id) > -1} />
                        <ListItemText 
                          primary={module.name} 
                          secondary={module.description}
                          primaryTypographyProps={{ variant: 'body1' }}
                          secondaryTypographyProps={{ variant: 'body2' }}
                        />
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography id="max-depth-slider" gutterBottom>
                  Maximum Crawl Depth: {scanConfig.max_depth}
                  <Tooltip title="How deep the scanner will crawl into the website structure">
                    <IconButton size="small">
                      <HelpOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Typography>
                <Slider
                  value={scanConfig.max_depth}
                  onChange={handleSliderChange('max_depth')}
                  aria-labelledby="max-depth-slider"
                  valueLabelDisplay="auto"
                  step={1}
                  marks
                  min={1}
                  max={10}
                  disabled={!scanConfig.custom_profile}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography id="max-pages-slider" gutterBottom>
                  Maximum Pages: {scanConfig.max_pages}
                  <Tooltip title="Maximum number of pages to scan">
                    <IconButton size="small">
                      <HelpOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Typography>
                <Slider
                  value={scanConfig.max_pages}
                  onChange={handleSliderChange('max_pages')}
                  aria-labelledby="max-pages-slider"
                  valueLabelDisplay="auto"
                  step={50}
                  marks
                  min={50}
                  max={1000}
                  disabled={!scanConfig.custom_profile}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography id="threads-slider" gutterBottom>
                  Concurrent Threads: {scanConfig.threads}
                  <Tooltip title="Number of concurrent requests">
                    <IconButton size="small">
                      <HelpOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Typography>
                <Slider
                  value={scanConfig.threads}
                  onChange={handleSliderChange('threads')}
                  aria-labelledby="threads-slider"
                  valueLabelDisplay="auto"
                  step={1}
                  marks
                  min={1}
                  max={30}
                  disabled={!scanConfig.custom_profile}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography id="request-delay-slider" gutterBottom>
                  Request Delay: {scanConfig.request_delay} seconds
                  <Tooltip title="Delay between requests (helps with stealth)">
                    <IconButton size="small">
                      <HelpOutlineIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Typography>
                <Slider
                  value={scanConfig.request_delay}
                  onChange={handleSliderChange('request_delay')}
                  aria-labelledby="request-delay-slider"
                  valueLabelDisplay="auto"
                  step={0.1}
                  marks
                  min={0}
                  max={5}
                  disabled={!scanConfig.custom_profile}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel id="stealth-level-label">Stealth Level</InputLabel>
                  <Select
                    labelId="stealth-level-label"
                    name="stealth_level"
                    value={scanConfig.stealth_level}
                    onChange={handleChange}
                    label="Stealth Level"
                    disabled={!scanConfig.custom_profile}
                  >
                    <MenuItem value="low">Low - Fast but Detectable</MenuItem>
                    <MenuItem value="medium">Medium - Balanced Approach</MenuItem>
                    <MenuItem value="high">High - More Evasive</MenuItem>
                    <MenuItem value="maximum">Maximum - Ultra Stealthy</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={scanConfig.user_agent_rotation}
                      onChange={handleChange}
                      name="user_agent_rotation"
                      disabled={!scanConfig.custom_profile}
                    />
                  }
                  label="Rotate User Agents"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={scanConfig.ip_rotation}
                      onChange={handleChange}
                      name="ip_rotation"
                      disabled={!scanConfig.custom_profile}
                    />
                  }
                  label="IP Rotation (if available)"
                />
              </Grid>
            </Grid>
          </Box>
        );
      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Authentication Configuration
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={scanConfig.auth_required}
                      onChange={handleChange}
                      name="auth_required"
                    />
                  }
                  label="Application Requires Authentication"
                />
              </Grid>
              
              {scanConfig.auth_required && (
                <>
                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel id="auth-type-label">Authentication Type</InputLabel>
                      <Select
                        labelId="auth-type-label"
                        name="auth_type"
                        value={scanConfig.auth_type}
                        onChange={handleChange}
                        label="Authentication Type"
                      >
                        <MenuItem value="form">Form-based Login</MenuItem>
                        <MenuItem value="basic">HTTP Basic Authentication</MenuItem>
                        <MenuItem value="token">API Token / Bearer</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  {scanConfig.auth_type === 'form' && (
                    <>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Login URL"
                          name="auth_url"
                          value={scanConfig.auth_url}
                          onChange={handleChange}
                          error={!!errors.auth_url}
                          helperText={errors.auth_url || 'URL of the login page or authentication endpoint'}
                          required
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Username"
                          name="username"
                          value={scanConfig.username}
                          onChange={handleChange}
                          error={!!errors.username}
                          helperText={errors.username}
                          required
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Password"
                          type="password"
                          name="password"
                          value={scanConfig.password}
                          onChange={handleChange}
                          error={!!errors.password}
                          helperText={errors.password}
                          required
                        />
                      </Grid>
                    </>
                  )}
                  
                  {scanConfig.auth_type === 'basic' && (
                    <>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Username"
                          name="username"
                          value={scanConfig.username}
                          onChange={handleChange}
                          error={!!errors.username}
                          helperText={errors.username}
                          required
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Password"
                          type="password"
                          name="password"
                          value={scanConfig.password}
                          onChange={handleChange}
                          error={!!errors.password}
                          helperText={errors.password}
                          required
                        />
                      </Grid>
                    </>
                  )}
                  
                  {scanConfig.auth_type === 'token' && (
                    <Grid item xs={12}>
                      <TextField
                        fullWidth
                        label="API Token / Bearer Token"
                        name="token"
                        value={scanConfig.token}
                        onChange={handleChange}
                        error={!!errors.token}
                        helperText={errors.token || 'Authentication token to include in requests'}
                        required
                      />
                    </Grid>
                  )}
                </>
              )}
              
              <Grid item xs={12}>
                <Alert severity="info" sx={{ mt: 2 }}>
                  <strong>Note:</strong> Authentication credentials are used only for the duration of the scan and are not stored permanently.
                </Alert>
              </Grid>
            </Grid>
          </Box>
        );
      case 3:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Review Scan Configuration
            </Typography>
            
            <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1">Target Information</Typography>
                  <Typography variant="body1">URL: {scanConfig.target_url}</Typography>
                  {scanConfig.target_name && (
                    <Typography variant="body1">Name: {scanConfig.target_name}</Typography>
                  )}
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1">Scan Profile</Typography>
                  <Typography variant="body1">
                    {scanConfig.custom_profile 
                      ? 'Custom Configuration' 
                      : scanProfiles.find(p => p.id === scanConfig.scan_profile)?.name || 'Standard Scan'}
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1">Scan Parameters</Typography>
                  <Typography variant="body2">Maximum Depth: {scanConfig.max_depth}</Typography>
                  <Typography variant="body2">Maximum Pages: {scanConfig.max_pages}</Typography>
                  <Typography variant="body2">Concurrent Threads: {scanConfig.threads}</Typography>
                  <Typography variant="body2">Request Delay: {scanConfig.request_delay}s</Typography>
                  <Typography variant="body2">
                    Stealth Level: {
                      {
                        'low': 'Low - Fast but Detectable',
                        'medium': 'Medium - Balanced Approach',
                        'high': 'High - More Evasive',
                        'maximum': 'Maximum - Ultra Stealthy'
                      }[scanConfig.stealth_level]
                    }
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1">Testing Modules</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {scanConfig.modules.map((moduleId) => (
                      <Chip 
                        key={moduleId} 
                        label={availableModules.find(m => m.id === moduleId)?.name || moduleId}
                        size="small"
                        sx={{ mb: 1 }}
                      />
                    ))}
                  </Box>
                </Grid>
                
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle1">Authentication</Typography>
                  {scanConfig.auth_required ? (
                    <>
                      <Typography variant="body2">
                        Method: {
                          {
                            'form': 'Form-based Login',
                            'basic': 'HTTP Basic Authentication',
                            'token': 'API Token / Bearer'
                          }[scanConfig.auth_type]
                        }
                      </Typography>
                      {scanConfig.auth_type === 'form' && (
                        <Typography variant="body2">Login URL: {scanConfig.auth_url}</Typography>
                      )}
                      <Typography variant="body2">
                        Credentials: {scanConfig.auth_type === 'token' ? '***** (Token)' : `${scanConfig.username} / *****`}
                      </Typography>
                    </>
                  ) : (
                    <Typography variant="body2">No authentication configured</Typography>
                  )}
                </Grid>
              </Grid>
            </Paper>
            
            <Alert severity="warning" sx={{ mb: 3 }}>
              <strong>Warning:</strong> Security testing can impact application performance. Only scan systems you own or have permission to test.
            </Alert>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleLaunch}
                endIcon={<SendIcon />}
                size="large"
              >
                Launch Scan
              </Button>
            </Box>
          </Box>
        );
      default:
        return 'Unknown step';
    }
  };
  
  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          New Security Scan
        </Typography>
        
        <Stepper activeStep={activeStep} sx={{ py: 3 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        <Box sx={{ mt: 2 }}>
          {getStepContent(activeStep)}
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
          {activeStep > 0 && (
            <Button
              onClick={handleBack}
              sx={{ mr: 1 }}
            >
              Back
            </Button>
          )}
          {activeStep < steps.length - 1 ? (
            <Button
              variant="contained"
              color="primary"
              onClick={handleNext}
            >
              Next
            </Button>
          ) : null}
        </Box>
      </Paper>
    </Container>
  );
};

export default ScanNew;