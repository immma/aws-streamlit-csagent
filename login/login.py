import streamlit as st
from agent_backend import create_aws_agent

# --- AUTHENTICATION CONFIG ---
USER_CREDENTIALS = {
    "admin": "password123",
    "cloud_user": "aws_pass_2024"
}

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

# --- MAIN APP LOGIC ---
if check_password():
    st.set_page_config(page_title="AWS Strands Chatbot", page_icon="☁️")

    with st.sidebar:
        st.success("Authenticated")
        if st.button("Sign Out"):
            del st.session_state["password_correct"]
            st.rerun()

    st.title("☁️ AWS Cloud Assistant")
    st.caption("Powered by Strands Agents & Amazon Bedrock. Code by ArdiH")
    
    # Initialize Agent
    if "agent" not in st.session_state:
        st.session_state.agent = create_aws_agent()

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("How many EC2 instances are running?"):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response (Direct display, no streaming)
        with st.chat_message("assistant"):
            with st.spinner("Querying AWS..."):
                try:
                    # Agent processes the request
                    agent_response = st.session_state.agent(prompt)
                    full_text = str(agent_response)
                    
                    # Display the text all at once
                    st.markdown(full_text)
                    
                    # Save to history
                    st.session_state.messages.append({"role": "assistant", "content": full_text})
                except Exception as e:
                    st.error(f"AWS Agent Error: {e}")