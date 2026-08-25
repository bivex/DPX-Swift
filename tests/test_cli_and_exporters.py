"""Unit tests for CLI commands and formatters/exporters in DPX-Swift."""

from __future__ import annotations

from typer.testing import CliRunner
from pattern_detector.adapters.inbound.cli.main import app
from pattern_detector.adapters.outbound.persistence import (
    HtmlReportFormatter,
    JsonReportFormatter,
    LlmReportFormatter,
    MarkdownReportFormatter,
    SarifReportFormatter,
)
from pattern_detector.domain.detection import Detection, DetectionReport
from pattern_detector.domain.value_objects import (
    Confidence,
    Evidence,
    PatternCategory,
    PatternType,
    SourceLocation,
)

runner = CliRunner()


def _create_sample_report() -> DetectionReport:
    loc = SourceLocation(file_path="Sources/App/Store.swift", line=10, column=1)
    ev = Evidence(rule_code="CONCURRENCY_ACTOR_ISOLATION", description="Actor provides state isolation", weight=0.95, location=loc)
    det = Detection(
        pattern_type=PatternType.ACTOR_MODEL_ISOLATION,
        pattern_category=PatternCategory.CONCURRENCY,
        target_name="AccountStore",
        target_kind="actor",
        confidence=Confidence(score=0.95, evidences=[ev]),
        primary_location=loc,
        evidences=[ev],
    )
    return DetectionReport(
        project_path="Sources/App",
        scanned_files_count=5,
        detections=[det],
        elapsed_seconds=0.012,
    )


def test_cli_rules_command() -> None:
    result = runner.invoke(app, ["rules"])
    assert result.exit_code == 0
    assert "DPX-Swift" in result.stdout
    assert "PROTOCOL_ORIENTED" in result.stdout
    assert "actor_model" in result.stdout


def test_cli_info_command() -> None:
    result = runner.invoke(app, ["info", "actor_model_isolation"])
    assert result.exit_code == 0
    assert "Actor Model Isolation" in result.stdout


def test_exporters_format() -> None:
    report = _create_sample_report()

    html_out = HtmlReportFormatter().format(report)
    assert "<!DOCTYPE html>" in html_out
    assert "Pattern Scanner Report" in html_out
    assert "AccountStore" in html_out
    assert "Copy AI Context Prompt" in html_out

    md_out = MarkdownReportFormatter().format(report)
    assert "# 🍏 DPX-Swift" in md_out
    assert "AccountStore" in md_out

    json_out = JsonReportFormatter().format(report)
    assert '"total_detections_count": 1' in json_out

    sarif_out = SarifReportFormatter().format(report)
    assert '"$schema"' in sarif_out

    llm_out = LlmReportFormatter().format_scan_report(report)
    assert '<codebase_architecture_analysis language="swift">' in llm_out
