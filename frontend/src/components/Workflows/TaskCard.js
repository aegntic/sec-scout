import React from 'react';
import { 
  Card, 
  CardContent, 
  Typography, 
  Box,
  Chip,
  LinearProgress,
  styled,
  alpha,
  Tooltip,
  IconButton
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { formatDistanceToNow } from 'date-fns';

// Tool icons
import BugReportIcon from '@mui/icons-material/BugReport'; // ZAP
import NetworkCheckIcon from '@mui/icons-material/NetworkCheck'; // Nmap
import StorageIcon from '@mui/icons-material/Storage'; // Trivy
import CodeIcon from '@mui/icons-material/Code'; // SQLMap
import SearchIcon from '@mui/icons-material/Search'; // Nuclei
import LanguageIcon from '@mui/icons-material/Language'; // Nikto
import TerminalIcon from '@mui/icons-material/Terminal'; // Default

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
    height: '20px',
    '& .MuiChip-label': {
      padding: '0 6px',
      fontSize: '0.7rem',
    }
  };
});

const ToolIcon = styled(Box)(({ theme, tool }) => {
  const getToolColor = (tool) => {
    const toolColors = {
      zap: theme.palette.error.main,
      nmap: theme.palette.info.main,
      trivy: theme.palette.warning.main,
      sqlmap: theme.palette.error.dark,
      nuclei: theme.palette.primary.main,
      nikto: theme.palette.secondary.main,
    };
    return toolColors[tool.toLowerCase()] || theme.palette.primary.light;
  };
  
  const color = getToolColor(tool);
  
  return {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: 32,
    height: 32,
    borderRadius: '50%',
    backgroundColor: alpha(color, 0.1),
    color: color,
    marginRight: theme.spacing(1.5),
  };
});

const getToolIcon = (adapterName) => {
  switch(adapterName.toLowerCase()) {
    case 'zap':
      return <BugReportIcon />;
    case 'nmap':
      return <NetworkCheckIcon />;
    case 'trivy':
      return <StorageIcon />;
    case 'sqlmap':
      return <CodeIcon />;
    case 'nuclei':
      return <SearchIcon />;
    case 'nikto':
      return <LanguageIcon />;
    default:
      return <TerminalIcon />;
  }
};

const TaskCard = ({ task, onClick }) => {
  const {
    task_id,
    task_name,
    adapter_name,
    status,
    start_time,
    end_time,
    error_message,
    result_summary,
    finding_count
  } = task;
  
  // Format times for display
  const getTimeDisplay = (isoString) => {
    if (!isoString) return null;
    try {
      return formatDistanceToNow(new Date(isoString), { addSuffix: true });
    } catch (e) {
      return isoString;
    }
  };
  
  const startTimeDisplay = getTimeDisplay(start_time);
  const endTimeDisplay = getTimeDisplay(end_time);
  const duration = start_time && end_time 
    ? new Date(end_time) - new Date(start_time) 
    : null;
  
  // Format duration
  const formatDuration = (ms) => {
    if (!ms) return null;
    
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  };
  
  const durationDisplay = formatDuration(duration);

  return (
    <Card 
      elevation={2} 
      sx={{ 
        mb: 2, 
        borderLeft: (theme) => `4px solid ${
          status === 'completed' ? theme.palette.success.main :
          status === 'running' ? theme.palette.primary.main :
          status === 'failed' ? theme.palette.error.main :
          status === 'cancelled' ? theme.palette.warning.main :
          theme.palette.grey[500]
        }`,
        transition: 'transform 0.2s',
        '&:hover': {
          transform: 'translateX(4px)',
        }
      }}
    >
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
            <ToolIcon tool={adapter_name}>
              {getToolIcon(adapter_name)}
            </ToolIcon>
            
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {task_name || `Task ${task_id}`}
              </Typography>
              
              <Typography variant="caption" color="text.secondary">
                {adapter_name}
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <StatusChip 
              size="small" 
              label={status?.toUpperCase()} 
              status={status}
            />
            
            <Tooltip title="View task details">
              <IconButton 
                size="small" 
                onClick={() => onClick && onClick(task)}
                sx={{ ml: 1 }}
              >
                <VisibilityIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        {status === 'running' && (
          <LinearProgress sx={{ mt: 1.5, mb: 1, height: 4, borderRadius: 2 }} />
        )}
        
        {finding_count !== undefined && status === 'completed' && (
          <Box sx={{ mt: 1.5, display: 'flex', alignItems: 'center' }}>
            <Chip 
              size="small"
              label={`${finding_count} findings`}
              color={finding_count > 0 ? "error" : "success"}
              variant="outlined"
              sx={{ 
                height: '20px',
                '& .MuiChip-label': { px: 1, py: 0.25, fontSize: '0.7rem' }
              }}
            />
          </Box>
        )}
        
        {error_message && status === 'failed' && (
          <Typography variant="caption" color="error" sx={{ display: 'block', mt: 1.5 }}>
            Error: {error_message}
          </Typography>
        )}
        
        <Box sx={{ mt: 1.5, display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'space-between' }}>
          {startTimeDisplay && (
            <Typography variant="caption" color="text.secondary">
              Started {startTimeDisplay}
            </Typography>
          )}
          
          {endTimeDisplay && (
            <Typography variant="caption" color="text.secondary">
              Finished {endTimeDisplay}
            </Typography>
          )}
          
          {durationDisplay && (
            <Typography variant="caption" color="text.secondary">
              Duration: {durationDisplay}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default TaskCard;