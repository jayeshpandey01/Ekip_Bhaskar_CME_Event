import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  StatusBar,
  Dimensions,
  Animated,
} from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import { Ionicons, MaterialIcons, FontAwesome5 } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { BlurView } from 'expo-blur';
import Header from '../components/Header';
import { APP_CONFIG, STATISTICS_DATA, CHART_DATA, TIME_FILTERS } from '../utils/constants';
import { logger } from '../utils/logger';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../types/navigation';
import ParticleBackground from '../components/ParticleBackground';

type Props = NativeStackScreenProps<RootStackParamList, 'GraphSimulation'>;

const screenWidth = Dimensions.get('window').width;

export default function GraphSimulationScreen({ navigation }: Props) {
  const [activeFilter, setActiveFilter] = useState('1D');
  const [activeTab, setActiveTab] = useState<'summary' | 'details'>('summary');
  const [fadeAnim] = useState(new Animated.Value(0));
  const [slideAnim] = useState(new Animated.Value(50));
  const [pulseAnim] = useState(new Animated.Value(1));
  const [chartAnim] = useState(new Animated.Value(0));

  useEffect(() => {
    // Entrance animations
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      }),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true,
      }),
    ]).start();

    // Chart animation
    Animated.timing(chartAnim, {
      toValue: 1,
      duration: 1500,
      useNativeDriver: true,
    }).start();

    // Pulse animation for live indicator
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.1,
          duration: 1500,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1500,
          useNativeDriver: true,
        }),
      ])
    ).start();
  }, []);

  const handleBackPress = () => {
    logger.info('Back button pressed', {}, 'GraphSimulationScreen');
    navigation.goBack();
  };

  const handleFilterPress = (filter: string) => {
    setActiveFilter(filter);
    logger.info('Filter changed', { filter }, 'GraphSimulationScreen');
  };

  const handleTabPress = (tab: 'summary' | 'details') => {
    setActiveTab(tab);
    logger.info('Tab changed', { tab }, 'GraphSimulationScreen');
  };

  // Enhanced solar physics data
  const solarData = {
    currentCME: {
      speed: '2,847 km/s',
      direction: 'Earth-directed',
      intensity: 'Strong (G3)',
      arrivalTime: '24-36 hours',
      confidence: '85%'
    },
    solarWind: {
      speed: '425 km/s',
      density: '8.2 particles/cm³',
      temperature: '1.2×10⁶ K',
      magneticField: '5.3 nT'
    },
    spaceWeather: {
      geomagneticActivity: 'Quiet',
      solarFlareProbability: '15%',
      auroraVisibility: 'Low',
      satelliteRisk: 'Minimal'
    }
  };

  // Enhanced chart data for different time periods
  const getChartData = (period: string) => {
    const baseData = [204.0, 207.5, 206.0, 208.0, 207.2, 206.8, 202.12];
    const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    
    switch (period) {
      case '1D':
        return {
          labels: ['00:00', '06:00', '12:00', '18:00', '24:00'],
          datasets: [{ data: [204, 206, 208, 207, 205] }]
        };
      case '1W':
        return { labels, datasets: [{ data: baseData }] };
      case '1M':
        return {
          labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
          datasets: [{ data: [205, 208, 206, 204] }]
        };
      default:
        return { labels, datasets: [{ data: baseData }] };
    }
  };

  return (
    <ParticleBackground>
      <SafeAreaView style={styles.safeArea}>
        <StatusBar barStyle="light-content" translucent backgroundColor="transparent" />
        <BlurView intensity={40} tint="dark" style={styles.blurTop} />
        
        <Header 
          title="Solar Activity Monitor" 
          onBackPress={handleBackPress}
          showBackButton={true}
        />

        <ScrollView style={styles.scrollContent} showsVerticalScrollIndicator={false}>
          {/* Enhanced Real-time Status Card */}
          <Animated.View 
            style={[
              styles.statusCard,
              {
                transform: [{ translateY: slideAnim }],
                opacity: fadeAnim,
              }
            ]}
          >
            <View style={styles.statusHeader}>
              <View style={styles.statusIcon}>
                <Ionicons name="radio" size={20} color={APP_CONFIG.colors.success} />
              </View>
              <Text style={styles.statusTitle}>Real-time Status</Text>
              <Animated.View 
                style={[
                  styles.statusIndicator,
                  {
                    transform: [{ scale: pulseAnim }],
                  }
                ]}
              >
                <View style={styles.liveDot} />
                <Text style={styles.liveText}>LIVE</Text>
              </Animated.View>
            </View>
            <View style={styles.statusDetails}>
              <View style={styles.statusRow}>
                <Ionicons name="checkmark-circle" size={16} color={APP_CONFIG.colors.success} />
                <Text style={styles.statusText}>Connected to Aditya-L1</Text>
              </View>
              <View style={styles.statusRow}>
                <Ionicons name="time-outline" size={16} color={APP_CONFIG.colors.text.secondary} />
                <Text style={styles.statusText}>Last update: 2 minutes ago</Text>
              </View>
            </View>
          </Animated.View>

          {/* Enhanced Time Filters */}
          <Animated.View 
            style={[
              styles.filters,
              {
                transform: [{ translateY: slideAnim }],
                opacity: fadeAnim,
              }
            ]}
          >
            {TIME_FILTERS.map((filter) => (
              <TouchableOpacity
                key={filter}
                style={activeFilter === filter ? styles.activeFilter : styles.filter}
                onPress={() => handleFilterPress(filter)}
              >
                <Text style={activeFilter === filter ? styles.activeFilterText : styles.filterText}>
                  {filter}
                </Text>
              </TouchableOpacity>
            ))}
          </Animated.View>

          {/* Enhanced Chart */}
          <Animated.View 
            style={[
              styles.graphCard,
              {
                transform: [{ scale: chartAnim }],
                opacity: chartAnim,
              }
            ]}
          >
            <View style={styles.chartHeader}>
              <View style={styles.chartIcon}>
                <Ionicons name="analytics" size={20} color={APP_CONFIG.colors.info} />
              </View>
              <View style={styles.chartTitleContainer}>
                <Text style={styles.chartTitle}>Solar Wind Particle Flux</Text>
                <Text style={styles.chartSubtitle}>Protons/cm²/s • SWIS Instrument</Text>
              </View>
            </View>
            <LineChart
              data={getChartData(activeFilter)}
              width={screenWidth - 48}
              height={220}
              yAxisSuffix=""
              chartConfig={{
                backgroundGradientFrom: 'transparent',
                backgroundGradientTo: 'transparent',
                color: (opacity = 1) => `rgba(0, 198, 255, ${opacity})`,
                strokeWidth: 3,
                decimalPlaces: 0,
                style: {
                  borderRadius: 16,
                },
                propsForDots: {
                  r: '4',
                  strokeWidth: '2',
                  stroke: APP_CONFIG.colors.success,
                },
                propsForBackgroundLines: {
                  strokeDasharray: '',
                  stroke: 'rgba(255, 255, 255, 0.1)',
                },
              }}
              bezier
              style={styles.chartStyle}
            />
          </Animated.View>

          {/* Enhanced CME Alert Card */}
          <Animated.View 
            style={[
              styles.alertCard,
              {
                transform: [{ translateY: slideAnim }],
                opacity: fadeAnim,
              }
            ]}
          >
            <View style={styles.alertHeader}>
              <View style={styles.alertIcon}>
                <MaterialIcons name="warning" size={24} color={APP_CONFIG.colors.warning} />
              </View>
              <Text style={styles.alertTitle}>CME Alert</Text>
              <View style={styles.alertBadge}>
                <Text style={styles.alertBadgeText}>G3</Text>
              </View>
            </View>
            <View style={styles.alertContent}>
              <View style={styles.alertRow}>
                <View style={styles.alertLabelContainer}>
                  <Ionicons name="speedometer" size={16} color={APP_CONFIG.colors.text.secondary} />
                  <Text style={styles.alertLabel}>Speed:</Text>
                </View>
                <Text style={styles.alertValue}>{solarData.currentCME.speed}</Text>
              </View>
              <View style={styles.alertRow}>
                <View style={styles.alertLabelContainer}>
                  <Ionicons name="compass" size={16} color={APP_CONFIG.colors.text.secondary} />
                  <Text style={styles.alertLabel}>Direction:</Text>
                </View>
                <Text style={styles.alertValue}>{solarData.currentCME.direction}</Text>
              </View>
              <View style={styles.alertRow}>
                <View style={styles.alertLabelContainer}>
                  <Ionicons name="time" size={16} color={APP_CONFIG.colors.text.secondary} />
                  <Text style={styles.alertLabel}>Arrival:</Text>
                </View>
                <Text style={styles.alertValue}>{solarData.currentCME.arrivalTime}</Text>
              </View>
              <View style={styles.alertRow}>
                <View style={styles.alertLabelContainer}>
                  <Ionicons name="trending-up" size={16} color={APP_CONFIG.colors.text.secondary} />
                  <Text style={styles.alertLabel}>Confidence:</Text>
                </View>
                <Text style={styles.alertValue}>{solarData.currentCME.confidence}</Text>
              </View>
            </View>
          </Animated.View>

          {/* Enhanced Solar Wind Parameters */}
          <Animated.View 
            style={[
              styles.parametersCard,
              {
                transform: [{ translateY: slideAnim }],
                opacity: fadeAnim,
              }
            ]}
          >
            <View style={styles.cardHeader}>
              <View style={styles.cardIcon}>
                <FontAwesome5 name="wind" size={20} color={APP_CONFIG.colors.info} />
              </View>
              <Text style={styles.cardTitle}>Solar Wind Parameters</Text>
            </View>
            <View style={styles.parametersGrid}>
              <View style={styles.parameterItem}>
                <View style={styles.parameterIcon}>
                  <Ionicons name="speedometer" size={16} color={APP_CONFIG.colors.success} />
                </View>
                <Text style={styles.parameterLabel}>Speed</Text>
                <Text style={styles.parameterValue}>{solarData.solarWind.speed}</Text>
                <Text style={styles.parameterUnit}>km/s</Text>
              </View>
              <View style={styles.parameterItem}>
                <View style={styles.parameterIcon}>
                  <Ionicons name="layers" size={16} color={APP_CONFIG.colors.warning} />
                </View>
                <Text style={styles.parameterLabel}>Density</Text>
                <Text style={styles.parameterValue}>{solarData.solarWind.density}</Text>
                <Text style={styles.parameterUnit}>particles/cm³</Text>
              </View>
              <View style={styles.parameterItem}>
                <View style={styles.parameterIcon}>
                  <Ionicons name="thermometer" size={16} color={APP_CONFIG.colors.warning} />
                </View>
                <Text style={styles.parameterLabel}>Temperature</Text>
                <Text style={styles.parameterValue}>{solarData.solarWind.temperature}</Text>
                <Text style={styles.parameterUnit}>Kelvin</Text>
              </View>
              <View style={styles.parameterItem}>
                <View style={styles.parameterIcon}>
                  <Ionicons name="magnet" size={16} color={APP_CONFIG.colors.info} />
                </View>
                <Text style={styles.parameterLabel}>B-Field</Text>
                <Text style={styles.parameterValue}>{solarData.solarWind.magneticField}</Text>
                <Text style={styles.parameterUnit}>nanoTesla</Text>
              </View>
            </View>
          </Animated.View>

          {/* Enhanced Space Weather Summary */}
          <Animated.View 
            style={[
              styles.weatherCard,
              {
                transform: [{ translateY: slideAnim }],
                opacity: fadeAnim,
              }
            ]}
          >
            <View style={styles.cardHeader}>
              <View style={styles.cardIcon}>
                <Ionicons name="partly-sunny" size={20} color={APP_CONFIG.colors.warning} />
              </View>
              <Text style={styles.cardTitle}>Space Weather Summary</Text>
            </View>
            <View style={styles.weatherGrid}>
              <View style={styles.weatherItem}>
                <View style={styles.weatherIcon}>
                  <Ionicons name="magnet" size={20} color={APP_CONFIG.colors.info} />
                </View>
                <Text style={styles.weatherLabel}>Geomagnetic</Text>
                <Text style={styles.weatherValue}>{solarData.spaceWeather.geomagneticActivity}</Text>
              </View>
              <View style={styles.weatherItem}>
                <View style={styles.weatherIcon}>
                  <Ionicons name="flash" size={20} color={APP_CONFIG.colors.warning} />
                </View>
                <Text style={styles.weatherLabel}>Flare Risk</Text>
                <Text style={styles.weatherValue}>{solarData.spaceWeather.solarFlareProbability}</Text>
              </View>
              <View style={styles.weatherItem}>
                <View style={styles.weatherIcon}>
                  <Ionicons name="eye" size={20} color={APP_CONFIG.colors.success} />
                </View>
                <Text style={styles.weatherLabel}>Aurora</Text>
                <Text style={styles.weatherValue}>{solarData.spaceWeather.auroraVisibility}</Text>
              </View>
              <View style={styles.weatherItem}>
                <View style={styles.weatherIcon}>
                  <Ionicons name="hardware-chip" size={20} color={APP_CONFIG.colors.text.secondary} />
                </View>
                <Text style={styles.weatherLabel}>Satellite Risk</Text>
                <Text style={styles.weatherValue}>{solarData.spaceWeather.satelliteRisk}</Text>
              </View>
            </View>
          </Animated.View>

          {/* Enhanced Summary / Details Tabs */}
          <Animated.View 
            style={[
              styles.tabRow,
              {
                transform: [{ translateY: slideAnim }],
                opacity: fadeAnim,
              }
            ]}
          >
            <TouchableOpacity 
              style={activeTab === 'summary' ? styles.tabActive : styles.tabInactive}
              onPress={() => handleTabPress('summary')}
            >
              <Ionicons 
                name="document-text" 
                size={16} 
                color={activeTab === 'summary' ? APP_CONFIG.colors.background.main : APP_CONFIG.colors.text.primary} 
              />
              <Text style={activeTab === 'summary' ? styles.tabTextActive : styles.tabTextInactive}>Summary</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={activeTab === 'details' ? styles.tabActive : styles.tabInactive}
              onPress={() => handleTabPress('details')}
            >
              <Ionicons 
                name="list" 
                size={16} 
                color={activeTab === 'details' ? APP_CONFIG.colors.background.main : APP_CONFIG.colors.text.primary} 
              />
              <Text style={activeTab === 'details' ? styles.tabTextActive : styles.tabTextInactive}>Details</Text>
            </TouchableOpacity>
          </Animated.View>

          {/* Content based on active tab */}
          <Animated.View 
            style={[
              activeTab === 'summary' ? styles.summaryContent : styles.detailsContent,
              {
                transform: [{ translateY: slideAnim }],
                opacity: fadeAnim,
              }
            ]}
          >
            {activeTab === 'summary' ? (
              <View>
                <View style={styles.contentHeader}>
                  <Ionicons name="information-circle" size={20} color={APP_CONFIG.colors.info} />
                  <Text style={styles.contentTitle}>Current Status</Text>
                </View>
                <Text style={styles.summaryText}>
                  Current solar activity shows moderate levels with one Earth-directed CME detected. 
                  Solar wind conditions are stable with no immediate threats to Earth's technology infrastructure. 
                  Aditya-L1 continues to monitor solar phenomena with high precision.
                </Text>
              </View>
            ) : (
              <View>
                <View style={styles.contentHeader}>
                  <Ionicons name="analytics" size={20} color={APP_CONFIG.colors.success} />
                  <Text style={styles.contentTitle}>Technical Details</Text>
                </View>
                <Text style={styles.detailsText}>
                  • SWIS instrument reports proton flux at 3.2×10⁸ particles/cm²/s{'\n'}
                  • ASPEX detects ion count of 4.1×10⁷ particles{'\n'}
                  • VELC observes stable coronal conditions{'\n'}
                  • No significant solar flares in the last 24 hours{'\n'}
                  • Geomagnetic field remains quiet (Kp index: 2){'\n'}
                  • Next solar storm probability: 15% in next 48 hours
                </Text>
              </View>
            )}
          </Animated.View>

          {/* Enhanced Footer Buttons */}
          <Animated.View 
            style={[
              styles.actions,
              {
                transform: [{ translateY: slideAnim }],
                opacity: fadeAnim,
              }
            ]}
          >
            <TouchableOpacity style={styles.blogBtn}>
              <View style={styles.btnContent}>
                <Ionicons name="book" size={16} color={APP_CONFIG.colors.text.primary} />
                <Text style={styles.blogText}>Read Analysis</Text>
              </View>
            </TouchableOpacity>
            <TouchableOpacity style={styles.paramBtn}>
              <View style={styles.btnContent}>
                <Ionicons name="settings" size={16} color={APP_CONFIG.colors.background.main} />
                <Text style={styles.paramText}>Parameters</Text>
              </View>
            </TouchableOpacity>
          </Animated.View>

          {/* Enhanced Footer Info */}
          <Animated.View 
            style={[
              styles.footer,
              {
                transform: [{ translateY: slideAnim }],
                opacity: fadeAnim,
              }
            ]}
          >
            <View style={styles.footerHeader}>
              <Ionicons name="information-circle-outline" size={16} color={APP_CONFIG.colors.text.secondary} />
              <Text style={styles.footerTitle}>Latest Updates</Text>
            </View>
            <Text style={styles.footerText}>Latest Update: CME detected near equator (9:12 AM IST)</Text>
            <Text style={styles.footerText}>Prediction: High possibility of magnetic disturbance in next 24h</Text>
            <Text style={styles.footerText}>Data Source: Aditya-L1 • ISRO</Text>
          </Animated.View>
        </ScrollView>

      </SafeAreaView>
    </ParticleBackground>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1 },
  blurTop: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: 30,
    zIndex: 10,
    borderBottomWidth: 1,
    borderBottomColor: APP_CONFIG.colors.overlay.dark,
  },
  container: {
    paddingHorizontal: APP_CONFIG.spacing.lg,
    paddingBottom: 60,
  },
  scrollContent: {
    paddingHorizontal: APP_CONFIG.spacing.lg,
    paddingBottom: 60,
  },
  filters: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: APP_CONFIG.spacing.md,
  },
  filter: {
    paddingVertical: APP_CONFIG.spacing.xs,
    paddingHorizontal: APP_CONFIG.spacing.sm,
    borderRadius: APP_CONFIG.borderRadius.full,
    backgroundColor: APP_CONFIG.colors.overlay.light,
    ...APP_CONFIG.shadows.light,
  },
  filterText: {
    color: APP_CONFIG.colors.text.primary,
  },
  activeFilter: {
    paddingVertical: APP_CONFIG.spacing.xs,
    paddingHorizontal: APP_CONFIG.spacing.sm,
    borderRadius: APP_CONFIG.borderRadius.full,
    backgroundColor: APP_CONFIG.colors.text.primary,
    ...APP_CONFIG.shadows.medium,
  },
  activeFilterText: {
    color: APP_CONFIG.colors.background.main,
    fontWeight: 'bold',
  },
  graphCard: {
    alignItems: 'center',
    padding: APP_CONFIG.spacing.sm,
    marginBottom: APP_CONFIG.spacing.lg,
  },
  chartHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: APP_CONFIG.spacing.md,
  },
  chartIcon: {
    backgroundColor: APP_CONFIG.colors.overlay.light,
    padding: APP_CONFIG.spacing.xs,
    borderRadius: APP_CONFIG.borderRadius.sm,
    marginRight: APP_CONFIG.spacing.sm,
  },
  chartTitleContainer: {
    alignItems: 'center',
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: APP_CONFIG.colors.text.primary,
  },
  chartSubtitle: {
    fontSize: 14,
    color: APP_CONFIG.colors.text.secondary,
  },
  chartStyle: {
    borderRadius: APP_CONFIG.borderRadius.lg,
    ...APP_CONFIG.shadows.medium,
  },
  statusCard: {
    backgroundColor: APP_CONFIG.colors.overlay.light,
    padding: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.md,
    marginBottom: APP_CONFIG.spacing.lg,
    ...APP_CONFIG.shadows.light,
  },
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: APP_CONFIG.spacing.sm,
  },
  statusIcon: {
    backgroundColor: APP_CONFIG.colors.overlay.dark,
    padding: APP_CONFIG.spacing.xs,
    borderRadius: APP_CONFIG.borderRadius.sm,
  },
  statusTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: APP_CONFIG.colors.text.primary,
    marginLeft: APP_CONFIG.spacing.sm,
    flex: 1,
  },
  statusIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  liveDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: APP_CONFIG.colors.success,
    marginRight: APP_CONFIG.spacing.xs,
  },
  liveText: {
    fontSize: 12,
    color: APP_CONFIG.colors.success,
    fontWeight: 'bold',
  },
  statusDetails: {
    gap: APP_CONFIG.spacing.xs,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusText: {
    fontSize: 14,
    color: APP_CONFIG.colors.text.secondary,
    marginLeft: APP_CONFIG.spacing.xs,
  },
  tabRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: APP_CONFIG.spacing.lg,
  },
  tabActive: {
    backgroundColor: APP_CONFIG.colors.text.primary,
    paddingVertical: APP_CONFIG.spacing.sm,
    paddingHorizontal: APP_CONFIG.spacing.lg,
    borderRadius: APP_CONFIG.borderRadius.full,
    marginRight: APP_CONFIG.spacing.sm,
    flexDirection: 'row',
    alignItems: 'center',
    ...APP_CONFIG.shadows.medium,
  },
  tabInactive: {
    borderWidth: 1,
    borderColor: APP_CONFIG.colors.text.primary,
    paddingVertical: APP_CONFIG.spacing.sm,
    paddingHorizontal: APP_CONFIG.spacing.lg,
    borderRadius: APP_CONFIG.borderRadius.full,
    backgroundColor: APP_CONFIG.colors.overlay.light,
    flexDirection: 'row',
    alignItems: 'center',
    ...APP_CONFIG.shadows.light,
  },
  tabTextActive: {
    color: APP_CONFIG.colors.background.main,
    fontWeight: 'bold',
    marginLeft: APP_CONFIG.spacing.xs,
  },
  tabTextInactive: {
    color: APP_CONFIG.colors.text.primary,
    marginLeft: APP_CONFIG.spacing.xs,
  },
  summaryContent: {
    backgroundColor: APP_CONFIG.colors.overlay.light,
    padding: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.md,
    marginBottom: APP_CONFIG.spacing.lg,
    ...APP_CONFIG.shadows.light,
  },
  detailsContent: {
    backgroundColor: APP_CONFIG.colors.overlay.light,
    padding: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.md,
    marginBottom: APP_CONFIG.spacing.lg,
    ...APP_CONFIG.shadows.light,
  },
  contentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: APP_CONFIG.spacing.sm,
  },
  contentTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: APP_CONFIG.colors.text.primary,
    marginLeft: APP_CONFIG.spacing.sm,
  },
  summaryText: {
    color: APP_CONFIG.colors.text.secondary,
    fontSize: 14,
    lineHeight: 20,
  },
  detailsText: {
    color: APP_CONFIG.colors.text.secondary,
    fontSize: 14,
    lineHeight: 20,
  },
  alertCard: {
    backgroundColor: APP_CONFIG.colors.overlay.light,
    padding: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.md,
    marginBottom: APP_CONFIG.spacing.lg,
    borderLeftWidth: 4,
    borderLeftColor: APP_CONFIG.colors.warning,
    ...APP_CONFIG.shadows.light,
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: APP_CONFIG.spacing.md,
  },
  alertIcon: {
    backgroundColor: APP_CONFIG.colors.overlay.dark,
    padding: APP_CONFIG.spacing.xs,
    borderRadius: APP_CONFIG.borderRadius.sm,
  },
  alertTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: APP_CONFIG.colors.text.primary,
    marginLeft: APP_CONFIG.spacing.sm,
    flex: 1,
  },
  alertBadge: {
    backgroundColor: APP_CONFIG.colors.warning,
    paddingHorizontal: APP_CONFIG.spacing.sm,
    paddingVertical: APP_CONFIG.spacing.xs,
    borderRadius: APP_CONFIG.borderRadius.sm,
  },
  alertBadgeText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: APP_CONFIG.colors.secondary,
  },
  alertContent: {
    gap: APP_CONFIG.spacing.sm,
  },
  alertRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  alertLabelContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  alertLabel: {
    fontSize: 14,
    color: APP_CONFIG.colors.text.secondary,
    marginLeft: APP_CONFIG.spacing.xs,
  },
  alertValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: APP_CONFIG.colors.text.primary,
  },
  parametersCard: {
    backgroundColor: APP_CONFIG.colors.overlay.light,
    padding: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.md,
    marginBottom: APP_CONFIG.spacing.lg,
    ...APP_CONFIG.shadows.light,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: APP_CONFIG.spacing.md,
  },
  cardIcon: {
    backgroundColor: APP_CONFIG.colors.overlay.dark,
    padding: APP_CONFIG.spacing.xs,
    borderRadius: APP_CONFIG.borderRadius.sm,
    marginRight: APP_CONFIG.spacing.sm,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: APP_CONFIG.colors.text.primary,
  },
  parametersGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  parameterItem: {
    width: '48%',
    alignItems: 'center',
    padding: APP_CONFIG.spacing.sm,
    marginBottom: APP_CONFIG.spacing.sm,
  },
  parameterIcon: {
    backgroundColor: APP_CONFIG.colors.overlay.dark,
    padding: APP_CONFIG.spacing.xs,
    borderRadius: APP_CONFIG.borderRadius.sm,
    marginBottom: APP_CONFIG.spacing.xs,
  },
  parameterLabel: {
    fontSize: 12,
    color: APP_CONFIG.colors.text.secondary,
    marginBottom: APP_CONFIG.spacing.xs,
  },
  parameterValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: APP_CONFIG.colors.text.primary,
  },
  parameterUnit: {
    fontSize: 10,
    color: APP_CONFIG.colors.text.tertiary,
    marginTop: APP_CONFIG.spacing.xs,
  },
  weatherCard: {
    backgroundColor: APP_CONFIG.colors.overlay.light,
    padding: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.md,
    marginBottom: APP_CONFIG.spacing.lg,
    ...APP_CONFIG.shadows.light,
  },
  weatherGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  weatherItem: {
    width: '48%',
    alignItems: 'center',
    padding: APP_CONFIG.spacing.sm,
    marginBottom: APP_CONFIG.spacing.sm,
  },
  weatherIcon: {
    backgroundColor: APP_CONFIG.colors.overlay.dark,
    padding: APP_CONFIG.spacing.xs,
    borderRadius: APP_CONFIG.borderRadius.sm,
    marginBottom: APP_CONFIG.spacing.xs,
  },
  weatherLabel: {
    fontSize: 12,
    color: APP_CONFIG.colors.text.secondary,
    marginBottom: APP_CONFIG.spacing.xs,
  },
  weatherValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: APP_CONFIG.colors.text.primary,
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: APP_CONFIG.spacing.lg,
  },
  btnContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  blogBtn: {
    flex: 1,
    backgroundColor: '#f88379',
    padding: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.md,
    marginRight: APP_CONFIG.spacing.sm,
    ...APP_CONFIG.shadows.medium,
  },
  blogText: {
    textAlign: 'center',
    color: APP_CONFIG.colors.text.primary,
    fontWeight: 'bold',
    marginLeft: APP_CONFIG.spacing.xs,
  },
  paramBtn: {
    flex: 1,
    backgroundColor: APP_CONFIG.colors.success,
    padding: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.md,
    ...APP_CONFIG.shadows.medium,
  },
  paramText: {
    textAlign: 'center',
    color: APP_CONFIG.colors.background.main,
    fontWeight: 'bold',
    marginLeft: APP_CONFIG.spacing.xs,
  },
  footer: {
    backgroundColor: APP_CONFIG.colors.overlay.light,
    padding: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.md,
    marginBottom: APP_CONFIG.spacing.lg,
    ...APP_CONFIG.shadows.light,
  },
  footerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: APP_CONFIG.spacing.sm,
  },
  footerTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: APP_CONFIG.colors.text.primary,
    marginLeft: APP_CONFIG.spacing.xs,
  },
  footerText: {
    color: APP_CONFIG.colors.text.secondary,
    fontSize: 13,
    marginBottom: APP_CONFIG.spacing.xs,
    lineHeight: 18,
  },
});