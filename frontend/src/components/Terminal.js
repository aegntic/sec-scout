import React, { useRef, useEffect } from 'react';
import { Box, Typography, IconButton, Paper } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import StopIcon from '@mui/icons-material/Stop';
import ClearIcon from '@mui/icons-material/Clear';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';

const Terminal = ({ title, logs, isRunning, onStart, onStop, onClear }) => {
  const terminalRef = useRef(null);

  // Auto-scroll to bottom when new logs are added
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  const copyToClipboard = () => {
    if (logs) {
      navigator.clipboard.writeText(logs).then(
        () => {
          console.log('Terminal content copied to clipboard');
        },
        (err) => {
          console.error('Could not copy text: ', err);
        }
      );
    }
  };

  // Function to apply color to log entries based on type
  const formatLogs = (text) => {
    if (!text) return '';
    
    return text.split('\\n').map((line, index) => {
      if (line.includes('[INFO]')) {
        return <div key={index} className="terminal-text-info">{line}</div>;
      } else if (line.includes('[SUCCESS]')) {
        return <div key={index} className="terminal-text-success">{line}</div>;
      } else if (line.includes('[WARNING]')) {
        return <div key={index} className="terminal-text-warning">{line}</div>;
      } else if (line.includes('[ERROR]')) {
        return <div key={index} className="terminal-text-error">{line}</div>;
      } else {
        return <div key={index}>{line}</div>;
      }
    });
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        mb: 3, 
        backgroundColor: '#1a1a1a', 
        borderRadius: 2,
        overflow: 'hidden'
      }}
    >
      <Box className="terminal-header" sx={{ px: 2, py: 1, backgroundColor: '#252525' }}>
        <Typography variant="subtitle1" className="terminal-header-title">
          {title || 'Terminal'}
        </Typography>
        <Box>
          {isRunning ? (
            <IconButton size="small" onClick={onStop} title="Stop">
              <StopIcon fontSize="small" sx={{ color: '#f39c12' }} />
            </IconButton>
          ) : (
            <IconButton size="small" onClick={onStart} title="Start">
              <PlayArrowIcon fontSize="small" sx={{ color: '#2ecc71' }} />
            </IconButton>
          )}
          <IconButton size="small" onClick={onClear} title="Clear">
            <ClearIcon fontSize="small" sx={{ color: '#e74c3c' }} />
          </IconButton>
          <IconButton size="small" onClick={copyToClipboard} title="Copy">
            <ContentCopyIcon fontSize="small" sx={{ color: '#3498db' }} />
          </IconButton>
        </Box>
      </Box>
      <Box 
        ref={terminalRef}
        className="terminal"
        sx={{ 
          height: 400, 
          overflowY: 'auto', 
          p: 2,
          fontFamily: '"Courier New", monospace',
          fontSize: '0.875rem'
        }}
      >
        {formatLogs(logs)}
        {isRunning && (
          <Box component="span" sx={{ animation: 'blink 1s step-end infinite' }}>
            _
          </Box>
        )}
      </Box>
      <style jsx="true">{`
        @keyframes blink {
          from, to { opacity: 1; }
          50% { opacity: 0; }
        }
      `}</style>
    </Paper>
  );
};

export default Terminal;