# tools.py
# this file contains the ordinaty python functions that our agent can invoke 

from __future__ import annotations

import ast
import operator
from datetime import datetime
from pathlib import Path


# =========================================================
# Safe Calculator
# =========================================================

_ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluate_expression(node: ast.AST) -> int | float:
    """
    Recursively evaluate a restricted arithmetic expression.
    """

    if isinstance(node, ast.Expression):
        return _evaluate_expression(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value

        raise ValueError("Only numeric constants are allowed.")

    if isinstance(node, ast.BinOp):
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_BINARY_OPERATORS:
            raise ValueError("Unsupported binary operator.")

        left = _evaluate_expression(node.left)
        right = _evaluate_expression(node.right)

        return _ALLOWED_BINARY_OPERATORS[operator_type](
            left,
            right,
        )

    if isinstance(node, ast.UnaryOp):
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_UNARY_OPERATORS:
            raise ValueError("Unsupported unary operator.")

        value = _evaluate_expression(node.operand)

        return _ALLOWED_UNARY_OPERATORS[operator_type](value)

    raise ValueError("Unsupported mathematical expression.")


def calculator(expression: str) -> str:
    """
    Safely calculate an arithmetic expression.

    Examples:
        10 + 5
        (25 * 8) / 4
        2 ** 10
    """

    try:
        parsed_expression = ast.parse(
            expression,
            mode="eval",
        )

        result = _evaluate_expression(
            parsed_expression
        )

        return str(result)

    except ZeroDivisionError:
        return "Calculation error: division by zero."

    except Exception as exc:
        return f"Calculation error: {exc}"


# =========================================================
# Date and Time
# =========================================================

def get_current_time() -> str:
    """
    Return the current local server date and time.
    """

    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# =========================================================
# Notes
# =========================================================

NOTES_DIRECTORY = Path("data/notes")


def _safe_note_name(title: str) -> str:
    """
    Sanitize a note filename.
    """

    safe_title = "".join(
        character
        for character in title
        if character.isalnum()
        or character in (" ", "-", "_")
    ).strip()

    return safe_title or "untitled_note"


def save_note(
    title: str,
    content: str,
) -> str:
    """
    Save a note to local disk.
    """

    NOTES_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    safe_title = _safe_note_name(title)

    file_path = (
        NOTES_DIRECTORY
        / f"{safe_title}.txt"
    )

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return (
        f"Note saved successfully to "
        f"{file_path}"
    )


def read_note(title: str) -> str:
    """
    Read a previously saved note.
    """

    safe_title = _safe_note_name(title)

    file_path = (
        NOTES_DIRECTORY
        / f"{safe_title}.txt"
    )

    if not file_path.exists():
        return (
            f"No note named '{title}' "
            f"was found."
        )

    return file_path.read_text(
        encoding="utf-8",
    )


def list_notes() -> str:
    """
    List locally stored notes.
    """

    NOTES_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    note_files = sorted(
        NOTES_DIRECTORY.glob("*.txt")
    )

    if not note_files:
        return "No notes have been saved."

    return "\n".join(
        file.stem
        for file in note_files
    )
