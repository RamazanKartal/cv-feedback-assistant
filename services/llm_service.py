"""
Multi-LLM Service Layer
Provides unified interface for OpenAI, Google Gemini, and Anthropic Claude
"""

from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, Optional

# LLM Provider configurations
LLM_PROVIDERS = {
    "OpenAI": {
        "models": {
            "GPT-5 Mini": "gpt-5-mini",
            "GPT-5 Nano": "gpt-5-nano"
        },
        "env_key": "OPENAI_API_KEY",
        "icon": "https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg"
    },
    "Google Gemini": {
        "models": {
            "Gemini 3 Flash": "gemini-3-flash-preview",
            "Gemini 2.5 Flash": "gemini-2.5-flash"
        },
        "env_key": "GOOGLE_API_KEY",
        "icon": "https://www.gstatic.com/lamda/images/gemini_sparkle_v002_d4735304ff6292a690345.svg"
    },
    "Anthropic Claude": {
        "models": {
            "Claude 4 Sonnet": "claude-sonnet-4-20250514",
            "Claude 3.5 Sonnet": "claude-3-5-sonnet-20241022",
            "Claude 3.5 Haiku": "claude-3-5-haiku-20241022"
        },
        "env_key": "ANTHROPIC_API_KEY",
        "icon": "https://www.anthropic.com/images/icons/apple-touch-icon.png"
    }
}

def get_prompt_template() -> str:
    """Define the CV analysis prompt template."""
    return """You are an expert career coach. Analyze this CV against the job description.

**CV:**
{cv_text}

**JOB DESCRIPTION:**
{job_description_text}

**CRITICAL: Write your ENTIRE response in {language}. Translate ALL section headers below to {language}.**

Use this exact markdown structure (but translate the headers):

## Quick Verdict
2-3 sentences: Is this candidate competitive? Biggest strength and gap?

## Skills Match
| Skill | Status |
|-------|--------|
| skill1 | Yes/Partial/No |
| skill2 | Yes/Partial/No |
| skill3 | Yes/Partial/No |
| skill4 | Yes/Partial/No |
| skill5 | Yes/Partial/No |

## Missing Keywords
- keyword1
- keyword2
- keyword3

## Top 3 Improvements
1. **Improvement 1** - specific suggestion
2. **Improvement 2** - specific suggestion
3. **Improvement 3** - specific suggestion

## Red Flags
- Any concerns a recruiter might have

IMPORTANT: If {language} is not English, translate these headers:
- "Quick Verdict" → translate to {language}
- "Skills Match" → translate to {language}
- "Missing Keywords" → translate to {language}
- "Top 3 Improvements" → translate to {language}
- "Red Flags" → translate to {language}
- Table headers "Skill" and "Status" → translate to {language}
- "Yes/Partial/No" → translate to {language}

Be specific - reference actual content from the CV and job description. No generic advice.
"""


class LLMService:
    """Service for handling multi-LLM operations"""

    @staticmethod
    def get_llm(provider: str, api_key: str, model: str, max_tokens: int = 16000, temperature: float = 0.5):
        """
        Get LLM instance based on provider

        Args:
            provider: One of "OpenAI", "Google Gemini", "Anthropic Claude"
            api_key: API key for the provider
            model: Model identifier
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation

        Returns:
            LangChain LLM instance
        """
        if provider == "OpenAI":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=api_key,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
        elif provider == "Google Gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model=model,
                max_output_tokens=max_tokens,
                temperature=temperature
            )
        elif provider == "Anthropic Claude":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                api_key=api_key,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    @staticmethod
    def create_chain(provider: str, api_key: str, model: str):
        """
        Create a LangChain chain for CV analysis

        Args:
            provider: LLM provider name
            api_key: API key
            model: Model identifier

        Returns:
            LangChain chain ready for invocation
        """
        llm = LLMService.get_llm(provider, api_key, model)
        prompt = ChatPromptTemplate.from_template(get_prompt_template())
        return prompt | llm

    @staticmethod
    def analyze_cv(
        provider: str,
        api_key: str,
        model: str,
        cv_text: str,
        job_description: str,
        language: str = "English"
    ) -> Dict[str, Any]:
        """
        Analyze CV against job description

        Args:
            provider: LLM provider name
            api_key: API key
            model: Model identifier
            cv_text: CV content
            job_description: Job description content
            language: Response language

        Returns:
            Dict with 'content' (response text) and 'model' used
        """
        chain = LLMService.create_chain(provider, api_key, model)
        response = chain.invoke({
            "cv_text": cv_text,
            "job_description_text": job_description,
            "language": language
        })

        content = response.content if hasattr(response, 'content') else str(response)

        return {
            "content": content,
            "model": model,
            "provider": provider
        }
