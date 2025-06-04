#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

print('=== DEBUGGING HEALTH CHECK ISSUES ===')

# Test basic imports
try:
    print('1. Testing basic imports...')
    from main import app
    from voice.ai_service import AIService
    from voice.call_manager import CallManager
    from voice.twilio_handler import TwilioHandler
    from government.brushy_creek import BrushyCreekMUD
    from config.settings import Settings
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test settings
try:
    print('\n2. Testing settings...')
    settings = Settings()
    print(f'TWILIO_ACCOUNT_SID: {settings.twilio_account_sid[:10] if settings.twilio_account_sid else "MISSING"}...')
    print(f'TWILIO_AUTH_TOKEN: {"SET" if settings.twilio_auth_token else "MISSING"}')
    print(f'OPENAI_API_KEY: {"SET" if settings.openai_api_key else "MISSING"}')
    print(f'PORT: {settings.app_port}')
    print(f'WEBHOOK_BASE_URL: {settings.webhook_base_url}')
    print('✅ Settings loaded')
except Exception as e:
    print(f'❌ Settings error: {e}')
    import traceback
    traceback.print_exc()

# Test service initialization
try:
    print('\n3. Testing service initialization...')
    call_manager = CallManager()
    government_service = BrushyCreekMUD()
    twilio_handler = TwilioHandler(call_manager, government_service)
    
    print(f'Twilio configured (before init): {twilio_handler.is_configured()}')
    print('✅ Services created')
except Exception as e:
    print(f'❌ Service creation error: {e}')
    import traceback
    traceback.print_exc()

# Test async initialization
try:
    print('\n4. Testing async initialization...')
    import asyncio
    
    async def test_async():
        await call_manager.initialize()
        print(f'AI service configured: {call_manager.ai_service.is_configured()}')
        
        # Test health check logic
        twilio_status = twilio_handler.is_configured()
        openai_status = call_manager.ai_service.is_configured()
        government_status = True
        
        print(f'Twilio status: {twilio_status}')
        print(f'OpenAI status: {openai_status}')
        print(f'Government status: {government_status}')
        
        overall_status = "healthy" if twilio_status and openai_status and government_status else "unhealthy"
        print(f'Overall health: {overall_status}')
    
    asyncio.run(test_async())
    print('✅ Async initialization successful')
except Exception as e:
    print(f'❌ Async initialization error: {e}')
    import traceback
    traceback.print_exc()

print('\n=== DEBUG COMPLETE ===') 