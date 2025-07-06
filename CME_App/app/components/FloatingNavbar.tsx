import React, { useEffect, useRef } from 'react';
import { View, TouchableOpacity, StyleSheet, Dimensions, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { APP_CONFIG } from '../utils/constants';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';

const { width } = Dimensions.get('window');

interface FloatingNavbarProps {
  activeTab: string;
  onTabPress: (tab: string) => void;
}

interface TabItem {
  id: string;
  activeIcon: keyof typeof Ionicons.glyphMap;
  inactiveIcon: keyof typeof Ionicons.glyphMap;
}

export default function FloatingNavbar({ activeTab, onTabPress }: FloatingNavbarProps) {
  const tabs: TabItem[] = [
    { 
      id: 'home', 
      activeIcon: 'home',
      inactiveIcon: 'home-outline'
    },
    { 
      id: 'blog', 
      activeIcon: 'book',
      inactiveIcon: 'book-outline'
    },
    { 
      id: 'chatbot', 
      activeIcon: 'chatbubble-ellipses',
      inactiveIcon: 'chatbubble-outline'
    },
  ];

  const animatedValues = useRef(tabs.map(() => new Animated.Value(0))).current;
  const floatAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Floating animation
    Animated.loop(
      Animated.sequence([
        Animated.timing(floatAnim, {
          toValue: 1,
          duration: 3000,
          useNativeDriver: true,
        }),
        Animated.timing(floatAnim, {
          toValue: 0,
          duration: 3000,
          useNativeDriver: true,
        }),
      ])
    ).start();

    // Animate the active tab
    const activeIndex = tabs.findIndex(tab => tab.id === activeTab);
    if (activeIndex !== -1) {
      Animated.parallel([
        // Reset all tabs
        ...animatedValues.map((anim, index) => 
          Animated.timing(anim, {
            toValue: index === activeIndex ? 1 : 0,
            duration: 300,
            useNativeDriver: true,
          })
        )
      ]).start();
    }
  }, [activeTab]);

  const handleTabPress = (tabId: string) => {
    onTabPress(tabId);
  };

  const translateY = floatAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [0, -3],
  });

  return (
    <Animated.View 
      style={[
        styles.container,
        {
          transform: [{ translateY }],
        }
      ]}
    >
      <LinearGradient
        colors={[
          'rgba(0, 0, 0, 0.95)', // Dark with high transparency
          'rgba(26, 10, 46, 0.9)', // Purple with transparency
          'rgba(22, 33, 62, 0.85)'  // Blue with transparency
        ]}
        style={styles.gradientContainer}
      >
        <BlurView intensity={30} tint="dark" style={styles.blurContainer}>
          {tabs.map((tab, index) => {
            const isActive = activeTab === tab.id;
            const scale = animatedValues[index].interpolate({
              inputRange: [0, 1],
              outputRange: [1, 1.1],
            });
            
            const tabTranslateY = animatedValues[index].interpolate({
              inputRange: [0, 1],
              outputRange: [0, -4],
            });

            return (
              <Animated.View
                key={tab.id}
                style={[
                  styles.tabContainer,
                  {
                    transform: [{ scale }, { translateY: tabTranslateY }],
                  }
                ]}
              >
                <TouchableOpacity
                  style={[
                    styles.tab,
                    isActive && styles.activeTab,
                  ]}
                  onPress={() => handleTabPress(tab.id)}
                  activeOpacity={0.8}
                >
                  <Animated.View style={styles.iconContainer}>
                    <Ionicons 
                      name={isActive ? tab.activeIcon : tab.inactiveIcon} 
                      size={24} 
                      color={isActive ? APP_CONFIG.colors.secondary : APP_CONFIG.colors.text.secondary} 
                    />
                    {isActive && (
                      <Animated.View 
                        style={[
                          styles.activeIndicator,
                          {
                            opacity: animatedValues[index],
                            transform: [{
                              scale: animatedValues[index].interpolate({
                                inputRange: [0, 1],
                                outputRange: [0, 1],
                              })
                            }]
                          }
                        ]} 
                      />
                    )}
                  </Animated.View>
                </TouchableOpacity>
              </Animated.View>
            );
          })}
        </BlurView>
      </LinearGradient>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    zIndex: 1000,
  },
  gradientContainer: {
    borderRadius: APP_CONFIG.borderRadius.xl,
    overflow: 'hidden',
    ...APP_CONFIG.shadows.heavy,
  },
  blurContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingVertical: APP_CONFIG.spacing.sm,
    paddingHorizontal: APP_CONFIG.spacing.sm,
    borderRadius: APP_CONFIG.borderRadius.xl,
  },
  tabContainer: {
    alignItems: 'center',
  },
  tab: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: APP_CONFIG.spacing.sm,
    paddingHorizontal: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.lg,
    minWidth: 60,
  },
  activeTab: {
    backgroundColor: APP_CONFIG.colors.text.primary,
    ...APP_CONFIG.shadows.medium,
  },
  iconContainer: {
    position: 'relative',
    alignItems: 'center',
    justifyContent: 'center',
  },
  activeIndicator: {
    position: 'absolute',
    top: -4,
    right: -4,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: APP_CONFIG.colors.success,
    borderWidth: 2,
    borderColor: APP_CONFIG.colors.text.primary,
  },
}); 