import streamlit as st
import uuid
import os
import json
from agent_backend import create_aws_agent
import datetime
from fpdf import FPDF
import io

current_date = datetime.datetime.now().strftime("%Y-%m-%d")

# Inside the st.download_button:
FILE_NAME=f"chat_backup_{current_date}.json"

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

# --- HELPER FUNCTION FOR PDF GENERATION ---
def generate_history_pdf(all_chats):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title of the Document
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AWS Cloud Assistant - Full Chat History", ln=True, align='C')
    pdf.ln(10)

    for chat_id, data in all_chats.items():
        title = data.get("title", "Untitled Chat")
        messages = data.get("messages", [])

        # Chat Header
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, f"Chat: {title}", ln=True, fill=True)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 5, f"ID: {chat_id}", ln=True)
        pdf.ln(5)

        # Messages
        for msg in messages:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            content = msg["content"]
            
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 5, f"{role}:", ln=True)
            
            pdf.set_font("Arial", "", 10)
            # multi_cell handles text wrapping
            pdf.multi_cell(0, 5, content)
            pdf.ln(2)
        
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Separator line
        pdf.ln(5)

    return pdf.output(dest='S') # Returns as bytes

# Delete chat history by id
def delete_chat(chat_id):
    data = load_all_history()
    if chat_id in data:
        del data[chat_id]
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=4)

        # Reset session and clear sidebar selection
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        if "history_select" in st.session_state:
            st.session_state.history_select = None
            
        st.rerun()

# --- CONFIRMATION DELETE DIALOG ---
@st.dialog("Delete Conversation")
def show_delete_dialog():
    st.warning("This will permanently delete this conversation.")
    st.caption("This action cannot be undone.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Cancel", use_container_width=True):
            st.rerun() # Just closes the dialog by refreshing

    with col2:
        if st.button("Delete", type="primary", use_container_width=True):
            delete_chat(st.session_state.chat_id)
            # delete_chat already has st.rerun(), so the app will refresh automatically

# --- SESSION STATE INITIALIZATION ---
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("Cloud Controls")
    
    # FIX 1: New Chat button now explicitly clears the selectbox state
    if st.button("Start New Conversation", use_container_width=True, icon=":material/add:", type="primary"):
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.messages = []
        # Clear the selectbox selection by resetting its key in session_state
        if "history_select" in st.session_state:
            st.session_state.history_select = None
        st.rerun()

    # 📁 Export All Chats Button
    all_history_data = load_all_history()
    
    if all_history_data:
        # Convert the entire database to a JSON string
        full_json_string = json.dumps(all_history_data, indent=4)
        st.download_button(
            label="📁 Export All History (JSON)",
            data=full_json_string,
            file_name=FILE_NAME,
            mime="application/json",
            use_container_width=True,
            help="Download all saved conversations in one file"
        )
    else:
        st.button("📁 Export All History", use_container_width=True, disabled=True)

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

# Load history to check if the current chat exists in the database
all_chats = load_all_history()

# --- DELETE CHAT BUTTON (TOP BAR) ---
top_col1, top_col2 = st.columns([0.5, 0.2])

if st.session_state.chat_id in all_chats:
    with top_col2:
        if st.button("Delete conversation", help="Delete this conversation", icon=":material/close:", type="primary"):
            show_delete_dialog()  # Calling the decorated function opens the popup
        else:
            pass

# --- DELETE CONFIRMATION DIALOG ---
if st.session_state.get("show_delete_dialog"):
    @st.dialog("Delete Conversation")
    def delete_dialog():
        st.warning("This will permanently delete this conversation.")
        st.caption("This action cannot be undone.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Cancel"):
                st.session_state.show_delete_dialog = False
                st.rerun()

        with col2:
            if st.button("Delete", type="primary"):
                st.session_state.show_delete_dialog = False
                delete_chat(st.session_state.chat_id)

    delete_dialog()

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