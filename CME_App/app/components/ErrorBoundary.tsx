import React, { Component, ErrorInfo, ReactNode } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { APP_CONFIG } from '../utils/constants';
import { logger } from '../utils/logger';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    logger.error('Error boundary caught an error', { error, errorInfo }, 'ErrorBoundary');
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined });
  };

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.container}>
          <View style={styles.errorCard}>
            <Ionicons name="warning" size={64} color={APP_CONFIG.colors.warning} />
            <Text style={styles.title}>Oops! Something went wrong</Text>
            <Text style={styles.message}>
              We encountered an unexpected error. Please try again.
            </Text>
            {__DEV__ && this.state.error && (
              <Text style={styles.errorDetails}>
                {this.state.error.message}
              </Text>
            )}
            <TouchableOpacity style={styles.retryButton} onPress={this.handleRetry}>
              <Text style={styles.retryText}>Try Again</Text>
            </TouchableOpacity>
          </View>
        </View>
      );
    }

    return this.props.children;
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: APP_CONFIG.colors.background.primary,
    alignItems: 'center',
    justifyContent: 'center',
    padding: APP_CONFIG.spacing.lg,
  },
  errorCard: {
    backgroundColor: APP_CONFIG.colors.overlay.light,
    borderRadius: APP_CONFIG.borderRadius.lg,
    padding: APP_CONFIG.spacing.xl,
    alignItems: 'center',
    maxWidth: 400,
    ...APP_CONFIG.shadows.medium,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: APP_CONFIG.colors.text.primary,
    marginTop: APP_CONFIG.spacing.lg,
    marginBottom: APP_CONFIG.spacing.md,
    textAlign: 'center',
  },
  message: {
    fontSize: 16,
    color: APP_CONFIG.colors.text.secondary,
    textAlign: 'center',
    marginBottom: APP_CONFIG.spacing.lg,
    lineHeight: 24,
  },
  errorDetails: {
    fontSize: 12,
    color: APP_CONFIG.colors.text.tertiary,
    textAlign: 'center',
    marginBottom: APP_CONFIG.spacing.lg,
    fontFamily: 'monospace',
  },
  retryButton: {
    backgroundColor: APP_CONFIG.colors.success,
    paddingHorizontal: APP_CONFIG.spacing.xl,
    paddingVertical: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.md,
    ...APP_CONFIG.shadows.light,
  },
  retryText: {
    color: APP_CONFIG.colors.background.primary,
    fontSize: 16,
    fontWeight: 'bold',
  },
}); 