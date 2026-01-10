"""
CV Feedback Assistant
AI-powered resume analysis with multi-LLM support
"""

import streamlit as st
from datetime import datetime
import os
import markdown
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="CV Feedback Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import custom modules
from styles import inject_custom_css, render_header, render_footer
from services.llm_service import LLMService, LLM_PROVIDERS
from services.match_scorer import MatchScorer
from services.document_parser import DocumentParser
from components.llm_selector import render_llm_selector, render_api_key_input, render_language_selector
from components.feedback_display import (
    render_match_score_gauge, render_match_details, render_download_button
)
from translations import get_text

# Inject custom CSS
inject_custom_css()


def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'cv_text': '',
        'job_description': '',
        'selected_language': 'English',
        'feedback_response': None,
        'match_score': None,
        'match_data': None,
        'analysis_provider': None,
        'analysis_model': None,
        'response_time': None,
        'last_uploaded_file': None,
        'api_key': ''
    }

    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def clear_inputs():
    """Clear all input fields"""
    st.session_state.cv_text = ''
    st.session_state.job_description = ''
    st.session_state.feedback_response = None
    st.session_state.match_score = None
    st.session_state.match_data = None
    st.session_state.last_uploaded_file = None


def render_sidebar():
    """Render sidebar with all controls"""
    st.sidebar.markdown("""
    <div style="text-align: center; margin-top: -3.5rem;">
        <h2 style="color: #06b6d4; margin: 0; font-size: 1.2rem;">CV Assistant</h2>
        <p style="color: #64748b; font-size: 0.7rem; margin: 0;">AI-Powered Analysis</p>
    </div>
    <hr style="margin: 3px 0; border-color: #374151;">
    """, unsafe_allow_html=True)

    # LLM Selection
    llm_config = render_llm_selector()

    # Language selection
    selected_language = render_language_selector()

    # API Key input
    api_key = render_api_key_input(llm_config['provider'])

    # Disclaimer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="background: rgba(245, 158, 11, 0.1); padding: 12px; border-radius: 8px; border-left: 3px solid #f59e0b; margin-bottom: 10px;">
        <p style="color: #f59e0b; font-size: 0.75rem; margin: 0;">
            <strong>Privacy:</strong> Don't include sensitive info like phone numbers or addresses.
        </p>
    </div>
    <div style="background: rgba(100, 116, 139, 0.1); padding: 12px; border-radius: 8px; border-left: 3px solid #64748b;">
        <p style="color: #94a3b8; font-size: 0.7rem; margin: 0;">
            <strong>Disclaimer:</strong> This tool is provided "as is" without warranty. We do not store, save, or retain any data you enter. Your CV and job descriptions are processed in real-time and not saved. The developer is not responsible for any decisions made based on the analysis provided.
        </p>
    </div>
    """, unsafe_allow_html=True)

    return {
        **llm_config,
        'language': selected_language,
        'api_key': api_key
    }


def render_input_section():
    """Render the CV and Job Description input section"""
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        # Section title
        st.markdown("#### 📄 Your CV / Resume")

        # File upload option in expander
        with st.expander("Upload file (PDF/DOCX)", expanded=False):
            uploaded_file = st.file_uploader(
                "Choose file",
                type=['pdf', 'docx'],
                key="cv_file_uploader",
                label_visibility="collapsed"
            )
            if uploaded_file:
                # Only process if it's a new file
                file_id = f"{uploaded_file.name}_{uploaded_file.size}"
                if st.session_state.last_uploaded_file != file_id:
                    with st.spinner("Extracting..."):
                        text, error = DocumentParser.parse_file(uploaded_file)
                        if error:
                            st.error(error)
                        elif text:
                            st.session_state.last_uploaded_file = file_id
                            st.session_state.cv_text = text
                            st.success(f"Extracted {len(text):,} chars")
                            st.rerun()
                else:
                    st.success(f"File loaded: {uploaded_file.name}")

        # Text area - use session state directly
        cv_text = st.text_area(
            "CV Content",
            value=st.session_state.cv_text,
            height=320,
            max_chars=10000,
            placeholder="Paste your CV/resume content here...\n\n• Work experience\n• Education\n• Skills\n• Achievements",
            label_visibility="collapsed"
        )
        # Update session state with any manual edits
        if cv_text != st.session_state.cv_text:
            st.session_state.cv_text = cv_text
        st.caption(f"{len(cv_text):,} / 10,000 characters")

    with col2:
        # Section title
        st.markdown("#### 💼 Target Job Description")

        # Matching expander for symmetry with CV column
        with st.expander("Tips for job description", expanded=False):
            st.markdown("Paste the complete job posting including requirements, responsibilities, and qualifications for best results.")

        # Text area
        job_description = st.text_area(
            "Job Description",
            value=st.session_state.job_description,
            height=320,
            max_chars=10000,
            placeholder="Paste the job description you're applying for...\n\n• Job title & company\n• Requirements\n• Responsibilities\n• Preferred qualifications",
            label_visibility="collapsed"
        )
        # Update session state with any manual edits
        if job_description != st.session_state.job_description:
            st.session_state.job_description = job_description
        st.caption(f"{len(job_description):,} / 10,000 characters")

    # Return from session state to ensure consistency
    return st.session_state.cv_text, st.session_state.job_description


def analyze_cv(cv_text: str, job_description: str, config: dict):
    """Perform CV analysis"""
    if not cv_text or not job_description:
        st.error("Please provide both CV and Job Description.")
        return

    if not config['api_key']:
        st.error(f"Please provide your {config['provider']} API key.")
        return

    try:
        start_time = datetime.now()

        with st.spinner(f"Analyzing with {config['provider']} ({config['model_name']})..."):
            # Calculate match score
            match_data = MatchScorer.calculate_score(cv_text, job_description)
            match_score = match_data['score']

            # Get AI feedback
            result = LLMService.analyze_cv(
                provider=config['provider'],
                api_key=config['api_key'],
                model=config['model'],
                cv_text=cv_text,
                job_description=job_description,
                language=config['language']
            )

            response_time = (datetime.now() - start_time).total_seconds()

            # Store results in session state
            st.session_state.feedback_response = result['content']
            st.session_state.match_score = match_score
            st.session_state.match_data = match_data
            st.session_state.analysis_provider = config['provider']
            st.session_state.analysis_model = config['model_name']
            st.session_state.response_time = response_time

            # Reset PDF state for new analysis
            st.session_state.pdf_ready = False
            st.session_state.pdf_data = None
            st.session_state.pdf_filename = None

            # Force rerun to display results
            st.rerun()

    except Exception as e:
        error_msg = str(e)
        st.error(f"Analysis failed: {error_msg}")


def render_results():
    """Render analysis results if available"""
    if st.session_state.feedback_response:
        st.markdown("---")

        # Get language for translations
        language = st.session_state.selected_language

        # Header with download button inline
        if st.session_state.match_score is not None:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"## {get_text('analysis_results', language)}")
            with col2:
                render_download_button(
                    feedback_content=st.session_state.feedback_response,
                    match_score=st.session_state.match_score,
                    provider=st.session_state.analysis_provider,
                    model=st.session_state.analysis_model,
                    language=language
                )
        else:
            st.markdown(f"## {get_text('analysis_results', language)}")

        # Score and details
        col1, col2 = st.columns([1, 2])

        with col1:
            if st.session_state.match_score is not None:
                render_match_score_gauge(st.session_state.match_score, language)

                st.markdown(f"""
                <div style="background: #262730; padding: 12px; border-radius: 8px; margin-top: 12px;">
                    <p style="margin: 4px 0; font-size: 12px; color: #94a3b8;">
                        <strong>{get_text('provider', language)}:</strong> {st.session_state.analysis_provider}
                    </p>
                    <p style="margin: 4px 0; font-size: 12px; color: #94a3b8;">
                        <strong>{get_text('model', language)}:</strong> {st.session_state.analysis_model}
                    </p>
                    <p style="margin: 4px 0; font-size: 12px; color: #94a3b8;">
                        <strong>{get_text('time', language)}:</strong> {st.session_state.response_time:.1f}s
                    </p>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            if st.session_state.match_data:
                render_match_details(st.session_state.match_data, language)

        # Detailed feedback
        st.markdown("---")
        st.markdown(f"### {get_text('detailed_feedback', language)}")

        # Convert markdown to HTML and wrap in styled container
        feedback_html = markdown.markdown(
            st.session_state.feedback_response,
            extensions=['tables', 'fenced_code']
        )
        st.markdown(
            f'<div class="feedback-container">{feedback_html}</div>',
            unsafe_allow_html=True
        )


def main():
    """Main application entry point"""
    initialize_session_state()
    render_header()
    config = render_sidebar()

    # Input section
    cv_text, job_description = render_input_section()

    # Action buttons - centered
    col1, col2, col3, col4 = st.columns([1.5, 1, 1, 1.5])

    with col2:
        if st.button("🔍 Analyze CV", use_container_width=True, type="primary"):
            analyze_cv(cv_text, job_description, config)

    with col3:
        if st.button("🗑️ Clear All", use_container_width=True):
            clear_inputs()
            st.rerun()

    # Results
    render_results()

    # Footer
    render_footer()


if __name__ == "__main__":
    main()
