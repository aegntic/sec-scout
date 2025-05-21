import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  Divider,
  CircularProgress,
  IconButton,
  Grid,
  Chip,
  Tabs,
  Tab,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  LinearProgress,
  Tooltip,
  Menu,
  MenuItem,
  Badge,
  Fade,
  Card,
  CardContent,
  Skeleton,
  Avatar,
  useTheme,
  useMediaQuery,
  Breadcrumbs,
  Link,
  Stack,
  Collapse,
} from '@mui/material';
import { styled, alpha } from '@mui/material/styles';
import RefreshIcon from '@mui/icons-material/Refresh';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import DeleteIcon from '@mui/icons-material/Delete';
import WebIcon from '@mui/icons-material/Web';
import ShareIcon from '@mui/icons-material/Share';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import NotificationsOffIcon from '@mui/icons-material/NotificationsOff';
import HomeIcon from '@mui/icons-material/Home';
import PlaylistPlayIcon from '@mui/icons-material/PlaylistPlay';
import TimelineIcon from '@mui/icons-material/Timeline';
import { formatDistanceToNow, formatRelative, format } from 'date-fns';
import apiService from '../services/api';

// Components
import TaskGraph from '../components/Workflows/TaskGraph';
import FindingsList from '../components/Workflows/FindingsList';
import WorkflowTimeline from '../components/Workflows/WorkflowTimeline';

// Styled components
const StyledTabs = styled(Tabs)(({ theme }) => ({
  '& .MuiTabs-indicator': {
    backgroundColor: theme.palette.primary.main,
    height: 3,
    borderRadius: 1.5,
  },
}));

const StyledTab = styled(Tab)(({ theme }) => ({
  textTransform: 'none',
  fontWeight: 600,
  padding: theme.spacing(1.5, 3),
  minWidth: 0,
  position: 'relative',
  '&.Mui-selected': {
    color: theme.palette.primary.main,
  },
}));

const TabBadge = styled(Badge)(({ theme }) => ({
  '& .MuiBadge-badge': {
    right: -3,
    top: -2,
    border: `2px solid ${theme.palette.background.paper}`,
    padding: '0 4px',
  },
}));

const TabPanel = ({ children, value, index, ...other }) => (
  <Box
    role="tabpanel"
    hidden={value !== index}
    id={`tabpanel-${index}`}
    aria-labelledby={`tab-${index}`}
    {...other}
    sx={{ py: 3 }}
  >
    {value === index && children}
  </Box>
);

const StatusChip = styled(Chip)(({ theme, status }) => {
  const statusColors = {
    pending: theme.palette.grey[500],
    running: theme.palette.primary.main,
    completed: theme.palette.success.main,
    failed: theme.palette.error.main,
    cancelled: theme.palette.warning.main,
  };
  
  return {
    backgroundColor: `${statusColors[status] || theme.palette.grey[500]}20`,
    color: statusColors[status] || theme.palette.grey[500],
    fontWeight: 600,
    '& .MuiChip-label': {
      padding: '0 8px',
    }
  };
});

const StatusAvatar = styled(Avatar)(({ theme, status }) => {
  const statusColors = {
    pending: theme.palette.grey[500],
    running: theme.palette.primary.main,
    completed: theme.palette.success.main,
    failed: theme.palette.error.main,
    cancelled: theme.palette.warning.main,
  };
  
  return {
    backgroundColor: alpha(statusColors[status] || theme.palette.grey[500], 0.2),
    color: statusColors[status] || theme.palette.grey[500],
    width: 40,
    height: 40,
  };
});

const InfoCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
  backgroundColor: alpha(theme.palette.background.paper, 0.7),
  backdropFilter: 'blur(20px)',
  display: 'flex',
  flexDirection: 'column',
  borderRadius: theme.shape.borderRadius,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  transition: 'all 0.3s ease',
  '&:hover': {
    boxShadow: `0 0 0 1px ${alpha(theme.palette.primary.main, 0.2)}`,
  },
}));

const HeaderCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  backgroundColor: alpha(theme.palette.background.paper, 0.7),
  backdropFilter: 'blur(20px)',
  borderRadius: theme.shape.borderRadius,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  marginBottom: theme.spacing(3),
  overflow: 'hidden',
  position: 'relative',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '4px',
    backgroundImage: 'linear-gradient(to right, #3f88c5, #4caf50)',
    opacity: 0.8,
  },
}));

const InfoItem = styled(Box)(({ theme }) => ({
  display: 'flex',
  marginBottom: theme.spacing(1),
}));

const InfoLabel = styled(Typography)(({ theme }) => ({
  fontWeight: 600,
  minWidth: '120px',
  color: theme.palette.text.secondary,
}));

const InfoValue = styled(Typography)(({ theme }) => ({
  color: theme.palette.text.primary,
}));

const TagsContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexWrap: 'wrap',
  gap: theme.spacing(0.5),
  marginTop: theme.spacing(1),
}));

const ContentContainer = styled(Paper)(({ theme }) => ({
  borderRadius: theme.shape.borderRadius,
  overflow: 'hidden',
  backgroundColor: alpha(theme.palette.background.paper, 0.7),
  backdropFilter: 'blur(20px)',
  flexGrow: 1,
}));

const PulsingDot = styled('span')(({ theme }) => ({
  display: 'inline-block',
  width: 8,
  height: 8,
  backgroundColor: theme.palette.primary.main,
  borderRadius: '50%',
  marginRight: 6,
  animation: 'pulse 1.5s infinite',
  '@keyframes pulse': {
    '0%': {
      transform: 'scale(0.95)',
      boxShadow: '0 0 0 0 rgba(63, 136, 197, 0.7)',
    },
    '70%': {
      transform: 'scale(1)',
      boxShadow: '0 0 0 6px rgba(63, 136, 197, 0)',
    },
    '100%': {
      transform: 'scale(0.95)',
    },
  },
}));

const ActionButton = styled(Button)(({ theme }) => ({
  boxShadow: 'none',
  textTransform: 'none',
  padding: theme.spacing(1, 2),
  borderRadius: theme.shape.borderRadius,
  fontWeight: 600,
  transition: 'all 0.2s',
  '&:hover': {
    boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
    transform: 'translateY(-1px)',
  },
}));

const StatusDivider = styled(Divider)(({ theme, status }) => {
  const statusColors = {
    pending: theme.palette.grey[400],
    running: theme.palette.primary.main,
    completed: theme.palette.success.main,
    failed: theme.palette.error.main,
    cancelled: theme.palette.warning.main,
  };
  
  return {
    '&::before, &::after': {
      borderColor: alpha(statusColors[status] || theme.palette.divider, 0.3),
    },
    color: statusColors[status] || theme.palette.text.secondary,
  };
});

const NavBreadcrumbs = styled(Breadcrumbs)(({ theme }) => ({
  '& .MuiTypography-root': {
    display: 'flex',
    alignItems: 'center',
  },
  '& .MuiBreadcrumbs-separator': {
    color: theme.palette.text.disabled,
  },
}));

const REFRESH_INTERVAL = 3000; // 3 seconds for running workflows

const WorkflowDetail = () => {
  const { workflowId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));
  
  const [tabValue, setTabValue] = useState(0);
  const [workflow, setWorkflow] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statusPolling, setStatusPolling] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [findings, setFindings] = useState([]);
  const [loadingFindings, setLoadingFindings] = useState(false);
  const [showNotifications, setShowNotifications] = useState(true);
  const [actionsMenuAnchor, setActionsMenuAnchor] = useState(null);
  const [showFullInfo, setShowFullInfo] = useState(!isSmallScreen);
  const [copySuccess, setCopySuccess] = useState(false);
  const [findingsCount, setFindingsCount] = useState({ total: 0, critical: 0, high: 0 });
  const [lastUpdated, setLastUpdated] = useState(null);
  
  // Get initial tab from URL if available
  useEffect(() => {
    const path = location.pathname;
    if (path.endsWith('/results')) {
      setTabValue(2); // Findings tab
    } else if (path.endsWith('/tasks')) {
      setTabValue(1); // Tasks tab
    }
  }, [location.pathname]);
  
  // Fetch workflow details
  const fetchWorkflow = async (showSuccessMessage = false) => {
    try {
      const response = await apiService.getWorkflow(workflowId);
      setWorkflow(response.data.data.workflow);
      setLastUpdated(new Date());
      
      // If workflow is running, start polling for status updates
      if (response.data.data.workflow.status === 'running') {
        startStatusPolling();
      } else {
        stopStatusPolling();
      }
      
      if (showSuccessMessage) {
        setSuccess('Workflow data refreshed');
      }
      
      // Update findings count from summary if available
      if (response.data.data.workflow.findings_summary) {
        const summary = response.data.data.workflow.findings_summary;
        setFindingsCount({
          total: Object.values(summary).reduce((a, b) => a + b, 0),
          critical: summary.critical || 0,
          high: summary.high || 0,
        });
      }
    } catch (error) {
      setError('Failed to load workflow details');
      console.error('Error fetching workflow:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch findings
  const fetchFindings = async (showSuccessMessage = false) => {
    if (tabValue === 2) { // Only fetch findings when on findings tab
      setLoadingFindings(true);
      try {
        const response = await apiService.getWorkflowFindings(workflowId);
        setFindings(response.data.data.findings);
        
        // Update findings count
        const findings = response.data.data.findings;
        const criticalCount = findings.filter(f => f.severity === 'critical').length;
        const highCount = findings.filter(f => f.severity === 'high').length;
        
        setFindingsCount({
          total: findings.length,
          critical: criticalCount,
          high: highCount,
        });
        
        if (showSuccessMessage) {
          setSuccess('Findings data refreshed');
        }
      } catch (error) {
        setError('Failed to load findings');
        console.error('Error fetching findings:', error);
      } finally {
        setLoadingFindings(false);
      }
    }
  };

  // Start polling for status updates when workflow is running
  const startStatusPolling = () => {
    if (!statusPolling) {
      const interval = setInterval(fetchWorkflow, REFRESH_INTERVAL);
      setStatusPolling(interval);
    }
  };

  // Stop polling when workflow is no longer running
  const stopStatusPolling = () => {
    if (statusPolling) {
      clearInterval(statusPolling);
      setStatusPolling(null);
    }
  };

  // Initialize data loading
  useEffect(() => {
    fetchWorkflow();
    
    // Cleanup polling on unmount
    return () => {
      stopStatusPolling();
    };
  }, [workflowId]);
  
  // Update page title
  useEffect(() => {
    if (workflow) {
      document.title = `${workflow.name} | SecureScout Workflow`;
    } else {
      document.title = 'Workflow Details | SecureScout';
    }
    
    return () => {
      document.title = 'SecureScout';
    };
  }, [workflow]);

  // Handle tab changes and load data for the selected tab
  useEffect(() => {
    if (tabValue === 2) {
      fetchFindings();
    }
    
    // Update URL based on selected tab
    let newPath;
    if (tabValue === 0) {
      newPath = `/workflows/${workflowId}`;
    } else if (tabValue === 1) {
      newPath = `/workflows/${workflowId}/tasks`;
    } else if (tabValue === 2) {
      newPath = `/workflows/${workflowId}/results`;
    }
    
    if (location.pathname !== newPath) {
      navigate(newPath, { replace: true });
    }
  }, [tabValue, workflowId, navigate, location.pathname]);
  
  // Update for responsive design
  useEffect(() => {
    setShowFullInfo(!isSmallScreen);
  }, [isSmallScreen]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleGoBack = () => {
    navigate('/workflows');
  };

  const handleRefresh = () => {
    fetchWorkflow(true);
    if (tabValue === 2) {
      fetchFindings(true);
    }
  };

  const handleExecuteWorkflow = async () => {
    try {
      await apiService.executeWorkflow(workflowId);
      setSuccess('Workflow execution started');
      fetchWorkflow();
    } catch (error) {
      setError('Failed to execute workflow');
    }
  };

  const handleCancelWorkflow = async () => {
    try {
      await apiService.cancelWorkflow(workflowId);
      setSuccess('Workflow cancelled');
      fetchWorkflow();
    } catch (error) {
      setError('Failed to cancel workflow');
    }
  };

  const handleDeleteWorkflow = () => {
    setDeleteConfirmOpen(true);
  };

  const confirmDeleteWorkflow = async () => {
    try {
      await apiService.deleteWorkflow(workflowId);
      setSuccess('Workflow deleted');
      setDeleteConfirmOpen(false);
      navigate('/workflows');
    } catch (error) {
      setError('Failed to delete workflow');
      setDeleteConfirmOpen(false);
    }
  };
  
  const handleExportResults = async (format = 'json') => {
    try {
      const response = await apiService.exportWorkflowResults(workflowId, format);
      
      // Create a blob and download it
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `workflow_${workflowId}_results.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      setSuccess(`Results exported as ${format.toUpperCase()}`);
    } catch (error) {
      setError('Failed to export results');
    }
    setActionsMenuAnchor(null);
  };
  
  const handleCopyId = () => {
    navigator.clipboard.writeText(workflowId);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
    setActionsMenuAnchor(null);
  };
  
  const handleToggleNotifications = () => {
    setShowNotifications(!showNotifications);
    if (!showNotifications) {
      // Renable notifications and refresh
      handleRefresh();
    }
    setActionsMenuAnchor(null);
  };
  
  const handleActionsMenuOpen = (event) => {
    setActionsMenuAnchor(event.currentTarget);
  };
  
  const handleActionsMenuClose = () => {
    setActionsMenuAnchor(null);
  };
  
  const toggleShowFullInfo = () => {
    setShowFullInfo(!showFullInfo);
  };

  // Format date time for display
  const formatDateTime = (dateString) => {
    if (!dateString) return 'Not available';
    try {
      const date = new Date(dateString);
      return format(date, 'MMM d, yyyy h:mm:ss a');
    } catch (e) {
      return dateString;
    }
  };
  
  // Format relative time for display
  const formatRelativeTime = (dateString) => {
    if (!dateString) return 'Not available';
    try {
      const date = new Date(dateString);
      return formatDistanceToNow(date, { addSuffix: true });
    } catch (e) {
      return dateString;
    }
  };

  // Calculate time elapsed
  const getTimeElapsed = (startTime, endTime) => {
    if (!startTime) return 'Not started';
    
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    
    const elapsedMs = end - start;
    const seconds = Math.floor(elapsedMs / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  };
  
  // Get status icon based on workflow status
  const getStatusIcon = (status) => {
    switch (status) {
      case 'running':
        return <PulsingDot />;
      case 'completed':
        return '✓';
      case 'failed':
        return '✗';
      case 'cancelled':
        return '⊘';
      default:
        return '⋯';
    }
  };
  
  // Loading state
  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ py: 4 }}>
          <Skeleton variant="text" width="60%" height={40} sx={{ mb: 1 }} />
          <Skeleton variant="text" width="40%" height={24} />
          
          <Grid container spacing={3} sx={{ mt: 3 }}>
            <Grid item xs={12} md={4}>
              <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 2 }} />
            </Grid>
            <Grid item xs={12} md={8}>
              <Skeleton variant="rectangular" height={60} sx={{ borderRadius: 1, mb: 2 }} />
              <Skeleton variant="rectangular" height={340} sx={{ borderRadius: 2 }} />
            </Grid>
          </Grid>
        </Box>
      </Container>
    );
  }

  // Error state
  if (!workflow) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ mt: 4 }}>
          <Alert 
            severity="error"
            sx={{ 
              borderRadius: 2, 
              mb: 3,
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}
          >
            <Typography variant="h6" sx={{ mb: 1 }}>Workflow Not Found</Typography>
            <Typography variant="body1">
              The workflow you're looking for could not be found or failed to load. It may have been deleted or you might not have permission to view it.
            </Typography>
          </Alert>
          <Button
            variant="outlined"
            startIcon={<ArrowBackIcon />}
            onClick={handleGoBack}
            sx={{ 
              textTransform: 'none',
              fontWeight: 600 
            }}
          >
            Back to Workflows
          </Button>
        </Box>
      </Container>
    );
  }

  // Calculate progress percentage
  const progressPercentage = workflow.task_count > 0
    ? Math.round((workflow.completed_tasks / workflow.task_count) * 100)
    : 0;

  return (
    <Container maxWidth="xl">
      {/* Breadcrumb navigation */}
      <NavBreadcrumbs aria-label="breadcrumb" sx={{ pt: 2, mb: 2 }}>
        <Link
          underline="hover"
          color="inherit"
          href="#"
          onClick={(e) => { e.preventDefault(); navigate('/'); }}
          sx={{ display: 'flex', alignItems: 'center' }}
        >
          <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Home
        </Link>
        <Link
          underline="hover"
          color="inherit"
          href="#"
          onClick={(e) => { e.preventDefault(); navigate('/workflows'); }}
          sx={{ display: 'flex', alignItems: 'center' }}
        >
          <PlaylistPlayIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Workflows
        </Link>
        <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center' }}>
          {workflow.name}
        </Typography>
      </NavBreadcrumbs>
      
      {/* Header Card */}
      <HeaderCard elevation={1}>
        <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, alignItems: { sm: 'center' }, justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: { xs: 2, sm: 0 } }}>
            <StatusAvatar status={workflow.status}>
              {getStatusIcon(workflow.status)}
            </StatusAvatar>
            <Box sx={{ ml: 2 }}>
              <Typography variant="h4" component="h1" sx={{ lineHeight: 1.3 }}>
                {workflow.name}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 1, mt: 0.5 }}>
                <StatusChip 
                  size="small" 
                  label={workflow.status?.toUpperCase()} 
                  status={workflow.status} 
                />
                {lastUpdated && (
                  <Tooltip title={`Last updated: ${formatDateTime(lastUpdated)}`}>
                    <Box sx={{ display: 'flex', alignItems: 'center', typography: 'caption', color: 'text.secondary' }}>
                      <AccessTimeIcon fontSize="inherit" sx={{ mr: 0.5 }} />
                      Updated {formatDistanceToNow(lastUpdated, { addSuffix: true })}
                    </Box>
                  </Tooltip>
                )}
              </Box>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: { xs: 'flex-start', sm: 'flex-end' } }}>
            <Tooltip title="Refresh">
              <IconButton 
                color="primary" 
                onClick={handleRefresh}
                sx={{ bgcolor: 'background.paper', boxShadow: 1 }}
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            
            {['pending', 'completed', 'failed', 'cancelled'].includes(workflow.status) && (
              <ActionButton 
                variant="contained" 
                startIcon={<PlayArrowIcon />}
                onClick={handleExecuteWorkflow}
                sx={{ 
                  bgcolor: 'primary.main',
                  '&:hover': { bgcolor: 'primary.dark' } 
                }}
              >
                Execute
              </ActionButton>
            )}
            
            {workflow.status === 'running' && (
              <ActionButton 
                variant="contained" 
                color="error"
                startIcon={<StopIcon />}
                onClick={handleCancelWorkflow}
              >
                Cancel
              </ActionButton>
            )}
            
            <IconButton 
              aria-label="more actions" 
              aria-controls="workflow-actions-menu" 
              aria-haspopup="true"
              onClick={handleActionsMenuOpen}
              sx={{ bgcolor: 'background.paper', boxShadow: 1 }}
            >
              <MoreVertIcon />
            </IconButton>
            <Menu
              id="workflow-actions-menu"
              anchorEl={actionsMenuAnchor}
              keepMounted
              open={Boolean(actionsMenuAnchor)}
              onClose={handleActionsMenuClose}
            >
              <MenuItem onClick={handleCopyId}>
                <ContentCopyIcon fontSize="small" sx={{ mr: 1 }} />
                Copy Workflow ID
              </MenuItem>
              <MenuItem onClick={() => handleExportResults('json')}>
                <CloudDownloadIcon fontSize="small" sx={{ mr: 1 }} />
                Export Results (JSON)
              </MenuItem>
              <MenuItem onClick={() => handleExportResults('csv')}>
                <CloudDownloadIcon fontSize="small" sx={{ mr: 1 }} />
                Export Results (CSV)
              </MenuItem>
              <MenuItem onClick={handleToggleNotifications}>
                {showNotifications ? (
                  <>
                    <NotificationsOffIcon fontSize="small" sx={{ mr: 1 }} />
                    Disable Notifications
                  </>
                ) : (
                  <>
                    <NotificationsActiveIcon fontSize="small" sx={{ mr: 1 }} />
                    Enable Notifications
                  </>
                )}
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleDeleteWorkflow} sx={{ color: 'error.main' }}>
                <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
                Delete Workflow
              </MenuItem>
            </Menu>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'flex-start', flexDirection: { xs: 'column', md: 'row' }, gap: { xs: 2, md: 4 }, mb: 2 }}>
          {/* Left column */}
          <Box sx={{ flex: 3 }}>
            <Typography variant="body1" sx={{ mb: 2, color: 'text.secondary' }}>
              {workflow.description || 'No description provided for this workflow.'}
            </Typography>
            
            {workflow.target && (
              <Chip
                icon={<WebIcon />}
                label={workflow.target}
                sx={{
                  fontFamily: 'monospace',
                  fontSize: '0.85rem',
                  height: 32,
                  px: 1,
                  mb: 2,
                  border: '1px solid',
                  borderColor: 'divider',
                  backgroundColor: 'transparent',
                }}
              />
            )}
            
            {/* Progress bar for running workflows */}
            {workflow.status === 'running' && (
              <Fade in={true}>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2" color="text.secondary">
                      Execution Progress
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {progressPercentage}%
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={progressPercentage}
                    sx={{ 
                      height: 8, 
                      borderRadius: 4, 
                      mb: 0.5,
                      backgroundColor: alpha(theme.palette.primary.main, 0.1)
                    }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {workflow.completed_tasks} of {workflow.task_count} tasks completed
                    {workflow.failed_tasks > 0 && ` (${workflow.failed_tasks} failed)`}
                  </Typography>
                </Box>
              </Fade>
            )}
            
            {workflow.status === 'completed' && (
              <Box>
                <StatusDivider status="completed">
                  <Chip
                    label={`Completed ${formatRelativeTime(workflow.end_time)}`}
                    size="small"
                    variant="outlined"
                    color="success"
                  />
                </StatusDivider>
              </Box>
            )}
            
            {workflow.status === 'failed' && (
              <Box>
                <StatusDivider status="failed">
                  <Chip
                    label={`Failed ${formatRelativeTime(workflow.end_time)}`}
                    size="small"
                    variant="outlined"
                    color="error"
                  />
                </StatusDivider>
              </Box>
            )}
          </Box>
          
          {/* Right column - Key metrics */}
          <Box sx={{ 
            flex: 2, 
            display: 'flex', 
            flexDirection: { xs: 'row', sm: 'row', md: 'column' },
            flexWrap: { xs: 'wrap', sm: 'nowrap' },
            gap: 2,
            justifyContent: 'flex-start',
            alignItems: { xs: 'flex-start', md: 'stretch' }
          }}>
            {/* Duration card */}
            <Card sx={{ 
              minWidth: { xs: 140, sm: 160 }, 
              flex: { xs: '1 0 30%', md: 'auto' },
              backgroundColor: alpha(theme.palette.background.paper, 0.4),
              backdropFilter: 'blur(10px)',
            }}>
              <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
                <Typography variant="overline" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                  Duration
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 600, fontFamily: 'monospace' }}>
                  {getTimeElapsed(workflow.start_time, workflow.end_time)}
                </Typography>
              </CardContent>
            </Card>
            
            {/* Tasks card */}
            <Card sx={{ 
              minWidth: { xs: 140, sm: 160 }, 
              flex: { xs: '1 0 30%', md: 'auto' },
              backgroundColor: alpha(theme.palette.background.paper, 0.4),
              backdropFilter: 'blur(10px)',
            }}>
              <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
                <Typography variant="overline" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                  Tasks
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {workflow.completed_tasks}/{workflow.task_count}
                  {workflow.failed_tasks > 0 && 
                    <Box component="span" sx={{ color: 'error.main', ml: 1 }}>
                      ({workflow.failed_tasks} failed)
                    </Box>
                  }
                </Typography>
              </CardContent>
            </Card>
            
            {/* Findings card */}
            <Card sx={{ 
              minWidth: { xs: 140, sm: 160 }, 
              flex: { xs: '1 0 30%', md: 'auto' },
              backgroundColor: alpha(theme.palette.background.paper, 0.4),
              backdropFilter: 'blur(10px)',
            }}>
              <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
                <Typography variant="overline" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                  Findings
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {findingsCount.total}
                  {(findingsCount.critical > 0 || findingsCount.high > 0) && (
                    <Box component="span" sx={{ ml: 1 }}>
                      {findingsCount.critical > 0 && 
                        <Chip 
                          size="small" 
                          label={findingsCount.critical} 
                          color="error" 
                          sx={{ height: 20, mr: 0.5 }}
                        />
                      }
                      {findingsCount.high > 0 && 
                        <Chip 
                          size="small" 
                          label={findingsCount.high} 
                          color="warning"
                          sx={{ height: 20 }}
                        />
                      }
                    </Box>
                  )}
                </Typography>
              </CardContent>
            </Card>
          </Box>
        </Box>
      </HeaderCard>
      
      {/* Main content grid */}
      <Grid container spacing={3}>
        {/* Left side - Workflow info */}
        <Grid item xs={12} md={4}>
          <Stack spacing={3}>
            {/* Workflow Information card */}
            <InfoCard elevation={0}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h6" gutterBottom>
                  Workflow Information
                </Typography>
                <IconButton 
                  size="small" 
                  onClick={toggleShowFullInfo}
                  sx={{ display: { xs: 'flex', md: 'none' } }}
                >
                  {showFullInfo ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Box>
              <Divider sx={{ mb: 2 }} />
              
              <Collapse in={showFullInfo} collapsedSize={isSmallScreen ? "80px" : "auto"}>
                <InfoItem>
                  <InfoLabel variant="body2">ID:</InfoLabel>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <InfoValue variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {workflowId}
                    </InfoValue>
                    <Tooltip title={copySuccess ? "Copied!" : "Copy ID"}>
                      <IconButton 
                        size="small" 
                        onClick={handleCopyId}
                        color={copySuccess ? "success" : "default"}
                        sx={{ ml: 1, width: 20, height: 20 }}
                      >
                        <ContentCopyIcon fontSize="inherit" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </InfoItem>
                
                <InfoItem>
                  <InfoLabel variant="body2">Status:</InfoLabel>
                  <InfoValue variant="body2">
                    <StatusChip 
                      size="small" 
                      label={workflow.status?.toUpperCase()} 
                      status={workflow.status} 
                    />
                  </InfoValue>
                </InfoItem>
                
                <InfoItem>
                  <InfoLabel variant="body2">Created By:</InfoLabel>
                  <InfoValue variant="body2">{workflow.created_by || 'System'}</InfoValue>
                </InfoItem>
                
                <InfoItem>
                  <InfoLabel variant="body2">Created:</InfoLabel>
                  <Tooltip title={formatDateTime(workflow.creation_time)}>
                    <InfoValue variant="body2">{formatRelativeTime(workflow.creation_time)}</InfoValue>
                  </Tooltip>
                </InfoItem>
                
                <InfoItem>
                  <InfoLabel variant="body2">Started:</InfoLabel>
                  <Tooltip title={workflow.start_time ? formatDateTime(workflow.start_time) : 'Not started'}>
                    <InfoValue variant="body2">{workflow.start_time ? formatRelativeTime(workflow.start_time) : 'Not started'}</InfoValue>
                  </Tooltip>
                </InfoItem>
                
                {workflow.end_time && (
                  <InfoItem>
                    <InfoLabel variant="body2">Completed:</InfoLabel>
                    <Tooltip title={formatDateTime(workflow.end_time)}>
                      <InfoValue variant="body2">{formatRelativeTime(workflow.end_time)}</InfoValue>
                    </Tooltip>
                  </InfoItem>
                )}
                
                <InfoItem>
                  <InfoLabel variant="body2">Duration:</InfoLabel>
                  <InfoValue variant="body2">{getTimeElapsed(workflow.start_time, workflow.end_time)}</InfoValue>
                </InfoItem>
                
                <InfoItem>
                  <InfoLabel variant="body2">Tasks:</InfoLabel>
                  <InfoValue variant="body2">
                    {workflow.completed_tasks || 0} / {workflow.task_count || 0} completed
                    {workflow.failed_tasks > 0 && `, ${workflow.failed_tasks} failed`}
                  </InfoValue>
                </InfoItem>
                
                {workflow.template_id && (
                  <InfoItem>
                    <InfoLabel variant="body2">Template:</InfoLabel>
                    <InfoValue variant="body2">{workflow.template_name || workflow.template_id}</InfoValue>
                  </InfoItem>
                )}
                
                {workflow.tags && workflow.tags.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <InfoLabel variant="body2" sx={{ mb: 1 }}>Tags:</InfoLabel>
                    <TagsContainer>
                      {workflow.tags.map((tag, index) => (
                        <Chip 
                          key={index} 
                          label={tag}
                          size="small"
                          variant="outlined"
                          sx={{ 
                            borderRadius: '4px',
                            height: '20px',
                            '& .MuiChip-label': { px: 1, py: 0.25, fontSize: '0.7rem' }
                          }}
                        />
                      ))}
                    </TagsContainer>
                  </Box>
                )}
              </Collapse>
              {isSmallScreen && !showFullInfo && (
                <Button
                  size="small"
                  onClick={toggleShowFullInfo}
                  endIcon={<ExpandMoreIcon />}
                  sx={{ mt: 1, textTransform: 'none' }}
                >
                  Show More
                </Button>
              )}
            </InfoCard>
            
            {/* Timeline */}
            <InfoCard elevation={0}>
              <Typography variant="h6" gutterBottom>
                Activity Timeline
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <WorkflowTimeline workflow={workflow} />
            </InfoCard>
          </Stack>
        </Grid>
        
        {/* Right side - Tabs for Tasks & Findings */}
        <Grid item xs={12} md={8}>
          <ContentContainer elevation={0}>
            <StyledTabs 
              value={tabValue} 
              onChange={handleTabChange}
              sx={{ px: 2, pt: 1 }}
            >
              <StyledTab label="Overview" id="tab-0" />
              <StyledTab label="Tasks" id="tab-1" />
              <TabBadge 
                badgeContent={findingsCount.total > 0 ? findingsCount.total : null}
                color={findingsCount.critical > 0 ? "error" : findingsCount.high > 0 ? "warning" : "primary"}
              >
                <StyledTab label="Findings" id="tab-2" />
              </TabBadge>
            </StyledTabs>
            
            <Divider />
            
            <TabPanel value={tabValue} index={0}>
              {/* Overview tab with interactive workflow visualization */}
              <Box sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Workflow Overview</Typography>
                <Box sx={{ mb: 4 }}>
                  <TaskGraph 
                    workflowId={workflowId}
                    tasks={workflow.tasks || []}
                    isOverview={true}
                  />
                </Box>
                
                {/* Workflow summary statistics */}
                <Box sx={{ mt: 4 }}>
                  <Typography variant="subtitle1" gutterBottom>Summary Statistics</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={4}>
                      <Card sx={{ bgcolor: alpha(theme.palette.primary.main, 0.05) }}>
                        <CardContent>
                          <Typography variant="subtitle2" color="text.secondary">Adapters Used</Typography>
                          <Typography variant="h5">
                            {Array.from(new Set((workflow.tasks || []).map(t => t.adapter))).length}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    
                    <Grid item xs={12} sm={6} md={4}>
                      <Card sx={{ bgcolor: alpha(theme.palette.success.main, 0.05) }}>
                        <CardContent>
                          <Typography variant="subtitle2" color="text.secondary">Success Rate</Typography>
                          <Typography variant="h5">
                            {workflow.task_count > 0 
                              ? `${Math.round((workflow.completed_tasks / workflow.task_count) * 100)}%` 
                              : 'N/A'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                    
                    <Grid item xs={12} sm={6} md={4}>
                      <Card sx={{ bgcolor: alpha(theme.palette.warning.main, 0.05) }}>
                        <CardContent>
                          <Typography variant="subtitle2" color="text.secondary">Avg. Task Duration</Typography>
                          <Typography variant="h5">
                            {workflow.completed_tasks > 0 && workflow.start_time && workflow.end_time
                              ? getTimeElapsed(
                                  workflow.start_time, 
                                  workflow.end_time, 
                                  Math.max(1, workflow.completed_tasks)
                                )
                              : 'N/A'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                </Box>
                
                {/* Quick findings summary if available */}
                {findingsCount.total > 0 && (
                  <Box sx={{ mt: 4 }}>
                    <Typography variant="subtitle1" gutterBottom>Findings Overview</Typography>
                    <Paper 
                      elevation={0} 
                      sx={{ 
                        p: 2, 
                        bgcolor: alpha(
                          findingsCount.critical > 0 
                            ? theme.palette.error.main 
                            : findingsCount.high > 0 
                              ? theme.palette.warning.main 
                              : theme.palette.info.main, 
                          0.05
                        ),
                        border: '1px solid',
                        borderColor: alpha(
                          findingsCount.critical > 0 
                            ? theme.palette.error.main 
                            : findingsCount.high > 0 
                              ? theme.palette.warning.main 
                              : theme.palette.info.main,
                          0.2
                        ),
                        borderRadius: 2
                      }}
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="subtitle1">
                          {findingsCount.total} {findingsCount.total === 1 ? 'finding' : 'findings'} detected
                        </Typography>
                        <Button 
                          size="small" 
                          variant="outlined"
                          onClick={() => setTabValue(2)}
                          sx={{ textTransform: 'none' }}
                        >
                          View Details
                        </Button>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                        {Object.entries(workflow.findings_summary || {}).map(([severity, count]) => (
                          <Chip 
                            key={severity}
                            label={`${severity}: ${count}`}
                            size="small"
                            color={
                              severity === 'critical' ? 'error' :
                              severity === 'high' ? 'error' :
                              severity === 'medium' ? 'warning' :
                              severity === 'low' ? 'info' : 'default'
                            }
                            variant={severity === 'critical' || severity === 'high' ? 'filled' : 'outlined'}
                          />
                        ))}
                      </Box>
                    </Paper>
                  </Box>
                )}
              </Box>
            </TabPanel>
            
            <TabPanel value={tabValue} index={1}>
              {/* Enhanced Task Graph */}
              <TaskGraph 
                workflowId={workflowId}
                tasks={workflow.tasks || []}
                onRefresh={handleRefresh}
              />
            </TabPanel>
            
            <TabPanel value={tabValue} index={2}>
              {loadingFindings ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <FindingsList 
                  findings={findings} 
                  workflowId={workflowId}
                  onRefresh={fetchFindings}
                />
              )}
            </TabPanel>
          </ContentContainer>
        </Grid>
      </Grid>
      
      {/* Delete confirmation dialog */}
      <Dialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
        PaperProps={{
          sx: { borderRadius: 2 }
        }}
      >
        <DialogTitle sx={{ pb: 1 }}>Delete Workflow</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the workflow <strong>{workflow.name}</strong>? 
            This action will permanently remove all associated tasks, results, and findings.
            This operation cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button 
            onClick={() => setDeleteConfirmOpen(false)}
            sx={{ textTransform: 'none', fontWeight: 600 }}
          >
            Cancel
          </Button>
          <Button 
            color="error" 
            variant="contained"
            onClick={confirmDeleteWorkflow}
            startIcon={<DeleteIcon />}
            sx={{ textTransform: 'none', fontWeight: 600 }}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Notifications */}
      {showNotifications && (
        <>
          <Snackbar
            open={Boolean(error)}
            autoHideDuration={6000}
            onClose={() => setError(null)}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          >
            <Alert 
              severity="error" 
              onClose={() => setError(null)}
              sx={{ width: '100%', boxShadow: 3, borderRadius: 2 }}
              variant="filled"
            >
              {error}
            </Alert>
          </Snackbar>
          
          <Snackbar
            open={Boolean(success)}
            autoHideDuration={4000}
            onClose={() => setSuccess(null)}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          >
            <Alert 
              severity="success" 
              onClose={() => setSuccess(null)}
              sx={{ width: '100%', boxShadow: 3, borderRadius: 2 }}
              variant="filled"
            >
              {success}
            </Alert>
          </Snackbar>
          
          <Snackbar
            open={copySuccess}
            autoHideDuration={2000}
            onClose={() => setCopySuccess(false)}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          >
            <Alert 
              severity="success" 
              onClose={() => setCopySuccess(false)}
              sx={{ width: '100%', boxShadow: 3, borderRadius: 2 }}
              variant="filled"
            >
              Workflow ID copied to clipboard!
            </Alert>
          </Snackbar>
        </>
      )}
    </Container>
  );
};

export default WorkflowDetail;