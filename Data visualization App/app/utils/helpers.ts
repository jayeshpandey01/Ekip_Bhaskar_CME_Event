import { Dimensions } from 'react-native';

const { width, height } = Dimensions.get('window');

export const screenDimensions = {
  width,
  height,
};

export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

export const formatPercentage = (value: number): string => {
  return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
};

export const getTrendIcon = (trendUp: boolean): 'trending-up' | 'trending-down' => {
  return trendUp ? 'trending-up' : 'trending-down';
};

export const getTrendColor = (trendUp: boolean, colors: any): string => {
  return trendUp ? colors.success : colors.warning;
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}; 