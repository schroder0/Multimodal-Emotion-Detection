# Multimodal Emotion Detection Frontend

React-based frontend for the multimodal emotion detection system.

## Setup

### Prerequisites
- Node.js 14+ and npm

### Installation

```bash
# Install dependencies
npm install

# Set environment variables (optional)
# Create .env file or update .env.local
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local

# Start development server
npm start
```

The app will open at http://localhost:3000

## Environment Variables

Create a `.env.local` file in the frontend directory:

```
REACT_APP_API_URL=http://localhost:8000
```

## Building for Production

```bash
npm run build
```

The optimized build will be in the `build` directory.

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── InputForm.js
│   │   ├── InputForm.css
│   │   ├── ResultCard.js
│   │   └── ResultCard.css
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

## Components

### InputForm
- Text input with emoji support
- Image upload functionality
- Form validation
- Loading state during analysis

### ResultCard
- Displays detected emotion
- Shows confidence score
- Detailed reasoning breakdown
- Context summary

## Features

✨ **Interactive UI**
- Real-time text input
- Image preview
- Responsive design
- Smooth animations

📊 **Detailed Results**
- Emotion with emoji
- Confidence score with progress bar
- Multi-step reasoning explanation
- Context summary

🎨 **Beautiful Design**
- Gradient background
- Color-coded emotions
- Smooth transitions
- Mobile responsive
