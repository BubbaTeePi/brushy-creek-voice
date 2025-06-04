#!/usr/bin/env python3
"""
Startup script for the Local Government AI Voice Service
"""

import os
import sys
from pathlib import Path
import asyncio
from dotenv import load_dotenv
import uvicorn

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config.settings import Settings
from voice.call_manager import CallManager
from government.brushy_creek import BrushyCreekMUD

def check_requirements():
    """Check if all required dependencies are installed"""
    required_packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'), 
        ('twilio', 'twilio'),
        ('openai', 'openai'),
        ('redis', 'redis'),
        ('pydantic', 'pydantic'),
        ('pydantic-settings', 'pydantic_settings'),
        ('python-dotenv', 'dotenv')
    ]
    
    missing_packages = []
    for pkg_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pkg_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\nInstall them with: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are installed")
    return True

def validate_environment():
    """Validate environment configuration"""
    load_dotenv()
    settings = Settings()
    
    issues = []
    warnings = []
    
    # Check critical settings
    if not settings.openai_api_key:
        issues.append("OpenAI API key not set (OPENAI_API_KEY)")
    
    if not settings.twilio_account_sid:
        warnings.append("Twilio Account SID not set (TWILIO_ACCOUNT_SID)")
    
    if not settings.twilio_auth_token:
        warnings.append("Twilio Auth Token not set (TWILIO_AUTH_TOKEN)")
    
    if not settings.twilio_phone_number:
        warnings.append("Twilio Phone Number not set (TWILIO_PHONE_NUMBER)")
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        warnings.append(".env file not found - using default values")
        print("💡 Copy env.example to .env and configure your API keys")
    
    # Report issues
    if issues:
        print("❌ Configuration Issues:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    if warnings:
        print("⚠️  Configuration Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
    
    print("✅ Environment configuration validated")
    return True

async def test_services():
    """Test that services can initialize properly"""
    print("🔧 Testing service initialization...")
    
    try:
        # Test CallManager initialization
        call_manager = CallManager()
        await call_manager.initialize()
        
        # Test AI service
        if call_manager.ai_service.is_configured():
            print("✅ OpenAI service initialized")
        else:
            print("⚠️  OpenAI service not configured (API key missing)")
        
        # Test government service
        government_service = BrushyCreekMUD()
        basic_info = await government_service.get_basic_info()
        print(f"✅ Government service initialized: {basic_info['name']}")
        
        # Cleanup
        await call_manager.cleanup()
        
        return True
        
    except Exception as e:
        print(f"❌ Service initialization failed: {e}")
        return False

def show_startup_info():
    """Show startup information and next steps"""
    settings = Settings()
    
    print("\n" + "="*60)
    print("🎉 LOCAL GOVERNMENT AI VOICE SERVICE")
    print("="*60)
    print(f"Government: Brushy Creek Municipal Utility District")
    print(f"Host: {settings.app_host}")
    print(f"Port: {settings.app_port}")
    print(f"Debug Mode: {settings.debug}")
    print("="*60)
    
    print("\n📋 NEXT STEPS:")
    print("1. Configure your API keys in .env file:")
    print("   - Get Twilio credentials: https://www.twilio.com/console")
    print("   - Get OpenAI API key: https://platform.openai.com/api-keys")
    
    print("\n2. Set up Twilio webhook:")
    webhook_url = settings.get_webhook_url("voice/incoming")
    print(f"   - Webhook URL: {webhook_url}")
    print("   - Configure this URL in your Twilio phone number settings")
    
    print("\n3. Test the service:")
    print("   - Call your Twilio phone number")
    print("   - Check the logs for any issues")
    print("   - Visit http://localhost:8000 for health check")
    
    print("\n4. Monitor the service:")
    print("   - Check /health endpoint for service status")
    print("   - View active calls at /voice/status/{call_sid}")
    
    print("\n🔧 DEVELOPMENT:")
    print("   - API documentation: http://localhost:8000/docs")
    print("   - Government info: http://localhost:8000/government/info")
    
    print("\n" + "="*60)

def start_server():
    """Start the FastAPI server with production settings"""
    settings = Settings()
    
    # Use PORT environment variable (Railway, Heroku, etc.)
    port = int(os.getenv("PORT", settings.app_port))
    
    # Production vs development settings
    if settings.debug:
        # Development mode
        uvicorn.run(
            "main:app",
            host=settings.app_host,
            port=port,
            reload=True,
            access_log=True
        )
    else:
        # Production mode
        uvicorn.run(
            "main:app",
            host=settings.app_host,
            port=port,
            reload=False,
            access_log=False,
            workers=1  # Single worker for voice service consistency
        )

if __name__ == "__main__":
    start_server() 