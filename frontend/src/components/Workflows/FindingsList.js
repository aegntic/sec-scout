import React, { useState, useEffect, useMemo } from 'react';
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
  Card,
  CardContent,
  ToggleButtonGroup,
  ToggleButton,
  Stack,
  LinearProgress,
  CircularProgress,
  ButtonGroup,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Collapse,
  Link,
  Badge,
  useTheme,
  useMediaQuery,
  Fade,
  Grow,
} from '@mui/material';
import { styled, alpha } from '@mui/material/styles';
import SearchIcon from '@mui/icons-material/Search';
import RefreshIcon from '@mui/icons-material/Refresh';
import FilterListIcon from '@mui/icons-material/FilterList';
import TuneIcon from '@mui/icons-material/Tune';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import SecurityIcon from '@mui/icons-material/Security';
import BugReportIcon from '@mui/icons-material/BugReport';
import CodeIcon from '@mui/icons-material/Code';
import InfoIcon from '@mui/icons-material/Info';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import ViewListIcon from '@mui/icons-material/ViewList';
import GridViewIcon from '@mui/icons-material/GridView';
import PieChartIcon from '@mui/icons-material/PieChart';
import BarChartIcon from '@mui/icons-material/BarChart';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import SaveAltIcon from '@mui/icons-material/SaveAlt';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import SortIcon from '@mui/icons-material/Sort';
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted';
import TableChartIcon from '@mui/icons-material/TableChart';
import CalendarViewMonthIcon from '@mui/icons-material/CalendarViewMonth';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';

// Get the severity for colors and ordering
const getSeverityOrder = (severity) => {
  switch (severity?.toLowerCase()) {
    case 'critical': return 1;
    case 'high': return 2;
    case 'medium': return 3;
    case 'low': return 4;
    case 'info': return 5;
    default: return 6;
  }
};

// Get color for severity
const getSeverityColor = (severity, theme) => {
  switch (severity?.toLowerCase()) {
    case 'critical': return theme.palette.error.dark;
    case 'high': return theme.palette.error.main;
    case 'medium': return theme.palette.warning.main;
    case 'low': return theme.palette.info.main;
    case 'info': return theme.palette.grey[500];
    default: return theme.palette.grey[500];
  }
};

// Styled components
const SeverityChip = styled(Chip)(({ theme, severity }) => {
  const color = getSeverityColor(severity, theme);
  
  return {
    backgroundColor: alpha(color, 0.12),
    color: color,
    fontWeight: 600,
    '& .MuiChip-label': {
      padding: '0 8px',
    }
  };
});

const FindingCard = styled(Paper)(({ theme, severity }) => {
  const color = getSeverityColor(severity, theme);
  
  return {
    borderLeft: `4px solid ${color}`,
    marginBottom: theme.spacing(2),
    overflow: 'hidden',
    transition: 'all 0.2s ease',
    '&:hover': {
      boxShadow: theme.shadows[4],
      transform: 'translateY(-2px)',
    }
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
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  maxHeight: '300px',
  overflow: 'auto',
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

const FindingGridCard = styled(Card)(({ theme, severity }) => {
  const color = getSeverityColor(severity, theme);
  
  return {
    position: 'relative',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    transition: 'all 0.2s ease',
    '&::after': {
      content: '""',
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      height: '4px',
      backgroundColor: color,
    },
    '&:hover': {
      transform: 'translateY(-4px)',
      boxShadow: theme.shadows[8],
    }
  };
});

const FilterContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(3),
  backgroundColor: alpha(theme.palette.background.paper, 0.6),
  borderRadius: theme.shape.borderRadius,
  border: `1px solid ${alpha(theme.palette.divider, 0.1)}`,
  backdropFilter: 'blur(8px)',
}));

const ViewOptionsButtonGroup = styled(ButtonGroup)(({ theme }) => ({
  '& .MuiButtonGroup-grouped': {
    border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
    '&:not(:last-of-type)': {
      borderRight: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
    },
  },
}));

const SummaryStatsGrid = styled(Grid)(({ theme }) => ({
  marginBottom: theme.spacing(3),
}));

const StatsCard = styled(Card)(({ theme, color }) => ({
  backgroundColor: alpha(color, 0.05),
  borderRadius: theme.shape.borderRadius,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
}));

const CopySuccessOverlay = styled(Box)(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: alpha(theme.palette.success.main, 0.9),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  zIndex: 10,
  borderRadius: theme.shape.borderRadius,
}));

const SortButton = styled(Button)(({ theme }) => ({
  textTransform: 'none',
  fontWeight: 600,
  '& .MuiButton-endIcon': {
    marginLeft: 4,
  },
}));

const FindingsList = ({ findings = [], workflowId, onRefresh }) => {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));
  
  // State management
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    severity: [],
    adapter: [],
    hasCve: null,
    hasCwe: null,
    hasRemediation: null,
  });
  const [showFilters, setShowFilters] = useState(false);
  const [viewMode, setViewMode] = useState('list'); // list, grid, stats
  const [statsView, setStatsView] = useState('pie'); // pie or bar
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [showFindingDialog, setShowFindingDialog] = useState(false);
  const [copiedText, setCopiedText] = useState(null);
  const [sortBy, setSortBy] = useState('severity');
  const [sortDirection, setSortDirection] = useState('asc'); // asc or desc
  const [bookmarkedFindings, setBookmarkedFindings] = useState([]);
  const [showOnlyBookmarked, setShowOnlyBookmarked] = useState(false);
  
  // Calculate finding stats and groupings
  const findingCounts = useMemo(() => {
    return findings.reduce((acc, finding) => {
      const severity = finding.severity || 'unknown';
      acc[severity] = (acc[severity] || 0) + 1;
      return acc;
    }, {});
  }, [findings]);
  
  // Get unique adapters for filtering
  const adapters = useMemo(() => {
    return [...new Set(findings.map(finding => finding.adapter))];
  }, [findings]);
  
  // Filter findings
  const filteredFindings = useMemo(() => {
    return findings.filter(finding => {
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
      
      // Apply CVE filter
      const cveMatch = filters.hasCve === null || 
        (filters.hasCve === true ? Boolean(finding.cve) : !Boolean(finding.cve));
      
      // Apply CWE filter
      const cweMatch = filters.hasCwe === null || 
        (filters.hasCwe === true ? Boolean(finding.cwe) : !Boolean(finding.cwe));
      
      // Apply remediation filter
      const remediationMatch = filters.hasRemediation === null || 
        (filters.hasRemediation === true ? Boolean(finding.remediation) : !Boolean(finding.remediation));
      
      // Apply bookmark filter
      const bookmarkMatch = !showOnlyBookmarked || 
        bookmarkedFindings.includes(finding.finding_id);
      
      return searchMatch && severityMatch && adapterMatch && cveMatch && cweMatch && remediationMatch && bookmarkMatch;
    });
  }, [findings, searchTerm, filters, bookmarkedFindings, showOnlyBookmarked]);
  
  // Sort findings
  const sortedFindings = useMemo(() => {
    return [...filteredFindings].sort((a, b) => {
      let compareA, compareB;
      
      // Determine which field to sort by
      switch (sortBy) {
        case 'severity':
          compareA = getSeverityOrder(a.severity);
          compareB = getSeverityOrder(b.severity);
          break;
        case 'title':
          compareA = a.title || '';
          compareB = b.title || '';
          break;
        case 'adapter':
          compareA = a.adapter || '';
          compareB = b.adapter || '';
          break;
        default:
          compareA = getSeverityOrder(a.severity);
          compareB = getSeverityOrder(b.severity);
      }
      
      // Apply sort direction
      const result = typeof compareA === 'string' 
        ? compareA.localeCompare(compareB)
        : compareA - compareB;
      
      return sortDirection === 'asc' ? result : -result;
    });
  }, [filteredFindings, sortBy, sortDirection]);
  
  // Prepare chart data
  const chartData = useMemo(() => {
    const severityOrder = ['critical', 'high', 'medium', 'low', 'info', 'unknown'];
    
    // For severity distribution
    const severityData = Object.entries(findingCounts)
      .map(([severity, count]) => ({
        name: severity,
        value: count,
        color: getSeverityColor(severity, theme)
      }))
      .sort((a, b) => {
        const indexA = severityOrder.indexOf(a.name.toLowerCase());
        const indexB = severityOrder.indexOf(b.name.toLowerCase());
        return indexA - indexB;
      });
    
    // For adapter distribution
    const adapterData = adapters.map(adapter => {
      const count = findings.filter(f => f.adapter === adapter).length;
      return { name: adapter, value: count };
    }).sort((a, b) => b.value - a.value);
    
    // For other metrics
    const hasCveCount = findings.filter(f => f.cve).length;
    const hasCweCount = findings.filter(f => f.cwe).length;
    const hasRemediationCount = findings.filter(f => f.remediation).length;
    
    const metricsData = [
      { name: 'With CVE', value: hasCveCount },
      { name: 'With CWE', value: hasCweCount },
      { name: 'With Remediation', value: hasRemediationCount },
    ];
    
    return {
      severityData,
      adapterData,
      metricsData
    };
  }, [findings, findingCounts, adapters, theme]);
  
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
  
  // Handle view mode change
  const handleViewModeChange = (event, newMode) => {
    if (newMode !== null) {
      setViewMode(newMode);
    }
  };
  
  // Handle stats view change
  const handleStatsViewChange = (event, newView) => {
    if (newView !== null) {
      setStatsView(newView);
    }
  };
  
  // Toggle filter panel
  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };
  
  // Handle finding selection for dialog
  const handleFindingClick = (finding) => {
    setSelectedFinding(finding);
    setShowFindingDialog(true);
  };
  
  // Close finding dialog
  const handleCloseDialog = () => {
    setShowFindingDialog(false);
  };
  
  // Handle sort change
  const handleSortChange = (field) => {
    if (sortBy === field) {
      // Toggle direction if clicking the same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to ascending
      setSortBy(field);
      setSortDirection('asc');
    }
  };
  
  // Copy text to clipboard
  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedText(id);
    setTimeout(() => setCopiedText(null), 1500);
  };
  
  // Toggle bookmark for a finding
  const toggleBookmark = (findingId) => {
    if (bookmarkedFindings.includes(findingId)) {
      setBookmarkedFindings(bookmarkedFindings.filter(id => id !== findingId));
    } else {
      setBookmarkedFindings([...bookmarkedFindings, findingId]);
    }
  };
  
  // Toggle showing only bookmarked findings
  const toggleShowOnlyBookmarked = () => {
    setShowOnlyBookmarked(!showOnlyBookmarked);
  };
  
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
  
  // Export findings to JSON
  const exportFindings = () => {
    const findingsJson = JSON.stringify(sortedFindings, null, 2);
    const blob = new Blob([findingsJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `workflow_${workflowId}_findings.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  // Empty state
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
          sx={{ textTransform: 'none', fontWeight: 600 }}
        >
          Refresh Findings
        </Button>
      </Box>
    );
  }
  
  // Render severity icon based on level
  const renderSeverityIcon = (severity, size = 'small') => {
    switch (severity?.toLowerCase()) {
      case 'critical':
      case 'high':
        return <BugReportIcon fontSize={size} sx={{ color: getSeverityColor(severity, theme) }} />;
      case 'medium':
        return <WarningAmberIcon fontSize={size} sx={{ color: getSeverityColor(severity, theme) }} />;
      case 'low':
        return <SecurityIcon fontSize={size} sx={{ color: getSeverityColor(severity, theme) }} />;
      default:
        return <InfoIcon fontSize={size} sx={{ color: getSeverityColor(severity, theme) }} />;
    }
  };
  
  // Main findings display based on selected view
  return (
    <Box sx={{ p: 2 }}>
      {/* Header with summary and actions */}
      <Box sx={{ mb: 3, display: 'flex', flexDirection: { xs: 'column', md: 'row' }, justifyContent: 'space-between', alignItems: { xs: 'flex-start', md: 'center' }, gap: 2 }}>
        <Box>
          <Typography variant="h6" gutterBottom>
            Findings Summary
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {Object.entries(findingCounts).map(([severity, count]) => (
              <SeverityChip 
                key={severity}
                label={`${severity}: ${count}`}
                severity={severity}
                icon={renderSeverityIcon(severity, 'small')}
              />
            ))}
            <Chip 
              label={`Total: ${findings.length}`}
              variant="outlined"
            />
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={handleViewModeChange}
            size="small"
            aria-label="view mode"
          >
            <ToggleButton value="list" aria-label="list view">
              <Tooltip title="List View">
                <ViewListIcon fontSize="small" />
              </Tooltip>
            </ToggleButton>
            <ToggleButton value="grid" aria-label="grid view">
              <Tooltip title="Grid View">
                <GridViewIcon fontSize="small" />
              </Tooltip>
            </ToggleButton>
            <ToggleButton value="stats" aria-label="statistics view">
              <Tooltip title="Statistics View">
                <BarChartIcon fontSize="small" />
              </Tooltip>
            </ToggleButton>
          </ToggleButtonGroup>
          
          <Button 
            variant="outlined"
            size="small"
            startIcon={<SaveAltIcon />}
            onClick={exportFindings}
            sx={{ textTransform: 'none', fontWeight: 600 }}
          >
            Export
          </Button>
          
          <Tooltip title="Refresh findings">
            <IconButton onClick={onRefresh} size="small" color="primary">
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      
      {/* Search and filters */}
      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={8}>
            <TextField
              fullWidth
              placeholder="Search findings by title, description, or other content..."
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
          
          <Grid item xs={6} md={2}>
            <Button
              fullWidth
              variant={showFilters ? "contained" : "outlined"}
              startIcon={<FilterListIcon />}
              onClick={toggleFilters}
              size="medium"
              sx={{ textTransform: 'none', fontWeight: 600 }}
            >
              Filters {filters.severity.length > 0 || filters.adapter.length > 0 ? `(${filters.severity.length + filters.adapter.length})` : ''}
            </Button>
          </Grid>
          
          <Grid item xs={6} md={2}>
            <Button
              fullWidth
              variant={showOnlyBookmarked ? "contained" : "outlined"}
              color={showOnlyBookmarked ? "primary" : "inherit"}
              startIcon={showOnlyBookmarked ? <BookmarkIcon /> : <BookmarkBorderIcon />}
              onClick={toggleShowOnlyBookmarked}
              size="medium"
              sx={{ textTransform: 'none', fontWeight: 600 }}
            >
              Bookmarked {bookmarkedFindings.length > 0 ? `(${bookmarkedFindings.length})` : ''}
            </Button>
          </Grid>
        </Grid>
      </Box>
      
      {/* Extended filter panel */}
      <Collapse in={showFilters}>
        <FilterContainer>
          <Typography variant="subtitle2" gutterBottom>
            Advanced Filters
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
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
                        <SeverityChip 
                          key={value} 
                          label={value} 
                          severity={value} 
                          size="small"
                        />
                      ))}
                    </Box>
                  )}
                >
                  {['critical', 'high', 'medium', 'low', 'info'].map((severity) => (
                    <MenuItem key={severity} value={severity}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {renderSeverityIcon(severity)}
                        <Typography>{severity}</Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Tool Type</InputLabel>
                <Select
                  multiple
                  value={filters.adapter}
                  onChange={(e) => handleFilterChange('adapter', e.target.value)}
                  label="Tool Type"
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
            
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', gap: 1, height: '100%' }}>
                <Button
                  variant={filters.hasCve === true ? "contained" : "outlined"}
                  color={filters.hasCve === true ? "error" : "inherit"}
                  size="small"
                  onClick={() => handleFilterChange('hasCve', filters.hasCve === true ? null : true)}
                  sx={{ flex: 1, textTransform: 'none' }}
                >
                  Has CVE
                </Button>
                
                <Button
                  variant={filters.hasCwe === true ? "contained" : "outlined"}
                  color={filters.hasCwe === true ? "warning" : "inherit"}
                  size="small"
                  onClick={() => handleFilterChange('hasCwe', filters.hasCwe === true ? null : true)}
                  sx={{ flex: 1, textTransform: 'none' }}
                >
                  Has CWE
                </Button>
                
                <Button
                  variant={filters.hasRemediation === true ? "contained" : "outlined"}
                  color={filters.hasRemediation === true ? "success" : "inherit"}
                  size="small"
                  onClick={() => handleFilterChange('hasRemediation', filters.hasRemediation === true ? null : true)}
                  sx={{ flex: 1, textTransform: 'none' }}
                >
                  Has Remediation
                </Button>
              </Box>
            </Grid>
          </Grid>
        </FilterContainer>
      </Collapse>
      
      {/* Sorting controls */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="subtitle1">
          {sortedFindings.length} {sortedFindings.length === 1 ? 'finding' : 'findings'} found
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <SortButton
            size="small"
            variant={sortBy === 'severity' ? "contained" : "outlined"}
            color={sortBy === 'severity' ? "primary" : "inherit"}
            onClick={() => handleSortChange('severity')}
            endIcon={sortBy === 'severity' && (sortDirection === 'asc' ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />)}
          >
            Severity
          </SortButton>
          
          <SortButton
            size="small"
            variant={sortBy === 'title' ? "contained" : "outlined"}
            color={sortBy === 'title' ? "primary" : "inherit"}
            onClick={() => handleSortChange('title')}
            endIcon={sortBy === 'title' && (sortDirection === 'asc' ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />)}
          >
            Title
          </SortButton>
          
          <SortButton
            size="small"
            variant={sortBy === 'adapter' ? "contained" : "outlined"}
            color={sortBy === 'adapter' ? "primary" : "inherit"}
            onClick={() => handleSortChange('adapter')}
            endIcon={sortBy === 'adapter' && (sortDirection === 'asc' ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />)}
          >
            Tool
          </SortButton>
        </Box>
      </Box>
      
      {/* Statistics View */}
      {viewMode === 'stats' && (
        <Box sx={{ mb: 3 }}>
          <Paper elevation={0} sx={{ p: 3, mb: 3 }}>
            <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">Finding Statistics</Typography>
              
              <ToggleButtonGroup
                value={statsView}
                exclusive
                onChange={handleStatsViewChange}
                size="small"
              >
                <ToggleButton value="pie">
                  <PieChartIcon fontSize="small" />
                </ToggleButton>
                <ToggleButton value="bar">
                  <BarChartIcon fontSize="small" />
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>
            
            <SummaryStatsGrid container spacing={3}>
              <Grid item xs={12} md={6}>
                <StatsCard color={theme.palette.primary.main}>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>Severity Distribution</Typography>
                    <Box sx={{ height: 300 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        {statsView === 'pie' ? (
                          <PieChart>
                            <Pie
                              data={chartData.severityData}
                              cx="50%"
                              cy="50%"
                              innerRadius={60}
                              outerRadius={100}
                              paddingAngle={2}
                              dataKey="value"
                              nameKey="name"
                              label={({name, value, percent}) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                              labelLine={false}
                            >
                              {chartData.severityData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                              ))}
                            </Pie>
                            <Legend />
                            <RechartsTooltip formatter={(value, name) => [`${value} findings`, name]} />
                          </PieChart>
                        ) : (
                          <BarChart data={chartData.severityData} layout="vertical">
                            <XAxis type="number" />
                            <YAxis dataKey="name" type="category" />
                            <RechartsTooltip formatter={(value) => [`${value} findings`]} />
                            <Bar dataKey="value" nameKey="name">
                              {chartData.severityData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                              ))}
                            </Bar>
                          </BarChart>
                        )}
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </StatsCard>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <StatsCard color={theme.palette.secondary.main}>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>Tool Distribution</Typography>
                    <Box sx={{ height: 300 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        {statsView === 'pie' ? (
                          <PieChart>
                            <Pie
                              data={chartData.adapterData}
                              cx="50%"
                              cy="50%"
                              innerRadius={60}
                              outerRadius={100}
                              paddingAngle={2}
                              dataKey="value"
                              nameKey="name"
                              label={({name, value, percent}) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                              labelLine={false}
                            >
                              {chartData.adapterData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={theme.palette.primary.main} opacity={(1 - (index * 0.1))} />
                              ))}
                            </Pie>
                            <Legend />
                            <RechartsTooltip formatter={(value, name) => [`${value} findings`, name]} />
                          </PieChart>
                        ) : (
                          <BarChart data={chartData.adapterData} layout="vertical">
                            <XAxis type="number" />
                            <YAxis dataKey="name" type="category" width={120} />
                            <RechartsTooltip formatter={(value) => [`${value} findings`]} />
                            <Bar dataKey="value" nameKey="name" fill={theme.palette.primary.main} />
                          </BarChart>
                        )}
                      </ResponsiveContainer>
                    </Box>
                  </CardContent>
                </StatsCard>
              </Grid>
            </SummaryStatsGrid>
            
            <Grid container spacing={3}>
              {Object.entries(findingCounts).map(([severity, count], index) => (
                <Grid item xs={6} sm={4} md={2} key={severity}>
                  <StatsCard color={getSeverityColor(severity, theme)}>
                    <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 2 }}>
                      {renderSeverityIcon(severity, 'large')}
                      <Typography variant="h4" sx={{ mt: 1, fontWeight: 600 }}>
                        {count}
                      </Typography>
                      <Typography variant="subtitle2" sx={{ textTransform: 'uppercase' }}>
                        {severity}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {((count / findings.length) * 100).toFixed(1)}% of total
                      </Typography>
                    </CardContent>
                  </StatsCard>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Box>
      )}
      
      {/* List View */}
      {viewMode === 'list' && sortedFindings.length === 0 && (
        <Alert severity="info">
          No findings match your current search and filter criteria.
        </Alert>
      )}
      
      {viewMode === 'list' && sortedFindings.length > 0 && (
        <Box>
          {sortedFindings.map((finding, index) => (
            <Grow
              key={finding.finding_id || index}
              in={true}
              style={{ transformOrigin: '0 0 0' }}
              timeout={100 + (index * 50)}
            >
              <FindingCard elevation={1} severity={finding.severity}>
                <Accordion disableGutters elevation={0}>
                  <AccordionSummary 
                    expandIcon={<ExpandMoreIcon />}
                    sx={{ px: 2 }}
                  >
                    <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, width: '100%', flexWrap: { xs: 'wrap', md: 'nowrap' }, gap: { xs: 1, md: 0 } }}>
                        <Box sx={{ display: 'flex', flexGrow: 1, alignItems: 'center', minWidth: 0 }}>
                          {renderSeverityIcon(finding.severity)}
                          <Typography 
                            variant="subtitle1" 
                            sx={{ 
                              fontWeight: 600, 
                              ml: 1,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {finding.title || 'Untitled Finding'}
                          </Typography>
                          <IconButton 
                            size="small" 
                            sx={{ ml: 1 }}
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleBookmark(finding.finding_id);
                            }}
                          >
                            {bookmarkedFindings.includes(finding.finding_id) ? 
                              <BookmarkIcon fontSize="small" color="primary" /> : 
                              <BookmarkBorderIcon fontSize="small" />
                            }
                          </IconButton>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: { xs: 0, md: 2 } }}>
                          <SeverityChip 
                            label={finding.severity?.toUpperCase() || 'UNKNOWN'}
                            severity={finding.severity}
                            size="small"
                          />
                          <AdapterChip 
                            label={finding.adapter}
                            size="small"
                          />
                          {finding.cve && (
                            <Chip 
                              label={finding.cve}
                              size="small"
                              variant="outlined"
                              color="error"
                            />
                          )}
                        </Box>
                      </Box>
                      
                      <Typography 
                        variant="body2" 
                        color="text.secondary" 
                        sx={{ 
                          mb: 1,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                        }}
                      >
                        {finding.description || 'No description available.'}
                      </Typography>
                      
                      {finding.url && (
                        <Box component="span" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                          <CodeIcon fontSize="inherit" />
                          <Typography variant="caption" sx={{ fontFamily: 'monospace' }}>
                            {formatUrl(finding.url)}
                          </Typography>
                        </Box>
                      )}
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
                      <Box sx={{ mb: 2, position: 'relative' }}>
                        <Typography variant="subtitle2" gutterBottom>Evidence</Typography>
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 0.5 }}>
                          <Button
                            size="small"
                            startIcon={<ContentCopyIcon fontSize="small" />}
                            onClick={() => copyToClipboard(finding.evidence, 'evidence')}
                            sx={{ textTransform: 'none', py: 0 }}
                          >
                            Copy
                          </Button>
                        </Box>
                        <CodeBlock>
                          {finding.evidence}
                          {copiedText === 'evidence' && (
                            <CopySuccessOverlay>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <CheckCircleIcon color="inherit" />
                                <Typography variant="body2" color="inherit">Copied!</Typography>
                              </Box>
                            </CopySuccessOverlay>
                          )}
                        </CodeBlock>
                      </Box>
                    )}
                    
                    <Grid container spacing={2}>
                      {finding.request && (
                        <Grid item xs={12} md={6}>
                          <Box sx={{ mb: 2, position: 'relative' }}>
                            <Typography variant="subtitle2" gutterBottom>Request</Typography>
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 0.5 }}>
                              <Button
                                size="small"
                                startIcon={<ContentCopyIcon fontSize="small" />}
                                onClick={() => copyToClipboard(finding.request, 'request')}
                                sx={{ textTransform: 'none', py: 0 }}
                              >
                                Copy
                              </Button>
                            </Box>
                            <CodeBlock>
                              {finding.request}
                              {copiedText === 'request' && (
                                <CopySuccessOverlay>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <CheckCircleIcon color="inherit" />
                                    <Typography variant="body2" color="inherit">Copied!</Typography>
                                  </Box>
                                </CopySuccessOverlay>
                              )}
                            </CodeBlock>
                          </Box>
                        </Grid>
                      )}
                      
                      {finding.response && (
                        <Grid item xs={12} md={6}>
                          <Box sx={{ mb: 2, position: 'relative' }}>
                            <Typography variant="subtitle2" gutterBottom>Response</Typography>
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 0.5 }}>
                              <Button
                                size="small"
                                startIcon={<ContentCopyIcon fontSize="small" />}
                                onClick={() => copyToClipboard(finding.response, 'response')}
                                sx={{ textTransform: 'none', py: 0 }}
                              >
                                Copy
                              </Button>
                            </Box>
                            <CodeBlock>
                              {finding.response}
                              {copiedText === 'response' && (
                                <CopySuccessOverlay>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <CheckCircleIcon color="inherit" />
                                    <Typography variant="body2" color="inherit">Copied!</Typography>
                                  </Box>
                                </CopySuccessOverlay>
                              )}
                            </CodeBlock>
                          </Box>
                        </Grid>
                      )}
                    </Grid>
                    
                    {finding.remediation && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>Remediation</Typography>
                        <Paper 
                          variant="outlined" 
                          sx={{ 
                            p: 2, 
                            backgroundColor: alpha(theme.palette.success.main, 0.05),
                            borderColor: alpha(theme.palette.success.main, 0.2),
                          }}
                        >
                          <Typography variant="body2">{finding.remediation}</Typography>
                        </Paper>
                      </Box>
                    )}
                    
                    {finding.references && finding.references.length > 0 && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>References</Typography>
                        <Box component="ul" sx={{ pl: 2, mt: 0.5 }}>
                          {finding.references.map((ref, idx) => (
                            <Box component="li" key={idx} sx={{ mb: 0.5 }}>
                              <Link href={ref} target="_blank" rel="noopener noreferrer" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                                  {ref}
                                </Typography>
                                <OpenInNewIcon fontSize="inherit" />
                              </Link>
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
            </Grow>
          ))}
        </Box>
      )}
      
      {/* Grid View */}
      {viewMode === 'grid' && sortedFindings.length === 0 && (
        <Alert severity="info">
          No findings match your current search and filter criteria.
        </Alert>
      )}
      
      {viewMode === 'grid' && sortedFindings.length > 0 && (
        <Grid container spacing={3}>
          {sortedFindings.map((finding, index) => (
            <Grid item xs={12} sm={6} md={4} key={finding.finding_id || index}>
              <Grow
                in={true}
                style={{ transformOrigin: '0 0 0' }}
                timeout={100 + (index * 50)}
              >
                <FindingGridCard elevation={2} severity={finding.severity} onClick={() => handleFindingClick(finding)}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 600, width: 'calc(100% - 80px)' }} noWrap>
                        {finding.title || 'Untitled Finding'}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <SeverityChip 
                          label={finding.severity?.toUpperCase() || 'UNKNOWN'}
                          severity={finding.severity}
                          size="small"
                        />
                        <IconButton 
                          size="small" 
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleBookmark(finding.finding_id);
                          }}
                        >
                          {bookmarkedFindings.includes(finding.finding_id) ? 
                            <BookmarkIcon fontSize="small" color="primary" /> : 
                            <BookmarkBorderIcon fontSize="small" />
                          }
                        </IconButton>
                      </Box>
                    </Box>
                    
                    <Typography 
                      variant="body2" 
                      color="text.secondary" 
                      sx={{ 
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                        mb: 2,
                        height: 60,
                      }}
                    >
                      {finding.description || 'No description available.'}
                    </Typography>
                    
                    <Divider sx={{ my: 1 }} />
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                      <AdapterChip 
                        label={finding.adapter}
                        size="small"
                      />
                      
                      <Box>
                        {finding.cve && (
                          <Tooltip title="Has CVE">
                            <Chip 
                              icon={<ErrorOutlineIcon />}
                              size="small"
                              variant="outlined"
                              color="error"
                              sx={{ mr: 0.5 }}
                            />
                          </Tooltip>
                        )}
                        {finding.cwe && (
                          <Tooltip title="Has CWE">
                            <Chip 
                              icon={<WarningAmberIcon />}
                              size="small"
                              variant="outlined"
                              color="warning"
                              sx={{ mr: 0.5 }}
                            />
                          </Tooltip>
                        )}
                        {finding.remediation && (
                          <Tooltip title="Has remediation">
                            <Chip 
                              icon={<CheckCircleIcon />}
                              size="small"
                              variant="outlined"
                              color="success"
                            />
                          </Tooltip>
                        )}
                      </Box>
                    </Box>
                  </CardContent>
                </FindingGridCard>
              </Grow>
            </Grid>
          ))}
        </Grid>
      )}
      
      {/* Detailed finding dialog */}
      <Dialog
        open={showFindingDialog}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 2 }
        }}
      >
        {selectedFinding && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {renderSeverityIcon(selectedFinding.severity)}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    {selectedFinding.title || 'Untitled Finding'}
                  </Typography>
                </Box>
                <Box>
                  <SeverityChip 
                    label={selectedFinding.severity?.toUpperCase() || 'UNKNOWN'}
                    severity={selectedFinding.severity}
                    size="small"
                  />
                </Box>
              </Box>
            </DialogTitle>
            
            <DialogContent dividers>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>Description</Typography>
                    <Typography variant="body1">
                      {selectedFinding.description || 'No description available.'}
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" gutterBottom>Details</Typography>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Stack spacing={1.5}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Typography variant="subtitle2" color="text.secondary">Tool</Typography>
                        <AdapterChip label={selectedFinding.adapter} />
                      </Box>
                      
                      {selectedFinding.cve && (
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <Typography variant="subtitle2" color="text.secondary">CVE</Typography>
                          <Chip 
                            label={selectedFinding.cve}
                            size="small"
                            variant="outlined"
                            color="error"
                          />
                        </Box>
                      )}
                      
                      {selectedFinding.cwe && (
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <Typography variant="subtitle2" color="text.secondary">CWE</Typography>
                          <Chip 
                            label={`CWE-${selectedFinding.cwe}`}
                            size="small"
                            variant="outlined"
                            color="warning"
                          />
                        </Box>
                      )}
                      
                      {selectedFinding.url && (
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                          <Typography variant="subtitle2" color="text.secondary">URL</Typography>
                          <Link href={selectedFinding.url} target="_blank" rel="noopener noreferrer">
                            <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                              {selectedFinding.url}
                            </Typography>
                          </Link>
                        </Box>
                      )}
                      
                      {selectedFinding.finding_id && (
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                          <Typography variant="subtitle2" color="text.secondary">Finding ID</Typography>
                          <Typography variant="body2" fontFamily="monospace">
                            {selectedFinding.finding_id}
                          </Typography>
                        </Box>
                      )}
                    </Stack>
                  </Paper>
                  
                  {selectedFinding.references && selectedFinding.references.length > 0 && (
                    <Box sx={{ mt: 3 }}>
                      <Typography variant="subtitle1" gutterBottom>References</Typography>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Box component="ul" sx={{ pl: 2, m: 0 }}>
                          {selectedFinding.references.map((ref, idx) => (
                            <Box component="li" key={idx} sx={{ mb: 1 }}>
                              <Link href={ref} target="_blank" rel="noopener noreferrer" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                                  {ref}
                                </Typography>
                                <OpenInNewIcon fontSize="inherit" />
                              </Link>
                            </Box>
                          ))}
                        </Box>
                      </Paper>
                    </Box>
                  )}
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  {selectedFinding.remediation && (
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="subtitle1" gutterBottom>Remediation</Typography>
                      <Paper 
                        variant="outlined" 
                        sx={{ 
                          p: 2, 
                          backgroundColor: alpha(theme.palette.success.main, 0.05),
                          borderColor: alpha(theme.palette.success.main, 0.2),
                        }}
                      >
                        <Typography variant="body1">{selectedFinding.remediation}</Typography>
                      </Paper>
                    </Box>
                  )}
                  
                  {selectedFinding.evidence && (
                    <Box sx={{ mb: 3, position: 'relative' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="subtitle1">Evidence</Typography>
                        <Button
                          size="small"
                          startIcon={<ContentCopyIcon fontSize="small" />}
                          onClick={() => copyToClipboard(selectedFinding.evidence, 'evidence-dialog')}
                          sx={{ textTransform: 'none' }}
                        >
                          Copy
                        </Button>
                      </Box>
                      <CodeBlock>
                        {selectedFinding.evidence}
                        {copiedText === 'evidence-dialog' && (
                          <CopySuccessOverlay>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <CheckCircleIcon color="inherit" />
                              <Typography variant="body2" color="inherit">Copied!</Typography>
                            </Box>
                          </CopySuccessOverlay>
                        )}
                      </CodeBlock>
                    </Box>
                  )}
                </Grid>
                
                {(selectedFinding.request || selectedFinding.response) && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle1" gutterBottom>HTTP Traffic</Typography>
                    <Tabs value={0} sx={{ mb: 2 }}>
                      <Tab label="Request/Response" />
                    </Tabs>
                    
                    <Grid container spacing={2}>
                      {selectedFinding.request && (
                        <Grid item xs={12} md={6}>
                          <Box sx={{ position: 'relative' }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                              <Typography variant="subtitle2">Request</Typography>
                              <Button
                                size="small"
                                startIcon={<ContentCopyIcon fontSize="small" />}
                                onClick={() => copyToClipboard(selectedFinding.request, 'request-dialog')}
                                sx={{ textTransform: 'none' }}
                              >
                                Copy
                              </Button>
                            </Box>
                            <CodeBlock>
                              {selectedFinding.request}
                              {copiedText === 'request-dialog' && (
                                <CopySuccessOverlay>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <CheckCircleIcon color="inherit" />
                                    <Typography variant="body2" color="inherit">Copied!</Typography>
                                  </Box>
                                </CopySuccessOverlay>
                              )}
                            </CodeBlock>
                          </Box>
                        </Grid>
                      )}
                      
                      {selectedFinding.response && (
                        <Grid item xs={12} md={6}>
                          <Box sx={{ position: 'relative' }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                              <Typography variant="subtitle2">Response</Typography>
                              <Button
                                size="small"
                                startIcon={<ContentCopyIcon fontSize="small" />}
                                onClick={() => copyToClipboard(selectedFinding.response, 'response-dialog')}
                                sx={{ textTransform: 'none' }}
                              >
                                Copy
                              </Button>
                            </Box>
                            <CodeBlock>
                              {selectedFinding.response}
                              {copiedText === 'response-dialog' && (
                                <CopySuccessOverlay>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <CheckCircleIcon color="inherit" />
                                    <Typography variant="body2" color="inherit">Copied!</Typography>
                                  </Box>
                                </CopySuccessOverlay>
                              )}
                            </CodeBlock>
                          </Box>
                        </Grid>
                      )}
                    </Grid>
                  </Grid>
                )}
              </Grid>
            </DialogContent>
            
            <DialogActions>
              <Button 
                variant="text" 
                onClick={() => toggleBookmark(selectedFinding.finding_id)}
                startIcon={bookmarkedFindings.includes(selectedFinding.finding_id) ? 
                  <BookmarkIcon /> : <BookmarkBorderIcon />
                }
                color={bookmarkedFindings.includes(selectedFinding.finding_id) ? "primary" : "inherit"}
                sx={{ mr: 'auto', textTransform: 'none', fontWeight: 600 }}
              >
                {bookmarkedFindings.includes(selectedFinding.finding_id) ? 'Bookmarked' : 'Bookmark'}
              </Button>
              
              <Button 
                variant="contained" 
                onClick={handleCloseDialog}
                sx={{ textTransform: 'none', fontWeight: 600 }}
              >
                Close
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default FindingsList;