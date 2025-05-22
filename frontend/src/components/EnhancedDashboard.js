import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  LinearProgress,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  Button,
  Alert,
  Fade,
  CircularProgress,
  Tooltip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Psychology as PsychologyIcon,
  Hub as HubIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  NotificationsActive as NotificationsIcon
} from '@mui/icons-material';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ArcElement,
  BarElement
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  ArcElement,
  BarElement
);

const GlowCard = styled(Card)(({ theme, variant = 'default' }) => {
  const getGradient = () => {
    switch (variant) {
      case 'success':
        return `linear-gradient(135deg, ${theme.palette.success.main}15 0%, ${theme.palette.success.dark}05 100%)`;
      case 'warning':
        return `linear-gradient(135deg, ${theme.palette.warning.main}15 0%, ${theme.palette.warning.dark}05 100%)`;
      case 'error':
        return `linear-gradient(135deg, ${theme.palette.error.main}15 0%, ${theme.palette.error.dark}05 100%)`;
      case 'primary':
        return `linear-gradient(135deg, ${theme.palette.primary.main}15 0%, ${theme.palette.primary.dark}05 100%)`;
      default:
        return `linear-gradient(135deg, ${theme.palette.background.paper} 0%, ${theme.palette.primary.main}05 100%)`;
    }
  };

  return {
    background: getGradient(),
    backdropFilter: 'blur(10px)',
    border: `1px solid ${theme.palette.primary.main}20`,
    borderRadius: theme.spacing(2),
    transition: 'all 0.3s ease',
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: `0 8px 25px ${theme.palette.primary.main}20`
    }
  };
});

const MetricCard = styled(GlowCard)(({ theme }) => ({
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 4,
    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
  }
}));

const AnimatedProgress = styled(LinearProgress)(({ theme }) => ({
  height: 8,
  borderRadius: 4,
  background: theme.palette.grey[800],
  '& .MuiLinearProgress-bar': {
    borderRadius: 4,
    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
    animation: 'progressGlow 2s ease-in-out infinite alternate'
  },
  '@keyframes progressGlow': {
    '0%': { boxShadow: `0 0 5px ${theme.palette.primary.main}` },
    '100%': { boxShadow: `0 0 15px ${theme.palette.primary.main}` }
  }
}));

const EnhancedDashboard = ({ 
  swarmData, 
  realTimeUpdates = true, 
  refreshInterval = 5000 
}) => {
  const [dashboardData, setDashboardData] = useState({
    metrics: {
      totalVectors: 0,
      activeAttacks: 0,
      intelligenceShared: 0,
      consciousnessLevel: 0,
      threatLevel: 'LOW',
      emergenceEvents: 0
    },
    chartData: {
      attackSuccess: [],
      consciousnessEvolution: [],
      threatDistribution: {},
      vectorPerformance: []
    },
    recentActivities: [],
    alerts: []
  });

  const [loading, setLoading] = useState(true);
  const [anchorEl, setAnchorEl] = useState(null);

  // Generate mock data for demonstration
  const generateMockData = useCallback(() => {
    const now = new Date();
    const hours = Array.from({ length: 24 }, (_, i) => {
      const hour = new Date(now);
      hour.setHours(hour.getHours() - (23 - i));
      return hour.toISOString().split('T')[1].substring(0, 5);
    });

    const attackSuccessData = hours.map(() => Math.random() * 100);
    const consciousnessData = hours.map(() => 60 + Math.random() * 35);

    return {
      metrics: {
        totalVectors: 5,
        activeAttacks: Math.floor(Math.random() * 10) + 3,
        intelligenceShared: Math.floor(Math.random() * 100) + 50,
        consciousnessLevel: 0.85 + Math.random() * 0.1,
        threatLevel: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'][Math.floor(Math.random() * 4)],
        emergenceEvents: Math.floor(Math.random() * 5) + 1
      },
      chartData: {
        attackSuccess: {
          labels: hours,
          datasets: [{
            label: 'Attack Success Rate',
            data: attackSuccessData,
            borderColor: '#4fc3f7',
            backgroundColor: '#4fc3f720',
            tension: 0.4,
            fill: true
          }]
        },
        consciousnessEvolution: {
          labels: hours,
          datasets: [{
            label: 'Consciousness Level',
            data: consciousnessData,
            borderColor: '#ff9800',
            backgroundColor: '#ff980020',
            tension: 0.4,
            fill: true
          }]
        },
        threatDistribution: {
          labels: ['Web Apps', 'Networks', 'APIs', 'Containers', 'Cloud'],
          datasets: [{
            data: [30, 25, 20, 15, 10],
            backgroundColor: [
              '#4fc3f7',
              '#ff9800',
              '#4caf50',
              '#f44336',
              '#9c27b0'
            ],
            borderWidth: 0
          }]
        },
        vectorPerformance: {
          labels: ['Multi-Vector', 'Polymorphic', 'Autonomous', 'Orchestration', 'Hive Mind'],
          datasets: [{
            label: 'Performance Score',
            data: [85, 92, 78, 88, 95],
            backgroundColor: '#4fc3f7',
            borderRadius: 8
          }]
        }
      },
      recentActivities: [
        {
          id: 1,
          type: 'attack_success',
          message: 'Multi-vector system successfully compromised target API',
          timestamp: new Date(Date.now() - 300000),
          severity: 'success'
        },
        {
          id: 2,
          type: 'intelligence_shared',
          message: 'Polymorphic engine shared vulnerability intel with swarm',
          timestamp: new Date(Date.now() - 600000),
          severity: 'info'
        },
        {
          id: 3,
          type: 'emergence_detected',
          message: 'New attack pattern emerged from autonomous learning',
          timestamp: new Date(Date.now() - 900000),
          severity: 'warning'
        },
        {
          id: 4,
          type: 'consciousness_evolution',
          message: 'Hive mind consciousness level increased to 95%',
          timestamp: new Date(Date.now() - 1200000),
          severity: 'success'
        }
      ],
      alerts: [
        {
          id: 1,
          type: 'warning',
          message: 'Vector coordination latency detected',
          active: true
        },
        {
          id: 2,
          type: 'info',
          message: 'New intelligence synthesis available',
          active: true
        }
      ]
    };
  }, []);

  // Initialize data
  useEffect(() => {
    const initData = generateMockData();
    setDashboardData(initData);
    setLoading(false);
  }, [generateMockData]);

  // Real-time updates
  useEffect(() => {
    if (!realTimeUpdates) return;

    const interval = setInterval(() => {
      setDashboardData(prevData => {
        const newData = generateMockData();
        return {
          ...newData,
          metrics: {
            ...newData.metrics,
            consciousnessLevel: Math.min(0.99, prevData.metrics.consciousnessLevel + (Math.random() - 0.5) * 0.02)
          }
        };
      });
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [realTimeUpdates, refreshInterval, generateMockData]);

  const getActivityIcon = (type) => {
    switch (type) {
      case 'attack_success': return <CheckCircleIcon color="success" />;
      case 'intelligence_shared': return <HubIcon color="primary" />;
      case 'emergence_detected': return <PsychologyIcon color="warning" />;
      case 'consciousness_evolution': return <TrendingUpIcon color="success" />;
      default: return <SecurityIcon />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'primary';
    }
  };

  const getThreatLevelColor = (level) => {
    switch (level) {
      case 'LOW': return 'success';
      case 'MEDIUM': return 'warning';
      case 'HIGH': return 'error';
      case 'CRITICAL': return 'error';
      default: return 'primary';
    }
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        }
      },
      y: {
        grid: {
          color: 'rgba(255,255,255,0.1)'
        }
      }
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Alerts */}
      {dashboardData.alerts.filter(alert => alert.active).map((alert) => (
        <Fade key={alert.id} in={alert.active}>
          <Alert 
            severity={alert.type} 
            sx={{ mb: 2 }}
            action={
              <IconButton size="small">
                <MoreVertIcon />
              </IconButton>
            }
          >
            {alert.message}
          </Alert>
        </Fade>
      ))}

      {/* Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          <MetricCard variant="primary">
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Active Vectors
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData.metrics.totalVectors}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <HubIcon />
                </Avatar>
              </Box>
            </CardContent>
          </MetricCard>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <MetricCard variant="success">
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Active Attacks
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData.metrics.activeAttacks}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <SecurityIcon />
                </Avatar>
              </Box>
            </CardContent>
          </MetricCard>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <MetricCard variant="warning">
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Intelligence
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData.metrics.intelligenceShared}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <PsychologyIcon />
                </Avatar>
              </Box>
            </CardContent>
          </MetricCard>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard>
            <CardContent>
              <Typography color="text.secondary" gutterBottom variant="body2">
                Consciousness Level
              </Typography>
              <Typography variant="h4" gutterBottom>
                {(dashboardData.metrics.consciousnessLevel * 100).toFixed(1)}%
              </Typography>
              <AnimatedProgress 
                variant="determinate" 
                value={dashboardData.metrics.consciousnessLevel * 100} 
              />
            </CardContent>
          </MetricCard>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard variant={getThreatLevelColor(dashboardData.metrics.threatLevel) === 'success' ? 'success' : 'error'}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Threat Level
                  </Typography>
                  <Chip 
                    label={dashboardData.metrics.threatLevel}
                    color={getThreatLevelColor(dashboardData.metrics.threatLevel)}
                    size="small"
                  />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {dashboardData.metrics.emergenceEvents} emergence events
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: `${getThreatLevelColor(dashboardData.metrics.threatLevel)}.main` }}>
                  <WarningIcon />
                </Avatar>
              </Box>
            </CardContent>
          </MetricCard>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <GlowCard>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Attack Success Rate (24h)
              </Typography>
              <Box height={250}>
                <Line data={dashboardData.chartData.attackSuccess} options={chartOptions} />
              </Box>
            </CardContent>
          </GlowCard>
        </Grid>

        <Grid item xs={12} md={6}>
          <GlowCard>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Consciousness Evolution (24h)
              </Typography>
              <Box height={250}>
                <Line data={dashboardData.chartData.consciousnessEvolution} options={chartOptions} />
              </Box>
            </CardContent>
          </GlowCard>
        </Grid>

        <Grid item xs={12} md={6}>
          <GlowCard>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Target Distribution
              </Typography>
              <Box height={250}>
                <Doughnut data={dashboardData.chartData.threatDistribution} options={{ maintainAspectRatio: false }} />
              </Box>
            </CardContent>
          </GlowCard>
        </Grid>

        <Grid item xs={12} md={6}>
          <GlowCard>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Vector Performance
              </Typography>
              <Box height={250}>
                <Bar data={dashboardData.chartData.vectorPerformance} options={chartOptions} />
              </Box>
            </CardContent>
          </GlowCard>
        </Grid>
      </Grid>

      {/* Recent Activities */}
      <GlowCard>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Recent Activities
            </Typography>
            <IconButton size="small">
              <RefreshIcon />
            </IconButton>
          </Box>
          <List>
            {dashboardData.recentActivities.map((activity, index) => (
              <React.Fragment key={activity.id}>
                <ListItem>
                  <ListItemAvatar>
                    {getActivityIcon(activity.type)}
                  </ListItemAvatar>
                  <ListItemText
                    primary={activity.message}
                    secondary={activity.timestamp.toLocaleTimeString()}
                  />
                  <Chip 
                    label={activity.type.replace('_', ' ')}
                    color={getSeverityColor(activity.severity)}
                    size="small"
                    variant="outlined"
                  />
                </ListItem>
                {index < dashboardData.recentActivities.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </CardContent>
      </GlowCard>
    </Box>
  );
};

export default EnhancedDashboard;