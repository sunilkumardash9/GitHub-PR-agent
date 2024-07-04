# Import necessary libraries
import os

from composio.client.collections import TriggerEventData

# Import modules from Composio and LlamaIndex
from composio_llamaindex import Action, App, ComposioToolSet
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.llms import ChatMessage
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI

# Initialize a ComposioToolSet with the API key from environment variables
composio_toolset = ComposioToolSet()

# Retrieve tools from Composio, specifically the EMBEDTOOL app
# Define the tools
tools = composio_toolset.get_actions(
    actions=[
        Action.GITHUB_GET_CODE_CHANGES_IN_PR,
        Action.GITHUB_PULLS_CREATE_REVIEW_COMMENT,
        Action.GITHUB_ISSUES_CREATE,
        Action.SLACKBOT_CHAT_POST_MESSAGE,
    ]
)

llm = OpenAI("GPT-4o")

# Define the system message for the agent
prefix_messages = [
    ChatMessage(
        role="system",
        content=(
            """
                You are an experienced code reviewer.
                Your task is to review the provided file diff and give constructive feedback.

                Follow these steps:
                1. Identify if the file contains significant logic changes.
                2. Summarize the changes in the diff in clear and concise English, within 100 words.
                3. Provide actionable suggestions if there are any issues in the code.

                Once you have decided on the changes, for any TODOs, create a Github issue.
                Also add the comprehensive review to the PR as a comment.
            """

        ),
    )
]

# Initialize a FunctionCallingAgentWorker with the tools, LLM, and system messages
agent = FunctionCallingAgentWorker(
    tools=tools,  # Tools available for the agent to use
    llm=llm,  # Language model for processing requests
    prefix_messages=prefix_messages,  # Initial system messages for context
    max_function_calls=10,  # Maximum number of function calls allowed
    allow_parallel_tool_calls=False,  # Disallow parallel tool calls
    verbose=True,  # Enable verbose output
).as_agent()


# Define the tools
pr_agent_tools = composio_toolset.get_actions(
    actions=[
        Action.GITHUB_GET_CODE_CHANGES_IN_PR,
        Action.GITHUB_PULLS_CREATE_REVIEW_COMMENT,
        Action.GITHUB_ISSUES_CREATE,
        Action.SLACKBOT_CHAT_POST_MESSAGE,
    ]
)

# Create a trigger listener
listener = composio_toolset.create_trigger_listener()
@listener.callback(filters={"trigger_name": "github_pull_request_event"})
def review_new_pr(event: TriggerEventData) -> None:
    # Using the information from Trigger, execute the agent
    code_to_review = str(event.payload)
    response = agent.chat("Review the following pr:"+code_to_review)
    print(response)

print("Listener started!")
print("Create a pr to get the review")
listener.listen()