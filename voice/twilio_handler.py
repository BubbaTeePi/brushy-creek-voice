from twilio.twiml.voice_response import VoiceResponse, Gather, Say, Record
from twilio import rest
from typing import Dict, Optional
import asyncio
import tempfile
import os
import time

from voice.call_manager import CallManager
from government.brushy_creek import BrushyCreekMUD
from config.settings import Settings

class TwilioHandler:
    """Handler for Twilio voice interactions with optimized gather settings"""
    
    def __init__(self, call_manager: CallManager, government_service: BrushyCreekMUD):
        self.settings = Settings()  # This loads from environment
        self.call_manager = call_manager
        self.government_service = government_service
        self.twilio_client = None
        
        # Print the webhook URL for debugging
        print(f"🌐 TwilioHandler webhook_base_url: {self.settings.webhook_base_url}")
        
        # Initialize Twilio client if credentials are available
        if self.settings.twilio_account_sid and self.settings.twilio_auth_token:
            self.twilio_client = rest.Client(
                self.settings.twilio_account_sid,
                self.settings.twilio_auth_token
            )
    
    def is_configured(self) -> bool:
        """Check if Twilio is properly configured"""
        return self.twilio_client is not None
    
    def create_welcome_response(self) -> str:
        """Create initial welcome message with optimized gather"""
        response = VoiceResponse()
        
        # Optimized gather with reduced sensitivity
        gather = Gather(
            input='speech',
            timeout=self.settings.gather_timeout,  # 4 seconds
            speechTimeout='auto',  # Let Twilio detect end of speech
            partialResultCallback=True,  # Enable partial results
            action='/voice/process',
            method='POST',
            language='en-US'
        )
        
        gather.say(
            "Hello! You've reached Brushy Creek Municipal Utility District. "
            "I'm here to help with water service, billing, facilities, or general information. "
            "How can I assist you today?"
        )
        
        response.append(gather)
        
        # Fallback if no input
        response.say("I didn't hear anything. Please call back or stay on the line for our main number.")
        response.redirect('/voice/transfer-to-human')
        
        return str(response)
    
    def create_processing_response(self, ai_response: str, audio_url: Optional[str] = None) -> str:
        """Create response with AI-generated content and optimized follow-up gather"""
        response = VoiceResponse()
        
        if audio_url:
            # Play AI-generated audio (ElevenLabs or OpenAI)
            response.play(audio_url)
        else:
            # Fallback to text-to-speech
            response.say(ai_response)
        
        # Optimized gather for follow-up questions
        gather = Gather(
            input='speech',
            timeout=self.settings.gather_timeout,  # 4 seconds
            speechTimeout='auto',
            partialResultCallback=True,
            action='/voice/process',
            method='POST',
            language='en-US',
            finishOnKey='#'  # Allow # to finish input early
        )
        
        gather.say("Is there anything else I can help you with today? I'm here and happy to assist!")
        response.append(gather)
        
        # End call gracefully if no further input
        response.say("Thanks so much for calling Brushy Creek! Feel free to call back anytime - we're always here to help!")
        response.hangup()
        
        return str(response)
    
    def create_error_response(self, error_message: str = None) -> str:
        """Create error response with option to try again or transfer"""
        response = VoiceResponse()
        
        if error_message:
            response.say(f"I'm sorry, {error_message}")
        else:
            response.say("I'm having trouble processing your request right now.")
        
        # Give option to try again or transfer
        gather = Gather(
            input='speech',
            timeout=3,  # Shorter timeout for error recovery
            speechTimeout='auto',
            action='/voice/retry',
            method='POST',
            language='en-US'
        )
        
        gather.say("Would you like to try again, or would you prefer to speak with someone?")
        response.append(gather)
        
        # Default to human transfer
        response.redirect('/voice/transfer-to-human')
        
        return str(response)
    
    def create_transfer_response(self) -> str:
        """Transfer to human agent"""
        response = VoiceResponse()
        
        response.say(
            "I'm transferring you to our customer service team. "
            "Please hold while I connect you, or you can call us directly at 5-1-2, 2-5-5, 4-6-5-2."
        )
        
        # In a real implementation, you would dial the customer service number
        # For now, we'll provide the number and hang up
        response.say(
            "Our customer service number is 5-1-2, 2-5-5, 4-6-5-2. "
            "They're available Monday through Friday, 8 AM to 5 PM. Thank you!"
        )
        response.hangup()
        
        return str(response)
    
    def create_goodbye_response(self) -> str:
        """Create goodbye message"""
        response = VoiceResponse()
        
        response.say(
            "Thank you for calling Brushy Creek Municipal Utility District. "
            "Have a great day!"
        )
        response.hangup()
        
        return str(response)
    
    async def save_audio_to_temp_url(self, audio_bytes: bytes, call_sid: str) -> str:
        """Save audio bytes to a temporary file and return URL"""
        try:
            # Create temp file
            temp_dir = "/tmp/voice_audio"
            os.makedirs(temp_dir, exist_ok=True)
            
            filename = f"response_{call_sid}_{int(time.time())}.mp3"
            file_path = os.path.join(temp_dir, filename)
            
            # Write audio to file
            with open(file_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Return URL that will be served by the FastAPI app
            return f"{self.settings.webhook_base_url}/audio/{filename}"
            
        except Exception as e:
            print(f"Error saving audio file: {e}")
            return None
    
    def parse_twilio_request(self, form_data: Dict) -> Dict:
        """Parse incoming Twilio request data"""
        return {
            'call_sid': form_data.get('CallSid', ''),
            'from_number': form_data.get('From', ''),
            'to_number': form_data.get('To', ''),
            'speech_result': form_data.get('SpeechResult', ''),
            'confidence': form_data.get('Confidence', '0'),
            'recording_url': form_data.get('RecordingUrl', ''),
            'call_status': form_data.get('CallStatus', ''),
            'direction': form_data.get('Direction', ''),
            'account_sid': form_data.get('AccountSid', ''),
        }
    
    def is_speech_confident(self, confidence: str, speech_result: str) -> bool:
        """Check if speech recognition confidence is acceptable"""
        try:
            confidence_score = float(confidence)
            # Lower threshold for better user experience
            # Also check if speech result seems reasonable
            return (confidence_score > 0.6 and 
                    len(speech_result.strip()) > 2 and 
                    speech_result.strip().lower() not in ['um', 'uh', 'hmm', 'hello'])
        except (ValueError, TypeError):
            return len(speech_result.strip()) > 2
    
    def create_clarification_response(self, original_speech: str) -> str:
        """Create response asking for clarification"""
        response = VoiceResponse()
        
        gather = Gather(
            input='speech',
            timeout=self.settings.gather_timeout,
            speechTimeout='auto',
            partialResultCallback=True,
            action='/voice/process',
            method='POST',
            language='en-US'
        )
        
        gather.say(
            f"I heard '{original_speech}' but I want to make sure I understand correctly. "
            "Could you please repeat that or rephrase your question?"
        )
        
        response.append(gather)
        
        # Fallback
        response.say("I'm having trouble understanding. Let me transfer you to customer service.")
        response.redirect('/voice/transfer-to-human')
        
        return str(response)
    
    async def handle_incoming_call(self, form_data: dict) -> VoiceResponse:
        """Handle incoming voice call from Twilio"""
        response = VoiceResponse()
        
        try:
            # Extract call information
            call_sid = form_data.get("CallSid", "")
            caller_number = form_data.get("From", "")
            
            # Get government context
            government_context = await self.government_service.get_context_for_ai()
            
            # Start call session
            session_id = await self.call_manager.start_call(
                call_sid=call_sid,
                caller_number=caller_number,
                government_context=government_context
            )
            
            # Check if it's business hours
            is_business_hours = await self.government_service.is_business_hours()
            
            if is_business_hours:
                greeting = f"Hello there! This is Casey, your friendly AI assistant for {self.government_service.name}. I'm here and excited to help with your water, billing, or facilities questions. What can I help you with today?"
            else:
                greeting = await self.government_service.get_after_hours_message()
            
            # **EMERGENCY FIX** - Use direct TTS instead of broken audio files
            print(f"🎤 Using Twilio TTS for greeting (ElevenLabs/audio files not available)")
            response.say(greeting)
            
            # Create initial gather for voice input - OPTIMIZED FOR INTERRUPTION
            gather = Gather(
                input='speech',
                action='/voice/gather',
                method='POST',
                speechTimeout=self.settings.gather_speech_timeout,  # Very short - 1 second
                timeout=self.settings.gather_timeout,  # Reduced to 2 seconds
                enhanced=True,
                speechModel='experimental_conversations',
                partialResultCallback=True,  # Enable real-time partial results
                language='en-US'
            )
            
            # Don't add text to gather since we already played the greeting
            response.append(gather)
            
            # Fallback if no input
            response.say("I didn't hear anything. Please call back if you need assistance. Goodbye!")
            
        except Exception as e:
            print(f"Error in handle_incoming_call: {e}")
            response.say("I'm sorry, we're experiencing technical difficulties. Please try calling back in a few minutes.")
        
        return response
    
    async def handle_voice_input(self, form_data: dict) -> VoiceResponse:
        """Handle voice input from user"""
        response = VoiceResponse()
        
        try:
            call_sid = form_data.get("CallSid", "")
            speech_result = form_data.get("SpeechResult", "")
            
            if not speech_result:
                # No speech detected, try to gather again with optimized interruption settings
                gather = Gather(
                    input='speech',
                    action='/voice/gather',
                    method='POST',
                    speechTimeout=self.settings.gather_speech_timeout,  # 1 second
                    timeout=self.settings.gather_timeout,  # 2 seconds
                    enhanced=True,
                    speechModel='experimental_conversations',
                    partialResultCallback=True,
                    language='en-US'
                )
                gather.say("I didn't catch that, but no worries! Could you repeat that?")
                response.append(gather)
                response.say("Thanks for calling Brushy Creek! Have a wonderful day!")
                return response
            
            # Process the user input through AI
            ai_response = await self.call_manager.process_user_input(call_sid, speech_result)
            
            # **EMERGENCY FIX** - Use direct TTS instead of broken audio files
            print(f"🎤 Using Twilio TTS for AI response (ElevenLabs/audio files not available)")
            response.say(ai_response)
            
            # Classify intent to determine if we should continue the conversation
            intent = await self.call_manager.ai_service.classify_intent(speech_result)
            
            # Determine if this should end the call or continue
            should_continue = await self._should_continue_conversation(intent, speech_result)
            
            if should_continue:
                # Continue conversation with optimized interruption settings
                gather = Gather(
                    input='speech',
                    action='/voice/gather',
                    method='POST',
                    speechTimeout=self.settings.gather_speech_timeout,  # 1 second
                    timeout=self.settings.gather_timeout,  # 2 seconds  
                    enhanced=True,
                    speechModel='experimental_conversations',
                    partialResultCallback=True,
                    language='en-US'
                )
                gather.say("Anything else?")  # Much shorter prompt
                response.append(gather)
                
                # Fallback for no response
                response.say("Thanks for calling! Have a great day!")
            else:
                # End the conversation - use direct TTS instead of broken audio files
                print(f"🎤 Using Twilio TTS for goodbye (ElevenLabs/audio files not available)")
                goodbye_text = "Thanks for calling! You have a fantastic day, and remember - we're always here when you need us!"
                response.say(goodbye_text)
            
            # End the call session if we're not continuing
            if not should_continue:
                await self.call_manager.end_call(call_sid)
                
        except Exception as e:
            print(f"Error in handle_voice_input: {e}")
            response.say("I apologize, but I'm having trouble processing your request. Please try calling back or contact our main number for assistance.")
        
        return response
    
    async def handle_recording(self, form_data: dict) -> VoiceResponse:
        """Handle voice recording from Twilio"""
        response = VoiceResponse()
        
        try:
            call_sid = form_data.get("CallSid", "")
            recording_url = form_data.get("RecordingUrl", "")
            
            if recording_url:
                # Transcribe the recording
                transcription = await self.call_manager.ai_service.transcribe_audio(recording_url)
                
                if transcription:
                    # Process the transcribed text
                    ai_response = await self.call_manager.process_user_input(call_sid, transcription)
                    response.say(ai_response)
                else:
                    response.say("I'm sorry, I couldn't understand the recording. Please try again.")
            else:
                response.say("No recording was received. Please try again.")
                
        except Exception as e:
            print(f"Error in handle_recording: {e}")
            response.say("I'm sorry, there was an error processing your recording.")
        
        return response
    
    async def _should_continue_conversation(self, intent: str, user_input: str) -> bool:
        """Determine if the conversation should continue based on intent and input"""
        # Keywords that typically indicate the caller wants to end
        ending_phrases = [
            "thank you", "thanks", "that's all", "goodbye", "bye",
            "no thanks", "nothing else", "that helps", "perfect"
        ]
        
        user_lower = user_input.lower()
        
        # If user explicitly indicates they're done
        if any(phrase in user_lower for phrase in ending_phrases):
            return False
        
        # For emergency situations, don't continue - route to appropriate service
        if intent == "water_emergency":
            return False
        
        # For complaints, might want to route to human
        if intent == "complaint":
            return False
        
        # Otherwise, continue the conversation
        return True
    
    async def make_outbound_call(self, to_number: str, message: str) -> Optional[str]:
        """Make an outbound call (for notifications/alerts)"""
        if not self.is_configured():
            print("Twilio not configured for outbound calls")
            return None
        
        try:
            # Create TwiML for the outbound call
            twiml = VoiceResponse()
            twiml.say(message)
            
            call = self.twilio_client.calls.create(
                twiml=str(twiml),
                to=to_number,
                from_=self.settings.twilio_phone_number
            )
            
            return call.sid
            
        except Exception as e:
            print(f"Error making outbound call: {e}")
            return None
    
    async def send_sms_notification(self, to_number: str, message: str) -> Optional[str]:
        """Send SMS notification"""
        if not self.is_configured():
            print("Twilio not configured for SMS")
            return None
        
        try:
            message = self.twilio_client.messages.create(
                body=message,
                from_=self.settings.twilio_phone_number,
                to=to_number
            )
            
            return message.sid
            
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return None
    
    def create_emergency_response(self, emergency_type: str) -> VoiceResponse:
        """Create TwiML response for emergency situations"""
        response = VoiceResponse()
        
        if emergency_type == "water_emergency":
            emergency_info = asyncio.run(self.government_service.get_emergency_info())
            message = f"""This sounds like a water emergency. Please call our emergency water line immediately at {emergency_info['water_emergency']['phone']}. 
            
This line is available {emergency_info['water_emergency']['hours']}. 

If this is not an emergency, you can call our main customer service line during business hours. Goodbye."""
            
            response.say(message)
        else:
            response.say("For urgent matters, please contact our main office or emergency services as appropriate. Goodbye.")
        
        return response 