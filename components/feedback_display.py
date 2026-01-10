"""
Feedback Display Component
Renders AI feedback with match score visualization
"""

import streamlit as st
from services.match_scorer import MatchScorer
from services.pdf_generator import PDFGenerator
from translations import get_text


def render_match_score_gauge(score: float, language: str = "English") -> None:
    """
    Render match score as a visual gauge

    Args:
        score: Match score percentage (0-100)
        language: Language for labels
    """
    interpretation = MatchScorer.get_score_interpretation(score, language)

    # Create gauge visualization using HTML/CSS
    gauge_html = f"""
    <div class="score-gauge-container">
        <div class="score-gauge">
            <div class="score-circle" style="--score: {score}; --color: {interpretation['color']}">
                <span class="score-value">{score:.0f}%</span>
            </div>
        </div>
        <div class="score-label" style="color: {interpretation['color']}">
            {interpretation['label']}
        </div>
        <div class="score-description">
            {interpretation['description']}
        </div>
    </div>

    <style>
    .score-gauge-container {{
        text-align: center;
        padding: 20px;
    }}
    .score-gauge {{
        display: flex;
        justify-content: center;
        margin-bottom: 15px;
    }}
    .score-circle {{
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background: conic-gradient(
            var(--color) calc(var(--score) * 1%),
            #374151 calc(var(--score) * 1%)
        );
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }}
    .score-circle::before {{
        content: '';
        position: absolute;
        width: 110px;
        height: 110px;
        border-radius: 50%;
        background: #1a1d24;
    }}
    .score-value {{
        position: relative;
        z-index: 1;
        font-size: 32px;
        font-weight: bold;
        color: #f8fafc;
    }}
    .score-label {{
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 8px;
    }}
    .score-description {{
        font-size: 14px;
        color: #94a3b8;
    }}
    </style>
    """

    st.markdown(gauge_html, unsafe_allow_html=True)


def render_match_details(match_data: dict, language: str = "English") -> None:
    """
    Render detailed match analysis

    Args:
        match_data: Match score data from MatchScorer
        language: Language for labels
    """
    with st.expander(get_text("match_details", language), expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{get_text('matching_keywords', language)}**")
            if match_data.get('matching_keywords'):
                keywords_html = " ".join([
                    f'<span class="keyword-tag match">{kw}</span>'
                    for kw in match_data['matching_keywords'][:10]
                ])
                st.markdown(f"""
                <div class="keywords-container">
                    {keywords_html}
                </div>
                <style>
                .keywords-container {{ display: flex; flex-wrap: wrap; gap: 8px; }}
                .keyword-tag {{ padding: 4px 10px; border-radius: 15px; font-size: 12px; }}
                .keyword-tag.match {{ background: rgba(16, 185, 129, 0.2); color: #10b981; }}
                .keyword-tag.missing {{ background: rgba(239, 68, 68, 0.2); color: #ef4444; }}
                </style>
                """, unsafe_allow_html=True)
            else:
                st.info(get_text("no_keyword_matches", language))

        with col2:
            st.markdown(f"**{get_text('missing_keywords', language)}**")
            if match_data.get('missing_keywords'):
                keywords_html = " ".join([
                    f'<span class="keyword-tag missing">{kw}</span>'
                    for kw in match_data['missing_keywords'][:10]
                ])
                st.markdown(f'<div class="keywords-container">{keywords_html}</div>',
                           unsafe_allow_html=True)
            else:
                st.success(get_text("no_missing_keywords", language))

        # Skill matches
        if match_data.get('skill_matches'):
            st.markdown("---")
            st.markdown(f"**{get_text('skill_categories_matched', language)}**")
            for category, skills in match_data['skill_matches'].items():
                st.markdown(f"- **{category.title()}**: {', '.join(skills)}")

        # Missing skills
        if match_data.get('skill_missing'):
            st.markdown(f"**{get_text('skills_to_add', language)}**")
            for category, skills in match_data['skill_missing'].items():
                st.markdown(f"- **{category.title()}**: {', '.join(skills)}")


def render_feedback(
    feedback_content: str,
    match_score: float,
    match_data: dict,
    provider: str,
    model: str,
    response_time: float
) -> None:
    """
    Render complete feedback display

    Args:
        feedback_content: AI-generated feedback text
        match_score: Match score percentage
        match_data: Detailed match analysis
        provider: LLM provider used
        model: Model used
        response_time: Time taken for analysis
    """
    st.markdown("---")

    # Header
    st.markdown("""
    <div class="feedback-header">
        <h2>Analysis Results</h2>
    </div>
    """, unsafe_allow_html=True)

    # Layout: Score on left, summary on right
    col1, col2 = st.columns([1, 2])

    with col1:
        # Match Score Gauge
        render_match_score_gauge(match_score)

        # Meta info
        st.markdown(f"""
        <div class="meta-info">
            <p><strong>Provider:</strong> {provider}</p>
            <p><strong>Model:</strong> {model}</p>
            <p><strong>Time:</strong> {response_time:.1f}s</p>
        </div>
        <style>
        .meta-info {{
            background: #262730;
            padding: 15px;
            border-radius: 10px;
            margin-top: 15px;
        }}
        .meta-info p {{
            margin: 5px 0;
            font-size: 13px;
            color: #94a3b8;
        }}
        </style>
        """, unsafe_allow_html=True)

    with col2:
        # Match details
        render_match_details(match_data)

    # Detailed Feedback
    st.markdown("---")
    st.markdown("### Detailed Feedback")

    # Render markdown feedback in styled container
    st.markdown(f"""
    <div class="feedback-content">
        {feedback_content}
    </div>
    <style>
    .feedback-content {{
        background: #262730;
        padding: 25px;
        border-radius: 12px;
        border-left: 4px solid #06b6d4;
        line-height: 1.7;
    }}
    .feedback-content h1, .feedback-content h2, .feedback-content h3 {{
        color: #f8fafc;
        margin-top: 20px;
        margin-bottom: 10px;
    }}
    .feedback-content ul, .feedback-content ol {{
        padding-left: 20px;
    }}
    .feedback-content li {{
        margin-bottom: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Actually render the markdown properly
    with st.container():
        st.markdown(feedback_content)


def render_download_button(
    feedback_content: str,
    match_score: float,
    provider: str,
    model: str,
    job_title: str = "Position",
    language: str = "English"
) -> None:
    """
    Render PDF download button with two-step process to prevent auto-download

    Args:
        feedback_content: AI feedback text
        match_score: Match percentage
        provider: LLM provider
        model: Model name
        job_title: Job title for the PDF
        language: Language for labels
    """
    # Initialize PDF ready state
    if 'pdf_ready' not in st.session_state:
        st.session_state.pdf_ready = False
    if 'pdf_data' not in st.session_state:
        st.session_state.pdf_data = None
    if 'pdf_filename' not in st.session_state:
        st.session_state.pdf_filename = None

    # Two-step download: First prepare, then download
    if not st.session_state.pdf_ready:
        if st.button(f"📄 {get_text('prepare_pdf', language)}", key="prepare_pdf_btn"):
            try:
                with st.spinner("Generating PDF..."):
                    pdf_bytes = PDFGenerator.generate_feedback_pdf(
                        feedback=feedback_content,
                        match_score=match_score,
                        job_title=job_title,
                        provider=provider,
                        model=model
                    )
                    st.session_state.pdf_data = pdf_bytes
                    st.session_state.pdf_filename = PDFGenerator.get_download_filename(job_title)
                    st.session_state.pdf_ready = True
                    st.rerun()
            except Exception as e:
                st.error(f"PDF error: {str(e)}")
    else:
        # Show download button only after PDF is prepared
        st.download_button(
            label=f"📥 {get_text('download_pdf', language)}",
            data=st.session_state.pdf_data,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf",
            key="download_pdf_button"
        )
