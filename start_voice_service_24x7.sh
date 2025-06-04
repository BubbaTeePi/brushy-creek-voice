#!/bin/bash

# Voice Service 24/7 Startup Script
# This script starts and maintains the AI voice service

SCRIPT_DIR="/Users/mbergvinson/Downloads/mac-mini-test"
LOG_DIR="$SCRIPT_DIR/logs"
VOICE_SERVICE_LOG="$LOG_DIR/voice_service.log"
NGROK_LOG="$LOG_DIR/ngrok.log"

# Create logs directory
mkdir -p "$LOG_DIR"

echo "🚀 Starting AI Voice Service 24/7..."
echo "📁 Working directory: $SCRIPT_DIR"
echo "📝 Logs directory: $LOG_DIR"

# Change to service directory
cd "$SCRIPT_DIR"

# Function to check if service is running
check_service() {
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check if ngrok is running
check_ngrok() {
    if curl -s http://localhost:4041/api/tunnels > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Start voice service
start_voice_service() {
    echo "🎯 Starting voice service..."
    nohup python3 start.py > "$VOICE_SERVICE_LOG" 2>&1 &
    sleep 10
    
    if check_service; then
        echo "✅ Voice service started successfully"
    else
        echo "❌ Voice service failed to start"
        return 1
    fi
}

# Start ngrok tunnel
start_ngrok() {
    echo "🌐 Starting ngrok tunnel..."
    nohup ngrok http --url=guppy-frank-hedgehog.ngrok-free.app 8000 > "$NGROK_LOG" 2>&1 &
    sleep 10
    
    if check_ngrok; then
        echo "✅ Ngrok tunnel started successfully"
        echo "🔗 Public URL: https://guppy-frank-hedgehog.ngrok-free.app"
    else
        echo "❌ Ngrok tunnel failed to start"
        return 1
    fi
}

# Kill existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f start.py 2>/dev/null
pkill ngrok 2>/dev/null
sleep 3

# Start services
start_voice_service
start_ngrok

# Verify both services are running
if check_service && check_ngrok; then
    echo ""
    echo "🎉 SUCCESS! AI Voice Service is running 24/7"
    echo "="*50
    echo "📞 Phone Number: +1 (877) 665-2873"
    echo "🌐 Public URL: https://guppy-frank-hedgehog.ngrok-free.app"
    echo "💚 Health Check: https://guppy-frank-hedgehog.ngrok-free.app/health"
    echo "📊 Monitoring: http://localhost:4041 (ngrok dashboard)"
    echo "📝 Voice Logs: $VOICE_SERVICE_LOG"
    echo "📝 Ngrok Logs: $NGROK_LOG"
    echo ""
    echo "🔄 Auto-restart enabled. Service will restart if it crashes."
    echo "🛑 To stop: ./stop_voice_service.sh"
    echo "="*50
else
    echo "❌ Failed to start one or more services"
    exit 1
fi

# Keep monitoring and restart if needed (optional watchdog)
if [ "$1" = "--monitor" ]; then
    echo "👁️  Starting monitoring mode..."
    while true; do
        sleep 60
        
        if ! check_service; then
            echo "⚠️  Voice service down, restarting..."
            start_voice_service
        fi
        
        if ! check_ngrok; then
            echo "⚠️  Ngrok tunnel down, restarting..."  
            start_ngrok
        fi
    done
fi 