# API Credentials Configuration Guide

This guide explains how to configure all API credentials for Helios0.1 Chat Webapp.

## Quick Overview

Helios0.1 requires credentials for:
1. **Jira** (Required) - For fetching project data
2. **Google Drive** (Required) - For reading meeting notes
3. **Gemini API** (Optional but Recommended) - For AI-powered responses

## Method 1: Environment Variables (Recommended for Production)

Set environment variables in your shell before running the app.

### For Linux/macOS (bash/zsh):

```bash
# Jira Configuration (Required)
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"

# Gemini API (Optional but Recommended)
export GEMINI_API_KEY="your-gemini-api-key"

# Google Drive (Optional - defaults shown)
export GOOGLE_DRIVE_CREDENTIALS_FILE="credentials.json"
export GOOGLE_DRIVE_TOKEN_FILE="token.pickle"
```

### For Windows (PowerShell):

```powershell
# Jira Configuration (Required)
$env:JIRA_BASE_URL="https://your-domain.atlassian.net"
$env:JIRA_EMAIL="your-email@example.com"
$env:JIRA_API_TOKEN="your-api-token"

# Gemini API (Optional but Recommended)
$env:GEMINI_API_KEY="your-gemini-api-key"
```

### For Windows (Command Prompt):

```cmd
set JIRA_BASE_URL=https://your-domain.atlassian.net
set JIRA_EMAIL=your-email@example.com
set JIRA_API_TOKEN=your-api-token
set GEMINI_API_KEY=your-gemini-api-key
```

## Method 2: .env File (Recommended for Development)

Create a `.env` file in the `Helios0.1` directory:

```bash
# .env file
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token

# Gemini API (Optional but Recommended)
GEMINI_API_KEY=your-gemini-api-key

# Google Drive (Optional - defaults shown)
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
GOOGLE_DRIVE_TOKEN_FILE=token.pickle
```

**Note**: Make sure `.env` is in `.gitignore` (already included) to avoid committing credentials.

## Detailed Credential Setup

### 1. Jira API Credentials (Required)

**Where to get them:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a label (e.g., "Helios0.1")
4. Copy the generated token immediately (you won't see it again)

**Environment Variables:**
- `JIRA_BASE_URL`: Your Jira instance URL (e.g., `https://yourcompany.atlassian.net`)
- `JIRA_EMAIL`: Your Jira account email address
- `JIRA_API_TOKEN`: The API token you just created

**Example:**
```bash
export JIRA_BASE_URL="https://mycompany.atlassian.net"
export JIRA_EMAIL="john.doe@mycompany.com"
export JIRA_API_TOKEN="ATATT3xFfGF0..."
```

### 2. Google Drive Credentials (Required)

**Where to get them:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Drive API
   - Google Docs API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Choose "Desktop app" as the application type
6. Download the JSON file
7. Save it as `credentials.json` in the `Helios0.1` directory

**File Location:**
- Place `credentials.json` in the `Helios0.1` folder
- The app will automatically use it (or set `GOOGLE_DRIVE_CREDENTIALS_FILE` to a different path)

**First-time Authentication:**
- On first run, the app will open a browser window for OAuth authentication
- After authentication, a `token.pickle` file will be created
- This file stores your authentication token for future use

**Environment Variables (Optional):**
- `GOOGLE_DRIVE_CREDENTIALS_FILE`: Path to credentials.json (default: `credentials.json`)
- `GOOGLE_DRIVE_TOKEN_FILE`: Path to store token (default: `token.pickle`)

### 3. Gemini API Key (Optional but Recommended)

**Where to get it:**
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

**Environment Variables:**
- `GEMINI_API_KEY`: Your Gemini API key
- `LLM_MODEL`: Model name (optional, defaults to `gemini-2.0-flash` for Gemini 2.0)
- `LLM_PROVIDER`: Set to `gemini` (optional, already the default)

**Example:**
```bash
export GEMINI_API_KEY="AIzaSy..."
export LLM_MODEL="gemini-2.0-flash"  # Optional
```

**Note**: The app uses Gemini 2.0 by default for advanced AI capabilities.

### 4. OpenAI API Key (Alternative to Gemini)

If you prefer OpenAI instead of Gemini:

**Where to get it:**
1. Go to https://platform.openai.com/api-keys
2. Sign in and create a new API key
3. Copy the key

**Environment Variables:**
```bash
export OPENAI_API_KEY="sk-..."
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4o-mini"  # Optional
```

## Verifying Your Credentials

### Check Environment Variables

**Linux/macOS:**
```bash
echo $JIRA_BASE_URL
echo $JIRA_EMAIL
echo $GEMINI_API_KEY
```

**Windows (PowerShell):**
```powershell
$env:JIRA_BASE_URL
$env:JIRA_EMAIL
$env:GEMINI_API_KEY
```

### Test Configuration

Run the app and check the initialization message:
```bash
streamlit run app.py
```

If credentials are missing, you'll see warnings in the sidebar.

## Security Best Practices

1. **Never commit credentials to Git**
   - `.env` and `credentials.json` are already in `.gitignore`
   - Never commit API keys or tokens

2. **Use environment variables in production**
   - More secure than files
   - Can be managed by your deployment platform

3. **Rotate credentials regularly**
   - Especially if they're exposed or compromised

4. **Use separate credentials for development and production**
   - Different API keys for different environments

## Troubleshooting

### "Jira configuration incomplete"
- Check that all three Jira variables are set: `JIRA_BASE_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`
- Verify the API token is correct (create a new one if needed)
- Make sure there are no extra spaces in the values

### "Credentials file not found"
- Ensure `credentials.json` is in the `Helios0.1` directory
- Or set `GOOGLE_DRIVE_CREDENTIALS_FILE` to the correct path

### "Gemini API key not provided"
- Set `GEMINI_API_KEY` environment variable
- Or the app will work without it (with limited AI features)

### "Failed to authenticate Google Drive"
- Make sure Google Drive API and Google Docs API are enabled
- Check that OAuth consent screen is configured
- Delete `token.pickle` and re-authenticate

## Updating Credentials

### To Update Jira Credentials:
```bash
export JIRA_BASE_URL="new-url"
export JIRA_EMAIL="new-email"
export JIRA_API_TOKEN="new-token"
```

### To Update Gemini API Key:
```bash
export GEMINI_API_KEY="new-key"
```

### To Update Google Drive:
- Replace `credentials.json` with new file
- Delete `token.pickle` to force re-authentication

## Example Complete Setup

Create a `setup_credentials.sh` script:

```bash
#!/bin/bash
# Helios0.1 Credentials Setup

export JIRA_BASE_URL="https://yourcompany.atlassian.net"
export JIRA_EMAIL="your.email@company.com"
export JIRA_API_TOKEN="ATATT3xFfGF0..."

export GEMINI_API_KEY="AIzaSy..."

# Google Drive credentials.json should be in the same directory
# No environment variables needed for Google Drive (uses defaults)

echo "Credentials configured!"
echo "Run: streamlit run app.py"
```

Make it executable: `chmod +x setup_credentials.sh`

Then run: `source setup_credentials.sh`

