# Local Government AI Voice Service

A low-latency voice service that provides AI-enabled customer support for local government services, starting with Brushy Creek Municipal Utility District (BCMUD).

## Features

- **Real-time Voice Processing**: Low-latency speech-to-text and text-to-speech
- **AI-Powered Responses**: Context-aware customer support using OpenAI GPT
- **Multi-Government Compatible**: Modular design for easy integration with different municipalities
- **24/7 Availability**: Automated support outside business hours
- **Intelligent Routing**: Can escalate to human agents when needed

## Architecture

- **Voice Interface**: Twilio Voice API for phone calls
- **Speech Processing**: OpenAI Whisper (STT) and TTS
- **AI Engine**: OpenAI GPT-4 for intelligent responses
- **Backend**: Python FastAPI with WebSocket support
- **Database**: PostgreSQL for logging and knowledge base
- **Caching**: Redis for fast response times

## Current Implementation: Brushy Creek MUD

The initial implementation supports:
- Water service inquiries and restrictions
- Community center, pool, and park information
- Event schedules and registration
- Emergency contact routing
- Business hours and contact information

## Setup Requirements

### API Keys Needed:
1. **Twilio Account**: https://www.twilio.com/
   - Account SID, Auth Token
   - Phone number for incoming calls
2. **OpenAI API**: https://platform.openai.com/
   - API key for GPT-4 and Whisper/TTS
3. **Optional**: Google Cloud Speech-to-Text for backup STT

### Environment Variables:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `OPENAI_API_KEY`
- `DATABASE_URL`
- `REDIS_URL`

## Installation

```bash
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Phone Number Setup

1. Get a Twilio phone number
2. Configure webhook URL: `https://yourdomain.com/voice/incoming`
3. Enable Voice capabilities

## Usage

Call the configured phone number to interact with the AI assistant for Brushy Creek MUD services.

## Development

- `main.py`: FastAPI application entry point
- `voice/`: Voice processing and Twilio integration
- `ai/`: AI response generation and context management
- `government/`: Government-specific integrations
- `config/`: Configuration and knowledge bases 