import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { StatusBar } from 'expo-status-bar';
import Welcome from './app/screens/Welcome';
import Landing from './app/screens/Landing';
import SearchScreen from './app/screens/SearchScreen';
import GraphSimulationScreen from './app/screens/GraphSimulationScreen';
import BlogScreen from './app/screens/BlogScreen';
import ChatbotScreen from './app/screens/ChatbotScreen';
import ErrorBoundary from './app/components/ErrorBoundary';
import { logger } from './app/utils/logger';
import type { RootStackParamList } from './app/types/navigation';

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  React.useEffect(() => {
    logger.info('App started successfully', { version: '1.0.0' }, 'App');
  }, []);

  return (
    <ErrorBoundary>
      <NavigationContainer
        onStateChange={(state) => {
          logger.debug('Navigation state changed', { state }, 'Navigation');
        }}
      >
        <StatusBar style="light" />
        <Stack.Navigator 
          initialRouteName="Welcome" 
          screenOptions={{ 
            headerShown: false,
            animation: 'slide_from_right',
            gestureEnabled: true,
          }}
        >
          <Stack.Screen name="Welcome" component={Welcome} />
          <Stack.Screen name="Landing" component={Landing} />
          <Stack.Screen name="Search" component={SearchScreen} />
          <Stack.Screen name="GraphSimulation" component={GraphSimulationScreen} />
          <Stack.Screen name="Blog" component={BlogScreen} />
          <Stack.Screen name="Chatbot" component={ChatbotScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    </ErrorBoundary>
  );
}
