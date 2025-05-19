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
  Alert,
  Tabs,
  Tab,
  Card,
  CardContent,
  CardActions,
  Grid,
  Chip,
  Menu,
  MenuItem,
  Divider
} from '@mui/material';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import VisibilityIcon from '@mui/icons-material/Visibility';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import RefreshIcon from '@mui/icons-material/Refresh';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import CompareIcon from '@mui/icons-material/Compare';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import ShareIcon from '@mui/icons-material/Share';
import CodeIcon from '@mui/icons-material/Code';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import { useNavigate } from 'react-router-dom';

// Mock data for reports
const mockReports = [
  {
    id: 'report123',
    name: 'Example.com Security Assessment',
    scan_id: 'scan123',
    target_url: 'https://example.com',
    generated_at: '2025-05-17T15:30:22',
    format: 'JSON',
    size: '1.2 MB',
    findings_summary: {
      critical: 0,
      high: 2,
      medium: 3,
      low: 5,
      info: 8
    }
  },
  {
    id: 'report456',
    name: 'API Security Analysis',
    scan_id: 'scan456',
    target_url: 'https://api.example.com',
    generated_at: '2025-05-16T11:45:33',
    format: 'PDF',
    size: '3.5 MB',
    findings_summary: {
      critical: 1,
      high: 3,
      medium: 2,
      low: 4,
      info: 6
    }
  },
  {
    id: 'report789',
    name: 'Admin Portal Security Review',
    scan_id: 'scan789',
    target_url: 'https://admin.example.com',
    generated_at: '2025-05-15T09:15:10',
    format: 'HTML',
    size: '2.8 MB',
    findings_summary: {
      critical: 2,
      high: 5,
      medium: 8,
      low: 3,
      info: 11
    }
  },
  {
    id: 'report101',
    name: 'Staging Environment Analysis',
    scan_id: 'scan101',
    target_url: 'https://staging.example.com',
    generated_at: '2025-05-14T16:30:15',
    format: 'JSON',
    size: '0.9 MB',
    findings_summary: {
      critical: 0,
      high: 0,
      medium: 1,
      low: 2,
      info: 5
    }
  }
];

// Tab index interface
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`report-tabpanel-${index}`}
      aria-labelledby={`report-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ pt: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

// Tab props
function tabProps(index) {
  return {
    id: `report-tab-${index}`,
    'aria-controls': `report-tabpanel-${index}`,
  };
}

const Reports = () => {
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [orderBy, setOrderBy] = useState('generated_at');
  const [order, setOrder] = useState('desc');
  const [selectedReport, setSelectedReport] = useState(null);
  const [viewReportDialog, setViewReportDialog] = useState(false);
  const [deleteReportDialog, setDeleteReportDialog] = useState(false);
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [activeReportMenu, setActiveReportMenu] = useState(null);
  
  // Fetch reports
  useEffect(() => {
    // Simulate fetching data
    setLoading(true);
    setTimeout(() => {
      setReports(mockReports);
      setLoading(false);
    }, 1000);
  }, []);
  
  // Filter reports based on search term
  const filteredReports = reports.filter(report => {
    const searchLower = searchTerm.toLowerCase();
    return (
      report.name.toLowerCase().includes(searchLower) ||
      report.target_url.toLowerCase().includes(searchLower) ||
      report.id.toLowerCase().includes(searchLower)
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
    if (orderBy === 'findings_summary') {
      const totalA = Object.values(a.findings_summary).reduce((sum, current) => sum + current, 0);
      const totalB = Object.values(b.findings_summary).reduce((sum, current) => sum + current, 0);
      return totalB - totalA;
    } else if (orderBy === 'generated_at') {
      return new Date(b[orderBy]) - new Date(a[orderBy]);
    } else if (orderBy === 'size') {
      return parseFloat(b.size) - parseFloat(a.size);
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
  
  // Tab change handler
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
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
  
  // Menu handlers
  const handleMenuOpen = (event, report) => {
    setMenuAnchorEl(event.currentTarget);
    setActiveReportMenu(report.id);
  };
  
  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setActiveReportMenu(null);
  };
  
  // Report action handlers
  const handleViewReport = (report) => {
    setSelectedReport(report);
    setViewReportDialog(true);
    handleMenuClose();
  };
  
  const handleDeleteReportClick = (report) => {
    setSelectedReport(report);
    setDeleteReportDialog(true);
    handleMenuClose();
  };
  
  const handleDeleteConfirm = () => {
    // In a real app, this would make an API call to delete the report
    setReports(reports.filter(report => report.id !== selectedReport.id));
    setDeleteReportDialog(false);
    setSelectedReport(null);
  };
  
  const handleCloseViewDialog = () => {
    setViewReportDialog(false);
    setSelectedReport(null);
  };
  
  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };
  
  // Calculate total findings
  const getTotalFindings = (findingsSummary) => {
    return Object.values(findingsSummary).reduce((sum, current) => sum + current, 0);
  };
  
  // Format icon for report type
  const getFormatIcon = (format) => {
    switch (format.toLowerCase()) {
      case 'pdf':
        return <PictureAsPdfIcon />;
      case 'html':
        return <CodeIcon />;
      case 'json':
        return <InsertDriveFileIcon />;
      default:
        return <InsertDriveFileIcon />;
    }
  };
  
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ mt: 2 }}>
          Loading reports...
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
          Security Reports
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
            variant="contained"
            color="primary"
            startIcon={<CompareIcon />}
          >
            Compare Reports
          </Button>
        </Box>
      </Box>
      
      <Paper elevation={3} sx={{ mb: 3 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="report view tabs"
          >
            <Tab label="Table View" {...tabProps(0)} />
            <Tab label="Grid View" {...tabProps(1)} />
          </Tabs>
        </Box>
        
        <Box sx={{ p: 2 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search by name, URL, or report ID"
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
        
        <TabPanel value={tabValue} index={0}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'generated_at'}
                      direction={orderBy === 'generated_at' ? order : 'asc'}
                      onClick={createSortHandler('generated_at')}
                    >
                      Date
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'name'}
                      direction={orderBy === 'name' ? order : 'asc'}
                      onClick={createSortHandler('name')}
                    >
                      Report Name
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
                      active={orderBy === 'format'}
                      direction={orderBy === 'format' ? order : 'asc'}
                      onClick={createSortHandler('format')}
                    >
                      Format
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'size'}
                      direction={orderBy === 'size' ? order : 'asc'}
                      onClick={createSortHandler('size')}
                    >
                      Size
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'findings_summary'}
                      direction={orderBy === 'findings_summary' ? order : 'asc'}
                      onClick={createSortHandler('findings_summary')}
                    >
                      Findings
                    </TableSortLabel>
                  </TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredReports
                  .sort(getSorting(order, orderBy))
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((report) => (
                    <TableRow key={report.id} hover>
                      <TableCell>
                        <Typography variant="body2">{formatDate(report.generated_at)}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {report.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {report.target_url}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          icon={getFormatIcon(report.format)}
                          label={report.format} 
                          size="small"
                          color={
                            report.format === 'PDF' ? 'error' :
                            report.format === 'HTML' ? 'info' :
                            report.format === 'JSON' ? 'success' :
                            'default'
                          }
                        />
                      </TableCell>
                      <TableCell>
                        {report.size}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {report.findings_summary.critical > 0 && (
                            <Tooltip title={`${report.findings_summary.critical} Critical`}>
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
                                {report.findings_summary.critical}
                              </Box>
                            </Tooltip>
                          )}
                          {report.findings_summary.high > 0 && (
                            <Tooltip title={`${report.findings_summary.high} High`}>
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
                                {report.findings_summary.high}
                              </Box>
                            </Tooltip>
                          )}
                          <Typography variant="body2">
                            {getTotalFindings(report.findings_summary)} total
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View Report">
                          <IconButton size="small" onClick={() => handleViewReport(report)}>
                            <VisibilityIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Download Report">
                          <IconButton size="small">
                            <FileDownloadIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="More Options">
                          <IconButton 
                            size="small" 
                            onClick={(event) => handleMenuOpen(event, report)}
                            aria-controls={activeReportMenu === report.id ? 'report-menu' : undefined}
                            aria-haspopup="true"
                          >
                            <MoreVertIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                {filteredReports.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography variant="body1" sx={{ py: 2 }}>
                        No reports found
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
            count={filteredReports.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            {filteredReports
              .sort(getSorting(order, orderBy))
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((report) => (
                <Grid item xs={12} sm={6} md={4} key={report.id}>
                  <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <Typography variant="h6" component="div">
                          {report.name}
                        </Typography>
                        <Chip 
                          label={report.format} 
                          size="small"
                          color={
                            report.format === 'PDF' ? 'error' :
                            report.format === 'HTML' ? 'info' :
                            report.format === 'JSON' ? 'success' :
                            'default'
                          }
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                        {report.target_url}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Generated: {formatDate(report.generated_at)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Size: {report.size}
                      </Typography>
                      
                      <Divider sx={{ my: 2 }} />
                      
                      <Typography variant="subtitle2" gutterBottom>
                        Findings Summary
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                        {report.findings_summary.critical > 0 && (
                          <Chip 
                            label={`${report.findings_summary.critical} Critical`} 
                            size="small"
                            sx={{ backgroundColor: '#e74c3c', color: 'white' }}
                          />
                        )}
                        {report.findings_summary.high > 0 && (
                          <Chip 
                            label={`${report.findings_summary.high} High`} 
                            size="small"
                            sx={{ backgroundColor: '#e67e22', color: 'white' }}
                          />
                        )}
                        {report.findings_summary.medium > 0 && (
                          <Chip 
                            label={`${report.findings_summary.medium} Medium`} 
                            size="small"
                            sx={{ backgroundColor: '#f39c12', color: 'white' }}
                          />
                        )}
                      </Box>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {report.findings_summary.low > 0 && (
                          <Chip 
                            label={`${report.findings_summary.low} Low`} 
                            size="small"
                            sx={{ backgroundColor: '#3498db', color: 'white' }}
                          />
                        )}
                        {report.findings_summary.info > 0 && (
                          <Chip 
                            label={`${report.findings_summary.info} Info`} 
                            size="small"
                            sx={{ backgroundColor: '#95a5a6', color: 'white' }}
                          />
                        )}
                      </Box>
                    </CardContent>
                    <CardActions>
                      <Button 
                        startIcon={<VisibilityIcon />} 
                        size="small"
                        onClick={() => handleViewReport(report)}
                      >
                        View
                      </Button>
                      <Button 
                        startIcon={<FileDownloadIcon />} 
                        size="small"
                      >
                        Download
                      </Button>
                      <IconButton 
                        size="small" 
                        onClick={(event) => handleMenuOpen(event, report)}
                        aria-controls={activeReportMenu === report.id ? 'report-menu' : undefined}
                        aria-haspopup="true"
                        sx={{ ml: 'auto' }}
                      >
                        <MoreVertIcon fontSize="small" />
                      </IconButton>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
          </Grid>
          
          {filteredReports.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <Typography variant="body1">
                No reports found
              </Typography>
            </Box>
          )}
          
          <TablePagination
            rowsPerPageOptions={[6, 12, 24]}
            component="div"
            count={filteredReports.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </TabPanel>
      </Paper>
      
      {/* Report action menu */}
      <Menu
        id="report-menu"
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => handleViewReport(reports.find(r => r.id === activeReportMenu))}>
          <VisibilityIcon fontSize="small" sx={{ mr: 1 }} />
          View Report
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <FileDownloadIcon fontSize="small" sx={{ mr: 1 }} />
          Download Report
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <ShareIcon fontSize="small" sx={{ mr: 1 }} />
          Share Report
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => handleDeleteReportClick(reports.find(r => r.id === activeReportMenu))}>
          <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
          Delete Report
        </MenuItem>
      </Menu>
      
      {/* View report dialog */}
      <Dialog
        open={viewReportDialog}
        onClose={handleCloseViewDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          {selectedReport?.name}
          <IconButton
            aria-label="close"
            onClick={handleCloseViewDialog}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <DeleteIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          {selectedReport && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Report Summary
              </Typography>
              <Typography variant="body2">
                This dialog would display the actual report content in a formatted way.
                In a real implementation, this would show vulnerabilities, charts, and detailed findings.
              </Typography>
              <Alert severity="info" sx={{ mt: 2 }}>
                In a production version, this would load the actual report content from the server
                and render it appropriately based on the report format (PDF, HTML, or JSON).
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseViewDialog}>Close</Button>
          <Button color="primary" startIcon={<FileDownloadIcon />}>
            Download Report
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Delete confirmation dialog */}
      <Dialog
        open={deleteReportDialog}
        onClose={() => setDeleteReportDialog(false)}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the report "{selectedReport?.name}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteReportDialog(false)} color="primary">
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

export default Reports;