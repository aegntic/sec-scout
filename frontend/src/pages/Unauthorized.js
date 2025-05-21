import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container, 
  Box, 
  Typography, 
  Button, 
  Paper, 
  Alert
} from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';
import authService from '../services/auth';

const Unauthorized = () => {
  const navigate = useNavigate();
  const user = authService.getCurrentUser();
  
  const handleGoBack = () => {
    navigate(-1);
  };
  
  const handleGoHome = () => {
    navigate('/');
  };
  
  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Paper
        elevation={3}
        sx={{
          p: 4,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <LockIcon color="error" sx={{ fontSize: 60, mb: 2 }} />
        
        <Typography variant="h4" component="h1" gutterBottom>
          Access Denied
        </Typography>
        
        <Alert severity="error" sx={{ width: '100%', mb: 3 }}>
          You don't have permission to access this resource.
        </Alert>
        
        <Typography variant="body1" align="center" sx={{ mb: 3 }}>
          {user 
            ? `Your account (${user.username}) does not have the required permissions for this action.`
            : 'You need to be logged in with appropriate permissions to access this resource.'}
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button 
            variant="outlined" 
            color="primary" 
            onClick={handleGoBack}
          >
            Go Back
          </Button>
          
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleGoHome}
          >
            Go to Dashboard
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Unauthorized;