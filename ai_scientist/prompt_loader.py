import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any


class PromptNotFoundError(FileNotFoundError):
    """Raised when a requested prompt file is missing."""


def _resolve_prompt_dir() -> Path:
    """Resolve the root directory that stores prompt template files."""
    env_dir = os.environ.get("AI_SCIENTIST_PROMPT_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    # Default to <repo_root>/prompt
    return Path(__file__).resolve().parents[1] / "prompt"


PROMPT_DIR = _resolve_prompt_dir()


@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    """
    Load a prompt template by name.

    Args:
        name: Relative path inside the prompt directory. The ".txt" suffix is
              optional; if omitted it is added automatically.

    Returns:
        The prompt text with trailing whitespace preserved.
    """

    rel_path = Path(name)
    if rel_path.suffix:
        prompt_path = PROMPT_DIR / rel_path
    else:
        prompt_path = PROMPT_DIR / rel_path.with_suffix(".txt")

    if not prompt_path.exists():
        raise PromptNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8")


def format_prompt(name: str, **kwargs) -> str:
    """
    Convenience helper to load and format a prompt template.

    Args:
        name: Relative path (without extension) to the prompt file.
        **kwargs: Keyword arguments passed to str.format on the template.

    Returns:
        The formatted prompt string.
    """

    return load_prompt(name).format(**kwargs)


def load_prompt_lines(name: str) -> list[str]:
    """
    Load a prompt template and return it as a list of lines.

    Args:
        name: Relative path (without extension) to the prompt file.

    Returns:
        List of lines preserving indentation and empty lines.
    """

    content = load_prompt(name)
    # Preserve indentation and intentional blank lines
    return content.splitlines()


def load_prompt_json(name: str) -> Any:
    """
    Load and parse a JSON prompt template.

    Args:
        name: Relative path (including .json if needed) to the prompt file.

    Returns:
        The parsed JSON content.
    """

    return json.loads(load_prompt(name))
