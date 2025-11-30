#!/bin/bash

# MediScanAI - Start Script
# Chạy cả Backend và Frontend cùng lúc

echo "🚀 Starting MediScanAI..."
echo ""

# Màu sắc cho output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Kiểm tra Python 3.11
if ! command -v /usr/local/opt/python@3.11/bin/python3.11 &> /dev/null; then
    echo -e "${RED}❌ Python 3.11 not found!${NC}"
    echo "Please install Python 3.11: brew install python@3.11"
    exit 1
fi

# Kiểm tra Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found!${NC}"
    echo "Please install Node.js: brew install node"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo -e "${BLUE}📡 Starting Backend (Port 5002)...${NC}"
cd Backend
/usr/local/opt/python@3.11/bin/python3.11 app.py > backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Đợi Backend khởi động
sleep 3

# Kiểm tra Backend
if curl -s http://localhost:5002/api/health > /dev/null; then
    echo -e "${GREEN}✅ Backend started successfully${NC}"
else
    echo -e "${YELLOW}⏳ Backend is starting (loading EasyOCR models...)${NC}"
    echo -e "${YELLOW}   This may take 1-2 minutes on first run${NC}"
fi

echo ""

# Start Frontend
echo -e "${BLUE}🎨 Starting Frontend (Port 3000)...${NC}"
cd Web
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Đợi Frontend khởi động
sleep 3

echo ""
echo -e "${GREEN}✨ MediScanAI is running!${NC}"
echo ""
echo "📍 URLs:"
echo "   Frontend: ${BLUE}http://localhost:3000${NC}"
echo "   Backend:  ${BLUE}http://localhost:5002${NC}"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f Backend/backend.log"
echo "   Frontend: tail -f Web/frontend.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Đợi cả 2 process
wait $BACKEND_PID
wait $FRONTEND_PID
