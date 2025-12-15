# Helios0.1 Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- Jira account with API token
- Google account with access to Google Drive
- (Optional) Gemini or OpenAI API key for AI features

## Step 1: Install Dependencies

```bash
cd Helios0.1
pip install -r requirements.txt
```

## Step 2: Set Environment Variables

Create a `.env` file or export these variables:

```bash
# Required: Jira Configuration
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"

# Required: Google Drive (will prompt for auth on first run)
# Just make sure you have credentials.json in this directory

# Optional: LLM for AI features (Gemini 2.0 recommended)
export GEMINI_API_KEY="your-gemini-key"  # Uses Gemini 2.0 (gemini-2.0-flash) by default
export LLM_MODEL="gemini-2.0-flash"  # Optional, already the default
# OR
export OPENAI_API_KEY="your-openai-key"
```

## Step 3: Get Google Drive Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Enable **Google Drive API** and **Google Docs API**
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Choose "Desktop app"
6. Download the JSON file
7. Save it as `credentials.json` in the Helios0.1 directory

## Step 4: Run the App

```bash
# Option 1: Use the startup script
./run.sh

# Option 2: Direct Streamlit command
streamlit run app.py
```

## Step 5: First Use

1. The app opens at `http://localhost:8501`
2. Click "Initialize Helios" in the sidebar
3. If prompted, authenticate Google Drive in your browser
4. Start asking questions like:
   - "What is the status of Project ABC?"
   - "Show me the roadmap for Project XYZ"

## Example Questions

- **Status**: "What is the current status of Project ABC?"
- **Roadmap**: "Show me the roadmap for Project XYZ"
- **Progress**: "What are the progress metrics for Project DEF?"
- **Follow-up**: After asking about a project, you can ask:
  - "Who has the most tasks?"
  - "What are the risks?"
  - "Show me overdue items"

## Troubleshooting

### "Jira configuration incomplete"
- Check that all three Jira env vars are set: `echo $JIRA_BASE_URL`

### "Credentials file not found"
- Make sure `credentials.json` is in the Helios0.1 directory
- Check the file name is exactly `credentials.json`

### "Failed to authenticate Google Drive"
- Make sure Google Drive API and Google Docs API are enabled
- Check that your OAuth consent screen is configured

### Charts not showing
- Make sure the project has issues in Jira
- Check that Plotly is installed: `pip install plotly`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize the charts and visualizations
- Integrate with additional data sources

Happy chatting with Helios! 🚀

