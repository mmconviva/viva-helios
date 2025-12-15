#!/bin/bash

# Helios0.1 Quick Start Script
# Activates virtual environment and runs the app

cd "$(dirname "$0")"

echo "🚀 Starting Helios0.1 Chat Webapp..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check credentials
echo ""
echo "📋 Checking configuration..."
if [ -z "$JIRA_BASE_URL" ] && [ ! -f ".env" ]; then
    echo "⚠️  Warning: Jira credentials not found in environment or .env file"
    echo "   Please set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN"
    echo ""
fi

if [ ! -f "credentials.json" ]; then
    echo "⚠️  Warning: credentials.json not found"
    echo "   Please download OAuth2 credentials from Google Cloud Console"
    echo ""
fi

if [ -z "$GEMINI_API_KEY" ] && [ ! -f ".env" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY not set (AI features will be limited)"
    echo ""
fi

echo "✅ Starting Streamlit app..."
echo "   The app will open in your browser at http://localhost:8501"
echo ""

streamlit run app.py

