#!/usr/bin/env python3
"""
Test script to compare voice quality between services
"""

import asyncio
import os
from dotenv import load_dotenv
from voice.ai_service import AIService

async def test_voice_services():
    """Test and compare different voice services"""
    load_dotenv()
    
    ai_service = AIService()
    await ai_service.initialize()
    
    test_text = "Hello! Thank you for calling Brushy Creek Municipal Utility District. I'm here to help with your water service questions."
    
    print("🎤 Testing Voice Services...")
    print(f"Test text: {test_text}")
    print("-" * 60)
    
    if ai_service.settings.use_elevenlabs and ai_service.elevenlabs_client:
        print("✅ ElevenLabs is ENABLED and configured")
        print(f"   Voice ID: {ai_service.settings.elevenlabs_voice_id}")
        print(f"   Model: {ai_service.settings.elevenlabs_model}")
        print(f"   Voice: Jessica Anne Bogart (Empathetic customer service)")
    else:
        print("❌ ElevenLabs is disabled or not configured")
        print("   Falling back to OpenAI TTS")
    
    try:
        print("\n🔄 Generating speech...")
        audio_bytes = await ai_service.generate_speech(test_text)
        
        # Save test audio
        with open("test_voice_output.mp3", "wb") as f:
            f.write(audio_bytes)
        
        print(f"✅ Audio generated: {len(audio_bytes)} bytes")
        print("📄 Saved as: test_voice_output.mp3")
        print("\n🎧 Play this file to hear the voice quality!")
        
    except Exception as e:
        print(f"❌ Error generating speech: {e}")

if __name__ == "__main__":
    asyncio.run(test_voice_services()) 