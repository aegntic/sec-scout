import React, { useEffect, useRef } from 'react';
import { Box, Typography, Paper, useTheme, alpha } from '@mui/material';
import { styled } from '@mui/material/styles';

// Task status colors
const getStatusColor = (status, theme) => {
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

// Canvas container
const GraphContainer = styled(Paper)(({ theme }) => ({
  width: '100%',
  height: 300,
  margin: '20px 0',
  background: alpha(theme.palette.background.paper, 0.6),
  position: 'relative',
  overflow: 'hidden',
  boxShadow: 'none',
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  borderRadius: theme.shape.borderRadius,
}));

// Task node
const TaskNode = styled(Box)(({ theme, status }) => ({
  position: 'absolute',
  borderRadius: theme.shape.borderRadius,
  padding: theme.spacing(1.5),
  width: 140,
  height: 70,
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  alignItems: 'center',
  backgroundColor: alpha(getStatusColor(status, theme), 0.1),
  border: `2px solid ${getStatusColor(status, theme)}`,
  boxShadow: `0 4px 10px ${alpha(getStatusColor(status, theme), 0.2)}`,
  transition: 'transform 0.2s, box-shadow 0.2s',
  cursor: 'pointer',
  zIndex: 10,
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: `0 6px 12px ${alpha(getStatusColor(status, theme), 0.3)}`,
  },
  '&::before': {
    content: '""',
    position: 'absolute',
    inset: 0,
    borderRadius: 'inherit',
    padding: 2,
    background: `linear-gradient(135deg, ${getStatusColor(status, theme)}, transparent 80%)`,
    mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
    maskComposite: 'exclude',
    pointerEvents: 'none',
  }
}));

// TaskNodeContent
const TaskNodeContent = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  width: '100%',
}));

// Status indicator
const StatusIndicator = styled(Box)(({ theme, status }) => ({
  width: 8,
  height: 8,
  borderRadius: '50%',
  backgroundColor: getStatusColor(status, theme),
  marginBottom: 4,
  display: 'inline-block',
}));

// Function to draw curved arrows between nodes
const drawArrow = (ctx, fromX, fromY, toX, toY, color) => {
  const headSize = 6;
  
  // Calculate control points for a curved line
  const dx = toX - fromX;
  const dy = toY - fromY;
  const midX = fromX + dx / 2;
  
  // Start drawing
  ctx.beginPath();
  ctx.moveTo(fromX, fromY);
  ctx.quadraticCurveTo(midX, fromY, toX, toY);
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.stroke();
  
  // Draw arrowhead
  const angle = Math.atan2(toY - (fromY + toY) / 2, toX - midX);
  ctx.beginPath();
  ctx.moveTo(toX, toY);
  ctx.lineTo(
    toX - headSize * Math.cos(angle - Math.PI / 6),
    toY - headSize * Math.sin(angle - Math.PI / 6)
  );
  ctx.lineTo(
    toX - headSize * Math.cos(angle + Math.PI / 6),
    toY - headSize * Math.sin(angle + Math.PI / 6)
  );
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();
};

// Main component
const WorkflowGraph = ({ tasks, onTaskClick }) => {
  const theme = useTheme();
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const nodeRefs = useRef({});
  
  // Calculate node positions
  const calculatePositions = () => {
    const containerWidth = containerRef.current?.clientWidth || 800;
    const containerHeight = containerRef.current?.clientHeight || 300;
    
    // Create a dependency graph
    const dependencies = {};
    const dependents = {};
    let maxLevel = 0;
    
    // Initialize
    tasks.forEach(task => {
      dependencies[task.task_id] = task.depends_on || [];
      dependents[task.task_id] = [];
    });
    
    // Fill dependents
    tasks.forEach(task => {
      (task.depends_on || []).forEach(depId => {
        if (dependents[depId]) {
          dependents[depId].push(task.task_id);
        }
      });
    });
    
    // Calculate levels (distance from root)
    const levels = {};
    const calculateLevel = (taskId, level = 0) => {
      if (levels[taskId] !== undefined && levels[taskId] >= level) return;
      
      levels[taskId] = level;
      maxLevel = Math.max(maxLevel, level);
      
      dependents[taskId].forEach(depId => {
        calculateLevel(depId, level + 1);
      });
    };
    
    // Start from root tasks (tasks with no dependencies)
    tasks.forEach(task => {
      if (dependencies[task.task_id].length === 0) {
        calculateLevel(task.task_id);
      }
    });
    
    // Tasks with no level assigned yet (disconnected or circular)
    tasks.forEach(task => {
      if (levels[task.task_id] === undefined) {
        calculateLevel(task.task_id);
      }
    });
    
    // Count tasks per level
    const tasksPerLevel = {};
    Object.keys(levels).forEach(taskId => {
      const level = levels[taskId];
      tasksPerLevel[level] = (tasksPerLevel[level] || 0) + 1;
    });
    
    // Calculate positions
    const positions = {};
    
    // Track placed tasks per level
    const placedPerLevel = {};
    
    Object.keys(levels).forEach(taskId => {
      const level = levels[taskId];
      placedPerLevel[level] = placedPerLevel[level] || 0;
      
      const levelWidth = containerWidth / (maxLevel + 1);
      const x = levelWidth * level + levelWidth / 2;
      
      const taskHeight = 70;
      const verticalSpacing = 20;
      const levelHeight = tasksPerLevel[level] * (taskHeight + verticalSpacing) - verticalSpacing;
      
      const y = (containerHeight - levelHeight) / 2 + 
                placedPerLevel[level] * (taskHeight + verticalSpacing) + taskHeight / 2;
      
      positions[taskId] = { x, y };
      placedPerLevel[level]++;
    });
    
    return positions;
  };

  // Draw the workflow graph
  useEffect(() => {
    if (!canvasRef.current || !containerRef.current || tasks.length === 0) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const { width, height } = canvas;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Calculate positions
    const positions = calculatePositions();
    
    // Draw connections
    tasks.forEach(task => {
      const fromPos = positions[task.task_id];
      if (!fromPos) return;
      
      // Get node dimensions
      const fromNode = nodeRefs.current[task.task_id];
      if (!fromNode) return;
      
      const fromRect = fromNode.getBoundingClientRect();
      const containerRect = containerRef.current.getBoundingClientRect();
      
      const fromX = fromRect.left + fromRect.width / 2 - containerRect.left;
      const fromY = fromRect.top + fromRect.height - containerRect.top;
      
      // Draw connections to dependents
      tasks.forEach(otherTask => {
        if ((otherTask.depends_on || []).includes(task.task_id)) {
          const toNode = nodeRefs.current[otherTask.task_id];
          if (!toNode) return;
          
          const toRect = toNode.getBoundingClientRect();
          const toX = toRect.left + toRect.width / 2 - containerRect.left;
          const toY = toRect.top - containerRect.top;
          
          // Get color based on dependency status
          let connectionColor;
          if (task.status === 'completed') {
            connectionColor = getStatusColor(otherTask.status, theme);
          } else if (task.status === 'failed' || task.status === 'cancelled') {
            connectionColor = alpha(theme.palette.grey[500], 0.5);
          } else {
            connectionColor = alpha(theme.palette.grey[500], 0.5);
          }
          
          drawArrow(ctx, fromX, fromY, toX, toY, connectionColor);
        }
      });
    });
  }, [tasks, theme]);
  
  // Handle canvas resize
  useEffect(() => {
    const handleResize = () => {
      if (canvasRef.current && containerRef.current) {
        const canvas = canvasRef.current;
        const container = containerRef.current;
        
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
        
        // Redraw on resize
        const event = new Event('resize');
        window.dispatchEvent(event);
      }
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);
  
  // Get positions for task nodes
  const positions = calculatePositions();
  
  return (
    <GraphContainer ref={containerRef}>
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
        }}
      />
      
      {tasks.map(task => {
        const pos = positions[task.task_id];
        if (!pos) return null;
        
        return (
          <TaskNode
            key={task.task_id}
            ref={el => nodeRefs.current[task.task_id] = el}
            status={task.status}
            style={{
              left: pos.x - 70, // Half width
              top: pos.y - 35,  // Half height
            }}
            onClick={() => onTaskClick && onTaskClick(task)}
          >
            <TaskNodeContent>
              <StatusIndicator status={task.status} />
              <Typography variant="subtitle2" noWrap>
                {task.task_name || `Task ${task.task_id.substring(0, 6)}`}
              </Typography>
              <Typography variant="caption" color="text.secondary" noWrap>
                {task.adapter_name}
              </Typography>
            </TaskNodeContent>
          </TaskNode>
        );
      })}
    </GraphContainer>
  );
};

export default WorkflowGraph;