import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Layout components
import Layout from './components/Layout';
import AuthProtect from './components/AuthProtect';

// Pages
import Dashboard from './pages/Dashboard';
import ScanNew from './pages/ScanNew';
import ScanActive from './pages/ScanActive';
import ScanHistory from './pages/ScanHistory';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';
import Login from './pages/Login';
import Setup from './pages/Setup';
import Unauthorized from './pages/Unauthorized';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3f88c5',
    },
    secondary: {
      main: '#00bfa5',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    error: {
      main: '#f44336',
    },
    warning: {
      main: '#ff9800',
    },
    info: {
      main: '#29b6f6',
    },
    success: {
      main: '#4caf50',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 500,
    },
    h2: {
      fontWeight: 500,
    },
    h3: {
      fontWeight: 500,
    },
    h4: {
      fontWeight: 500,
    },
    h5: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(45deg, #1e3c72 30%, #2a5298 90%)',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/setup" element={<Setup />} />

          {/* Protected routes */}
          <Route path="/" element={
            <AuthProtect>
              <Layout>
                <Dashboard />
              </Layout>
            </AuthProtect>
          } />

          <Route path="/dashboard" element={
            <AuthProtect>
              <Layout>
                <Dashboard />
              </Layout>
            </AuthProtect>
          } />

          <Route path="/scan/new" element={
            <AuthProtect requiredPermissions={['scan:create']}>
              <Layout>
                <ScanNew />
              </Layout>
            </AuthProtect>
          } />

          <Route path="/scan/active" element={
            <AuthProtect requiredPermissions={['scan:read']}>
              <Layout>
                <ScanActive />
              </Layout>
            </AuthProtect>
          } />

          <Route path="/scan/active/:scanId" element={
            <AuthProtect requiredPermissions={['scan:read']}>
              <Layout>
                <ScanActive />
              </Layout>
            </AuthProtect>
          } />

          <Route path="/scan/history" element={
            <AuthProtect requiredPermissions={['scan:read']}>
              <Layout>
                <ScanHistory />
              </Layout>
            </AuthProtect>
          } />

          <Route path="/reports" element={
            <AuthProtect requiredPermissions={['report:read']}>
              <Layout>
                <Reports />
              </Layout>
            </AuthProtect>
          } />

          <Route path="/settings" element={
            <AuthProtect>
              <Layout>
                <Settings />
              </Layout>
            </AuthProtect>
          } />

          {/* Unauthorized route */}
          <Route path="/unauthorized" element={<Unauthorized />} />

          {/* Catch-all route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;