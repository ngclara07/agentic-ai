# agent.py
# Core Pydantic AI implementation.
#
# Local development:
#   Pydantic AI -> Ollama -> qwen3:4b
#
# Streamlit Cloud:
#   Pydantic AI -> Groq OpenAI-compatible API -> Qwen model

from __future__ import annotations

import os

from dotenv import load_dotenv

from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
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


# =========================================================
# Environment Configuration
# =========================================================

load_dotenv()


AI_PROVIDER = os.getenv(
    "AI_PROVIDER",
    "ollama",
).strip().lower()


# =========================================================
# Model Configuration
# =========================================================

if AI_PROVIDER == "groq":

    MODEL_NAME = os.getenv(
        "AI_MODEL",
        "qwen/qwen3-32b",
    )

    GROQ_API_KEY = os.getenv(
        "GROQ_API_KEY"
    )

    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is required when "
            "AI_PROVIDER=groq."
        )

    model = OpenAIChatModel(
        MODEL_NAME,
        provider=OpenAIProvider(
            base_url=(
                "https://api.groq.com/openai/v1"
            ),
            api_key=GROQ_API_KEY,
        ),
    )


elif AI_PROVIDER == "ollama":

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


else:

    raise ValueError(
        f"Unsupported AI_PROVIDER: {AI_PROVIDER}. "
        "Supported providers are 'ollama' and 'groq'."
    )


# =========================================================
# Agent Definition
# =========================================================

agent = Agent(
    model,

    instructions="""
You are an agentic AI assistant built with Pydantic AI.

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
- current local/server date and time
- saving notes
- reading saved notes
- listing saved notes
- conversational memory

Rules:

- Use the calculator for non-trivial arithmetic.
- Use the time tool when exact current time is requested.
- Save a note only when the user explicitly requests persistence.
- Read notes using the appropriate note tool.
- Never claim that a tool was executed unless it actually succeeded.
- Never fabricate tool results.
- Do not reveal hidden chain-of-thought.
- If a tool fails, explain the failure clearly.
""",
)


# =========================================================
# Agent Tools
# =========================================================

@agent.tool_plain
def calculate(expression: str) -> str:
    """
    Safely calculate an arithmetic expression.
    """
    return calculator(expression)


@agent.tool_plain
def current_time() -> str:
    """
    Return the current local/server date and time.
    """
    return get_current_time()


@agent.tool_plain
def create_note(
    title: str,
    content: str,
) -> str:
    """
    Save a text note.
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


# =========================================================
# Agent Runner
# =========================================================

def run_agent(
    message: str,
    session_id: str,
) -> str:
    """
    Run the agent with persisted conversation history.
    """

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
