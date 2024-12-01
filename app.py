import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import sqlite3
import hashlib
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def get_client_ip():
    """Get client IP and return hashed value."""
    try:
        # Try to get the real IP from Streamlit's internal state
        ip = st.get_client_ip()
    except:
        ip = "127.0.0.1"  # Fallback to localhost if can't get real IP
    
    try:
        # Hash the IP
        hashed_ip = hashlib.sha256(ip.encode()).hexdigest()
        
        conn = sqlite3.connect('user_tracking.db')
        c = conn.cursor()
        
        # First ensure user exists in user_usage with proper initialization
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('''INSERT OR IGNORE INTO user_usage 
                     (ip_hash, last_used, usage_count, created_at) 
                     VALUES (?, ?, 0, ?)''', 
                 (hashed_ip, current_time, current_time))
        
        # Then update ip_mapping
        c.execute('INSERT OR REPLACE INTO ip_mapping (ip_hash, original_ip) VALUES (?, ?)', 
                 (hashed_ip, ip))
        
        conn.commit()
        return hashed_ip
    except sqlite3.Error as e:
        print(f"Error in get_client_ip: {e}")
        # Return a fallback hash in case of error
        return hashlib.sha256("127.0.0.1".encode()).hexdigest()
    finally:
        if 'conn' in locals():
            conn.close()

def init_db():
    """Initialize SQLite database with enhanced tracking."""
    try:
        conn = sqlite3.connect('user_tracking.db')
        c = conn.cursor()
        
        # Create tables only if they don't exist (remove the DROP TABLE statements)
        c.execute('''CREATE TABLE IF NOT EXISTS user_usage
                     (ip_hash TEXT PRIMARY KEY,
                      last_used TIMESTAMP,
                      usage_count INTEGER DEFAULT 0,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      last_api_key_used TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS ip_mapping
                     (ip_hash TEXT PRIMARY KEY,
                      original_ip TEXT,
                      FOREIGN KEY (ip_hash) REFERENCES user_usage(ip_hash))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS usage_history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      ip_hash TEXT,
                      timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      selected_language TEXT,
                      cv_length INTEGER,
                      job_desc_length INTEGER,
                      success BOOLEAN,
                      error_message TEXT,
                      response_time FLOAT,
                      FOREIGN KEY (ip_hash) REFERENCES user_usage(ip_hash))''')
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def get_user_usage(ip_hash):
    """Get current user usage from database."""
    try:
        conn = sqlite3.connect('user_tracking.db')
        c = conn.cursor()
        
        # Get current usage count
        c.execute('SELECT usage_count FROM user_usage WHERE ip_hash = ?', (ip_hash,))
        result = c.fetchone()
        return result[0] if result else 0
    except sqlite3.Error as e:
        print(f"Error getting user usage: {e}")
        return 0
    finally:
        if 'conn' in locals():
            conn.close()

def initialize_user(ip_hash):
    """Initialize or get user record."""
    try:
        conn = sqlite3.connect('user_tracking.db')
        c = conn.cursor()
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert if not exists
        c.execute('''INSERT OR IGNORE INTO user_usage 
                     (ip_hash, last_used, usage_count, created_at) 
                     VALUES (?, ?, 0, ?)''', 
                 (ip_hash, current_time, current_time))
        conn.commit()
        
        # Get current usage count
        c.execute('SELECT usage_count FROM user_usage WHERE ip_hash = ?', (ip_hash,))
        result = c.fetchone()
        
        return result[0] if result else 0
    except sqlite3.Error as e:
        print(f"Error initializing user: {e}")
        return 0
    finally:
        if 'conn' in locals():
            conn.close()

# Initialize database at startup
init_db()

# Initialize session state variables if they don't exist
if 'free_uses_remaining' not in st.session_state:
    try:
        # Get the client's IP hash
        ip_hash = get_client_ip()
        
        # Get current usage from database
        used_count = get_user_usage(ip_hash)
        
        # Calculate remaining uses
        st.session_state.free_uses_remaining = max(5 - used_count, 0)
        
    except Exception as e:
        print(f"Error initializing session state: {e}")
        st.session_state.free_uses_remaining = 0  # Default to 0 if there's an error

if 'cv_text' not in st.session_state:
    st.session_state.cv_text = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "English"
if 'feedback_response' not in st.session_state:
    st.session_state.feedback_response = None

def check_user_limit(ip_hash):
    """Check if user has reached their free usage limit."""
    try:
        used_count = initialize_user(ip_hash)
        remaining = max(5 - used_count, 0)
        # Update session state to match database
        st.session_state.free_uses_remaining = remaining
        return used_count < 5
    except Exception as e:
        print(f"Error checking user limit: {e}")
        return False  # Restrict usage in case of error

def update_usage(ip_hash, api_key=None):
    """Update user usage with enhanced tracking."""
    try:
        conn = sqlite3.connect('user_tracking.db')
        c = conn.cursor()
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # First, ensure the user exists in user_usage with proper initialization
        c.execute('''INSERT OR IGNORE INTO user_usage 
                     (ip_hash, last_used, usage_count, created_at) 
                     VALUES (?, ?, 0, ?)''', 
                 (ip_hash, current_time, current_time))
        
        # Then update the usage count and last used time
        c.execute('''UPDATE user_usage 
                     SET usage_count = usage_count + 1,
                         last_used = ?,
                         last_api_key_used = ?
                     WHERE ip_hash = ?''',
                 (current_time, api_key, ip_hash))
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating usage: {e}")
        st.error("Failed to update usage tracking. Please try again.")
    finally:
        if 'conn' in locals():
            conn.close()

def log_usage_attempt(ip_hash, selected_language, cv_text, job_description, success=True, error_message=None, response_time=0):
    """Log detailed information about each usage attempt."""
    conn = sqlite3.connect('user_tracking.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO usage_history 
                 (ip_hash, selected_language, cv_length, job_desc_length, 
                  success, error_message, response_time)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
             (ip_hash, 
              selected_language,
              len(cv_text),
              len(job_description),
              success,
              error_message,
              response_time))
    
    conn.commit()
    conn.close()

def get_prompt_template():
    """Define the prompt template."""
    return """
You are an HR expert reviewing CVs for job applications. 
Your goal is to analyze and provide constructive feedback to improve the CV based on the given job description.

Below are the inputs:

1. Candidate's CV: {cv_text}
2. Job Description: {job_description_text}

Instructions:
- Analyze the CV against the job description requirements (skills, experience, qualifications).
- Identify gaps or mismatches in the CV and suggest concrete improvements (e.g., rephrasing accomplishments, adding missing skills, emphasizing relevant experience).
- Recommend formatting and structure improvements to make the CV more professional, concise, and tailored to the job.

Constraints:
- Stick strictly to the CV and job description; avoid discussing politics, religion, or other sensitive topics.
- Be professional, constructive, and actionable in your advice.
- Provide specific examples to help the candidate implement your suggestions.
- Conclude with:
  - A summary of the top 3-5 areas for improvement.
  - A professional opinion on how well the candidate's profile aligns with the job requirements.
  - Practical steps to enhance their chances of success.

Additional Guidelines:
- Use clear, concise language.
- Limit your feedback to 4000 tokens. Be structured and prioritize key points.
- If either the CV or job description is missing or incomplete, politely ask the user to provide both.
- If the user entered nonsense or not enough information, politely ask them to provide more information but do not write a lot of text.

Feedback should be written in: {language}.

    """

def clear_inputs():
    """Clear all input fields and reset language selection."""
    st.session_state.cv_text = ""
    st.session_state.job_description = ""
    st.session_state.selected_language = "English"
    st.session_state.feedback_response = None

def main():
    st.title("CV Feedback Assistant")
    
    # Sidebar disclaimer and instructions
    st.sidebar.markdown(
        '<p style="color:orange;">**Please Note:** Do not include sensitive or private information in your CV or Job Description. '
        'This application provides feedback based on the information you input, so avoid sharing personal '
        'data like phone numbers, addresses, or other private information.</p><br><br>', 
        unsafe_allow_html=True
    )
    
    st.sidebar.title("How To Get Your OpenAI API Key")
    
    # Add a link to instructions for obtaining an OpenAI API key with a thumbnail image
    st.sidebar.markdown(
        '[![How to get your OpenAI API key](https://img.youtube.com/vi/hSVTPU-FVLI/0.jpg)](https://www.youtube.com/watch?v=hSVTPU-FVLI)',
        unsafe_allow_html=True
    )
    
    # Language selection
    languages = [
        "English", "Turkish", "Arabic", "Chinese", "French", "German", "Hindi", "Italian",  
        "Japanese", "Korean", "Portuguese", "Russian", "Spanish" 
    ]
    selected_language = st.selectbox(
        "Select feedback language:", 
        languages, 
        index=languages.index(st.session_state.selected_language),
        key="language_selector"
    )
    st.session_state.selected_language = selected_language
    
    # OpenAI API key input (if needed)
    ip_hash = get_client_ip()
    user_has_free_uses = check_user_limit(ip_hash)
    
    if not user_has_free_uses:
        api_key = st.text_input("Enter your OpenAI API key:", type="password")
        if not api_key:
            st.warning("Please enter your OpenAI API key to continue using the service.")
            return
    else:
        api_key = os.getenv("OPENAI_API_KEY")
    
    # Input fields with session state and character limits
    cv_text = st.text_area(
        "Enter your CV (max 8000 characters):", 
        value=st.session_state.cv_text,
        height=200,
        key="cv_input",
        max_chars=8000
    )
    st.session_state.cv_text = cv_text
    
    job_description = st.text_area(
        "Enter the Job Description (max 8000 characters):", 
        value=st.session_state.job_description,
        height=200,
        key="jd_input",
        max_chars=8000
    )
    st.session_state.job_description = job_description
    
    col1, col2 = st.columns(2)
    
    feedback_container = st.container()  # Create container for feedback outside columns
    
    with col1:
        if st.button("Get Feedback"):
            if not cv_text or not job_description:
                st.error("Please provide both CV and Job Description.")
                return
                
            try:
                start_time = datetime.now()
                # Show processing message
                with st.spinner('Analyzing your CV and generating feedback...'):
                    # Initialize LangChain components
                    llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini", max_tokens=4000, temperature=0.6)
                    prompt = ChatPromptTemplate.from_template(get_prompt_template())
                    
                    # Create the chain
                    chain = prompt | llm
                    
                    # Get response
                    response = chain.invoke({
                        "cv_text": cv_text,
                        "job_description_text": job_description,
                        "language": selected_language
                    })
                    
                    response_time = (datetime.now() - start_time).total_seconds()
                    
                    # Update usage tracking
                    if user_has_free_uses:
                        update_usage(ip_hash, api_key)
                        st.session_state.free_uses_remaining -= 1
                    
                    # Log successful attempt
                    log_usage_attempt(
                        ip_hash=ip_hash,
                        selected_language=selected_language,
                        cv_text=cv_text,
                        job_description=job_description,
                        success=True,
                        response_time=response_time
                    )
                    
                    # Store response in session state for display
                    st.session_state.feedback_response = response.content
                
            except Exception as e:
                error_msg = str(e)
                st.error(f"An error occurred: {error_msg}")
                
                # Log failed attempt
                log_usage_attempt(
                    ip_hash=ip_hash,
                    selected_language=selected_language,
                    cv_text=cv_text,
                    job_description=job_description,
                    success=False,
                    error_message=error_msg,
                    response_time=0
                )
    
    with col2:
        if st.button("Clear"):
            clear_inputs()
            st.rerun()
    
    # Display remaining free uses
    if user_has_free_uses:
        st.info(f"You have {st.session_state.free_uses_remaining} free uses remaining.")
    
    # Display feedback outside of columns if it exists
    if 'feedback_response' in st.session_state and st.session_state.feedback_response:
        st.markdown("---")  # Add a separator
        with feedback_container:
            with st.expander("Detailed Feedback Analysis", expanded=True):
                st.markdown("""
                    <style>
                        .stExpander {
                            border-left: 1px solid #ccc;
                            border-right: 1px solid #ccc;
                            border-radius: 5px;
                            padding: 10px;
                            margin: 10px 0;
                        }
                    </style>
                    """, unsafe_allow_html=True)
                st.markdown(st.session_state.feedback_response)

if __name__ == "__main__":
    main() 