"""
File Upload Component
Handles PDF/DOCX file uploads with preview
"""

import streamlit as st
from services.document_parser import DocumentParser


def render_file_upload(key_prefix: str = "cv") -> tuple:
    """
    Render file upload component with text extraction

    Args:
        key_prefix: Prefix for session state keys

    Returns:
        Tuple of (extracted_text, upload_method)
    """
    # Upload method selection
    upload_method = st.radio(
        "How would you like to provide your CV?",
        ["Paste Text", "Upload File"],
        horizontal=True,
        key=f"{key_prefix}_upload_method"
    )

    extracted_text = ""
    error_message = None

    if upload_method == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload your CV (PDF or DOCX)",
            type=['pdf', 'docx'],
            key=f"{key_prefix}_file_uploader",
            help="Supported formats: PDF, DOCX (max 10MB)"
        )

        if uploaded_file is not None:
            # Show file info
            file_info = DocumentParser.get_file_info(uploaded_file)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("File", file_info['name'][:20] + "..." if len(file_info['name']) > 20 else file_info['name'])
            with col2:
                st.metric("Size", f"{file_info['size_kb']} KB")
            with col3:
                st.metric("Type", file_info['type'].split('/')[-1].upper())

            # Extract text
            with st.spinner("Extracting text from file..."):
                extracted_text, error_message = DocumentParser.parse_file(uploaded_file)

            if error_message:
                st.error(f"Error: {error_message}")
                extracted_text = ""
            elif extracted_text:
                st.success(f"Successfully extracted {len(extracted_text)} characters")

                # Show preview
                with st.expander("Preview extracted text", expanded=False):
                    st.text(extracted_text[:1000] + ("..." if len(extracted_text) > 1000 else ""))

    return extracted_text, upload_method


def render_cv_input(session_key: str = "cv_text") -> str:
    """
    Render CV input section with file upload or text paste

    Args:
        session_key: Session state key for storing CV text

    Returns:
        CV text content
    """
    st.markdown("""
        <div class="input-section">
            <h3>Your CV / Resume</h3>
        </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if session_key not in st.session_state:
        st.session_state[session_key] = ""

    extracted_text, upload_method = render_file_upload("cv")

    if upload_method == "Upload File" and extracted_text:
        st.session_state[session_key] = extracted_text
        return extracted_text
    else:
        # Text input
        cv_text = st.text_area(
            "Paste your CV content here:",
            value=st.session_state.get(session_key, ""),
            height=250,
            max_chars=10000,
            key="cv_text_area",
            placeholder="Paste your CV/resume text here...\n\nInclude your:\n- Contact information\n- Work experience\n- Education\n- Skills\n- Achievements"
        )
        st.session_state[session_key] = cv_text
        return cv_text


def render_job_description_input(session_key: str = "job_description") -> str:
    """
    Render job description input section

    Args:
        session_key: Session state key for storing job description

    Returns:
        Job description text content
    """
    st.markdown("""
        <div class="input-section">
            <h3>Target Job Description</h3>
        </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if session_key not in st.session_state:
        st.session_state[session_key] = ""

    job_description = st.text_area(
        "Paste the job description here:",
        value=st.session_state.get(session_key, ""),
        height=250,
        max_chars=10000,
        key="job_desc_text_area",
        placeholder="Paste the job description you're applying for...\n\nInclude:\n- Job title and company\n- Required qualifications\n- Responsibilities\n- Preferred skills"
    )
    st.session_state[session_key] = job_description
    return job_description
