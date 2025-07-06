// screens/SearchScreen.tsx
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  StatusBar,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import data from '../../assets/searchData.json';
import { APP_CONFIG } from '../utils/constants';
import { logger } from '../utils/logger';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../types/navigation';
import ParticleBackground from '../components/ParticleBackground';

type Props = NativeStackScreenProps<RootStackParamList, 'Search'>;

export default function SearchScreen({ navigation }: Props) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);

  const handleSearch = (text: string) => {
    setQuery(text);
    logger.debug('Search query updated', { query: text }, 'SearchScreen');
    
    const filtered = data.filter((item) =>
      item.name.toLowerCase().includes(text.toLowerCase()) ||
      item.description.toLowerCase().includes(text.toLowerCase())
    );
    setResults(filtered);
    logger.info('Search results updated', { count: filtered.length }, 'SearchScreen');
  };

  const handleResultPress = (item: any) => {
    logger.info('Search result selected', { item }, 'SearchScreen');
    // TODO: Navigate to the appropriate screen based on item.path
    // navigation.navigate(item.path as keyof RootStackParamList);
  };

  const handleBackPress = () => {
    logger.info('Back button pressed', {}, 'SearchScreen');
    navigation.goBack();
  };

  const renderItem = ({ item }: { item: any }) => (
    <TouchableOpacity style={styles.result} onPress={() => handleResultPress(item)}>
      <Text style={styles.emoji}>
        {item.type === 'graph' ? '📈' : item.type === 'blog' ? '📝' : '📁'}
      </Text>
      <View style={styles.resultContent}>
        <Text style={styles.name}>{item.name}</Text>
        <Text style={styles.desc}>{item.description}</Text>
      </View>
      <Ionicons name="chevron-forward" size={20} color={APP_CONFIG.colors.text.secondary} />
    </TouchableOpacity>
  );

  return (
    <ParticleBackground>
      <SafeAreaView style={[styles.safeArea, { backgroundColor: 'transparent' }]}>
        <StatusBar barStyle="light-content" translucent backgroundColor="transparent" />
        
        <View style={styles.searchBar}>
          <TouchableOpacity onPress={handleBackPress} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color={APP_CONFIG.colors.text.primary} />
          </TouchableOpacity>
          <TextInput
            value={query}
            onChangeText={handleSearch}
            placeholder="Search for CME data..."
            placeholderTextColor={APP_CONFIG.colors.text.tertiary}
            style={styles.input}
            autoFocus
          />
        </View>
        
        <FlatList
          data={results}
          keyExtractor={(item) => item.name}
          renderItem={renderItem}
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
          ListEmptyComponent={
            query ? (
              <View style={styles.emptyState}>
                <Ionicons name="search" size={48} color={APP_CONFIG.colors.text.tertiary} />
                <Text style={styles.emptyText}>No results found for "{query}"</Text>
                <Text style={styles.emptySubtext}>Try different keywords</Text>
              </View>
            ) : (
              <View style={styles.emptyState}>
                <Ionicons name="search-outline" size={48} color={APP_CONFIG.colors.text.tertiary} />
                <Text style={styles.emptyText}>Search for CME data, sensors, or articles</Text>
                <Text style={styles.emptySubtext}>Start typing to see results</Text>
              </View>
            )
          }
        />
      </SafeAreaView>
    </ParticleBackground>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
  },
  safeArea: {
    flex: 1,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: APP_CONFIG.colors.secondary,
    padding: APP_CONFIG.spacing.md,
    margin: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.xl,
    ...APP_CONFIG.shadows.medium,
  },
  backButton: {
    marginRight: APP_CONFIG.spacing.sm,
    padding: APP_CONFIG.spacing.xs,
  },
  input: {
    flex: 1,
    color: APP_CONFIG.colors.text.primary,
    fontSize: 16,
  },
  listContainer: { 
    padding: APP_CONFIG.spacing.md,
  },
  result: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: APP_CONFIG.colors.secondary,
    padding: APP_CONFIG.spacing.md,
    marginBottom: APP_CONFIG.spacing.sm,
    borderRadius: APP_CONFIG.borderRadius.xl,
    ...APP_CONFIG.shadows.light,
  },
  emoji: {
    fontSize: 24,
    marginRight: APP_CONFIG.spacing.md,
  },
  resultContent: {
    flex: 1,
  },
  name: {
    color: APP_CONFIG.colors.text.primary,
    fontWeight: 'bold',
    fontSize: 16,
    marginBottom: APP_CONFIG.spacing.xs,
  },
  desc: {
    color: APP_CONFIG.colors.text.secondary,
    fontSize: 14,
    lineHeight: 20,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: APP_CONFIG.spacing.xxl,
  },
  emptyText: {
    color: APP_CONFIG.colors.text.secondary,
    fontSize: 16,
    textAlign: 'center',
    marginTop: APP_CONFIG.spacing.md,
    marginBottom: APP_CONFIG.spacing.xs,
  },
  emptySubtext: {
    color: APP_CONFIG.colors.text.tertiary,
    fontSize: 14,
    textAlign: 'center',
  },
});
