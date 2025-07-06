export const APP_CONFIG = {
  name: 'SolarSim',
  version: '1.0.0',
  description: 'Solar CME Simulation & Monitoring System',
  colors: {
    primary: '#ffffff',
    secondary: '#1a1a1a',
    accent: '#00c6ff',
    success: '#00ff7f',
    warning: '#ff6b6b',
    info: '#00c6ff',
    background: {
      main: '#000000',
      secondary: '#1a1a1a',
      tertiary: '#2a2a2a',
    },
    text: {
      primary: '#ffffff',
      secondary: '#cccccc',
      tertiary: '#888888',
    },
    overlay: {
      light: 'rgba(255,255,255,0.04)',
      medium: 'rgba(255,255,255,0.08)',
      dark: 'rgba(255,255,255,0.12)',
    },
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  borderRadius: {
    sm: 8,
    md: 12,
    lg: 16,
    xl: 20,
    full: 999,
  },
  shadows: {
    light: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.2,
      shadowRadius: 4,
      elevation: 3,
    },
    medium: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.25,
      shadowRadius: 8,
      elevation: 6,
    },
    heavy: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 8 },
      shadowOpacity: 0.3,
      shadowRadius: 16,
      elevation: 12,
    },
  },
  animation: {
    duration: {
      fast: 200,
      normal: 300,
      slow: 500,
    },
    easing: {
      ease: 'ease',
      easeIn: 'ease-in',
      easeOut: 'ease-out',
      easeInOut: 'ease-in-out',
    },
  },
};

export const SENSOR_DATA = [
  {
    id: '1',
    name: 'SWIS',
    desc: 'Solar Wind Ion Spectrometer',
    reading: 'Proton Flux: 3.2×10⁸',
    trendUp: true,
    graph: require('../../assets/graph_01.png'),
  },
  {
    id: '2',
    name: 'ASPEX',
    desc: 'Aditya Solar Wind Particle Experiment',
    reading: 'Ion Count: 4.1×10⁷',
    trendUp: false,
    graph: require('../../assets/graph_02.png'),
  },
  {
    id: '3',
    name: 'VELC',
    desc: 'Visible Emission Line Coronagraph',
    reading: 'Intensity: 1.2×10⁶',
    trendUp: true,
    graph: require('../../assets/graph_03.png'),
  },
];

export const TRENDING_DATA = [
  { id: '1', name: 'Magnetic Field', change: '↑ Stable', trendUp: true },
  { id: '2', name: 'Solar Flare Activity', change: '↓ Low', trendUp: false },
  { id: '3', name: 'Particle Flux', change: '↑ Rising', trendUp: true },
];

export const TIME_FILTERS = ['1D', '1W', '1M', '1Y', '5Y', 'ALL'];

export const STATISTICS_DATA = [
  ['Open', '204.00'],
  ['High', '209.15'],
  ['Low', '202.12'],
  ['Volume', '1.3M'],
  ['Avg Volume', '1.1M'],
  ['Activity', 'Rising'],
];

export const CHART_DATA = {
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  datasets: [
    {
      data: [204.0, 207.5, 206.0, 208.0, 207.2, 206.8, 202.12],
    },
  ],
}; 