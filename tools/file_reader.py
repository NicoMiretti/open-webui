"""
Tool: file_reader
Description: Reads a file from the local filesystem and returns its content.
             Agents use this to inspect source code, configs, or documents
             directly without copy-pasting into the chat.

Usage in OpenWebUI:
  - Workspace → Tools → New Tool → paste this file.
  - Enable in Dev Agent and QA Agent configurations.
"""

import os
from pathlib import Path


def file_reader(file_path: str, max_lines: int = 300) -> str:
    """
    Read a file from the filesystem and return its content.

    Args:
        file_path: Absolute or relative path to the file.
        max_lines: Maximum number of lines to return (default 300).
                   Use 0 for no limit.

    Returns:
        File content as a string, or an error message.
    """
    try:
        path = Path(file_path).expanduser().resolve()

        if not path.exists():
            return f"[ERROR] File not found: {path}"

        if not path.is_file():
            return f"[ERROR] Path is not a file: {path}"

        # Basic safety: refuse to read sensitive files
        blocked = [".env", "id_rsa", "id_ed25519", ".pem", ".key"]
        if any(path.name.endswith(b) or path.name == b.lstrip(".") for b in blocked):
            return f"[BLOCKED] Refused to read sensitive file: {path.name}"

        size_kb = path.stat().st_size / 1024
        if size_kb > 512:
            return f"[ERROR] File too large ({size_kb:.0f} KB). Max 512 KB."

        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()

        if max_lines and len(lines) > max_lines:
            truncated = "\n".join(lines[:max_lines])
            return (
                f"# {path}\n"
                f"# [Truncated: showing {max_lines} of {len(lines)} lines]\n\n"
                + truncated
            )

        return f"# {path}\n\n{content}"

    except PermissionError:
        return f"[ERROR] Permission denied: {file_path}"
    except Exception as e:
        return f"[ERROR] Could not read file: {e}"


def list_directory(dir_path: str, depth: int = 2) -> str:
    """
    List the contents of a directory up to a given depth.

    Args:
        dir_path: Path to the directory.
        depth: How many levels deep to list (default 2).

    Returns:
        Tree-like string representation of the directory.
    """
    try:
        path = Path(dir_path).expanduser().resolve()

        if not path.exists():
            return f"[ERROR] Directory not found: {path}"

        if not path.is_dir():
            return f"[ERROR] Not a directory: {path}"

        lines = [str(path)]

        def _walk(current: Path, current_depth: int, prefix: str):
            if current_depth > depth:
                return
            try:
                entries = sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name))
            except PermissionError:
                return

            for i, entry in enumerate(entries):
                is_last = i == len(entries) - 1
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{entry.name}")
                if entry.is_dir():
                    extension = "    " if is_last else "│   "
                    _walk(entry, current_depth + 1, prefix + extension)

        _walk(path, 1, "")
        return "\n".join(lines)

    except Exception as e:
        return f"[ERROR] Could not list directory: {e}"
