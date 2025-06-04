#!/usr/bin/env python3
"""
Setup Twilio Webhooks Script
This script configures your Twilio phone number to use your voice service
"""

import os
import time
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

def setup_webhooks():
    """Configure Twilio webhooks for the voice service"""
    
    # Load Twilio credentials
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if not account_sid or not auth_token:
        print("❌ Error: Twilio credentials not found in environment variables")
        print("Please run: python3 setup_env.py")
        return False
    
    try:
        print("🔄 Setting up Twilio webhooks...")
        client = Client(account_sid, auth_token)
        
        # Get your phone numbers
        phone_numbers = client.incoming_phone_numbers.list()
        
        if not phone_numbers:
            print("❌ No phone numbers found in your Twilio account")
            return False
        
        print(f"📱 Found {len(phone_numbers)} phone number(s):")
        for number in phone_numbers:
            print(f"   • {number.phone_number}")
        
        # Use the first phone number
        phone_number = phone_numbers[0]
        
        # Your service URL (you'll need to expose this publicly)
        # For now, we'll use a placeholder - you'll need ngrok or similar
        webhook_url = "https://your-ngrok-url.ngrok-free.app/voice/incoming"
        
        print(f"\n🎯 Setting up webhooks for {phone_number.phone_number}")
        print(f"   Voice Webhook: {webhook_url}")
        
        # Note: We're not actually updating yet because we need the public URL
        print("\n⚠️  IMPORTANT NEXT STEPS:")
        print("1. Your voice service is running locally on port 8000")
        print("2. You need to expose it publicly using ngrok:")
        print("   • Install ngrok: brew install ngrok (on Mac)")
        print("   • Run: ngrok http 8000")
        print("   • Copy the https://xxxx.ngrok-free.app URL")
        print("3. Then update this script with your ngrok URL and run it again")
        
        print(f"\n🚀 Once you have ngrok running, update the webhook_url in this script to:")
        print(f"   https://YOUR-NGROK-URL.ngrok-free.app/voice/incoming")
        
        # For demonstration, let's show what the update would look like
        print(f"\n📋 Webhook configuration ready:")
        print(f"   Phone Number: {phone_number.phone_number}")
        print(f"   SID: {phone_number.sid}")
        print(f"   Current Voice URL: {phone_number.voice_url or 'None'}")
        
        return True
        
    except TwilioException as e:
        print(f"❌ Twilio error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def update_webhook_url(ngrok_url):
    """Update the webhook URL with your ngrok URL"""
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    try:
        client = Client(account_sid, auth_token)
        phone_numbers = client.incoming_phone_numbers.list()
        
        if not phone_numbers:
            print("❌ No phone numbers found")
            return False
            
        phone_number = phone_numbers[0]
        webhook_url = f"{ngrok_url}/voice/incoming"
        
        print(f"🔄 Updating webhook for {phone_number.phone_number}")
        print(f"   New URL: {webhook_url}")
        
        # Update the phone number configuration
        phone_number.update(
            voice_url=webhook_url,
            voice_method='POST'
        )
        
        print("✅ Webhook updated successfully!")
        print(f"🎉 Your phone number {phone_number.phone_number} is now connected to your voice service!")
        print("\n📞 Test it by calling your Twilio number!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating webhook: {e}")
        return False

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🔧 Twilio Webhook Setup")
    print("=" * 50)
    
    if setup_webhooks():
        print("\n🎯 Ready for next step!")
        
        # Check if user provided ngrok URL as argument
        import sys
        if len(sys.argv) > 1:
            ngrok_url = sys.argv[1].rstrip('/')
            if ngrok_url.startswith('http'):
                print(f"\n🔄 Updating webhook with URL: {ngrok_url}")
                update_webhook_url(ngrok_url)
            else:
                print("❌ Please provide a valid HTTP/HTTPS URL")
        else:
            print("\n💡 To update webhook URL, run:")
            print("   python3 setup_webhooks.py https://YOUR-NGROK-URL.ngrok-free.app") 