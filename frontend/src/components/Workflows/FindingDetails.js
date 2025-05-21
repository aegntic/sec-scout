import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Chip, 
  Divider, 
  Card, 
  CardContent,
  Grid,
  Link,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  styled,
  alpha
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import BugReportOutlinedIcon from '@mui/icons-material/BugReportOutlined';
import LinkIcon from '@mui/icons-material/Link';
import SecurityIcon from '@mui/icons-material/Security';
import CodeIcon from '@mui/icons-material/Code';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import ReactJson from 'react-json-view';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const SeverityChip = styled(Chip)(({ theme, severity }) => {
  const getSeverityColor = (severity) => {
    const severityMap = {
      critical: theme.palette.severity.critical,
      high: theme.palette.severity.high,
      medium: theme.palette.severity.medium,
      low: theme.palette.severity.low,
      info: theme.palette.severity.info,
      unknown: theme.palette.grey[500]
    };
    return severityMap[severity.toLowerCase()] || theme.palette.grey[500];
  };
  
  const color = getSeverityColor(severity);
  
  return {
    backgroundColor: alpha(color, 0.15),
    color: color,
    fontWeight: 600,
    '& .MuiChip-label': {
      padding: '0 8px',
    }
  };
});

const SectionCard = styled(Card)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  overflow: 'visible',
  border: `1px solid ${alpha(theme.palette.divider, 0.05)}`,
  boxShadow: theme.shadows[2],
}));

const SectionTitle = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  marginBottom: theme.spacing(1),
  '& svg': {
    marginRight: theme.spacing(1),
    color: theme.palette.primary.main,
  },
}));

const CodeBlock = styled(Box)(({ theme }) => ({
  borderRadius: theme.shape.borderRadius,
  overflow: 'hidden',
  marginTop: theme.spacing(1),
  marginBottom: theme.spacing(1),
}));

const FindingDetails = ({ finding }) => {
  if (!finding) return null;
  
  const { 
    title, 
    severity, 
    description, 
    evidence = {},
    remediation,
    template_id,
    host,
    url,
    tags = [],
    task_id,
    task_name,
    adapter_name
  } = finding;
  
  const renderEvidence = () => {
    // Handle different types of evidence structures
    if (!evidence || Object.keys(evidence).length === 0) {
      return <Typography variant="body2" color="text.secondary">No evidence provided</Typography>;
    }
    
    // Special case: render request/response if available
    if (evidence.request && evidence.response) {
      return (
        <>
          <Accordion sx={{ mb: 1 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2">HTTP Request</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <CodeBlock>
                <SyntaxHighlighter language="http" style={atomOneDark}>
                  {evidence.request}
                </SyntaxHighlighter>
              </CodeBlock>
            </AccordionDetails>
          </Accordion>
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle2">HTTP Response</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <CodeBlock>
                <SyntaxHighlighter language="http" style={atomOneDark}>
                  {evidence.response}
                </SyntaxHighlighter>
              </CodeBlock>
            </AccordionDetails>
          </Accordion>
        </>
      );
    }
    
    // Special case: render parameters if available
    if (evidence.parameter) {
      return (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Vulnerable Parameter
          </Typography>
          <Typography variant="body2" sx={{ fontFamily: 'monospace', p: 1, bgcolor: 'background.dark', borderRadius: 1 }}>
            {evidence.parameter}
          </Typography>
          
          {evidence.injection_type && (
            <Box sx={{ mt: a => 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Injection Type
              </Typography>
              <Typography variant="body2">
                {evidence.injection_type}
              </Typography>
            </Box>
          )}
        </Box>
      );
    }
    
    // Default: render evidence as JSON
    return (
      <Box sx={{ mt: 1 }}>
        <ReactJson 
          src={evidence} 
          theme="monokai" 
          displayDataTypes={false} 
          collapsed={1}
          name={false}
          style={{ 
            padding: '10px', 
            borderRadius: '8px',
            backgroundColor: '#272822'
          }}
        />
      </Box>
    );
  };
  
  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ mb: 1, fontWeight: 600 }}>
            {title}
          </Typography>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1 }}>
            <SeverityChip 
              label={severity.toUpperCase()} 
              severity={severity}
              size="small"
            />
            
            {template_id && (
              <Chip 
                size="small" 
                label={template_id}
                variant="outlined"
              />
            )}
            
            {adapter_name && (
              <Chip 
                size="small" 
                label={adapter_name}
                color="primary"
                variant="outlined"
              />
            )}
          </Box>
        </Box>
      </Box>
      
      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          {/* Description Section */}
          <SectionCard>
            <CardContent>
              <SectionTitle>
                <BugReportOutlinedIcon />
                <Typography variant="h6">Description</Typography>
              </SectionTitle>
              <Typography variant="body1">{description}</Typography>
            </CardContent>
          </SectionCard>
          
          {/* Evidence Section */}
          <SectionCard>
            <CardContent>
              <SectionTitle>
                <CodeIcon />
                <Typography variant="h6">Evidence</Typography>
              </SectionTitle>
              {renderEvidence()}
            </CardContent>
          </SectionCard>
          
          {/* Remediation Section */}
          {remediation && (
            <SectionCard>
              <CardContent>
                <SectionTitle>
                  <VerifiedUserIcon />
                  <Typography variant="h6">Remediation</Typography>
                </SectionTitle>
                <Typography variant="body1">{remediation}</Typography>
              </CardContent>
            </SectionCard>
          )}
        </Grid>
        
        <Grid item xs={12} md={4}>
          {/* Details Section */}
          <SectionCard>
            <CardContent>
              <SectionTitle>
                <SecurityIcon />
                <Typography variant="h6">Details</Typography>
              </SectionTitle>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Source
                </Typography>
                <Typography variant="body2">
                  {task_name || `Task ${task_id}`}
                </Typography>
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              {host && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Host
                  </Typography>
                  <Typography variant="body2" sx={{ wordBreak: 'break-all' }}>
                    {host}
                  </Typography>
                </Box>
              )}
              
              {url && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    URL
                  </Typography>
                  <Link 
                    href={url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    sx={{ 
                      display: 'inline-flex', 
                      alignItems: 'center',
                      wordBreak: 'break-all',
                      maxWidth: '100%',
                      '& svg': { ml: 0.5, fontSize: '1rem' }
                    }}
                  >
                    <Typography variant="body2" noWrap>
                      {url}
                    </Typography>
                    <LinkIcon fontSize="small" />
                  </Link>
                </Box>
              )}
              
              {tags && tags.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Tags
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {tags.map((tag, index) => (
                      <Chip 
                        key={index}
                        size="small"
                        label={tag}
                        variant="outlined"
                        sx={{ 
                          borderRadius: '4px',
                          height: '20px',
                          '& .MuiChip-label': { px: 1, py: 0.25, fontSize: '0.7rem' }
                        }}
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </CardContent>
          </SectionCard>
          
          {/* References Section (if available) */}
          {evidence && evidence.references && evidence.references.length > 0 && (
            <SectionCard>
              <CardContent>
                <SectionTitle>
                  <HelpOutlineIcon />
                  <Typography variant="h6">References</Typography>
                </SectionTitle>
                <Box component="ul" sx={{ pl: 2 }}>
                  {evidence.references.map((ref, index) => (
                    <Box component="li" key={index} sx={{ mb: 1 }}>
                      <Link href={ref} target="_blank" rel="noopener noreferrer" sx={{ wordBreak: 'break-all' }}>
                        {ref}
                      </Link>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </SectionCard>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default FindingDetails;