import React, { useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  IconButton,
  Divider,
  Chip,
  LinearProgress,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  Refresh as RefreshIcon,
  Security as SecurityIcon,
  BugReport as BugReportIcon,
  Assessment as AssessmentIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const SimpleDashboard = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const stats = {
    totalScans: 42,
    activeScans: 2,
    criticalVulns: 3,
    highVulns: 7,
    mediumVulns: 15,
    lowVulns: 28
  };

  const recentScans = [
    { id: 1, target: 'example.com', status: 'completed', severity: 'high' },
    { id: 2, target: 'test.local', status: 'running', severity: 'medium' },
    { id: 3, target: 'api.service.com', status: 'completed', severity: 'critical' }
  ];

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 1000);
  };

  const StatCard = ({ title, value, icon, color }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {icon}
          <Typography variant="h6" sx={{ ml: 1 }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h3" sx={{ color, fontWeight: 'bold' }}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">Security Dashboard</Typography>
        <Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/scan/new')}
            sx={{ mr: 2 }}
          >
            New Scan
          </Button>
          <IconButton onClick={handleRefresh} disabled={isLoading}>
            <RefreshIcon />
          </IconButton>
        </Box>
      </Box>

      {isLoading && <LinearProgress sx={{ mb: 2 }} />}

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Scans"
            value={stats.totalScans}
            icon={<AssessmentIcon />}
            color="primary.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Scans"
            value={stats.activeScans}
            icon={<RefreshIcon />}
            color="info.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Critical Issues"
            value={stats.criticalVulns}
            icon={<WarningIcon />}
            color="error.main"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="High Issues"
            value={stats.highVulns}
            icon={<BugReportIcon />}
            color="warning.main"
          />
        </Grid>

        {/* Recent Scans */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Scans
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {recentScans.map((scan) => (
              <Box
                key={scan.id}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  py: 2,
                  borderBottom: '1px solid rgba(255, 255, 255, 0.08)'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <SecurityIcon sx={{ mr: 2 }} />
                  <Box>
                    <Typography variant="body1">{scan.target}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Scan #{scan.id}
                    </Typography>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip
                    label={scan.status}
                    color={scan.status === 'running' ? 'info' : 'success'}
                    size="small"
                  />
                  <Chip
                    label={scan.severity}
                    color={
                      scan.severity === 'critical' ? 'error' :
                      scan.severity === 'high' ? 'warning' : 'default'
                    }
                    size="small"
                  />
                  <Button
                    size="small"
                    onClick={() => navigate(`/scan/active/${scan.id}`)}
                  >
                    View
                  </Button>
                </Box>
              </Box>
            ))}
          </Paper>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/scan/new')}
                  startIcon={<AddIcon />}
                >
                  New Scan
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/reports')}
                  startIcon={<AssessmentIcon />}
                >
                  View Reports
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/workflows')}
                  startIcon={<SecurityIcon />}
                >
                  Workflows
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => navigate('/godmode')}
                  startIcon={<WarningIcon />}
                  color="warning"
                >
                  GODMODE
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default SimpleDashboard;