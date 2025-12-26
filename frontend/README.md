# CureLink Frontend: The Patient Experience

This is the "Face" of CureLink—a modern, responsive, and performance-optimized React application designed to provide a seamless clinical chat experience.

## 🎨 Design Philosophy
We’ve built the UI to feel familiar but premium. 
- **WhatsApp Style**: Familiar chat bubbles, timestamps, and message status ticks (single for sent, double sky-blue for delivered).
- **Dark Mode First**: A sleek `slate-950` theme with yellow accents to reduce eye strain for medical professionals.
- **Micro-Animations**: Uses `Framer Motion` for smooth message entries and typing indicators, making the AI feel alive.

## 🛠️ Key Technical Features

### 1. Protocol-Aware WebSockets
Our chat system is built to work anywhere. It intelligently detects if it's running on `http` or `https` and automatically switches the WebSocket protocol between `ws` and `wss`. This prevents "Mixed Content" security blocks in production.

### 2. Optimistic Updates
To make the app feel instant, we show your message in the chat immediately (with a gray tick) before the server even confirms it. Once the AI starts processing, the status updates dynamically.

### 3. Responsive Layout (DVH)
We use `Dynamic Viewport Height (dvh)` instead of standard `vh`. This ensures that on mobile devices, the chat header and input box stay perfectly fixed even when the browser address bar slides in or out.

## 🏗️ Folder Structure
- `src/pages/Chat.tsx`: The heart of the app—manages the WebSocket loop, message history, and the auto-scroll logic.
- `src/components/`: Reusable UI elements like buttons, inputs, and icons.
- `src/context/`: Handles global authentication and user state.
- `nginx.conf`: Our production web server configuration that handles SPA routing and API proxying.

## ⚙️ Development

### Environment Variables
Create a `.env` in this directory:
```env
VITE_API_URL=http://localhost:8000
```

### Commands
- `npm run dev`: Start local development server.
- `npm run build`: Create a production-ready bundle in the `/dist` folder.
