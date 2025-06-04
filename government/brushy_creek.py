from typing import Dict, List, Optional
from datetime import datetime, time
import json
from government.brushy_creek_knowledge import BrushyCreekKnowledgeBase
import asyncio

class BrushyCreekMUD:
    """Enhanced Brushy Creek Municipal Utility District service with comprehensive FAQ support"""
    
    def __init__(self):
        self.name = "Brushy Creek Municipal Utility District"
        self.knowledge_base = BrushyCreekKnowledgeBase()
        
        # Current service information - UPDATED FROM WEBSITE
        self.phone = "(512) 255-7871"
        self.address = "16318 Great Oaks Drive, Round Rock, TX 78681"
        self.website = "bcmud.org"
        
        # Current alerts and notices
        self.current_status = {
            "water_restrictions": "Stage 1 Water Restrictions currently in effect",
            "notices": [
                "Community Garden access: 7am-6pm",
                "Stairway connecting Creekside Park & Pool to Powder Horn Drive temporarily closed",
                "Some playground closures for maintenance"
            ]
        }
        
        # Service hours
        self.customer_service_hours = {
            "monday_friday": "8am - 6pm",
            "saturday": "9am - 3pm",
            "sunday": "Closed"
        }
        
        # Enhanced emergency contacts
        self.emergency_water = {
            "phone": "(512) 255-7871 ext. 508",
            "hours": "Monday-Friday 6pm-8am, Weekends anytime, Holidays"
        }
        
        self.security = {
            "phone": "(512) 255-7871 ext. 232"
        }
        
        # Detailed service information
        self.services = {
            "water": {
                "source": "Lake Georgetown (primary) and groundwater wells",
                "treatment": "State-of-the-art microfiltration plant with semi-permeable membrane",
                "quality": "Superior Water designation from TCEQ"
            },
            "rates": {
                "water_base": "$20.00/month (5/8 inch meter)",
                "water_off_peak": "$3.50 per 1,000 gallons (Oct-May)",  
                "water_peak": "$4.70 per 1,000 gallons (June-Sept)",
                "sewer_base": "$9.00/month in district",
                "sewer_rate": "$3.20 per 1,000 gallons",
                "solid_waste": "$24.03/month (includes 96-gal garbage + recycling)",
                "stormwater": "$2.00/month"
            },
            "facilities": {
                "community_center": "60,000+ sq ft with gym, meeting spaces",
                "pools": "Four swimming pools with lessons",
                "parks": "Multiple parks, trails, 18-hole disc golf course"
            }
        }

    async def get_context_for_ai(self) -> str:
        """Get comprehensive context including FAQ knowledge for AI responses"""
        return self.knowledge_base.get_comprehensive_context()

    async def answer_question(self, question: str) -> str:
        """Answer questions using the comprehensive knowledge base"""
        question_lower = question.lower()
        
        # Search knowledge base for relevant information
        results = self.knowledge_base.search_knowledge_base(question)
        
        if results:
            # Priority: Emergency scenarios first
            emergency_results = [r for r in results if r.get("priority") == "emergency"]
            if emergency_results:
                return emergency_results[0]["response"]
            
            # Then FAQ answers with specific information
            faq_results = [r for r in results if r["type"] == "faq"]
            if faq_results:
                best_result = faq_results[0]
                return best_result["answer"]
            
            # Then general scenario responses
            scenario_results = [r for r in results if r["type"] == "scenario"]
            if scenario_results:
                return scenario_results[0]["response"]
        
        # Specific common questions with direct answers
        if "water" in question_lower and any(word in question_lower for word in ["rate", "cost", "bill", "price"]):
            return f"Water rates: $20 base fee + $3.50-4.70 per 1,000 gallons (seasonal). Need more details? Call {self.phone}."
        
        if "hours" in question_lower and any(word in question_lower for word in ["community center", "center"]):
            return "Community Center: Mon-Fri 5:30am-9pm, Sat 7am-9pm, Sun 10am-5pm."
        
        if "hours" in question_lower and "customer service" in question_lower:
            return f"Customer Service: Mon-Fri 8am-6pm, Sat 9am-3pm. Call {self.phone}."
        
        if "garbage" in question_lower or "trash" in question_lower:
            return "Garbage: Weekly pickup. Recycling: Every other week. $24.03/month includes both 96-gal carts."
        
        if "recycle" in question_lower or "recycling" in question_lower:
            return "Recycling: Every other week, tan cart. Accepts plastic #1-7, cans, cardboard, paper. NO glass or styrofoam."
        
        if "sewer" in question_lower and any(word in question_lower for word in ["rate", "cost", "bill"]):
            return "Sewer: $9 base + $3.20/1000 gal based on winter average (Nov-Feb). New residents: 7,000 gal average."
        
        if "pool" in question_lower:
            return "Four pools with swim lessons available. Lessons: 8 sessions, CPR-certified instructors. Pool hours vary by season."
        
        if "emergency" in question_lower and "water" in question_lower:
            return f"Water emergency? Call {self.emergency_water['phone']} immediately! Available {self.emergency_water['hours']}."
        
        # Default with helpful suggestion
        return f"For detailed information, call {self.phone} (Mon-Fri 8am-6pm, Sat 9am-3pm) or visit {self.website}."

    async def get_detailed_answer(self, category: str, question: str) -> str:
        """Get detailed FAQ answer for specific categories"""
        if category == "billing":
            if "same amount" in question.lower() or "same bill" in question.lower():
                return "Bills calculated per 1,000 gallons. If you use 1,500 gallons, only 1,000 shows on bill, 500 carries to next month. Consistent usage = same bill amount."
            elif "sewer average" in question.lower():
                return "Sewer based on 4-month winter average (Nov-Feb). New residents: 7,000 gal average until established. You can request 6-month history for lower average."
            elif "payment" in question.lower():
                return "Pay online, by phone, in-person, or drop box at Community Center. Due dates on weekends/holidays move to next business day."
        
        elif category == "water_quality":
            if "cloudy" in question.lower():
                return "Cloudy water usually from air bubbles, more common in winter. Harmless - will clear if glass sits for a few moments."
            elif "brown" in question.lower() or "yellow" in question.lower():
                return "Brown/yellow water may be from main breaks or fire hydrant use. Run cold water briefly to clear. If constant, wait 30-40 minutes."
            elif "taste" in question.lower() or "smell" in question.lower():
                return "Taste/smell changes often seasonal or mineral-related. Refrigerate water overnight to dissipate chlorine. If rotten egg smell, test away from sink."
        
        elif category == "trash":
            if "schedule" in question.lower():
                return "Garbage: Weekly. Recycling: Every other week. Check TDS Waste Wizard app or district website for your schedule."
            elif "cart" in question.lower() and ("broken" in question.lower() or "damaged" in question.lower()):
                return "Broken carts: Free repair/replacement for normal wear. Contact BCMUD Customer Service, not TDS directly."
        
        # Fallback to knowledge base search
        return await self.answer_question(question)

    async def is_business_hours(self) -> bool:
        """Check if it's currently business hours"""
        now = datetime.now()
        current_time = now.time()
        
        # Monday-Friday 8am-6pm
        if now.weekday() < 5:  # 0-4 is Monday-Friday
            return time(8, 0) <= current_time <= time(18, 0)
        # Saturday 9am-3pm  
        elif now.weekday() == 5:  # Saturday
            return time(9, 0) <= current_time <= time(15, 0)
        # Sunday closed
        return False

    async def get_after_hours_message(self) -> str:
        """Get appropriate after-hours message with Casey's personality"""
        return f"""Hello there! This is Casey, your friendly AI assistant for {self.name}. 
        
Even though our customer service team isn't available right now, I'm here to help!

Our customer service hours are Monday through Friday 8am to 6pm, and Saturday 9am to 3pm.
        
For water emergencies, please call {self.emergency_water['phone']} immediately.
For security issues, please call {self.security['phone']}.
        
You can also visit our website at {self.website} for more information.
        
What can I help you with today?"""

    async def get_emergency_info(self) -> Dict:
        """Get emergency contact information"""
        return {
            "water_emergency": self.emergency_water,
            "security": self.security,
            "customer_service": {
                "phone": self.phone,
                "hours": "Monday-Friday 8am-6pm, Saturday 9am-3pm"
            }
        }

    async def get_current_status(self) -> Dict:
        """Get current service status and notices"""
        return {
            "status": "Operational",
            "alerts": self.current_status,
            "last_updated": datetime.now().isoformat()
        }

    async def get_basic_info(self) -> Dict:
        """Get basic information about Brushy Creek MUD"""
        return {
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
            "website": self.website,
            "current_status": {
                "water_restrictions": self.current_status["water_restrictions"]
            },
            "hours": self.customer_service_hours
        }

    async def search_knowledge(self, query: str) -> List[Dict]:
        """Search the comprehensive knowledge base"""
        return self.knowledge_base.search_knowledge_base(query) 