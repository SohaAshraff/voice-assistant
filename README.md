# 🎙️ Voice AI Store Assistant with RAG

A real-time voice assistant powered by Google Gemini Live API, LiveKit, and FAISS-based Retrieval-Augmented Generation (RAG) for accurate store information retrieval.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Running Locally](#running-locally)
- [Demo video](#example_interactions)
- [How It Works](#how-it-works)
- [RAG Integration](#rag-integration)
- [Example Usage](#example-usage)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This project implements a voice-powered AI assistant for a retail store that can answer customer questions about:
- Store hours and location
- Services offered
- Payment methods
- Return policies
- Contact information
- Accessibility features

The assistant uses **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware responses by searching a knowledge base before answering.

---

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │ ◄─────► │ FastAPI      │ ◄─────► │  LiveKit    │
│  (React UI) │  HTTP   │ Token Server │  WebRTC │   Server    │
└─────────────┘         └──────────────┘         └─────────────┘
                                                         │
                                                         ▼
                        ┌──────────────────────────────────────┐
                        │      Voice Agent (Python)            │
                        │  ┌────────────────────────────────┐  │
                        │  │  Google Gemini Live API        │  │
                        │  │  (Realtime Voice Model)        │  │
                        │  └────────────────────────────────┘  │
                        │              │                        │
                        │              ▼                        │
                        │  ┌────────────────────────────────┐  │
                        │  │  RAG System (FAISS)            │  │
                        │  │  • Sentence Transformers       │  │
                        │  │  • Vector Search               │  │
                        │  │  • Knowledge Base Retrieval    │  │
                        │  └────────────────────────────────┘  │
                        └──────────────────────────────────────┘
```

### Component Flow:

1. **User** speaks through the web interface
2. **FastAPI** generates LiveKit access token
3. **LiveKit** handles WebRTC audio streaming
4. **Voice Agent** receives audio and processes with Gemini
5. **RAG System** retrieves relevant context from knowledge base
6. **Gemini Live API** generates context-aware voice response
7. **LiveKit** streams audio response back to user

---

##  Features

- ✅ **Real-time Voice Interaction**: Bidirectional voice communication
- ✅ **RAG-Enhanced Responses**: Accurate answers from store knowledge base
- ✅ **Automatic Context Injection**: AI receives relevant info for every query
- ✅ **Live Transcript**: See the conversation in real-time
- ✅ **Noise Cancellation**: Built-in audio processing
- ✅ **Web Interface**: Clean, responsive React UI

---

## 📦 Prerequisites

### Required Software:
- **Python 3.10+** 
- **Node.js 18+**
- **npm or yarn**

### Required API Keys:
1. **LiveKit Cloud Account** (free tier available)
   - Get from: https://cloud.livekit.io
   - You'll need: API Key, API Secret, and WebSocket URL

2. **Google AI Studio API Key**
   - Get from: https://ai.google.dev/
   - Required for Gemini 2.0 Flash model

---


## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/SohaAshraff/voice-assistant.git
cd voice-assistant
```

### Step 2: Backend Setup

#### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```


#### Configure Environment Variables

Create a file named `.env` in the `backend/` folder:

```bash
cd backend
touch .env
```

Add your credentials to `.env`:

```env
# LiveKit Credentials (from https://cloud.livekit.io)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxx

# Google Gemini API Key (from https://ai.google.dev/)
GOOGLE_API_KEY=AIzaXXXXXXXXXXXXXXXXXXXX
```

⚠️ **Important:** 
- Replace the `xxx` with your actual credentials

### Step 3: Frontend Setup

#### Install Node Dependencies

```bash
cd frontend
npm install
```
This installs:
- React - UI framework
- Vite - Build tool
- LiveKit Client - Audio communication

---

## 🏃 Running the Application

You need to run **3 separate services** in 3 different terminal windows.

### Terminal 1: Start the Token Server

This server generates access tokens for LiveKit connections.

```bash
cd backend
python server.py
```

✅ **Success:** You should see:
```
==================================================
🚀 FastAPI Token Server Starting...
==================================================
📡 LiveKit URL: wss://your-project.livekit.cloud
🌐 Server: http://localhost:5000
==================================================
INFO:     Uvicorn running on http://0.0.0.0:5000
```

**Keep this terminal running!**

---

### Terminal 2: Start the Voice Agent

This is the AI agent that handles voice interactions and RAG retrieval.

```bash
cd backend
python Agent.py start
```

✅ **Success:** You should see:
```
✅ Voice agent with FAISS RAG is ready!
```

**Keep this terminal running!**

---

### Terminal 3: Start the Frontend

This launches the web interface.

```bash
cd frontend
npm run dev
```

✅ **Success:** You should see:
```
  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Keep this terminal running!**

---

## 🌐 Using the Application

### 1. Open Your Browser

Go to: **http://localhost:5173**

You should see a purple interface with "🎙️ Store Assistant"

### 2. Connect to the Assistant

Click the **"Connect to Assistant"** button

### 3. Allow Microphone Access

Your browser will ask for microphone permission - click **"Allow"**

### 4. Start Talking!

Just speak naturally. Try these questions:
- "What are your store hours?"
- "What's the store location"

The assistant will respond with voice and show the conversation in the transcript box.

### 5. Disconnect When Done

Click the **"Disconnect"** button to end the session.

---

## 🎬 Demo Video

I’ve included a short demo video showing the voice assistant in action. In the video, you can see:

- Connecting to the assistant through the web interface
- Speaking naturally and receiving voice responses
- Real-time transcript display
- RAG-powered contextual answers from the store knowledge base

**Watch it here:** [Demo.mp4](./Demo.mp4)

> The video demonstrates a typical interaction with the agent and highlights how the system processes your voice input to provide accurate, context-aware responses.

---

## 🔧 How It Works

### What Happens When You Ask a Question

```
1. You speak: "What's the store location?"
   ↓
2. LiveKit streams your voice to the agent in real time
   ↓
3. Gemini converts the audio into text
   ↓
4. Gemini decides that external knowledge is needed
   ↓
5. Gemini automatically triggers the function tool:
      search_knowledge_base("store location")
   ↓
6. The RAG system (FAISS) searches the knowledge base
   ↓
7. The function returns relevant context back to Gemini:
      "Our store is located Downtown Street 12, Cairo..."
   ↓
8. Gemini generates a final answer using the retrieved context
   ↓
9. The response is converted to speech by the agent
   ↓
10. You hear:
     "Our store is located at Downtown Street 12, Cairo, Egypt"

```

### RAG (Retrieval-Augmented Generation)

The system uses semantic search to provide accurate, context-aware responses. The workflow integrates **function tools** so Gemini can call the RAG system automatically when needed:

```
Your Question → Gemini decides external info is needed → Function Tool Call → search_knowledge_base("User Question") → RAG System (FAISS + Sentence Transformers) → Gemini receives context from tool → Context + original question → AI Prompt → Gemini generates final, natural answer → Agent converts text to speech → User hears accurate, context-aware response
```

**Learn more:** [RAG_INTEGRATION.md](RAG_INTEGRATION.md)

---

## 📁 Project Core Structure

```
voice-assistant/
├── backend/
│   ├── server.py              # FastAPI token server
│   ├── agent.py               # Voice agent with RAG integration
│   ├── RAG.py                 # FAISS retrieval system
│   ├── store.txt              # Knowledge base (store information)
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Your API keys 
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # React UI component
│   │   └── main.jsx          # React entry point
│   ├── package.json          # Node dependencies
│   └── index.html            # HTML template
│
├── RAG_INTEGRATION.md         # RAG implementation guide
│   
├── README.md                  # This file
├── Demo.mp4                   #Demo video showing example interactions.
└── .gitignore                 # Files to ignore in git
```

---

## 🔍 Troubleshooting

### Common Issues


#### ❌ "npm: command not found"

**Problem:** Node.js not installed

**Solution:** Download and install from https://nodejs.org

---

#### ❌ "Connection failed" in browser

**Problem:** Agent not running or wrong LiveKit credentials

**Solution:**
1. Check Terminal 2 shows "Voice agent ready"
2. Verify `.env` has correct `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
3. Make sure `LIVEKIT_URL` starts with `wss://`

---

#### ❌ No audio from agent

**Problem:** Microphone not enabled or audio output issue

**Solution:**
1. Check browser granted microphone permission
2. Look for "Connected - You can speak now!" message
3. Try Chrome browser (recommended)
4. Check system audio settings

---

#### ❌ Agent doesn't use knowledge base

**Problem:** RAG not working

**Solution:**
```bash
# Test RAG directly
cd backend
python RAG.py

# Should see:
# Total Chunks
# ✅ FAISS index created 
```

---

### Quick Diagnostics

Run these commands to verify your setup:

```bash
# Check Python version (should be 3.10+)
python --version

# Check Node version (should be 18+)
node --version

# Check if backend dependencies are installed
cd backend
pip list | grep fastapi

# Check if frontend dependencies are installed
cd frontend
npm list livekit-client

```

---

## 📝 Customizing the Knowledge Base

To update the store information:

1. **Edit the file:**
```bash
nano backend/store.txt
```

2. **Add or modify information:**
```txt
opening hours: Monday-Friday 9AM-6PM, Saturday 10AM-5PM

# Add your own sections...
```

3. **Restart the agent:**
```bash
# Stop agent (Ctrl+C in Terminal 2)
python agent.py dev
```

---

## 🧪 Testing

### Test Questions

Try these to verify everything works:

| Question | Should find |
|----------|----------------|
| "What time do you close?" | Store hours |
| "Where are you located?" | Location |

---

## 📚 Documentation

- **[RAG_INTEGRATION.md](RAG_INTEGRATION.md)** - How RAG works

---

## 🔐 Security Notes

- ⚠️ Never commit your `.env` file
- ⚠️ Keep your API keys secret
- ⚠️ `.gitignore` is configured to exclude `.env`
---

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---
