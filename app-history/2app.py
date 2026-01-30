import streamlit as st
import uuid
import os
import json
from agent_backend import create_aws_agent

st.set_page_config(page_title="AWS Strands Chat", page_icon="☁️")
st.title("☁️ AWS Cloud Assistant")
st.caption("Powered by Strands Agents & Amazon Bedrock. Code by ArdiH")

# --- SETTINGS & PATHS ---
DB_FILE = "chatdb/master_history_2.json"
os.makedirs("chatdb", exist_ok=True)

# --- DATABASE FUNCTIONS ---
def load_all_history():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_to_master(chat_id, messages, title=None):
    data = load_all_history()
    # If this ID exists, keep its title; otherwise use the new one or default
    if chat_id in data and isinstance(data[chat_id], dict):
        display_title = data[chat_id].get("title", "Existing Chat")
    else:
        display_title = title if title else "New Chat"

    data[chat_id] = {"title": display_title, "messages": messages}
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- SESSION STATE INITIALIZATION ---
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("Cloud Controls")
    
    # FIX 1: New Chat button now explicitly clears the selectbox state
    if st.button("➕ Start New Conversation", use_container_width=True):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        # Clear the selectbox selection by resetting its key in session_state
        if "history_select" in st.session_state:
            st.session_state.history_select = None
        st.rerun()

    st.divider()
    st.subheader("Recent Chats")
    
    all_chats = load_all_history()
    
    if all_chats:
        chat_mapping = {v['title'] if isinstance(v, dict) else f"Legacy {k[:5]}": k 
                        for k, v in all_chats.items()}
        
        # FIX 2: Added 'key' to selectbox so we can control it programmatically
        selected_title = st.selectbox(
            "Browse History:",
            options=list(chat_mapping.keys()),
            index=None,
            placeholder="Select a topic...",
            key="history_select" 
        )
        
        # FIX 3: Only switch chats if the user EXPLICITLY clicks the selectbox
        # We check if the session_state for this widget matches the current chat
        if selected_title:
            target_id = chat_mapping[selected_title]
            if target_id != st.session_state.chat_id:
                st.session_state.chat_id = target_id
                chat_data = all_chats[target_id]
                st.session_state.messages = chat_data['messages'] if isinstance(chat_data, dict) else chat_data
                st.rerun()
    else:
        st.info("No history yet.")

# --- MAIN CHAT INTERFACE ---
st.caption(f"Current Session ID: {st.session_state.chat_id}")

# --- MAIN CHAT ---
# Display messages from the current active session
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help with your AWS stack?"):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AWS Doctor is thinking..."):
            try:
                # Use the current chat_id (whether new or from history)
                agent = create_aws_agent(session_id=st.session_state.chat_id)
                response = agent(prompt)
                full_text = str(response)
                
                st.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                
                # Title Logic: Set title ONLY if it's a brand new chat (1st message)
                chat_title = None
                if len(st.session_state.messages) <= 2:
                    chat_title = prompt[:35] + ("..." if len(prompt) > 35 else "")
                
                save_to_master(st.session_state.chat_id, st.session_state.messages, title=chat_title)
                
                print("CHAT ID: " + st.session_state.chat_id)
            except Exception as e:
                st.error(f"Error: {e}")