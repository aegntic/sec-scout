import React, { useState, useEffect } from 'react';
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
  Divider
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import VisibilityIcon from '@mui/icons-material/Visibility';
import SecurityIcon from '@mui/icons-material/Security';
import BugReportIcon from '@mui/icons-material/BugReport';
import AssessmentIcon from '@mui/icons-material/Assessment';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import { useNavigate } from 'react-router-dom';
import { Bar, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

// Register ChartJS components
ChartJS.register(ArcElement, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

// Mock data for demo
const mockStats = {
  scansToday: 3,
  activeScans: 1,
  totalScans: 42,
  vulnerabilities: {
    critical: 2,
    high: 5,
    medium: 8,
    low: 12,
    info: 23
  },
  recentScans: [
    { 
      id: 'abc123', 
      target: 'https://example.com', 
      date: '2025-05-17 14:30:22', 
      status: 'completed',
      vulnerabilityCount: 12
    },
    { 
      id: 'def456', 
      target: 'https://test-application.net',
      date: '2025-05-17 09:15:07', 
      status: 'completed',
      vulnerabilityCount: 3
    },
    { 
      id: 'ghi789', 
      target: 'https://staging-api.example.org',  
      date: '2025-05-16 16:45:33', 
      status: 'in_progress',
      vulnerabilityCount: 8
    }
  ]
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(mockStats);
  const [isLoading, setIsLoading] = useState(false);

  // Simulate fetch data
  const fetchData = () => {
    setIsLoading(true);
    // In a real app, this would be an API call
    setTimeout(() => {
      setStats(mockStats);
      setIsLoading(false);
    }, 1000);
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Navigate to new scan page
  const handleNewScan = () => {
    navigate('/scan/new');
  };

  // View specific scan
  const handleViewScan = (scanId) => {
    navigate(`/scan/active/${scanId}`);
  };

  // Chart configurations
  const severityChartData = {
    labels: ['Critical', 'High', 'Medium', 'Low', 'Info'],
    datasets: [
      {
        data: [
          stats.vulnerabilities.critical,
          stats.vulnerabilities.high,
          stats.vulnerabilities.medium,
          stats.vulnerabilities.low,
          stats.vulnerabilities.info
        ],
        backgroundColor: [
          '#e74c3c',
          '#e67e22',
          '#f39c12',
          '#3498db',
          '#95a5a6'
        ],
        borderWidth: 0,
      },
    ],
  };

  const scanHistoryData = {
    labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
    datasets: [
      {
        label: 'Scans Performed',
        data: [3, 5, 2, 8, 6, 1, 4],
        backgroundColor: 'rgba(63, 136, 197, 0.6)',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          color: '#f1f1f1'
        }
      }
    }
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#f1f1f1'
        }
      },
      title: {
        display: true,
        text: 'Weekly Scan Activity',
        color: '#f1f1f1'
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: '#f1f1f1'
        }
      },
      x: {
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        },
        ticks: {
          color: '#f1f1f1'
        }
      }
    }
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Box>
          <Button
            variant="outlined"
            color="primary"
            onClick={fetchData}
            startIcon={<RefreshIcon />}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleNewScan}
            startIcon={<AddIcon />}
          >
            New Scan
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <SecurityIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6" component="div">
                Active Scans
              </Typography>
            </Box>
            <Typography variant="h3" component="div" sx={{ my: 1, fontWeight: 'bold' }}>
              {stats.activeScans}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {stats.scansToday} scans today
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <AssessmentIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6" component="div">
                Total Scans
              </Typography>
            </Box>
            <Typography variant="h3" component="div" sx={{ my: 1, fontWeight: 'bold' }}>
              {stats.totalScans}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Across all projects
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <LockOpenIcon sx={{ color: '#e74c3c', mr: 1 }} />
              <Typography variant="h6" component="div">
                Critical Issues
              </Typography>
            </Box>
            <Typography variant="h3" component="div" sx={{ my: 1, fontWeight: 'bold', color: '#e74c3c' }}>
              {stats.vulnerabilities.critical}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Require immediate attention
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper elevation={3} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <BugReportIcon color="warning" sx={{ mr: 1 }} />
              <Typography variant="h6" component="div">
                Total Vulnerabilities
              </Typography>
            </Box>
            <Typography variant="h3" component="div" sx={{ my: 1, fontWeight: 'bold' }}>
              {Object.values(stats.vulnerabilities).reduce((sum, current) => sum + current, 0)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Across all scans
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Scan Activity
            </Typography>
            <Box sx={{ height: 300 }}>
              <Bar data={scanHistoryData} options={barChartOptions} />
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Vulnerabilities by Severity
            </Typography>
            <Box sx={{ height: 300, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <Doughnut data={severityChartData} options={chartOptions} />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Scans */}
      <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Scans
        </Typography>
        <Grid container spacing={2}>
          {stats.recentScans.map((scan) => (
            <Grid item xs={12} md={4} key={scan.id}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Typography variant="subtitle1" component="div">
                      {scan.target}
                    </Typography>
                    <IconButton 
                      size="small" 
                      onClick={() => handleViewScan(scan.id)}
                      title="View scan details"
                    >
                      <VisibilityIcon fontSize="small" />
                    </IconButton>
                  </Box>
                  <Typography variant="caption" color="text.secondary" display="block">
                    {scan.date}
                  </Typography>
                  <Divider sx={{ my: 1 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="body2" component="div">
                        Status: <span style={{ 
                          color: scan.status === 'completed' ? '#4caf50' : '#f39c12'
                        }}>{scan.status === 'completed' ? 'Completed' : 'In Progress'}</span>
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" component="div">
                        Issues: <strong>{scan.vulnerabilityCount}</strong>
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Container>
  );
};

export default Dashboard;