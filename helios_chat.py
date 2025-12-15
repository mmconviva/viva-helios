"""
Helios0.1 Chat - Main chat engine that integrates Jira and Google Docs.
"""
from jira_data_fetcher import JiraDataFetcher
from google_docs_reader import GoogleDocsReader
from llm_service import LLMService
from typing import Dict, List, Optional, Any
import re


class HeliosChat:
    """Main chat engine for Helios0.1."""
    
    def __init__(self, jira_client, google_docs_reader: GoogleDocsReader, llm_service: LLMService):
        """
        Initialize Helios chat.
        
        Args:
            jira_client: Initialized JiraClient instance
            google_docs_reader: Initialized GoogleDocsReader instance
            llm_service: Initialized LLMService instance
        """
        self.jira_fetcher = JiraDataFetcher(jira_client)
        self.docs_reader = google_docs_reader
        self.llm = llm_service
        self.conversation_history = []
    
    def extract_project_name(self, query: str) -> Optional[str]:
        """
        Extract project name/key from user query.
        
        Args:
            query: User query string
        
        Returns:
            Project key/name if found, None otherwise
        """
        # Common words to exclude (not project names)
        excluded_words = {
            'WHAT', 'WHEN', 'WHERE', 'WHY', 'HOW', 'WHO', 'WHICH', 'WHOSE',
            'THE', 'IS', 'ARE', 'WAS', 'WERE', 'BE', 'BEEN', 'BEING',
            'OF', 'TO', 'IN', 'ON', 'AT', 'FOR', 'WITH', 'FROM', 'BY',
            'AND', 'OR', 'BUT', 'IF', 'THEN', 'ELSE', 'THIS', 'THAT',
            'STATUS', 'PROJECT', 'PROJECTS', 'SHOW', 'TELL', 'GIVE',
            'ME', 'MY', 'YOU', 'YOUR', 'OUR', 'THEIR', 'HIS', 'HER',
            'ABOUT', 'STATUS', 'ROADMAP', 'SUMMARY', 'DETAILS'
        }
        
        # Look for patterns like "Project ABC", "ABC", "project ABC", etc.
        # Priority order matters - more specific patterns first
        patterns = [
            r'project\s+([A-Z]{2,10})\b',  # "project ABC" or "Project ABC"
            r'Project\s+([A-Z]{2,10})\b',  # "Project ABC"
            r'\b([A-Z]{2,10})\s+project',   # "ABC project" or "ABC projects"
            r'\b([A-Z]{2,10})\s+projects',  # "ABC projects"
            r'of\s+([A-Z]{2,10})\b',        # "status of ABC"
            r'for\s+([A-Z]{2,10})\b',       # "status for ABC"
            r'\b([A-Z]{2,10})\b',           # Any 2-10 capital letters (last resort)
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, query, re.IGNORECASE)
            for match in matches:
                potential_project = match.group(1).upper()
                # Skip if it's a common word
                if potential_project not in excluded_words:
                    return potential_project
        
        return None
    
    def process_query(self, query: str, project_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query and generate response.
        
        Args:
            query: User query
            project_key: Optional project key (will be extracted from query if not provided)
        
        Returns:
            Dictionary with response data including summary, roadmap, charts data, etc.
        """
        # Extract project key if not provided
        if not project_key:
            project_key = self.extract_project_name(query)
        
        if not project_key:
            return {
                "error": "Could not identify project. Please mention the project name (e.g., 'What is the status of Project ABC?')",
                "response": "I couldn't identify which project you're asking about. Please mention the project name in your question."
            }
        
        # Fetch Jira data
        try:
            jira_data = self.jira_fetcher.get_project_issues(project_key)
            # Debug: Check what we got
            total = jira_data.get('total_issues', 0)
            epics_count = len(jira_data.get('epics', []))
            stories_count = len(jira_data.get('stories', []))
            tasks_count = len(jira_data.get('tasks', []))
            
            # If we got 0, try direct API call to debug
            if total == 0:
                jql = f"project = {project_key}"
                direct_issues = self.jira_fetcher.jira.search_issues(jql, max_results=10)
                if len(direct_issues) > 0:
                    # We have issues from API but they're not being categorized
                    # This suggests a categorization problem
                    issue_types = {}
                    for issue in direct_issues[:10]:
                        issue_type = issue.get('fields', {}).get('issuetype', {}).get('name', 'Unknown')
                        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
                    return {
                        "error": f"Found {len(direct_issues)} issues from API but categorization returned 0. Issue types found: {issue_types}",
                        "response": f"I found {len(direct_issues)} issues from Jira API, but they weren't categorized correctly. Issue types: {list(issue_types.keys())}. This may indicate a problem with issue type matching."
                    }
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return {
                "error": f"Failed to fetch Jira data: {str(e)}",
                "response": f"I encountered an error while fetching data from Jira: {str(e)}\n\nDetails: {error_details[:500]}"
            }
        
        # Find meeting notes
        meeting_notes = []
        try:
            meeting_notes = self.docs_reader.find_meeting_notes(project_key)
        except Exception as e:
            # Continue even if meeting notes fail
            pass
        
        # Generate summaries
        status_summary = self.jira_fetcher.generate_status_summary(jira_data)
        roadmap = self.jira_fetcher.generate_roadmap(jira_data)
        
        # Combine meeting notes context with Gemini 2.0 summarization
        meeting_context = ""
        if meeting_notes:
            meeting_context = "\n\n**Recent Meeting Notes:**\n"
            for note in meeting_notes[:3]:  # Top 3 most relevant
                note_content = note.get('content', '')
                note_name = note.get('name', 'Unknown')
                
                # Use Gemini 2.0 to summarize meeting notes if LLM is available
                if hasattr(self.llm, 'provider') and self.llm.provider != "dummy" and hasattr(self.llm, 'generate_summary'):
                    try:
                        # Summarize long meeting notes using Gemini 2.0
                        if len(note_content) > 500:
                            summary = self.llm.generate_summary(note_content, max_length=150)
                            meeting_context += f"- {note_name}: {summary}\n"
                        else:
                            meeting_context += f"- {note_name}: {note_content[:500]}...\n"
                    except Exception as e:
                        # Fallback to truncation if summarization fails
                        meeting_context += f"- {note_name}: {note_content[:500]}...\n"
                else:
                    # Fallback to truncation without LLM
                    meeting_context += f"- {note_name}: {note_content[:500]}...\n"
        
        # Determine if this is a status/overview query (use data-driven response)
        # or a complex analytical query (use LLM enhancement)
        query_lower = query.lower()
        is_status_query = any(phrase in query_lower for phrase in [
            'status', 'what is', 'show me', 'tell me about', 'overview', 
            'summary', 'how many', 'count', 'progress'
        ])
        
        # For status queries, always use data-driven response (more reliable)
        # For complex queries, use LLM to enhance the response
        if is_status_query or jira_data.get('total_issues', 0) == 0:
            # Use data-driven response for status queries
            answer = f"""**Project {project_key} Status:**

{status_summary}

{roadmap}

{meeting_context if meeting_context else ''}

Would you like more details about any specific aspect of this project?"""
        else:
            # For complex queries, try LLM but with strong validation
            try:
                if hasattr(self.llm, 'provider') and self.llm.provider != "dummy":
                    # Build a clearer prompt with explicit data
                    data_summary = f"""
Project Key: {project_key}
Total Issues: {jira_data.get('total_issues', 0)}
Epics: {len(jira_data.get('epics', []))}
Stories: {len(jira_data.get('stories', []))}
Tasks: {len(jira_data.get('tasks', []))}
"""
                    
                    llm_prompt = f"""You are Helios, a project management assistant. Answer the user's question about project {project_key}.

CRITICAL: The project {project_key} has {jira_data.get('total_issues', 0)} total issues. This is a FACT.

PROJECT DATA:
{data_summary}

STATUS SUMMARY:
{status_summary}

ROADMAP:
{roadmap}
{meeting_context}

USER QUESTION: {query}

INSTRUCTIONS:
- The project {project_key} DEFINITELY has {jira_data.get('total_issues', 0)} issues
- NEVER say there are no issues or that the project doesn't exist
- Reference the specific numbers from the data above
- Be accurate and helpful"""
                    
                    if self.llm.provider == "gemini":
                        response = self.llm.client.generate_content(llm_prompt)
                        answer = response.text.strip()
                    else:  # OpenAI
                        response = self.llm.client.chat.completions.create(
                            model=self.llm.model,
                            messages=[
                                {"role": "system", "content": "You are Helios, a helpful project management assistant. Always be accurate and reference the data provided."},
                                {"role": "user", "content": llm_prompt}
                            ]
                        )
                        answer = response.choices[0].message.content.strip()
                    
                    # Strong validation - if LLM says no issues when we have issues, override it
                    if jira_data.get('total_issues', 0) > 0:
                        no_issues_phrases = [
                            'no issues', 'no data', 'no information', 'not found', 
                            'does not exist', 'cannot find', 'unable to find', 
                            'there are no', 'no issues associated', 'within the what project'
                        ]
                        answer_lower = answer.lower()
                        if any(phrase in answer_lower for phrase in no_issues_phrases):
                            # LLM gave incorrect response, override with data-driven response
                            answer = f"""**Project {project_key} Status:**

{status_summary}

{roadmap}

{meeting_context if meeting_context else ''}

Would you like more details about any specific aspect of this project?"""
                else:
                    # No LLM, use data-driven response
                    answer = f"""**Project {project_key} Status:**

{status_summary}

{roadmap}

{meeting_context if meeting_context else ''}

Is there anything specific you'd like to know more about?"""
            except Exception as e:
                # On any error, use data-driven response
                answer = f"""**Project {project_key} Status:**

{status_summary}

{roadmap}

{meeting_context if meeting_context else ''}

(Note: AI processing encountered an issue, but here's the data we found)"""
        
        # Prepare charts data
        metrics = jira_data.get('metrics', {})
        charts_data = {
            'by_type': {
                'Epics': len(jira_data.get('epics', [])),
                'Stories': len(jira_data.get('stories', [])),
                'Tasks': len(jira_data.get('tasks', []))
            },
            'by_status': metrics.get('status_counts', {}),
            'by_assignee': metrics.get('assignee_counts', {}),
            'by_assignee_and_status': self._prepare_assignee_status_data(jira_data)
        }
        
        # Store in conversation history
        self.conversation_history.append({
            'query': query,
            'project_key': project_key,
            'response': answer
        })
        
        return {
            'project_key': project_key,
            'response': answer,
            'status_summary': status_summary,
            'roadmap': roadmap,
            'meeting_notes': meeting_notes,
            'charts_data': charts_data,
            'jira_data': jira_data
        }
    
    def _prepare_assignee_status_data(self, jira_data: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
        """Prepare data for assignee vs status chart."""
        all_issues = jira_data.get('epics', []) + jira_data.get('stories', []) + jira_data.get('tasks', [])
        
        assignee_status = {}
        for issue in all_issues:
            assignee = issue.get('assignee', 'Unassigned')
            status = issue.get('status', 'Unknown')
            
            if assignee not in assignee_status:
                assignee_status[assignee] = {}
            assignee_status[assignee][status] = assignee_status[assignee].get(status, 0) + 1
        
        return assignee_status
    
    def answer_followup(self, query: str, previous_context: Dict[str, Any]) -> str:
        """
        Answer a follow-up question using previous context.
        
        Args:
            query: Follow-up question
            previous_context: Previous response context
        
        Returns:
            Answer string
        """
        context_str = f"""
Previous Project: {previous_context.get('project_key')}
Previous Status Summary: {previous_context.get('status_summary', '')}
Previous Roadmap: {previous_context.get('roadmap', '')}
Previous Response: {previous_context.get('response', '')}

Current Question: {query}
"""
        
        try:
            if hasattr(self.llm, 'provider') and self.llm.provider != "dummy":
                prompt = f"""You are Helios, a project management assistant. Answer the follow-up question based on the previous context.

{context_str}

Provide a clear, helpful answer."""
                
                if self.llm.provider == "gemini":
                    response = self.llm.client.generate_content(prompt)
                    return response.text.strip()
                else:  # OpenAI
                    response = self.llm.client.chat.completions.create(
                        model=self.llm.model,
                        messages=[
                            {"role": "system", "content": "You are Helios, a helpful project management assistant."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    return response.choices[0].message.content.strip()
            else:
                # Fallback response
                return f"Based on the previous context about {previous_context.get('project_key', 'the project')}, I can help you understand the status, roadmap, and progress. What specific aspect would you like to know more about?"
        except Exception as e:
            return f"I encountered an error while processing your question: {str(e)}"

