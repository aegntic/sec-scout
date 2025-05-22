import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  Divider,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Chip,
  Grid,
  Autocomplete,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Alert,
  CircularProgress,
  alpha
} from '@mui/material';
import { styled } from '@mui/material/styles';
import CloseIcon from '@mui/icons-material/Close';
import IconButton from '@mui/material/IconButton';
import SecurityIcon from '@mui/icons-material/Security';
import AddIcon from '@mui/icons-material/Add';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import apiService from '../../services/api';

const OptionsPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginTop: theme.spacing(2),
  marginBottom: theme.spacing(2),
  background: alpha(theme.palette.background.paper, 0.7),
  backdropFilter: 'blur(10px)',
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
}));

const TemplateHeader = styled(Box)(({ theme, templateType }) => {
  const getGradient = (type) => {
    switch (type) {
      case 'web':
        return 'linear-gradient(135deg, #6C63FF 0%, #4335D0 100%)';
      case 'network':
        return 'linear-gradient(135deg, #00BFA6 0%, #008B7A 100%)';
      case 'container':
        return 'linear-gradient(135deg, #FF5252 0%, #C62828 100%)';
      case 'fullstack':
        return 'linear-gradient(135deg, #FFB74D 0%, #EF6C00 100%)';
      case 'api':
        return 'linear-gradient(135deg, #4FC3F7 0%, #0288D1 100%)';
      default:
        return 'linear-gradient(135deg, #9575CD 0%, #5E35B1 100%)';
    }
  };
  
  return {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: theme.spacing(2),
    marginBottom: theme.spacing(3),
    borderRadius: theme.shape.borderRadius,
    background: getGradient(templateType),
    color: 'white',
    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
  };
});

const getTemplateType = (templateId) => {
  if (templateId.includes('web')) return 'web';
  if (templateId.includes('network')) return 'network';
  if (templateId.includes('container')) return 'container';
  if (templateId.includes('fullstack')) return 'fullstack';
  if (templateId.includes('api')) return 'api';
  return 'security';
};

// Common scan options for different template types
const templateOptions = {
  web_application_scan: [
    { 
      key: 'nikto_tuning', 
      label: 'Nikto Tuning', 
      type: 'select',
      options: [
        { value: '1234abc', label: 'Default (All Checks)' },
        { value: '1', label: 'File Upload' },
        { value: '2', label: 'Misconfiguration' },
        { value: '3', label: 'Information Disclosure' },
        { value: '4', label: 'Injection' },
        { value: '5', label: 'Remote File Retrieval' },
      ],
      default: '1234abc',
      description: 'Controls which security checks Nikto will perform'
    },
    { 
      key: 'nuclei_tags', 
      label: 'Nuclei Tags', 
      type: 'text',
      default: 'cve,oast',
      description: 'Comma-separated list of template tags to include'
    },
    { 
      key: 'sqlmap_level', 
      label: 'SQLMap Level', 
      type: 'select',
      options: [
        { value: 1, label: 'Level 1 (Default)' },
        { value: 2, label: 'Level 2' },
        { value: 3, label: 'Level 3' },
        { value: 4, label: 'Level 4' },
        { value: 5, label: 'Level 5 (Thorough)' },
      ],
      default: 1,
      description: 'Level of tests to perform (higher = more tests)'
    }
  ],
  network_infrastructure_scan: [
    { 
      key: 'nmap_scan_type', 
      label: 'Scan Type', 
      type: 'select',
      options: [
        { value: 'SV', label: 'Service Detection' },
        { value: 'A', label: 'Aggressive Scan' },
        { value: 'T', label: 'TCP Connect Scan' },
        { value: 'S', label: 'SYN Scan' },
      ],
      default: 'SV',
      description: 'Type of port scan to perform'
    },
    { 
      key: 'nmap_ports', 
      label: 'Port Range', 
      type: 'text',
      default: '1-1000',
      description: 'Range of ports to scan (e.g., 1-1000, 80,443,8080)'
    }
  ],
  container_security_scan: [
    { 
      key: 'trivy_severity', 
      label: 'Severity Levels', 
      type: 'multiselect',
      options: [
        { value: 'CRITICAL', label: 'Critical' },
        { value: 'HIGH', label: 'High' },
        { value: 'MEDIUM', label: 'Medium' },
        { value: 'LOW', label: 'Low' },
      ],
      default: ['CRITICAL', 'HIGH'],
      description: 'Severity levels to include in scan results'
    }
  ],
  full_stack_security_scan: [
    { 
      key: 'network_target', 
      label: 'Network Target', 
      type: 'text',
      default: '',
      description: 'IP address or hostname for network scanning (leave empty to derive from web target)'
    },
    { 
      key: 'container_target', 
      label: 'Container Target', 
      type: 'text',
      default: '',
      description: 'Container image to scan (e.g., nginx:latest)'
    }
  ]
};

const CreateWorkflowDialog = ({ open, template, onClose, onSuccess }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    target: '',
    options: {},
    runImmediately: false
  });
  
  // Initialize options with defaults
  React.useEffect(() => {
    if (template && template.id) {
      const options = {};
      const templateOpts = templateOptions[template.id] || [];
      
      templateOpts.forEach(opt => {
        options[opt.key] = opt.default;
      });
      
      setFormData(prev => ({
        ...prev,
        options
      }));
    }
  }, [template]);
  
  const steps = ['Basic Information', 'Configure Options', 'Review & Create'];
  
  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleOptionChange = (key, value) => {
    setFormData({
      ...formData,
      options: {
        ...formData.options,
        [key]: value
      }
    });
  };
  
  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };
  
  const handleClose = () => {
    setActiveStep(0);
    setError(null);
    setLoading(false);
    setFormData({
      target: '',
      options: {},
      runImmediately: false
    });
    onClose();
  };
  
  const validateForm = () => {
    if (!formData.target) {
      setError('Target is required');
      return false;
    }
    
    // Template specific validation
    if (template.id === 'container_security_scan' && 
        !formData.target.includes(':')) {
      setError('Container target should include a tag (e.g., nginx:latest)');
      return false;
    }
    
    setError(null);
    return true;
  };
  
  const handleSubmit = async () => {
    if (!validateForm()) return;
    
    setLoading(true);
    
    try {
      const response = await apiService.createWorkflowFromTemplate(
        template.id,
        formData.target,
        formData.options
      );
      
      const workflowId = response.data.data.workflow.workflow_id;
      
      // If runImmediately is true, execute the workflow
      if (formData.runImmediately) {
        await apiService.executeWorkflow(workflowId);
      }
      
      setLoading(false);
      
      if (onSuccess) {
        onSuccess(response.data.data.workflow);
      }
      
      handleClose();
    } catch (error) {
      setLoading(false);
      setError(error.response?.data?.message || 'Failed to create workflow');
    }
  };
  
  if (!template) return null;
  
  const templateType = getTemplateType(template.id);
  const templateOpts = templateOptions[template.id] || [];
  
  // Render form based on active step
  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <>
            <TemplateHeader templateType={templateType}>
              <SecurityIcon fontSize="large" sx={{ mr: 1 }} />
              <Typography variant="h5">{template.name}</Typography>
            </TemplateHeader>
            
            <Typography variant="body1" paragraph>
              {template.description}
            </Typography>
            
            <Box sx={{ mt: 3 }}>
              <TextField
                name="target"
                label={`Target ${template.target_type.toUpperCase()}`}
                value={formData.target}
                onChange={handleInputChange}
                fullWidth
                required
                variant="outlined"
                placeholder={
                  template.target_type === 'url' ? 'https://example.com' : 
                  template.target_type === 'ip_or_hostname' ? '192.168.1.1 or example.com' :
                  template.target_type === 'container_image' ? 'nginx:latest' : 
                  'Target'
                }
                helperText={
                  template.target_type === 'url' ? 'Enter the URL to scan' : 
                  template.target_type === 'ip_or_hostname' ? 'Enter the IP address or hostname to scan' :
                  template.target_type === 'container_image' ? 'Enter the container image to scan' : 
                  'Enter the target'
                }
              />
            </Box>
          </>
        );
        
      case 1:
        return (
          <>
            <Typography variant="h6" gutterBottom>
              Configure Scan Options
            </Typography>
            
            <Typography variant="body2" color="text.secondary" paragraph>
              Customize the scan options for {template.name}
            </Typography>
            
            <OptionsPaper>
              <Grid container spacing={2}>
                {templateOpts.map((option) => (
                  <Grid item xs={12} md={6} key={option.key}>
                    {option.type === 'select' && (
                      <FormControl fullWidth variant="outlined">
                        <InputLabel id={`${option.key}-label`}>{option.label}</InputLabel>
                        <Select
                          labelId={`${option.key}-label`}
                          value={formData.options[option.key] || option.default}
                          onChange={(e) => handleOptionChange(option.key, e.target.value)}
                          label={option.label}
                        >
                          {option.options.map((opt) => (
                            <MenuItem key={opt.value} value={opt.value}>
                              {opt.label}
                            </MenuItem>
                          ))}
                        </Select>
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                          {option.description}
                        </Typography>
                      </FormControl>
                    )}
                    
                    {option.type === 'text' && (
                      <TextField
                        label={option.label}
                        value={formData.options[option.key] || option.default}
                        onChange={(e) => handleOptionChange(option.key, e.target.value)}
                        fullWidth
                        variant="outlined"
                        helperText={option.description}
                      />
                    )}
                    
                    {option.type === 'multiselect' && (
                      <FormControl fullWidth variant="outlined">
                        <Autocomplete
                          multiple
                          id={`${option.key}-autocomplete`}
                          options={option.options}
                          getOptionLabel={(option) => option.label}
                          value={
                            (formData.options[option.key] || option.default).map(val => 
                              option.options.find(opt => opt.value === val) || { value: val, label: val }
                            )
                          }
                          onChange={(e, newValue) => {
                            handleOptionChange(
                              option.key, 
                              newValue.map(item => item.value)
                            );
                          }}
                          renderInput={(params) => (
                            <TextField
                              {...params}
                              variant="outlined"
                              label={option.label}
                              placeholder="Select options"
                            />
                          )}
                          renderTags={(selected, getTagProps) =>
                            selected.map((option, index) => (
                              <Chip 
                                label={option.label} 
                                {...getTagProps({ index })} 
                                size="small"
                              />
                            ))
                          }
                        />
                        <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                          {option.description}
                        </Typography>
                      </FormControl>
                    )}
                  </Grid>
                ))}
              </Grid>
            </OptionsPaper>
          </>
        );
        
      case 2:
        return (
          <>
            <Typography variant="h6" gutterBottom>
              Review Settings
            </Typography>
            
            <OptionsPaper>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Template
                  </Typography>
                  <Typography variant="body1">
                    {template.name}
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Target
                  </Typography>
                  <Typography variant="body1" sx={{ wordBreak: 'break-all' }}>
                    {formData.target}
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="subtitle2" color="text.secondary">
                    Options
                  </Typography>
                </Grid>
                
                {templateOpts.map((option) => (
                  <Grid item xs={12} sm={6} key={option.key}>
                    <Typography variant="subtitle2">
                      {option.label}
                    </Typography>
                    <Typography variant="body2">
                      {option.type === 'multiselect' 
                        ? (formData.options[option.key] || option.default)
                            .map(val => option.options.find(opt => opt.value === val)?.label || val)
                            .join(', ')
                        : option.type === 'select'
                            ? option.options.find(opt => opt.value === (formData.options[option.key] || option.default))?.label 
                            : formData.options[option.key] || option.default
                      }
                    </Typography>
                  </Grid>
                ))}
              </Grid>
            </OptionsPaper>
            
            <FormControl component="fieldset" sx={{ mt: 2 }}>
              <label>
                <input
                  type="checkbox"
                  checked={formData.runImmediately}
                  onChange={(e) => setFormData({ ...formData, runImmediately: e.target.checked })}
                  style={{ marginRight: '8px' }}
                />
                Run workflow immediately after creation
              </label>
            </FormControl>
          </>
        );
        
      default:
        return null;
    }
  };
  
  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          backgroundImage: 'linear-gradient(rgba(25, 26, 42, 0.7) 0%, rgba(25, 26, 42, 0.9) 100%)',
          backdropFilter: 'blur(10px)',
        }
      }}
    >
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Create New Workflow</Typography>
        <IconButton aria-label="close" onClick={handleClose} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <Divider />
      
      <DialogContent>
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {error && (
          <Alert 
            severity="error" 
            sx={{ mb: 2 }}
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}
        
        {renderStepContent(activeStep)}
      </DialogContent>
      
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button 
          onClick={handleClose}
          disabled={loading}
          variant="outlined"
        >
          Cancel
        </Button>
        
        <Box sx={{ flexGrow: 1 }} />
        
        {activeStep > 0 && (
          <Button 
            onClick={handleBack}
            disabled={loading}
            sx={{ mr: 1 }}
          >
            Back
          </Button>
        )}
        
        {activeStep < steps.length - 1 ? (
          <Button 
            onClick={handleNext}
            variant="contained"
            disabled={activeStep === 0 && !formData.target}
          >
            Next
          </Button>
        ) : (
          <Button 
            onClick={handleSubmit}
            variant="contained"
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : formData.runImmediately ? <PlayArrowIcon /> : <AddIcon />}
          >
            {loading ? 'Creating...' : formData.runImmediately ? 'Create & Run' : 'Create Workflow'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CreateWorkflowDialog;