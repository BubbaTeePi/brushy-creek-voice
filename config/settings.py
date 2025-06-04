from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Twilio Configuration
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    # OpenAI Configuration
    openai_api_key: str = ""
    
    # ElevenLabs Configuration (Higher Quality Voice)
    elevenlabs_api_key: str = ""
    use_elevenlabs: bool = True  # Switch to ElevenLabs for better voice
    
    # Database Configuration
    database_url: str = "sqlite:///./voice_service.db"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # Application Configuration
    app_host: str = "0.0.0.0"
    app_port: int = int(os.getenv("PORT", 8000))  # Railway/Heroku use PORT env var
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"  # Production should be false
    
    # Webhook Configuration
    webhook_base_url: str = os.getenv("WEBHOOK_BASE_URL", "https://localhost:8000")
    
    # AI Configuration (OPTIMIZED FOR VOICE INTERRUPTION)
    ai_model: str = "gpt-4o"  # Latest high-speed model with excellent performance
    max_tokens: int = 25  # MUCH shorter for voice - 20-30 words max to allow interruptions
    temperature: float = 0.3  # More consistent personality
    
    # Voice Configuration - OpenAI Fallback
    voice_model: str = "tts-1-hd"
    voice_name: str = "nova"
    speech_speed: float = 1.1  # Slightly faster for efficiency
    
    # ElevenLabs Voice Configuration (MUCH BETTER QUALITY)
    elevenlabs_voice_id: str = "g6xIsTj2HwM6VR4iXFCw"  # Jessica Anne Bogart - Empathetic customer service
    elevenlabs_model: str = "eleven_flash_v2_5"  # Fastest model for low latency
    elevenlabs_stability: float = 0.4  # More dynamic, emotional delivery  
    elevenlabs_similarity_boost: float = 0.8  # Higher clarity
    elevenlabs_style: float = 0.2  # Slight style variation
    elevenlabs_speed: float = 1.1  # Slightly faster to reduce interruption time
    
    # Timeouts (OPTIMIZED FOR INTERRUPTION)
    call_timeout: int = 180  # 3 minutes max call
    response_timeout: int = 5  # 5 seconds max AI response
    
    # Twilio Gather Configuration (OPTIMIZED FOR INTERRUPTION)
    gather_timeout: int = 2  # Reduced to 2 seconds for faster interruption detection
    gather_finish_on_key: str = "#"  # Allow # to finish input
    gather_partial_result_callback: bool = True  # Enable partial results
    gather_speech_timeout: str = "1"  # Very short speech timeout for interruption
    
    # Security Configuration
    jwt_secret_key: str = ""
    encryption_key: str = ""
    webhook_secret: str = ""
    
    # Additional AI Configuration
    ai_max_tokens: int = 500
    speech_model: str = "whisper-1"
    
    # Government Service Configuration
    government_service: str = "brushy_creek_mud"
    
    # Compliance Configuration
    audit_level: str = "standard"
    compliance_frameworks: str = "FISMA,NIST,SOC2"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.debug
        
    def get_webhook_url(self, endpoint: str) -> str:
        """Get full webhook URL for Twilio"""
        return f"{self.webhook_base_url.rstrip('/')}/{endpoint.lstrip('/')}" 