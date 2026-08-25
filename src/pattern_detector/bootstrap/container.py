"""Bootstrap Dependency Injection Container / Composition Root for Swift Pattern Detector."""

from __future__ import annotations

from pattern_detector.adapters.outbound.filesystem.file_source_provider import FileSourceProvider
from pattern_detector.adapters.outbound.parsers.native_swift_parser import NativeSwiftParserAdapter
from pattern_detector.adapters.outbound.persistence import (
    ConsoleReportFormatter,
    FileResultRepository,
    HtmlReportFormatter,
    JsonReportFormatter,
    LlmReportFormatter,
    MarkdownReportFormatter,
    SarifReportFormatter,
)
from pattern_detector.application.scanning_service import ScanningService
from pattern_detector.domain.rules import get_default_rules
from pattern_detector.domain.services.rule_engine import RuleEngineService
from pattern_detector.ports.inbound import ScannerPort
from pattern_detector.ports.outbound import (
    ParserPort,
    ReportFormatterPort,
    ResultRepositoryPort,
    SourceProviderPort,
)


class Container:
    """Dependency Injection Container and Composition Root."""

    def __init__(
        self,
        source_provider: SourceProviderPort | None = None,
        parser: ParserPort | None = None,
        json_repository: ResultRepositoryPort | None = None,
        html_repository: ResultRepositoryPort | None = None,
        markdown_repository: ResultRepositoryPort | None = None,
        sarif_repository: ResultRepositoryPort | None = None,
        report_formatter: ReportFormatterPort | None = None,
        html_formatter: ReportFormatterPort | None = None,
        markdown_formatter: ReportFormatterPort | None = None,
        sarif_formatter: ReportFormatterPort | None = None,
        llm_formatter: LlmReportFormatter | None = None,
        rule_engine: RuleEngineService | None = None,
    ) -> None:
        # Outbound Driven Adapters
        self.source_provider: SourceProviderPort = source_provider or FileSourceProvider()
        self.parser: ParserPort = parser or NativeSwiftParserAdapter()

        self.html_formatter: ReportFormatterPort = html_formatter or HtmlReportFormatter()
        self.markdown_formatter: ReportFormatterPort = markdown_formatter or MarkdownReportFormatter()
        self.sarif_formatter: ReportFormatterPort = sarif_formatter or SarifReportFormatter()
        self.llm_formatter: LlmReportFormatter = llm_formatter or LlmReportFormatter()
        self.report_formatter: ReportFormatterPort = report_formatter or ConsoleReportFormatter()

        self.json_repository: ResultRepositoryPort = json_repository or FileResultRepository(formatter=JsonReportFormatter())
        self.html_repository: ResultRepositoryPort = html_repository or FileResultRepository(formatter=self.html_formatter)
        self.markdown_repository: ResultRepositoryPort = markdown_repository or FileResultRepository(formatter=self.markdown_formatter)
        self.sarif_repository: ResultRepositoryPort = sarif_repository or FileResultRepository(formatter=self.sarif_formatter)

        # Domain Service & Rules
        self.rule_engine: RuleEngineService = rule_engine or RuleEngineService(rules=get_default_rules())

        # Application Service (Inbound Port implementation)
        self.scanning_service: ScanningService = ScanningService(
            source_provider=self.source_provider,
            parser=self.parser,
            rule_engine=self.rule_engine,
            json_repository=self.json_repository,
            html_repository=self.html_repository,
            markdown_repository=self.markdown_repository,
            sarif_repository=self.sarif_repository,
        )

    def get_scanner(self) -> ScannerPort:
        return self.scanning_service

    def get_formatter(self) -> ReportFormatterPort:
        return self.report_formatter


def create_container() -> Container:
    """Create a default production container."""
    return Container()
