#!/bin/bash

# MediScanAI - Stop Script
# Dừng tất cả servers

echo "🛑 Stopping MediScanAI..."

# Kill Backend (Python)
pkill -f "python.*app.py" && echo "✅ Backend stopped"

# Kill Frontend (Node)
pkill -f "vite" && echo "✅ Frontend stopped"

# Kill ports nếu vẫn còn
lsof -ti:5002 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo ""
echo "✨ All servers stopped"
