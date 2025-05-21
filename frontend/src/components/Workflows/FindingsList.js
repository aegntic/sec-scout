import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Divider,
  Chip,
  TextField,
  InputAdornment,
  IconButton,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Tooltip,
  Alert,
} from '@mui/material';
import { styled, alpha } from '@mui/material/styles';
import SearchIcon from '@mui/icons-material/Search';
import RefreshIcon from '@mui/icons-material/Refresh';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SecurityIcon from '@mui/icons-material/Security';
import BugReportIcon from '@mui/icons-material/BugReport';
import CodeIcon from '@mui/icons-material/Code';
import InfoIcon from '@mui/icons-material/Info';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

const SeverityChip = styled(Chip)(({ theme, severity }) => {
  const getSeverityColor = () => {
    switch (severity) {
      case 'critical': return theme.palette.error.dark;
      case 'high': return theme.palette.error.main;
      case 'medium': return theme.palette.warning.main;
      case 'low': return theme.palette.info.main;
      case 'info': return theme.palette.grey[500];
      default: return theme.palette.grey[500];
    }
  };
  
  return {
    backgroundColor: `${getSeverityColor()}20`,
    color: getSeverityColor(),
    fontWeight: 600,
    '& .MuiChip-label': {
      padding: '0 8px',
    }
  };
});

const FindingCard = styled(Paper)(({ theme, severity }) => {
  const getSeverityColor = () => {
    switch (severity) {
      case 'critical': return theme.palette.error.dark;
      case 'high': return theme.palette.error.main;
      case 'medium': return theme.palette.warning.main;
      case 'low': return theme.palette.info.main;
      case 'info': return theme.palette.grey[500];
      default: return theme.palette.grey[500];
    }
  };
  
  return {
    borderLeft: `4px solid ${getSeverityColor()}`,
    marginBottom: theme.spacing(2),
    overflow: 'hidden',
  };
});

const CodeBlock = styled(Box)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.background.default, 0.7),
  borderRadius: theme.shape.borderRadius,
  padding: theme.spacing(1),
  fontFamily: 'monospace',
  fontSize: '0.85rem',
  overflowX: 'auto',
  whiteSpace: 'pre-wrap',
  wordBreak: 'break-all',
  marginTop: theme.spacing(1),
  marginBottom: theme.spacing(1),
}));

const AdapterChip = styled(Chip)(({ theme }) => ({
  backgroundColor: alpha(theme.palette.primary.main, 0.15),
  color: theme.palette.primary.main,
  fontWeight: 500,
  height: 24,
  fontSize: '0.75rem',
  '& .MuiChip-label': {
    padding: '0 8px',
  }
}));

const FindingsList = ({ findings = [], workflowId, onRefresh }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    severity: [],
    adapter: [],
  });
  
  // Count findings by severity for summary
  const findingCounts = findings.reduce((acc, finding) => {
    const severity = finding.severity || 'unknown';
    acc[severity] = (acc[severity] || 0) + 1;
    return acc;
  }, {});
  
  // Get unique adapters for filtering
  const adapters = [...new Set(findings.map(finding => finding.adapter))];
  
  // Handle search input
  const handleSearch = (event) => {
    setSearchTerm(event.target.value);
  };
  
  // Handle filter changes
  const handleFilterChange = (filterType, value) => {
    setFilters({
      ...filters,
      [filterType]: value,
    });
  };
  
  // Filter findings based on search and filters
  const filteredFindings = findings.filter(finding => {
    // Apply search filter
    const searchMatch = searchTerm === '' || 
      (finding.title && finding.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (finding.description && finding.description.toLowerCase().includes(searchTerm.toLowerCase()));
    
    // Apply severity filter
    const severityMatch = filters.severity.length === 0 || 
      filters.severity.includes(finding.severity || 'unknown');
    
    // Apply adapter filter
    const adapterMatch = filters.adapter.length === 0 || 
      filters.adapter.includes(finding.adapter);
    
    return searchMatch && severityMatch && adapterMatch;
  });
  
  // Format URL for display
  const formatUrl = (url) => {
    if (!url) return null;
    try {
      const urlObj = new URL(url);
      return `${urlObj.hostname}${urlObj.pathname}`;
    } catch (e) {
      return url;
    }
  };
  
  if (findings.length === 0) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="info" sx={{ mb: 2 }}>
          No findings available for this workflow. This could mean the scan found no vulnerabilities, or the workflow has not completed yet.
        </Alert>
        <Button 
          variant="outlined" 
          startIcon={<RefreshIcon />} 
          onClick={onRefresh}
        >
          Refresh Findings
        </Button>
      </Box>
    );
  }
  
  return (
    <Box sx={{ p: 2 }}>
      {/* Summary */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Findings Summary
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {Object.entries(findingCounts).map(([severity, count]) => (
            <SeverityChip 
              key={severity}
              label={`${severity}: ${count}`}
              severity={severity}
            />
          ))}
          <Chip 
            label={`Total: ${findings.length}`}
            variant="outlined"
          />
        </Box>
      </Box>
      
      <Divider sx={{ mb: 3 }} />
      
      {/* Search and Filters */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            placeholder="Search findings..."
            value={searchTerm}
            onChange={handleSearch}
            variant="outlined"
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item xs={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Severity</InputLabel>
            <Select
              multiple
              value={filters.severity}
              onChange={(e) => handleFilterChange('severity', e.target.value)}
              label="Severity"
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <SeverityChip key={value} label={value} severity={value} size="small" />
                  ))}
                </Box>
              )}
            >
              {['critical', 'high', 'medium', 'low', 'info'].map((severity) => (
                <MenuItem key={severity} value={severity}>
                  {severity}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Adapter</InputLabel>
            <Select
              multiple
              value={filters.adapter}
              onChange={(e) => handleFilterChange('adapter', e.target.value)}
              label="Adapter"
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <AdapterChip key={value} label={value} size="small" />
                  ))}
                </Box>
              )}
            >
              {adapters.map((adapter) => (
                <MenuItem key={adapter} value={adapter}>
                  {adapter}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      
      {/* Findings List */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="subtitle1">
          {filteredFindings.length} {filteredFindings.length === 1 ? 'finding' : 'findings'} found
        </Typography>
        <Tooltip title="Refresh findings">
          <IconButton onClick={onRefresh} size="small">
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>
      
      {filteredFindings.length === 0 ? (
        <Alert severity="info">
          No findings match your current search and filter criteria.
        </Alert>
      ) : (
        filteredFindings.map((finding, index) => (
          <FindingCard key={index} elevation={1} severity={finding.severity}>
            <Accordion disableGutters elevation={0}>
              <AccordionSummary 
                expandIcon={<ExpandMoreIcon />}
                sx={{ px: 2 }}
              >
                <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Box sx={{ display: 'flex', flexGrow: 1, alignItems: 'center' }}>
                      {finding.severity === 'critical' || finding.severity === 'high' ? (
                        <BugReportIcon sx={{ mr: 1, color: 'error.main' }} fontSize="small" />
                      ) : finding.severity === 'medium' ? (
                        <SecurityIcon sx={{ mr: 1, color: 'warning.main' }} fontSize="small" />
                      ) : (
                        <InfoIcon sx={{ mr: 1, color: 'info.main' }} fontSize="small" />
                      )}
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {finding.title || 'Untitled Finding'}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
                      <SeverityChip 
                        label={finding.severity?.toUpperCase() || 'UNKNOWN'}
                        severity={finding.severity}
                        size="small"
                      />
                      <AdapterChip 
                        label={finding.adapter}
                        size="small"
                      />
                    </Box>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {finding.url && (
                      <Box component="span" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                        <CodeIcon fontSize="inherit" />
                        {formatUrl(finding.url)}
                      </Box>
                    )}
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails sx={{ px: 2, pb: 2 }}>
                <Divider sx={{ mb: 2 }} />
                
                {finding.description && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>Description</Typography>
                    <Typography variant="body2">{finding.description}</Typography>
                  </Box>
                )}
                
                {finding.evidence && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>Evidence</Typography>
                    <CodeBlock>{finding.evidence}</CodeBlock>
                  </Box>
                )}
                
                {finding.request && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>Request</Typography>
                    <CodeBlock>{finding.request}</CodeBlock>
                  </Box>
                )}
                
                {finding.response && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>Response</Typography>
                    <CodeBlock>{finding.response}</CodeBlock>
                  </Box>
                )}
                
                {finding.remediation && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>Remediation</Typography>
                    <Typography variant="body2">{finding.remediation}</Typography>
                  </Box>
                )}
                
                {finding.references && finding.references.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>References</Typography>
                    <Box component="ul" sx={{ pl: 2, mt: 0.5 }}>
                      {finding.references.map((ref, idx) => (
                        <Box component="li" key={idx} sx={{ mb: 0.5 }}>
                          <Typography variant="body2" component="a" href={ref} target="_blank" rel="noopener noreferrer" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            {ref}
                            <OpenInNewIcon fontSize="inherit" />
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                )}
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Finding ID: {finding.finding_id || 'N/A'}
                    </Typography>
                  </Box>
                  <Box>
                    {finding.cve && (
                      <Chip 
                        label={finding.cve}
                        size="small"
                        variant="outlined"
                        color="error"
                        sx={{ mr: 1 }}
                      />
                    )}
                    {finding.cwe && (
                      <Chip 
                        label={`CWE-${finding.cwe}`}
                        size="small"
                        variant="outlined"
                        color="warning"
                      />
                    )}
                  </Box>
                </Box>
              </AccordionDetails>
            </Accordion>
          </FindingCard>
        ))
      )}
    </Box>
  );
};

export default FindingsList;