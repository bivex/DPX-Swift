"""Unit tests for SOLID principles and code quality rules in Swift."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_swift_parser import NativeSwiftParserAdapter
from pattern_detector.domain.rules.solid_principles_rules import (
    FatProtocolIspRule,
    KissCyclomaticComplexityRule,
    KissLongParameterListRule,
    MassiveViewControllerSrpRule,
)
from pattern_detector.domain.value_objects import PatternType


def test_massive_view_controller_srp() -> None:
    methods_code = "\n".join(f"func method{i}() {{}}" for i in range(16))
    code = f"""
    class OrderViewController: UIViewController {{
        {methods_code}
    }}
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("OrderViewController.swift", code)])

    rule = MassiveViewControllerSrpRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.MASSIVE_VIEW_CONTROLLER_SRP
    assert detections[0].target_name == "OrderViewController"


def test_fat_protocol_isp() -> None:
    methods_code = "\n".join(f"func req{i}()" for i in range(10))
    code = f"""
    protocol MegaServiceProtocol {{
        {methods_code}
    }}
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("MegaService.swift", code)])

    rule = FatProtocolIspRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.FAT_PROTOCOL_ISP


def test_kiss_long_parameter_list() -> None:
    code = """
    func configureUser(id: String, name: String, age: Int, email: String, address: String, role: String) {
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("UserConfig.swift", code)])

    rule = KissLongParameterListRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.KISS_LONG_PARAMETER_LIST


def test_kiss_cyclomatic_complexity() -> None:
    branches = "\n".join(f"if x == {i} {{ print({i}) }}" for i in range(11))
    code = f"""
    func complexBranching(x: Int) {{
        {branches}
    }}
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Complex.swift", code)])

    rule = KissCyclomaticComplexityRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.KISS_CYCLOMATIC_COMPLEXITY
