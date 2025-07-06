// Text formatting utilities for React Native

export interface FormattedTextSegment {
  text: string;
  style?: 'bold' | 'italic' | 'code' | 'normal';
}

export const parseFormattedText = (text: string): FormattedTextSegment[] => {
  const segments: FormattedTextSegment[] = [];
  let currentText = '';
  let currentStyle: 'bold' | 'italic' | 'code' | 'normal' = 'normal';
  
  // Simple markdown-like parser
  const tokens = text.split(/(\*\*.*?\*\*|\*.*?\*|`.*?`)/);
  
  tokens.forEach((token) => {
    if (token.startsWith('**') && token.endsWith('**')) {
      // Bold text
      if (currentText) {
        segments.push({ text: currentText, style: currentStyle });
        currentText = '';
      }
      segments.push({ text: token.slice(2, -2), style: 'bold' });
    } else if (token.startsWith('*') && token.endsWith('*') && token.length > 2) {
      // Italic text
      if (currentText) {
        segments.push({ text: currentText, style: currentStyle });
        currentText = '';
      }
      segments.push({ text: token.slice(1, -1), style: 'italic' });
    } else if (token.startsWith('`') && token.endsWith('`')) {
      // Code text
      if (currentText) {
        segments.push({ text: currentText, style: currentStyle });
        currentText = '';
      }
      segments.push({ text: token.slice(1, -1), style: 'code' });
    } else {
      currentText += token;
    }
  });
  
  if (currentText) {
    segments.push({ text: currentText, style: currentStyle });
  }
  
  return segments;
};

// Clean markdown from text
export const cleanMarkdown = (text: string): string => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markers
    .replace(/\*(.*?)\*/g, '$1') // Remove italic markers
    .replace(/`(.*?)`/g, '$1') // Remove code markers
    .replace(/\[(.*?)\]\(.*?\)/g, '$1') // Remove link markers
    .replace(/^#+\s*/gm, '') // Remove heading markers
    .replace(/^\s*[-*+]\s*/gm, '• ') // Convert list markers
    .trim();
};

// Format search results for better display
export const formatSearchResults = (query: string, results: any[]): string => {
  let formattedText = `Web Search Results for: "${query}"\n\n`;
  
  results.forEach((result, index) => {
    formattedText += `${index + 1}. ${result.title}\n`;
    if (result.snippet) {
      formattedText += `${result.snippet}\n`;
    }
    formattedText += `Source: ${result.link}\n\n`;
  });
  
  return formattedText;
}; 