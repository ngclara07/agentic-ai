# app.py
# the streamlit interrface remains straightforward 

from __future__ import annotations

import streamlit as st

from agent import (
    MODEL_NAME,
    run_agent,
)

from conversation_store import (
    create_conversation,
    delete_conversation_metadata,
    list_conversations,
    rename_conversation,
    set_automatic_title,
)

from memory import (
    clear_history,
    history_to_ui_messages,
)


# =========================================================
# Page Configuration
# =========================================================

st.set_page_config(
    page_title="Local Agentic AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# Custom Styling
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1180px;
        padding-top: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-bottom: 2rem;
    }

    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        overflow-x: hidden !important;
    }

    section[data-testid="stSidebar"] {
        overflow-x: hidden !important;
    }

    section[data-testid="stSidebar"] * {
        max-width: 100%;
        box-sizing: border-box;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Session State Initialization
# =========================================================

if "conversation_id" not in st.session_state:

    conversations = list_conversations()

    if conversations:

        st.session_state.conversation_id = (
            conversations[0]["id"]
        )

    else:

        st.session_state.conversation_id = (
            create_conversation()
        )


if "messages" not in st.session_state:

    st.session_state.messages = (
        history_to_ui_messages(
            st.session_state.conversation_id
        )
    )


if "renaming_conversation" not in st.session_state:

    st.session_state.renaming_conversation = None


if "confirm_delete" not in st.session_state:

    st.session_state.confirm_delete = None


# =========================================================
# Helper Functions
# =========================================================

def switch_conversation(
    conversation_id: str,
) -> None:
    """
    Switch the UI to another saved conversation.
    """

    st.session_state.conversation_id = (
        conversation_id
    )

    st.session_state.messages = (
        history_to_ui_messages(
            conversation_id
        )
    )

    st.session_state.renaming_conversation = None
    st.session_state.confirm_delete = None


def create_new_conversation() -> None:
    """
    Create and switch to a new empty conversation.
    """

    conversation_id = (
        create_conversation()
    )

    st.session_state.conversation_id = (
        conversation_id
    )

    st.session_state.messages = []

    st.session_state.renaming_conversation = None
    st.session_state.confirm_delete = None


def delete_conversation(
    conversation_id: str,
) -> None:
    """
    Remove a conversation's history and metadata.
    """

    clear_history(
        conversation_id
    )

    delete_conversation_metadata(
        conversation_id
    )

    remaining_conversations = (
        list_conversations()
    )

    if remaining_conversations:

        switch_conversation(
            remaining_conversations[0]["id"]
        )

    else:

        create_new_conversation()


# =========================================================
# Sidebar
# =========================================================

with st.sidebar:

    st.title("🤖 Agent")

    st.caption(
        "Pydantic AI + Ollama"
    )

    st.divider()

    # -----------------------------------------------------
    # New Conversation Button
    # -----------------------------------------------------

    if st.button(
        "+ New conversation",
        use_container_width=True,
        type="primary",
    ):

        create_new_conversation()

        st.rerun()


    # -----------------------------------------------------
    # Previous Conversations
    # -----------------------------------------------------

    st.subheader(
        "Previous conversations"
    )

    conversations = (
        list_conversations()
    )

    if not conversations:

        st.caption(
            "No saved conversations yet."
        )


    for conversation in conversations:

        conversation_id = (
            conversation["id"]
        )

        title = conversation.get(
            "title",
            "Untitled conversation",
        )

        is_current = (
            conversation_id
            == st.session_state.conversation_id
        )


        # =================================================
        # Rename Mode
        # =================================================

        if (
            st.session_state.renaming_conversation
            == conversation_id
        ):

            new_title = st.text_input(
                "Rename conversation",
                value=title,
                key=(
                    f"rename_input_"
                    f"{conversation_id}"
                ),
            )

            rename_save_col, rename_cancel_col = (
                st.columns([1, 1])
            )


            with rename_save_col:

                if st.button(
                    "Save",
                    key=(
                        f"save_rename_"
                        f"{conversation_id}"
                    ),
                    use_container_width=True,
                    type="primary",
                ):

                    rename_conversation(
                        conversation_id,
                        new_title,
                    )

                    st.session_state.renaming_conversation = (
                        None
                    )

                    st.rerun()


            with rename_cancel_col:

                if st.button(
                    "Cancel",
                    key=(
                        f"cancel_rename_"
                        f"{conversation_id}"
                    ),
                    use_container_width=True,
                ):

                    st.session_state.renaming_conversation = (
                        None
                    )

                    st.rerun()


        # =================================================
        # Normal Conversation Row
        # =================================================

        else:

            col_chat, col_edit, col_delete = (
                st.columns(
                    [5, 2.5, 2.5]
                )
            )

            # ---------------------------------------------
            # Conversation Button
            # ---------------------------------------------

            with col_chat:

                button_type = (
                    "primary"
                    if is_current
                    else "secondary"
                )

                if st.button(
                    title,
                    key=(
                        f"conversation_"
                        f"{conversation_id}"
                    ),
                    use_container_width=True,
                    type=button_type,
                ):

                    switch_conversation(
                        conversation_id
                    )

                    st.rerun()


            # ---------------------------------------------
            # Rename Button
            # ---------------------------------------------

            with col_edit:

                if st.button(
                    "Edit",
                    key=(
                        f"edit_"
                        f"{conversation_id}"
                    ),
                    help="Rename conversation",
                    use_container_width=True,
                ):

                    st.session_state.renaming_conversation = (
                        conversation_id
                    )

                    st.session_state.confirm_delete = (
                        None
                    )

                    st.rerun()


            # ---------------------------------------------
            # Delete Button
            # ---------------------------------------------

            with col_delete:

                if st.button(
                    "Delete",
                    key=(
                        f"delete_"
                        f"{conversation_id}"
                    ),
                    help="Delete conversation",
                    use_container_width=True,
                ):

                    st.session_state.confirm_delete = (
                        conversation_id
                    )

                    st.session_state.renaming_conversation = (
                        None
                    )

                    st.rerun()


    # -----------------------------------------------------
    # Delete Confirmation
    # -----------------------------------------------------

    delete_id = (
        st.session_state.confirm_delete
    )

    if delete_id:

        target = next(
            (
                item
                for item in conversations
                if item["id"] == delete_id
            ),
            None,
        )

        if target:

            target_title = target.get(
                "title",
                "Untitled conversation",
            )

            st.warning(
                f'Delete "{target_title}"?'
            )

            delete_confirm_col, delete_cancel_col = (
                st.columns([1, 1])
            )


            with delete_confirm_col:

                if st.button(
                    "Confirm delete",
                    key=(
                        f"confirm_delete_"
                        f"{delete_id}"
                    ),
                    type="primary",
                    use_container_width=True,
                ):

                    st.session_state.confirm_delete = (
                        None
                    )

                    delete_conversation(
                        delete_id
                    )

                    st.rerun()


            with delete_cancel_col:

                if st.button(
                    "Cancel",
                    key=(
                        f"cancel_delete_"
                        f"{delete_id}"
                    ),
                    use_container_width=True,
                ):

                    st.session_state.confirm_delete = (
                        None
                    )

                    st.rerun()


    # -----------------------------------------------------
    # Capabilities
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "Capabilities"
    )

    st.markdown(
        """
- 🧠 Conversation memory
- 🧮 Calculator
- 🕒 Date and time
- 📝 Save notes
- 📖 Read notes
- 🔧 Autonomous tool selection
- 🖥️ Local Ollama inference
        """
    )

    st.divider()


    # -----------------------------------------------------
    # Model Information
    # -----------------------------------------------------

    st.subheader(
        "Model"
    )

    st.code(
        MODEL_NAME,
        language=None,
    )

    st.caption(
        "Runs locally through Ollama"
    )


    st.divider()


    # -----------------------------------------------------
    # Current Session Information
    # -----------------------------------------------------

    st.caption(
        "Conversation ID:"
    )

    st.code(
        st.session_state.conversation_id[:8],
        language=None,
    )


# =========================================================
# Main Page
# =========================================================

st.title(
    "🤖 Agentic AI"
)

st.caption(
    f"Local AI assistant built with "
    f"Pydantic AI + Ollama • {MODEL_NAME}"
)


# =========================================================
# Display Existing Conversation
# =========================================================

for message in (
    st.session_state.messages
):

    role = message.get(
        "role",
        "assistant",
    )

    content = message.get(
        "content",
        "",
    )

    with st.chat_message(
        role
    ):

        st.markdown(
            content
        )


# =========================================================
# User Input
# =========================================================

prompt = st.chat_input(
    "Give the local agent a task..."
)


if prompt:

    conversation_id = (
        st.session_state.conversation_id
    )


    # -----------------------------------------------------
    # Automatically Name Fresh Conversation
    # -----------------------------------------------------

    if not st.session_state.messages:

        set_automatic_title(
            conversation_id,
            prompt,
        )


    # -----------------------------------------------------
    # Store and Display User Message
    # -----------------------------------------------------

    user_message = {
        "role": "user",
        "content": prompt,
    }

    st.session_state.messages.append(
        user_message
    )


    with st.chat_message(
        "user"
    ):

        st.markdown(
            prompt
        )


    # -----------------------------------------------------
    # Run Agent
    # -----------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            f"{MODEL_NAME} is working locally..."
        ):

            try:

                response = run_agent(
                    message=prompt,
                    session_id=(
                        conversation_id
                    ),
                )

            except Exception as exc:

                response = (
                    "The local agent encountered "
                    "an error:\n\n"
                    f"`{type(exc).__name__}: "
                    f"{exc}`"
                )


        st.markdown(
            response
        )


    # -----------------------------------------------------
    # Store Assistant Message
    # -----------------------------------------------------

    assistant_message = {
        "role": "assistant",
        "content": response,
    }

    st.session_state.messages.append(
        assistant_message
    )


    # -----------------------------------------------------
    # Refresh Sidebar
    # -----------------------------------------------------

    st.rerun()
