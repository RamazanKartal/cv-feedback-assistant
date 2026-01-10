"""
LLM Selector Component
Handles LLM provider and model selection
"""

import streamlit as st
import os
from services.llm_service import LLM_PROVIDERS


def render_llm_selector() -> dict:
    """
    Render LLM provider and model selector in sidebar

    Returns:
        Dict with provider, model, and model_name
    """
    st.sidebar.markdown("### AI Provider")

    # Provider selection
    provider_options = list(LLM_PROVIDERS.keys())

    selected_provider = st.sidebar.selectbox(
        "Select Provider",
        options=provider_options,
        key="llm_provider_select",
        label_visibility="collapsed"
    )

    provider_config = LLM_PROVIDERS[selected_provider]

    # Model selection
    st.sidebar.markdown("### Model")
    model_options = list(provider_config['models'].keys())

    selected_model_name = st.sidebar.selectbox(
        "Select Model",
        options=model_options,
        key="llm_model_select",
        label_visibility="collapsed"
    )

    # Get actual model identifier
    selected_model = provider_config['models'][selected_model_name]
    st.session_state.selected_model = selected_model

    st.sidebar.markdown("---")

    return {
        "provider": selected_provider,
        "model": selected_model,
        "model_name": selected_model_name
    }


def render_api_key_input(provider: str) -> str:
    """
    Render API key input based on provider

    Args:
        provider: Selected LLM provider

    Returns:
        API key string
    """
    provider_config = LLM_PROVIDERS[provider]
    env_key = provider_config['env_key']

    # Check for environment API key (for local development)
    env_api_key = os.getenv(env_key, "")

    if env_api_key:
        st.sidebar.success(f"Using configured {provider} key")
        return env_api_key

    # User needs to provide their own key
    st.sidebar.markdown(f"### {provider} API Key")

    # Help link based on provider
    help_links = {
        "OpenAI": "https://platform.openai.com/api-keys",
        "Google Gemini": "https://aistudio.google.com/app/apikey",
        "Anthropic Claude": "https://console.anthropic.com/settings/keys"
    }

    st.sidebar.markdown(f"[Get your API key]({help_links[provider]})")

    api_key = st.sidebar.text_input(
        f"Enter your {provider} API key:",
        type="password",
        key=f"{provider}_api_key_input",
        help="Your API key is only used for this session"
    )

    if not api_key:
        st.sidebar.warning(f"Please enter your {provider} API key to continue.")

    return api_key


def render_language_selector() -> str:
    """
    Render language selector for feedback

    Returns:
        Selected language string
    """
    # Keep sidebar labels in English always
    st.sidebar.markdown("### Feedback Language")

    languages = [
        "English",
        "Turkish",
        "German",
        "French",
        "Spanish",
        "Arabic",
        "Russian",
        "Chinese",
        "Hindi",
    ]

    selected_language = st.sidebar.selectbox(
        "Select Language",
        options=languages,
        key="language_select",
        label_visibility="collapsed"
    )

    # Update session state
    st.session_state.selected_language = selected_language

    st.sidebar.markdown("---")

    return selected_language
