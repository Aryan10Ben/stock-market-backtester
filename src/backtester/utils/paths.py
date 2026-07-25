from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    """
    Get the absolute path to the project root directory.
    This resolves relative to this file's location, ensuring it works
    regardless of the current working directory.
    """
    return Path(__file__).resolve().parent.parent.parent.parent

def resolve_path(relative_path: str | Path) -> Path:
    """
    Resolve a path relative to the project root.
    """
    path = Path(relative_path)
    if path.is_absolute():
        return path
    return get_project_root() / path
