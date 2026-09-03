# memory.py
# pydantic AI treats conversations as  sequences of model messages;
# a subsequent run can receive previous messages through "message_history";
# the framework also exposes "ModelMessagesTypeAdapter" specifically for serializing and reloading them

# this file gives the application persistent disk-backed conversation memory 

from __future__ import annotations

from pathlib import Path

from pydantic_ai import (
    ModelMessage,
    ModelMessagesTypeAdapter,
)


MEMORY_DIRECTORY = Path(
    "data/conversations"
)


def _conversation_file(
    session_id: str,
) -> Path:
    """
    Return the JSON history file associated with a conversation.
    """

    MEMORY_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_session_id = "".join(
        character
        for character in session_id
        if character.isalnum()
        or character in ("-", "_")
    )

    return (
        MEMORY_DIRECTORY
        / f"{safe_session_id}.json"
    )


def load_history(
    session_id: str,
) -> list[ModelMessage]:
    """
    Load stored Pydantic AI conversation history.
    """

    file_path = _conversation_file(
        session_id
    )

    if not file_path.exists():
        return []

    try:
        return (
            ModelMessagesTypeAdapter
            .validate_json(
                file_path.read_bytes()
            )
        )

    except Exception:
        return []


def save_history(
    session_id: str,
    messages: list[ModelMessage],
) -> None:
    """
    Save Pydantic AI conversation history.
    """

    file_path = _conversation_file(
        session_id
    )

    json_data = (
        ModelMessagesTypeAdapter
        .dump_json(
            messages,
            indent=2,
        )
    )

    file_path.write_bytes(
        json_data
    )


def clear_history(
    session_id: str,
) -> None:
    """
    Delete stored conversation history.
    """

    file_path = _conversation_file(
        session_id
    )

    if file_path.exists():
        file_path.unlink()


def history_to_ui_messages(
    session_id: str,
) -> list[dict]:
    """
    Convert stored Pydantic AI model history
    into Streamlit-compatible chat messages.

    Returns:
        [
            {
                "role": "user",
                "content": "..."
            },
            {
                "role": "assistant",
                "content": "..."
            }
        ]
    """

    history = load_history(
        session_id
    )

    ui_messages: list[dict] = []

    for message in history:

        message_kind = getattr(
            message,
            "kind",
            None,
        )

        parts = getattr(
            message,
            "parts",
            [],
        )

        for part in parts:

            part_kind = getattr(
                part,
                "part_kind",
                "",
            )

            content = getattr(
                part,
                "content",
                None,
            )

            if not isinstance(
                content,
                str,
            ):
                continue

            content = content.strip()

            if not content:
                continue

            # User message
            if (
                message_kind == "request"
                and part_kind == "user-prompt"
            ):
                ui_messages.append(
                    {
                        "role": "user",
                        "content": content,
                    }
                )

            # Assistant response
            elif (
                message_kind == "response"
                and part_kind == "text"
            ):
                ui_messages.append(
                    {
                        "role": "assistant",
                        "content": content,
                    }
                )

    return ui_messages
