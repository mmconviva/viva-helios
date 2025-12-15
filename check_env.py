#!/usr/bin/env python3
"""
Script to check and validate .env file configuration.
Shows what needs to be updated.
"""
import os
from pathlib import Path

# Change to script directory
script_dir = Path(__file__).parent
os.chdir(script_dir)

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    env_loaded = True
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    env_loaded = False

print("=" * 60)
print("Helios0.1 Environment Configuration Checker")
print("=" * 60)
print()

# Check if .env file exists
env_file = Path(".env")
if not env_file.exists():
    print("❌ .env file not found!")
    print("   Create a .env file in the Helios0.1 directory.")
    print("   You can copy .env.example as a template.")
    print()
    exit(1)

print(f"✅ Found .env file: {env_file.absolute()}")
print()

# Read and check .env file
issues = []
warnings = []

# Check Jira configuration
print("📋 JIRA CONFIGURATION:")
jira_base_url = os.getenv('JIRA_BASE_URL', '')
jira_email = os.getenv('JIRA_EMAIL', '')
jira_token = os.getenv('JIRA_API_TOKEN', '')

# Check for placeholder values
if not jira_base_url or 'your-domain' in jira_base_url:
    print(f"  ❌ JIRA_BASE_URL: {jira_base_url or 'NOT SET'}")
    issues.append("JIRA_BASE_URL contains placeholder 'your-domain' or is empty")
    print("     → Replace with your actual Jira URL (e.g., https://yourcompany.atlassian.net)")
else:
    print(f"  ✅ JIRA_BASE_URL: {jira_base_url}")

if not jira_email or 'your-email' in jira_email:
    print(f"  ❌ JIRA_EMAIL: {jira_email or 'NOT SET'}")
    issues.append("JIRA_EMAIL contains placeholder 'your-email' or is empty")
    print("     → Replace with your actual Jira account email")
else:
    print(f"  ✅ JIRA_EMAIL: {jira_email}")

if not jira_token or 'your-api-token' in jira_token:
    print(f"  ❌ JIRA_API_TOKEN: {'SET' if jira_token else 'NOT SET'} (contains placeholder)")
    issues.append("JIRA_API_TOKEN contains placeholder 'your-api-token' or is empty")
    print("     → Replace with your actual Jira API token")
    print("     → Get it from: https://id.atlassian.com/manage-profile/security/api-tokens")
else:
    print(f"  ✅ JIRA_API_TOKEN: SET")

print()

# Check Google Drive
print("📁 GOOGLE DRIVE:")
credentials_file = os.getenv('GOOGLE_DRIVE_CREDENTIALS_FILE', 'credentials.json')
if Path(credentials_file).exists():
    print(f"  ✅ credentials.json: Found")
else:
    print(f"  ❌ credentials.json: Not found")
    issues.append(f"credentials.json not found at {credentials_file}")

token_file = os.getenv('GOOGLE_DRIVE_TOKEN_FILE', 'token.pickle')
if Path(token_file).exists():
    print(f"  ✅ token.pickle: Found (will be auto-generated if missing)")
else:
    print(f"  ⚠️  token.pickle: Not found (will be auto-generated on first run)")

print()

# Check Gemini API
print("🤖 GEMINI API (Optional but Recommended):")
gemini_key = os.getenv('GEMINI_API_KEY', '')
if not gemini_key:
    print(f"  ⚠️  GEMINI_API_KEY: NOT SET")
    warnings.append("GEMINI_API_KEY not set - AI features will be limited")
    print("     → Get it from: https://makersuite.google.com/app/apikey")
else:
    print(f"  ✅ GEMINI_API_KEY: SET")

print()

# Summary
print("=" * 60)
print("SUMMARY:")
print("=" * 60)

if issues:
    print(f"\n❌ Found {len(issues)} issue(s) that need to be fixed:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    print("\n📝 To fix:")
    print("   1. Open the .env file in the Helios0.1 directory")
    print("   2. Replace all placeholder values with your actual credentials")
    print("   3. Save the file and restart the app")
    print()
    exit(1)
elif warnings:
    print(f"\n⚠️  Found {len(warnings)} warning(s):")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")
    print("\n✅ All required credentials are configured!")
    print("   The app will work, but some features may be limited.")
    print()
    exit(0)
else:
    print("\n✅ All credentials are properly configured!")
    print("   You're ready to run the app!")
    print()
    exit(0)

