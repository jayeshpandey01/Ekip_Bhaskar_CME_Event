import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { FontAwesome } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../types/navigation';
import { APP_CONFIG } from '../utils/constants';
import { logger } from '../utils/logger';
import ParticleBackground from '../components/ParticleBackground';

const Welcome = () => {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  const handleStartExploring = () => {
    logger.info('Start exploring button pressed', {}, 'Welcome');
    navigation.navigate('Landing');
  };

  const handleGoogleSignIn = () => {
    logger.info('Google sign in pressed', {}, 'Welcome');
    // TODO: Implement Google sign in
  };

  const handleFacebookSignIn = () => {
    logger.info('Facebook sign in pressed', {}, 'Welcome');
    // TODO: Implement Facebook sign in
  };

  return (
    <ParticleBackground>
      <View style={styles.contentWrapper}>
        <Text style={styles.logoText}>{APP_CONFIG.name}</Text>

        <Text style={styles.mainHeading}>
          <Text style={styles.bold}>Simulate</Text> Solar {'\n'}
          <Text style={styles.bold}>Events</Text> and Explore {'\n'}
          Real-Time <Text style={styles.bold}>CME Data</Text>
        </Text>

        <Text style={styles.subText}>
          Experience our visualization of Coronal Mass Ejections (CMEs) based on real particle data from the SWIS-ASPEX payload aboard Aditya-L1. Dive into interactive solar event simulations, insights, and tools designed for space weather researchers and enthusiasts.
        </Text>

        <View style={styles.authRow}>
          <TouchableOpacity style={styles.iconButton} onPress={handleGoogleSignIn}>
            <FontAwesome name="google" size={20} color={APP_CONFIG.colors.text.primary} />
          </TouchableOpacity>
          <TouchableOpacity style={styles.iconButton} onPress={handleFacebookSignIn}>
            <FontAwesome name="facebook" size={20} color={APP_CONFIG.colors.text.primary} />
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.letsGo}
            onPress={handleStartExploring}
          >
            <Text style={styles.letsGoText}>Start Exploring</Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.signupText}>
          Don't have an account? <Text style={styles.link}>Sign Up</Text>
        </Text>
      </View>
    </ParticleBackground>
  );
};

export default Welcome;

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  contentWrapper: {
    flex: 1,
    padding: APP_CONFIG.spacing.lg,
    justifyContent: 'flex-end',
  },
  logoText: {
    fontSize: 32,
    color: APP_CONFIG.colors.text.primary,
    fontWeight: 'bold',
    marginBottom: APP_CONFIG.spacing.xl,
    fontFamily: 'System',
  },
  mainHeading: {
    fontSize: 28,
    color: APP_CONFIG.colors.text.secondary,
    marginBottom: APP_CONFIG.spacing.lg,
    lineHeight: 36,
  },
  bold: {
    color: APP_CONFIG.colors.text.primary,
    fontWeight: 'bold',
  },
  subText: {
    color: APP_CONFIG.colors.text.tertiary,
    fontSize: 14,
    marginBottom: APP_CONFIG.spacing.xl,
    lineHeight: 20,
  },
  authRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: APP_CONFIG.spacing.sm,
    alignItems: 'center',
  },
  iconButton: {
    backgroundColor: APP_CONFIG.colors.secondary,
    padding: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.xl,
    ...APP_CONFIG.shadows.medium,
  },
  letsGo: {
    backgroundColor: APP_CONFIG.colors.text.primary,
    width: '70%',
    alignItems: 'center',
    paddingVertical: APP_CONFIG.spacing.md,
    paddingHorizontal: APP_CONFIG.spacing.xl,
    borderRadius: APP_CONFIG.borderRadius.xl,
    ...APP_CONFIG.shadows.heavy,
  },
  letsGoText: {
    color: APP_CONFIG.colors.secondary,
    fontWeight: 'bold',
    fontSize: 16,
  },
  signupText: {
    color: APP_CONFIG.colors.text.tertiary,
    marginTop: APP_CONFIG.spacing.xl,
    textAlign: 'center',
    fontSize: 14,
  },
  link: {
    color: APP_CONFIG.colors.text.primary,
    fontWeight: 'bold',
  },
});
