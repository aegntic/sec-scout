import React, { useState } from 'react';
import { Container, Typography, Button, Box, Paper, TextField, Alert } from '@mui/material';

const TestPage = () => {
  const [count, setCount] = useState(0);
  const [message, setMessage] = useState('');
  const [error, setError] = useState(null);

  const handleClick = () => {
    try {
      setCount(count + 1);
      setMessage(`Button clicked ${count + 1} times`);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          SecureScout Test Page
        </Typography>
        
        <Paper sx={{ p: 3, mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            Basic Functionality Test
          </Typography>
          
          <Box sx={{ mt: 2 }}>
            <Button 
              variant="contained" 
              onClick={handleClick}
              sx={{ mr: 2 }}
            >
              Test Button
            </Button>
            
            <Typography variant="body1" sx={{ mt: 2 }}>
              Click count: {count}
            </Typography>
            
            {message && (
              <Alert severity="info" sx={{ mt: 2 }}>
                {message}
              </Alert>
            )}
            
            {error && (
              <Alert severity="error" sx={{ mt: 2 }}>
                Error: {error}
              </Alert>
            )}
          </Box>
          
          <Box sx={{ mt: 3 }}>
            <TextField
              fullWidth
              label="Test Input"
              variant="outlined"
              onChange={(e) => setMessage(`Input value: ${e.target.value}`)}
            />
          </Box>
        </Paper>
        
        <Paper sx={{ p: 3, mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            System Status
          </Typography>
          <Typography variant="body2">
            • React: Working ✓
          </Typography>
          <Typography variant="body2">
            • Material-UI: Working ✓
          </Typography>
          <Typography variant="body2">
            • State Management: Working ✓
          </Typography>
          <Typography variant="body2">
            • Event Handlers: Working ✓
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
};

export default TestPage;