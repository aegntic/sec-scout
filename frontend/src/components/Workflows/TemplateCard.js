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
  CardActionArea,
  alpha
} from '@mui/material';
import { styled } from '@mui/material/styles';
import AddIcon from '@mui/icons-material/Add';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';

// Template icons
import WebIcon from '@mui/icons-material/Web';
import StorageIcon from '@mui/icons-material/Storage';
import DnsIcon from '@mui/icons-material/Dns';
import LayersIcon from '@mui/icons-material/Layers';
import ApiIcon from '@mui/icons-material/Api';
import SecurityIcon from '@mui/icons-material/Security';

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
  marginTop: theme.spacing(1.5),
}));

const TemplateIcon = styled(Box)(({ theme, templateType }) => {
  const getGradient = (type) => {
    switch (type) {
      case 'web':
        return 'linear-gradient(135deg, #6C63FF 0%, #4335D0 100%)';
      case 'network':
        return 'linear-gradient(135deg, #00BFA6 0%, #008B7A 100%)';
      case 'container':
        return 'linear-gradient(135deg, #FF5252 0%, #C62828 100%)';
      case 'fullstack':
        return 'linear-gradient(135deg, #FFB74D 0%, #EF6C00 100%)';
      case 'api':
        return 'linear-gradient(135deg, #4FC3F7 0%, #0288D1 100%)';
      default:
        return 'linear-gradient(135deg, #9575CD 0%, #5E35B1 100%)';
    }
  };
  
  return {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: 48,
    height: 48,
    borderRadius: 8,
    background: getGradient(templateType),
    boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
    marginRight: theme.spacing(2),
  };
});

const getTemplateIcon = (templateId) => {
  if (templateId.includes('web')) return <WebIcon fontSize="large" />;
  if (templateId.includes('network')) return <DnsIcon fontSize="large" />;
  if (templateId.includes('container')) return <StorageIcon fontSize="large" />;
  if (templateId.includes('fullstack')) return <LayersIcon fontSize="large" />;
  if (templateId.includes('api')) return <ApiIcon fontSize="large" />;
  return <SecurityIcon fontSize="large" />;
};

const getTemplateType = (templateId) => {
  if (templateId.includes('web')) return 'web';
  if (templateId.includes('network')) return 'network';
  if (templateId.includes('container')) return 'container';
  if (templateId.includes('fullstack')) return 'fullstack';
  if (templateId.includes('api')) return 'api';
  return 'security';
};

const TemplateCard = ({ 
  template, 
  onSelect, 
  onInfo
}) => {
  const {
    id,
    name,
    description,
    target_type,
    tags = [],
  } = template;

  const templateType = getTemplateType(id);
  const icon = getTemplateIcon(id);

  // Handle button clicks without triggering card click
  const handleButtonClick = (event, callback) => {
    event.stopPropagation();
    if (callback) callback(template);
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
        },
        background: (theme) => `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.9)}, ${theme.palette.background.paper})`,
        position: 'relative',
        overflow: 'hidden',
        '&::after': {
          content: '""',
          position: 'absolute',
          top: 0,
          right: 0,
          width: '100px',
          height: '100px',
          background: (theme) => `linear-gradient(135deg, transparent 50%, ${alpha(theme.palette.primary.main, 0.05)} 50%)`,
          borderTopRightRadius: 12,
          zIndex: 0,
        },
      }}
    >
      <CardActionArea onClick={() => onSelect && onSelect(template)} sx={{ flexGrow: 1 }}>
        <CardContent sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
            <TemplateIcon templateType={templateType}>
              {icon}
            </TemplateIcon>
            
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" component="div" noWrap>
                {name}
              </Typography>
              <Chip 
                size="small" 
                label={target_type?.toUpperCase() || 'ALL'}
                sx={{
                  fontWeight: 500,
                  fontSize: '0.7rem',
                  height: 20,
                  bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1),
                  color: 'primary.main',
                  mt: 0.5
                }}
              />
            </Box>
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ 
            mb: 1, 
            flexGrow: 1,
            overflow: 'hidden', 
            textOverflow: 'ellipsis', 
            display: '-webkit-box', 
            WebkitLineClamp: 3, 
            WebkitBoxOrient: 'vertical' 
          }}>
            {description}
          </Typography>
          
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

      <CardActions disableSpacing sx={{ p: 1.5, pt: 0.5, justifyContent: 'space-between' }}>
        <Tooltip title="View template details">
          <IconButton 
            size="small"
            color="info"
            onClick={(e) => handleButtonClick(e, onInfo)}
          >
            <InfoOutlinedIcon />
          </IconButton>
        </Tooltip>
        
        <Button 
          variant="contained" 
          startIcon={<AddIcon />}
          onClick={(e) => handleButtonClick(e, onSelect)}
          size="small"
        >
          Use Template
        </Button>
      </CardActions>
    </Card>
  );
};

export default TemplateCard;