from typing import Dict, List, Optional
import json

class BrushyCreekKnowledgeBase:
    """Comprehensive knowledge base with FAQ and detailed information for Brushy Creek MUD"""
    
    def __init__(self):
        # Detailed FAQ sections from the website
        self.water_quality_faq = {
            "general": {
                "pure_water": "Pure water doesn't exist in nature. All water contains some impurities. Drinking water standards ensure safety by limiting impurities to safe levels set by EPA and TCEQ.",
                "water_safety": "District water is safe to drink for healthy people. Water meets EPA and TCEQ standards 24/7. People with compromised immune systems should consult their physician.",
                "water_testing": "Customer can get water tested by TCEQ-accredited labs for a fee. List available at tceq.texas.gov. District provides annual Water Quality Reports.",
                "chloramines": "Required disinfectant that provides continuous protection against contamination throughout the distribution system."
            },
            "discolored_water": {
                "white_cloudy": "Usually caused by tiny air bubbles. More common in winter due to temperature differences. Harmless and will clear if glass sits for a few moments.",
                "blue_water": "May be caused by toilet bowl disinfectant if water was recently shut off. Don't drink - flush all taps until clear.",
                "green_water": "Can be from fluorescent lights, copper traces, or seasonal algae blooms. District adjusts treatment when algae detected.",
                "brown_yellow_first_draw": "May result from main breaks, fire hydrant use, or flushing. Iron from old galvanized pipes. Run water briefly to clear.",
                "brown_yellow_constant": "Sediments stirred up by hydrant use or increased flow. Wait 30-40 minutes, then run cold water to clear.",
                "hot_tap_only": "Likely water heater issue. Turn off heater, let cool, drain and flush. Consult manual or plumber.",
                "crystals": "Usually calcium carbonate deposits. Can be removed with white vinegar. Harmless natural mineral."
            },
            "taste_smell": {
                "funny_taste": "May be due to different mineral content or seasonal changes. Algae blooms in summer can change taste but are harmless.",
                "improve_taste": "Refrigerate water in covered pitcher overnight. Chlorine will dissipate naturally.",
                "rotten_eggs": "Usually drain gases, not water. Test by taking glass away from sink. If still smells, contact customer service. May be water heater bacteria in hot water only."
            },
            "hardness": {
                "hardness_level": "Check District Water Hardness page for current levels in grains and milligrams.",
                "hard_vs_soft": "Hard water has high calcium/magnesium. Causes scale deposits. Soft water is treated with sodium.",
                "dishwasher_spots": "Mineral deposits from water evaporation. Use commercial products or vinegar. New low-phosphate detergents may increase spotting.",
                "white_deposits": "Mineral deposits around showerheads. Remove with vinegar or commercial cleaners.",
                "water_softener": "Personal preference. Improves soap performance but adds sodium. May be corrosive to pipes. Consult physician if on sodium-restricted diet."
            },
            "lead_fluoride": {
                "lead_water": "No lead in water leaving treatment plant. May come from home plumbing. Flush tap if unused 6+ hours. Use cold water for cooking.",
                "fluoride_max": "EPA maximum is 4.0 mg/L. Secondary standard for aesthetics is 2.0 mg/L.",
                "fluoride_levels": "Natural fluoride averages 0.35 mg/L. District doesn't add fluoride.",
                "home_treatment_fluoride": "Reverse osmosis, distillation remove 85-95% of fluoride. Ion exchange softeners don't remove fluoride."
            },
            "treatment_devices": {
                "improve_safety": "District water meets all standards. Home devices may remove chlorine/taste but rarely improve safety significantly. Require regular maintenance.",
                "aerators": "Mix air with water to prevent splashing and conserve water by reducing flow about 50%."
            }
        }
        
        self.billing_faq = {
            "water_rates": {
                "base_fee": "$20.00 monthly for 5/8 inch standard meter",
                "off_peak": "$3.50 per 1,000 gallons (October-May)",
                "peak": "$4.70 per 1,000 gallons (June-September)",
                "fire_connections": "Exempt from base fee if used only for fire suppression"
            },
            "same_bill_amount": {
                "explanation": "Bills calculated per 1,000 gallons. Consistent usage = same bill. Usage under 1,000 gallons may show zero usage but carries over to next month.",
                "example": "Using 1,500 gallons shows 1,000 on bill, 500 carries to next month"
            },
            "sewer_rates": {
                "new_residents": "Billed on 7,000 gallon average until winter average established",
                "established": "Based on 4-month average (Nov-Feb) from previous year",
                "base_fee_in_district": "$9.00",
                "rate_in_district": "$3.20 per 1,000 gallons",
                "base_fee_out_district": "$12.00",
                "rate_out_district": "$10.80 per 1,000 gallons",
                "adjustments": "Sewer Adjustment Request form available for leaks/pool fills during averaging months"
            },
            "solid_waste": {
                "provider": "Texas Disposal Systems",
                "standard_service": "$24.03 monthly (96-gallon garbage + recycling cart)",
                "additional_cart": "$7.08 each",
                "replacement_cost": "$65 + $25 delivery for lost/damaged carts",
                "stop_restart_fee": "$15.00 per occurrence"
            },
            "stormwater_fee": "$2.00 monthly for standard residential (Equivalent Residential Unit)",
            "payment_options": "Online, phone (credit card), in-person, drop box at Community Center. Due dates on weekends/holidays moved to next business day."
        }
        
        self.facilities_faq = {
            "swim_lessons": {
                "what_to_bring": "Towel, sunscreen, hair tie, goggles. Swim diapers for Parent & Child classes. No life jackets needed.",
                "arrival": "Arrive 10-15 minutes early for check-in",
                "weather_policy": "Pools close 30 minutes after last lightning/thunder",
                "learning_timeline": "Every child unique. Requires time and practice. Continue lessons throughout childhood for best results.",
                "parent_participation": "Only in Parent & Child classes. Parents can distract in other classes.",
                "supervision": "Must stay in pool area if child is 12 or under",
                "reluctant_children": "Positive talk before arrival helps. Contact swimlessons@bcmud.org if child won't participate.",
                "missed_classes": "No makeup classes. Refunds for weather/district cancellations. Request transfers up to week before class.",
                "instructor_certification": "All instructors CPR/AED/First Aid certified by American Red Cross",
                "swimsuit_requirement": "Yes, swimsuits required. No jean shorts. Rashguards/leggings allowed.",
                "lesson_length": "Most classes: 8 sessions of 30 minutes each"
            },
            "community_center": {
                "hours": {
                    "monday_friday": "5:30 AM - 9:00 PM",
                    "saturday": "7:00 AM - 9:00 PM", 
                    "sunday": "10:00 AM - 5:00 PM"
                },
                "size": "Over 60,000 square feet",
                "history": "Opened 2004 with 35,000 sq ft, expanded 2017",
                "features": "Recreation and meeting space, gym"
            }
        }
        
        self.trash_recycling_faq = {
            "service_schedule": {
                "garbage": "Weekly pickup",
                "recycling": "Every other week",
                "find_schedule": "Check district website or TDS Waste Wizard app"
            },
            "cart_issues": {
                "wheels_broken": "Contact BCMUD Customer Service for free repair/replacement",
                "damaged_lost": "Normal wear: free replacement. Abuse/loss: $65 + $25 delivery",
                "cart_size": "96-gallon containers (both garbage and recycling)",
                "recycling_cart": "Tan lid with recycling sticker",
                "garbage_cart": "Black lid"
            },
            "contact_policy": "Contact BCMUD Customer Service, not TDS directly",
            "additional_bags": "Up to 6 bags/bundles allowed. Max 4 feet length, 3 inches diameter, 35 lbs",
            "waste_wizard_app": "Free TDS app for schedule checking",
            "bulk_pickup": "2 free Saturday pickups per year. Schedule with Bulk Item Pick Up Request Form",
            "recyclables_accepted": [
                "Rigid plastic containers #1-7 (remove caps)",
                "Aluminum cans", "Steel/tin cans", 
                "Food boxes", "Paper towel/toilet paper rolls",
                "Newsprint", "Office paper", "Magazines",
                "Corrugated cardboard (bundle large amounts)"
            ],
            "recyclables_not_accepted": [
                "Glass", "Styrofoam", "Foil/aluminum tins",
                "Paper towels", "Toilet paper", "Facial tissue",
                "Plastic bags", "Wet paper", "Paper plates",
                "Plastic utensils", "Shiny-lined food boxes"
            ]
        }
        
        self.district_history = {
            "establishment": "Originally created as Williamson County MUD No. 2 on Oct 27, 1977. Confirmation election Jan 21, 1978.",
            "name_change": "Changed to Brushy Creek MUD on Aug 31, 1990",
            "area": "Originally 725 acres, expanded to 2,210 in 1983, now about 2,300 acres in two non-contiguous areas",
            "location": "Between Sam Bass Road and FM 1431 (North), and south of Brushy Creek including tract south of FM 620",
            "hoas": [
                "Brushy Creek North", "Sendero Springs", "Brushy Creek South",
                "Liberty Village/Neenah Oaks", "Villages of Brushy Creek", "Hunter Brook",
                "Cat Hollow", "Cat Hollow Condominiums", "Meadows of Brushy Creek",
                "Woods of Brushy Creek (multiple sections)", "Highlands of Brushy Creek",
                "Highland Horizon", "Enclave at Highland Horizon"
            ],
            "etj_history": "Originally in Austin and Round Rock ETJ. In 1997, all moved to Round Rock ETJ.",
            "water_service_evolution": "Started with groundwater wells and Round Rock purchased water. Now treats Lake Georgetown raw water and groundwater with advanced membrane filtration.",
            "wastewater_treatment": "Treated by Brushy Creek Regional Wastewater Treatment Plant (owned by Round Rock, Austin, Cedar Park)",
            "parks_development": "Funded by developer fees. Multiple parks, trails, greenbelts, 18-hole disc golf, 60,000+ sq ft Community Center, four swimming pools."
        }
        
        # Service areas and common call scenarios
        self.common_scenarios = {
            "water_emergency": {
                "keywords": ["leak", "no water", "burst pipe", "emergency", "flooding"],
                "response": "This sounds like a water emergency. Please call our emergency water line immediately at (512) 255-7871 ext. 508. This line is available Monday-Friday 6pm-8am, Saturday-Sunday anytime, and holidays.",
                "priority": "emergency"
            },
            "billing_questions": {
                "keywords": ["bill", "payment", "charge", "due date", "amount"],
                "response": "For billing questions, you can contact customer service at (512) 255-7871 during business hours: Monday-Friday 8am-6pm, Saturday 9am-3pm. You can also pay online or view your bill at our website.",
                "priority": "high"
            },
            "water_quality": {
                "keywords": ["taste", "smell", "color", "cloudy", "brown", "discolored"],
                "response": "Water quality issues can have various causes. Most are harmless but if you have concerns, contact customer service at (512) 255-7871. For detailed water quality information, check our comprehensive FAQ section.",
                "priority": "medium"
            },
            "service_interruption": {
                "keywords": ["outage", "no service", "pressure", "restoration"],
                "response": "For service interruptions, check our website for updates or call customer service. For water emergencies, call (512) 255-7871 ext. 508.",
                "priority": "high"
            },
            "facilities_hours": {
                "keywords": ["hours", "open", "closed", "pool", "community center", "park"],
                "response": "Community Center: Mon-Fri 5:30am-9pm, Sat 7am-9pm, Sun 10am-5pm. Parks: Spring/Summer 5am-11pm, Fall/Winter 6am-11pm. Pool hours vary by season.",
                "priority": "low"
            }
        }
    
    def get_faq_response(self, category: str, question: str) -> Optional[str]:
        """Get specific FAQ response"""
        category_data = getattr(self, f"{category}_faq", None)
        if not category_data:
            return None
        
        # Simple keyword matching for questions
        question_lower = question.lower()
        for section, items in category_data.items():
            if isinstance(items, dict):
                for key, value in items.items():
                    if any(word in question_lower for word in key.split('_')):
                        return value
        return None
    
    def search_knowledge_base(self, query: str) -> List[Dict]:
        """Search across all knowledge base content"""
        results = []
        query_lower = query.lower()
        
        # Search scenarios first
        for scenario, data in self.common_scenarios.items():
            if any(keyword in query_lower for keyword in data["keywords"]):
                results.append({
                    "type": "scenario",
                    "category": scenario,
                    "response": data["response"],
                    "priority": data["priority"]
                })
        
        # Search FAQ sections
        for section in ["water_quality_faq", "billing_faq", "facilities_faq", "trash_recycling_faq"]:
            section_data = getattr(self, section)
            for category, items in section_data.items():
                if isinstance(items, dict):
                    for key, value in items.items():
                        if any(word in query_lower for word in [key] + key.split('_')):
                            results.append({
                                "type": "faq",
                                "section": section.replace('_faq', ''),
                                "category": category,
                                "topic": key,
                                "answer": value
                            })
        
        return results
    
    def get_comprehensive_context(self) -> str:
        """Get comprehensive context for AI including all FAQ content"""
        context = """
COMPREHENSIVE BRUSHY CREEK MUD KNOWLEDGE BASE:

WATER QUALITY ISSUES:
- Cloudy water: Usually air bubbles, harmless, clears when sitting
- Discolored water: May be from main breaks, hydrant use, or home plumbing
- Taste/smell issues: Often seasonal or due to mineral content
- Hard water: Contains calcium/magnesium, causes spots on dishes/fixtures
- Water hardness level: Check district website for current levels
- Lead: Not in district water, may come from home plumbing with brass fixtures
- Fluoride: Natural level 0.35 mg/L, district doesn't add fluoride

BILLING INFORMATION:
- Water: $20 base + $3.50-4.70/1000 gallons (seasonal rates)
- Sewer: $9 base + $3.20/1000 gallons (based on winter average)
- Solid waste: $24.03/month (includes 96-gal garbage + recycling)
- Bills calculated per 1000 gallons, usage under 1000 carries over
- Payment: Online, phone, in-person, or drop box

FACILITIES & SERVICES:
- Community Center: 60,000+ sq ft, gym, meeting spaces
- Four swimming pools with lessons available
- Multiple parks, trails, 18-hole disc golf course
- Swim lessons: 8 sessions of 30 minutes, CPR-certified instructors

TRASH & RECYCLING:
- Garbage: Weekly pickup, up to 6 extra bags allowed
- Recycling: Every other week, tan lid cart
- Accepts: Plastic #1-7, cans, cardboard, paper
- Does NOT accept: Glass, styrofoam, plastic bags, wet paper
- Bulk pickup: 2 free Saturday pickups per year

EMERGENCY CONTACTS:
- Water emergencies: (512) 255-7871 ext. 508 (evenings/weekends/holidays)
- Security: (512) 255-7871 ext. 232
- Customer service: (512) 255-7871 (Mon-Fri 8am-6pm, Sat 9am-3pm)

CURRENT STATUS:
- Stage 1 Water Restrictions in effect
- Community Garden access: 7am-6pm
- Stairway connecting Creekside Park & Pool to Powder Horn Drive temporarily closed
"""
        return context 