import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
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
import Workflows from './pages/Workflows';
import WorkflowDetail from './pages/WorkflowDetail';
import GodMode from './pages/GodMode';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3',
      light: '#64b5f6',
      dark: '#1976d2',
    },
    secondary: {
      main: '#00e676',
      light: '#69f0ae',
      dark: '#00c853',
    },
    background: {
      default: '#0a0e27',
      paper: '#151938',
    },
    error: {
      main: '#ff5252',
      light: '#ff8a80',
      dark: '#d32f2f',
    },
    warning: {
      main: '#ffa726',
      light: '#ffb74d',
      dark: '#f57c00',
    },
    info: {
      main: '#40c4ff',
      light: '#80d8ff',
      dark: '#0091ea',
    },
    success: {
      main: '#00e676',
      light: '#69f0ae',
      dark: '#00c853',
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
      fontSize: '3rem',
      letterSpacing: '-0.02em',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2.5rem',
      letterSpacing: '-0.01em',
    },
    h3: {
      fontWeight: 600,
      fontSize: '2rem',
      letterSpacing: '-0.01em',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.75rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    subtitle1: {
      fontSize: '1.125rem',
      fontWeight: 500,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 8,
          padding: '10px 20px',
          fontSize: '0.95rem',
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(33, 150, 243, 0.3)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #1a237e 0%, #3949ab 100%)',
          backdropFilter: 'blur(10px)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(135deg, rgba(21, 25, 56, 0.9) 0%, rgba(21, 25, 56, 0.95) 100%)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(20px)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(135deg, rgba(21, 25, 56, 0.9) 0%, rgba(21, 25, 56, 0.95) 100%)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 600,
          fontSize: '0.85rem',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          height: 6,
          borderRadius: 3,
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
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

          <Route path="/workflows" element={
            <AuthProtect requiredPermissions={['workflow:read']}>
              <Layout>
                <Workflows />
              </Layout>
            </AuthProtect>
          } />

          <Route path="/workflows/:workflowId" element={
            <AuthProtect requiredPermissions={['workflow:read']}>
              <Layout>
                <WorkflowDetail />
              </Layout>
            </AuthProtect>
          } />

          <Route path="/workflows/:workflowId/results" element={
            <AuthProtect requiredPermissions={['workflow:read']}>
              <Layout>
                <WorkflowDetail />
              </Layout>
            </AuthProtect>
          } />

          <Route path="/godmode" element={
            <AuthProtect requiredPermissions={['admin']}>
              <Layout>
                <GodMode />
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