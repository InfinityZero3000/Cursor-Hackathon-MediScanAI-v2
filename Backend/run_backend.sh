#!/bin/bash

# Script to run backend server

cd "$(dirname "$0")"

echo "🔍 Checking dependencies..."
python3 -c "import flask, cv2, pandas, PIL" 2>&1

if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip3 install Flask flask-cors opencv-python Pillow pandas "numpy>=1.26.0,<2.0" Werkzeug pypdf
fi

echo ""
echo "🚀 Starting backend server..."
echo "📡 API will be available at http://localhost:5001"
echo ""

python3 app.py

