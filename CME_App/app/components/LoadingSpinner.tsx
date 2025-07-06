import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet } from 'react-native';
import { APP_CONFIG } from '../utils/constants';

interface LoadingSpinnerProps {
  size?: 'small' | 'large';
  color?: string;
  text?: string;
  fullScreen?: boolean;
}

export default function LoadingSpinner({ 
  size = 'large', 
  color = APP_CONFIG.colors.success,
  text,
  fullScreen = false 
}: LoadingSpinnerProps) {
  const containerStyle = fullScreen ? styles.fullScreen : styles.container;
  
  return (
    <View style={containerStyle}>
      <ActivityIndicator size={size} color={color} />
      {text && <Text style={styles.text}>{text}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: APP_CONFIG.spacing.lg,
    alignItems: 'center',
    justifyContent: 'center',
  },
  fullScreen: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: APP_CONFIG.colors.background.primary,
  },
  text: {
    marginTop: APP_CONFIG.spacing.md,
    color: APP_CONFIG.colors.text.secondary,
    fontSize: 16,
    textAlign: 'center',
  },
}); 