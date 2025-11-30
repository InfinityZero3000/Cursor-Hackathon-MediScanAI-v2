#!/bin/bash

# MediScan Backend Start Script

echo "Starting MediScan Backend API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please configure .env file before running the server!"
    exit 1
fi

# Create uploads directory
mkdir -p uploads

# Run Flask app
echo "Starting Flask server..."
python app.py
