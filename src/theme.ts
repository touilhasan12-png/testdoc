export const T = {
  bg: '#060a12',
  ink: '#eef3fb',
  mute: '#93a4bf',
  red: '#e5483b',
  redDeep: '#8e1412',
  blue: '#43b0ff',
  cyan: '#8ff0ff',
  green: '#4fd1a5',
  gold: '#ffc857',
  grey: '#2c3a55',
  land: '#1f3150',
  dim: '#1d2c46',
  paper: '#e9e2d0',
  font: "'Helvetica Neue', Helvetica, Arial, 'Liberation Sans', 'DejaVu Sans', sans-serif",
};

export const FPS = 30;

// Thousands separators with a fixed decimal count (deterministic, locale-free).
export const fmtNum = (v: number, dec = 0): string => {
  const neg = v < 0;
  const [int, frac] = Math.abs(v).toFixed(dec).split('.');
  const grouped = int.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return (neg ? '-' : '') + grouped + (frac ? '.' + frac : '');
};
