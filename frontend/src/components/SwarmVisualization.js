import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Paper,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
  Button,
  Alert,
  Fade,
  CircularProgress
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Visibility as VisibilityIcon,
  Memory as MemoryIcon,
  Hub as HubIcon,
  Psychology as PsychologyIcon,
  AutoGraph as AutoGraphIcon,
  Refresh as RefreshIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Share as ShareIcon
} from '@mui/icons-material';

const SwarmContainer = styled(Paper)(({ theme }) => ({
  background: `linear-gradient(135deg, 
    ${theme.palette.background.paper} 0%, 
    ${theme.palette.primary.dark}15 100%)`,
  border: `1px solid ${theme.palette.primary.main}30`,
  borderRadius: theme.spacing(2),
  overflow: 'hidden',
  position: 'relative',
  minHeight: '600px'
}));

const VectorNode = styled(Box)(({ theme, status, consciousness }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'active': return theme.palette.success.main;
      case 'learning': return theme.palette.warning.main;
      case 'attacking': return theme.palette.error.main;
      case 'dormant': return theme.palette.grey[500];
      default: return theme.palette.primary.main;
    }
  };

  const getConsciousnessGlow = () => {
    const intensity = Math.min(consciousness * 100, 100);
    return `0 0 ${10 + intensity/10}px ${getStatusColor()}${Math.floor(intensity * 2.55).toString(16).padStart(2, '0')}`;
  };

  return {
    position: 'absolute',
    width: 40 + consciousness * 20,
    height: 40 + consciousness * 20,
    borderRadius: '50%',
    background: `radial-gradient(circle, ${getStatusColor()}80, ${getStatusColor()}40)`,
    border: `2px solid ${getStatusColor()}`,
    boxShadow: getConsciousnessGlow(),
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    animation: status === 'active' ? 'pulse 2s infinite' : 'none',
    '&:hover': {
      transform: 'scale(1.1)',
      boxShadow: `${getConsciousnessGlow()}, 0 4px 20px rgba(0,0,0,0.3)`
    },
    '@keyframes pulse': {
      '0%': { opacity: 0.8 },
      '50%': { opacity: 1 },
      '100%': { opacity: 0.8 }
    }
  };
});

const ConnectionLine = styled('svg')(({ theme }) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  width: '100%',
  height: '100%',
  pointerEvents: 'none',
  zIndex: 1
}));

const ConsciousnessBar = styled(LinearProgress)(({ theme }) => ({
  height: 8,
  borderRadius: 4,
  background: theme.palette.grey[800],
  '& .MuiLinearProgress-bar': {
    borderRadius: 4,
    background: `linear-gradient(90deg, 
      ${theme.palette.primary.main}, 
      ${theme.palette.secondary.main}, 
      ${theme.palette.success.main})`
  }
}));

const SwarmVisualization = ({ swarmData, realTimeUpdates = true }) => {
  const [vectors, setVectors] = useState([]);
  const [connections, setConnections] = useState([]);
  const [hiveMindState, setHiveMindState] = useState({});
  const [selectedVector, setSelectedVector] = useState(null);
  const [showConnections, setShowConnections] = useState(true);
  const [animationSpeed, setAnimationSpeed] = useState(1);
  const [containerDimensions, setContainerDimensions] = useState({ width: 800, height: 600 });

  // Generate random positions for vectors
  const generateVectorPositions = useCallback((vectorCount) => {
    const positions = [];
    for (let i = 0; i < vectorCount; i++) {
      positions.push({
        x: Math.random() * (containerDimensions.width - 100) + 50,
        y: Math.random() * (containerDimensions.height - 100) + 50
      });
    }
    return positions;
  }, [containerDimensions]);

  // Simulate swarm data if not provided
  useEffect(() => {
    if (!swarmData) {
      const mockVectors = [
        {
          id: 'vector_1',
          type: 'multi_vector',
          status: 'active',
          consciousness: 0.85,
          capabilities: ['injection', 'bypass', 'reconnaissance'],
          intelligence_shared: 15,
          attacks_coordinated: 3
        },
        {
          id: 'vector_2', 
          type: 'polymorphic',
          status: 'learning',
          consciousness: 0.72,
          capabilities: ['mutation', 'evasion', 'adaptation'],
          intelligence_shared: 8,
          attacks_coordinated: 1
        },
        {
          id: 'vector_3',
          type: 'orchestration',
          status: 'attacking',
          consciousness: 0.91,
          capabilities: ['coordination', 'strategy', 'execution'],
          intelligence_shared: 22,
          attacks_coordinated: 7
        },
        {
          id: 'vector_4',
          type: 'autonomous',
          status: 'dormant',
          consciousness: 0.45,
          capabilities: ['autonomous_decision', 'learning', 'evolution'],
          intelligence_shared: 3,
          attacks_coordinated: 0
        },
        {
          id: 'hive_mind',
          type: 'coordinator',
          status: 'active',
          consciousness: 0.95,
          capabilities: ['global_coordination', 'intelligence_synthesis', 'emergence_detection'],
          intelligence_shared: 50,
          attacks_coordinated: 11
        }
      ];

      const positions = generateVectorPositions(mockVectors.length);
      const vectorsWithPositions = mockVectors.map((vector, index) => ({
        ...vector,
        ...positions[index]
      }));

      setVectors(vectorsWithPositions);

      // Generate connections between vectors
      const mockConnections = [];
      for (let i = 0; i < vectorsWithPositions.length; i++) {
        for (let j = i + 1; j < vectorsWithPositions.length; j++) {
          if (Math.random() > 0.4) { // 60% chance of connection
            mockConnections.push({
              from: vectorsWithPositions[i].id,
              to: vectorsWithPositions[j].id,
              strength: Math.random(),
              type: Math.random() > 0.5 ? 'intelligence' : 'coordination'
            });
          }
        }
      }
      setConnections(mockConnections);

      setHiveMindState({
        collective_iq: 0.83,
        active_vectors: mockVectors.filter(v => v.status === 'active').length,
        total_intelligence_shared: mockVectors.reduce((sum, v) => sum + v.intelligence_shared, 0),
        consciousness_level: mockVectors.reduce((sum, v) => sum + v.consciousness, 0) / mockVectors.length,
        emergence_events: 3,
        coordination_efficiency: 0.91
      });
    }
  }, [swarmData, generateVectorPositions]);

  // Real-time updates simulation
  useEffect(() => {
    if (!realTimeUpdates) return;

    const interval = setInterval(() => {
      setVectors(prevVectors => 
        prevVectors.map(vector => ({
          ...vector,
          consciousness: Math.min(0.99, vector.consciousness + (Math.random() - 0.5) * 0.05),
          intelligence_shared: vector.intelligence_shared + Math.floor(Math.random() * 3),
          status: Math.random() > 0.8 ? 
            ['active', 'learning', 'attacking', 'dormant'][Math.floor(Math.random() * 4)] : 
            vector.status
        }))
      );

      setHiveMindState(prevState => ({
        ...prevState,
        collective_iq: Math.min(0.99, prevState.collective_iq + (Math.random() - 0.5) * 0.02),
        consciousness_level: Math.min(0.99, prevState.consciousness_level + (Math.random() - 0.5) * 0.01)
      }));
    }, 2000 / animationSpeed);

    return () => clearInterval(interval);
  }, [realTimeUpdates, animationSpeed]);

  const renderVector = (vector) => (
    <VectorNode
      key={vector.id}
      status={vector.status}
      consciousness={vector.consciousness}
      style={{
        left: vector.x,
        top: vector.y,
        zIndex: selectedVector === vector.id ? 10 : 2
      }}
      onClick={() => setSelectedVector(selectedVector === vector.id ? null : vector.id)}
    >
      {vector.type === 'coordinator' ? <HubIcon /> : 
       vector.type === 'polymorphic' ? <AutoGraphIcon /> :
       vector.type === 'autonomous' ? <PsychologyIcon /> : <SecurityIcon />}
    </VectorNode>
  );

  const renderConnections = () => {
    if (!showConnections) return null;

    return (
      <ConnectionLine>
        {connections.map((connection, index) => {
          const fromVector = vectors.find(v => v.id === connection.from);
          const toVector = vectors.find(v => v.id === connection.to);
          
          if (!fromVector || !toVector) return null;

          const opacity = connection.strength * 0.8 + 0.2;
          const strokeWidth = connection.strength * 3 + 1;
          const color = connection.type === 'intelligence' ? '#4fc3f7' : '#ff9800';

          return (
            <line
              key={index}
              x1={fromVector.x + 20}
              y1={fromVector.y + 20}
              x2={toVector.x + 20}
              y2={toVector.y + 20}
              stroke={color}
              strokeWidth={strokeWidth}
              strokeOpacity={opacity}
              strokeDasharray={connection.type === 'coordination' ? '5,5' : 'none'}
            />
          );
        })}
      </ConnectionLine>
    );
  };

  const getVectorDetails = () => {
    if (!selectedVector) return null;
    const vector = vectors.find(v => v.id === selectedVector);
    if (!vector) return null;

    return (
      <Card sx={{ position: 'absolute', top: 16, right: 16, width: 300, zIndex: 20 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {vector.type.replace('_', ' ').toUpperCase()} Vector
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            ID: {vector.id}
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>
              Consciousness Level: {(vector.consciousness * 100).toFixed(1)}%
            </Typography>
            <ConsciousnessBar variant="determinate" value={vector.consciousness * 100} />
          </Box>

          <Box sx={{ mb: 2 }}>
            <Chip 
              label={vector.status.toUpperCase()} 
              color={vector.status === 'active' ? 'success' : 
                     vector.status === 'learning' ? 'warning' :
                     vector.status === 'attacking' ? 'error' : 'default'}
              size="small"
            />
          </Box>

          <Typography variant="body2" gutterBottom>
            Capabilities:
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
            {vector.capabilities.map((cap, index) => (
              <Chip key={index} label={cap} size="small" variant="outlined" />
            ))}
          </Box>

          <Grid container spacing={1}>
            <Grid item xs={6}>
              <Typography variant="caption">Intelligence Shared</Typography>
              <Typography variant="h6">{vector.intelligence_shared}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption">Attacks Coordinated</Typography>
              <Typography variant="h6">{vector.attacks_coordinated}</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      {/* Hive Mind Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={8}>
              <Typography variant="h5" gutterBottom>
                <HubIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Swarm Intelligence Hub
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption">Collective IQ</Typography>
                  <Typography variant="h6">{(hiveMindState.collective_iq * 100).toFixed(1)}%</Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption">Active Vectors</Typography>
                  <Typography variant="h6">{hiveMindState.active_vectors}</Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption">Intelligence Shared</Typography>
                  <Typography variant="h6">{hiveMindState.total_intelligence_shared}</Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography variant="caption">Emergence Events</Typography>
                  <Typography variant="h6">{hiveMindState.emergence_events}</Typography>
                </Grid>
              </Grid>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <FormControlLabel
                  control={
                    <Switch 
                      checked={showConnections} 
                      onChange={(e) => setShowConnections(e.target.checked)}
                      size="small"
                    />
                  }
                  label="Connections"
                />
                <Tooltip title="Refresh Data">
                  <IconButton size="small">
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Real-time Updates">
                  <IconButton size="small" color={realTimeUpdates ? 'primary' : 'default'}>
                    <VisibilityIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Consciousness Level Bar */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="body2" gutterBottom>
          Collective Consciousness Level: {(hiveMindState.consciousness_level * 100).toFixed(1)}%
        </Typography>
        <ConsciousnessBar 
          variant="determinate" 
          value={hiveMindState.consciousness_level * 100} 
        />
      </Box>

      {/* Swarm Visualization */}
      <SwarmContainer elevation={3}>
        {renderConnections()}
        {vectors.map(renderVector)}
        {getVectorDetails()}
      </SwarmContainer>

      {/* Legend */}
      <Box sx={{ mt: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Chip icon={<SecurityIcon />} label="Multi-Vector" size="small" />
        <Chip icon={<AutoGraphIcon />} label="Polymorphic" size="small" />
        <Chip icon={<PsychologyIcon />} label="Autonomous" size="small" />
        <Chip icon={<HubIcon />} label="Hive Mind" size="small" />
      </Box>
    </Box>
  );
};

export default SwarmVisualization;