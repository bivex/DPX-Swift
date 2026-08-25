"""Filesystem source provider adapter for discovering Swift source files."""

from __future__ import annotations

import os
from pathlib import Path
from pattern_detector.ports.outbound import SourceProviderPort


class FileSourceProvider(SourceProviderPort):
    """Recursively discovers and reads Swift source files from disk."""

    DEFAULT_EXCLUDES = {
        ".git",
        ".build",
        ".swiftpm",
        "DerivedData",
        "Pods",
        "Carthage",
        ".venv",
        "node_modules",
        "__pycache__",
    }

    def load_files(
        self,
        target_path: str,
        extensions: list[str],
        exclude_dirs: list[str] | None = None,
    ) -> list[tuple[str, str]]:
        path_obj = Path(target_path).resolve()
        excludes = self.DEFAULT_EXCLUDES.union(set(exclude_dirs or []))
        results: list[tuple[str, str]] = []

        if path_obj.is_file():
            if any(path_obj.name.endswith(ext) for ext in extensions):
                try:
                    content = path_obj.read_text(encoding="utf-8", errors="replace")
                    return [(str(path_obj), content)]
                except Exception:
                    return []
            return []

        for root, dirs, files in os.walk(path_obj):
            dirs[:] = [d for d in dirs if d not in excludes and not d.startswith(".")]

            for file_name in files:
                if any(file_name.endswith(ext) for ext in extensions):
                    full_p = Path(root) / file_name
                    try:
                        content = full_p.read_text(encoding="utf-8", errors="replace")
                        results.append((str(full_p), content))
                    except Exception:
                        continue

        return results
