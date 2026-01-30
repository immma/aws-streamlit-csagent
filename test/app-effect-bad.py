import streamlit as st
import time
from agent_backend import create_aws_agent

st.set_page_config(page_title="AWS Strands Chatbot", page_icon="☁️")
st.title("☁️ AWS Cloud Assistant")

if "agent" not in st.session_state:
    st.session_state.agent = create_aws_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Helper function to create a stream effect from the agent's response
def stream_data(text: str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04) # Adjust speed as needed

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about your AWS resources..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. Run the agent logic
        with st.spinner("Analyzing environment..."):
            agent_response = st.session_state.agent(prompt)
            full_text = str(agent_response)

        # 2. Use write_stream for the typewriter effect
        response_placeholder = st.write_stream(stream_data(full_text))
        
    st.session_state.messages.append({"role": "assistant", "content": full_text})