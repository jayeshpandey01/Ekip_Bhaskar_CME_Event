import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  StatusBar,
  KeyboardAvoidingView,
  Platform,
  Alert,
  Image,
  Linking,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import LottieView from 'lottie-react-native';
import { APP_CONFIG } from '../utils/constants';
import { API_CONFIG, isApiConfigured, buildSearchUrl } from '../utils/apiConfig';
import { logger } from '../utils/logger';
import Header from '../components/Header';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../types/navigation';
import { localSolarLLM } from '../utils/localLLM';
import { cleanMarkdown, formatSearchResults } from '../utils/textFormatter';

type Props = NativeStackScreenProps<RootStackParamList, 'Chatbot'>;

interface SearchResult {
  title: string;
  snippet: string;
  link: string;
  imageUrl?: string;
  imageWidth?: number;
  imageHeight?: number;
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
  source?: 'web' | 'model' | 'local_llm';
  searchResults?: SearchResult[];
}

type ResponseMode = 'web' | 'model';

const quickQuestions = [
  'What is a CME?',
  'How does Aditya-L1 work?',
  'What are solar flares?',
  'How to read solar data?',
];

export default function ChatbotScreen({ navigation }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: isApiConfigured() 
        ? 'Hello! I\'m your Solar AI assistant. I can help you with web search results or generate responses using AI models. Choose your preferred mode below.'
        : 'Hello! I\'m your Solar AI assistant. Please configure your API keys in apiConfig.ts to enable web search and AI model features.',
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [responseMode, setResponseMode] = useState<ResponseMode>('model');

  const handleSendMessage = async () => {
    if (inputText.trim() === '') return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      let response: string;
      let source: 'web' | 'model' | 'local_llm';
      let searchResults: SearchResult[] | undefined;

      if (responseMode === 'web') {
        if (!isApiConfigured()) {
          response = 'Web search requires API configuration. Please set up your Google Search API key.';
          source = 'web';
        } else {
          const searchData = await performWebSearch(inputText);
          response = searchData.responseText;
          searchResults = searchData.results;
          source = 'web';
        }
      } else {
        if (!isApiConfigured()) {
          response = generateLocalResponse(inputText);
          source = 'local_llm';
        } else {
          response = await generateModelResponse(inputText);
          source = 'model';
        }
      }

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response,
        isUser: false,
        timestamp: new Date(),
        source,
        searchResults,
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      logger.error('Error generating response', { error }, 'ChatbotScreen');
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        isUser: false,
        timestamp: new Date(),
        source: responseMode,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }

    logger.info('Message sent', { text: inputText, mode: responseMode }, 'ChatbotScreen');
  };

  const performWebSearch = async (query: string): Promise<{ responseText: string; results: SearchResult[] }> => {
    try {
      const url = buildSearchUrl(query, 'image');
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Web search failed: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.items && data.items.length > 0) {
        const results: SearchResult[] = data.items.slice(0, API_CONFIG.WEB_SEARCH.max_results).map((item: any) => ({
          title: cleanMarkdown(item.title),
          snippet: cleanMarkdown(item.snippet || item.title),
          link: item.link,
          imageUrl: item.image?.thumbnailLink || item.image?.src || item.link,
          imageWidth: item.image?.thumbnailWidth || 150,
          imageHeight: item.image?.thumbnailHeight || 150,
        }));
        
        // Use the new formatting utility
        const responseText = formatSearchResults(query, results);
        
        return { responseText, results };
      } else {
        return { 
          responseText: `No web search results found for "${query}". Try rephrasing your question.`,
          results: []
        };
      }
    } catch (error) {
      logger.error('Web search error', { error }, 'ChatbotScreen');
      return {
        responseText: 'Web search is currently unavailable. Please try the AI model mode instead.',
        results: []
      };
    }
  };

  const generateModelResponse = async (query: string): Promise<string> => {
    try {
      logger.info('Starting model inference', { query }, 'ChatbotScreen');
      
      // First, try the local LLM for immediate response
      const localResponse = localSolarLLM.generateResponse(query);
      logger.info('Local LLM response generated', { 
        confidence: localResponse.confidence, 
        source: localResponse.source 
      }, 'ChatbotScreen');
      
      // If local LLM has high confidence, use it
      if (localResponse.confidence >= 0.8) {
        return localResponse.text;
      }
      
      // Otherwise, try the online model as fallback
      logger.info('Attempting online model as fallback', {}, 'ChatbotScreen');
      
      // Prepare the request payload
      const payload = {
        inputs: query,
        parameters: {
          ...API_CONFIG.MODEL_PARAMS,
          return_full_text: false, // Only return the generated part
        },
        options: {
          wait_for_model: true, // Wait for model to load if needed
        },
      };

      // Create a timeout promise
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), API_CONFIG.REQUEST_TIMEOUT);
      });

      // Create the fetch promise
      const fetchPromise = fetch(API_CONFIG.HUGGING_FACE.MODEL_URL, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${API_CONFIG.HUGGING_FACE.API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      // Race between fetch and timeout
      const response = await Promise.race([fetchPromise, timeoutPromise]) as Response;
      
      logger.info('Model API response status', { status: response.status }, 'ChatbotScreen');
      
      if (!response.ok) {
        const errorText = await response.text();
        logger.error('Model API error response', { 
          status: response.status, 
          statusText: response.statusText,
          errorText 
        }, 'ChatbotScreen');
        throw new Error(`Model inference failed: ${response.status} - ${errorText}`);
      }
      
      const data = await response.json();
      logger.info('Model API response data', { dataType: typeof data, hasData: !!data }, 'ChatbotScreen');
      
      // Handle different response formats
      let generatedText = '';
      
      if (Array.isArray(data) && data.length > 0) {
        // Format: [{ generated_text: "..." }]
        if (data[0].generated_text) {
          generatedText = data[0].generated_text;
        } else if (data[0].text) {
          generatedText = data[0].text;
        }
      } else if (typeof data === 'string') {
        // Format: "generated text"
        generatedText = data;
      } else if (data && typeof data === 'object') {
        // Format: { generated_text: "..." }
        if (data.generated_text) {
          generatedText = data.generated_text;
        } else if (data.text) {
          generatedText = data.text;
        }
      }
      
      // Clean up the generated text
      if (generatedText) {
        // Remove the input query from the beginning if it's there
        const cleanText = generatedText.replace(query, '').trim();
        if (cleanText.length > 10) {
          return cleanText;
        } else {
          return generatedText;
        }
      } else {
        logger.warn('No generated text found in response', { data }, 'ChatbotScreen');
        // Fallback to local response generation
        return localResponse.text;
      }
      
    } catch (error) {
      logger.error('Model inference error', { 
        error: error instanceof Error ? error.message : error,
        stack: error instanceof Error ? error.stack : undefined
      }, 'ChatbotScreen');
      
      // Fallback to local LLM response
      const localResponse = localSolarLLM.generateResponse(query);
      return localResponse.text;
    }
  };

  const generateLocalResponse = (query: string): string => {
    const input = query.toLowerCase();
    
    // Enhanced local "small LLM" for solar physics
    const responses = {
      // CME and Solar Events
      cme: [
        'A Coronal Mass Ejection (CME) is a massive burst of solar wind and magnetic fields rising above the solar corona or being released into space. CMEs can affect Earth\'s magnetic field and cause geomagnetic storms that may impact satellites, power grids, and communication systems.',
        'CMEs are among the most powerful solar events, releasing billions of tons of plasma into space at speeds up to 3,000 km/s. They can cause beautiful auroras but also disrupt technology on Earth.',
        'Coronal Mass Ejections occur when the Sun\'s magnetic field becomes unstable and releases huge amounts of charged particles. These events are closely monitored by space weather scientists.'
      ],
      
      // Aditya-L1 Mission
      aditya: [
        'Aditya-L1 is India\'s first space-based observatory to study the Sun. It carries seven payloads to observe the photosphere, chromosphere, and corona using electromagnetic and particle detectors. The mission aims to understand solar dynamics and space weather.',
        'The Aditya-L1 mission is positioned at the L1 Lagrange point, about 1.5 million km from Earth, providing continuous observation of the Sun without occultation.',
        'Aditya-L1\'s instruments include SWIS, ASPEX, VELC, and others that help us understand solar wind, particle acceleration, and coronal heating processes.'
      ],
      
      // Solar Flares
      solar_flare: [
        'Solar flares are sudden, intense bursts of radiation from the Sun\'s surface. They can affect radio communications, power grids, and navigation systems on Earth. Flares are classified by their X-ray brightness: A, B, C, M, and X (strongest).',
        'Solar flares release energy equivalent to millions of hydrogen bombs in just minutes. They are caused by the sudden release of magnetic energy stored in the Sun\'s atmosphere.',
        'The most powerful solar flares can cause radio blackouts and affect satellite operations. The Carrington Event of 1859 was one of the most intense solar storms ever recorded.'
      ],
      
      // Solar Wind
      solar_wind: [
        'Solar wind is a stream of charged particles (plasma) released from the Sun\'s corona. It consists mainly of electrons and protons and can travel at speeds of 400-800 km/s. Solar wind interacts with Earth\'s magnetosphere.',
        'The solar wind is constantly flowing from the Sun, carrying the Sun\'s magnetic field throughout the solar system. It creates the heliosphere that protects us from cosmic rays.',
        'Solar wind speed and density vary with solar activity. During solar maximum, the wind is more turbulent and can cause more geomagnetic storms on Earth.'
      ],
      
      // Space Weather
      space_weather: [
        'Space weather refers to conditions on the Sun and in the solar wind that can influence the performance and reliability of space-borne and ground-based technological systems. It includes solar flares, CMEs, and geomagnetic storms.',
        'Space weather affects satellites, power grids, GPS systems, and radio communications. Understanding it is crucial for protecting our technology-dependent society.',
        'Space weather forecasting helps us prepare for solar storms that could disrupt critical infrastructure. Organizations like NOAA monitor space weather 24/7.'
      ],
      
      // General Solar Topics
      sun: [
        'The Sun is our star, a massive ball of hydrogen and helium that provides light and energy to Earth. It has various layers including the core, radiative zone, convective zone, photosphere, chromosphere, and corona.',
        'The Sun is about 4.6 billion years old and will continue shining for another 5 billion years. It converts hydrogen to helium through nuclear fusion, releasing enormous amounts of energy.',
        'The Sun\'s surface temperature is about 5,500°C, but its corona can reach millions of degrees. This temperature paradox is one of the great mysteries of solar physics.'
      ]
    };
    
    // Smart response selection based on query content
    let selectedResponses: string[] = [];
    
    if (input.includes('cme') || input.includes('coronal mass ejection')) {
      selectedResponses = responses.cme;
    } else if (input.includes('aditya') || input.includes('l1')) {
      selectedResponses = responses.aditya;
    } else if (input.includes('solar flare') || input.includes('flare')) {
      selectedResponses = responses.solar_flare;
    } else if (input.includes('solar wind') || input.includes('wind')) {
      selectedResponses = responses.solar_wind;
    } else if (input.includes('space weather') || input.includes('weather')) {
      selectedResponses = responses.space_weather;
    } else if (input.includes('sun') || input.includes('solar')) {
      selectedResponses = responses.sun;
    } else if (input.includes('geomagnetic storm') || input.includes('storm')) {
      return 'A geomagnetic storm is a temporary disturbance of Earth\'s magnetosphere caused by solar wind shock waves. These storms can cause auroras, disrupt satellite communications, and affect power grids on Earth.';
    } else if (input.includes('aurora') || input.includes('northern lights')) {
      return 'Auroras are natural light displays in the sky, caused by the interaction of solar wind particles with Earth\'s magnetic field. They typically occur near the poles and are most visible during geomagnetic storms.';
    } else if (input.includes('magnetosphere')) {
      return 'Earth\'s magnetosphere is the region around our planet dominated by its magnetic field. It protects us from harmful solar radiation and cosmic rays, acting as a shield against the solar wind.';
    } else if (input.includes('hello') || input.includes('hi') || input.includes('hey')) {
      return 'Hello! I\'m your Solar AI Assistant. I can help you understand solar phenomena, space weather, CMEs, and the Aditya-L1 mission. What would you like to know about?';
    } else if (input.includes('help') || input.includes('what can you do')) {
      return 'I can help you with questions about solar physics, space weather, CMEs, solar flares, the Aditya-L1 mission, and related topics. You can also use web search mode to get the latest information from the internet.';
    } else if (input.includes('solar data') || input.includes('read') || input.includes('measurement')) {
      return 'Solar data includes measurements of solar wind particles, magnetic fields, and radiation. The SWIS and ASPEX instruments on Aditya-L1 help us understand these phenomena by detecting solar wind ions and electrons.';
    }
    
    // Return a random response from the selected category for variety
    if (selectedResponses.length > 0) {
      const randomIndex = Math.floor(Math.random() * selectedResponses.length);
      return selectedResponses[randomIndex];
    }
    
    // Default response with suggestions
    return 'I\'m here to help you understand solar phenomena, space weather, and the Aditya-L1 mission. You can ask me about CMEs, solar flares, solar wind, auroras, or any other space weather topics. Try asking something specific about solar physics!';
  };

  const handleQuickQuestion = (question: string) => {
    setInputText(question);
    handleSendMessage();
  };

  const handleBackPress = () => {
    logger.info('Back button pressed', {}, 'ChatbotScreen');
    navigation.goBack();
  };

  const handleModeSwitch = (mode: ResponseMode) => {
    setResponseMode(mode);
    logger.info('Response mode changed', { mode }, 'ChatbotScreen');
  };

  const handleLinkPress = async (url: string) => {
    try {
      const supported = await Linking.canOpenURL(url);
      if (supported) {
        await Linking.openURL(url);
        logger.info('Link opened in browser', { url }, 'ChatbotScreen');
      } else {
        logger.warn('Cannot open URL', { url }, 'ChatbotScreen');
      }
    } catch (error) {
      logger.error('Error opening link', { error, url }, 'ChatbotScreen');
    }
  };

  const renderSearchResult = (result: SearchResult, index: number) => (
    <View key={index} style={styles.searchResultItem}>
      <View style={styles.searchResultContent}>
        <TouchableOpacity onPress={() => handleLinkPress(result.link)}>
          <View style={styles.titleContainer}>
            <Text style={styles.searchResultTitle}>{result.title}</Text>
            <Ionicons name="open-outline" size={12} color={APP_CONFIG.colors.info} />
          </View>
        </TouchableOpacity>
        {result.snippet && (
          <Text style={styles.searchResultSnippet}>{result.snippet}</Text>
        )}
        <TouchableOpacity onPress={() => handleLinkPress(result.link)}>
          <Text style={styles.searchResultLink}>{result.link}</Text>
        </TouchableOpacity>
      </View>
      {result.imageUrl && (
        <TouchableOpacity onPress={() => handleLinkPress(result.link)} style={styles.imageContainer}>
          <Image 
            source={{ uri: result.imageUrl }} 
            style={styles.searchResultImage}
            resizeMode="cover"
          />
          <View style={styles.imageOverlay}>
            <Ionicons name="open-outline" size={16} color={APP_CONFIG.colors.text.primary} />
          </View>
        </TouchableOpacity>
      )}
    </View>
  );

  const renderMessage = (message: Message) => (
    <View key={message.id} style={[styles.messageContainer, message.isUser ? styles.userMessage : styles.aiMessage]}>
      <View style={[styles.messageBubble, message.isUser ? styles.userBubble : styles.aiBubble]}>
        {!message.isUser && message.source && (
          <View style={styles.sourceIndicator}>
            <Ionicons 
              name={message.source === 'web' ? 'globe' : 'bulb'} 
              size={12} 
              color={APP_CONFIG.colors.text.secondary} 
            />
            <Text style={styles.sourceText}>
              {message.source === 'web' ? 'Web Search' : message.source === 'local_llm' ? 'Local AI' : 'AI Model'}
            </Text>
          </View>
        )}
        <Text style={[styles.messageText, message.isUser ? styles.userText : styles.aiText]}>
          {message.text}
        </Text>
        
        {/* Render search results with images */}
        {message.searchResults && message.searchResults.length > 0 && (
          <View style={styles.searchResultsContainer}>
            {message.searchResults.map((result, index) => renderSearchResult(result, index))}
          </View>
        )}
        
        <Text style={styles.timestamp}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </View>
    </View>
  );

  return (
    <LinearGradient
      colors={[APP_CONFIG.colors.primary, APP_CONFIG.colors.background.secondary, APP_CONFIG.colors.background.tertiary]}
      style={styles.container}
    >
      <SafeAreaView style={styles.safeArea}>
        <StatusBar barStyle="light-content" translucent backgroundColor="transparent" />
        
        <LottieView
          source={require('../../assets/particles.json')}
          autoPlay
          loop
          style={StyleSheet.absoluteFill}
        />

        <Header 
          title="Solar AI Assistant" 
          showBackButton={true}
          onBackPress={handleBackPress}
        />

        {/* Response Mode Selector */}
        <View style={styles.modeSelector}>
          <TouchableOpacity
            style={[styles.modeButton, responseMode === 'model' && styles.activeModeButton]}
            onPress={() => handleModeSwitch('model')}
          >
            <Ionicons 
              name="bulb" 
              size={20} 
              color={responseMode === 'model' ? APP_CONFIG.colors.secondary : APP_CONFIG.colors.text.secondary} 
            />
            <Text style={[styles.modeText, responseMode === 'model' && styles.activeModeText]}>
              AI Model
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={[styles.modeButton, responseMode === 'web' && styles.activeModeButton]}
            onPress={() => handleModeSwitch('web')}
          >
            <Ionicons 
              name="globe" 
              size={20} 
              color={responseMode === 'web' ? APP_CONFIG.colors.secondary : APP_CONFIG.colors.text.secondary} 
            />
            <Text style={[styles.modeText, responseMode === 'web' && styles.activeModeText]}>
              Web Search
            </Text>
          </TouchableOpacity>
        </View>

        <KeyboardAvoidingView 
          style={styles.chatContainer} 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
          <ScrollView 
            style={styles.messagesContainer}
            contentContainerStyle={styles.messagesContent}
            showsVerticalScrollIndicator={false}
          >
            {messages.map(renderMessage)}
            
            {isTyping && (
              <View style={[styles.messageContainer, styles.aiMessage]}>
                <View style={[styles.messageBubble, styles.aiBubble]}>
                  <View style={styles.typingIndicator}>
                    <Text style={styles.typingText}>
                      {responseMode === 'web' ? 'Searching web...' : 'AI is thinking...'}
                    </Text>
                    <View style={styles.typingDots}>
                      <View style={[styles.dot, styles.dot1]} />
                      <View style={[styles.dot, styles.dot2]} />
                      <View style={[styles.dot, styles.dot3]} />
                    </View>
                  </View>
                </View>
              </View>
            )}
          </ScrollView>

          {/* Quick Questions */}
          {messages.length === 1 && (
            <View style={styles.quickQuestionsContainer}>
              <Text style={styles.quickQuestionsTitle}>Quick Questions:</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                {quickQuestions.map((question, index) => (
                  <TouchableOpacity
                    key={index}
                    style={styles.quickQuestionChip}
                    onPress={() => handleQuickQuestion(question)}
                  >
                    <Text style={styles.quickQuestionText}>{question}</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>
          )}

          {/* Input Area */}
          <View style={styles.inputContainer}>
            <TextInput
              style={styles.textInput}
              value={inputText}
              onChangeText={setInputText}
              placeholder={`Ask about solar events, CMEs, or space weather (${responseMode === 'web' ? 'Web Search' : 'AI Model'} mode)...`}
              placeholderTextColor={APP_CONFIG.colors.text.tertiary}
              multiline
              maxLength={500}
            />
            <TouchableOpacity 
              style={[styles.sendButton, inputText.trim() === '' && styles.sendButtonDisabled]}
              onPress={handleSendMessage}
              disabled={inputText.trim() === ''}
            >
              <Ionicons 
                name="send" 
                size={20} 
                color={inputText.trim() === '' ? APP_CONFIG.colors.text.tertiary : APP_CONFIG.colors.text.primary} 
              />
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1,
    paddingHorizontal: APP_CONFIG.spacing.lg,
  },
  safeArea: { flex: 1 },
  modeSelector: {
    flexDirection: 'row',
    backgroundColor: APP_CONFIG.colors.secondary,
    borderRadius: APP_CONFIG.borderRadius.xl,
    padding: APP_CONFIG.spacing.xs,
    marginBottom: APP_CONFIG.spacing.lg,
    ...APP_CONFIG.shadows.medium,
  },
  modeButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: APP_CONFIG.spacing.sm,
    paddingHorizontal: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.lg,
  },
  activeModeButton: {
    backgroundColor: APP_CONFIG.colors.text.primary,
  },
  modeText: {
    marginLeft: APP_CONFIG.spacing.xs,
    fontSize: 14,
    fontWeight: '600',
    color: APP_CONFIG.colors.text.secondary,
  },
  activeModeText: {
    color: APP_CONFIG.colors.secondary,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    paddingBottom: APP_CONFIG.spacing.lg,
  },
  messageContainer: {
    marginBottom: APP_CONFIG.spacing.md,
  },
  userMessage: {
    alignItems: 'flex-end',
  },
  aiMessage: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: APP_CONFIG.spacing.md,
    borderRadius: APP_CONFIG.borderRadius.xl,
    ...APP_CONFIG.shadows.light,
  },
  userBubble: {
    backgroundColor: APP_CONFIG.colors.success,
  },
  aiBubble: {
    backgroundColor: APP_CONFIG.colors.secondary,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
  userText: {
    color: APP_CONFIG.colors.primary,
    fontWeight: '500',
  },
  aiText: {
    color: APP_CONFIG.colors.text.primary,
  },
  timestamp: {
    fontSize: 12,
    color: APP_CONFIG.colors.text.tertiary,
    marginTop: APP_CONFIG.spacing.xs,
    alignSelf: 'flex-end',
  },
  typingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  typingText: {
    color: APP_CONFIG.colors.text.secondary,
    fontSize: 14,
    marginRight: APP_CONFIG.spacing.sm,
  },
  typingDots: {
    flexDirection: 'row',
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: APP_CONFIG.colors.text.secondary,
    marginHorizontal: 2,
  },
  dot1: {
    opacity: 0.4,
  },
  dot2: {
    opacity: 0.7,
  },
  dot3: {
    opacity: 1,
  },
  quickQuestionsContainer: {
    marginBottom: APP_CONFIG.spacing.lg,
  },
  quickQuestionsTitle: {
    color: APP_CONFIG.colors.text.primary,
    fontSize: 16,
    fontWeight: '600',
    marginBottom: APP_CONFIG.spacing.sm,
  },
  quickQuestionChip: {
    backgroundColor: APP_CONFIG.colors.secondary,
    paddingHorizontal: APP_CONFIG.spacing.md,
    paddingVertical: APP_CONFIG.spacing.sm,
    borderRadius: APP_CONFIG.borderRadius.full,
    marginRight: APP_CONFIG.spacing.sm,
    ...APP_CONFIG.shadows.light,
  },
  quickQuestionText: {
    color: APP_CONFIG.colors.text.primary,
    fontSize: 14,
    fontWeight: '500',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    backgroundColor: APP_CONFIG.colors.secondary,
    borderRadius: APP_CONFIG.borderRadius.xl,
    padding: APP_CONFIG.spacing.sm,
    marginTop: APP_CONFIG.spacing.md,
    ...APP_CONFIG.shadows.medium,
  },
  textInput: {
    flex: 1,
    color: APP_CONFIG.colors.text.primary,
    fontSize: 16,
    maxHeight: 100,
    paddingHorizontal: APP_CONFIG.spacing.sm,
    paddingVertical: APP_CONFIG.spacing.xs,
  },
  sendButton: {
    backgroundColor: APP_CONFIG.colors.success,
    padding: APP_CONFIG.spacing.sm,
    borderRadius: APP_CONFIG.borderRadius.full,
    marginLeft: APP_CONFIG.spacing.sm,
  },
  sendButtonDisabled: {
    backgroundColor: APP_CONFIG.colors.overlay.dark,
  },
  searchResultContainer: {
    marginTop: APP_CONFIG.spacing.sm,
    padding: APP_CONFIG.spacing.sm,
    backgroundColor: APP_CONFIG.colors.overlay.light,
    borderRadius: APP_CONFIG.borderRadius.md,
  },
  searchResultTitle: {
    color: APP_CONFIG.colors.text.primary,
    fontSize: 14,
    fontWeight: '600',
    marginBottom: APP_CONFIG.spacing.xs,
  },
  searchResultSnippet: {
    color: APP_CONFIG.colors.text.secondary,
    fontSize: 12,
    lineHeight: 16,
    marginBottom: APP_CONFIG.spacing.xs,
  },
  searchResultLink: {
    color: APP_CONFIG.colors.info,
    fontSize: 12,
    textDecorationLine: 'underline',
  },
  searchResultImage: {
    width: 80,
    height: 60,
    borderRadius: APP_CONFIG.borderRadius.sm,
    marginTop: APP_CONFIG.spacing.xs,
  },
  sourceIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: APP_CONFIG.spacing.xs,
  },
  sourceText: {
    fontSize: 12,
    color: APP_CONFIG.colors.text.tertiary,
    marginLeft: APP_CONFIG.spacing.xs,
  },
  searchResultItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: APP_CONFIG.spacing.md,
    padding: APP_CONFIG.spacing.md,
    backgroundColor: APP_CONFIG.colors.overlay.light,
    borderRadius: APP_CONFIG.borderRadius.lg,
    borderLeftWidth: 3,
    borderLeftColor: APP_CONFIG.colors.info,
    ...APP_CONFIG.shadows.light,
  },
  searchResultContent: {
    flex: 1,
    marginRight: APP_CONFIG.spacing.sm,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: APP_CONFIG.spacing.xs,
  },
  imageContainer: {
    position: 'relative',
  },
  imageOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    borderRadius: APP_CONFIG.borderRadius.sm,
  },
  searchResultsContainer: {
    marginTop: APP_CONFIG.spacing.md,
    marginBottom: APP_CONFIG.spacing.sm,
  },
  chatContainer: {
    flex: 1,
  },
}); 