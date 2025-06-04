#!/usr/bin/env python3

import asyncio
from government.brushy_creek import BrushyCreekMUD
from datetime import datetime

async def test_greeting():
    gov = BrushyCreekMUD()
    
    # Check current time
    now = datetime.now()
    print(f"Current time: {now.strftime('%A %I:%M %p')}")
    
    # Check if business hours
    is_business = await gov.is_business_hours()
    print(f"Is business hours: {is_business}")
    
    # Get the greeting that would be used
    if is_business:
        greeting = f"Hello there! This is Casey, your friendly AI assistant for {gov.name}. I'm here and excited to help with your water, billing, or facilities questions. What can I help you with today?"
        print(f"✅ BUSINESS HOURS - Casey greeting:")
        print(f"   {greeting}")
    else:
        greeting = await gov.get_after_hours_message()
        print(f"❌ AFTER HOURS - Generic greeting:")
        print(f"   {greeting[:100]}...")

if __name__ == "__main__":
    asyncio.run(test_greeting()) 