#!/bin/bash

# Script to build and deploy to Firebase Hosting

echo "🔨 Building frontend..."
cd Web
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"
cd ..

echo "🚀 Deploying to Firebase Hosting..."
firebase deploy --only hosting

if [ $? -eq 0 ]; then
    echo "✅ Deploy successful!"
    echo "🌐 Your app is live at: https://mediscanai-96f18.web.app"
else
    echo "❌ Deploy failed!"
    exit 1
fi

