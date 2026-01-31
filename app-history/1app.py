import streamlit as st
import uuid
import os
import json
from agent_backend import create_aws_agent

st.set_page_config(page_title="AWS Strands Chat", page_icon="☁️")
st.title("☁️ AWS Cloud Assistant")

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
    if chat_id in data and isinstance(data[chat_id], dict):
        display_title = data[chat_id].get("title", "Existing Chat")
    else:
        display_title = title if title else "New Chat"

    data[chat_id] = {"title": display_title, "messages": messages}
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def delete_chat(chat_id):
    data = load_all_history()
    if chat_id in data:
        del data[chat_id]
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)
        
        # Reset to a fresh state if the deleted chat was the active one
        if st.session_state.chat_id == chat_id:
            st.session_state.chat_id = str(uuid.uuid4())
            st.session_state.messages = []
        
        # Force a rerun to close all popovers and refresh list
        st.rerun()

# --- SESSION STATE INITIALIZATION ---
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("Cloud Controls")
    
    if st.button("➕ Start New Conversation", use_container_width=True, type="primary"):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    # --- DOWNLOAD SECTION ---
    all_history_data = load_all_history()
    if all_history_data:
        # 1. Download Entire Database (JSON)
        json_bytes = json.dumps(all_history_data, indent=4).encode('utf-8')
        st.download_button(
            label="📥 Export Full DB (JSON)",
            data=json_bytes,
            file_name="aws_master_history.json",
            mime="application/json",
            use_container_width=True
        )
        
        # 2. Download CURRENT Chat (Text)
        if st.session_state.messages:
            chat_text = f"AWS Chat Session: {st.session_state.chat_id}\n" + "="*30 + "\n"
            for m in st.session_state.messages:
                chat_text += f"{m['role'].upper()}: {m['content']}\n\n"
            
            st.download_button(
                label="📄 Export Current Chat (TXT)",
                data=chat_text,
                file_name=f"chat_{st.session_state.chat_id[:8]}.txt",
                mime="text/plain",
                use_container_width=True
            )

    st.divider()
    st.subheader("Recent Chats")
    
    search_query = st.text_input("🔍 Search", placeholder="Keywords...").lower()
    
    if all_history_data:
        filtered_chats = {
            cid: cdata for cid, cdata in all_history_data.items() 
            if search_query in (cdata['title'] if isinstance(cdata, dict) else "").lower()
        }

        if filtered_chats:
            for cid, cdata in reversed(list(filtered_chats.items())):
                title = cdata['title'] if isinstance(cdata, dict) else f"Legacy {cid[:5]}"
                label = f"➡️ {title}" if cid == st.session_state.chat_id else f"💬 {title}"
                
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    if st.button(label, key=f"load_{cid}", use_container_width=True):
                        st.session_state.chat_id = cid
                        st.session_state.messages = cdata['messages'] if isinstance(cdata, dict) else cdata
                        st.rerun()
                with col2:
                    # Native Popover for confirmation
                    with st.popover("🗑️"):
                        st.write("Confirm delete?")
                        # Calling delete_chat here will trigger st.rerun() inside the function
                        if st.button("Yes, delete", key=f"conf_{cid}", type="primary"):
                            delete_chat(cid)
        else:
            st.info("No matches.")
    else:
        st.info("No history yet.")

# --- MAIN CHAT ---
st.caption(f"Session: {st.session_state.chat_id}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help with your AWS stack?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("AWS Doctor is thinking..."):
            try:
                agent = create_aws_agent(session_id=st.session_state.chat_id)
                response = agent(prompt)
                full_text = str(response)
                
                st.markdown(full_text)
                st.session_state.messages.append({"role": "assistant", "content": full_text})
                
                chat_title = None
                if len(st.session_state.messages) <= 2:
                    chat_title = prompt[:30] + ("..." if len(prompt) > 30 else "")
                
                save_to_master(st.session_state.chat_id, st.session_state.messages, title=chat_title)
                
            except Exception as e:
                st.error(f"Error: {e}")