"""
Configuration management for Helios0.1 Chat Webapp.
Loads credentials from environment variables or .env file.
"""
import os
from typing import Dict, Optional

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # python-dotenv not installed, use environment variables only


def load_config() -> Dict:
    """
    Load configuration from environment variables.
    
    Environment variables:
    - JIRA_BASE_URL: Jira instance URL
    - JIRA_EMAIL: Jira email address
    - JIRA_API_TOKEN: Jira API token
    - GOOGLE_DRIVE_CREDENTIALS_FILE: Path to OAuth2 credentials JSON
    - GOOGLE_DRIVE_TOKEN_FILE: Path to store authentication token
    - GEMINI_API_KEY: Google Gemini API key for LLM features (Gemini 2.0)
    - OPENAI_API_KEY: OpenAI API key for LLM features (alternative)
    - LLM_PROVIDER: LLM provider ('gemini' default, or 'openai')
    - LLM_MODEL: LLM model name (default: 'gemini-2.0-flash' for Gemini 2.0, 'gpt-4o-mini' for OpenAI)
    """
    config = {
        'jira': {
            'base_url': os.getenv('JIRA_BASE_URL', ''),
            'email': os.getenv('JIRA_EMAIL', ''),
            'api_token': os.getenv('JIRA_API_TOKEN', '')
        },
        'google_drive': {
            'credentials_file': os.getenv('GOOGLE_DRIVE_CREDENTIALS_FILE', 'credentials.json'),
            'token_file': os.getenv('GOOGLE_DRIVE_TOKEN_FILE', 'token.pickle')
        }
    }
    
    # LLM configuration (optional)
    # Prefer Gemini 2.0, fallback to OpenAI
    llm_provider = os.getenv('LLM_PROVIDER', 'gemini').lower()
    llm_api_key = None
    default_model = None
    
    if llm_provider == 'gemini':
        llm_api_key = os.getenv('GEMINI_API_KEY')
        default_model = 'gemini-2.0-flash'  # Gemini 2.0
    elif llm_provider == 'openai':
        llm_api_key = os.getenv('OPENAI_API_KEY')
        default_model = 'gpt-4o-mini'
    else:
        # Auto-detect: try Gemini first, then OpenAI
        llm_api_key = os.getenv('GEMINI_API_KEY') or os.getenv('OPENAI_API_KEY')
        if os.getenv('GEMINI_API_KEY'):
            llm_provider = 'gemini'
            default_model = 'gemini-2.0-flash'  # Gemini 2.0
        elif os.getenv('OPENAI_API_KEY'):
            llm_provider = 'openai'
            default_model = 'gpt-4o-mini'
    
    if llm_api_key:
        config['llm'] = {
            'provider': llm_provider,
            'api_key': llm_api_key,
            'model': os.getenv('LLM_MODEL', default_model)
        }
    
    return config


def validate_config(config: Dict) -> bool:
    """Validate that required configuration is present."""
    required = [
        config['jira']['base_url'],
        config['jira']['email'],
        config['jira']['api_token']
    ]
    return all(required)

