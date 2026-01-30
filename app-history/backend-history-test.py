import os
from strands import Agent
from strands.models import BedrockModel
from strands_tools import use_aws
from strands.session import FileSessionManager

def create_aws_agent(session_id="default-session"):
    # Ensure the directory exists
    os.makedirs("./sessions", exist_ok=True)

    model = BedrockModel(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        region_name="us-east-1"
    )

    # Pass the session_id directly into the constructor
    session_manager = FileSessionManager(
        path="./sessions", 
        session_id=session_id
    )

    return Agent(
        model=model,
        tools=[use_aws],
        session_manager=session_manager,
        system_prompt="You are a helpful AWS expert assistant."
    )

print(create_aws_agent('aws-admin-session-1').messages)