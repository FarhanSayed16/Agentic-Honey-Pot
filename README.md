# 🍯 Agentic Honey-Pot

**AI-powered honeypot API that detects scam messages, autonomously engages scammers, and extracts actionable intelligence in real time.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
  - [Local Development](#local-development)
  - [Testing](#testing)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Tech Stack](#tech-stack)
- [Contributing](#contributing)

---

## 🎯 Overview

**Agentic Honey-Pot** is a sophisticated AI-powered honeypot system designed to combat fraud and scam operations. It functions as an intelligent detection and engagement layer that:

1. **Detects** incoming scam messages with high accuracy
2. **Engages** scammers autonomously using natural language generation
3. **Extracts** critical intelligence (bank accounts, UPI IDs, phone numbers, links)
4. **Reports** findings back to security systems for further investigation

Built for the **GUVI Hackathon** — Agentic Honey-Pot for Scam Detection & Intelligence Extraction, this system represents a state-of-the-art approach to cybercrime prevention.

---

## ✨ Key Features

- **Real-Time Scam Detection**: Uses intelligent analysis to identify phishing, fraud, and scam messages
- **Autonomous Agent**: LLM-powered responses that realistically engage scammers without human intervention
- **Intelligence Extraction**: Automatically extracts and structures malicious indicators (contact info, links, financial accounts)
- **Session Management**: Maintains conversation state across multiple messages per session
- **Callback Integration**: Posts results back to external systems for forensic analysis
- **Production Ready**: Built with FastAPI, deployed on Render/Railway with proper error handling
- **Security First**: API key authentication, CORS protection, input validation

---

## 🏗️ Architecture

### High-Level Flow

```
Request → Auth Middleware → Scam Detector → LLM Agent → Intelligence Extractor → Session Store → Callback
```

### Key Components

| Component | Purpose |
|-----------|---------|
| **API Gateway** | Authentication, request routing, response formatting |
| **Scam Detector** | Analyzes message + history for fraud indicators |
| **LLM Agent** | Generates contextual, human-like replies using OpenAI API |
| **Intelligence Extractor** | Identifies and structures malicious indicators (emails, phones, UPI IDs, links) |
| **Session Store** | In-memory persistence of conversation state |
| **Callback Service** | Posts final analysis results to external endpoints |

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **pip** (Python package manager)
- **OpenAI API Key** (for LLM integration)
- **Git** (optional, for version control)

### Local Development

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/agentic-honey-pot.git
cd agentic-honey-pot
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
# API_KEY=your-secret-key-here
```

For detailed setup instructions, see [docs/MANUAL_SETUP_GUIDE.md](docs/MANUAL_SETUP_GUIDE.md).

#### 5. Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. View interactive API docs at `http://localhost:8000/docs`.

---

## 🧪 Testing

### Start the Server (Terminal 1)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Test Suite (Terminal 2)
```bash
python tests/test_phase11.py
```

### Manual API Test with curl

```bash
curl -X POST http://localhost:8000/api/honeypot \
  -H "x-api-key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-1",
    "message": {
      "sender": "scammer@example.com",
      "text": "Your account will be blocked. Verify your details now.",
      "timestamp": "2026-01-21T10:15:30Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

### Expected Response

```json
{
  "status": "success",
  "sessionId": "test-session-1",
  "scamDetected": true,
  "scamProbability": 0.95,
  "reply": "I'm concerned about this message. Can you provide more details?",
  "intelligence": {
    "bankAccounts": [],
    "upiIds": [],
    "phoneNumbers": ["1234567890"],
    "links": [],
    "emails": ["scammer@example.com"]
  },
  "turn": 1
}
```

---

## 📡 API Reference

### POST `/api/honeypot`

Analyze a message, detect scams, generate a reply, and extract intelligence.

**Headers:**
```
x-api-key: your-secret-key
Content-Type: application/json
```

**Request Body:**
```json
{
  "sessionId": "string",
  "message": {
    "sender": "string",
    "text": "string",
    "timestamp": "ISO 8601 datetime"
  },
  "conversationHistory": [
    {
      "sender": "string",
      "text": "string",
      "timestamp": "ISO 8601 datetime"
    }
  ],
  "metadata": {
    "channel": "SMS|Email|Chat|Phone",
    "language": "string",
    "locale": "string"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "sessionId": "string",
  "scamDetected": boolean,
  "scamProbability": 0.0-1.0,
  "reply": "string (agent response)",
  "intelligence": {
    "bankAccounts": ["string"],
    "upiIds": ["string"],
    "phoneNumbers": ["string"],
    "links": ["string"],
    "emails": ["string"]
  },
  "turn": integer
}
```

---

## 🌐 Deployment

### Deployment Options

The application is designed for cloud deployment. We support:
- **Render** (recommended)
- **Railway**
- **Heroku** (with minor config changes)
- **Other Docker-compatible platforms**

### Quick Deployment (Render)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - New → Web Service
   - Connect your GitHub repo
   - Set Environment Variable: `API_KEY` = your-secret-key
   - Deploy

3. **Test Your Deployment**
   - Use the provided API Endpoint Tester
   - See [docs/DEPLOYMENT_FULL_GUIDE.md](docs/DEPLOYMENT_FULL_GUIDE.md)

For comprehensive deployment instructions, see:
- **Full Guide**: [docs/DEPLOYMENT_FULL_GUIDE.md](docs/DEPLOYMENT_FULL_GUIDE.md)
- **Quick Reference**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 📂 Project Structure

```
agentic-honey-pot/
├── app/
│   ├── main.py              # FastAPI application & routes
│   ├── config.py            # Configuration, environment variables
│   ├── models.py            # Pydantic request/response models
│   ├── detector.py          # Scam detection logic
│   ├── agent.py             # LLM integration & reply generation
│   ├── extractor.py         # Intelligence extraction (emails, phones, etc.)
│   ├── callback.py          # Callback service for external systems
│   └── session_store.py     # In-memory session state management
├── docs/
│   ├── README.md            # Documentation index
│   ├── ARCHITECTURE.md      # System design & component details
│   ├── DEPLOYMENT_FULL_GUIDE.md  # Complete deployment walkthrough
│   ├── MANUAL_SETUP_GUIDE.md     # Local environment setup
│   ├── TECH_STACK.md        # Technology details
│   └── diagrams/            # PlantUML architecture diagrams
├── tests/
│   └── test_phase11.py      # Test suite
├── requirements.txt         # Python dependencies
├── runtime.txt              # Python version specification
├── .env.example             # Example environment configuration
├── .gitignore               # Git ignore rules
├── Procfile                 # Deployment process definition
└── README.md                # This file
```

---

## 📚 Documentation

Complete documentation is available in the **[docs/](docs/)** directory:

| Document | Purpose |
|----------|---------|
| [docs/README.md](docs/README.md) | Documentation index & quick links |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, component overview, UML diagrams |
| [docs/DEPLOYMENT_FULL_GUIDE.md](docs/DEPLOYMENT_FULL_GUIDE.md) | Step-by-step deployment with testing |
| [docs/MANUAL_SETUP_GUIDE.md](docs/MANUAL_SETUP_GUIDE.md) | Local environment setup & verification |
| [docs/TECH_STACK.md](docs/TECH_STACK.md) | Technologies, dependencies, versions |
| [docs/HACKATHON_DETAILS.md](docs/HACKATHON_DETAILS.md) | Problem statement, API specifications |

---

## 🔧 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (0.104+)
- **Server**: [Uvicorn](https://www.uvicorn.org/) (0.24+)
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/) (2.0+)
- **LLM Integration**: [OpenAI Python Client](https://github.com/openai/openai-python) (1.0+)
- **HTTP Client**: [httpx](https://www.python-httpx.org/) (0.25+)
- **Environment**: [python-dotenv](https://github.com/theskumar/python-dotenv) (1.0+)
- **Runtime**: Python 3.11.9
- **Deployment**: Render / Railway / Docker

---

## 🛡️ Security Features

- **API Key Authentication**: All requests require valid `x-api-key` header
- **CORS Protection**: Configurable cross-origin request handling
- **Input Validation**: Pydantic models ensure data integrity
- **Rate Limiting Ready**: Architecture supports middleware for rate limiting
- **Error Handling**: Graceful fallbacks and error logging
- **Environment Secrets**: Sensitive credentials stored in `.env` (never committed)

---

## 📝 Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4

# Application Security
API_KEY=your-secret-api-key-here

# GUVI Callback
GUVI_CALLBACK_URL=https://guvi.example.com/callback
```

Never commit `.env` to version control.

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** with clear commit messages
4. **Write or update tests** for new functionality
5. **Push to your fork**: `git push origin feature/your-feature-name`
6. **Open a Pull Request** with a detailed description

### Development Guidelines

- Follow PEP 8 style guide
- Write docstrings for all functions and modules
- Add unit tests for new features
- Update documentation as needed
- Keep commit messages clear and descriptive

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 💡 Use Cases

- **Financial Institutions**: Detect and analyze fraudulent SMS/email attacks on customer accounts
- **Telecom Operators**: Identify scam patterns across network traffic
- **E-commerce Platforms**: Monitor and counter phishing attempts targeting users
- **Law Enforcement**: Gather intelligence on active scam operations for investigation
- **Security Research**: Analyze scammer tactics and methods for prevention

---

## 🎓 Acknowledgments

Built for the **GUVI Hackathon** — Agentic Honey-Pot for Scam Detection & Intelligence Extraction.

---

## 📧 Support

For issues, questions, or suggestions:

1. **Check existing documentation**: [docs/](docs/)
2. **Review test cases**: [tests/](tests/)
3. **Open an issue** on GitHub with detailed description
4. **Check test requirements**: [docs/TESTER_REQUIREMENTS.md](docs/TESTER_REQUIREMENTS.md)

---

**Made with ❤️ for cybersecurity**
