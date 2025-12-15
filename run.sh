#!/bin/bash

# Helios0.1 Chat Webapp Startup Script

echo "🚀 Starting Helios0.1 Chat Webapp..."
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the Helios0.1 directory."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Check environment variables
echo "📋 Checking configuration..."
if [ -z "$JIRA_BASE_URL" ] || [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
    echo "⚠️  Warning: Jira environment variables not set."
    echo "   Please set: JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN"
    echo ""
fi

if [ ! -f "credentials.json" ]; then
    echo "⚠️  Warning: credentials.json not found."
    echo "   Please download OAuth2 credentials from Google Cloud Console."
    echo ""
fi

if [ -z "$GEMINI_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: LLM API key not set (GEMINI_API_KEY or OPENAI_API_KEY)."
    echo "   Some features may be limited."
    echo ""
fi

echo "✅ Starting Streamlit app..."
echo "   The app will open in your browser at http://localhost:8501"
echo ""

streamlit run app.py

