import React from 'react';
import { View, StyleSheet } from 'react-native';
import LottieView from 'lottie-react-native';

interface ParticleBackgroundProps {
  children: React.ReactNode;
}

export default function ParticleBackground({ children }: ParticleBackgroundProps) {
  return (
    <View style={styles.container}>
      {/* Dark background color */}
      <View style={styles.darkBackground} />
      
      {/* Particle animation */}
      <LottieView
        source={require('../../assets/particles.json')}
        autoPlay
        loop
        style={styles.background}
        speed={0.5}
      />
      
      {/* Content overlay */}
      <View style={styles.content}>
        {children}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    position: 'relative',
  },
  darkBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#000000', // Deep black background
    zIndex: -2,
  },
  background: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: -1,
    opacity: 0.8, // Slightly reduce opacity to make particles more visible
  },
  content: {
    flex: 1,
    zIndex: 1,
  },
}); 