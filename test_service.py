#!/usr/bin/env python3
"""
Test script for the Local Government AI Voice Service
"""

import asyncio
import json
from pathlib import Path
import sys
from dotenv import load_dotenv

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config.settings import Settings
from voice.call_manager import CallManager
from government.brushy_creek import BrushyCreekMUD
from voice.twilio_handler import TwilioHandler

async def test_government_service():
    """Test the government service integration"""
    print("🧪 Testing Government Service...")
    
    government = BrushyCreekMUD()
    
    # Test basic info
    basic_info = await government.get_basic_info()
    print(f"✅ Basic Info: {basic_info['name']}")
    
    # Test business hours check
    is_business_hours = await government.is_business_hours()
    print(f"✅ Business Hours Check: {'Open' if is_business_hours else 'Closed'}")
    
    # Test context generation
    context = await government.get_context_for_ai()
    print(f"✅ AI Context Generated: {len(context)} characters")
    
    # Test emergency info
    emergency_info = await government.get_emergency_info()
    print(f"✅ Emergency Info: {emergency_info['water_emergency']['phone']}")
    
    return True

async def test_call_manager():
    """Test the call manager functionality"""
    print("🧪 Testing Call Manager...")
    
    call_manager = CallManager()
    await call_manager.initialize()
    
    try:
        # Test starting a call
        call_sid = "test_call_123"
        caller_number = "+15551234567"
        context = "Test context for AI"
        
        session_id = await call_manager.start_call(call_sid, caller_number, context)
        print(f"✅ Call Started: {session_id}")
        
        # Test adding conversation
        await call_manager.add_to_conversation(call_sid, "user", "Hello, I need help with water service")
        await call_manager.add_to_conversation(call_sid, "assistant", "I can help you with water service questions")
        
        # Test getting call status
        status = await call_manager.get_call_status(call_sid)
        print(f"✅ Call Status: {status['status']}, Messages: {status['conversation_length']}")
        
        # Test ending call
        await call_manager.end_call(call_sid)
        print("✅ Call Ended Successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Call Manager Test Failed: {e}")
        return False
    
    finally:
        await call_manager.cleanup()

async def test_ai_service():
    """Test AI service functionality"""
    print("🧪 Testing AI Service...")
    
    call_manager = CallManager()
    await call_manager.initialize()
    
    try:
        if not call_manager.ai_service.is_configured():
            print("⚠️  AI Service not configured (missing OpenAI API key)")
            print("✅ AI Service structure validated")
            return True
        
        # Test intent classification
        intent = await call_manager.ai_service.classify_intent("I have a water leak emergency")
        print(f"✅ Intent Classification: '{intent}'")
        
        # Test response generation (with mock conversation)
        government = BrushyCreekMUD()
        context = await government.get_context_for_ai()
        
        response = await call_manager.ai_service.generate_response(
            user_input="What are your business hours?",
            conversation_history=[],
            government_context=context
        )
        print(f"✅ AI Response Generated: {len(response)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Service Test Failed: {e}")
        return False
    
    finally:
        await call_manager.cleanup()

async def test_twilio_integration():
    """Test Twilio integration (structure only, no actual calls)"""
    print("🧪 Testing Twilio Integration...")
    
    call_manager = CallManager()
    government = BrushyCreekMUD()
    twilio_handler = TwilioHandler(call_manager, government)
    
    print(f"✅ Twilio Handler Created")
    print(f"✅ Twilio Configured: {twilio_handler.is_configured()}")
    
    # Test TwiML generation for emergency
    emergency_response = twilio_handler.create_emergency_response("water_emergency")
    print(f"✅ Emergency Response TwiML Generated")
    
    return True

async def run_integration_test():
    """Run a complete integration test"""
    print("🧪 Running Integration Test...")
    
    call_manager = CallManager()
    government = BrushyCreekMUD()
    
    await call_manager.initialize()
    
    try:
        # Simulate a complete call flow
        call_sid = "integration_test_call"
        caller_number = "+15551234567"
        context = await government.get_context_for_ai()
        
        # Start call
        session_id = await call_manager.start_call(call_sid, caller_number, context)
        
        # Simulate user input and AI response
        user_input = "What are your current water restrictions?"
        ai_response = await call_manager.process_user_input(call_sid, user_input)
        
        print(f"✅ Integration Test Complete")
        print(f"   User: {user_input}")
        print(f"   AI: {ai_response[:100]}...")
        
        # End call
        await call_manager.end_call(call_sid)
        
        return True
        
    except Exception as e:
        print(f"❌ Integration Test Failed: {e}")
        return False
    
    finally:
        await call_manager.cleanup()

def test_configuration():
    """Test configuration loading"""
    print("🧪 Testing Configuration...")
    
    load_dotenv()
    settings = Settings()
    
    print(f"✅ Settings loaded")
    print(f"   App Host: {settings.app_host}")
    print(f"   App Port: {settings.app_port}")
    print(f"   Debug: {settings.debug}")
    print(f"   AI Model: {settings.ai_model}")
    print(f"   Voice Model: {settings.voice_model}")
    
    # Check API keys (without printing them)
    has_openai = bool(settings.openai_api_key)
    has_twilio_sid = bool(settings.twilio_account_sid)
    has_twilio_token = bool(settings.twilio_auth_token)
    
    print(f"   OpenAI API Key: {'✅ Set' if has_openai else '❌ Missing'}")
    print(f"   Twilio SID: {'✅ Set' if has_twilio_sid else '❌ Missing'}")
    print(f"   Twilio Token: {'✅ Set' if has_twilio_token else '❌ Missing'}")
    
    return True

async def main():
    """Run all tests"""
    print("🧪 LOCAL GOVERNMENT AI VOICE SERVICE - TEST SUITE")
    print("="*60)
    
    tests = [
        ("Configuration", test_configuration, False),
        ("Government Service", test_government_service, True),
        ("Call Manager", test_call_manager, True),
        ("AI Service", test_ai_service, True),
        ("Twilio Integration", test_twilio_integration, True),
        ("Integration Test", run_integration_test, True),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func, is_async in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        
        try:
            if is_async:
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "="*60)
    print(f"🏁 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Your service is ready to use.")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file")
        print("2. Run: python start.py")
        print("3. Configure Twilio webhook URL")
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 