import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { APP_CONFIG } from '../utils/constants';

interface HeaderProps {
  title: string;
  onBackPress?: () => void;
  showBackButton?: boolean;
  rightComponent?: React.ReactNode;
}

export default function Header({ 
  title, 
  onBackPress, 
  showBackButton = false,
  rightComponent 
}: HeaderProps) {
  return (
    <View style={styles.header}>
      {showBackButton ? (
        <TouchableOpacity onPress={onBackPress} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={APP_CONFIG.colors.text.primary} />
        </TouchableOpacity>
      ) : (
        <View style={{ width: 24 }} />
      )}
      
      <Text style={styles.title}>{title}</Text>
      
      {rightComponent || <View style={{ width: 24 }} />}
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginVertical: APP_CONFIG.spacing.lg,
  },
  backButton: {
    padding: APP_CONFIG.spacing.xs,
    borderRadius: APP_CONFIG.borderRadius.sm,
  },
  title: {
    fontSize: 20,
    color: APP_CONFIG.colors.text.primary,
    fontWeight: '600',
  },
}); 