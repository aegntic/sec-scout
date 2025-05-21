import React from 'react';
import {
  Box,
  Typography,
  Tooltip,
  Paper,
  Avatar,
  useTheme,
} from '@mui/material';
import { styled, alpha } from '@mui/material/styles';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import DoneIcon from '@mui/icons-material/Done';
import ErrorIcon from '@mui/icons-material/Error';
import CancelIcon from '@mui/icons-material/Cancel';
import PendingIcon from '@mui/icons-material/Pending';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import EngineeringIcon from '@mui/icons-material/Engineering';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined';
import PersonIcon from '@mui/icons-material/Person';
import { formatDistanceToNow, format, parseISO, isValid } from 'date-fns';

const TimelineDot = styled(Avatar)(({ theme, status }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return theme.palette.success.main;
      case 'running':
        return theme.palette.primary.main;
      case 'failed':
        return theme.palette.error.main;
      case 'cancelled':
        return theme.palette.warning.main;
      case 'created':
        return theme.palette.info.main;
      default:
        return theme.palette.grey[500];
    }
  };
  
  return {
    width: 36,
    height: 36,
    backgroundColor: alpha(getStatusColor(), 0.1),
    color: getStatusColor(),
    border: `2px solid ${alpha(getStatusColor(), 0.5)}`,
    boxShadow: `0 0 0 4px ${alpha(getStatusColor(), 0.05)}`,
  };
});

const TimelineConnector = styled(Box)(({ theme, active }) => ({
  width: 2,
  flexGrow: 1,
  backgroundColor: active 
    ? alpha(theme.palette.primary.main, 0.3)
    : alpha(theme.palette.divider, 0.3),
  margin: '0 auto',
}));

const TimelineItem = styled(Box)(({ theme }) => ({
  display: 'flex',
  '&:last-child .timeline-connector': {
    display: 'none',
  },
}));

const TimelineContent = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1, 2),
  maxWidth: 'calc(100% - 50px)',
}));

const TimelineRoot = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  maxHeight: 400,
  overflowY: 'auto',
  padding: theme.spacing(1, 0),
  marginRight: -8,
  paddingRight: 8,
  '&::-webkit-scrollbar': {
    width: 6,
  },
  '&::-webkit-scrollbar-track': {
    background: alpha(theme.palette.divider, 0.1),
    borderRadius: 8,
  },
  '&::-webkit-scrollbar-thumb': {
    backgroundColor: alpha(theme.palette.primary.main, 0.2),
    borderRadius: 8,
    '&:hover': {
      backgroundColor: alpha(theme.palette.primary.main, 0.3),
    },
  },
}));

const EmptyState = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(4),
  color: theme.palette.text.secondary,
  textAlign: 'center',
}));

const getStatusDetails = (status) => {
  switch (status) {
    case 'created':
      return {
        icon: <PersonIcon />,
        label: 'Workflow Created',
        description: 'The workflow was created and is ready to be executed'
      };
    case 'pending':
      return {
        icon: <PendingIcon />,
        label: 'Pending Execution',
        description: 'The workflow is waiting to be executed'
      };
    case 'running':
      return {
        icon: <PlayArrowIcon />,
        label: 'Execution Started',
        description: 'The workflow is currently running'
      };
    case 'completed':
      return {
        icon: <DoneIcon />,
        label: 'Execution Completed',
        description: 'The workflow completed successfully'
      };
    case 'failed':
      return {
        icon: <ErrorIcon />,
        label: 'Execution Failed',
        description: 'The workflow failed during execution'
      };
    case 'cancelled':
      return {
        icon: <CancelIcon />,
        label: 'Execution Cancelled',
        description: 'The workflow was cancelled by a user'
      };
    default:
      return {
        icon: <AccessTimeIcon />,
        label: status,
        description: 'Unknown status'
      };
  }
};

const formatDateTime = (dateString) => {
  if (!dateString) return '';
  try {
    const date = parseISO(dateString);
    if (!isValid(date)) return '';
    return format(date, 'MMM d, yyyy h:mm:ss a');
  } catch (e) {
    return '';
  }
};

const WorkflowTimeline = ({ workflow }) => {
  const theme = useTheme();
  
  if (!workflow) {
    return (
      <EmptyState>
        <Typography variant="body2">
          No timeline data available
        </Typography>
      </EmptyState>
    );
  }
  
  // Create timeline events from workflow data
  const events = [];
  
  // Add creation event
  if (workflow.creation_time) {
    events.push({
      status: 'created',
      time: workflow.creation_time,
      details: `Created by ${workflow.created_by || 'System'}`,
    });
  }
  
  // Add start event
  if (workflow.start_time) {
    events.push({
      status: 'running',
      time: workflow.start_time,
      details: 'Execution started',
    });
  }
  
  // Add task events (optionally, for important tasks)
  if (workflow.tasks && workflow.tasks.length > 0) {
    // Sort tasks by start_time (if available)
    const sortedTasks = [...workflow.tasks]
      .filter(task => task.start_time || task.end_time)
      .sort((a, b) => {
        const aTime = a.start_time || a.end_time || '';
        const bTime = b.start_time || b.end_time || '';
        return new Date(aTime) - new Date(bTime);
      });
      
    // Add important task events (limit to avoid overwhelming the timeline)
    const importantTasks = sortedTasks.filter(task => 
      task.status === 'failed' || task.is_critical || task.adapter === 'nuclei' || task.adapter === 'sqlmap'
    );
    
    // Add up to 3 important task events
    importantTasks.slice(0, 3).forEach(task => {
      events.push({
        status: task.status,
        time: task.end_time || task.start_time,
        details: `Task: ${task.name || task.adapter || 'Unknown task'} ${task.status}`,
        isTask: true,
        task,
      });
    });
  }
  
  // Add end event if workflow is completed or failed
  if (workflow.end_time && ['completed', 'failed', 'cancelled'].includes(workflow.status)) {
    events.push({
      status: workflow.status,
      time: workflow.end_time,
      details: `Workflow ${workflow.status}`,
    });
  }
  
  // Sort events by time
  events.sort((a, b) => new Date(a.time) - new Date(b.time));
  
  // Add current state if workflow is still running and no end event
  if (workflow.status === 'running' && !events.find(e => e.time === workflow.end_time)) {
    events.push({
      status: 'running',
      time: new Date().toISOString(),
      details: 'Currently running',
      current: true,
    });
  }
  
  return (
    <TimelineRoot>
      {events.length === 0 ? (
        <EmptyState>
          <AccessTimeIcon sx={{ fontSize: 40, mb: 1, opacity: 0.6 }} />
          <Typography variant="body2">
            No timeline events available
          </Typography>
        </EmptyState>
      ) : (
        events.map((event, index) => {
          const { icon, label } = getStatusDetails(event.status);
          const isActive = index < events.length - 1;
          const isLast = index === events.length - 1;
          
          return (
            <TimelineItem key={`${event.status}-${event.time}-${index}`}>
              <Box sx={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                minWidth: 50,
              }}>
                <Tooltip
                  title={formatDateTime(event.time)}
                  placement="top"
                  arrow
                >
                  <TimelineDot status={event.status}>
                    {icon}
                  </TimelineDot>
                </Tooltip>
                <TimelineConnector 
                  active={isActive} 
                  className="timeline-connector"
                  sx={{
                    display: isLast ? 'none' : 'block',
                    background: isActive && event.status === 'running' 
                      ? `linear-gradient(to bottom, ${alpha(theme.palette.primary.main, 0.3)}, ${alpha(theme.palette.divider, 0.2)})`
                      : undefined,
                  }}
                />
              </Box>
              
              <TimelineContent>
                <Box sx={{ mb: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    {label}
                    {event.current && (
                      <Box 
                        component="span" 
                        sx={{ 
                          ml: 1, 
                          display: 'inline-block', 
                          width: 8, 
                          height: 8, 
                          borderRadius: '50%', 
                          bgcolor: 'primary.main',
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
                        }}
                      />
                    )}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                    {event.time ? formatDistanceToNow(new Date(event.time), { addSuffix: true }) : ''}
                  </Typography>
                </Box>
                
                <Typography variant="body2" color="text.secondary">
                  {event.details}
                </Typography>
                
                {event.isTask && event.task && (
                  <Paper 
                    variant="outlined" 
                    sx={{ 
                      mt: 1, 
                      p: 1, 
                      backgroundColor: alpha(theme.palette.background.paper, 0.4),
                      borderColor: alpha(
                        event.task.status === 'completed' 
                          ? theme.palette.success.main 
                          : event.task.status === 'failed'
                            ? theme.palette.error.main
                            : theme.palette.primary.main, 
                        0.2
                      ),
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                      {event.task.status === 'completed' ? (
                        <CheckCircleOutlineIcon color="success" fontSize="small" sx={{ mr: 1 }} />
                      ) : event.task.status === 'failed' ? (
                        <CancelOutlinedIcon color="error" fontSize="small" sx={{ mr: 1 }} />
                      ) : (
                        <EngineeringIcon color="primary" fontSize="small" sx={{ mr: 1 }} />
                      )}
                      <Typography variant="caption" sx={{ fontWeight: 600 }}>
                        {event.task.adapter} {event.task.status}
                      </Typography>
                    </Box>
                    
                    {event.task.command && (
                      <Typography 
                        variant="caption" 
                        sx={{ 
                          display: 'block', 
                          fontFamily: 'monospace', 
                          whiteSpace: 'nowrap', 
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          bgcolor: alpha(theme.palette.background.paper, 0.6),
                          p: 0.5,
                          borderRadius: 0.5,
                        }}
                      >
                        {event.task.command.substring(0, 50)}
                        {event.task.command.length > 50 ? '...' : ''}
                      </Typography>
                    )}
                  </Paper>
                )}
              </TimelineContent>
            </TimelineItem>
          );
        })
      )}
    </TimelineRoot>
  );
};

export default WorkflowTimeline;