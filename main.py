from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from voice.twilio_handler import TwilioHandler
from voice.call_manager import CallManager
from government.brushy_creek import BrushyCreekMUD
from config.settings import Settings

# Load environment variables
load_dotenv()

# Initialize settings
settings = Settings()

# Initialize services
call_manager = CallManager()
government_service = BrushyCreekMUD()
twilio_handler = TwilioHandler(call_manager, government_service)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await call_manager.initialize()
    yield
    # Shutdown
    await call_manager.cleanup()

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
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "twilio": twilio_handler.is_configured(),
            "openai": call_manager.ai_service.is_configured(),
            "government": True
        }
    }

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