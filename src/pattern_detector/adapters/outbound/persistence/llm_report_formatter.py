"""Token-Efficient LLM / AI Prompt Context Formatter for Swift."""

from __future__ import annotations

from pattern_detector.domain.detection import DetectionReport
from pattern_detector.domain.value_objects import PatternCategory


class LlmReportFormatter:
    """Formatter that generates structured architectural context for LLMs."""

    def format_scan_report(self, report: DetectionReport) -> str:
        """Render DetectionReport as structured XML/Markdown context for LLMs."""
        lines: list[str] = [
            "<codebase_architecture_analysis language=\"swift\">",
            f'  <project path="{report.project_path or "."}" files="{report.scanned_files_count}" detections="{report.total_detections_count}">',
            "    <category_summary>",
        ]

        for cat, count in report.summary_by_category.items():
            if count > 0:
                lines.append(f'      <category name="{cat.upper()}" count="{count}" />')
        lines.append("    </category_summary>")

        # Separate Design Patterns, Concurrency, and Violations
        patterns = [d for d in report.detections if d.pattern_category not in (PatternCategory.PRINCIPLE, PatternCategory.RESILIENCE)]
        hazards = [d for d in report.detections if d.pattern_category in (PatternCategory.PRINCIPLE, PatternCategory.RESILIENCE)]

        if patterns:
            lines.append("    <swift_design_patterns_and_concurrency>")
            for d in patterns:
                loc = f"{d.primary_location.file_path}:{d.primary_location.line}" if d.primary_location else ""
                lines.append(f'      <pattern type="{d.pattern_type.value}" target="{d.target_name}" category="{d.pattern_category.value}" confidence="{d.confidence.percentage_str}" location="{loc}">')
                lines.append(f"        <summary>{d.summary}</summary>")
                lines.append("        <evidence>")
                for ev in d.evidences:
                    lines.append(f'          <item rule="{ev.rule_code}" weight="+{int(ev.weight * 100)}%">{ev.description}</item>')
                lines.append("        </evidence>")
                lines.append("      </pattern>")
            lines.append("    </swift_design_patterns_and_concurrency>")

        if hazards:
            lines.append("    <architectural_violations_and_safety_hazards>")
            for v in hazards:
                loc = f"{v.primary_location.file_path}:{v.primary_location.line}" if v.primary_location else ""
                lines.append(f'      <hazard rule="{v.pattern_type.value}" target="{v.target_name}" category="{v.pattern_category.value}" confidence="{v.confidence.percentage_str}" location="{loc}">')
                lines.append(f"        <risk>{v.summary}</risk>")
                lines.append("        <evidence>")
                for ev in v.evidences:
                    lines.append(f'          <item rule="{ev.rule_code}">{ev.description}</item>')
                lines.append("        </evidence>")
                lines.append("      </hazard>")
            lines.append("    </architectural_violations_and_safety_hazards>")

        lines.extend([
            "  </project>",
            "</codebase_architecture_analysis>",
        ])
        return "\n".join(lines)
