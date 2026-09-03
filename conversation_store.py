# conversation_store.py

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path


DATA_DIRECTORY = Path("data")

INDEX_FILE = (
    DATA_DIRECTORY
    / "conversations_index.json"
)


def _ensure_storage() -> None:
    """
    Ensure the data directory and index file exist.
    """

    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not INDEX_FILE.exists():
        INDEX_FILE.write_text(
            "{}",
            encoding="utf-8",
        )


def _load_index() -> dict:
    """
    Load conversation metadata.
    """

    _ensure_storage()

    try:
        return json.loads(
            INDEX_FILE.read_text(
                encoding="utf-8"
            )
        )

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return {}


def _save_index(
    conversations: dict,
) -> None:
    """
    Save conversation metadata.
    """

    _ensure_storage()

    INDEX_FILE.write_text(
        json.dumps(
            conversations,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def create_conversation(
    title: str = "New conversation",
) -> str:
    """
    Create a conversation and return its ID.
    """

    conversations = _load_index()

    conversation_id = str(
        uuid.uuid4()
    )

    now = datetime.now().isoformat()

    conversations[conversation_id] = {
        "title": title,
        "created_at": now,
        "updated_at": now,
    }

    _save_index(conversations)

    return conversation_id


def list_conversations() -> list[dict]:
    """
    Return non-empty conversations ordered
    by most recently updated.
    """

    conversations = _load_index()

    result = []

    for conversation_id, metadata in conversations.items():

        if metadata.get("title") == "New conversation":
            continue

        result.append(
            {
                "id": conversation_id,
                **metadata,
            }
        )

    result.sort(
        key=lambda item: item.get(
            "updated_at",
            "",
        ),
        reverse=True,
    )

    return result


def get_conversation(
    conversation_id: str,
) -> dict | None:
    """
    Retrieve conversation metadata.
    """

    conversations = _load_index()

    metadata = conversations.get(
        conversation_id
    )

    if metadata is None:
        return None

    return {
        "id": conversation_id,
        **metadata,
    }


def rename_conversation(
    conversation_id: str,
    new_title: str,
) -> None:
    """
    Rename a conversation.
    """

    conversations = _load_index()

    if conversation_id not in conversations:
        return

    cleaned_title = (
        new_title.strip()
        or "Untitled conversation"
    )

    conversations[
        conversation_id
    ]["title"] = cleaned_title

    conversations[
        conversation_id
    ]["updated_at"] = (
        datetime.now().isoformat()
    )

    _save_index(conversations)


def touch_conversation(
    conversation_id: str,
) -> None:
    """
    Update the conversation's modified timestamp.
    """

    conversations = _load_index()

    if conversation_id not in conversations:
        return

    conversations[
        conversation_id
    ]["updated_at"] = (
        datetime.now().isoformat()
    )

    _save_index(conversations)


def set_automatic_title(
    conversation_id: str,
    user_message: str,
) -> None:
    """
    Give a new conversation a title based on
    the first user message.
    """

    conversations = _load_index()

    if conversation_id not in conversations:
        return

    current_title = conversations[
        conversation_id
    ].get(
        "title",
        "New conversation",
    )

    if current_title != "New conversation":
        return

    title = " ".join(
        user_message
        .strip()
        .split()
    )

    if len(title) > 42:
        title = title[:42].rstrip() + "..."

    if not title:
        title = "New conversation"

    conversations[
        conversation_id
    ]["title"] = title

    conversations[
        conversation_id
    ]["updated_at"] = (
        datetime.now().isoformat()
    )

    _save_index(conversations)


def delete_conversation_metadata(
    conversation_id: str,
) -> None:
    """
    Remove conversation metadata.
    """

    conversations = _load_index()

    conversations.pop(
        conversation_id,
        None,
    )

    _save_index(conversations)
