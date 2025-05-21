import React from 'react';
import { Card, CardContent, Typography, Box, IconButton, Tooltip, LinearProgress } from '@mui/material';
import { alpha } from '@mui/material/styles';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';

const StatCard = ({ 
  title, 
  value, 
  description, 
  icon, 
  color = 'primary', 
  change, 
  suffix,
  progress
}) => {
  // Generate box shadow based on color with reduced opacity
  const generateBoxShadow = (color) => {
    return `0 10px 20px ${alpha(color, 0.1)}, 0 6px 6px ${alpha(color, 0.1)}`;
  };

  // Determine change icon and color
  const showChange = change !== undefined && change !== null;
  const changeIcon = change >= 0 ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />;
  const changeColor = change >= 0 ? 'success.main' : 'error.main';
  
  return (
    <Card 
      sx={{ 
        height: '100%',
        position: 'relative',
        overflow: 'visible',
        boxShadow: generateBoxShadow(theme => theme.palette[color].main),
        borderTop: 3,
        borderColor: color + '.main',
        display: 'flex',
        flexDirection: 'column',
        '&:hover': {
          boxShadow: generateBoxShadow(theme => theme.palette[color].dark),
          transform: 'translateY(-5px)',
        },
        transition: 'transform 0.3s, box-shadow 0.3s',
      }}
    >
      <CardContent sx={{ flexGrow: 1, pb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ display: 'flex', flexDirection: 'column' }}>
            <Typography variant="overline" sx={{ mb: 0.5, color: 'text.secondary' }}>
              {title}
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Typography 
                variant="h4" 
                component="div" 
                sx={{ fontWeight: 700, color: `${color}.main` }}
              >
                {value}
                {suffix && <Typography component="span" variant="subtitle1" sx={{ ml: 0.5 }}>{suffix}</Typography>}
              </Typography>
              
              {showChange && (
                <Typography 
                  variant="body2" 
                  sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    color: changeColor,
                    ml: 1
                  }}
                >
                  {changeIcon}
                  {Math.abs(change)}%
                </Typography>
              )}
            </Box>
          </Box>
          
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            p: 1.5,
            borderRadius: '50%',
            bgcolor: `${color}.main`,
            color: 'white',
            boxShadow: `0 4px 10px ${alpha(theme => theme.palette[color].main, 0.3)}`
          }}>
            {icon}
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
          <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1 }}>
            {description}
          </Typography>
          
          {description && (
            <Tooltip title={description}>
              <IconButton size="small" sx={{ ml: 0.5 }}>
                <InfoOutlinedIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
        
        {progress !== undefined && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              color={color} 
              sx={{ 
                height: 6,
                borderRadius: 3,
                bgcolor: theme => alpha(theme.palette[color].main, 0.15)
              }} 
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default StatCard;