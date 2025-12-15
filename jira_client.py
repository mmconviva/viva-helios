"""
Jira API Client for interacting with Jira issues, projects, and workflows.
"""
import requests
from typing import Dict, List, Optional, Any
from requests.auth import HTTPBasicAuth
import json


class JiraClient:
    """Client for interacting with Jira API."""
    
    def __init__(self, base_url: str, email: str, api_token: str):
        """
        Initialize Jira client.
        
        Args:
            base_url: Jira instance URL (e.g., 'https://your-domain.atlassian.net')
            email: Your Jira email address
            api_token: Jira API token (generate from https://id.atlassian.com/manage-profile/security/api-tokens)
        """
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Jira API."""
        # Use API v3 (v2 search endpoint has been deprecated)
        url = f"{self.base_url}/rest/api/3/{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                auth=self.auth,
                json=data
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Jira API request failed: {str(e)}")
    
    def get_issue(self, issue_key: str) -> Dict:
        """Get details of a specific issue."""
        return self._make_request("GET", f"issue/{issue_key}")
    
    def create_issue(self, project_key: str, summary: str, description: str, 
                     issue_type: str = "Task", **kwargs) -> Dict:
        """Create a new Jira issue."""
        data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}]
                        }
                    ]
                },
                "issuetype": {"name": issue_type}
            }
        }
        # Add any additional fields
        for key, value in kwargs.items():
            data["fields"][key] = value
        
        return self._make_request("POST", "issue", data=data)
    
    def update_issue(self, issue_key: str, fields: Dict) -> Dict:
        """Update an existing issue."""
        data = {"fields": fields}
        return self._make_request("PUT", f"issue/{issue_key}", data=data)
    
    def search_issues(self, jql: str, max_results: int = 50, expand: str = None) -> List[Dict]:
        """Search issues using JQL (Jira Query Language)."""
        # Use the new /search/jql endpoint (required as of Jira API v3)
        import urllib.parse
        jql_encoded = urllib.parse.quote(jql)
        
        # Request essential fields for the search
        fields = "key,summary,issuetype,status,assignee,created,updated,priority,description,duedate"
        endpoint = f"search/jql?jql={jql_encoded}&maxResults={max_results}&fields={fields}"
        
        if expand:
            endpoint += f"&expand={expand}"
        else:
            # Get essential expanded fields
            endpoint += "&expand=names,schema"
        
        response = self._make_request("GET", endpoint)
        
        # The /search/jql endpoint returns: {'issues': [...], 'nextPageToken': ..., 'isLast': ...}
        if isinstance(response, dict):
            issues = response.get("issues", [])
            # Handle pagination if needed
            if not response.get('isLast', True) and len(issues) < max_results:
                # Fetch more pages if needed (up to max_results)
                next_token = response.get('nextPageToken')
                while next_token and len(issues) < max_results:
                    page_endpoint = f"search/jql?jql={jql_encoded}&maxResults={max_results}&nextPageToken={next_token}&fields={fields}"
                    if expand:
                        page_endpoint += f"&expand={expand}"
                    else:
                        page_endpoint += "&expand=names,schema"
                    page_response = self._make_request("GET", page_endpoint)
                    if isinstance(page_response, dict):
                        issues.extend(page_response.get("issues", []))
                        next_token = page_response.get('nextPageToken') if not page_response.get('isLast', True) else None
                    else:
                        break
            return issues
        return []
    
    def get_issue_with_comments(self, issue_key: str) -> Dict:
        """Get issue details including comments."""
        return self._make_request("GET", f"issue/{issue_key}?expand=renderedFields,names,schema,transitions,operations,editmeta,changelog,versionedRepresentations")
    
    def add_comment(self, issue_key: str, comment: str) -> Dict:
        """Add a comment to an issue."""
        data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": comment}]
                    }
                ]
            }
        }
        return self._make_request("POST", f"issue/{issue_key}/comment", data=data)
    
    def get_projects(self) -> List[Dict]:
        """Get all accessible projects."""
        # Try /project endpoint first (simpler, returns list directly)
        try:
            response = self._make_request("GET", "project")
            if isinstance(response, list):
                return response
        except Exception:
            pass
        
        # Fallback to /project/search endpoint (returns paginated results)
        try:
            response = self._make_request("GET", "project/search")
            # The response is a dict with 'values' key containing the projects list
            if isinstance(response, dict):
                projects = response.get('values', [])
                total = response.get('total', len(projects))
                # If we have pagination, fetch all pages
                if total > len(projects) and not response.get('isLast', True):
                    all_projects = list(projects)
                    start_at = len(projects)
                    while start_at < total:
                        page_response = self._make_request("GET", f"project/search?startAt={start_at}")
                        if isinstance(page_response, dict):
                            all_projects.extend(page_response.get('values', []))
                            start_at += len(page_response.get('values', []))
                            if page_response.get('isLast', True):
                                break
                        else:
                            break
                    return all_projects
                return projects
        except Exception:
            pass
        
        # If both fail, return empty list
        return []
    
    def transition_issue(self, issue_key: str, transition_id: str) -> Dict:
        """Transition an issue to a different status."""
        data = {"transition": {"id": transition_id}}
        return self._make_request("POST", f"issue/{issue_key}/transitions", data=data)
    
    def get_issue_transitions(self, issue_key: str) -> List[Dict]:
        """Get available transitions for an issue."""
        response = self._make_request("GET", f"issue/{issue_key}/transitions")
        return response.get("transitions", [])

