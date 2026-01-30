import streamlit as st
from agent_backend import create_aws_agent

st.set_page_config(page_title="AWS Strands Chatbot", page_icon="☁️")
st.title("☁️ AWS Cloud Assistant")
st.caption("Powered by Strands Agents & Amazon Bedrock. Code by Ardih")

# Initialize the agent in session state so it persists across reruns
if "agent" not in st.session_state:
    st.session_state.agent = create_aws_agent()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is running in my S3 buckets?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Diagnosing AWS..."):
            try:
                # Strands agent call
                response = st.session_state.agent(prompt)
                full_response = str(response)
                st.markdown(full_response)
                # Save to history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Error: {str(e)}")