from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import sys

from voice.twilio_handler import TwilioHandler
from voice.call_manager import CallManager
from government.brushy_creek import BrushyCreekMUD
from config.settings import Settings

# Load environment variables
load_dotenv()

print("🚀 Starting Brushy Creek Voice Service...")
print(f"🐍 Python version: {sys.version}")
print(f"📁 Working directory: {os.getcwd()}")

# Initialize settings
try:
    settings = Settings()
    print("✅ Settings loaded successfully")
    print(f"🌐 PORT: {settings.app_port}")
    print(f"🔗 WEBHOOK_BASE_URL: {settings.webhook_base_url}")
    print(f"🔑 TWILIO_ACCOUNT_SID: {settings.twilio_account_sid[:10] if settings.twilio_account_sid else 'MISSING'}...")
    print(f"🔑 TWILIO_AUTH_TOKEN: {'SET' if settings.twilio_auth_token else 'MISSING'}")
    print(f"🔑 OPENAI_API_KEY: {'SET' if settings.openai_api_key else 'MISSING'}")
except Exception as e:
    print(f"❌ Settings initialization failed: {e}")
    import traceback
    traceback.print_exc()
    raise

# Initialize services
print("🔧 Initializing services...")
try:
    call_manager = CallManager()
    government_service = BrushyCreekMUD()
    twilio_handler = TwilioHandler(call_manager, government_service)
    print("✅ Services created successfully")
except Exception as e:
    print(f"❌ Service creation failed: {e}")
    import traceback
    traceback.print_exc()
    raise

# Global initialization status
INITIALIZATION_STATUS = {
    "call_manager": False,
    "error": None
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🔄 Starting async initialization...")
    try:
        await call_manager.initialize()
        INITIALIZATION_STATUS["call_manager"] = True
        print("✅ Async initialization completed successfully")
    except Exception as e:
        print(f"❌ Async initialization failed: {e}")
        import traceback
        traceback.print_exc()
        INITIALIZATION_STATUS["error"] = str(e)
        # Don't raise - let the app start but mark as unhealthy
    
    yield
    
    # Shutdown
    print("🔄 Shutting down...")
    try:
        await call_manager.cleanup()
        print("✅ Cleanup completed")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

# Create FastAPI app
app = FastAPI(
    title="Local Government AI Voice Service",
    description="Low-latency AI-powered customer support for local government",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    print("📞 Root endpoint called")
    return {
        "status": "healthy",
        "service": "Local Government AI Voice Service",
        "version": "1.0.0",
        "government": "Brushy Creek MUD"
    }

@app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming voice calls from Twilio"""
    try:
        form_data = await request.form()
        response = await twilio_handler.handle_incoming_call(form_data)
        return Response(content=str(response), media_type="application/xml")
    except Exception as e:
        print(f"Error handling incoming call: {e}")
        # Return a basic TwiML response for error cases
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, we are experiencing technical difficulties. Please try again later.</Say></Response>',
            media_type="application/xml"
        )

@app.post("/voice/gather")
async def handle_voice_input(request: Request):
    """Handle voice input from Twilio Gather"""
    try:
        form_data = await request.form()
        response = await twilio_handler.handle_voice_input(form_data)
        return Response(content=str(response), media_type="application/xml")
    except Exception as e:
        print(f"Error handling voice input: {e}")
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, I didn\'t understand that. Please try again.</Say><Redirect>/voice/gather</Redirect></Response>',
            media_type="application/xml"
        )

@app.post("/voice/recording")
async def handle_recording(request: Request):
    """Handle voice recordings from Twilio"""
    try:
        form_data = await request.form()
        response = await twilio_handler.handle_recording(form_data)
        return Response(content=str(response), media_type="application/xml")
    except Exception as e:
        print(f"Error handling recording: {e}")
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, we couldn\'t process your request. Please try again.</Say></Response>',
            media_type="application/xml"
        )

@app.get("/voice/status/{call_sid}")
async def get_call_status(call_sid: str):
    """Get the status of a specific call"""
    try:
        status = await call_manager.get_call_status(call_sid)
        return {"call_sid": call_sid, "status": status}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Call not found: {e}")

@app.get("/government/info")
async def get_government_info():
    """Get information about the current government service"""
    return await government_service.get_basic_info()

@app.get("/health")
async def health_check():
    """Detailed health check with debugging - temporarily always returns 200 for diagnosis"""
    print("🏥 Health check called")
    
    try:
        # Check individual services
        twilio_status = twilio_handler.is_configured()
        government_status = True
        
        # Check if async initialization completed
        call_manager_status = INITIALIZATION_STATUS["call_manager"]
        openai_status = False
        if call_manager_status:
            try:
                openai_status = call_manager.ai_service.is_configured()
            except Exception as e:
                print(f"❌ Error checking OpenAI status: {e}")

        # Log detailed status
        print(f"[HEALTH CHECK] Twilio Configured: {twilio_status}")
        print(f"[HEALTH CHECK] Call Manager Initialized: {call_manager_status}")
        print(f"[HEALTH CHECK] OpenAI Configured: {openai_status}")
        print(f"[HEALTH CHECK] Government Service: {government_status}")
        print(f"[HEALTH CHECK] Initialization Error: {INITIALIZATION_STATUS.get('error', 'None')}")
        print(f"[HEALTH CHECK] TWILIO_ACCOUNT_SID: {settings.twilio_account_sid[:10] if settings.twilio_account_sid else 'MISSING'}...")
        print(f"[HEALTH CHECK] TWILIO_AUTH_TOKEN set: {bool(settings.twilio_auth_token)}")
        print(f"[HEALTH CHECK] OPENAI_API_KEY set: {bool(settings.openai_api_key)}")
        print(f"[HEALTH CHECK] PORT: {settings.app_port}")
        print(f"[HEALTH CHECK] WEBHOOK_BASE_URL: {settings.webhook_base_url}")

        # Determine overall health
        overall_healthy = twilio_status and openai_status and government_status and call_manager_status
        status_text = "healthy" if overall_healthy else "unhealthy"
        
        response_data = {
            "status": status_text,
            "services": {
                "twilio": twilio_status,
                "openai": openai_status,
                "call_manager": call_manager_status,
                "government": government_status
            },
            "env": {
                "twilio_account_sid": settings.twilio_account_sid[:10] if settings.twilio_account_sid else "MISSING",
                "twilio_auth_token_set": bool(settings.twilio_auth_token),
                "openai_api_key_set": bool(settings.openai_api_key),
                "port": settings.app_port,
                "webhook_base_url": settings.webhook_base_url
            },
            "initialization_error": INITIALIZATION_STATUS.get("error")
        }
        
        # TEMPORARILY: Always return 200 OK for Railway deployment diagnosis
        if overall_healthy:
            print("✅ Health check: HEALTHY")
        else:
            print("❌ Health check: UNHEALTHY (but returning 200 for diagnosis)")
        
        return response_data
            
    except Exception as e:
        print(f"❌ Health check failed with exception: {e}")
        import traceback
        traceback.print_exc()
        
        error_response = {
            "status": "error",
            "error": str(e),
            "services": {
                "twilio": False,
                "openai": False,
                "call_manager": False,
                "government": False
            }
        }
        
        # TEMPORARILY: Return 200 even for errors
        return error_response

@app.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve generated audio files"""
    try:
        file_path = f"/tmp/voice_audio/{filename}"
        if os.path.exists(file_path):
            return FileResponse(
                file_path, 
                media_type="audio/mpeg",
                headers={"Cache-Control": "no-cache"}
            )
        else:
            raise HTTPException(status_code=404, detail="Audio file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving audio: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    ) 