import streamlit as st
import uuid
import os
import json
from agent_backend import create_aws_agent

st.set_page_config(page_title="AWS Strands Chat", page_icon="☁️")
st.title("☁️ AWS Cloud Assistant")
st.caption("Powered by Strands Agents & Amazon Bedrock. Code by ArdiH")

# --- SETTINGS & PATHS ---
DB_FILE = "chatdb/master_history.json"
os.makedirs("chatdb", exist_ok=True)

# --- DATABASE FUNCTIONS ---
def load_all_history():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_to_master(chat_id, messages):
    data = load_all_history()
    data[chat_id] = messages
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- SESSION STATE INITIALIZATION ---
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("Control Panel")
    
    # BUTTON: Create New Chat
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.header("History")
    
    all_chats = load_all_history()
    chat_options = list(all_chats.keys())

    if chat_options:
        # We use a selectbox to switch between old chats
        selected_id = st.selectbox(
            "Select a previous chat:",
            options=chat_options,
            index=None,
            placeholder="Choose a session..."
        )
        
        if selected_id and selected_id != st.session_state.chat_id:
            st.session_state.chat_id = selected_id
            st.session_state.messages = all_chats[selected_id]
            st.rerun()
    else:
        st.info("No saved chats yet.")

# --- MAIN CHAT INTERFACE ---
st.caption(f"Current Session ID: {st.session_state.chat_id}")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about your AWS resources..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Consulting AWS..."):
            try:
                # Backend agent uses the same chat_id
                agent = create_aws_agent(session_id=st.session_state.chat_id)
                response = agent(prompt)
                full_text = str(response)
                print("CHAT ID: " + st.session_state.chat_id)
                st.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                
                # Save to the single master JSON
                save_to_master(st.session_state.chat_id, st.session_state.messages)
                
            except Exception as e:
                st.error(f"Error: {e}")