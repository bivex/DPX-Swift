"""Unit tests for SwiftUI & Declarative DSL detection rules in Swift."""

from __future__ import annotations

from pattern_detector.adapters.outbound.parsers.native_swift_parser import NativeSwiftParserAdapter
from pattern_detector.domain.rules.declarative_dsl_rules import (
    KeyPathDynamicLookupRule,
    PropertyWrapperPatternRule,
    ResultBuilderDslRule,
    ViewModifierPipelineRule,
)
from pattern_detector.domain.value_objects import PatternType


def test_property_wrapper_pattern() -> None:
    code = """
    @propertyWrapper
    struct Clamped<T: Comparable> {
        private var value: T
        private let range: ClosedRange<T>

        var wrappedValue: T {
            get { value }
            set { value = min(max(newValue, range.lowerBound), range.upperBound) }
        }

        init(wrappedValue: T, range: ClosedRange<T>) {
            self.range = range
            self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("Clamped.swift", code)])

    rule = PropertyWrapperPatternRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.PROPERTY_WRAPPER_PATTERN
    assert detections[0].target_name == "Clamped"


def test_result_builder_dsl() -> None:
    code = """
    @resultBuilder
    struct MenuBuilder {
        static func buildBlock(_ components: MenuItem...) -> [MenuItem] {
            return components
        }

        static func buildEither(first component: [MenuItem]) -> [MenuItem] {
            return component
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("MenuBuilder.swift", code)])

    rule = ResultBuilderDslRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.RESULT_BUILDER_DSL
    assert detections[0].target_name == "MenuBuilder"


def test_view_modifier_pipeline() -> None:
    code = """
    struct PrimaryButtonModifier: ViewModifier {
        func body(content: Content) -> some View {
            content
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(8)
        }
    }
    """
    parser = NativeSwiftParserAdapter()
    model = parser.parse_codebase([("ButtonModifier.swift", code)])

    rule = ViewModifierPipelineRule()
    detections = rule.evaluate(model)

    assert len(detections) == 1
    assert detections[0].pattern_type == PatternType.VIEW_MODIFIER_PIPELINE
    assert detections[0].target_name == "PrimaryButtonModifier"
