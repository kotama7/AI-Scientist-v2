import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional


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


def _resolve_prompt_path(name: str, base_dir: Optional[Path] = None) -> Path:
    """Resolve a prompt path relative to the configured prompt directory or a custom base."""
    rel_path = Path(name)
    if rel_path.suffix:
        prompt_path = rel_path
    else:
        prompt_path = rel_path.with_suffix(".txt")

    base = (base_dir or PROMPT_DIR).expanduser().resolve()
    return base / prompt_path


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

    prompt_path = _resolve_prompt_path(name)

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


def load_prompt_from_dir(name: str, base_dir: Path) -> str:
    """
    Load a prompt from an explicit directory, bypassing the global prompt root.

    Args:
        name: Relative path to the prompt file.
        base_dir: Directory that should be treated as the prompt root.
    """

    prompt_path = _resolve_prompt_path(name, base_dir=base_dir)
    if not prompt_path.exists():
        raise PromptNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def write_prompt(
    name: str,
    content: str,
    *,
    base_dir: Optional[Path] = None,
) -> None:
    """
    Write prompt content to disk, optionally targeting a custom prompt root.

    Args:
        name: Relative path to the prompt file.
        content: Text content to write.
        base_dir: Optional base directory; defaults to the global prompt root.
    """

    prompt_path = _resolve_prompt_path(name, base_dir=base_dir)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(content, encoding="utf-8")
    # Clear caches so future reads pick up the updated content.
    load_prompt.cache_clear()
