import streamlit as st
import os
import json
from agent_backend import create_aws_agent

st.set_page_config(page_title="AWS Strands Chat", page_icon="☁️")
st.title("☁️ AWS Cloud Assistant")
st.caption("Powered by Strands Agents & Amazon Bedrock. Code by ArdiH")

SESSION_ID = "aws-admin-session-3"
st.caption(SESSION_ID)

# --- STORAGE SETTINGS ---
DB_FILE = SESSION_ID + ".json"

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

# print(create_aws_agent(session_id=SESSION_ID).messages)

# 1. Initialize the agent
if "agent" not in st.session_state:
    st.session_state.agent = create_aws_agent(session_id=SESSION_ID)

# 2. Sync Streamlit UI history with Agent's internal session memory (direct from bedrock agent)
# if "messages" not in st.session_state:
#     st.session_state.messages = create_aws_agent(session_id=SESSION_ID).messages
#     print(create_aws_agent(session_id=SESSION_ID).messages)

# new 
if "messages" not in st.session_state:
        st.session_state.messages = load_history()

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(str(message["content"]))

# Chat input
if prompt := st.chat_input("Ask about your AWS resources..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consulting AWS..."):
            try:
                # The agent automatically uses its internal session_manager
                response = st.session_state.agent(prompt)
                full_text = str(response)
                
                st.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                save_history(st.session_state.messages)
            except Exception as e:
                st.error(f"Error: {e}")