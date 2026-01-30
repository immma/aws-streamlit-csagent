import streamlit as st
import json
import os
from agent_backend import create_aws_agent

# --- STORAGE SETTINGS ---
DB_FILE = "chat_db.json"

def load_history():
    """Load history from file if it exists."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(messages):
    """Save history to a local JSON file."""
    with open(DB_FILE, "w") as f:
        json.dump(messages, f)

# --- AUTHENTICATION (Keep your existing check_password logic) ---
# --- AUTHENTICATION CONFIG ---
USER_CREDENTIALS = {
    "admin": "password123",
    "cloud_user": "aws_pass_2024"
}
# ... (check_password code from previous step) ...
def check_password():
    """Returns True if the user had the correct password."""
    if "password_correct" not in st.session_state:
        st.title("🔐 AWS Agent Login")
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Log In"):
            if user in USER_CREDENTIALS and password == USER_CREDENTIALS[user]:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("😕 Invalid username or password")
        return False
    return True

if check_password():
    st.set_page_config(page_title="AWS Strands Chatbot", page_icon="☁️")
    with st.sidebar:
        st.success("Authenticated")
        if st.button("Sign Out"):
            del st.session_state["password_correct"]
            st.rerun()

    st.title("☁️ AWS Cloud Assistant")
    
    # Initialize Agent
    if "agent" not in st.session_state:
        st.session_state.agent = create_aws_agent()

    # CRITICAL: Initialize history from the file instead of an empty list
    if "messages" not in st.session_state:
        st.session_state.messages = load_history()

    # Display History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask about your AWS resources..."):
        # 1. Update session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Query Agent
        with st.chat_message("assistant"):
            with st.spinner("Querying AWS..."):
                try:
                    agent_response = st.session_state.agent(prompt)
                    full_text = str(agent_response)
                    st.markdown(full_text)
                    
                    # 3. Save assistant response
                    st.session_state.messages.append({"role": "assistant", "content": full_text})
                    
                    # 4. PERSIST TO DISK
                    save_history(st.session_state.messages)
                except Exception as e:
                    st.error(f"AWS Agent Error: {e}")

    # Optional: Clear History Button
    if st.sidebar.button("Clear History"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        st.session_state.messages = []
        st.rerun()