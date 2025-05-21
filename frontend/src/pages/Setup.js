import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Alert,
  InputAdornment,
  IconButton,
  CircularProgress,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import SecurityIcon from '@mui/icons-material/Security';
import apiService from '../services/api';
import authService from '../services/auth';

const Setup = () => {
  const navigate = useNavigate();
  
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [formData, setFormData] = useState({
    username: 'admin',
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  // Check if setup is already complete
  useEffect(() => {
    const checkSetup = async () => {
      try {
        const { setup_complete } = await authService.checkSetupStatus();
        if (setup_complete) {
          // Setup is already complete, redirect to login
          navigate('/login');
        }
      } catch (error) {
        console.error('Error checking setup status', error);
      }
    };
    
    checkSetup();
  }, [navigate]);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };
  
  const validateForm = () => {
    // Reset error
    setError('');
    
    // Validate username
    if (formData.username.length < 3) {
      setError('Username must be at least 3 characters');
      return false;
    }
    
    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }
    
    // Validate password
    if (formData.password.length < 12) {
      setError('Password must be at least 12 characters');
      return false;
    }
    
    // Check for uppercase, lowercase, number, and special char
    const hasUpperCase = /[A-Z]/.test(formData.password);
    const hasLowerCase = /[a-z]/.test(formData.password);
    const hasNumber = /[0-9]/.test(formData.password);
    const hasSpecial = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(formData.password);
    
    if (!hasUpperCase || !hasLowerCase || !hasNumber || !hasSpecial) {
      setError('Password must include uppercase, lowercase, number, and special character');
      return false;
    }
    
    // Confirm passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    
    return true;
  };
  
  const handleNext = () => {
    if (validateForm()) {
      setActiveStep(activeStep + 1);
    }
  };
  
  const handleBack = () => {
    setActiveStep(activeStep - 1);
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      // Create the first admin user via direct API call
      // In a real app, this would use a special setup endpoint
      const response = await apiService.createUser({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        role: 'ADMIN'
      });
      
      if (response.data && response.data.user) {
        // Login with the new admin account
        const loginResult = await authService.login(
          formData.username,
          formData.password
        );
        
        if (loginResult.success) {
          // Redirect to dashboard
          navigate('/dashboard');
        } else {
          throw new Error(loginResult.error || 'Login failed after setup');
        }
      }
    } catch (error) {
      console.error('Setup error:', error);
      setError(error.response?.data?.error || 'Failed to create admin account');
    } finally {
      setLoading(false);
    }
  };
  
  // Setup steps
  const steps = ['Admin Account', 'Confirmation'];
  
  // Step content
  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <>
            <Typography variant="subtitle1" gutterBottom align="left">
              Create your administrator account to get started with SecureScout.
            </Typography>
            
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              autoFocus
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              id="password"
              value={formData.password}
              onChange={handleChange}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              name="confirmPassword"
              label="Confirm Password"
              type={showConfirmPassword ? 'text' : 'password'}
              id="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      edge="end"
                    >
                      {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </>
        );
      case 1:
        return (
          <>
            <Typography variant="subtitle1" gutterBottom>
              Please confirm your administrator account details:
            </Typography>
            
            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
              <Typography variant="body1">
                <strong>Username:</strong> {formData.username}
              </Typography>
              <Typography variant="body1">
                <strong>Email:</strong> {formData.email}
              </Typography>
              <Typography variant="body1">
                <strong>Role:</strong> Administrator
              </Typography>
            </Box>
            
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              This account will have full control over the SecureScout application.
              Make sure to keep your credentials secure.
            </Typography>
          </>
        );
      default:
        return 'Unknown step';
    }
  };
  
  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          marginBottom: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            width: '100%',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              mb: 4
            }}
          >
            <SecurityIcon color="primary" fontSize="large" sx={{ mr: 1 }} />
            <Typography component="h1" variant="h4">
              SecureScout Setup
            </Typography>
          </Box>
          
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleSubmit}>
            {getStepContent(activeStep)}
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
              <Button
                disabled={activeStep === 0 || loading}
                onClick={handleBack}
              >
                Back
              </Button>
              
              <Box>
                {activeStep === steps.length - 1 ? (
                  <Button
                    variant="contained"
                    color="primary"
                    type="submit"
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Create Admin Account'}
                  </Button>
                ) : (
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleNext}
                    disabled={loading}
                  >
                    Next
                  </Button>
                )}
              </Box>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Setup;