from strands import Agent
from strands.models import BedrockModel
from strands_tools import use_aws

def create_aws_agent():
    # Initialize the model (using Claude 3.5 Sonnet on Bedrock)
    model = BedrockModel(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0",
        region_name="us-east-1", # Change to your Bedrock region
        temperature=0.5
    )

    # Define the system prompt to give the agent its identity
    system_prompt = (
        "You are an expert AWS Cloud Engineer. Your name is AWS Doctor, please greeting before you answer. You have access to the AWS environment "
        "via the 'use_aws' tool. Use this tool to list resources, check statuses, and "
        "answer technical questions about the current infrastructure."
    )

    # Create the agent with the AWS tool enabled
    return Agent(
        model=model,
        tools=[use_aws],
        system_prompt=system_prompt
    )