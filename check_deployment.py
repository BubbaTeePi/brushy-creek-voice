#!/usr/bin/env python3
"""
Deployment verification script for Brushy Creek Voice Service
"""

import requests
import json
import os
from urllib.parse import urljoin

def check_deployment(base_url: str):
    """Check if the deployment is working correctly"""
    
    print(f"🔍 Checking deployment at: {base_url}")
    print("=" * 60)
    
    checks = []
    
    # 1. Health Check
    try:
        health_url = urljoin(base_url, "/health")
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            checks.append(("✅ Health Check", "PASS", f"Status: {health_data.get('status')}"))
        else:
            checks.append(("❌ Health Check", "FAIL", f"Status: {response.status_code}"))
    except Exception as e:
        checks.append(("❌ Health Check", "FAIL", f"Error: {e}"))
    
    # 2. Government Info Endpoint
    try:
        gov_url = urljoin(base_url, "/government/info")
        response = requests.get(gov_url, timeout=10)
        if response.status_code == 200:
            gov_data = response.json()
            name = gov_data.get('name', 'Unknown')
            checks.append(("✅ Government Info", "PASS", f"Name: {name}"))
        else:
            checks.append(("❌ Government Info", "FAIL", f"Status: {response.status_code}"))
    except Exception as e:
        checks.append(("❌ Government Info", "FAIL", f"Error: {e}"))
    
    # 3. Voice Incoming Endpoint (should handle POST)
    try:
        voice_url = urljoin(base_url, "/voice/incoming")
        # Test with minimal Twilio-like data
        test_data = {
            "CallSid": "TEST123",
            "From": "+15551234567",
            "To": "+18776652873"
        }
        response = requests.post(voice_url, data=test_data, timeout=15)
        if response.status_code in [200, 201]:
            checks.append(("✅ Voice Webhook", "PASS", "Accepts POST requests"))
        else:
            checks.append(("❌ Voice Webhook", "FAIL", f"Status: {response.status_code}"))
    except Exception as e:
        checks.append(("❌ Voice Webhook", "FAIL", f"Error: {e}"))
    
    # 4. Environment Variables Check
    required_env_vars = [
        "OPENAI_API_KEY",
        "ELEVENLABS_API_KEY", 
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "WEBHOOK_BASE_URL"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if not missing_vars:
        checks.append(("✅ Environment Variables", "PASS", "All required vars present"))
    else:
        checks.append(("❌ Environment Variables", "FAIL", f"Missing: {', '.join(missing_vars)}"))
    
    # Print results
    print("\n📊 DEPLOYMENT CHECK RESULTS:")
    print("-" * 60)
    
    passed = 0
    total = len(checks)
    
    for check_name, status, details in checks:
        print(f"{check_name:<25} {status:<6} {details}")
        if status == "PASS":
            passed += 1
    
    print("-" * 60)
    print(f"📈 SCORE: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 DEPLOYMENT SUCCESS!")
        print(f"🌟 Your voice service is ready at: {base_url}")
        print(f"📞 Test by calling: +1 (877) 665-2873")
        print(f"🔗 Health check: {urljoin(base_url, '/health')}")
        return True
    else:
        print(f"\n⚠️  DEPLOYMENT ISSUES FOUND")
        print("Please fix the failed checks before going live.")
        return False

def main():
    """Main function"""
    # Try to get base URL from environment or ask user
    base_url = os.getenv("WEBHOOK_BASE_URL")
    
    if not base_url:
        print("🌐 Enter your deployment URL:")
        print("Examples:")
        print("  - Railway: https://yourapp.railway.app")
        print("  - Fly.io: https://yourapp.fly.dev")
        print("  - Cloud Run: https://yourapp-xxx.run.app")
        print()
        base_url = input("URL: ").strip()
    
    if not base_url:
        print("❌ No URL provided")
        return
    
    # Ensure URL has protocol
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'https://' + base_url
    
    success = check_deployment(base_url)
    
    if success:
        print("\n🚀 NEXT STEPS:")
        print("1. Update Twilio webhook URL in console")
        print(f"   - Set to: {urljoin(base_url, '/voice/incoming')}")
        print("2. Test with a phone call")
        print("3. Monitor logs for any issues")
    
if __name__ == "__main__":
    main() 