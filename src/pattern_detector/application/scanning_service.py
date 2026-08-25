"""Application scanning service orchestrating Swift pattern detection."""

from __future__ import annotations

import time
from pattern_detector.domain.detection import DetectionReport
from pattern_detector.domain.rules import get_default_rules
from pattern_detector.domain.services.rule_engine import RuleEngineService
from pattern_detector.ports.inbound import ScanOptions, ScannerPort
from pattern_detector.ports.outbound import (
    ParserPort,
    ResultRepositoryPort,
    SourceProviderPort,
)


class ScanningService(ScannerPort):
    """Coordinates discovering, parsing, rule evaluation, and exporting for Swift codebases."""

    def __init__(
        self,
        source_provider: SourceProviderPort,
        parser: ParserPort,
        rule_engine: RuleEngineService | None = None,
        json_repository: ResultRepositoryPort | None = None,
        html_repository: ResultRepositoryPort | None = None,
        markdown_repository: ResultRepositoryPort | None = None,
        sarif_repository: ResultRepositoryPort | None = None,
    ) -> None:
        self.source_provider = source_provider
        self.parser = parser
        self.rule_engine = rule_engine or RuleEngineService(rules=get_default_rules())
        self.json_repository = json_repository
        self.html_repository = html_repository
        self.markdown_repository = markdown_repository
        self.sarif_repository = sarif_repository

    def scan_path(self, target_path: str, options: ScanOptions | None = None) -> DetectionReport:
        opts = options or ScanOptions()
        t0 = time.perf_counter()

        # 1. Discover files
        loaded_files = self.source_provider.load_files(
            target_path=target_path,
            extensions=opts.file_extensions,
            exclude_dirs=opts.exclude_dirs,
        )

        # 2. Parse into domain CodeModel
        model = self.parser.parse_codebase(loaded_files, target_path=target_path)

        # 3. Evaluate rules
        detections = self.rule_engine.evaluate(
            model=model,
            min_confidence=opts.min_confidence,
            enabled_patterns=opts.enabled_patterns,
        )

        t1 = time.perf_counter()

        report = DetectionReport(
            project_path=target_path,
            scanned_files_count=len(loaded_files),
            detections=detections,
            elapsed_seconds=t1 - t0,
        )

        # 4. Optional Exports
        if opts.output_json_path and self.json_repository:
            self.json_repository.save(report, opts.output_json_path, verbose=opts.verbose)

        if opts.output_html_path and self.html_repository:
            self.html_repository.save(report, opts.output_html_path, verbose=opts.verbose)

        if opts.output_markdown_path and self.markdown_repository:
            self.markdown_repository.save(report, opts.output_markdown_path, verbose=opts.verbose)

        if opts.output_sarif_path and self.sarif_repository:
            self.sarif_repository.save(report, opts.output_sarif_path, verbose=opts.verbose)

        return report
