# cAIber Frontend - Threat Intelligence Platform UI

## Overview
A futuristic, cyber-themed web interface for the cAIber threat intelligence platform. Built with React, Vite, and modern visualization libraries to provide security analysts with an intuitive command center for threat analysis.

## Features

### 🎯 Main Dashboard
- Real-time pipeline status monitoring
- One-click threat analysis initiation
- Live metrics cards (threats detected, critical risks, analysis time)
- 4-stage pipeline visualization with progress indicators

### 🔍 Analysis View
- Priority Intelligence Requirements (PIRs) display
- Threat landscape browser (CVEs, OTX indicators, GitHub advisories)
- Risk assessment matrix and detailed threat cards
- Executive summary generation

### 🛡️ Threat Modeling
- Interactive attack path visualization
- MITRE ATT&CK framework mapping
- STRIDE threat classification
- Step-by-step attack sequence analysis

### ✨ Visual Features
- 3D particle background animation (Three.js)
- Neon cyber color scheme (cyan, purple, green)
- Glass morphism UI components
- Animated transitions and hover effects
- Holographic and glitch text effects

## Tech Stack

- **Framework**: React 18 + Vite
- **Routing**: React Router v6
- **State Management**: Zustand
- **Styling**: Tailwind CSS + Custom CSS
- **3D Graphics**: Three.js, React Three Fiber
- **Charts**: D3.js, Recharts
- **Animations**: Framer Motion
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Notifications**: React Hot Toast

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
# Create optimized production build
npm run build

# Preview production build locally
npm run preview
```

## API Integration

The frontend connects to these backend endpoints:

- `GET /generate-pirs` - Generate Priority Intelligence Requirements
- `POST /collect-threats` - Collect threats from multiple sources
- `POST /correlate-threats` - Correlate threats with organizational context
- `POST /collect-and-correlate` - Combined collection and correlation
- `POST /run-all` - Execute complete pipeline

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API client configuration
│   ├── pages/            # Main page components
│   │   ├── Dashboard.jsx
│   │   ├── Analysis.jsx
│   │   └── ThreatModeling.jsx
│   ├── components/       # Reusable components
│   │   ├── PipelineControl/
│   │   ├── Visualizations/
│   │   └── Common/
│   ├── store/           # Zustand state management
│   └── styles/          # Global styles and themes
├── public/              # Static assets
└── index.html          # Entry HTML file
```

## Configuration

### Environment Variables
Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

### Customization

#### Color Theme
Modify colors in `tailwind.config.js`:
```javascript
colors: {
  cyber: {
    cyan: '#00ffff',
    purple: '#b829dd',
    green: '#00ff88',
    // ...
  }
}
```

#### Animation Speed
Adjust animation durations in component files or global CSS.

## Usage

### Running Analysis
1. Open the Dashboard
2. Click "INITIATE THREAT ANALYSIS"
3. Monitor progress through 4 stages:
   - Stage 1: Organizational DNA extraction
   - Stage 2: Threat collection (OTX, CVE, GitHub)
   - Stage 3: Risk correlation
   - Stage 4: Threat modeling
4. View results in Analysis page
5. Explore attack paths in Threat Modeling page

### Advanced Options
- **Skip DNA Building**: Use cached organizational data
- **Autonomous Mode**: Enable AI-powered correlation
- **Fast Mode**: Limited sources for quicker analysis

## Performance

- Optimized bundle size with code splitting
- Lazy loading for heavy visualizations
- Memoized components to prevent unnecessary re-renders
- Efficient WebGL rendering for 3D animations

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style and component patterns
2. Use TypeScript for new components when possible
3. Ensure responsive design for all screen sizes
4. Test on multiple browsers before submitting PR

## License

Part of the cAIber Threat Intelligence Platform