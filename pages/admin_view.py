import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

st.set_page_config(page_title="User Tracking - Admin View")

# Add password protection
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        if st.session_state["password"] == admin_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "Password", type="password", key="password",
            on_change=password_entered)
        return False
    
    return st.session_state["password_correct"]

def get_user_data():
    """Retrieve enhanced user tracking data from SQLite database."""
    try:
        conn = sqlite3.connect('user_tracking.db')
        
        # First check if tables exist and have proper structure
        c = conn.cursor()
        table_check = c.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name='user_usage'
        """).fetchone()[0]
        
        if not table_check:
            st.error("user_usage table does not exist")
            return pd.DataFrame()
            
        # Check for required columns
        columns = [row[1] for row in c.execute('PRAGMA table_info(user_usage)').fetchall()]
        required_columns = ['ip_hash', 'last_used', 'usage_count', 'created_at']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            st.error(f"Missing columns in user_usage table: {', '.join(missing_columns)}")
            return pd.DataFrame()
        
        # Modified query to show all records properly
        query = """
        WITH UserStats AS (
            SELECT 
                h.ip_hash,
                COUNT(*) as attempt_count,
                ROUND(AVG(CASE WHEN h.success = 1 THEN 1 ELSE 0 END) * 100, 2) as success_rate,
                ROUND(AVG(h.response_time), 2) as avg_response_time,
                GROUP_CONCAT(DISTINCT h.selected_language) as languages_used
            FROM usage_history h
            GROUP BY h.ip_hash
        )
        SELECT 
            u.ip_hash as 'User ID',
            m.original_ip as 'IP Address',
            datetime(u.created_at) as 'First Used',
            datetime(u.last_used) as 'Last Used',
            u.usage_count as 'Usage Count',
            CASE 
                WHEN u.usage_count >= 5 THEN 'Exceeded'
                ELSE 'Active'
            END as 'Status',
            COALESCE(s.attempt_count, 0) as 'Total Attempts',
            COALESCE(s.success_rate, 0) as 'Success Rate',
            COALESCE(s.avg_response_time, 0) as 'Avg Response Time (s)',
            COALESCE(s.languages_used, '') as 'Languages Used'
        FROM user_usage u
        LEFT JOIN ip_mapping m ON u.ip_hash = m.ip_hash
        LEFT JOIN UserStats s ON u.ip_hash = s.ip_hash
        ORDER BY u.last_used DESC, u.created_at DESC
        """
        
        df = pd.read_sql_query(query, conn)
        return df
        
    except sqlite3.Error as e:
        st.error(f"SQLite error in get_user_data: {str(e)}")
        if "no such table" in str(e):
            st.error("Database tables are not properly initialized")
        elif "no such column" in str(e):
            st.error("Database schema mismatch. Please check if the database is up to date")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error in get_user_data: {str(e)}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()

def get_usage_history():
    """Retrieve detailed usage history."""
    try:
        conn = sqlite3.connect('user_tracking.db')
        query = """
        SELECT 
            datetime(h.timestamp) as 'Timestamp',
            m.original_ip as 'IP Address',
            h.selected_language as 'Language',
            h.cv_length as 'CV Length',
            h.job_desc_length as 'Job Desc Length',
            h.success as 'Success',
            h.error_message as 'Error Message',
            h.response_time as 'Response Time (s)'
        FROM usage_history h
        LEFT JOIN ip_mapping m ON h.ip_hash = m.ip_hash
        ORDER BY datetime(h.timestamp) DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    except sqlite3.Error as e:
        st.error(f"Database error: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()

def get_language_stats():
    """Get statistics about language usage."""
    try:
        conn = sqlite3.connect('user_tracking.db')
        query = """
        SELECT 
            selected_language as 'Language',
            COUNT(*) as 'Usage Count',
            ROUND(AVG(CASE WHEN success = 1 THEN 100.0 ELSE 0 END), 2) as 'Success Rate',
            ROUND(AVG(CASE WHEN success = 1 THEN response_time ELSE NULL END), 2) as 'Avg Response Time (s)'
        FROM usage_history
        WHERE selected_language IS NOT NULL
        GROUP BY selected_language
        ORDER BY COUNT(*) DESC
        """
        df = pd.read_sql_query(query, conn)
        return df
    except sqlite3.Error as e:
        st.error(f"Database error: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals():
            conn.close()

def export_data(df_users, df_history, df_languages):
    """Export data to Excel with error handling."""
    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_users.to_excel(writer, sheet_name='Users', index=False)
            df_history.to_excel(writer, sheet_name='Usage History', index=False)
            df_languages.to_excel(writer, sheet_name='Language Stats', index=False)
        
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")
        return None

def check_database():
    """Check if database and required tables exist and have data."""
    try:
        conn = sqlite3.connect('user_tracking.db')
        c = conn.cursor()
        
        # Check if tables exist
        tables_query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name IN ('user_usage', 'usage_history', 'ip_mapping')
        """
        existing_tables = [row[0] for row in c.execute(tables_query).fetchall()]
        
        missing_tables = []
        required_tables = ['user_usage', 'usage_history', 'ip_mapping']
        
        for table in required_tables:
            if table not in existing_tables:
                missing_tables.append(table)
        
        if missing_tables:
            st.error(f"Missing tables in database: {', '.join(missing_tables)}")
            return False
        
        # Check if tables have data
        table_counts = {}
        for table in existing_tables:
            count = c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            table_counts[table] = count
        
        return table_counts
        
    except sqlite3.Error as e:
        st.error(f"Database connection error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"Error checking database: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def reset_database():
    """Reset the database tables if needed."""
    try:
        conn = sqlite3.connect('user_tracking.db')
        c = conn.cursor()
        
        # Drop existing tables
        c.execute("DROP TABLE IF EXISTS usage_history")
        c.execute("DROP TABLE IF EXISTS ip_mapping")
        c.execute("DROP TABLE IF EXISTS user_usage")
        
        conn.commit()
        
        # Reinitialize database
        from app import init_db
        success = init_db()
        
        if success:
            st.success("Database reset successfully")
        else:
            st.error("Failed to reset database")
            
    except sqlite3.Error as e:
        st.error(f"Database reset error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def get_db_stats():
    """Get database statistics and performance metrics."""
    try:
        conn = sqlite3.connect('user_tracking.db')
        c = conn.cursor()
        
        stats = {}
        
        # Get database file size
        try:
            stats['db_size'] = os.path.getsize('user_tracking.db') / (1024 * 1024)  # Size in MB
        except:
            stats['db_size'] = 0
            
        # Get table row counts
        for table in ['user_usage', 'usage_history', 'ip_mapping']:
            c.execute(f"SELECT COUNT(*) FROM {table}")
            stats[f'{table}_rows'] = c.fetchone()[0]
            
        # Get average response time
        c.execute("SELECT AVG(response_time) FROM usage_history WHERE success = 1")
        stats['avg_response_time'] = c.fetchone()[0] or 0
        
        # Get success rate
        c.execute("""
            SELECT 
                ROUND(AVG(CASE WHEN success = 1 THEN 100.0 ELSE 0 END), 2)
            FROM usage_history
        """)
        stats['overall_success_rate'] = c.fetchone()[0] or 0
        
        return stats
    except sqlite3.Error as e:
        print(f"Error getting DB stats: {e}")
        return {}
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    try:
        st.title("👥 User Tracking Dashboard")
        
        # Add reset button and stats in sidebar
        st.sidebar.subheader("Database Controls")
        if st.sidebar.button("🔄 Reset Database"):
            reset_database()
        
        # Display database stats in sidebar
        st.sidebar.subheader("Database Stats")
        db_stats = get_db_stats()
        if db_stats:
            st.sidebar.metric("Database Size", f"{db_stats['db_size']:.2f} MB")
            st.sidebar.metric("Avg Response Time", f"{db_stats['avg_response_time']:.2f}s")
            st.sidebar.metric("Overall Success Rate", f"{db_stats['overall_success_rate']:.1f}%")
        
        # Check database status first
        table_counts = check_database()
        if not table_counts:
            st.error("Database check failed. Please ensure the database is properly initialized.")
            return
        
        # Display database status
        st.sidebar.subheader("Database Status")
        for table, count in table_counts.items():
            status_color = "🟢" if count > 0 else "🔴"
            st.sidebar.text(f"{status_color} {table}: {count} records")
        
        # Add refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        # Get data with error handling
        with st.spinner("Loading data..."):
            df_users = get_user_data()
            df_history = get_usage_history()
            df_languages = get_language_stats()
        
        if df_users.empty and df_history.empty and df_languages.empty:
            if all(count == 0 for count in table_counts.values()):
                st.info("No data available yet. Wait for users to start using the application.")
            else:
                st.warning("Failed to retrieve data. Please check the error messages above.")
            return
        
        # Display summary metrics
        try:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Users", len(df_users))
            with col2:
                st.metric("Active Users", len(df_users[df_users['Status'] == 'Active']))
            with col3:
                st.metric("Total Attempts", df_users['Total Attempts'].sum())
            with col4:
                avg_success = df_users['Success Rate'].mean()
                st.metric("Overall Success Rate", f"{avg_success:.1f}%" if not pd.isna(avg_success) else "N/A")
        except Exception as e:
            st.error(f"Error displaying metrics: {str(e)}")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["User Overview", "Usage History", "Language Statistics"])
        
        with tab1:
            try:
                st.subheader("📊 User Overview")
                if df_users.empty:
                    st.info("No user data available.")
                else:
                    # Add filters
                    status_filter = st.multiselect(
                        "Filter by Status",
                        options=['Active', 'Exceeded'],
                        default=['Active', 'Exceeded']
                    )
                    
                    # Apply filters
                    filtered_df = df_users[df_users['Status'].isin(status_filter)]
                    
                    if filtered_df.empty:
                        st.info("No data matches the selected filters.")
                    else:
                        st.dataframe(
                            filtered_df,
                            column_config={
                                "User ID": st.column_config.TextColumn("User ID", width="medium"),
                                "IP Address": st.column_config.TextColumn("IP Address", width="small"),
                                "First Used": st.column_config.DatetimeColumn("First Used", format="D MMM YYYY, HH:mm"),
                                "Last Used": st.column_config.DatetimeColumn("Last Used", format="D MMM YYYY, HH:mm"),
                                "Usage Count": st.column_config.NumberColumn("Usage Count"),
                                "Total Attempts": st.column_config.NumberColumn("Total Attempts"),
                                "Success Rate": st.column_config.NumberColumn("Success Rate", format="%.1f%%"),
                                "Avg Response Time (s)": st.column_config.NumberColumn("Avg Response Time", format="%.2f"),
                                "Languages Used": st.column_config.TextColumn("Languages Used", width="large"),
                                "Status": st.column_config.TextColumn(
                                    "Status",
                                    width="small",
                                    help="Active: Under 5 uses, Exceeded: 5 or more uses"
                                ),
                            },
                            hide_index=True,
                            height=400,
                            use_container_width=True
                        )
            except Exception as e:
                st.error(f"Error in User Overview tab: {str(e)}")
        
        with tab2:
            try:
                st.subheader("📝 Usage History")
                if df_history.empty:
                    st.info("No usage history available.")
                else:
                    # Add date filter
                    min_date = pd.to_datetime(df_history['Timestamp']).min().date()
                    max_date = pd.to_datetime(df_history['Timestamp']).max().date()
                    
                    date_range = st.date_input(
                        "Filter by Date Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                    
                    # Apply date filter
                    df_history['Timestamp'] = pd.to_datetime(df_history['Timestamp'])
                    mask = (df_history['Timestamp'].dt.date >= date_range[0]) & (df_history['Timestamp'].dt.date <= date_range[1])
                    filtered_history = df_history[mask]
                    
                    if filtered_history.empty:
                        st.info("No data available for the selected date range.")
                    else:
                        st.dataframe(
                            filtered_history,
                            column_config={
                                "Timestamp": st.column_config.DatetimeColumn("Timestamp", format="D MMM YYYY, HH:mm:ss"),
                                "IP Address": st.column_config.TextColumn("IP Address", width="small"),
                                "Language": st.column_config.TextColumn("Language", width="small"),
                                "CV Length": st.column_config.NumberColumn("CV Length"),
                                "Job Desc Length": st.column_config.NumberColumn("Job Desc Length"),
                                "Success": st.column_config.CheckboxColumn("Success"),
                                "Error Message": st.column_config.TextColumn("Error Message", width="large"),
                                "Response Time (s)": st.column_config.NumberColumn("Response Time", format="%.2f")
                            },
                            hide_index=True,
                            height=400,
                            use_container_width=True
                        )
            except Exception as e:
                st.error(f"Error in Usage History tab: {str(e)}")

        with tab3:
            try:
                st.subheader("🌐 Language Statistics")
                if df_languages.empty:
                    st.info("No language statistics available.")
                else:
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.dataframe(
                            df_languages,
                            column_config={
                                "Language": st.column_config.TextColumn("Language", width="medium"),
                                "Usage Count": st.column_config.NumberColumn("Usage Count"),
                                "Success Rate": st.column_config.NumberColumn("Success Rate", format="%.1f%%"),
                                "Avg Response Time (s)": st.column_config.NumberColumn("Avg Response Time", format="%.2f")
                            },
                            hide_index=True,
                            height=300,
                            use_container_width=True
                        )
                    
                    with col2:
                        # Add a bar chart for language usage
                        st.bar_chart(df_languages.set_index('Language')['Usage Count'])
            except Exception as e:
                st.error(f"Error in Language Statistics tab: {str(e)}")
        
        # Add export functionality
        if st.button("📥 Export All Data"):
            try:
                buffer = export_data(df_users, df_history, df_languages)
                if buffer:
                    st.download_button(
                        label="Download Excel Report",
                        data=buffer,
                        file_name=f"cv_feedback_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.ms-excel"
                    )
            except Exception as e:
                st.error(f"Error during export: {str(e)}")
    
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.error("Please try refreshing the page or contact support if the issue persists.")

if __name__ == "__main__":
    try:
        if check_password():
            main()
        else:
            st.error("⚠️ Password incorrect")
    except Exception as e:
        st.error(f"Authentication error: {str(e)}") 