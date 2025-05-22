import React from 'react';
import { Box, Typography, Link, Container, Divider } from '@mui/material';
import { styled } from '@mui/material/styles';

const FooterWrapper = styled(Box)(({ theme }) => ({
  marginTop: 'auto',
  paddingTop: theme.spacing(3),
  paddingBottom: theme.spacing(3),
  backgroundColor: theme.palette.background.dark,
  backgroundImage: 'linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.2) 100%)',
  backdropFilter: 'blur(10px)',
  position: 'relative',
  overflow: 'hidden',
  boxShadow: '0 -4px 20px rgba(0,0,0,0.1)',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '1px',
    background: 'linear-gradient(90deg, rgba(108, 99, 255, 0), rgba(108, 99, 255, 0.5), rgba(108, 99, 255, 0))',
  }
}));

const FooterContainer = styled(Container)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  textAlign: 'center',
}));

const FooterDivider = styled(Divider)(({ theme }) => ({
  margin: theme.spacing(2, 0),
  width: '100%',
  background: 'linear-gradient(90deg, rgba(108, 99, 255, 0), rgba(108, 99, 255, 0.3), rgba(108, 99, 255, 0))',
}));

const LogoText = styled(Typography)(({ theme }) => ({
  fontWeight: 700,
  background: 'linear-gradient(90deg, #6C63FF, #00BFA6)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  display: 'inline-block',
}));

const AegnticText = styled(Typography)(({ theme }) => ({
  fontWeight: 700,
  background: 'linear-gradient(90deg, #FF4081, #FF9100)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  display: 'inline-block',
  marginLeft: theme.spacing(0.5),
}));

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <FooterWrapper>
      <FooterContainer maxWidth="lg">
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
          <LogoText variant="h5">SecureScout</LogoText>
        </Box>
        
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Elite Security Testing Platform
        </Typography>
        
        <FooterDivider />
        
        <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 3, mb: 2 }}>
          <Link href="/dashboard" color="textSecondary" underline="hover">
            Dashboard
          </Link>
          <Link href="/scan/new" color="textSecondary" underline="hover">
            New Scan
          </Link>
          <Link href="/reports" color="textSecondary" underline="hover">
            Reports
          </Link>
          <Link href="/settings" color="textSecondary" underline="hover">
            Settings
          </Link>
        </Box>
        
        <Typography variant="body2" color="text.secondary" align="center">
          Copyright © {currentYear} SecureScout. All rights reserved.
        </Typography>
        
        <Typography variant="caption" color="text.secondary" align="center" sx={{ mt: 1, opacity: 0.7 }}>
          An <AegnticText variant="caption">aegntic</AegnticText> project by <Link href="https://aegntic.ai" target="_blank" rel="noopener" color="inherit" underline="hover">aegntic.ai</Link>
        </Typography>
      </FooterContainer>
    </FooterWrapper>
  );
};

export default Footer;