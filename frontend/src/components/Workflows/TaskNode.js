import React from 'react';
import { Handle, Position } from 'reactflow';
import {
  Box,
  Typography,
  LinearProgress,
  Tooltip,
  Chip,
} from '@mui/material';
import { styled, alpha } from '@mui/material/styles';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import DoneIcon from '@mui/icons-material/Done';
import ErrorIcon from '@mui/icons-material/Error';
import PendingIcon from '@mui/icons-material/Pending';
import { formatDistanceToNow } from 'date-fns';

const NodeContainer = styled(Box)(({ theme, status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'completed': return theme.palette.success.main;
      case 'running': return theme.palette.primary.main;
      case 'failed': return theme.palette.error.main;
      default: return theme.palette.grey[500];
    }
  };
  
  return {
    minWidth: 200,
    maxWidth: 250,
    backgroundColor: alpha(theme.palette.background.paper, 0.9),
    border: `2px solid ${getStatusColor()}`,
    borderRadius: theme.shape.borderRadius,
    padding: theme.spacing(1),
    fontSize: 12,
    color: theme.palette.text.primary,
    backdropFilter: 'blur(4px)',
  };
});

const StatusIconContainer = styled(Box)(({ theme, status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'completed': return theme.palette.success.main;
      case 'running': return theme.palette.primary.main;
      case 'failed': return theme.palette.error.main;
      default: return theme.palette.grey[500];
    }
  };
  
  return {
    position: 'absolute',
    top: -10,
    right: -10,
    backgroundColor: theme.palette.background.paper,
    border: `2px solid ${getStatusColor()}`,
    borderRadius: '50%',
    width: 24,
    height: 24,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: getStatusColor(),
  };
});

const ProgressIndicator = styled(Box)(({ theme }) => ({
  width: '100%',
  marginTop: theme.spacing(1),
}));

const AdapterBadge = styled(Chip)(({ theme }) => ({
  position: 'absolute',
  top: -8,
  left: 8,
  height: 20,
  borderRadius: 4,
  fontSize: '0.65rem',
  backgroundColor: alpha(theme.palette.primary.main, 0.15),
  color: theme.palette.primary.main,
  '& .MuiChip-label': {
    padding: '0 6px',
  }
}));

const TaskNode = ({ data }) => {
  const {
    task,
    adapter,
    label,
    status,
    start_time,
    end_time,
    progress = 0,
  } = data;
  
  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <DoneIcon fontSize="small" />;
      case 'running':
        return <PlayArrowIcon fontSize="small" />;
      case 'failed':
        return <ErrorIcon fontSize="small" />;
      default:
        return <PendingIcon fontSize="small" />;
    }
  };
  
  // Format times for display
  const getTimeDisplay = (isoString) => {
    if (!isoString) return 'Not started';
    try {
      return formatDistanceToNow(new Date(isoString), { addSuffix: true });
    } catch (e) {
      return isoString;
    }
  };
  
  // Calculate duration if applicable
  const getDuration = () => {
    if (!start_time) return null;
    
    const start = new Date(start_time);
    const end = end_time ? new Date(end_time) : new Date();
    
    const durationMs = end - start;
    const seconds = Math.floor(durationMs / 1000);
    
    if (seconds < 60) {
      return `${seconds}s`;
    } else if (seconds < 3600) {
      return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    } else {
      return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
    }
  };
  
  const getTooltipContent = () => {
    return (
      <Box sx={{ p: 1 }}>
        <Typography variant="subtitle2">{label}</Typography>
        <Typography variant="body2" sx={{ mt: 0.5 }}>Adapter: {adapter}</Typography>
        <Typography variant="body2">Status: {status}</Typography>
        {start_time && <Typography variant="body2">Started: {getTimeDisplay(start_time)}</Typography>}
        {end_time && <Typography variant="body2">Ended: {getTimeDisplay(end_time)}</Typography>}
        {getDuration() && <Typography variant="body2">Duration: {getDuration()}</Typography>}
        {task.command && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="caption" sx={{ fontWeight: 'bold' }}>Command:</Typography>
            <Typography variant="caption" sx={{ display: 'block', fontFamily: 'monospace', whiteSpace: 'pre-wrap', bgcolor: 'background.paper', p: 0.5, borderRadius: 0.5, fontSize: '0.7rem' }}>
              {task.command}
            </Typography>
          </Box>
        )}
      </Box>
    );
  };
  
  return (
    <Tooltip title={getTooltipContent()} placement="top" arrow>
      <NodeContainer status={status}>
        <Handle
          type="target"
          position={Position.Left}
          style={{ background: '#555' }}
        />
        
        <StatusIconContainer status={status}>
          {getStatusIcon()}
        </StatusIconContainer>
        
        <AdapterBadge
          label={adapter}
          size="small"
        />
        
        <Typography 
          variant="subtitle2" 
          sx={{ 
            fontWeight: 600, 
            mt: 1.5, 
            mb: 0.5,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {label}
        </Typography>
        
        {status === 'running' && (
          <ProgressIndicator>
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              sx={{ height: 4, borderRadius: 2 }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'right', mt: 0.5 }}>
              {Math.round(progress)}%
            </Typography>
          </ProgressIndicator>
        )}
        
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
          {status === 'completed' && 'Completed'}
          {status === 'running' && 'Running'}
          {status === 'failed' && 'Failed'}
          {status === 'pending' && 'Pending'}
          
          {(status === 'completed' || status === 'running' || status === 'failed') && start_time && (
            <>
              {' - '}
              {getDuration()}
            </>
          )}
        </Typography>
        
        <Handle
          type="source"
          position={Position.Right}
          style={{ background: '#555' }}
        />
      </NodeContainer>
    </Tooltip>
  );
};

export default TaskNode;