"""Persistence formatters and repositories package for DPX-Swift."""

from __future__ import annotations

from pattern_detector.adapters.outbound.persistence.console_report_formatter import ConsoleReportFormatter
from pattern_detector.adapters.outbound.persistence.formatters import (
    FileResultRepository,
    JsonReportFormatter,
    MarkdownReportFormatter,
    SarifReportFormatter,
)
from pattern_detector.adapters.outbound.persistence.html_report_formatter import HtmlReportFormatter
from pattern_detector.adapters.outbound.persistence.llm_report_formatter import LlmReportFormatter

__all__ = [
    "ConsoleReportFormatter",
    "HtmlReportFormatter",
    "JsonReportFormatter",
    "MarkdownReportFormatter",
    "SarifReportFormatter",
    "LlmReportFormatter",
    "FileResultRepository",
]
