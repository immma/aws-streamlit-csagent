import streamlit as st
import uuid
import os
import json
from agent_backend import create_aws_agent
from pathlib import Path

st.set_page_config(page_title="AWS Strands Chat", page_icon="☁️")
st.title("☁️ AWS Cloud Assistant")
st.caption("Powered by Strands Agents & Amazon Bedrock. Code by ArdiH")

SESSION_ID = "aws-admin-session-3"
# st.caption(SESSION_ID)

# initiate uuid
unique_id = uuid.uuid4()
# Convert the UUID object to a string representation
id_string = str(unique_id)

st.caption(f"Unique id {id_string}")

# --- STORAGE SETTINGS ---
# DB_FILE = SESSION_ID + ".json"

def load_history():
    """Load history from file if it exists."""
    if os.path.exists("./chatdb/"+DB_FILE):
        with open("./chatdb/"+DB_FILE, "r") as f:
            return json.load(f)
    return []

def load_specific_history(dbfile):
    """Load history from file if it exists."""
    if os.path.exists("./chatdb/"+dbfile):
        with open("./chatdb/"+dbfile, "r") as f:
            return json.load(f)
    return []

def save_history(messages):
    """Save history to a local JSON file."""
    os.makedirs("./chatdb", exist_ok=True)
    with open("./chatdb/"+DB_FILE, "w") as f:
        json.dump(messages, f)

# Define the directory to scan (create a 'files_to_load' folder in your app's directory for testing)

DIRECTORY_PATH = Path("./chatdb")
# Function to get a list of files in the directory
def get_files_in_directory(path):
    # Use list comprehension to get only files (not directories) and filter by extension if needed
    files = [p.name for p in path.iterdir() if p.is_file() and p.suffix in ['.json', '.csv', '.py']]
    files.sort() # Sort alphabetically for consistent ordering
    return files

file_list = get_files_in_directory(DIRECTORY_PATH)

# 1. Initialize the agent
if "agent" not in st.session_state:
    st.session_state.agent = create_aws_agent(session_id=SESSION_ID)

# 2. Sync Streamlit UI history with Agent's internal session memory (direct from bedrock agent)
# if "messages" not in st.session_state:
#     st.session_state.messages = create_aws_agent(session_id=SESSION_ID).messages
#     print(create_aws_agent(session_id=SESSION_ID).messages)

# NEW load history from json file 
# if "messages" not in st.session_state:
#         st.session_state.messages = load_history()

# # Display history
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(str(message["content"]))

# sidebar
with st.sidebar: 
    if st.button("New chat"):
        print(id_string)

    st.header("History")
    if file_list:
        # Create a selectbox in the sidebar
        selected_file = st.selectbox(
            "Select a history to view:",
            file_list, 
            index = None
        )
    else:
        st.info("No supported files found in the directory.")
        selected_file = None

# Select history
if selected_file:
    st.success(f"You selected: **{selected_file}**")
    # load_specific_history(selected_file)
    st.session_state.messages = []
    SESSION_ID = selected_file
    st.caption(SESSION_ID)
    st.session_state.messages = load_specific_history(selected_file)
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