#!/usr/bin/env python3
"""
Test script to verify voice service setup
"""

import os
from dotenv import load_dotenv

def test_environment():
    """Test that environment variables are loaded correctly"""
    
    # Load environment variables
    load_dotenv()
    
    print("🧪 Testing Environment Setup...")
    print("=" * 50)
    
    # Check Twilio
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    if twilio_sid and twilio_token and twilio_number:
        print("✅ Twilio credentials loaded")
        print(f"   📞 Phone: {twilio_number}")
        print(f"   🆔 SID: {twilio_sid[:8]}...")
        
        # Test Twilio connection
        try:
            from twilio.rest import Client
            client = Client(twilio_sid, twilio_token)
            numbers = client.incoming_phone_numbers.list()
            print(f"   ✅ Connection successful ({len(numbers)} numbers)")
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
    else:
        print("❌ Twilio credentials missing")
    
    # Check OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key != 'your_openai_api_key_here':
        print("✅ OpenAI API key loaded")
        print(f"   🔑 Key: {openai_key[:8]}...")
        
        # Test OpenAI connection (optional)
        try:
            import openai
            openai.api_key = openai_key
            # Don't actually test to avoid charges
            print("   ✅ Ready for testing")
        except Exception as e:
            print(f"   ⚠️  OpenAI module issue: {e}")
    else:
        print("❌ OpenAI API key needed!")
        print("   Go to: https://platform.openai.com/api-keys")
    
    # Check security keys
    jwt_key = os.getenv('JWT_SECRET_KEY')
    encryption_key = os.getenv('ENCRYPTION_KEY')
    
    if jwt_key and encryption_key:
        print("✅ Security keys generated")
    else:
        print("❌ Security keys missing")
    
    print("=" * 50)
    
    if twilio_sid and openai_key and openai_key != 'your_openai_api_key_here':
        print("🎉 Setup complete! Ready to start voice service")
        print("🚀 Run: python3 start.py")
    else:
        print("⚠️  Setup incomplete - add OpenAI API key")

def test_imports():
    """Test that required modules can be imported"""
    
    print("\n🧪 Testing Module Imports...")
    print("=" * 50)
    
    required_modules = [
        'twilio',
        'openai', 
        'fastapi',
        'uvicorn',
        'dotenv'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - Run: pip3 install {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  Install missing modules:")
        print(f"pip3 install {' '.join(missing_modules)}")
    else:
        print("\n✅ All modules available!")

if __name__ == "__main__":
    test_environment()
    test_imports() 