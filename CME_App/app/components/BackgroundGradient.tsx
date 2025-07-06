import React from 'react';
import { LinearGradient, LinearGradientProps } from 'expo-linear-gradient';
import { APP_CONFIG } from '../utils/constants';

interface BackgroundGradientProps extends Omit<LinearGradientProps, 'colors'> {
  children: React.ReactNode;
}

export default function BackgroundGradient({ children, ...props }: BackgroundGradientProps) {
  return (
    <LinearGradient
      colors={[
        APP_CONFIG.colors.background.primary,
        APP_CONFIG.colors.background.secondary,
        APP_CONFIG.colors.background.tertiary
      ]}
      style={{ flex: 1 }}
      {...props}
    >
      {children}
    </LinearGradient>
  );
} 