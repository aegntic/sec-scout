import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Tabs,
  Tab,
  Paper,
  Divider,
  CircularProgress,
  IconButton,
  Card,
  CardContent,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  MenuItem,
  Menu,
} from '@mui/material';
import { styled, alpha } from '@mui/material/styles';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import FilterListIcon from '@mui/icons-material/FilterList';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import SortIcon from '@mui/icons-material/Sort';
import WorkflowCard from '../components/Workflows/WorkflowCard';
import TemplateCard from '../components/Workflows/TemplateCard';
import CreateWorkflowDialog from '../components/Workflows/CreateWorkflowDialog';
import apiService from '../services/api';

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

const HeaderButton = styled(Button)(({ theme }) => ({
  borderRadius: theme.shape.borderRadius,
  fontWeight: 600,
  boxShadow: 'none',
  '&:hover': {
    boxShadow: 'none',
  },
}));

const Workflows = () => {
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [workflows, setWorkflows] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [workflowToDelete, setWorkflowToDelete] = useState(null);
  
  // Menu states
  const [sortAnchorEl, setSortAnchorEl] = useState(null);
  const [filterAnchorEl, setFilterAnchorEl] = useState(null);
  
  // Sorting and filtering
  const [sortBy, setSortBy] = useState('newest');
  const [filterStatus, setFilterStatus] = useState('all');
  
  const sortOptions = [
    { value: 'newest', label: 'Newest First' },
    { value: 'oldest', label: 'Oldest First' },
    { value: 'name_asc', label: 'Name (A-Z)' },
    { value: 'name_desc', label: 'Name (Z-A)' },
  ];
  
  const filterOptions = [
    { value: 'all', label: 'All Workflows' },
    { value: 'running', label: 'Running' },
    { value: 'completed', label: 'Completed' },
    { value: 'failed', label: 'Failed' },
    { value: 'pending', label: 'Pending' },
  ];
  
  // Load workflows and templates
  useEffect(() => {
    fetchWorkflows();
    fetchTemplates();
  }, []);
  
  const fetchWorkflows = async () => {
    setLoading(true);
    try {
      const response = await apiService.listWorkflows();
      setWorkflows(response.data.data.workflows);
      setLoading(false);
    } catch (error) {
      setError('Failed to load workflows');
      setLoading(false);
    }
  };
  
  const fetchTemplates = async () => {
    try {
      const response = await apiService.listWorkflowTemplates();
      setTemplates(response.data.data.templates);
    } catch (error) {
      setError('Failed to load templates');
    }
  };
  
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };
  
  const handleCreateWorkflow = () => {
    setCreateDialogOpen(true);
  };
  
  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    setCreateDialogOpen(true);
  };
  
  const handleCreateDialogClose = () => {
    setCreateDialogOpen(false);
    setSelectedTemplate(null);
  };
  
  const handleWorkflowCreated = (workflow) => {
    setSuccess(`Workflow "${workflow.name}" created successfully`);
    fetchWorkflows();
  };
  
  const handleWorkflowClick = (workflowId) => {
    navigate(`/workflows/${workflowId}`);
  };
  
  const handleExecuteWorkflow = async (workflowId) => {
    try {
      await apiService.executeWorkflow(workflowId);
      setSuccess('Workflow execution started');
      fetchWorkflows();
    } catch (error) {
      setError('Failed to execute workflow');
    }
  };
  
  const handleCancelWorkflow = async (workflowId) => {
    try {
      await apiService.cancelWorkflow(workflowId);
      setSuccess('Workflow cancelled');
      fetchWorkflows();
    } catch (error) {
      setError('Failed to cancel workflow');
    }
  };
  
  const handleDeleteWorkflow = (workflowId) => {
    setWorkflowToDelete(workflowId);
    setDeleteConfirmOpen(true);
  };
  
  const confirmDeleteWorkflow = async () => {
    try {
      await apiService.deleteWorkflow(workflowToDelete);
      setSuccess('Workflow deleted');
      fetchWorkflows();
      setDeleteConfirmOpen(false);
      setWorkflowToDelete(null);
    } catch (error) {
      setError('Failed to delete workflow');
      setDeleteConfirmOpen(false);
    }
  };
  
  const handleViewWorkflowResults = (workflowId) => {
    navigate(`/workflows/${workflowId}/results`);
  };
  
  const handleRefresh = () => {
    fetchWorkflows();
  };
  
  const handleSortClick = (event) => {
    setSortAnchorEl(event.currentTarget);
  };
  
  const handleSortClose = () => {
    setSortAnchorEl(null);
  };
  
  const handleSortSelect = (value) => {
    setSortBy(value);
    setSortAnchorEl(null);
  };
  
  const handleFilterClick = (event) => {
    setFilterAnchorEl(event.currentTarget);
  };
  
  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };
  
  const handleFilterSelect = (value) => {
    setFilterStatus(value);
    setFilterAnchorEl(null);
  };
  
  // Apply sorting and filtering
  const getSortedAndFilteredWorkflows = () => {
    let filtered = [...workflows];
    
    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(wf => wf.status === filterStatus);
    }
    
    // Apply sorting
    switch (sortBy) {
      case 'newest':
        return filtered.sort((a, b) => new Date(b.start_time || 0) - new Date(a.start_time || 0));
      case 'oldest':
        return filtered.sort((a, b) => new Date(a.start_time || 0) - new Date(b.start_time || 0));
      case 'name_asc':
        return filtered.sort((a, b) => a.name.localeCompare(b.name));
      case 'name_desc':
        return filtered.sort((a, b) => b.name.localeCompare(a.name));
      default:
        return filtered;
    }
  };
  
  const filteredWorkflows = getSortedAndFilteredWorkflows();
  
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1">
            Workflows
          </Typography>
          
          <Box>
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
            
            <HeaderButton 
              variant="contained" 
              startIcon={<AddIcon />}
              onClick={handleCreateWorkflow}
            >
              Create Workflow
            </HeaderButton>
          </Box>
        </Box>
        
        <Typography variant="body1" color="text.secondary">
          Create and manage security testing workflows with integrated security tools
        </Typography>
      </Box>
      
      <Paper 
        elevation={0} 
        sx={{ 
          borderRadius: 2, 
          overflow: 'hidden',
          backgroundColor: theme => alpha(theme.palette.background.paper, 0.7),
          backgroundImage: 'none',
          backdropFilter: 'blur(20px)',
        }}
      >
        <StyledTabs 
          value={tabValue} 
          onChange={handleTabChange}
          sx={{ px: 2, pt: 1 }}
        >
          <StyledTab label="My Workflows" id="tab-0" />
          <StyledTab label="Templates" id="tab-1" />
        </StyledTabs>
        
        <Divider />
        
        <TabPanel value={tabValue} index={0}>
          <Box sx={{ px: 3, pb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Box>
                <Typography variant="subtitle1" component="div">
                  {filteredWorkflows.length} workflows {filterStatus !== 'all' ? `(${filterStatus})` : ''}
                </Typography>
              </Box>
              
              <Box>
                <IconButton onClick={handleFilterClick} size="small" sx={{ mr: 1 }}>
                  <FilterListIcon />
                </IconButton>
                
                <Menu
                  anchorEl={filterAnchorEl}
                  open={Boolean(filterAnchorEl)}
                  onClose={handleFilterClose}
                >
                  {filterOptions.map(option => (
                    <MenuItem 
                      key={option.value}
                      selected={filterStatus === option.value}
                      onClick={() => handleFilterSelect(option.value)}
                    >
                      {option.label}
                    </MenuItem>
                  ))}
                </Menu>
                
                <IconButton onClick={handleSortClick} size="small">
                  <SortIcon />
                </IconButton>
                
                <Menu
                  anchorEl={sortAnchorEl}
                  open={Boolean(sortAnchorEl)}
                  onClose={handleSortClose}
                >
                  {sortOptions.map(option => (
                    <MenuItem 
                      key={option.value}
                      selected={sortBy === option.value}
                      onClick={() => handleSortSelect(option.value)}
                    >
                      {option.label}
                    </MenuItem>
                  ))}
                </Menu>
              </Box>
            </Box>
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                <CircularProgress />
              </Box>
            ) : filteredWorkflows.length === 0 ? (
              <Card 
                elevation={0}
                sx={{ 
                  backgroundColor: theme => alpha(theme.palette.background.paper, 0.5),
                  border: theme => `1px dashed ${alpha(theme.palette.divider, 0.2)}`,
                  textAlign: 'center',
                  py: 6,
                  px: 2,
                  mb: 2
                }}
              >
                <CardContent>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No workflows found
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {filterStatus !== 'all' 
                      ? `No ${filterStatus} workflows to display. Try changing the filter or create a new workflow.`
                      : 'Get started by creating your first workflow using the "Create Workflow" button above.'}
                  </Typography>
                  
                  <Button 
                    variant="contained" 
                    startIcon={<AddIcon />} 
                    onClick={handleCreateWorkflow}
                    sx={{ mt: 3 }}
                  >
                    Create Workflow
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <Grid container spacing={3}>
                {filteredWorkflows.map((workflow) => (
                  <Grid item xs={12} sm={6} md={4} key={workflow.workflow_id}>
                    <WorkflowCard
                      workflow={workflow}
                      onExecute={handleExecuteWorkflow}
                      onCancel={handleCancelWorkflow}
                      onView={handleWorkflowClick}
                      onDelete={handleDeleteWorkflow}
                      onViewResults={handleViewWorkflowResults}
                      onClick={handleWorkflowClick}
                    />
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ px: 3, pb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Available Templates
            </Typography>
            
            <Typography variant="body2" color="text.secondary" paragraph>
              Use these templates to quickly create common security testing workflows
            </Typography>
            
            <Grid container spacing={3}>
              {templates.map((template) => (
                <Grid item xs={12} sm={6} md={4} key={template.id}>
                  <TemplateCard
                    template={template}
                    onSelect={handleTemplateSelect}
                    onInfo={() => handleTemplateSelect(template)}
                  />
                </Grid>
              ))}
            </Grid>
          </Box>
        </TabPanel>
      </Paper>
      
      {/* Create workflow dialog */}
      <CreateWorkflowDialog
        open={createDialogOpen}
        template={selectedTemplate}
        onClose={handleCreateDialogClose}
        onSuccess={handleWorkflowCreated}
      />
      
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

export default Workflows;