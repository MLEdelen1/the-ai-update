from __future__ import annotations

import os
import sys
from pathlib import Path


def project_root(start: Path | None = None) -> Path:
    """Resolve project root from this repository layout.

    Priority: explicit env override, then derive from caller location.
    """
    env_root = os.environ.get("X_MANAGE_PROJECT_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    anchor = (start or Path(__file__)).resolve()
    # src/runtime_paths.py -> repo root is parent of src
    if anchor.is_file():
        anchor = anchor.parent
    if anchor.name == "src":
        return anchor.parent
    return anchor


def python_executable() -> str:
    """Best-effort interpreter for subprocess python invocations."""
    return sys.executable or os.environ.get("PYTHON") or "python"
