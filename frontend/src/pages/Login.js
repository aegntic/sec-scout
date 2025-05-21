import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
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
  CircularProgress
} from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import authService from '../services/auth';
import apiService from '../services/api';

const Login = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [needsMfa, setNeedsMfa] = useState(false);
  const [setupRequired, setSetupRequired] = useState(false);
  
  // Check if app needs setup
  useEffect(() => {
    const checkSetup = async () => {
      try {
        const { setup_complete } = await authService.checkSetupStatus();
        setSetupRequired(!setup_complete);
      } catch (error) {
        console.error('Error checking setup status', error);
      }
    };
    
    checkSetup();
  }, []);
  
  // Check if already logged in
  useEffect(() => {
    if (authService.isAuthenticated()) {
      navigate(from, { replace: true });
    }
  }, [from, navigate]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const result = await authService.login(username, password, needsMfa ? mfaCode : null);
      
      if (result.success) {
        navigate(from, { replace: true });
      } else if (result.error === 'MFA code required') {
        setNeedsMfa(true);
        setError('Please enter your MFA code');
      } else {
        setError(result.error);
      }
    } catch (error) {
      setError('Login failed. Please check your credentials.');
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSetupAdmin = async () => {
    navigate('/setup');
  };
  
  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%'
          }}
        >
          <Box
            sx={{
              p: 2,
              borderRadius: '50%',
              bgcolor: 'primary.main',
              color: 'white',
              mb: 2
            }}
          >
            <LockOutlinedIcon />
          </Box>
          
          <Typography component="h1" variant="h5" gutterBottom>
            SecureScout Login
          </Typography>
          
          {setupRequired ? (
            <Box sx={{ width: '100%', mt: 2 }}>
              <Alert severity="info" sx={{ mb: 2 }}>
                No admin account found. Please set up the initial admin account.
              </Alert>
              <Button
                fullWidth
                variant="contained"
                color="primary"
                onClick={handleSetupAdmin}
              >
                Setup Admin Account
              </Button>
            </Box>
          ) : (
            <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%', mt: 1 }}>
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}
              
              <TextField
                margin="normal"
                required
                fullWidth
                id="username"
                label="Username"
                name="username"
                autoComplete="username"
                autoFocus
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={needsMfa || loading}
              />
              
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type={showPassword ? 'text' : 'password'}
                id="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={needsMfa || loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle password visibility"
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
              
              {needsMfa && (
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="mfaCode"
                  label="MFA Code"
                  id="mfaCode"
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value)}
                  disabled={loading}
                />
              )}
              
              <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
                sx={{ mt: 3, mb: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Sign In'}
              </Button>
            </Box>
          )}
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;