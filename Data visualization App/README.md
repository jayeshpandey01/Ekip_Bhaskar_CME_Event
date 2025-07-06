# SolarSim 🌞

**Solar CME Simulation & Monitoring System**

Experience real-time solar particle data visualization from the Aditya-L1 mission. Dive into interactive solar event simulations, insights, and tools designed for space weather researchers and enthusiasts.

## 🚀 Features

- **Real-time CME Data**: Monitor Coronal Mass Ejection events with live data from Aditya-L1
- **Interactive Simulations**: Visualize solar particle behavior and magnetic field interactions
- **Sensor Dashboard**: Track SWIS, ASPEX, and VELC sensor readings
- **Professional UI**: Modern, responsive design with smooth animations
- **Search Functionality**: Find specific data, articles, and simulations quickly
- **Error Handling**: Robust error boundaries and user-friendly error messages

## 📱 Screenshots

*Screenshots will be added here*

## 🛠️ Tech Stack

- **React Native** - Cross-platform mobile development
- **Expo** - Development platform and build tools
- **TypeScript** - Type-safe JavaScript
- **React Navigation** - Navigation between screens
- **Lottie** - Smooth animations
- **Chart Kit** - Data visualization
- **Linear Gradient** - Beautiful gradients
- **Blur Effects** - Modern UI elements

## 📋 Prerequisites

- Node.js (>= 16.0.0)
- npm (>= 8.0.0)
- Expo CLI
- iOS Simulator (for iOS development)
- Android Studio (for Android development)

## 🚀 Getting Started

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/solarsim/solarsim-app.git
   cd solarsim-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Run on your device/simulator**
   - Press `i` for iOS simulator
   - Press `a` for Android emulator
   - Scan QR code with Expo Go app on your phone

### Development Scripts

```bash
# Start development server
npm start

# Run on specific platform
npm run ios
npm run android
npm run web

# Build for production
npm run build:android
npm run build:ios

# Type checking
npm run type-check

# Linting (when ESLint is configured)
npm run lint
```

## 📁 Project Structure

```
solarsim-app/
├── app/
│   ├── components/          # Reusable UI components
│   │   ├── ErrorBoundary.tsx
│   │   └── LoadingSpinner.tsx
│   ├── screens/            # Screen components
│   │   ├── Welcome.tsx
│   │   ├── Landing.tsx
│   │   ├── SearchScreen.tsx
│   │   └── GraphSimulationScreen.tsx
│   ├── types/              # TypeScript type definitions
│   │   └── navigation.ts
│   └── utils/              # Utility functions
│       ├── constants.ts
│       └── logger.ts
├── assets/                 # Static assets
│   ├── particles.json
│   ├── sample_graph.png
│   └── searchData.json
├── App.tsx                 # Main app component
├── app.json               # Expo configuration
└── package.json           # Dependencies and scripts
```

## 🎨 Design System

The app uses a consistent design system with:

- **Colors**: Dark theme with purple and green gradients
- **Typography**: Monospace font for technical data, system fonts for UI
- **Spacing**: Consistent spacing scale (xs, sm, md, lg, xl, xxl)
- **Shadows**: Multiple shadow levels for depth
- **Border Radius**: Consistent rounded corners
- **Animations**: Smooth transitions and micro-interactions

## 🔧 Configuration

### App Configuration

Key configuration is centralized in `app/utils/constants.ts`:

- Color palette
- Spacing values
- Shadow definitions
- Animation settings
- App metadata

### Navigation

Navigation types are defined in `app/types/navigation.ts` for type safety.

## 📊 Data Sources

The app simulates data from the Aditya-L1 mission:

- **SWIS** (Solar Wind Ion Spectrometer)
- **ASPEX** (Aditya Solar Wind Particle Experiment)
- **VELC** (Visible Emission Line Coronagraph)

## 🐛 Error Handling

The app includes comprehensive error handling:

- **Error Boundaries**: Catch and display React errors gracefully
- **Professional Logging**: Structured logging with different levels
- **User Feedback**: Clear error messages and retry options

## 📝 Logging

The app uses a professional logging system:

```typescript
import { logger } from './app/utils/logger';

// Different log levels
logger.debug('Debug information');
logger.info('General information');
logger.warn('Warning message');
logger.error('Error message');
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **ISRO** for the Aditya-L1 mission data
- **Expo** team for the amazing development platform
- **React Native** community for the robust framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/solarsim/solarsim-app/issues)
- **Documentation**: [Wiki](https://github.com/solarsim/solarsim-app/wiki)
- **Email**: support@solarsim.app

---

**Made with ❤️ by the SolarSim Team** 