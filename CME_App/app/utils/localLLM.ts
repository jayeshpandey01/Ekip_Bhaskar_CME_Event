// Local Small LLM for Solar Physics
// This provides intelligent responses without requiring external API calls

export interface LocalLLMResponse {
  text: string;
  confidence: number;
  source: 'local_llm';
}

export class LocalSolarLLM {
  private knowledgeBase = {
    // Solar Physics Core Concepts
    solar_physics: {
      sun: {
        description: 'The Sun is our star, a massive ball of hydrogen and helium that provides light and energy to Earth.',
        layers: ['core', 'radiative zone', 'convective zone', 'photosphere', 'chromosphere', 'corona'],
        temperature: '5,500°C surface, millions of degrees in corona',
        age: '4.6 billion years old',
        energy_source: 'nuclear fusion converting hydrogen to helium'
      },
      solar_wind: {
        description: 'Stream of charged particles (plasma) released from the Sun\'s corona',
        composition: ['electrons', 'protons', 'alpha particles'],
        speed: '400-800 km/s',
        effects: ['interacts with Earth\'s magnetosphere', 'creates heliosphere', 'varies with solar activity']
      }
    },
    
    // Space Weather Events
    space_weather: {
      cme: {
        description: 'Coronal Mass Ejection - massive burst of solar wind and magnetic fields',
        speed: 'up to 3,000 km/s',
        effects: ['geomagnetic storms', 'auroras', 'satellite disruption', 'power grid effects'],
        monitoring: 'closely monitored by space weather scientists'
      },
      solar_flare: {
        description: 'Sudden, intense bursts of radiation from the Sun\'s surface',
        classification: ['A', 'B', 'C', 'M', 'X'],
        effects: ['radio blackouts', 'satellite operations', 'power grids'],
        energy: 'equivalent to millions of hydrogen bombs'
      },
      geomagnetic_storm: {
        description: 'Temporary disturbance of Earth\'s magnetosphere',
        causes: ['solar wind shock waves', 'CMEs', 'solar flares'],
        effects: ['auroras', 'satellite communications', 'power grids']
      }
    },
    
    // Missions and Instruments
    missions: {
      aditya_l1: {
        description: 'India\'s first space-based solar observatory',
        position: 'L1 Lagrange point, 1.5 million km from Earth',
        instruments: ['SWIS', 'ASPEX', 'VELC', 'SUIT', 'HEL1OS', 'ASPEX', 'PAPA'],
        purpose: 'study solar dynamics and space weather',
        advantages: 'continuous observation without occultation'
      },
      instruments: {
        swis: 'Solar Wind Ion Spectrometer - measures solar wind ions',
        aspex: 'Aditya Solar Wind Particle Experiment - detects particles',
        velc: 'Visible Emission Line Coronagraph - observes corona'
      }
    }
  };

  // Enhanced response generation with context awareness
  public generateResponse(query: string): LocalLLMResponse {
    const input = query.toLowerCase();
    let response = '';
    let confidence = 0.5;

    // Context-aware response generation
    if (this.isAboutCME(input)) {
      response = this.generateCMEResponse(input);
      confidence = 0.9;
    } else if (this.isAboutSolarFlares(input)) {
      response = this.generateSolarFlareResponse(input);
      confidence = 0.9;
    } else if (this.isAboutAdityaL1(input)) {
      response = this.generateAdityaL1Response(input);
      confidence = 0.9;
    } else if (this.isAboutSolarWind(input)) {
      response = this.generateSolarWindResponse(input);
      confidence = 0.8;
    } else if (this.isAboutSpaceWeather(input)) {
      response = this.generateSpaceWeatherResponse(input);
      confidence = 0.8;
    } else if (this.isGreeting(input)) {
      response = this.generateGreetingResponse();
      confidence = 0.7;
    } else if (this.isHelpRequest(input)) {
      response = this.generateHelpResponse();
      confidence = 0.7;
    } else {
      response = this.generateGeneralResponse(input);
      confidence = 0.6;
    }

    return {
      text: response,
      confidence,
      source: 'local_llm'
    };
  }

  private isAboutCME(input: string): boolean {
    return input.includes('cme') || input.includes('coronal mass ejection') || 
           input.includes('solar storm') || input.includes('mass ejection');
  }

  private isAboutSolarFlares(input: string): boolean {
    return input.includes('solar flare') || input.includes('flare') || 
           input.includes('solar burst') || input.includes('radiation burst');
  }

  private isAboutAdityaL1(input: string): boolean {
    return input.includes('aditya') || input.includes('l1') || 
           input.includes('indian solar mission') || input.includes('solar observatory');
  }

  private isAboutSolarWind(input: string): boolean {
    return input.includes('solar wind') || input.includes('wind') || 
           input.includes('plasma') || input.includes('charged particles');
  }

  private isAboutSpaceWeather(input: string): boolean {
    return input.includes('space weather') || input.includes('geomagnetic') || 
           input.includes('aurora') || input.includes('magnetosphere');
  }

  private isGreeting(input: string): boolean {
    return input.includes('hello') || input.includes('hi') || input.includes('hey') || 
           input.includes('good morning') || input.includes('good afternoon');
  }

  private isHelpRequest(input: string): boolean {
    return input.includes('help') || input.includes('what can you do') || 
           input.includes('how do you work') || input.includes('capabilities');
  }

  private generateCMEResponse(input: string): string {
    const responses = [
      'A Coronal Mass Ejection (CME) is a massive burst of solar wind and magnetic fields rising above the solar corona or being released into space. CMEs can affect Earth\'s magnetic field and cause geomagnetic storms that may impact satellites, power grids, and communication systems.',
      'CMEs are among the most powerful solar events, releasing billions of tons of plasma into space at speeds up to 3,000 km/s. They can cause beautiful auroras but also disrupt technology on Earth.',
      'Coronal Mass Ejections occur when the Sun\'s magnetic field becomes unstable and releases huge amounts of charged particles. These events are closely monitored by space weather scientists for their potential impact on Earth.'
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  }

  private generateSolarFlareResponse(input: string): string {
    const responses = [
      'Solar flares are sudden, intense bursts of radiation from the Sun\'s surface. They can affect radio communications, power grids, and navigation systems on Earth. Flares are classified by their X-ray brightness: A, B, C, M, and X (strongest).',
      'Solar flares release energy equivalent to millions of hydrogen bombs in just minutes. They are caused by the sudden release of magnetic energy stored in the Sun\'s atmosphere.',
      'The most powerful solar flares can cause radio blackouts and affect satellite operations. The Carrington Event of 1859 was one of the most intense solar storms ever recorded.'
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  }

  private generateAdityaL1Response(input: string): string {
    const responses = [
      'Aditya-L1 is India\'s first space-based observatory to study the Sun. It carries seven payloads to observe the photosphere, chromosphere, and corona using electromagnetic and particle detectors. The mission aims to understand solar dynamics and space weather.',
      'The Aditya-L1 mission is positioned at the L1 Lagrange point, about 1.5 million km from Earth, providing continuous observation of the Sun without occultation.',
      'Aditya-L1\'s instruments include SWIS, ASPEX, VELC, and others that help us understand solar wind, particle acceleration, and coronal heating processes.'
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  }

  private generateSolarWindResponse(input: string): string {
    const responses = [
      'Solar wind is a stream of charged particles (plasma) released from the Sun\'s corona. It consists mainly of electrons and protons and can travel at speeds of 400-800 km/s. Solar wind interacts with Earth\'s magnetosphere.',
      'The solar wind is constantly flowing from the Sun, carrying the Sun\'s magnetic field throughout the solar system. It creates the heliosphere that protects us from cosmic rays.',
      'Solar wind speed and density vary with solar activity. During solar maximum, the wind is more turbulent and can cause more geomagnetic storms on Earth.'
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  }

  private generateSpaceWeatherResponse(input: string): string {
    const responses = [
      'Space weather refers to conditions on the Sun and in the solar wind that can influence the performance and reliability of space-borne and ground-based technological systems. It includes solar flares, CMEs, and geomagnetic storms.',
      'Space weather affects satellites, power grids, GPS systems, and radio communications. Understanding it is crucial for protecting our technology-dependent society.',
      'Space weather forecasting helps us prepare for solar storms that could disrupt critical infrastructure. Organizations like NOAA monitor space weather 24/7.'
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  }

  private generateGreetingResponse(): string {
    return 'Hello! I\'m your Solar AI Assistant. I can help you understand solar phenomena, space weather, CMEs, and the Aditya-L1 mission. What would you like to know about?';
  }

  private generateHelpResponse(): string {
    return 'I can help you with questions about solar physics, space weather, CMEs, solar flares, the Aditya-L1 mission, and related topics. You can also use web search mode to get the latest information from the internet.';
  }

  private generateGeneralResponse(input: string): string {
    return 'I\'m here to help you understand solar phenomena, space weather, and the Aditya-L1 mission. You can ask me about CMEs, solar flares, solar wind, auroras, or any other space weather topics. Try asking something specific about solar physics!';
  }
}

// Export singleton instance
export const localSolarLLM = new LocalSolarLLM(); 