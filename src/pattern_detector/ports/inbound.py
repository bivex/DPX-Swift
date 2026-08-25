"""Inbound driving ports for DPX-Swift."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from pattern_detector.domain.detection import DetectionReport
from pattern_detector.domain.value_objects import ConfidenceLevel


@dataclass
class ScanOptions:
    """Configuration options for a Swift scanning session."""

    min_confidence: float = 0.0
    enabled_patterns: list[str] = field(default_factory=list)
    file_extensions: list[str] = field(default_factory=lambda: [".swift"])
    output_json_path: str | None = None
    output_html_path: str | None = None
    output_markdown_path: str | None = None
    output_sarif_path: str | None = None
    include_principles: bool = True
    exclude_dirs: list[str] = field(default_factory=list)
    verbose: bool = False


class ScannerPort(Protocol):
    """Inbound port for scanning a target directory or file."""

    def scan_path(self, target_path: str, options: ScanOptions | None = None) -> DetectionReport:
        """Scan a path and return detection report."""
        ...
