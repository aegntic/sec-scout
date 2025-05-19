import React from 'react';
import { Container, Typography, Box, Button, Paper } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import HomeIcon from '@mui/icons-material/Home';
import SearchIcon from '@mui/icons-material/Search';

const NotFound = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="md" sx={{ mt: 8, textAlign: 'center' }}>
      <Paper elevation={3} sx={{ p: 5, borderRadius: 2 }}>
        <Typography variant="h1" component="h1" gutterBottom sx={{ fontSize: '5rem', fontWeight: 'bold' }}>
          404
        </Typography>
        <Typography variant="h4" component="h2" gutterBottom>
          Page Not Found
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph sx={{ mb: 4 }}>
          The page you are looking for doesn't exist or has been moved.
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<HomeIcon />}
            onClick={() => navigate('/')}
            size="large"
          >
            Go to Dashboard
          </Button>
          <Button 
            variant="outlined" 
            color="primary"
            startIcon={<SearchIcon />}
            onClick={() => navigate('/scan/new')}
            size="large"
          >
            Start New Scan
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default NotFound;