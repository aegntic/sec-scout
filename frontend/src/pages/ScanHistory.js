import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Button,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  InputAdornment,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  CircularProgress,
  Alert
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DeleteIcon from '@mui/icons-material/Delete';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import CompareIcon from '@mui/icons-material/Compare';
import SearchIcon from '@mui/icons-material/Search';
import RefreshIcon from '@mui/icons-material/Refresh';
import FilterListIcon from '@mui/icons-material/FilterList';
import { useNavigate } from 'react-router-dom';

// Mock data for scan history
const mockScanHistory = [
  {
    id: 'scan123',
    target_url: 'https://example.com',
    target_name: 'Example Main Site',
    start_time: '2025-05-16T09:30:15',
    end_time: '2025-05-16T10:45:22',
    duration: '01:15:07',
    status: 'completed',
    findings_count: {
      critical: 0,
      high: 2,
      medium: 3,
      low: 5,
      info: 8
    },
    scan_profile: 'standard',
    has_report: true
  },
  {
    id: 'scan456',
    target_url: 'https://api.example.com',
    target_name: 'Example API',
    start_time: '2025-05-15T14:22:10',
    end_time: '2025-05-15T15:35:42',
    duration: '01:13:32',
    status: 'completed',
    findings_count: {
      critical: 1,
      high: 3,
      medium: 2,
      low: 4,
      info: 6
    },
    scan_profile: 'aggressive',
    has_report: true
  },
  {
    id: 'scan789',
    target_url: 'https://admin.example.com',
    target_name: 'Example Admin Portal',
    start_time: '2025-05-14T11:05:33',
    end_time: '2025-05-14T13:15:10',
    duration: '02:09:37',
    status: 'completed',
    findings_count: {
      critical: 2,
      high: 5,
      medium: 8,
      low: 3,
      info: 11
    },
    scan_profile: 'aggressive',
    has_report: true
  },
  {
    id: 'scan101',
    target_url: 'https://staging.example.com',
    target_name: 'Example Staging Environment',
    start_time: '2025-05-13T15:45:22',
    end_time: '2025-05-13T16:30:15',
    duration: '00:44:53',
    status: 'completed',
    findings_count: {
      critical: 0,
      high: 0,
      medium: 1,
      low: 2,
      info: 5
    },
    scan_profile: 'passive',
    has_report: true
  },
  {
    id: 'scan112',
    target_url: 'https://beta.example.com',
    target_name: 'Example Beta Site',
    start_time: '2025-05-12T09:10:45',
    end_time: null,
    duration: null,
    status: 'failed',
    findings_count: {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      info: 0
    },
    scan_profile: 'standard',
    has_report: false,
    error_message: 'Connection timeout after 300s'
  }
];

const ScanHistory = () => {
  const navigate = useNavigate();
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [orderBy, setOrderBy] = useState('start_time');
  const [order, setOrder] = useState('desc');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [scanToDelete, setScanToDelete] = useState(null);
  
  // Fetch scan history
  useEffect(() => {
    // Simulate fetching data
    setLoading(true);
    setTimeout(() => {
      setScans(mockScanHistory);
      setLoading(false);
    }, 1000);
  }, []);
  
  // Filter scans based on search term
  const filteredScans = scans.filter(scan => {
    const searchLower = searchTerm.toLowerCase();
    return (
      scan.target_url.toLowerCase().includes(searchLower) ||
      (scan.target_name && scan.target_name.toLowerCase().includes(searchLower)) ||
      scan.id.toLowerCase().includes(searchLower)
    );
  });
  
  // Sort function
  const getSorting = (order, orderBy) => {
    return order === 'desc'
      ? (a, b) => descendingComparator(a, b, orderBy)
      : (a, b) => -descendingComparator(a, b, orderBy);
  };
  
  const descendingComparator = (a, b, orderBy) => {
    // Special handling for nested properties and dates
    if (orderBy === 'findings_count') {
      const totalA = Object.values(a.findings_count).reduce((sum, current) => sum + current, 0);
      const totalB = Object.values(b.findings_count).reduce((sum, current) => sum + current, 0);
      return totalB - totalA;
    } else if (orderBy === 'start_time' || orderBy === 'end_time') {
      // Handle null end_time for incomplete scans
      if (orderBy === 'end_time' && (!a.end_time || !b.end_time)) {
        return !a.end_time ? 1 : -1;
      }
      return new Date(b[orderBy]) - new Date(a[orderBy]);
    }
    
    if (b[orderBy] < a[orderBy]) {
      return -1;
    }
    if (b[orderBy] > a[orderBy]) {
      return 1;
    }
    return 0;
  };
  
  // Sorting handler
  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };
  
  // Create sort handler for a specific column
  const createSortHandler = (property) => () => {
    handleRequestSort(property);
  };
  
  // Pagination handlers
  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  
  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  // Search handler
  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
    setPage(0);
  };
  
  // View scan handler
  const handleViewScan = (scanId) => {
    navigate(`/scan/active/${scanId}`);
  };
  
  // Delete scan dialog handlers
  const handleDeleteClick = (scan) => {
    setScanToDelete(scan);
    setDeleteDialogOpen(true);
  };
  
  const handleDeleteConfirm = () => {
    // In a real app, this would make an API call to delete the scan
    setScans(scans.filter(scan => scan.id !== scanToDelete.id));
    setDeleteDialogOpen(false);
    setScanToDelete(null);
  };
  
  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setScanToDelete(null);
  };
  
  // Calculate total findings
  const getTotalFindings = (findingsCount) => {
    return Object.values(findingsCount).reduce((sum, current) => sum + current, 0);
  };
  
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };
  
  // Status chip color
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'primary';
      case 'failed':
        return 'error';
      case 'stopped':
        return 'warning';
      default:
        return 'default';
    }
  };
  
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading scan history...
        </Typography>
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="xl">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Scan History
        </Typography>
        <Box>
          <Button
            variant="outlined"
            color="primary"
            startIcon={<RefreshIcon />}
            onClick={() => window.location.reload()}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            color="primary"
            startIcon={<FilterListIcon />}
          >
            Filter
          </Button>
        </Box>
      </Box>
      
      <Paper elevation={3} sx={{ mb: 3 }}>
        <Box sx={{ p: 2 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search by URL, name, or scan ID"
            value={searchTerm}
            onChange={handleSearchChange}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Box>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'start_time'}
                    direction={orderBy === 'start_time' ? order : 'asc'}
                    onClick={createSortHandler('start_time')}
                  >
                    Date
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'target_url'}
                    direction={orderBy === 'target_url' ? order : 'asc'}
                    onClick={createSortHandler('target_url')}
                  >
                    Target
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'scan_profile'}
                    direction={orderBy === 'scan_profile' ? order : 'asc'}
                    onClick={createSortHandler('scan_profile')}
                  >
                    Profile
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'duration'}
                    direction={orderBy === 'duration' ? order : 'asc'}
                    onClick={createSortHandler('duration')}
                  >
                    Duration
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'status'}
                    direction={orderBy === 'status' ? order : 'asc'}
                    onClick={createSortHandler('status')}
                  >
                    Status
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={orderBy === 'findings_count'}
                    direction={orderBy === 'findings_count' ? order : 'asc'}
                    onClick={createSortHandler('findings_count')}
                  >
                    Findings
                  </TableSortLabel>
                </TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredScans
                .sort(getSorting(order, orderBy))
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((scan) => (
                  <TableRow key={scan.id} hover>
                    <TableCell>
                      <Typography variant="body2">{formatDate(scan.start_time)}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {scan.target_name || 'Unnamed Scan'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {scan.target_url}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={scan.scan_profile} 
                        size="small"
                        color={
                          scan.scan_profile === 'passive' ? 'info' :
                          scan.scan_profile === 'standard' ? 'primary' :
                          scan.scan_profile === 'aggressive' ? 'warning' :
                          scan.scan_profile === 'stealth' ? 'secondary' :
                          'default'
                        }
                      />
                    </TableCell>
                    <TableCell>
                      {scan.duration || 'N/A'}
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={scan.status} 
                        size="small"
                        color={getStatusColor(scan.status)}
                      />
                      {scan.error_message && (
                        <Tooltip title={scan.error_message}>
                          <Typography variant="caption" color="error" sx={{ display: 'block', mt: 0.5 }}>
                            Error...
                          </Typography>
                        </Tooltip>
                      )}
                    </TableCell>
                    <TableCell>
                      {scan.status === 'completed' ? (
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {scan.findings_count.critical > 0 && (
                            <Tooltip title={`${scan.findings_count.critical} Critical`}>
                              <Box
                                sx={{
                                  width: 16,
                                  height: 16,
                                  backgroundColor: '#e74c3c',
                                  borderRadius: '50%',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  mr: 0.5,
                                  fontSize: '10px',
                                  color: 'white',
                                  fontWeight: 'bold'
                                }}
                              >
                                {scan.findings_count.critical}
                              </Box>
                            </Tooltip>
                          )}
                          {scan.findings_count.high > 0 && (
                            <Tooltip title={`${scan.findings_count.high} High`}>
                              <Box
                                sx={{
                                  width: 16,
                                  height: 16,
                                  backgroundColor: '#e67e22',
                                  borderRadius: '50%',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  mr: 0.5,
                                  fontSize: '10px',
                                  color: 'white',
                                  fontWeight: 'bold'
                                }}
                              >
                                {scan.findings_count.high}
                              </Box>
                            </Tooltip>
                          )}
                          <Typography variant="body2">
                            {getTotalFindings(scan.findings_count)} total
                          </Typography>
                        </Box>
                      ) : (
                        <Typography variant="body2">N/A</Typography>
                      )}
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Scan">
                        <IconButton size="small" onClick={() => handleViewScan(scan.id)}>
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      {scan.has_report && (
                        <Tooltip title="Download Report">
                          <IconButton size="small">
                            <FileDownloadIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                      <Tooltip title="Delete Scan">
                        <IconButton size="small" onClick={() => handleDeleteClick(scan)}>
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              {filteredScans.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    <Typography variant="body1" sx={{ py: 2 }}>
                      No scan history found
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredScans.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
      
      {/* Delete confirmation dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the scan of {scanToDelete?.target_url}? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteConfirm} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ScanHistory;