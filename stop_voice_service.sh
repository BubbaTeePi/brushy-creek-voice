#!/bin/bash

# Stop Voice Service Script

echo "🛑 Stopping AI Voice Service..."

# Kill voice service
echo "🎯 Stopping voice service..."
pkill -f start.py
pkill -f "python3 start.py"

# Kill ngrok
echo "🌐 Stopping ngrok tunnel..."
pkill ngrok

# Wait a moment
sleep 3

# Check if processes are stopped
if ! pgrep -f start.py > /dev/null && ! pgrep ngrok > /dev/null; then
    echo "✅ All services stopped successfully"
    echo "📱 Phone calls to +1 (877) 665-2873 will no longer work"
    echo "🔄 To restart: ./start_voice_service_24x7.sh"
else
    echo "⚠️  Some processes may still be running"
    echo "📋 Current processes:"
    pgrep -fl "start.py|ngrok" || echo "   No processes found"
fi 