import asyncio
from typing import List, Dict, Optional
import openai
import httpx
import io
from pydub import AudioSegment
import tempfile
import os
import hashlib
from functools import lru_cache
import time

# ElevenLabs import
try:
    from elevenlabs import ElevenLabs, Voice, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    print("ElevenLabs not available, using OpenAI TTS as fallback")

from config.settings import Settings

class AIService:
    """AI service for handling OpenAI integration with ElevenLabs voice"""
    
    def __init__(self):
        self.settings = Settings()
        self.openai_client = None
        self.elevenlabs_client = None
        self.is_initialized = False
        self.response_cache = {}  # Simple cache for common responses
    
    async def initialize(self):
        """Initialize the OpenAI and ElevenLabs clients"""
        # Initialize OpenAI
        if not self.settings.openai_api_key:
            print("Warning: OpenAI API key not provided")
        else:
            try:
                self.openai_client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)
                # Test the connection
                await self.openai_client.models.list()
                print("OpenAI client initialized successfully")
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
        
        # Initialize ElevenLabs if enabled and available
        if self.settings.use_elevenlabs and ELEVENLABS_AVAILABLE:
            if self.settings.elevenlabs_api_key:
                try:
                    self.elevenlabs_client = ElevenLabs(api_key=self.settings.elevenlabs_api_key)
                    print("ElevenLabs client initialized successfully")
                except Exception as e:
                    print(f"Error initializing ElevenLabs client: {e}")
                    print("Falling back to OpenAI TTS")
                    self.elevenlabs_client = None
            else:
                print("ElevenLabs API key not provided, using OpenAI TTS")
        
        self.is_initialized = True
    
    def is_configured(self) -> bool:
        """Check if the AI service is properly configured"""
        return self.is_initialized and self.openai_client is not None
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for responses"""
        return hashlib.md5(text.lower().strip().encode()).hexdigest()
    
    async def generate_response(self, user_input: str, conversation_history: List[Dict], government_context: str) -> str:
        """Generate an AI response using OpenAI GPT with caching for speed"""
        if not self.is_configured():
            return "AI service is not available at the moment. Please try again later."
        
        # Check cache for common responses
        cache_key = self._get_cache_key(user_input)
        if cache_key in self.response_cache:
            print(f"Using cached response for: {user_input[:50]}...")
            return self.response_cache[cache_key]
        
        try:
            # Build optimized messages for faster response
            messages = [
                {
                    "role": "system", 
                    "content": f"""You are Casey, a cheerful and knowledgeable AI assistant for Brushy Creek Municipal Utility District! 

🌟 YOUR PERSONALITY:
- You're genuinely excited to help residents with their utility needs
- You have a warm, friendly demeanor like a helpful neighbor who works at city hall  
- You're knowledgeable and well-informed about the district's services
- You care about your community and take pride in providing accurate information
- You're optimistic and solution-focused

🎯 CRITICAL FOR VOICE CALLS - BE HELPFUL, NOT A DEFLECTOR:
- Maximum 15-20 words per response for voice calls
- USE the detailed knowledge base - don't always say "call customer service"
- Give SPECIFIC helpful answers when you have the information
- Only refer to customer service for complex account issues or emergencies

📚 YOU HAVE EXTENSIVE KNOWLEDGE - USE IT:
{government_context}

🗣️ VOICE RESPONSE EXAMPLES - BE HELPFUL:

WATER RATES (Don't deflect - give the answer!):
❌ Wrong: "For billing questions, call customer service"
✅ Right: "Water: $20 base plus $3.50-4.70 per 1000 gallons. Anything else?"

WATER QUALITY (Use your knowledge!):
❌ Wrong: "Call customer service for water issues"  
✅ Right: "Cloudy water is usually air bubbles - harmless. Clears in minutes."

TRASH/RECYCLING (You know this!):
❌ Wrong: "Contact customer service about trash"
✅ Right: "Garbage weekly, recycling every other week. $24 monthly."

COMMUNITY CENTER HOURS (You have this info!):
❌ Wrong: "Call for hours information"
✅ Right: "Community Center: Mon-Fri 5:30am-9pm, weekends vary."

ONLY DEFLECT FOR:
- Account-specific billing problems
- Water emergencies (give emergency number immediately)
- Complex service requests
- Things requiring account access

🎯 YOUR GOAL: Be the helpful neighborhood expert who knows answers!
- Residents should get helpful info from YOU, not always be told to call
- Use your knowledge base to solve common questions immediately  
- Keep responses brief but informative
- End with "Anything else?" to show you're ready for more

REMEMBER: You're not just a receptionist - you're a knowledgeable assistant! 🌞"""
                }
            ]
            
            # Add only the last 3 messages to reduce context size and improve speed
            recent_history = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
            for msg in recent_history:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current user input
            messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Generate response with faster model
            start_time = time.time()
            response = await self.openai_client.chat.completions.create(
                model=self.settings.ai_model,  # Now using gpt-4o-mini for speed
                messages=messages,
                max_tokens=self.settings.max_tokens,  # Reduced to 75
                temperature=self.settings.temperature,  # Reduced to 0.4
                timeout=self.settings.response_timeout  # 5 seconds max
            )
            
            response_text = response.choices[0].message.content.strip()
            response_time = time.time() - start_time
            print(f"AI response generated in {response_time:.2f}s")
            
            # Cache common responses for future speed
            if len(user_input) < 50:  # Cache short queries
                self.response_cache[cache_key] = response_text
            
            return response_text
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "I'm having trouble right now. Please call our main number at (512) 255-4652 for immediate assistance."
    
    async def transcribe_audio(self, audio_url: str) -> str:
        """Transcribe audio using OpenAI Whisper"""
        if not self.is_configured():
            return "Sorry, I couldn't understand what you said. Please try again."
        
        try:
            # Download the audio file
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url, timeout=10)
                response.raise_for_status()
                audio_data = response.content
            
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe using Whisper
                with open(temp_file_path, "rb") as audio_file:
                    transcript = await self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="en"
                    )
                
                return transcript.text.strip()
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return "Sorry, I couldn't understand what you said. Please speak clearly and try again."
    
    async def generate_speech(self, text: str) -> bytes:
        """Generate speech using ElevenLabs (preferred) or OpenAI TTS (fallback)"""
        if not self.is_configured():
            raise Exception("AI service not configured")
        
        # Try ElevenLabs first for much better quality
        if self.settings.use_elevenlabs and self.elevenlabs_client and ELEVENLABS_AVAILABLE:
            try:
                start_time = time.time()
                
                # Generate speech with ElevenLabs using the correct client API
                audio = self.elevenlabs_client.text_to_speech.convert(
                    voice_id=self.settings.elevenlabs_voice_id,
                    text=text,
                    model_id=self.settings.elevenlabs_model,
                    voice_settings=VoiceSettings(
                        stability=self.settings.elevenlabs_stability,
                        similarity_boost=self.settings.elevenlabs_similarity_boost,
                        style=self.settings.elevenlabs_style,
                        use_speaker_boost=True
                    )
                )
                
                # Convert to bytes (audio should be bytes from the generate method)
                if hasattr(audio, 'content'):
                    audio_bytes = audio.content
                elif isinstance(audio, bytes):
                    audio_bytes = audio
                else:
                    # Handle iterator/generator case
                    audio_bytes = b''.join(audio)
                
                generation_time = time.time() - start_time
                print(f"ElevenLabs speech generated in {generation_time:.2f}s")
                
                return audio_bytes
                
            except Exception as e:
                print(f"ElevenLabs error, falling back to OpenAI: {e}")
        
        # Fallback to OpenAI TTS
        try:
            start_time = time.time()
            response = await self.openai_client.audio.speech.create(
                model=self.settings.voice_model,
                voice=self.settings.voice_name,
                input=text,
                speed=self.settings.speech_speed,
                response_format="mp3"
            )
            
            generation_time = time.time() - start_time
            print(f"OpenAI TTS generated in {generation_time:.2f}s")
            
            return response.content
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            raise Exception(f"Speech generation failed: {e}")
    
    async def generate_summary(self, conversation_text: str) -> str:
        """Generate a summary of the conversation"""
        if not self.is_configured():
            return "Summary unavailable - AI service not configured"
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.settings.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize this customer service conversation in 2-3 sentences, focusing on the main request and outcome."
                    },
                    {
                        "role": "user",
                        "content": f"Conversation:\n{conversation_text}"
                    }
                ],
                max_tokens=100,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Summary generation failed"
    
    async def classify_intent(self, user_input: str) -> str:
        """Classify the user's intent to help route the conversation"""
        if not self.is_configured():
            return "general"
        
        # Check cache for intent classification
        cache_key = f"intent_{self._get_cache_key(user_input)}"
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.settings.ai_model,  # Use fast model for classification
                messages=[
                    {
                        "role": "system",
                        "content": """Classify the user's intent into one of these categories:
- water_emergency: water outages, leaks, or urgent water issues
- water_service: billing, restrictions, general water service questions  
- facilities: community center, pools, parks questions
- events: upcoming events, registration, schedules
- general: general information, hours, contact info
- complaint: complaints or issues to escalate

Respond with only the category name."""
                    },
                    {
                        "role": "user", 
                        "content": user_input
                    }
                ],
                max_tokens=20,
                temperature=0.1
            )
            
            intent = response.choices[0].message.content.strip().lower()
            valid_intents = ["water_emergency", "water_service", "facilities", "events", "general", "complaint"]
            
            result = intent if intent in valid_intents else "general"
            
            # Cache the result
            self.response_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            print(f"Error classifying intent: {e}")
            return "general" 