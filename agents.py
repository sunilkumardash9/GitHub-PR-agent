from llama_index.core.agent import FunctionCallingAgentWorker

agent = FunctionCallingAgentWorker(
    tools=tools,
    llm=llm,
    prefix_messages=prefix_messages,
    max_function_calls=10,
    allow_parallel_tool_calls=False,
    verbose=True
).as_agent()    allow_parallel_tool_calls=False,  # Disallow parallel tool calls
    verbose=True,  # Enable verbose output
).as_agent()