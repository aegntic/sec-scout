import React, { useState, useEffect } from 'react';
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
} from 'reactflow';
import 'reactflow/dist/style.css';
import RefreshIcon from '@mui/icons-material/Refresh';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit';
import InfoIcon from '@mui/icons-material/Info';
import apiService from '../../services/api';

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
}));

const TaskGraph = ({ workflowId, tasks = [] }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fullscreen, setFullscreen] = useState(false);
  
  // Convert tasks to ReactFlow nodes and edges
  const buildGraph = (tasks) => {
    if (!tasks || tasks.length === 0) {
      setNodes([]);
      setEdges([]);
      return;
    }
    
    const calculatedNodes = [];
    const calculatedEdges = [];
    const taskMap = new Map();
    
    // Create a map of task IDs to tasks for quick lookup
    tasks.forEach(task => {
      taskMap.set(task.task_id, task);
    });
    
    // Calculate positions based on dependencies
    // This is a simple layering algorithm
    const processedTasks = new Set();
    const layers = [];
    let currentLayer = [];
    
    // Find tasks with no dependencies
    tasks.forEach(task => {
      if (!task.dependencies || task.dependencies.length === 0) {
        currentLayer.push(task);
        processedTasks.add(task.task_id);
      }
    });
    
    layers.push([...currentLayer]);
    
    // Continue processing layers until all tasks are processed
    while (processedTasks.size < tasks.length) {
      currentLayer = [];
      
      // Find tasks whose dependencies are all processed
      tasks.forEach(task => {
        if (processedTasks.has(task.task_id)) return;
        
        const allDependenciesProcessed = !task.dependencies || task.dependencies.every(depId => 
          processedTasks.has(depId)
        );
        
        if (allDependenciesProcessed) {
          currentLayer.push(task);
          processedTasks.add(task.task_id);
        }
      });
      
      // If we couldn't process any tasks, we might have a cycle
      if (currentLayer.length === 0) {
        // Handle potentially cyclic dependencies
        tasks.forEach(task => {
          if (!processedTasks.has(task.task_id)) {
            currentLayer.push(task);
            processedTasks.add(task.task_id);
          }
        });
      }
      
      if (currentLayer.length > 0) {
        layers.push([...currentLayer]);
      }
    }
    
    // Now create nodes based on layers
    const horizontalSpacing = 300;
    const verticalSpacing = 150;
    
    layers.forEach((layer, layerIndex) => {
      layer.forEach((task, taskIndex) => {
        // Calculate position
        const x = layerIndex * horizontalSpacing + 50;
        const y = taskIndex * verticalSpacing + 50;
        
        // Create node
        calculatedNodes.push({
          id: task.task_id,
          type: 'taskNode',
          position: { x, y },
          data: {
            task: task,
            adapter: task.adapter,
            label: task.name || task.adapter,
            status: task.status || 'pending',
            start_time: task.start_time,
            end_time: task.end_time,
            progress: task.progress || 0,
          },
        });
        
        // Create edges for dependencies
        if (task.dependencies) {
          task.dependencies.forEach(depId => {
            calculatedEdges.push({
              id: `${depId}-${task.task_id}`,
              source: depId,
              target: task.task_id,
              type: 'smoothstep',
              animated: task.status === 'running',
              style: { strokeWidth: 2 },
              markerEnd: {
                type: MarkerType.ArrowClosed,
                width: 15,
                height: 15,
              },
            });
          });
        }
      });
    });
    
    setNodes(calculatedNodes);
    setEdges(calculatedEdges);
  };
  
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
  
  // Initialize the graph
  useEffect(() => {
    if (tasks.length > 0) {
      buildGraph(tasks);
      setLoading(false);
    } else {
      fetchTasks();
    }
  }, [workflowId]);
  
  const handleRefresh = () => {
    fetchTasks();
  };
  
  const toggleFullscreen = () => {
    setFullscreen(!fullscreen);
  };
  
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }
  
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
  
  if (nodes.length === 0) {
    return (
      <Paper 
        elevation={0}
        sx={{ 
          p: 3, 
          textAlign: 'center', 
          backgroundColor: theme => alpha(theme.palette.background.paper, 0.5),
          backdropFilter: 'blur(10px)',
        }}
      >
        <InfoIcon sx={{ fontSize: 48, color: 'primary.main', opacity: 0.7, mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          No tasks found in this workflow
        </Typography>
        <Typography variant="body2" color="text.secondary">
          This workflow doesn't have any tasks defined or the tasks failed to load.
        </Typography>
        <Button 
          variant="outlined" 
          startIcon={<RefreshIcon />} 
          sx={{ mt: 2 }}
          onClick={handleRefresh}
        >
          Refresh
        </Button>
      </Paper>
    );
  }
  
  return (
    <Box sx={{ 
      height: fullscreen ? '100vh' : '600px', 
      width: fullscreen ? '100vw' : '100%',
      position: fullscreen ? 'fixed' : 'relative',
      top: fullscreen ? 0 : 'auto',
      left: fullscreen ? 0 : 'auto',
      zIndex: fullscreen ? 1300 : 'auto',
      bgcolor: 'background.paper',
    }}>
      <StyledReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
      >
        <Controls />
        <MiniMap 
          nodeStrokeColor={(n) => {
            if (n.data?.status === 'completed') return '#4caf50';
            if (n.data?.status === 'running') return '#2196f3';
            if (n.data?.status === 'failed') return '#f44336';
            return '#555';
          }}
          nodeColor={(n) => {
            if (n.data?.status === 'completed') return '#4caf5020';
            if (n.data?.status === 'running') return '#2196f320';
            if (n.data?.status === 'failed') return '#f4433620';
            return '#55555520';
          }}
          nodeBorderRadius={2}
        />
        <Background color="#aaa" gap={16} />
        <Panel position="top-right">
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Refresh tasks">
              <IconButton 
                onClick={handleRefresh} 
                size="small"
                sx={{ bgcolor: 'background.paper', boxShadow: 1 }}
              >
                <RefreshIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title={fullscreen ? "Exit fullscreen" : "Fullscreen"}>
              <IconButton 
                onClick={toggleFullscreen} 
                size="small"
                sx={{ bgcolor: 'background.paper', boxShadow: 1 }}
              >
                {fullscreen ? <FullscreenExitIcon fontSize="small" /> : <FullscreenIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
          </Box>
        </Panel>
        <Panel position="top-left">
          <Box sx={{ 
            p: 1, 
            bgcolor: 'background.paper', 
            borderRadius: 1, 
            boxShadow: 1,
            display: 'flex',
            flexWrap: 'wrap',
            gap: 1 
          }}>
            <Chip 
              size="small" 
              color="primary" 
              variant="outlined" 
              label="Running"
              sx={{ height: 20, '& .MuiChip-label': { px: 1 } }}
            />
            <Chip 
              size="small" 
              color="success" 
              variant="outlined" 
              label="Completed" 
              sx={{ height: 20, '& .MuiChip-label': { px: 1 } }}
            />
            <Chip 
              size="small" 
              color="error" 
              variant="outlined" 
              label="Failed" 
              sx={{ height: 20, '& .MuiChip-label': { px: 1 } }}
            />
            <Chip 
              size="small" 
              color="default" 
              variant="outlined" 
              label="Pending" 
              sx={{ height: 20, '& .MuiChip-label': { px: 1 } }}
            />
          </Box>
        </Panel>
      </StyledReactFlow>
    </Box>
  );
};

export default TaskGraph;