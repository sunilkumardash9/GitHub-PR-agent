import os

from composio.client.collections import TriggerEventData

from composio_llamaindex import Action, App, ComposioToolSet
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.llms import ChatMessage
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI

composio_toolset = ComposioToolSet()

tools = composio_toolset.get_actions(
    actions=[
        Action.GITHUB_GET_CODE_CHANGES_IN_PR,
        Action.GITHUB_PULLS_CREATE_REVIEW_COMMENT,
        Action.GITHUB_ISSUES_CREATE,
        Action.SLACKBOT_CHAT_POST_MESSAGE,
    ]
)

llm = OpenAI("GPT-4o")

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

agent = FunctionCallingAgentWorker(
    tools=tools,
    llm=llm,
    prefix_messages=prefix_messages,
    max_function_calls=10,
    allow_parallel_tool_calls=False,
    verbose=True
).as_agent()

pr_agent_tools = composio_toolset.get_actions(
    actions=[
        Action.GITHUB_GET_CODE_CHANGES_IN_PR,
        Action.GITHUB_PULLS_CREATE_REVIEW_COMMENT,
        Action.GITHUB_ISSUES_CREATE,
        Action.SLACKBOT_CHAT_POST_MESSAGE,
    ]
)

listener = composio_toolset.create_trigger_listener()
@listener.callback(filters={"trigger_name": "github_pull_request_event"})
def review_new_pr(event: TriggerEventData) -> None:
    code_to_review = str(event.payload)
    response = agent.chat("Review the following pr:"+code_to_review)
    print(response)

print("Listener started!")
print("Create a pr to get the review")
listener.listen()