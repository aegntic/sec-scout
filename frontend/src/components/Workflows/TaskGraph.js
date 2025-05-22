import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  Button,
  Chip,
  Tooltip,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  ToggleButtonGroup,
  ToggleButton,
  useTheme,
  useMediaQuery,
  Slider,
  Stack,
  FormControl,
  InputLabel,
  Select,
  Divider,
  Fade,
  Zoom,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import { styled, alpha } from '@mui/material/styles';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  Panel,
  useNodesState,
  useEdgesState,
  MarkerType,
  useReactFlow,
  addEdge,
  useKeyPress,
  Position,
  BaseEdge,
} from 'reactflow';
import 'reactflow/dist/style.css';
import RefreshIcon from '@mui/icons-material/Refresh';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit';
import InfoIcon from '@mui/icons-material/Info';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import FilterAltIcon from '@mui/icons-material/FilterAlt';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import VisibilityIcon from '@mui/icons-material/Visibility';
import GridViewIcon from '@mui/icons-material/GridView';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import FitScreenIcon from '@mui/icons-material/FitScreen';
import AbcIcon from '@mui/icons-material/Abc';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import TuneIcon from '@mui/icons-material/Tune';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import TimelineIcon from '@mui/icons-material/Timeline';
import DoneIcon from '@mui/icons-material/Done';
import ErrorIcon from '@mui/icons-material/Error';
import apiService from '../../services/api';
import dagre from 'dagre';

// Custom node components
import TaskNode from './TaskNode';

// Register custom node types
const nodeTypes = {
  taskNode: TaskNode,
};

const StyledReactFlow = styled(ReactFlow)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.background.default, 0.5),
  borderRadius: theme.shape.borderRadius,
  height: '600px',
  '& .react-flow__edge-path': {
    strokeWidth: 2,
  },
  '& .react-flow__edge-path-bg': {
    strokeWidth: 4,
    stroke: alpha(theme.palette.background.paper, 0.8),
  },
  '& .react-flow__controls-button': {
    backgroundColor: theme.palette.background.paper,
    borderColor: alpha(theme.palette.divider, 0.5),
    color: theme.palette.text.secondary,
    '&:hover': {
      backgroundColor: alpha(theme.palette.primary.main, 0.1),
    },
  },
  '& .react-flow__minimap': {
    backgroundColor: alpha(theme.palette.background.paper, 0.8),
    border: `1px solid ${alpha(theme.palette.divider, 0.2)}`,
    borderRadius: '4px',
  },
  '& .react-flow__attribution': {
    backgroundColor: 'transparent',
    color: alpha(theme.palette.text.secondary, 0.5),
  },
}));

const GraphControlButton = styled(IconButton)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.background.paper, 0.7),
  backdropFilter: 'blur(8px)',
  boxShadow: `0 1px 3px ${alpha(theme.palette.common.black, 0.1)}`,
  '&:hover': {
    backgroundColor: alpha(theme.palette.background.paper, 0.9),
  },
}));

const GraphControlFloatingPanel = styled(Box)(({ theme }) => ({
  position: 'absolute',
  bottom: 20,
  right: 20,
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(1),
  zIndex: 5,
}));

const FilterPanel = styled(Paper)(({ theme }) => ({
  position: 'absolute',
  top: 10,
  left: 10,
  padding: theme.spacing(1.5),
  zIndex: 5,
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(1),
  backgroundColor: alpha(theme.palette.background.paper, 0.9),
  backdropFilter: 'blur(8px)',
  maxWidth: 300,
  boxShadow: theme.shadows[3],
  borderRadius: theme.shape.borderRadius,
  transition: 'all 0.3s',
}));

const LayoutPanel = styled(Box)(({ theme }) => ({
  marginTop: theme.spacing(1),
  padding: theme.spacing(1.5),
  backgroundColor: alpha(theme.palette.background.paper, 0.7),
  borderRadius: theme.shape.borderRadius,
  boxShadow: `inset 0 0 0 1px ${alpha(theme.palette.primary.main, 0.1)}`,
}));

const GraphLegend = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(1),
  backgroundColor: alpha(theme.palette.background.paper, 0.7),
  backdropFilter: 'blur(8px)',
  display: 'flex',
  flexWrap: 'wrap',
  gap: theme.spacing(0.5),
  borderRadius: theme.shape.borderRadius,
  boxShadow: `0 1px 3px ${alpha(theme.palette.common.black, 0.1)}`,
}));

const InfoCard = styled(Card)(({ theme }) => ({
  position: 'absolute',
  bottom: 20,
  left: 20,
  zIndex: 5,
  backgroundColor: alpha(theme.palette.background.paper, 0.85),
  backdropFilter: 'blur(8px)',
  maxWidth: 300,
  boxShadow: theme.shadows[4],
  borderRadius: theme.shape.borderRadius,
}));

// Edge customization
const STATUS_COLORS = {
  running: '#3f88c5',
  completed: '#4caf50',
  failed: '#f44336',
  cancelled: '#ff9800',
  pending: '#9e9e9e'
};

// Layout direction options
const LAYOUT_DIRECTIONS = {
  LR: { name: 'Left to Right', rankdir: 'LR' },
  RL: { name: 'Right to Left', rankdir: 'RL' },
  TB: { name: 'Top to Bottom', rankdir: 'TB' },
  BT: { name: 'Bottom to Top', rankdir: 'BT' },
};

// Helper to get node status color
const getNodeStatusColor = (status, theme) => {
  switch (status) {
    case 'completed':
      return theme.palette.success.main;
    case 'running':
      return theme.palette.primary.main;
    case 'failed':
      return theme.palette.error.main;
    case 'cancelled':
      return theme.palette.warning.main;
    default:
      return theme.palette.grey[500];
  }
};

// Helper to get edge color by status
const getEdgeColor = (source, target, tasks) => {
  if (!tasks) return STATUS_COLORS.pending;
  
  const sourceTask = tasks.find(t => t.task_id === source);
  const targetTask = tasks.find(t => t.task_id === target);
  
  if (!sourceTask || !targetTask) return STATUS_COLORS.pending;
  
  if (targetTask.status === 'running') {
    return STATUS_COLORS.running;
  } else if (sourceTask.status === 'completed' && targetTask.status === 'completed') {
    return STATUS_COLORS.completed;
  } else if (targetTask.status === 'failed') {
    return STATUS_COLORS.failed;
  } else if (targetTask.status === 'cancelled') {
    return STATUS_COLORS.cancelled;
  }
  
  return STATUS_COLORS.pending;
};

// Create a layout using dagre
const getLayoutedElements = (nodes, edges, direction = 'LR') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  
  const rankdir = LAYOUT_DIRECTIONS[direction]?.rankdir || 'LR';
  const isHorizontal = rankdir === 'LR' || rankdir === 'RL';
  
  dagreGraph.setGraph({ 
    rankdir,
    nodesep: 80,
    ranksep: 200,
    edgesep: 80,
    marginx: 20,
    marginy: 20,
  });
  
  // Add nodes to dagre
  nodes.forEach(node => {
    dagreGraph.setNode(node.id, { 
      width: 220, 
      height: 100
    });
  });
  
  // Add edges to dagre
  edges.forEach(edge => {
    dagreGraph.setEdge(edge.source, edge.target);
  });
  
  // Calculate layout
  dagre.layout(dagreGraph);
  
  // Apply positions to nodes
  const layoutedNodes = nodes.map(node => {
    const nodeWithPosition = dagreGraph.node(node.id);
    
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - 110, 
        y: nodeWithPosition.y - 50
      }
    };
  });
  
  return { nodes: layoutedNodes, edges };
};

// Custom edge with dynamic styling
const CustomEdge = ({ id, source, target, style = {}, animated, selected, markerEnd, data, ...props }) => {
  const { tasks } = data || {};
  const edgeColor = getEdgeColor(source, target, tasks);
  
  return (
    <BaseEdge
      id={id}
      source={source}
      target={target}
      style={{
        ...style,
        stroke: edgeColor,
        strokeWidth: selected ? 3 : 2,
        strokeDasharray: animated ? '5,5' : undefined,
      }}
      animated={animated}
      selected={selected}
      markerEnd={markerEnd}
      {...props}
    />
  );
};

// Define the edge types
const edgeTypes = {
  custom: CustomEdge,
};

const TaskGraph = ({ workflowId, tasks = [], onRefresh, isOverview = false }) => {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));
  const reactFlowWrapper = useRef(null);
  const reactFlowInstance = useReactFlow();
  
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fullscreen, setFullscreen] = useState(false);
  const [selectedLayout, setSelectedLayout] = useState('LR');
  const [showFilterPanel, setShowFilterPanel] = useState(false);
  const [showInfoCard, setShowInfoCard] = useState(isOverview);
  const [nodeFilters, setNodeFilters] = useState({ status: [], adapter: [] });
  const [edgeAnimations, setEdgeAnimations] = useState(true);
  const [adaptOptions, setAdaptOptions] = useState([]);
  const [taskDetails, setTaskDetails] = useState([]);
  const [showInfoModal, setShowInfoModal] = useState(false);
  const [infoModalContent, setInfoModalContent] = useState(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [uniqueAdapters, setUniqueAdapters] = useState([]);
  const [showStats, setShowStats] = useState(true);
  
  const spacePressed = useKeyPress('Space');
  
  // Functions to handle node clicks
  const onNodeClick = (event, node) => {
    setInfoModalContent(node.data);
    setShowInfoModal(true);
  };
  
  // Convert tasks to ReactFlow nodes and edges
  const buildGraph = useCallback((tasks) => {
    if (!tasks || tasks.length === 0) {
      setNodes([]);
      setEdges([]);
      setTaskDetails([]);
      return;
    }
    
    // Extract all unique adapters for filtering
    const adapters = Array.from(new Set(tasks.map(task => task.adapter)));
    setUniqueAdapters(adapters);
    
    // Store task detail info
    setTaskDetails(tasks);
    
    // Create initial nodes and edges
    const initialNodes = tasks.map(task => ({
      id: task.task_id,
      type: 'taskNode',
      position: { x: 0, y: 0 }, // Will be repositioned by layout
      data: {
        task: task,
        adapter: task.adapter,
        label: task.name || task.adapter,
        status: task.status || 'pending',
        start_time: task.start_time,
        end_time: task.end_time,
        progress: task.progress || 0,
        onClick: onNodeClick,
      },
    }));
    
    const initialEdges = [];
    tasks.forEach(task => {
      if (task.dependencies && task.dependencies.length > 0) {
        task.dependencies.forEach(depId => {
          initialEdges.push({
            id: `${depId}-${task.task_id}`,
            source: depId,
            target: task.task_id,
            type: 'custom',
            animated: edgeAnimations && task.status === 'running',
            style: { strokeWidth: 2 },
            data: { tasks },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              width: 15,
              height: 15,
              color: getEdgeColor(depId, task.task_id, tasks),
            },
          });
        });
      }
    });
    
    // Apply layout
    const layouted = getLayoutedElements(initialNodes, initialEdges, selectedLayout);
    setNodes(layouted.nodes);
    setEdges(layouted.edges);
  }, [selectedLayout, edgeAnimations]);
  
  // Create edge animations for running tasks
  useEffect(() => {
    if (edges.length > 0 && taskDetails.length > 0) {
      const updatedEdges = edges.map(edge => {
        const targetTask = taskDetails.find(t => t.task_id === edge.target);
        return {
          ...edge,
          animated: edgeAnimations && targetTask?.status === 'running',
          data: { tasks: taskDetails },
        };
      });
      setEdges(updatedEdges);
    }
  }, [edgeAnimations, taskDetails]);
  
  // Load task details
  const fetchTasks = async () => {
    setLoading(true);
    try {
      const response = await apiService.getWorkflow(workflowId);
      const workflowTasks = response.data.data.workflow.tasks || [];
      buildGraph(workflowTasks);
    } catch (error) {
      setError('Failed to load workflow tasks');
      console.error('Error fetching workflow tasks:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Re-layout when layout direction changes
  useEffect(() => {
    if (nodes.length > 0 && edges.length > 0) {
      const layouted = getLayoutedElements(nodes, edges, selectedLayout);
      setNodes([...layouted.nodes]);
      setEdges([...layouted.edges]);
      
      // After layouting, fit the view
      setTimeout(() => {
        if (reactFlowInstance) {
          reactFlowInstance.fitView({ padding: 0.2 });
        }
      }, 50);
    }
  }, [selectedLayout]);
  
  // Update zoom level when it changes in ReactFlow
  const onMove = useCallback((event) => {
    setZoomLevel(event.zoom);
  }, []);
  
  // Handle zoom in/out
  const handleZoomIn = () => {
    if (reactFlowInstance) {
      reactFlowInstance.zoomIn();
    }
  };
  
  const handleZoomOut = () => {
    if (reactFlowInstance) {
      reactFlowInstance.zoomOut();
    }
  };
  
  const handleFitView = () => {
    if (reactFlowInstance) {
      reactFlowInstance.fitView({ padding: 0.2 });
    }
  };
  
  // Initialize the graph
  useEffect(() => {
    if (tasks.length > 0) {
      buildGraph(tasks);
      setLoading(false);
    } else {
      fetchTasks();
    }
  }, [workflowId, buildGraph]);
  
  // Apply filters to nodes
  useEffect(() => {
    if (taskDetails.length === 0) return;
    
    // Clone the original nodes before filtering
    let filteredNodes = [...nodes];
    
    // Apply status filters
    if (nodeFilters.status.length > 0) {
      filteredNodes = filteredNodes.map(node => ({
        ...node,
        hidden: !nodeFilters.status.includes(node.data.status),
      }));
    }
    
    // Apply adapter filters
    if (nodeFilters.adapter.length > 0) {
      filteredNodes = filteredNodes.map(node => ({
        ...node,
        hidden: node.hidden || !nodeFilters.adapter.includes(node.data.adapter),
      }));
    }
    
    // Update nodes with filtered versions
    setNodes(filteredNodes);
    
  }, [nodeFilters, taskDetails]);
  
  const handleRefresh = () => {
    fetchTasks();
    if (onRefresh) onRefresh();
  };
  
  const toggleFullscreen = () => {
    setFullscreen(!fullscreen);
    // After toggling fullscreen, fit view
    setTimeout(() => {
      if (reactFlowInstance) {
        reactFlowInstance.fitView({ padding: 0.2 });
      }
    }, 100);
  };
  
  const handleLayoutChange = (event, newLayout) => {
    if (newLayout !== null) {
      setSelectedLayout(newLayout);
    }
  };
  
  const toggleFilterPanel = () => {
    setShowFilterPanel(!showFilterPanel);
  };
  
  const toggleInfoCard = () => {
    setShowInfoCard(!showInfoCard);
  };
  
  const handleStatusFilterChange = (event) => {
    setNodeFilters({
      ...nodeFilters,
      status: event.target.value,
    });
  };
  
  const handleAdapterFilterChange = (event) => {
    setNodeFilters({
      ...nodeFilters,
      adapter: event.target.value,
    });
  };
  
  const toggleEdgeAnimations = () => {
    setEdgeAnimations(!edgeAnimations);
  };
  
  const handleCloseInfoModal = () => {
    setShowInfoModal(false);
  };
  
  // Generate statistics about the workflow graph
  const getGraphStats = () => {
    if (!taskDetails || taskDetails.length === 0) return [];
    
    const stats = {
      totalTasks: taskDetails.length,
      completedTasks: taskDetails.filter(t => t.status === 'completed').length,
      failedTasks: taskDetails.filter(t => t.status === 'failed').length,
      runningTasks: taskDetails.filter(t => t.status === 'running').length,
      pendingTasks: taskDetails.filter(t => t.status === 'pending').length,
      uniqueAdapters: uniqueAdapters.length,
      connections: edges.length,
      connectionDensity: edges.length / taskDetails.length,
    };
    
    return stats;
  };
  
  const graphStats = getGraphStats();
  
  // Loading state
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  // Error state
  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
        <Button variant="outlined" size="small" sx={{ ml: 2 }} onClick={handleRefresh}>
          Retry
        </Button>
      </Alert>
    );
  }
  
  // Empty state
  if (nodes.length === 0) {
    return (
      <Paper 
        elevation={0}
        sx={{ 
          p: 3, 
          textAlign: 'center', 
          backgroundColor: alpha(theme.palette.background.paper, 0.7),
          backdropFilter: 'blur(10px)',
          borderRadius: theme.shape.borderRadius,
        }}
      >
        <InfoIcon sx={{ fontSize: 48, color: 'primary.main', opacity: 0.7, mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          No tasks found in this workflow
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          This workflow doesn't have any tasks defined or the tasks failed to load.
        </Typography>
        <Button 
          variant="outlined" 
          startIcon={<RefreshIcon />} 
          onClick={handleRefresh}
          sx={{ 
            textTransform: 'none',
            fontWeight: 600,
          }}
        >
          Refresh Tasks
        </Button>
      </Paper>
    );
  }
  
  // Workflow graph visualization
  return (
    <Box 
      ref={reactFlowWrapper}
      sx={{ 
        height: isOverview ? 350 : (fullscreen ? '100vh' : 600), 
        width: fullscreen ? '100vw' : '100%',
        position: fullscreen ? 'fixed' : 'relative',
        top: fullscreen ? 0 : 'auto',
        left: fullscreen ? 0 : 'auto',
        zIndex: fullscreen ? 1300 : 'auto',
        bgcolor: 'background.paper',
        borderRadius: theme.shape.borderRadius,
        overflow: 'hidden',
        boxShadow: fullscreen ? 24 : 0,
      }}
    >
      <StyledReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        onNodeClick={onNodeClick}
        onMove={onMove}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={2}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }}
        attributionPosition="bottom-left"
        elevateEdgesOnSelect
        proOptions={{ hideAttribution: isOverview }}
      >
        {!isOverview && <Controls showInteractive={false} />}
        
        {!isOverview && (
          <MiniMap 
            nodeStrokeColor={(n) => getNodeStatusColor(n.data?.status, theme)}
            nodeColor={(n) => alpha(getNodeStatusColor(n.data?.status, theme), 0.1)}
            nodeBorderRadius={4}
            maskColor={alpha(theme.palette.background.default, 0.5)}
            style={{
              backgroundColor: alpha(theme.palette.background.paper, 0.7),
              backdropFilter: 'blur(8px)',
            }}
          />
        )}
        
        <Background 
          color={alpha(theme.palette.text.primary, 0.05)}
          gap={16} 
          size={1}
          variant={isOverview ? 'dots' : 'lines'}
        />
        
        {/* Legend panel */}
        {!isOverview && (
          <Panel position="top-left">
            <GraphLegend>
              <Chip 
                size="small" 
                color="primary" 
                variant="outlined" 
                icon={<PlayArrowIcon fontSize="small" />}
                label="Running"
                sx={{ height: 22, '& .MuiChip-label': { px: 1 } }}
              />
              <Chip 
                size="small" 
                color="success" 
                variant="outlined" 
                icon={<DoneIcon fontSize="small" />}
                label="Completed" 
                sx={{ height: 22, '& .MuiChip-label': { px: 1 } }}
              />
              <Chip 
                size="small" 
                color="error" 
                variant="outlined" 
                icon={<ErrorIcon fontSize="small" />}
                label="Failed" 
                sx={{ height: 22, '& .MuiChip-label': { px: 1 } }}
              />
              <Chip 
                size="small" 
                color="default" 
                variant="outlined" 
                icon={<InfoOutlinedIcon fontSize="small" />} 
                label="Pending" 
                sx={{ height: 22, '& .MuiChip-label': { px: 1 } }}
              />
            </GraphLegend>
          </Panel>
        )}
        
        {/* Filter panel */}
        {showFilterPanel && !isOverview && (
          <Fade in={showFilterPanel}>
            <FilterPanel>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2">Task Filters</Typography>
                <IconButton size="small" onClick={toggleFilterPanel}>
                  <FilterAltIcon fontSize="small" />
                </IconButton>
              </Box>
              <Divider />
              
              {/* Status filter */}
              <FormControl size="small" fullWidth>
                <InputLabel id="status-filter-label">Status</InputLabel>
                <Select
                  labelId="status-filter-label"
                  id="status-filter"
                  multiple
                  value={nodeFilters.status}
                  onChange={handleStatusFilterChange}
                  label="Status"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip 
                          key={value} 
                          label={value}
                          size="small"
                          sx={{ 
                            height: 20,
                            backgroundColor: alpha(getNodeStatusColor(value, theme), 0.1),
                            color: getNodeStatusColor(value, theme),
                            '& .MuiChip-label': { px: 1, py: 0 }
                          }}
                        />
                      ))}
                    </Box>
                  )}
                >
                  {['pending', 'running', 'completed', 'failed', 'cancelled'].map((status) => (
                    <MenuItem key={status} value={status}>
                      <Chip 
                        size="small" 
                        label={status}
                        sx={{ 
                          height: 20,
                          backgroundColor: alpha(getNodeStatusColor(status, theme), 0.1),
                          color: getNodeStatusColor(status, theme),
                          '& .MuiChip-label': { px: 1, py: 0 }
                        }}
                      />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              {/* Adapter filter */}
              <FormControl size="small" fullWidth>
                <InputLabel id="adapter-filter-label">Tool Type</InputLabel>
                <Select
                  labelId="adapter-filter-label"
                  id="adapter-filter"
                  multiple
                  value={nodeFilters.adapter}
                  onChange={handleAdapterFilterChange}
                  label="Tool Type"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip 
                          key={value} 
                          label={value}
                          size="small"
                          sx={{ height: 20, '& .MuiChip-label': { px: 1, py: 0 } }}
                        />
                      ))}
                    </Box>
                  )}
                >
                  {uniqueAdapters.map((adapter) => (
                    <MenuItem key={adapter} value={adapter}>
                      {adapter}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              {/* Layout controls */}
              <LayoutPanel>
                <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
                  Layout Direction
                </Typography>
                <ToggleButtonGroup
                  value={selectedLayout}
                  exclusive
                  onChange={handleLayoutChange}
                  size="small"
                  fullWidth
                >
                  {Object.entries(LAYOUT_DIRECTIONS).map(([key, { name }]) => (
                    <ToggleButton 
                      key={key} 
                      value={key}
                      sx={{ 
                        textTransform: 'none',
                        py: 0.5,
                        fontSize: '0.75rem',
                      }}
                    >
                      {name}
                    </ToggleButton>
                  ))}
                </ToggleButtonGroup>
                
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Edge Animation
                  </Typography>
                  <Button
                    size="small"
                    onClick={toggleEdgeAnimations}
                    variant={edgeAnimations ? "contained" : "outlined"}
                    color={edgeAnimations ? "primary" : "inherit"}
                    startIcon={<TimelineIcon />}
                    fullWidth
                    sx={{ 
                      mt: 0.5, 
                      textTransform: 'none',
                      py: 0.5,
                      fontSize: '0.75rem',
                    }}
                  >
                    {edgeAnimations ? "Animations ON" : "Animations OFF"}
                  </Button>
                </Box>
              </LayoutPanel>
              
              <Button 
                size="small" 
                startIcon={<FitScreenIcon />} 
                onClick={handleFitView}
                sx={{ 
                  mt: 1, 
                  textTransform: 'none',
                  fontWeight: 600,
                }}
              >
                Fit View
              </Button>
            </FilterPanel>
          </Fade>
        )}
        
        {/* Workflow stats card */}
        {showInfoCard && (
          <Fade in={showInfoCard}>
            <InfoCard sx={{ maxWidth: isOverview ? '100%' : 280 }}>
              <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="subtitle2">Workflow Graph</Typography>
                  {!isOverview && (
                    <IconButton size="small" onClick={toggleInfoCard}>
                      <InfoOutlinedIcon fontSize="small" />
                    </IconButton>
                  )}
                </Box>
                
                <Divider sx={{ mb: 1 }} />
                
                <Stack spacing={0.5}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Tasks:</Typography>
                    <Typography variant="body2" fontWeight={600}>{graphStats.totalTasks}</Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Completed:</Typography>
                    <Typography variant="body2" color="success.main" fontWeight={600}>
                      {graphStats.completedTasks} ({Math.round((graphStats.completedTasks / graphStats.totalTasks) * 100)}%)
                    </Typography>
                  </Box>
                  
                  {graphStats.failedTasks > 0 && (
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">Failed:</Typography>
                      <Typography variant="body2" color="error.main" fontWeight={600}>
                        {graphStats.failedTasks}
                      </Typography>
                    </Box>
                  )}
                  
                  {graphStats.runningTasks > 0 && (
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2" color="text.secondary">Running:</Typography>
                      <Typography variant="body2" color="primary.main" fontWeight={600}>
                        {graphStats.runningTasks}
                      </Typography>
                    </Box>
                  )}
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Tool types:</Typography>
                    <Typography variant="body2" fontWeight={600}>{graphStats.uniqueAdapters}</Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">Dependencies:</Typography>
                    <Typography variant="body2" fontWeight={600}>{graphStats.connections}</Typography>
                  </Box>
                </Stack>
                
                {!isOverview && (
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                    Click on any task node to view details
                  </Typography>
                )}
              </CardContent>
            </InfoCard>
          </Fade>
        )}
        
        {/* Main controls */}
        {!isOverview && (
          <GraphControlFloatingPanel>
            <GraphControlButton 
              onClick={handleRefresh} 
              color="inherit"
              size="small"
              title="Refresh Tasks"
            >
              <RefreshIcon fontSize="small" />
            </GraphControlButton>
            
            <GraphControlButton
              onClick={toggleFullscreen}
              color="inherit"
              size="small"
              title={fullscreen ? "Exit Fullscreen" : "Fullscreen Mode"}
            >
              {fullscreen ? <FullscreenExitIcon fontSize="small" /> : <FullscreenIcon fontSize="small" />}
            </GraphControlButton>
            
            <GraphControlButton
              onClick={toggleFilterPanel}
              color={showFilterPanel ? "primary" : "inherit"}
              size="small"
              title="Show Filters"
            >
              <FilterAltIcon fontSize="small" />
            </GraphControlButton>
            
            <GraphControlButton
              onClick={toggleInfoCard}
              color={showInfoCard ? "primary" : "inherit"}
              size="small"
              title="Show Statistics"
            >
              <InfoOutlinedIcon fontSize="small" />
            </GraphControlButton>
            
            <Divider sx={{ my: 0.5 }} />
            
            <GraphControlButton
              onClick={handleZoomIn}
              color="inherit"
              size="small"
              title="Zoom In"
            >
              <ZoomInIcon fontSize="small" />
            </GraphControlButton>
            
            <GraphControlButton
              onClick={handleZoomOut}
              color="inherit"
              size="small"
              title="Zoom Out"
            >
              <ZoomOutIcon fontSize="small" />
            </GraphControlButton>
            
            <GraphControlButton
              onClick={handleFitView}
              color="inherit"
              size="small"
              title="Fit View"
            >
              <FitScreenIcon fontSize="small" />
            </GraphControlButton>
          </GraphControlFloatingPanel>
        )}
      </StyledReactFlow>
      
      {/* Task Details Modal */}
      <Dialog
        open={showInfoModal}
        onClose={handleCloseInfoModal}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 2 }
        }}
      >
        {infoModalContent && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box 
                  sx={{ 
                    width: 12, 
                    height: 12, 
                    borderRadius: '50%', 
                    backgroundColor: getNodeStatusColor(infoModalContent.status, theme),
                    mr: 1.5,
                    boxShadow: `0 0 0 3px ${alpha(getNodeStatusColor(infoModalContent.status, theme), 0.2)}`
                  }} 
                />
                Task Details: {infoModalContent.label}
              </Box>
            </DialogTitle>
            <DialogContent dividers>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>Status</Typography>
                <Chip 
                  label={infoModalContent.status.toUpperCase()}
                  variant="outlined"
                  size="small"
                  sx={{ 
                    borderColor: getNodeStatusColor(infoModalContent.status, theme),
                    color: getNodeStatusColor(infoModalContent.status, theme),
                  }}
                />
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>Tool Details</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Adapter</Typography>
                    <Typography variant="body1">{infoModalContent.adapter}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">Task ID</Typography>
                    <Typography variant="body1" fontFamily="monospace" fontSize="0.85rem">{infoModalContent.task.task_id}</Typography>
                  </Grid>
                </Grid>
                
                {infoModalContent.task.options && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" color="text.secondary">Options</Typography>
                    <Paper variant="outlined" sx={{ p: 1, mt: 0.5, backgroundColor: alpha(theme.palette.background.paper, 0.4) }}>
                      <Typography variant="body2" fontFamily="monospace" fontSize="0.85rem" sx={{ whiteSpace: 'pre-wrap' }}>
                        {JSON.stringify(infoModalContent.task.options, null, 2)}
                      </Typography>
                    </Paper>
                  </Box>
                )}
              </Box>
              
              {(infoModalContent.start_time || infoModalContent.end_time) && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>Timing</Typography>
                  <Grid container spacing={2}>
                    {infoModalContent.start_time && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="text.secondary">Started</Typography>
                        <Typography variant="body1">{new Date(infoModalContent.start_time).toLocaleString()}</Typography>
                      </Grid>
                    )}
                    {infoModalContent.end_time && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color="text.secondary">Completed</Typography>
                        <Typography variant="body1">{new Date(infoModalContent.end_time).toLocaleString()}</Typography>
                      </Grid>
                    )}
                  </Grid>
                </Box>
              )}
              
              {infoModalContent.task.command && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>Command</Typography>
                  <Paper variant="outlined" sx={{ p: 1.5, backgroundColor: theme.palette.background.default }}>
                    <Typography variant="body2" fontFamily="monospace" fontSize="0.85rem" sx={{ whiteSpace: 'pre-wrap' }}>
                      {infoModalContent.task.command}
                    </Typography>
                  </Paper>
                </Box>
              )}
              
              {infoModalContent.task.dependencies && infoModalContent.task.dependencies.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>Dependencies</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {infoModalContent.task.dependencies.map(depId => {
                      const depTask = taskDetails.find(t => t.task_id === depId);
                      return (
                        <Chip 
                          key={depId}
                          label={depTask ? (depTask.name || depTask.adapter) : depId}
                          size="small"
                          variant="outlined"
                          sx={{ 
                            borderColor: depTask ? alpha(getNodeStatusColor(depTask.status, theme), 0.5) : undefined,
                            color: depTask ? getNodeStatusColor(depTask.status, theme) : undefined,
                          }}
                        />
                      );
                    })}
                  </Box>
                </Box>
              )}
              
              {infoModalContent.task.results && (
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>Results</Typography>
                  <Paper variant="outlined" sx={{ p: 1.5, backgroundColor: theme.palette.background.default }}>
                    <Typography variant="body2" fontFamily="monospace" fontSize="0.85rem" sx={{ whiteSpace: 'pre-wrap', maxHeight: 200, overflow: 'auto' }}>
                      {typeof infoModalContent.task.results === 'string' 
                        ? infoModalContent.task.results 
                        : JSON.stringify(infoModalContent.task.results, null, 2)}
                    </Typography>
                  </Paper>
                </Box>
              )}
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseInfoModal} sx={{ textTransform: 'none', fontWeight: 600 }}>
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default TaskGraph;