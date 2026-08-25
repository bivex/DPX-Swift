"""JSON, Markdown, and SARIF formatters & persistence repositories for Swift."""

from __future__ import annotations

import json
from pathlib import Path
from pattern_detector.domain.detection import DetectionReport
from pattern_detector.ports.outbound import ReportFormatterPort, ResultRepositoryPort


class JsonReportFormatter(ReportFormatterPort):
    """Formats report into structured JSON."""

    def format(self, report: DetectionReport, verbose: bool = False) -> str:
        return json.dumps(report.to_dict(), indent=2)


class MarkdownReportFormatter(ReportFormatterPort):
    """Formats report into clean GitHub-flavored Markdown."""

    def format(self, report: DetectionReport, verbose: bool = False) -> str:
        lines = [
            f"# 🍏 DPX-Swift: Architectural Context & Design Pattern Report",
            f"",
            f"- **Target Project:** `{report.project_path}`",
            f"- **Scanned Files:** {report.scanned_files_count}",
            f"- **Total Detections:** {report.total_detections_count}",
            f"- **Scan Time:** {report.elapsed_seconds:.3f}s",
            f"",
            f"## 📊 Summary by Category",
            f"",
            f"| Category | Detections |",
            f"|---|:---:|",
        ]
        for cat, cnt in sorted(report.summary_by_category.items(), key=lambda x: -x[1]):
            if cnt > 0:
                lines.append(f"| `{cat}` | {cnt} |")

        lines.extend([
            f"",
            f"## 🔍 Detailed Pattern Instances & Violations",
            f"",
        ])

        for idx, d in enumerate(report.detections, 1):
            loc_str = f"`{d.primary_location}`" if d.primary_location else "N/A"
            lines.extend([
                f"### {idx}. {d.pattern_type.value} on `{d.target_name}` ({d.confidence.percentage_str} [{d.level.value}])",
                f"- **Category:** `{d.pattern_category.value}`",
                f"- **Target Kind:** `{d.target_kind}`",
                f"- **Location:** {loc_str}",
                f"- **Summary:** {d.summary}",
            ])
            if d.evidences:
                lines.append(f"- **Evidence Trail:**")
                for ev in d.evidences:
                    lines.append(f"  - `+{int(ev.weight * 100)}%` ({ev.rule_code}): {ev.description}")
            lines.append("")

        return "\n".join(lines)


class SarifReportFormatter(ReportFormatterPort):
    """Formats report into OASIS SARIF v2.1.0 JSON for GitHub Security / Code Scanning."""

    def format(self, report: DetectionReport, verbose: bool = False) -> str:
        results = []
        for det in report.detections:
            loc = det.primary_location
            file_uri = loc.file_path if loc else "unknown"
            line = loc.line if loc else 1
            col = loc.column if loc else 1

            level = "error" if det.pattern_category.value in ("resilience", "principle") else "note"

            results.append({
                "ruleId": det.pattern_type.value,
                "level": level,
                "message": {
                    "text": det.summary,
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": file_uri,
                            },
                            "region": {
                                "startLine": line,
                                "startColumn": col,
                            },
                        }
                    }
                ],
            })

        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "DPX-Swift",
                            "informationUri": "https://github.com/bivex/DPX-Swift",
                            "version": "0.1.0",
                        }
                    },
                    "results": results,
                }
            ],
        }
        return json.dumps(sarif, indent=2)


class FileResultRepository(ResultRepositoryPort):
    """Persists formatted string to file path."""

    def __init__(self, formatter: ReportFormatterPort) -> None:
        self.formatter = formatter

    def save(self, report: DetectionReport, destination_path: str, verbose: bool = False) -> None:
        content = self.formatter.format(report, verbose=verbose)
        path_obj = Path(destination_path).resolve()
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        path_obj.write_text(content, encoding="utf-8")
