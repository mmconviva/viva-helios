#!/usr/bin/env python3
"""Debug script to test the exact flow the app uses."""

from jira_client import JiraClient
from jira_data_fetcher import JiraDataFetcher
from helios_chat import HeliosChat
from google_docs_reader import GoogleDocsReader
from llm_service import LLMService
from config import load_config
from dotenv import load_dotenv
import os

load_dotenv()

print("=== Loading Config ===")
config = load_config()
jira_config = config['jira']
print(f"Base URL: {jira_config['base_url']}")
print(f"Email: {jira_config['email']}")

print("\n=== Creating Jira Client ===")
jira_client = JiraClient(
    base_url=jira_config['base_url'],
    email=jira_config['email'],
    api_token=jira_config['api_token']
)

print("\n=== Creating Google Docs Reader ===")
try:
    drive_config = config.get('google_drive', {})
    docs_reader = GoogleDocsReader(
        credentials_file=drive_config.get('credentials_file', 'credentials.json'),
        token_file=drive_config.get('token_file', 'token.pickle')
    )
    print("Google Docs Reader created successfully")
except Exception as e:
    print(f"Google Docs Reader failed (this is OK for testing): {e}")
    docs_reader = None

print("\n=== Creating LLM Service ===")
llm_config = config.get('llm', {})
if llm_config:
    try:
        llm_service = LLMService(
            provider=llm_config.get('provider', 'gemini'),
            api_key=llm_config.get('api_key'),
            model=llm_config.get('model', 'gemini-2.0-flash')
        )
        print(f"LLM Service created: {llm_service.model}")
    except Exception as e:
        print(f"LLM Service failed: {e}")
        llm_service = None
else:
    print("No LLM config, using None")
    llm_service = None

print("\n=== Creating Helios Chat ===")
if docs_reader:
    helios_chat = HeliosChat(jira_client, docs_reader, llm_service)
else:
    # Create a dummy reader if needed
    class DummyReader:
        def find_meeting_notes(self, project_name):
            return []
    helios_chat = HeliosChat(jira_client, DummyReader(), llm_service)

print("\n=== Testing Query: 'What is the status of Project AME?' ===")
query = "What is the status of Project AME?"
result = helios_chat.process_query(query)

print(f"\n=== Result Keys: {result.keys()}")
print(f"Has error: {'error' in result}")
if 'error' in result:
    print(f"Error: {result.get('error')}")
    print(f"Response: {result.get('response')}")

print(f"\n=== Jira Data ===")
jira_data = result.get('jira_data', {})
print(f"Jira data keys: {jira_data.keys() if jira_data else 'None'}")
if jira_data:
    print(f"Total Issues: {jira_data.get('total_issues', 'N/A')}")
    print(f"Epics: {len(jira_data.get('epics', []))}")
    print(f"Stories: {len(jira_data.get('stories', []))}")
    print(f"Tasks: {len(jira_data.get('tasks', []))}")
    print(f"Metrics: {jira_data.get('metrics', {})}")

print(f"\n=== Status Summary ===")
status_summary = result.get('status_summary', 'N/A')
print(status_summary[:500] if len(str(status_summary)) > 500 else status_summary)

print(f"\n=== Charts Data ===")
charts_data = result.get('charts_data', {})
print(f"Charts data keys: {charts_data.keys() if charts_data else 'None'}")
if charts_data:
    print(f"By type: {charts_data.get('by_type', {})}")
    print(f"By status: {charts_data.get('by_status', {})}")

