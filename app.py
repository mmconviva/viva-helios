"""
Helios0.1 Chat Webapp - Streamlit UI
"""
import streamlit as st
import os

from helios_chat import HeliosChat
from jira_client import JiraClient
from google_docs_reader import GoogleDocsReader
from llm_service import LLMService
from config import load_config
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any


# Page configuration
st.set_page_config(
    page_title="Helios0.1 Chat",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'helios_chat' not in st.session_state:
    st.session_state.helios_chat = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'current_context' not in st.session_state:
    st.session_state.current_context = None


def initialize_helios():
    """Initialize Helios chat engine."""
    if st.session_state.helios_chat is None:
        try:
            config = load_config()
            
            # Initialize Jira client
            jira_config = config.get('jira', {})
            base_url = jira_config.get('base_url', '')
            email = jira_config.get('email', '')
            api_token = jira_config.get('api_token', '')
            
            # Check for placeholder values
            if 'your-domain' in base_url or 'your-email' in email or 'your-api-token' in api_token:
                st.error("⚠️ **Jira credentials contain placeholder values!**\n\n"
                        "Please update your `.env` file with actual values:\n"
                        "- Replace `https://your-domain.atlassian.net` with your actual Jira URL\n"
                        "- Replace `your-email@example.com` with your actual email\n"
                        "- Replace `your-api-token-here` with your actual API token\n\n"
                        "The `.env` file is in the Helios0.1 directory.")
                return None
            
            if not all([base_url, email, api_token]):
                st.error("Jira configuration incomplete. Please set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN in your `.env` file.")
                return None
            
            jira_client = JiraClient(
                base_url=jira_config['base_url'],
                email=jira_config['email'],
                api_token=jira_config['api_token']
            )
            
            # Initialize Google Docs reader
            drive_config = config.get('google_drive', {})
            docs_reader = GoogleDocsReader(
                credentials_file=drive_config.get('credentials_file', 'credentials.json'),
                token_file=drive_config.get('token_file', 'token.pickle')
            )
            
            # Initialize LLM service with Gemini 2.0
            llm_config = config.get('llm', {})
            if not llm_config:
                st.warning("LLM not configured. Some features may be limited. Set GEMINI_API_KEY for Gemini 2.0.")
                llm_service = None
            else:
                # Use Gemini 2.0 (gemini-2.0-flash) as default
                llm_service = LLMService(
                    provider=llm_config.get('provider', 'gemini'),
                    api_key=llm_config.get('api_key'),
                    model=llm_config.get('model', 'gemini-2.0-flash')  # Gemini 2.0
                )
                st.success(f"✅ Using {llm_service.model} (Gemini 2.0) for AI-powered responses and summarization")
            
            if llm_service is None:
                # Create a dummy LLM service that returns basic responses
                class DummyLLM:
                    def __init__(self):
                        self.provider = "dummy"
                        self.model = "dummy"
                        self.client = None
                
                llm_service = DummyLLM()
                st.warning("LLM not configured. Responses will be basic summaries without AI enhancement.")
            
            st.session_state.helios_chat = HeliosChat(jira_client, docs_reader, llm_service)
            return True
        except Exception as e:
            st.error(f"Failed to initialize Helios: {str(e)}")
            return False
    return True


def create_charts(charts_data: Dict[str, Any]):
    """Create visualization charts."""
    if not charts_data:
        return
    
    # Chart 1: Issues by Type
    if 'by_type' in charts_data:
        st.subheader("📊 Issues by Type")
        type_data = charts_data['by_type']
        fig = px.pie(
            values=list(type_data.values()),
            names=list(type_data.keys()),
            title="Total Epics, Stories, and Tasks"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Chart 2: Issues by Status
    if 'by_status' in charts_data:
        st.subheader("📈 Issues by Status")
        status_data = charts_data['by_status']
        if status_data:
            fig = px.bar(
                x=list(status_data.keys()),
                y=list(status_data.values()),
                title="Issue Count by Status",
                labels={'x': 'Status', 'y': 'Count'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Chart 3: Issues by Assignee
    if 'by_assignee' in charts_data:
        st.subheader("👥 Issues by Assignee")
        assignee_data = charts_data['by_assignee']
        if assignee_data:
            # Limit to top 10 assignees
            sorted_assignees = sorted(assignee_data.items(), key=lambda x: x[1], reverse=True)[:10]
            fig = px.bar(
                x=[a[0] for a in sorted_assignees],
                y=[a[1] for a in sorted_assignees],
                title="Issue Count by Assignee (Top 10)",
                labels={'x': 'Assignee', 'y': 'Count'}
            )
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Chart 4: Issues by Assignee and Status (Heatmap)
    if 'by_assignee_and_status' in charts_data:
        st.subheader("🔥 Issues by Assignee and Status")
        assignee_status_data = charts_data['by_assignee_and_status']
        if assignee_status_data:
            # Prepare data for heatmap
            assignees = []
            statuses = []
            counts = []
            
            for assignee, status_dict in assignee_status_data.items():
                for status, count in status_dict.items():
                    assignees.append(assignee)
                    statuses.append(status)
                    counts.append(count)
            
            if assignees:
                df = pd.DataFrame({
                    'Assignee': assignees,
                    'Status': statuses,
                    'Count': counts
                })
                
                # Create pivot table
                pivot = df.pivot_table(values='Count', index='Assignee', columns='Status', fill_value=0)
                
                # Limit to top 10 assignees
                if len(pivot) > 10:
                    pivot = pivot.head(10)
                
                fig = px.imshow(
                    pivot.values,
                    labels=dict(x="Status", y="Assignee", color="Count"),
                    x=pivot.columns,
                    y=pivot.index,
                    title="Issue Distribution: Assignee vs Status",
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)


def main():
    """Main application."""
    st.title("🚀 Helios0.1 Chat")
    st.markdown("**Your AI-powered project management assistant integrating Jira and Google Docs**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        if st.button("Initialize Helios", type="primary"):
            # Clear any existing session state to force fresh initialization
            st.session_state.helios_chat = None
            st.session_state.current_context = None
            st.session_state.conversation_history = []  # Clear conversation too
            with st.spinner("Initializing..."):
                if initialize_helios():
                    st.success("✅ Helios initialized successfully!")
                    st.rerun()  # Rerun to refresh the app
                else:
                    st.error("Initialization failed. Check your configuration.")
        
        # Add a button to clear session state if needed
        if st.session_state.helios_chat is not None:
            if st.button("🔄 Clear All & Re-initialize"):
                st.session_state.helios_chat = None
                st.session_state.current_context = None
                st.session_state.conversation_history = []
                st.success("✅ Session cleared! Click 'Initialize Helios' to restart.")
                st.rerun()
        
        # Debug: Show current state
        if st.session_state.helios_chat is not None:
            with st.expander("🔍 Debug: Current State", expanded=False):
                st.write("**Helios Chat:**", "Initialized ✅" if st.session_state.helios_chat else "Not initialized ❌")
                if st.session_state.current_context:
                    jira_data = st.session_state.current_context.get('jira_data', {})
                    st.write(f"**Last Project:** {st.session_state.current_context.get('project_key', 'N/A')}")
                    st.write(f"**Last Total Issues:** {jira_data.get('total_issues', 0) if jira_data else 0}")
        
        st.markdown("---")
        st.markdown("### 📝 Instructions")
        st.markdown("""
        1. Click "Initialize Helios" to start
        2. Ask questions about your Jira projects
        3. Helios will:
           - Fetch project data from Jira
           - Find relevant meeting notes in Google Drive
           - Generate summaries and roadmaps
           - Show progress charts
        """)
        
        if st.session_state.current_context:
            st.markdown("---")
            st.markdown("### 📊 Current Project")
            st.info(f"**{st.session_state.current_context.get('project_key', 'N/A')}**")
    
    # Main content
    if st.session_state.helios_chat is None:
        st.info("👆 Please initialize Helios from the sidebar to begin.")
        return
    
    # Chat interface
    st.header("💬 Chat with Helios")
    
    # Display conversation history
    for i, conv in enumerate(st.session_state.conversation_history):
        with st.chat_message("user"):
            st.write(conv['query'])
        
        with st.chat_message("assistant"):
            st.write(conv['response'])
    
    # Chat input
    user_query = st.chat_input("Ask about a project (e.g., 'What is the status of Project ABC?')")
    
    if user_query:
        # Add user message to history
        st.session_state.conversation_history.append({
            'query': user_query,
            'response': 'Processing...'
        })
        
        with st.spinner("🔍 Analyzing project and fetching data..."):
            try:
                result = st.session_state.helios_chat.process_query(user_query)
                
                # Debug: Check what we got
                jira_data = result.get('jira_data', {})
                total_issues = jira_data.get('total_issues', 0) if jira_data else 0
                
                if 'error' in result:
                    response_text = result.get('response', result.get('error', 'An error occurred.'))
                else:
                    response_text = result.get('response', 'No response generated.')
                    st.session_state.current_context = result
                    
                    # Debug warning if we got 0 issues but shouldn't have
                    if total_issues == 0 and result.get('project_key'):
                        st.warning(f"⚠️ Debug: Got 0 issues for project {result.get('project_key')}. This might indicate a data fetching issue.")
                        # Show debug info
                        with st.expander("🐛 Debug Info", expanded=True):
                            st.write("**Raw Result Data:**")
                            st.json({
                                'project_key': result.get('project_key'),
                                'jira_data_keys': list(jira_data.keys()) if jira_data else [],
                                'total_issues': total_issues,
                                'epics_count': len(jira_data.get('epics', [])) if jira_data else 0,
                                'stories_count': len(jira_data.get('stories', [])) if jira_data else 0,
                                'tasks_count': len(jira_data.get('tasks', [])) if jira_data else 0,
                            })
                
                # Update conversation history
                st.session_state.conversation_history[-1]['response'] = response_text
                
                # Rerun to show the response
                st.rerun()
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                error_msg = f"Error: {str(e)}"
                st.session_state.conversation_history[-1]['response'] = error_msg
                st.error(error_msg)
                with st.expander("🐛 Error Details", expanded=False):
                    st.code(error_details)
                st.rerun()
    
    # Display current project information
    if st.session_state.current_context and 'error' not in st.session_state.current_context:
        st.markdown("---")
        st.header("📋 Project Summary")
        
        context = st.session_state.current_context
        
        # Status Summary
        if context.get('status_summary'):
            with st.expander("📊 Status Summary", expanded=True):
                st.markdown(context['status_summary'])
        
        # Debug: Show raw data if counts are 0
        jira_data = context.get('jira_data', {})
        if jira_data and jira_data.get('total_issues', 0) == 0:
            with st.expander("🐛 Debug Info", expanded=True):
                st.write("**Raw Jira Data:**")
                st.json({
                    'total_issues': jira_data.get('total_issues'),
                    'epics_count': len(jira_data.get('epics', [])),
                    'stories_count': len(jira_data.get('stories', [])),
                    'tasks_count': len(jira_data.get('tasks', [])),
                    'metrics': jira_data.get('metrics', {})
                })
                st.warning("⚠️ If you see 0 issues here, there may be a data fetching issue. Try re-initializing Helios.")
        
        # Roadmap
        if context.get('roadmap'):
            with st.expander("🗺️ Roadmap with Risk Assessment", expanded=True):
                st.markdown(context['roadmap'])
        
        # Meeting Notes
        if context.get('meeting_notes'):
            with st.expander("📝 Relevant Meeting Notes", expanded=False):
                for note in context['meeting_notes'][:5]:
                    st.markdown(f"**{note.get('name')}**")
                    st.markdown(f"*Last modified: {note.get('modified_time', 'Unknown')}*")
                    st.markdown(note.get('content', '')[:500] + "...")
                    st.markdown("---")
        
        # Charts
        if context.get('charts_data'):
            st.markdown("---")
            st.header("📈 Progress Charts")
            create_charts(context['charts_data'])
        
        # Follow-up questions
        st.markdown("---")
        st.header("💭 Ask a Follow-up Question")
        followup_query = st.text_input("Ask more about this project:")
        
        if followup_query:
            with st.spinner("Thinking..."):
                try:
                    followup_answer = st.session_state.helios_chat.answer_followup(
                        followup_query,
                        context
                    )
                    st.session_state.conversation_history.append({
                        'query': followup_query,
                        'response': followup_answer
                    })
                    st.info(followup_answer)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing follow-up: {str(e)}")


if __name__ == "__main__":
    main()

