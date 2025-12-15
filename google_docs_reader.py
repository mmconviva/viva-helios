"""
Google Docs Reader - Extracts text content from Google Docs files.
"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from typing import Dict, List, Optional
import os
import pickle


class GoogleDocsReader:
    """Reader for extracting text from Google Docs files."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/documents.readonly'
    ]
    
    def __init__(self, credentials_file: str = 'credentials.json', 
                 token_file: str = 'token.pickle'):
        """
        Initialize Google Docs reader.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store/load authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.drive_service = None
        self.docs_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate and build the Drive and Docs services."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_file}\n"
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.docs_service = build('docs', 'v1', credentials=creds)
    
    def read_document(self, file_id: str) -> str:
        """
        Read text content from a Google Doc.
        
        Args:
            file_id: Google Drive file ID of the document
        
        Returns:
            Extracted text content
        """
        try:
            doc = self.docs_service.documents().get(documentId=file_id).execute()
            content = doc.get('body', {}).get('content', [])
            text_parts = []
            
            def extract_text(element):
                """Recursively extract text from document elements."""
                if 'paragraph' in element:
                    para = element['paragraph']
                    for elem in para.get('elements', []):
                        if 'textRun' in elem:
                            text_parts.append(elem['textRun'].get('content', ''))
                elif 'table' in element:
                    table = element['table']
                    for row in table.get('tableRows', []):
                        for cell in row.get('tableCells', []):
                            for content_elem in cell.get('content', []):
                                extract_text(content_elem)
            
            for element in content:
                extract_text(element)
            
            return ''.join(text_parts)
        except Exception as e:
            raise Exception(f"Failed to read document {file_id}: {str(e)}")
    
    def search_documents(self, query: str, mime_type: str = 'application/vnd.google-apps.document') -> List[Dict]:
        """
        Search for Google Docs files.
        
        Args:
            query: Search query
            mime_type: MIME type filter (default: Google Docs)
        
        Returns:
            List of matching documents
        """
        try:
            search_query = f"name contains '{query}' and mimeType='{mime_type}'"
            results = self.drive_service.files().list(
                q=search_query,
                pageSize=50,
                fields="files(id, name, mimeType, createdTime, modifiedTime, owners)"
            ).execute()
            return results.get('files', [])
        except Exception as e:
            raise Exception(f"Failed to search documents: {str(e)}")
    
    def find_meeting_notes(self, project_name: str) -> List[Dict]:
        """
        Find meeting notes related to a project.
        
        Args:
            project_name: Name of the project to search for
        
        Returns:
            List of meeting note documents with content
        """
        search_terms = [
            f"{project_name} meeting",
            f"{project_name} summary",
            f"{project_name} notes",
            "meeting notes",
            "meeting summary"
        ]
        
        all_docs = {}
        for term in search_terms:
            try:
                docs = self.search_documents(term)
                for doc in docs:
                    doc_id = doc.get('id')
                    if doc_id and doc_id not in all_docs:
                        all_docs[doc_id] = doc
            except Exception as e:
                continue
        
        # Read content for each document and check if it mentions the project
        meeting_notes = []
        for doc_id, doc in list(all_docs.items())[:20]:  # Limit to 20 docs
            try:
                content = self.read_document(doc_id)
                # Check if project name is mentioned in the content
                if project_name.lower() in content.lower():
                    meeting_notes.append({
                        'id': doc_id,
                        'name': doc.get('name'),
                        'content': content,
                        'modified_time': doc.get('modifiedTime')
                    })
            except Exception as e:
                continue
        
        return meeting_notes

