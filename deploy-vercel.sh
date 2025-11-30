#!/bin/bash

# MediScanAI - Vercel Deployment Script
echo "🚀 Deploying MediScanAI Frontend to Vercel..."
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found!"
    echo "Installing Vercel CLI..."
    npm install -g vercel
fi

# Navigate to Web directory
cd Web

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the project
echo "🔨 Building React app..."
npm run build

# Go back to root
cd ..

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo ""
echo "⚠️  Important: Update API_URL in Web/src/utils/api.js with your backend URL"
