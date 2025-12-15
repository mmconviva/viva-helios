"""
LLM Service for generating summaries and extracting action items.
Supports OpenAI and Google Gemini API with Gemini 2.0.
"""
import os
import json
from typing import Dict, List, Optional, Any

# Conditional imports for LLM providers
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class LLMService:
    """Service for interacting with Large Language Models."""
    
    def __init__(self, provider: str = "gemini", api_key: Optional[str] = None, 
                 model: str = "gemini-2.0-flash"):
        """
        Initialize LLM service.
        
        Args:
            provider: LLM provider ('gemini', 'openai')
            api_key: API key for the provider (if None, reads from env)
            model: Model name to use (default: Gemini 2.0)
        """
        self.provider = provider.lower()
        self.model = model
        
        if self.provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
            self.api_key = api_key or os.getenv("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable.")
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(model)
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                self.api_key = api_key or os.getenv("OPENAI_API_KEY")
                if not self.api_key:
                    raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("OpenAI package not installed. Install with: pip install openai")
        else:
            raise ValueError(f"Provider {provider} not supported. Use 'gemini' or 'openai'.")
    
    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """
        Generate a concise summary of the given text using Gemini 2.0.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words
        
        Returns:
            Generated summary
        """
        prompt = f"""Please provide a concise summary of the following text in approximately {max_length} words or less.
Focus on the key points, current status, and any important details.

Text:
{text}

Summary:"""
        
        try:
            if self.provider == "gemini":
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=500
                    )
                )
                return response.text.strip()
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that creates concise, informative summaries."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")
    
    def extract_action_items(self, meeting_summary: str) -> List[Dict[str, Any]]:
        """
        Extract action items from a meeting summary.
        
        Args:
            meeting_summary: Text of the meeting summary
        
        Returns:
            List of action items with details
        """
        # Adjust prompt based on provider for better JSON formatting
        if self.provider == "gemini":
            prompt = f"""Analyze the following meeting summary and extract all action items.
For each action item, identify:
1. The task/action description
2. The assignee (person responsible, if mentioned)
3. Priority (high/medium/low, if mentioned)
4. Due date or timeline (if mentioned)
5. Related context or dependencies

Return the results as a JSON object with an "action_items" array:
{{
  "action_items": [
    {{
      "task": "description of the action item",
      "assignee": "name or null if not mentioned",
      "priority": "high/medium/low or null",
      "due_date": "date or timeline or null",
      "context": "additional context or dependencies"
    }}
  ]
}}

Meeting Summary:
{meeting_summary}"""
        else:
            prompt = f"""Analyze the following meeting summary and extract all action items.
For each action item, identify:
1. The task/action description
2. The assignee (person responsible, if mentioned)
3. Priority (high/medium/low, if mentioned)
4. Due date or timeline (if mentioned)
5. Related context or dependencies

Return the results as a JSON array with the following structure:
[
  {{
    "task": "description of the action item",
    "assignee": "name or null if not mentioned",
    "priority": "high/medium/low or null",
    "due_date": "date or timeline or null",
    "context": "additional context or dependencies"
  }}
]

Meeting Summary:
{meeting_summary}

Action Items (JSON only, no additional text):"""
        
        try:
            if self.provider == "gemini":
                # Gemini supports JSON mode
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        response_mime_type="application/json"
                    )
                )
                content = response.text.strip()
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that extracts action items from meeting summaries. Always return valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"} if "gpt-4" in self.model else None
                )
                content = response.choices[0].message.content.strip()
            
            # Try to parse JSON - handle cases where LLM adds extra text
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            # Try to extract JSON array
            try:
                parsed = json.loads(content)
                if isinstance(parsed, dict) and "action_items" in parsed:
                    return parsed["action_items"]
                elif isinstance(parsed, list):
                    return parsed
                elif isinstance(parsed, dict):
                    # Single action item or wrapped in a key
                    if len(parsed) == 1 and isinstance(list(parsed.values())[0], list):
                        return list(parsed.values())[0]
                    return [parsed]
            except json.JSONDecodeError:
                # Fallback: try to find JSON array in the response
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                # Try to find JSON object
                json_obj_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_obj_match:
                    parsed = json.loads(json_obj_match.group())
                    if isinstance(parsed, dict) and "action_items" in parsed:
                        return parsed["action_items"]
                raise
            
            return []
        except Exception as e:
            raise Exception(f"Failed to extract action items: {str(e)}")
    
    def generate_issue_summary(self, issue_data: Dict) -> str:
        """
        Generate a comprehensive summary of a Jira issue for status updates.
        
        Args:
            issue_data: Jira issue data dictionary
        
        Returns:
            Generated summary text
        """
        fields = issue_data.get('fields', {})
        issue_key = issue_data.get('key', 'Unknown')
        
        summary = fields.get('summary', 'No summary')
        description = self._extract_text_from_jira_content(fields.get('description', {}))
        status = fields.get('status', {}).get('name', 'Unknown')
        assignee = fields.get('assignee', {}).get('displayName', 'Unassigned')
        reporter = fields.get('reporter', {}).get('displayName', 'Unknown')
        comments = fields.get('comment', {}).get('comments', [])
        
        # Get recent comments
        recent_comments = []
        for comment in comments[-3:]:  # Last 3 comments
            comment_text = self._extract_text_from_jira_content(comment.get('body', {}))
            comment_author = comment.get('author', {}).get('displayName', 'Unknown')
            recent_comments.append(f"{comment_author}: {comment_text}")
        
        issue_context = f"""
Jira Issue: {issue_key}
Title: {summary}
Status: {status}
Assignee: {assignee}
Reporter: {reporter}

Description:
{description}

Recent Comments:
{chr(10).join(recent_comments) if recent_comments else 'No comments'}
"""
        
        prompt = f"""Based on the following Jira issue information, generate a comprehensive status summary.
The summary should include:
1. Current status and progress
2. Key accomplishments or blockers
3. Next steps or recommendations
4. Any risks or dependencies

Issue Information:
{issue_context}

Status Summary:"""
        
        try:
            if self.provider == "gemini":
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=800
                    )
                )
                return response.text.strip()
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a project management assistant that creates clear, actionable status summaries for Jira issues."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Failed to generate issue summary: {str(e)}")
    
    def suggest_ticket_structure(self, action_items: List[Dict]) -> Dict[str, Any]:
        """
        Analyze action items and suggest ticket structure (parent/child relationships).
        
        Args:
            action_items: List of action items extracted from meeting
        
        Returns:
            Dictionary with suggested ticket structure
        """
        items_json = json.dumps(action_items, indent=2)
        
        prompt = f"""Analyze the following action items and suggest how they should be structured as Jira tickets.
Determine:
1. Which items should be parent tickets vs subtasks
2. Grouping of related items
3. Suggested issue types (Task, Story, Bug, Epic, etc.)
4. Suggested priorities
5. Dependencies between items

Action Items:
{items_json}

Return a JSON object with this structure:
{{
  "parent_tickets": [
    {{
      "summary": "ticket title",
      "issue_type": "Epic/Story/Task",
      "description": "detailed description",
      "priority": "high/medium/low",
      "subtasks": [
        {{
          "summary": "subtask title",
          "description": "subtask description",
          "assignee": "name or null"
        }}
      ]
    }}
  ],
  "standalone_tickets": [
    {{
      "summary": "ticket title",
      "issue_type": "Task/Bug",
      "description": "description",
      "priority": "high/medium/low",
      "assignee": "name or null"
    }}
  ]
}}

Suggested Structure (JSON only):"""
        
        try:
            if self.provider == "gemini":
                response = self.client.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        response_mime_type="application/json"
                    )
                )
                content = response.text.strip()
            else:  # OpenAI
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a project management assistant that structures action items into well-organized Jira tickets. Always return valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"} if "gpt-4" in self.model else None
                )
                content = response.choices[0].message.content.strip()
            
            # Clean up JSON response
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()
            
            return json.loads(content)
        except Exception as e:
            raise Exception(f"Failed to suggest ticket structure: {str(e)}")
    
    def _extract_text_from_jira_content(self, content: Any) -> str:
        """Extract plain text from Jira's content format."""
        if isinstance(content, str):
            return content
        if isinstance(content, dict):
            if 'content' in content:
                return self._extract_text_from_jira_content(content['content'])
            if 'text' in content:
                return content['text']
        if isinstance(content, list):
            return ' '.join([
                self._extract_text_from_jira_content(item) 
                for item in content 
                if item.get('type') == 'text' or item.get('type') == 'paragraph'
            ])
        return str(content) if content else ""

