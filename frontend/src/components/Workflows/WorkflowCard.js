import React from 'react';
import { 
  Card, 
  CardContent, 
  CardActions, 
  Button, 
  Typography, 
  Box,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
  CardActionArea
} from '@mui/material';
import { styled } from '@mui/material/styles';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DeleteIcon from '@mui/icons-material/Delete';
import AssessmentIcon from '@mui/icons-material/Assessment';
import { formatDistanceToNow } from 'date-fns';

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

const CardHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'flex-start',
  marginBottom: theme.spacing(1),
}));

const TagsContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexWrap: 'wrap',
  gap: theme.spacing(0.5),
  marginTop: theme.spacing(1),
}));

const ProgressIndicator = styled(Box)(({ theme, status }) => ({
  display: 'flex',
  flexDirection: 'column',
  width: '100%',
  marginTop: theme.spacing(1),
}));

const ProgressStatsWrapper = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  marginTop: theme.spacing(0.5),
}));

const WorkflowCard = ({ 
  workflow, 
  onExecute, 
  onCancel, 
  onView, 
  onDelete, 
  onViewResults,
  onClick 
}) => {
  const {
    workflow_id,
    name,
    description,
    status,
    start_time,
    end_time,
    target,
    tags = [],
    task_count = 0,
    completed_tasks = 0,
    failed_tasks = 0,
  } = workflow;

  // Calculate progress percentage
  const progress = task_count > 0 ? (completed_tasks / task_count) * 100 : 0;
  
  // Format times for display
  const getTimeDisplay = (isoString) => {
    if (!isoString) return 'Not started';
    try {
      return formatDistanceToNow(new Date(isoString), { addSuffix: true });
    } catch (e) {
      return isoString;
    }
  };

  // Handle button clicks without triggering card click
  const handleButtonClick = (event, callback) => {
    event.stopPropagation();
    if (callback) callback(workflow_id);
  };

  return (
    <Card 
      elevation={3} 
      sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 8,
        }
      }}
    >
      <CardActionArea onClick={() => onClick && onClick(workflow_id)} sx={{ flexGrow: 1 }}>
        <CardContent>
          <CardHeader>
            <Typography variant="h6" component="div" noWrap sx={{ maxWidth: 'calc(100% - 100px)' }}>
              {name}
            </Typography>
            <StatusChip 
              size="small" 
              label={status?.toUpperCase()} 
              status={status} 
            />
          </CardHeader>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1, height: '40px', overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
            {description}
          </Typography>
          
          {target && (
            <Typography variant="body2" sx={{ mb: 1 }}>
              <Box component="span" sx={{ fontWeight: 'bold', mr: 0.5 }}>Target:</Box>
              <Box component="span" sx={{ fontFamily: 'monospace', fontSize: '0.85rem', color: 'primary.light' }}>{target}</Box>
            </Typography>
          )}
          
          {status === 'running' && (
            <ProgressIndicator status={status}>
              <LinearProgress 
                variant="determinate" 
                value={progress} 
                sx={{ height: 6, borderRadius: 3 }}
              />
              <ProgressStatsWrapper>
                <Typography variant="caption" color="text.secondary">
                  {completed_tasks} of {task_count} tasks completed
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {Math.round(progress)}%
                </Typography>
              </ProgressStatsWrapper>
            </ProgressIndicator>
          )}
          
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
            <Typography variant="caption" color="text.secondary">
              {start_time ? `Started ${getTimeDisplay(start_time)}` : 'Not started'}
            </Typography>
            {end_time && (
              <Typography variant="caption" color="text.secondary">
                {`Ended ${getTimeDisplay(end_time)}`}
              </Typography>
            )}
          </Box>
          
          <TagsContainer>
            {tags.map((tag, index) => (
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
        </CardContent>
      </CardActionArea>

      <CardActions disableSpacing sx={{ p: 1, pt: 0, justifyContent: 'flex-end' }}>
        {['pending', 'completed', 'failed', 'cancelled'].includes(status) && (
          <Tooltip title="Execute workflow">
            <IconButton 
              size="small" 
              color="primary"
              onClick={(e) => handleButtonClick(e, onExecute)}
            >
              <PlayArrowIcon />
            </IconButton>
          </Tooltip>
        )}
        
        {status === 'running' && (
          <Tooltip title="Cancel workflow">
            <IconButton 
              size="small" 
              color="error"
              onClick={(e) => handleButtonClick(e, onCancel)}
            >
              <StopIcon />
            </IconButton>
          </Tooltip>
        )}
        
        <Tooltip title="View details">
          <IconButton 
            size="small"
            color="info"
            onClick={(e) => handleButtonClick(e, onView)}
          >
            <VisibilityIcon />
          </IconButton>
        </Tooltip>

        {status === 'completed' && (
          <Tooltip title="View results">
            <IconButton 
              size="small"
              color="success"
              onClick={(e) => handleButtonClick(e, onViewResults)}
            >
              <AssessmentIcon />
            </IconButton>
          </Tooltip>
        )}
        
        <Tooltip title="Delete workflow">
          <IconButton 
            size="small"
            color="error"
            onClick={(e) => handleButtonClick(e, onDelete)}
          >
            <DeleteIcon />
          </IconButton>
        </Tooltip>
      </CardActions>
    </Card>
  );
};

export default WorkflowCard;