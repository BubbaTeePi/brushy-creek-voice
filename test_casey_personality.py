#!/usr/bin/env python3
"""
Test script to see Casey's cheerful personality in action
"""

import asyncio
from voice.call_manager import CallManager
from government.brushy_creek import BrushyCreekMUD

async def test_casey_personality():
    """Test Casey's new cheerful personality"""
    print("🎭 Testing Casey's Cheerful Personality...")
    
    call_manager = CallManager()
    government = BrushyCreekMUD()
    
    await call_manager.initialize()
    
    try:
        if not call_manager.ai_service.is_configured():
            print("⚠️  AI Service not configured (missing OpenAI API key)")
            return
        
        # Get government context
        context = await government.get_context_for_ai()
        
        # Test various scenarios with Casey
        test_scenarios = [
            "What are your water rates?",
            "I have a water emergency!",
            "How do I pay my bill?", 
            "What are your hours?",
            "I need help with recycling"
        ]
        
        print(f"\n💬 Testing Casey's responses with {call_manager.ai_service.settings.ai_model}:")
        print("="*60)
        
        for scenario in test_scenarios:
            print(f"\n👤 User: {scenario}")
            
            response = await call_manager.ai_service.generate_response(
                user_input=scenario,
                conversation_history=[],
                government_context=context
            )
            
            print(f"🤖 Casey: {response}")
            print("-" * 40)
            
        print("\n✅ Casey personality test complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        await call_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(test_casey_personality()) 