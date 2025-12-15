# Helios0.1 Chat Webapp

A simple AI-powered chat webapp that integrates Jira and Google Docs to provide project insights, summaries, roadmaps, and progress visualizations. Powered by **Google Gemini 2.0** for advanced summarization and intelligent agent capabilities.

## Features

- **Jira Integration**: Fetches project data including Epics, Stories, and Tasks
- **Google Docs Integration**: Searches and reads meeting summary notes from Google Drive
- **Intelligent Matching**: Finds relevant meeting notes based on project names mentioned in documents
- **Status Summary**: Generates comprehensive project status summaries
- **Roadmap with Risk Assessment**: Creates roadmaps with risk indicators (overdue, unassigned, etc.)
- **Progress Charts**: Visualizes progress by:
  - Total Epics, Stories, and Tasks
  - Status breakdown
  - Assignee distribution
  - Assignee vs Status heatmap
- **Chat Interface**: Ask questions and get AI-powered responses using Gemini 2.0
- **Follow-up Questions**: Continue the conversation with context-aware follow-ups
- **Gemini 2.0 Integration**: Advanced AI capabilities for summarization, analysis, and intelligent responses

## Setup

### 1. Install Dependencies

```bash
cd Helios0.1
pip install -r requirements.txt
```

### 2. Configure Credentials

**📖 See [CREDENTIALS.md](CREDENTIALS.md) for detailed instructions on setting up all API credentials.**

**Quick Setup:**

**Option A: Using .env file (Recommended for Development)**
1. Copy `.env.example` to `.env` (if available) or create a `.env` file
2. Fill in your credentials:
```bash
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
GEMINI_API_KEY=your-gemini-api-key
```

**Option B: Using Environment Variables (Recommended for Production)**
```bash
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
export GEMINI_API_KEY="your-gemini-api-key"
```

To get a Jira API token:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token

### 3. Configure Google Drive

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API and Google Docs API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the credentials JSON file
6. Save it as `credentials.json` in the Helios0.1 directory

Set environment variables (optional, defaults shown):

```bash
export GOOGLE_DRIVE_CREDENTIALS_FILE="credentials.json"
export GOOGLE_DRIVE_TOKEN_FILE="token.pickle"
```

### 4. Configure LLM (Optional but Recommended)

For AI-powered responses, set one of:

**Option 1: Google Gemini 2.0 (Recommended)**
```bash
export GEMINI_API_KEY="your-gemini-api-key"
export LLM_MODEL="gemini-2.0-flash"  # Optional, defaults to Gemini 2.0
```

Get your API key from: https://makersuite.google.com/app/apikey

**Note**: The app uses Gemini 2.0 (via `gemini-2.0-flash`) for advanced summarization and agent brain capabilities.

**Option 2: OpenAI**
```bash
export OPENAI_API_KEY="your-openai-api-key"
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4o-mini"  # Optional, defaults to gpt-4o-mini
```

## Running the App

### Start the Streamlit App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### First Run

1. Click "Initialize Helios" in the sidebar
2. If this is your first time using Google Drive, you'll be prompted to authenticate in your browser
3. Once initialized, you can start asking questions!

## Usage Examples

### Basic Questions

- "What is the status of Project ABC?"
- "Show me the roadmap for Project XYZ"
- "What are the current issues in Project DEF?"

### Follow-up Questions

After asking an initial question, you can ask follow-ups like:
- "Who is working on the most tasks?"
- "What are the risks in this project?"
- "Show me the overdue items"

## Project Structure

```
Helios0.1/
├── app.py                  # Main Streamlit UI
├── helios_chat.py          # Chat engine
├── jira_data_fetcher.py    # Jira data fetching and processing
├── google_docs_reader.py   # Google Docs reading and searching
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## How It Works

1. **Query Processing**: Extracts project name from your question
2. **Jira Data Fetching**: Retrieves all issues (Epics, Stories, Tasks) for the project
3. **Meeting Notes Search**: Searches Google Drive for meeting notes mentioning the project
4. **Data Analysis**: 
   - Generates status summaries
   - Creates roadmaps with risk assessment
   - Prepares data for visualizations
5. **AI Response**: Uses LLM to generate natural language responses
6. **Visualization**: Displays interactive charts using Plotly

## Charts Explained

- **Issues by Type**: Pie chart showing distribution of Epics, Stories, and Tasks
- **Issues by Status**: Bar chart showing count of issues in each status
- **Issues by Assignee**: Bar chart showing workload distribution (top 10)
- **Assignee vs Status Heatmap**: Matrix showing how many issues each person has in each status

## Troubleshooting

### "Jira configuration incomplete"
- Make sure all three Jira environment variables are set
- Verify your API token is correct

### "Credentials file not found"
- Download OAuth2 credentials from Google Cloud Console
- Save as `credentials.json` in the Helios0.1 directory

### "Failed to read document"
- Make sure the Google Docs API is enabled in Google Cloud Console
- Verify you have access to the documents you're trying to read

### Charts not showing
- Make sure Plotly is installed: `pip install plotly`
- Check that the project has issues in Jira

## Notes

- The app searches for meeting notes containing the project name
- Meeting notes are limited to the first 20 matching documents
- Charts show top 10 assignees if there are more
- The app maintains conversation history during your session

## License

This is a simple demo application. Use at your own discretion.

