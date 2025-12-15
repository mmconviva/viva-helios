#!/usr/bin/env python3
"""Test script to verify LLM (Gemini 2.0) is working correctly."""

from llm_service import LLMService
from config import load_config
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 60)
print("LLM (Gemini 2.0) Connection Test")
print("=" * 60)

# Load config
print("\n1. Loading configuration...")
config = load_config()
llm_config = config.get('llm', {})

if not llm_config:
    print("❌ ERROR: LLM not configured in config!")
    print("   Check your .env file for GEMINI_API_KEY")
    exit(1)

print(f"   ✅ Config loaded")
print(f"   Provider: {llm_config.get('provider')}")
print(f"   Model: {llm_config.get('model')}")
print(f"   API Key: {llm_config.get('api_key', '')[:20]}..." if llm_config.get('api_key') else "   API Key: NOT SET")

# Check API key from environment
api_key_from_env = os.getenv('GEMINI_API_KEY')
if api_key_from_env:
    print(f"   API Key from env: {api_key_from_env[:20]}...")
else:
    print("   ⚠️  GEMINI_API_KEY not found in environment")

# Initialize LLM Service
print("\n2. Initializing LLM Service...")
try:
    llm_service = LLMService(
        provider=llm_config.get('provider', 'gemini'),
        api_key=llm_config.get('api_key'),
        model=llm_config.get('model', 'gemini-2.0-flash')
    )
    print(f"   ✅ LLM Service initialized")
    print(f"   Provider: {llm_service.provider}")
    print(f"   Model: {llm_service.model}")
except Exception as e:
    print(f"   ❌ ERROR: Failed to initialize LLM Service: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 1: Simple generation
print("\n3. Test 1: Simple text generation...")
try:
    test_prompt = "Say 'Hello, I am working correctly!' in one sentence."
    print(f"   Prompt: {test_prompt}")
    
    if llm_service.provider == "gemini":
        response = llm_service.client.generate_content(test_prompt)
        answer = response.text.strip()
    else:  # OpenAI
        response = llm_service.client.chat.completions.create(
            model=llm_service.model,
            messages=[
                {"role": "user", "content": test_prompt}
            ]
        )
        answer = response.choices[0].message.content.strip()
    
    print(f"   ✅ Response received: {answer[:100]}")
except Exception as e:
    print(f"   ❌ ERROR: Failed to generate content: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 2: Summary generation
print("\n4. Test 2: Summary generation...")
try:
    test_text = """
    This is a test document about project management. 
    We have multiple teams working on different features.
    The project is progressing well with 50% completion.
    There are some risks related to timeline and resources.
    """
    summary = llm_service.generate_summary(test_text, max_length=50)
    print(f"   ✅ Summary generated: {summary[:100]}")
except Exception as e:
    print(f"   ❌ ERROR: Failed to generate summary: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 3: Action items extraction
print("\n5. Test 3: Action items extraction...")
try:
    meeting_text = """
    Meeting Notes:
    - John will complete the API documentation by Friday
    - Sarah needs to review the design mockups
    - Mike should update the project timeline
    """
    action_items = llm_service.extract_action_items(meeting_text)
    print(f"   ✅ Action items extracted: {len(action_items)} items")
    if action_items:
        for i, item in enumerate(action_items[:3], 1):
            print(f"      {i}. {item.get('task', 'N/A')[:50]}")
except Exception as e:
    print(f"   ❌ ERROR: Failed to extract action items: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Test with project context (like the app does)
print("\n6. Test 4: Project status query (like app usage)...")
try:
    project_context = """
    Project: AME
    Total Issues: 438
    Epics: 66
    Stories: 195
    Tasks: 177
    """
    test_query = "What is the status of Project AME?"
    prompt = f"""You are Helios, a project management assistant. Answer the user's question.

{project_context}

User Question: {test_query}

Provide a brief answer."""
    
    if llm_service.provider == "gemini":
        response = llm_service.client.generate_content(prompt)
        answer = response.text.strip()
    else:  # OpenAI
        response = llm_service.client.chat.completions.create(
            model=llm_service.model,
            messages=[
                {"role": "system", "content": "You are Helios, a helpful project management assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content.strip()
    
    print(f"   ✅ Project query response received")
    print(f"   Response: {answer[:200]}...")
except Exception as e:
    print(f"   ❌ ERROR: Failed to process project query: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - LLM is working correctly!")
print("=" * 60)

