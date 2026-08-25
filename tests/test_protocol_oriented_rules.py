"""Unit tests for Protocol-Oriented Programming (POP) detection rules in Swift."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_swift_parser import NativeSwiftParserAdapter
from pattern_detector.domain.rules.protocol_oriented_rules import (
    AssociatedTypePatRule,
    ExistentialAnyBoxRule,
    OpaqueReturnTypeRule,
    ProtocolCompositionRule,
    ProtocolExtensionDefaultImplRule,
)
from pattern_detector.domain.value_objects import PatternType


def test_protocol_extension_default_impl() -> None:
    code = """
    protocol Repository {
        func fetch(id: String) -> User?
        func fetchAll() -> [User]
    }

    extension Repository {
        func fetchAll() -> [User] {
            return []
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Repository.swift", code)])

    rule = ProtocolExtensionDefaultImplRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.PROTOCOL_EXTENSION_DEFAULT_IMPL
    assert detections[0].target_name == "Repository"
    assert detections[0].confidence.percentage >= 85


def test_associated_type_pat_rule() -> None:
    code = """
    protocol CollectionViewAdapter {
        associatedtype Item: Identifiable
        associatedtype CellView: View

        func render(item: Item) -> CellView
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Adapter.swift", code)])

    rule = AssociatedTypePatRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.ASSOCIATED_TYPE_PAT
    assert detections[0].target_name == "CollectionViewAdapter"


def test_protocol_composition_rule() -> None:
    code = """
    typealias ProfileRecord = Codable & Identifiable & CustomStringConvertible

    func renderCard(entity: any Identifiable & View) {
        print(entity)
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Types.swift", code)])

    rule = ProtocolCompositionRule()
    detections = rule.evaluate(model)

    assert len(detections) >= 1
    assert detections[0].pattern_type == PatternType.PROTOCOL_COMPOSITION


def test_opaque_return_type_rule() -> None:
    code = """
    struct HomeView: View {
        var body: some View {
            Text("Hello")
        }

        func makeHeader() -> some Shape {
            return Circle()
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("HomeView.swift", code)])

    rule = OpaqueReturnTypeRule()
    detections = rule.evaluate(model)

    assert len(detections) >= 1
    assert detections[0].pattern_type == PatternType.OPAQUE_RETURN_TYPE


def test_existential_any_box_rule() -> None:
    code = """
    class Coordinator {
        var activePlugin: any PluginProtocol
        init(plugin: any PluginProtocol) {
            self.activePlugin = plugin
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Coordinator.swift", code)])

    rule = ExistentialAnyBoxRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.EXISTENTIAL_ANY_BOX
    assert "PluginProtocol" in detections[0].target_name
