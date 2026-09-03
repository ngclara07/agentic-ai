# agent.py
# this is the core pydantic AI implementation 

# currently pydantic AI allows normal python functions to be registered using 
# "@agent.tool_plain"; tools requiring dependency context use "@agent.tool"

# for web access, current pydantic AI exposes "WebSearchTool" through a "NativeTool" 
# capability when using an openAI responses model 

from __future__ import annotations

import os

from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.usage import UsageLimits

from memory import (
    load_history,
    save_history,
)

from tools import (
    calculator,
    get_current_time,
    list_notes,
    read_note,
    save_note,
)

from conversation_store import (
    touch_conversation,
)


load_dotenv()


MODEL_NAME = os.getenv(
    "AI_MODEL",
    "qwen3:4b",
)

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434/v1",
)


model = OllamaModel(
    MODEL_NAME,
    provider=OllamaProvider(
        base_url=OLLAMA_BASE_URL,
    ),
)


agent = Agent(
    model,

    instructions="""
You are a local agentic AI assistant running through
Pydantic AI and Ollama.

Your objective is to accomplish user tasks rather than
merely generate conversational responses.

For each request:

1. Determine the user's objective.
2. Decide whether one or more tools are required.
3. Invoke the appropriate tool when necessary.
4. Inspect the tool result.
5. Perform another tool action if required.
6. Return a concise and complete final answer.

Available capabilities include:

- mathematical calculations
- current local date and time
- saving notes
- reading saved notes
- listing saved notes
- conversational memory

Rules:

- Use the calculator for non-trivial arithmetic.
- Use the time tool when exact local time is requested.
- Save a note only when the user requests persistence.
- Read notes using the appropriate note tool.
- Never claim that a tool was executed unless it actually succeeded.
- Never fabricate tool results.
- Do not reveal hidden chain-of-thought.
""",
)


@agent.tool_plain
def calculate(expression: str) -> str:
    """
    Safely calculate an arithmetic expression.
    """
    return calculator(expression)


@agent.tool_plain
def current_time() -> str:
    """
    Return the current local date and time.
    """
    return get_current_time()


@agent.tool_plain
def create_note(
    title: str,
    content: str,
) -> str:
    """
    Save a text note locally.
    """
    return save_note(
        title=title,
        content=content,
    )


@agent.tool_plain
def retrieve_note(title: str) -> str:
    """
    Read a previously stored note.
    """
    return read_note(title)


@agent.tool_plain
def available_notes() -> str:
    """
    List all saved notes.
    """
    return list_notes()


def run_agent(
    message: str,
    session_id: str,
) -> str:

    history = load_history(
        session_id
    )

    result = agent.run_sync(
        message,
        message_history=history,
        usage_limits=UsageLimits(
            request_limit=10,
            tool_calls_limit=8,
        ),
    )

    save_history(
        session_id=session_id,
        messages=result.all_messages(),
    )

    touch_conversation(
        session_id
    )

    return result.output
