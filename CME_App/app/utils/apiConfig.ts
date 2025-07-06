// API Configuration for Chatbot Features
// Replace these with your actual API keys

export const API_CONFIG = {
  // Google Custom Search API
  GOOGLE_SEARCH: {
    API_KEY: 'AIzaSyDTitczfSXxm9wAPpZousGX-Ujl9e4R4BY', // Get from Google Cloud Console
    SEARCH_ENGINE_ID: 'd75ee2d736f8f48f3', // Get from Google Custom Search
    BASE_URL: 'https://www.googleapis.com/customsearch/v1',
  },
  
  // Hugging Face Inference API
  HUGGING_FACE: {
    API_KEY: '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', // Get from Hugging Face
    MODEL_URL: 'https://api-inference.huggingface.co/models/microsoft/DialoGPT-small',
    // Alternative models you can use:
    // - 'microsoft/DialoGPT-small' (conversational, smaller, reliable)
    // - 'distilgpt2' (faster, smaller, reliable)
    // - 'gpt2' (general purpose, reliable)
    // - 'EleutherAI/gpt-neo-125M' (good balance)
    // - 'microsoft/DialoGPT-medium' (conversational, medium)
  },
  
  // Request settings
  REQUEST_TIMEOUT: 15000, // 15 seconds for model inference
  MAX_RETRIES: 3,
  
  // Model parameters - simplified for better compatibility
  MODEL_PARAMS: {
    max_length: 100,
    temperature: 0.8,
    do_sample: true,
    top_p: 0.9,
    num_return_sequences: 1,
    pad_token_id: 50256, // GPT-2 pad token
  },
  
  // Web search settings
  WEB_SEARCH: {
    max_results: 3,
    search_domain: 'solar physics space weather', // Optional: restrict search domain
    include_images: true, // Enable image search results
    image_size: 'medium', // 'small', 'medium', 'large'
    search_type: 'image', // 'web', 'image', or 'news'
  },
};

// Helper function to check if API keys are configured
export const isApiConfigured = () => {
  return (
    API_CONFIG.GOOGLE_SEARCH.API_KEY !== 'YOUR_GOOGLE_SEARCH_API_KEY' &&
    API_CONFIG.HUGGING_FACE.API_KEY !== 'YOUR_HUGGING_FACE_API_KEY'
  );
};

// Helper function to get API key with fallback
export const getApiKey = (service: 'google' | 'huggingface') => {
  if (service === 'google') {
    return API_CONFIG.GOOGLE_SEARCH.API_KEY;
  } else {
    return API_CONFIG.HUGGING_FACE.API_KEY;
  }
};

// Helper function to build search URL with parameters
export const buildSearchUrl = (query: string, searchType: 'web' | 'image' | 'news' = 'web') => {
  const baseUrl = API_CONFIG.GOOGLE_SEARCH.BASE_URL;
  const params = new URLSearchParams({
    key: API_CONFIG.GOOGLE_SEARCH.API_KEY,
    cx: API_CONFIG.GOOGLE_SEARCH.SEARCH_ENGINE_ID,
    q: `${query} ${API_CONFIG.WEB_SEARCH.search_domain}`,
    num: API_CONFIG.WEB_SEARCH.max_results.toString(),
  });

  if (searchType === 'image') {
    params.append('searchType', 'image');
    if (API_CONFIG.WEB_SEARCH.image_size !== 'medium') {
      params.append('imgSize', API_CONFIG.WEB_SEARCH.image_size);
    }
  } else if (searchType === 'news') {
    params.append('searchType', 'news');
  }

  return `${baseUrl}?${params.toString()}`;
}; 