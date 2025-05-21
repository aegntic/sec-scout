import React, { useRef, useEffect, useState } from 'react';
import { Box, Card, CardContent, Typography, Divider, useTheme } from '@mui/material';
import { severityColors } from '../../theme';

const ThreatMap = ({ data = [] }) => {
  const canvasRef = useRef(null);
  const theme = useTheme();
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  
  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      if (canvasRef.current) {
        const container = canvasRef.current.parentElement;
        setDimensions({
          width: container.clientWidth,
          height: Math.max(300, container.clientWidth * 0.5)  // Maintain aspect ratio
        });
      }
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.addEventListener('resize', handleResize);
    };
  }, []);
  
  // Draw the threat map
  useEffect(() => {
    if (!canvasRef.current || !dimensions.width || !data.length) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const { width, height } = dimensions;
    
    // Set canvas size
    canvas.width = width;
    canvas.height = height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw background grid
    ctx.strokeStyle = theme.palette.divider;
    ctx.lineWidth = 0.5;
    
    // Grid size
    const gridSize = 30;
    
    // Draw vertical grid lines
    for (let x = 0; x <= width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    
    // Draw horizontal grid lines
    for (let y = 0; y <= height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }
    
    // Draw nodes
    // Each node will be a colored circle representing a vulnerability
    const centerX = width / 2;
    const centerY = height / 2;
    const maxRadius = Math.min(width, height) * 0.4;
    
    // Group data by severity
    const groupedData = data.reduce((acc, item) => {
      if (!acc[item.severity]) {
        acc[item.severity] = [];
      }
      acc[item.severity].push(item);
      return acc;
    }, {});
    
    // Draw connections from center to vulnerability groups
    Object.entries(groupedData).forEach(([severity, items], severityIndex) => {
      const severityColor = severityColors[severity] || theme.palette.grey[500];
      const angle = (2 * Math.PI / Object.keys(groupedData).length) * severityIndex;
      const radius = maxRadius * 0.7;
      
      const groupX = centerX + radius * Math.cos(angle);
      const groupY = centerY + radius * Math.sin(angle);
      
      // Draw connection line
      ctx.beginPath();
      ctx.strokeStyle = severityColor;
      ctx.lineWidth = 1.5;
      ctx.setLineDash([5, 5]);
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(groupX, groupY);
      ctx.stroke();
      ctx.setLineDash([]);
      
      // Draw vulnerability nodes in a circular pattern around the severity group
      const nodeRadius = 8;
      const groupRadius = nodeRadius * 5;
      
      items.forEach((item, itemIndex) => {
        const itemAngle = angle - Math.PI/4 + (Math.PI/2 / (items.length + 1)) * (itemIndex + 1);
        const itemX = groupX + groupRadius * Math.cos(itemAngle);
        const itemY = groupY + groupRadius * Math.sin(itemAngle);
        
        // Draw node
        ctx.beginPath();
        ctx.fillStyle = severityColor;
        ctx.arc(itemX, itemY, nodeRadius, 0, 2 * Math.PI);
        ctx.fill();
        
        // Add glow effect
        ctx.beginPath();
        const gradient = ctx.createRadialGradient(
          itemX, itemY, nodeRadius * 0.5,
          itemX, itemY, nodeRadius * 2
        );
        gradient.addColorStop(0, 'rgba(255, 255, 255, 0)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        
        // Add pulse animation effect
        if (itemIndex % 3 === 0) {  // Only some nodes will pulse
          const now = Date.now();
          const pulseFactor = Math.sin(now / 500) * 0.5 + 0.5;  // Value between 0 and 1
          gradient.addColorStop(0, `rgba(255, 255, 255, ${0.3 * pulseFactor})`);
        }
        
        ctx.fillStyle = gradient;
        ctx.arc(itemX, itemY, nodeRadius * 3, 0, 2 * Math.PI);
        ctx.fill();
        
        // Connect to neighbor nodes within the same severity group
        if (itemIndex > 0) {
          const prevItemAngle = angle - Math.PI/4 + (Math.PI/2 / (items.length + 1)) * itemIndex;
          const prevItemX = groupX + groupRadius * Math.cos(prevItemAngle);
          const prevItemY = groupY + groupRadius * Math.sin(prevItemAngle);
          
          ctx.beginPath();
          ctx.strokeStyle = severityColor;
          ctx.lineWidth = 0.75;
          ctx.moveTo(itemX, itemY);
          ctx.lineTo(prevItemX, prevItemY);
          ctx.stroke();
        }
      });
      
      // Label for the severity group
      ctx.font = '12px Arial';
      ctx.fillStyle = severityColor;
      ctx.textAlign = 'center';
      
      // Position the text outside the group
      const textRadius = maxRadius * 0.85;
      const textX = centerX + textRadius * Math.cos(angle);
      const textY = centerY + textRadius * Math.sin(angle);
      
      ctx.fillText(
        `${severity.toUpperCase()} (${items.length})`, 
        textX, 
        textY
      );
    });
    
    // Draw a node at the center representing the target
    ctx.beginPath();
    ctx.fillStyle = theme.palette.primary.main;
    ctx.arc(centerX, centerY, 12, 0, 2 * Math.PI);
    ctx.fill();
    
    // Add a glow effect to the center node
    const gradient = ctx.createRadialGradient(
      centerX, centerY, 12,
      centerX, centerY, 40
    );
    gradient.addColorStop(0, 'rgba(108, 99, 255, 0.2)');
    gradient.addColorStop(1, 'rgba(108, 99, 255, 0)');
    
    ctx.beginPath();
    ctx.fillStyle = gradient;
    ctx.arc(centerX, centerY, 40, 0, 2 * Math.PI);
    ctx.fill();
    
    // Add label for the center node
    ctx.font = 'bold 12px Arial';
    ctx.fillStyle = theme.palette.text.primary;
    ctx.textAlign = 'center';
    ctx.fillText('TARGET', centerX, centerY + 30);
    
  }, [data, dimensions, theme]);
  
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Threat Visualization Map
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Visual representation of detected vulnerabilities and their relationship to the target
        </Typography>
        <Divider sx={{ mb: 3 }} />
        
        <Box sx={{ position: 'relative', width: '100%' }}>
          <canvas 
            ref={canvasRef} 
            style={{ width: '100%', height: 'auto' }}
          />
          
          {data.length === 0 && (
            <Box 
              sx={{ 
                position: 'absolute', 
                top: 0, 
                left: 0, 
                right: 0, 
                bottom: 0, 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                bgcolor: 'rgba(0,0,0,0.1)',
                borderRadius: 1
              }}
            >
              <Typography variant="subtitle1" color="text.secondary">
                No vulnerability data available
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default ThreatMap;