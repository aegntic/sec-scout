import { createTheme, alpha } from '@mui/material/styles';

// Custom color palette
const primaryColor = '#6C63FF';  // Main purple/blue
const secondaryColor = '#00BFA6'; // Teal accent
const errorColor = '#FF5252';     // Bright red
const warningColor = '#FFB74D';   // Orange
const infoColor = '#4FC3F7';      // Light blue
const successColor = '#66BB6A';   // Green
const darkColor = '#1E1E2F';      // Dark blue-black

// Severity colors
export const severityColors = {
  critical: '#E53935', // Deep red
  high: '#FF5252',     // Bright red
  medium: '#FFB74D',   // Orange
  low: '#4FC3F7',      // Light blue
  info: '#78909C'      // Blue-grey
};

// Background gradients
const darkGradient = `linear-gradient(315deg, ${darkColor} 0%, #27293D 100%)`;
const primaryGradient = `linear-gradient(315deg, ${primaryColor} 0%, #8E86FF 100%)`;

// Create a theme instance
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: primaryColor,
      light: '#8E86FF',
      dark: '#5A51DE',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: secondaryColor,
      light: '#33CAAE',
      dark: '#00A389',
      contrastText: '#FFFFFF',
    },
    error: {
      main: errorColor,
      light: '#FF7676',
      dark: '#DC3545',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: warningColor,
      light: '#FFCC80',
      dark: '#F57C00',
      contrastText: '#FFFFFF',
    },
    info: {
      main: infoColor,
      light: '#81D4FA',
      dark: '#0288D1',
      contrastText: '#FFFFFF',
    },
    success: {
      main: successColor,
      light: '#A5D6A7',
      dark: '#388E3C',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#1A1B2A',
      paper: '#27293D',
      dark: darkColor,
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#FFFFFFB3',
      disabled: '#FFFFFF80',
    },
    divider: 'rgba(255, 255, 255, 0.12)',
    action: {
      active: 'rgba(255, 255, 255, 0.7)',
      hover: 'rgba(255, 255, 255, 0.08)',
      selected: 'rgba(255, 255, 255, 0.16)',
      disabled: 'rgba(255, 255, 255, 0.3)',
      disabledBackground: 'rgba(255, 255, 255, 0.12)',
    },
    severity: severityColors,
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 600,
      fontSize: '2.5rem',
      lineHeight: 1.2,
      letterSpacing: '-0.01562em',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
      lineHeight: 1.2,
      letterSpacing: '-0.00833em',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
      lineHeight: 1.2,
      letterSpacing: '0em',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
      lineHeight: 1.2,
      letterSpacing: '0.00735em',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
      lineHeight: 1.2,
      letterSpacing: '0em',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
      lineHeight: 1.2,
      letterSpacing: '0.0075em',
    },
    subtitle1: {
      fontWeight: 500,
      fontSize: '1rem',
      lineHeight: 1.5,
      letterSpacing: '0.00938em',
    },
    subtitle2: {
      fontWeight: 500,
      fontSize: '0.875rem',
      lineHeight: 1.5,
      letterSpacing: '0.00714em',
    },
    body1: {
      fontWeight: 400,
      fontSize: '1rem',
      lineHeight: 1.5,
      letterSpacing: '0.00938em',
    },
    body2: {
      fontWeight: 400,
      fontSize: '0.875rem',
      lineHeight: 1.5,
      letterSpacing: '0.01071em',
    },
    button: {
      fontWeight: 600,
      fontSize: '0.875rem',
      lineHeight: 1.5,
      letterSpacing: '0.02857em',
      textTransform: 'none',
    },
    caption: {
      fontWeight: 400,
      fontSize: '0.75rem',
      lineHeight: 1.5,
      letterSpacing: '0.03333em',
    },
    overline: {
      fontWeight: 500,
      fontSize: '0.75rem',
      lineHeight: 1.5,
      letterSpacing: '0.08333em',
      textTransform: 'uppercase',
    },
  },
  shape: {
    borderRadius: 10,
  },
  shadows: [
    'none',
    '0px 2px 4px rgba(0, 0, 0, 0.1)',
    '0px 4px 8px rgba(0, 0, 0, 0.12)',
    '0px 6px 12px rgba(0, 0, 0, 0.14)',
    '0px 8px 16px rgba(0, 0, 0, 0.16)',
    '0px 10px 20px rgba(0, 0, 0, 0.18)',
    '0px 12px 24px rgba(0, 0, 0, 0.2)',
    '0px 14px 28px rgba(0, 0, 0, 0.22)',
    '0px 16px 32px rgba(0, 0, 0, 0.24)',
    '0px 18px 36px rgba(0, 0, 0, 0.26)',
    '0px 20px 40px rgba(0, 0, 0, 0.28)',
    '0px 22px 44px rgba(0, 0, 0, 0.3)',
    '0px 24px 48px rgba(0, 0, 0, 0.32)',
    '0px 26px 52px rgba(0, 0, 0, 0.34)',
    '0px 28px 56px rgba(0, 0, 0, 0.36)',
    '0px 30px 60px rgba(0, 0, 0, 0.38)',
    '0px 32px 64px rgba(0, 0, 0, 0.4)',
    '0px 34px 68px rgba(0, 0, 0, 0.42)',
    '0px 36px 72px rgba(0, 0, 0, 0.44)',
    '0px 38px 76px rgba(0, 0, 0, 0.46)',
    '0px 40px 80px rgba(0, 0, 0, 0.48)',
    '0px 42px 84px rgba(0, 0, 0, 0.5)',
    '0px 44px 88px rgba(0, 0, 0, 0.52)',
    '0px 46px 92px rgba(0, 0, 0, 0.54)',
    '0px 48px 96px rgba(0, 0, 0, 0.56)'
  ],
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundColor: '#1A1B2A',
          backgroundImage: 'radial-gradient(at 50% 0%, rgba(108, 99, 255, 0.1) 0%, rgba(26, 27, 42, 0) 75%)',
          backgroundAttachment: 'fixed',
          '&::-webkit-scrollbar': {
            width: '8px',
            height: '8px',
          },
          '&::-webkit-scrollbar-track': {
            background: 'rgba(255, 255, 255, 0.05)',
          },
          '&::-webkit-scrollbar-thumb': {
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '4px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: 'rgba(255, 255, 255, 0.2)',
          },
        },
        '@keyframes pulse': {
          '0%': {
            opacity: 0.6,
          },
          '50%': {
            opacity: 0.3,
          },
          '100%': {
            opacity: 0.6,
          },
        },
        '.animate-pulse': {
          animation: 'pulse 2s cubic-bezier(.4,0,.6,1) infinite',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: darkGradient,
          boxShadow: '0 4px 20px 0 rgba(0, 0, 0, 0.14)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: darkColor,
          backgroundImage: darkGradient,
          borderRight: 'none',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#27293D',
          boxShadow: '0 1px 20px 0 rgba(0, 0, 0, 0.1)',
          '&.MuiPaper-elevation0': {
            boxShadow: 'none',
          },
        },
        outlined: {
          borderColor: 'rgba(255, 255, 255, 0.12)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: '8px',
          padding: '8px 16px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          '&:hover': {
            boxShadow: '0 6px 10px rgba(0, 0, 0, 0.2)',
          },
        },
        contained: {
          boxShadow: '0 3px 5px 0 rgba(0, 0, 0, 0.2)',
        },
        containedPrimary: {
          background: primaryGradient,
          '&:hover': {
            background: primaryGradient,
            filter: 'brightness(1.1)',
          },
        },
        containedSecondary: {
          background: `linear-gradient(315deg, ${secondaryColor} 0%, #33CAAE 100%)`,
          '&:hover': {
            background: `linear-gradient(315deg, ${secondaryColor} 0%, #33CAAE 100%)`,
            filter: 'brightness(1.1)',
          },
        },
        outlined: {
          borderWidth: '2px',
          '&:hover': {
            borderWidth: '2px',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#27293D',
          backgroundImage: 'none',
          borderRadius: '12px',
          boxShadow: '0 2px 10px 0 rgba(0, 0, 0, 0.1)',
          overflow: 'hidden',
          transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
          '&:hover': {
            boxShadow: '0 5px 15px 0 rgba(0, 0, 0, 0.15)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiCardHeader: {
      styleOverrides: {
        root: {
          padding: '16px 20px',
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: '20px',
          '&:last-child': {
            paddingBottom: '20px',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '8px',
            transition: 'box-shadow 0.2s ease-in-out',
            '&.Mui-focused': {
              boxShadow: `0 0 0 2px ${alpha(primaryColor, 0.25)}`,
            },
          },
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: 'rgba(255, 255, 255, 0.23)',
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: primaryColor,
            borderWidth: 2,
          },
        },
        notchedOutline: {
          borderColor: 'rgba(255, 255, 255, 0.15)',
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
          padding: '16px',
        },
        head: {
          fontWeight: 600,
          color: 'rgba(255, 255, 255, 0.8)',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: '4px',
          minHeight: '48px',
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        indicator: {
          height: '3px',
          borderRadius: '1.5px',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: '6px',
          fontWeight: 500,
        },
        filled: {
          boxShadow: '0 2px 5px 0 rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          marginBottom: '4px',
          '&.Mui-selected': {
            backgroundColor: alpha(primaryColor, 0.15),
            '&:hover': {
              backgroundColor: alpha(primaryColor, 0.25),
            },
          },
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          '&.Mui-selected': {
            backgroundColor: alpha(primaryColor, 0.15),
            '&:hover': {
              backgroundColor: alpha(primaryColor, 0.25),
            },
          },
        },
      },
    },
    MuiSwitch: {
      styleOverrides: {
        root: {
          width: 42,
          height: 26,
          padding: 0,
          margin: 8,
        },
        switchBase: {
          padding: 1,
          '&.Mui-checked': {
            transform: 'translateX(16px)',
            color: '#fff',
            '& + .MuiSwitch-track': {
              backgroundColor: primaryColor,
              opacity: 1,
              border: 'none',
            },
          },
          '&.Mui-focusVisible .MuiSwitch-thumb': {
            color: primaryColor,
            border: '6px solid #fff',
          },
        },
        thumb: {
          width: 24,
          height: 24,
        },
        track: {
          borderRadius: 26 / 2,
          backgroundColor: 'rgba(255, 255, 255, 0.3)',
          opacity: 1,
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: '8px',
          boxShadow: '0 2px 10px 0 rgba(0, 0, 0, 0.1)',
        },
        standardError: {
          backgroundColor: alpha(errorColor, 0.15),
          color: alpha(errorColor, 0.9),
        },
        standardWarning: {
          backgroundColor: alpha(warningColor, 0.15),
          color: alpha(warningColor, 0.9),
        },
        standardInfo: {
          backgroundColor: alpha(infoColor, 0.15),
          color: alpha(infoColor, 0.9),
        },
        standardSuccess: {
          backgroundColor: alpha(successColor, 0.15),
          color: alpha(successColor, 0.9),
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(255, 255, 255, 0.08)',
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: alpha(darkColor, 0.95),
          border: `1px solid ${alpha('#fff', 0.1)}`,
          borderRadius: '8px',
          boxShadow: '0 4px 14px 0 rgba(0, 0, 0, 0.3)',
          padding: '10px 14px',
          fontSize: '12px',
        },
      },
    },
    MuiBadge: {
      styleOverrides: {
        badge: {
          fontWeight: 600,
        },
      },
    },
    MuiBackdrop: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(4px)',
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: '12px',
          boxShadow: '0 8px 30px rgba(0, 0, 0, 0.25)',
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: '10px',
          overflow: 'hidden',
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
        },
      },
    },
  },
});

export default theme;