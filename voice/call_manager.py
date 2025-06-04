import asyncio
from typing import Dict, Optional, List
import json
from datetime import datetime, timedelta
import uuid

from voice.ai_service import AIService
from config.settings import Settings

class CallManager:
    """Manages active calls and coordinates between voice services and AI"""
    
    def __init__(self):
        self.settings = Settings()
        self.ai_service = AIService()
        self.active_calls: Dict[str, Dict] = {}
        self.call_history: List[Dict] = []
        self.redis_client = None  # Will be initialized if Redis is available
        
    async def initialize(self):
        """Initialize the call manager"""
        await self.ai_service.initialize()
        
        # Try to initialize Redis for session storage
        try:
            import redis
            if hasattr(redis, 'asyncio'):
                # New redis-py version
                self.redis_client = redis.asyncio.from_url(self.settings.redis_url)
            else:
                # Fallback for older versions
                import aioredis
                self.redis_client = aioredis.from_url(self.settings.redis_url)
            
            await self.redis_client.ping()
            print("Redis connected successfully")
        except ImportError as e:
            print(f"Redis module not available: {e}")
            self.redis_client = None
        except Exception as e:
            print(f"Redis not available, using in-memory storage: {e}")
            self.redis_client = None
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def start_call(self, call_sid: str, caller_number: str, government_context: str) -> str:
        """Start a new call session"""
        call_data = {
            "call_sid": call_sid,
            "caller_number": caller_number,
            "start_time": datetime.utcnow().isoformat(),
            "conversation_history": [],
            "status": "active",
            "government_context": government_context,
            "session_id": str(uuid.uuid4())
        }
        
        # Store in memory
        self.active_calls[call_sid] = call_data
        
        # Store in Redis if available
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"call:{call_sid}",
                    self.settings.call_timeout,
                    json.dumps(call_data, default=str)
                )
            except Exception as e:
                print(f"Error storing call in Redis: {e}")
        
        return call_data["session_id"]
    
    async def end_call(self, call_sid: str):
        """End a call session"""
        if call_sid in self.active_calls:
            call_data = self.active_calls[call_sid]
            call_data["status"] = "completed"
            call_data["end_time"] = datetime.utcnow().isoformat()
            
            # Move to history
            self.call_history.append(call_data.copy())
            
            # Remove from active calls
            del self.active_calls[call_sid]
            
            # Remove from Redis
            if self.redis_client:
                try:
                    await self.redis_client.delete(f"call:{call_sid}")
                except Exception as e:
                    print(f"Error removing call from Redis: {e}")
    
    async def get_call_data(self, call_sid: str) -> Optional[Dict]:
        """Get call data by SID"""
        # Check memory first
        if call_sid in self.active_calls:
            return self.active_calls[call_sid]
        
        # Check Redis if available
        if self.redis_client:
            try:
                data = await self.redis_client.get(f"call:{call_sid}")
                if data:
                    return json.loads(data)
            except Exception as e:
                print(f"Error retrieving call from Redis: {e}")
        
        return None
    
    async def add_to_conversation(self, call_sid: str, role: str, content: str):
        """Add a message to the conversation history"""
        call_data = await self.get_call_data(call_sid)
        if call_data:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            call_data["conversation_history"].append(message)
            
            # Update in memory
            if call_sid in self.active_calls:
                self.active_calls[call_sid] = call_data
            
            # Update in Redis
            if self.redis_client:
                try:
                    await self.redis_client.setex(
                        f"call:{call_sid}",
                        self.settings.call_timeout,
                        json.dumps(call_data, default=str)
                    )
                except Exception as e:
                    print(f"Error updating call in Redis: {e}")
    
    async def process_user_input(self, call_sid: str, user_input: str) -> str:
        """Process user input and generate AI response"""
        call_data = await self.get_call_data(call_sid)
        if not call_data:
            return "I'm sorry, there was an error with your call. Please try again."
        
        # Add user input to conversation
        await self.add_to_conversation(call_sid, "user", user_input)
        
        # Generate AI response
        try:
            response = await self.ai_service.generate_response(
                user_input=user_input,
                conversation_history=call_data["conversation_history"],
                government_context=call_data["government_context"]
            )
            
            # Add AI response to conversation
            await self.add_to_conversation(call_sid, "assistant", response)
            
            return response
            
        except Exception as e:
            error_msg = "I apologize, but I'm having trouble processing your request right now. Please try again or call our main number for assistance."
            print(f"Error generating AI response: {e}")
            await self.add_to_conversation(call_sid, "assistant", error_msg)
            return error_msg
    
    async def get_call_status(self, call_sid: str) -> Dict:
        """Get the current status of a call"""
        call_data = await self.get_call_data(call_sid)
        if call_data:
            return {
                "status": call_data["status"],
                "start_time": call_data["start_time"],
                "conversation_length": len(call_data["conversation_history"]),
                "last_activity": call_data["conversation_history"][-1]["timestamp"] if call_data["conversation_history"] else call_data["start_time"]
            }
        
        # Check history for completed calls
        for call in self.call_history:
            if call["call_sid"] == call_sid:
                return {
                    "status": call["status"],
                    "start_time": call["start_time"],
                    "end_time": call.get("end_time"),
                    "conversation_length": len(call["conversation_history"])
                }
        
        return {"status": "not_found"}
    
    async def cleanup_expired_calls(self):
        """Remove expired calls from memory"""
        current_time = datetime.utcnow()
        expired_calls = []
        
        for call_sid, call_data in self.active_calls.items():
            start_time = datetime.fromisoformat(call_data["start_time"])
            if current_time - start_time > timedelta(seconds=self.settings.call_timeout):
                expired_calls.append(call_sid)
        
        for call_sid in expired_calls:
            await self.end_call(call_sid)
            print(f"Expired call removed: {call_sid}")
    
    async def get_active_calls_count(self) -> int:
        """Get the number of active calls"""
        return len(self.active_calls)
    
    async def get_conversation_summary(self, call_sid: str) -> Optional[str]:
        """Get a summary of the conversation for the call"""
        call_data = await self.get_call_data(call_sid)
        if not call_data or not call_data["conversation_history"]:
            return None
        
        # Generate a brief summary of the conversation
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in call_data["conversation_history"]
        ])
        
        try:
            summary = await self.ai_service.generate_summary(conversation_text)
            return summary
        except Exception as e:
            print(f"Error generating conversation summary: {e}")
            return "Summary unavailable" 