"""
Jira Data Fetcher - Fetches project data including epics, stories, and tasks.
"""
from jira_client import JiraClient
from typing import Dict, List, Optional, Any
from datetime import datetime
import re


class JiraDataFetcher:
    """Fetches and processes Jira project data."""
    
    def __init__(self, jira_client: JiraClient):
        """
        Initialize Jira data fetcher.
        
        Args:
            jira_client: Initialized JiraClient instance
        """
        self.jira = jira_client
    
    def get_project_issues(self, project_key: str) -> Dict[str, Any]:
        """
        Get all issues for a project, categorized by type.
        
        Args:
            project_key: Jira project key (e.g., 'PROJ')
        
        Returns:
            Dictionary with epics, stories, tasks, and metrics
        """
        # First, verify the project exists by trying to get project info
        try:
            projects = self.jira.get_projects()
            project_keys = [p.get('key', '') for p in projects]
            if project_key not in project_keys:
                available_projects = ', '.join(project_keys[:10])  # Show first 10
                raise Exception(
                    f"Project '{project_key}' not found. "
                    f"Available projects: {available_projects}"
                    + (f" (and {len(project_keys) - 10} more)" if len(project_keys) > 10 else "")
                )
        except Exception as e:
            # If project listing fails, continue anyway - might be a permission issue
            pass
        
        # Search for all issues in the project
        jql = f"project = {project_key}"
        all_issues = self.jira.search_issues(jql, max_results=500)
        
        epics = []
        stories = []
        tasks = []
        
        for issue in all_issues:
            fields = issue.get('fields', {})
            issue_type = fields.get('issuetype', {}).get('name', '').lower()
            assignee = fields.get('assignee')
            assignee_name = assignee.get('displayName', 'Unassigned') if assignee else 'Unassigned'
            status = fields.get('status', {}).get('name', 'Unknown')
            
            issue_data = {
                'key': issue.get('key'),
                'summary': fields.get('summary', ''),
                'status': status,
                'assignee': assignee_name,
                'created': fields.get('created', ''),
                'updated': fields.get('updated', ''),
                'priority': fields.get('priority', {}).get('name', 'Medium'),
                'due_date': fields.get('duedate', ''),
                'description': self._extract_text_from_content(fields.get('description')),
                'url': f"{self.jira.base_url}/browse/{issue.get('key')}"
            }
            
            if 'epic' in issue_type:
                epic_name = fields.get('customfield_10011', '')  # Epic Name field
                issue_data['epic_name'] = epic_name
                epics.append(issue_data)
            elif 'story' in issue_type:
                stories.append(issue_data)
            elif 'task' in issue_type or 'subtask' in issue_type:
                tasks.append(issue_data)
        
        # Calculate metrics
        metrics = self._calculate_metrics(epics, stories, tasks)
        
        return {
            'project_key': project_key,
            'epics': epics,
            'stories': stories,
            'tasks': tasks,
            'metrics': metrics,
            'total_issues': len(epics) + len(stories) + len(tasks)
        }
    
    def _calculate_metrics(self, epics: List[Dict], stories: List[Dict], tasks: List[Dict]) -> Dict[str, Any]:
        """Calculate project metrics."""
        all_issues = epics + stories + tasks
        
        # Status breakdown
        status_counts = {}
        for issue in all_issues:
            status = issue.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Assignee breakdown
        assignee_counts = {}
        for issue in all_issues:
            assignee = issue.get('assignee', 'Unassigned')
            assignee_counts[assignee] = assignee_counts.get(assignee, 0) + 1
        
        # Count by type
        type_counts = {
            'epics': len(epics),
            'stories': len(stories),
            'tasks': len(tasks)
        }
        
        # Count by status and assignee (for charts)
        status_assignee_matrix = {}
        for issue in all_issues:
            status = issue.get('status', 'Unknown')
            assignee = issue.get('assignee', 'Unassigned')
            key = f"{assignee}|{status}"
            status_assignee_matrix[key] = status_assignee_matrix.get(key, 0) + 1
        
        # Overdue issues
        overdue_count = 0
        today = datetime.now().date()
        for issue in all_issues:
            due_date_str = issue.get('due_date')
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
                    if due_date < today and issue.get('status') not in ['Done', 'Closed', 'Resolved']:
                        overdue_count += 1
                except:
                    pass
        
        return {
            'status_counts': status_counts,
            'assignee_counts': assignee_counts,
            'type_counts': type_counts,
            'status_assignee_matrix': status_assignee_matrix,
            'overdue_count': overdue_count,
            'total_issues': len(all_issues)
        }
    
    def _extract_text_from_content(self, content: Any) -> str:
        """Extract plain text from Jira's content format."""
        if not content:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, dict):
            if 'content' in content:
                return self._extract_text_from_content(content['content'])
            if 'text' in content:
                return content['text']
        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        texts.append(item.get('text', ''))
                    elif item.get('type') == 'paragraph':
                        texts.append(self._extract_text_from_content(item.get('content', [])))
                elif isinstance(item, str):
                    texts.append(item)
            return ' '.join(texts)
        return str(content) if content else ""
    
    def generate_status_summary(self, project_data: Dict[str, Any]) -> str:
        """Generate a status summary for the project."""
        metrics = project_data.get('metrics', {})
        epics = project_data.get('epics', [])
        stories = project_data.get('stories', [])
        tasks = project_data.get('tasks', [])
        
        # Calculate total from actual lists if metrics is missing total_issues
        total_from_metrics = metrics.get('total_issues', 0)
        total_from_lists = len(epics) + len(stories) + len(tasks)
        total_issues = total_from_metrics if total_from_metrics > 0 else total_from_lists
        
        summary_parts = [
            f"**Project: {project_data.get('project_key')}**\n",
            f"Total Issues: {total_issues}",
            f"  - Epics: {len(epics)}",
            f"  - Stories: {len(stories)}",
            f"  - Tasks: {len(tasks)}",
            f"\n**Status Breakdown:**"
        ]
        
        for status, count in metrics.get('status_counts', {}).items():
            summary_parts.append(f"  - {status}: {count}")
        
        if metrics.get('overdue_count', 0) > 0:
            summary_parts.append(f"\n⚠️ **Overdue Issues: {metrics['overdue_count']}**")
        
        return '\n'.join(summary_parts)
    
    def generate_roadmap(self, project_data: Dict[str, Any]) -> str:
        """Generate a roadmap summary with risk assessment."""
        epics = project_data.get('epics', [])
        
        if not epics:
            return "No epics found for this project."
        
        roadmap_parts = ["**Roadmap:**\n"]
        
        for epic in epics[:10]:  # Top 10 epics
            epic_name = epic.get('epic_name', epic.get('summary', 'Unknown'))
            status = epic.get('status', 'Unknown')
            assignee = epic.get('assignee', 'Unassigned')
            
            roadmap_parts.append(f"**{epic.get('key')}**: {epic_name}")
            roadmap_parts.append(f"  - Status: {status}")
            roadmap_parts.append(f"  - Assignee: {assignee}")
            
            # Risk assessment
            risks = []
            if assignee == 'Unassigned':
                risks.append("⚠️ Unassigned")
            if status in ['To Do', 'Backlog']:
                risks.append("⚠️ Not started")
            due_date = epic.get('due_date')
            if due_date:
                try:
                    due = datetime.fromisoformat(due_date.replace('Z', '+00:00')).date()
                    today = datetime.now().date()
                    if due < today and status not in ['Done', 'Closed']:
                        risks.append("🔴 Overdue")
                    elif (due - today).days < 7:
                        risks.append("🟡 Due soon")
                except:
                    pass
            
            if risks:
                roadmap_parts.append(f"  - Risks: {', '.join(risks)}")
            roadmap_parts.append("")
        
        return '\n'.join(roadmap_parts)

