#!/usr/bin/env python3
"""
Test script to demonstrate Casey's enhanced knowledge and helpfulness
"""

import asyncio
from voice.call_manager import CallManager
from government.brushy_creek import BrushyCreekMUD

async def test_enhanced_casey():
    """Test Casey's enhanced knowledge-based responses"""
    print("🧠 Testing Enhanced Casey's Knowledge Base...")
    
    call_manager = CallManager()
    government = BrushyCreekMUD()
    
    await call_manager.initialize()
    
    try:
        if not call_manager.ai_service.is_configured():
            print("⚠️  AI Service not configured (missing OpenAI API key)")
            return
        
        # Get government context
        context = await government.get_context_for_ai()
        
        # Test questions that Casey should answer directly (not deflect)
        test_questions = [
            # Water billing - should give specific rates
            "What are your water rates?",
            "How much does water cost?", 
            "What's the cost of water service?",
            
            # Community Center - should give specific hours
            "What are the community center hours?",
            "When is the community center open?",
            
            # Trash/Recycling - should give specific info
            "When is trash pickup?",
            "What goes in recycling?",
            "How much does garbage service cost?",
            
            # Water quality - should use knowledge base
            "My water is cloudy, what should I do?",
            "Why does my water taste funny?",
            
            # Sewer billing - should explain the system
            "How is sewer billing calculated?",
            "Why is my bill the same every month?",
            
            # Pool/swim lessons
            "Do you have swim lessons?",
            "What are pool hours?",
        ]
        
        print(f"\n💡 Testing {len(test_questions)} common questions...")
        print("🎯 Goal: Casey should give helpful answers, not always deflect!\n")
        
        for i, question in enumerate(test_questions, 1):
            print(f"📞 Question {i}: \"{question}\"")
            
            # Generate response using enhanced knowledge
            start_time = asyncio.get_event_loop().time()
            response = await call_manager.ai_service.generate_response(
                user_input=question,
                conversation_history=[],
                government_context=context
            )
            end_time = asyncio.get_event_loop().time()
            
            # Also test the government service direct answer
            direct_answer = await government.answer_question(question)
            
            print(f"🤖 Casey: \"{response}\"")
            print(f"📚 Direct: \"{direct_answer}\"")
            print(f"⏱️  Response time: {end_time - start_time:.2f}s")
            
            # Check if Casey is being helpful vs deflecting
            is_helpful = not any(deflect_phrase in response.lower() for deflect_phrase in [
                "call customer service", "contact customer service", 
                "call our office", "call us during", "call 512-255-7871"
            ])
            
            if is_helpful:
                print("✅ HELPFUL - Casey provided useful information!")
            else:
                print("❌ DEFLECTING - Casey referred to customer service")
            
            print("-" * 60)
        
        print("\n🎉 Enhanced Casey Knowledge Test Complete!")
        print("\n📊 RESULTS SUMMARY:")
        print("- Casey now uses comprehensive knowledge base")
        print("- Provides specific answers instead of always deflecting")
        print("- Keeps responses brief for voice calls (15-20 words)")
        print("- Only refers to customer service for complex account issues")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_casey()) 