import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
} from '@mui/material';
import { styled, alpha } from '@mui/material/styles';
import RefreshIcon from '@mui/icons-material/Refresh';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import DeleteIcon from '@mui/icons-material/Delete';
import WebIcon from '@mui/icons-material/Web';
import { formatDistanceToNow, formatRelative } from 'date-fns';
import apiService from '../services/api';

// Components we'll create separately
import TaskGraph from '../components/Workflows/TaskGraph';
import FindingsList from '../components/Workflows/FindingsList';

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

const InfoCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
  backgroundColor: alpha(theme.palette.background.paper, 0.7),
  backdropFilter: 'blur(20px)',
  display: 'flex',
  flexDirection: 'column',
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

const WorkflowDetail = () => {
  const { workflowId } = useParams();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [workflow, setWorkflow] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statusPolling, setStatusPolling] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [findings, setFindings] = useState([]);
  const [loadingFindings, setLoadingFindings] = useState(false);

  // Fetch workflow details
  const fetchWorkflow = async () => {
    try {
      const response = await apiService.getWorkflow(workflowId);
      setWorkflow(response.data.data.workflow);
      
      // If workflow is running, start polling for status updates
      if (response.data.data.workflow.status === 'running') {
        startStatusPolling();
      } else {
        stopStatusPolling();
      }
    } catch (error) {
      setError('Failed to load workflow details');
      console.error('Error fetching workflow:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch findings
  const fetchFindings = async () => {
    if (tabValue === 2) { // Only fetch findings when on findings tab
      setLoadingFindings(true);
      try {
        const response = await apiService.getWorkflowFindings(workflowId);
        setFindings(response.data.data.findings);
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
      const interval = setInterval(fetchWorkflow, 5000);
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

  // Handle tab changes and load data for the selected tab
  useEffect(() => {
    if (tabValue === 2) {
      fetchFindings();
    }
  }, [tabValue]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleGoBack = () => {
    navigate('/workflows');
  };

  const handleRefresh = () => {
    fetchWorkflow();
    if (tabValue === 2) {
      fetchFindings();
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

  const formatDateTime = (dateString) => {
    if (!dateString) return 'Not available';
    try {
      const date = new Date(dateString);
      return formatRelative(date, new Date());
    } catch (e) {
      return dateString;
    }
  };

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

  if (loading) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (!workflow) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ mt: 4 }}>
          <Alert severity="error">
            Workflow not found or failed to load
          </Alert>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={handleGoBack}
            sx={{ mt: 2 }}
          >
            Back to Workflows
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton onClick={handleGoBack} sx={{ mr: 1 }}>
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="h4" component="h1">
              {workflow.name}
            </Typography>
            <StatusChip 
              size="small" 
              label={workflow.status?.toUpperCase()} 
              status={workflow.status} 
              sx={{ ml: 2 }}
            />
          </Box>
          
          <Box>
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
            
            {['pending', 'completed', 'failed', 'cancelled'].includes(workflow.status) && (
              <Button 
                variant="contained" 
                startIcon={<PlayArrowIcon />}
                onClick={handleExecuteWorkflow}
                sx={{ mr: 1 }}
              >
                Execute
              </Button>
            )}
            
            {workflow.status === 'running' && (
              <Button 
                variant="contained" 
                color="error"
                startIcon={<StopIcon />}
                onClick={handleCancelWorkflow}
                sx={{ mr: 1 }}
              >
                Cancel
              </Button>
            )}
            
            <Button 
              variant="outlined" 
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleDeleteWorkflow}
            >
              Delete
            </Button>
          </Box>
        </Box>
        
        <Typography variant="body1" color="text.secondary">
          {workflow.description}
        </Typography>

        {workflow.target && (
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <WebIcon sx={{ mr: 1, fontSize: '1rem', color: 'primary.light' }} />
            <Typography variant="body2" sx={{ fontFamily: 'monospace', color: 'primary.light' }}>
              {workflow.target}
            </Typography>
          </Box>
        )}
      </Box>
      
      {/* Workflow details & tabs */}
      <Grid container spacing={3}>
        {/* Left side - Workflow info */}
        <Grid item xs={12} md={4}>
          <InfoCard elevation={0}>
            <Typography variant="h6" gutterBottom>
              Workflow Information
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <InfoItem>
              <InfoLabel variant="body2">ID:</InfoLabel>
              <InfoValue variant="body2" sx={{ fontFamily: 'monospace' }}>{workflow.workflow_id}</InfoValue>
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
              <InfoValue variant="body2">{formatDateTime(workflow.creation_time)}</InfoValue>
            </InfoItem>
            
            <InfoItem>
              <InfoLabel variant="body2">Started:</InfoLabel>
              <InfoValue variant="body2">{formatDateTime(workflow.start_time)}</InfoValue>
            </InfoItem>
            
            {workflow.end_time && (
              <InfoItem>
                <InfoLabel variant="body2">Completed:</InfoLabel>
                <InfoValue variant="body2">{formatDateTime(workflow.end_time)}</InfoValue>
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
          </InfoCard>
        </Grid>
        
        {/* Right side - Tabs for Tasks & Findings */}
        <Grid item xs={12} md={8}>
          <Paper 
            elevation={0}
            sx={{ 
              borderRadius: 2, 
              overflow: 'hidden',
              backgroundColor: theme => alpha(theme.palette.background.paper, 0.7),
              backdropFilter: 'blur(20px)',
              height: '100%',
            }}
          >
            <StyledTabs 
              value={tabValue} 
              onChange={handleTabChange}
              sx={{ px: 2, pt: 1 }}
            >
              <StyledTab label="Overview" id="tab-0" />
              <StyledTab label="Tasks" id="tab-1" />
              <StyledTab label="Findings" id="tab-2" />
            </StyledTabs>
            
            <Divider />
            
            <TabPanel value={tabValue} index={0}>
              {/* Overview tab - Summary information */}
              <Box sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Summary</Typography>
                <Typography variant="body2" paragraph>
                  {workflow.description || 'No description provided for this workflow.'}
                </Typography>
                
                {/* Task completion progress */}
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" gutterBottom>Task Completion</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box sx={{ width: '100%', mr: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={workflow.task_count > 0 ? (workflow.completed_tasks / workflow.task_count) * 100 : 0}
                        sx={{ height: 10, borderRadius: 5 }}
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {workflow.task_count > 0 ? Math.round((workflow.completed_tasks / workflow.task_count) * 100) : 0}%
                    </Typography>
                  </Box>
                </Box>
                
                {/* Findings summary if available */}
                {workflow.findings_summary && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle1" gutterBottom>Findings</Typography>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      {Object.entries(workflow.findings_summary).map(([severity, count]) => (
                        <Chip 
                          key={severity}
                          label={`${severity}: ${count}`}
                          color={
                            severity === 'critical' ? 'error' :
                            severity === 'high' ? 'error' :
                            severity === 'medium' ? 'warning' :
                            severity === 'low' ? 'info' : 'default'
                          }
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </Box>
            </TabPanel>
            
            <TabPanel value={tabValue} index={1}>
              {/* Task Graph component to visualize dependencies */}
              <TaskGraph 
                workflowId={workflowId}
                tasks={workflow.tasks || []}
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
          </Paper>
        </Grid>
      </Grid>
      
      {/* Delete confirmation dialog */}
      <Dialog
        open={deleteConfirmOpen}
        onClose={() => setDeleteConfirmOpen(false)}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this workflow? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirmOpen(false)}>Cancel</Button>
          <Button color="error" onClick={confirmDeleteWorkflow}>Delete</Button>
        </DialogActions>
      </Dialog>
      
      {/* Notifications */}
      <Snackbar
        open={Boolean(error)}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>
      
      <Snackbar
        open={Boolean(success)}
        autoHideDuration={6000}
        onClose={() => setSuccess(null)}
      >
        <Alert severity="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default WorkflowDetail;