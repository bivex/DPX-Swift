"""SwiftUI & Declarative DSL detection rules."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BaseRule
from pattern_detector.domain.value_objects import (
    Confidence,
    Evidence,
    PatternCategory,
    PatternType,
)


class PropertyWrapperPatternRule(BaseRule):
    """Detects `@propertyWrapper` declarations and property wrapper definitions."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if any("@propertyWrapper" in attr for attr in t.attributes):
                has_wrapped_val = any(p.name == "wrappedValue" for p in t.properties)
                weight = 0.95 if has_wrapped_val else 0.85
                evidences = [
                    Evidence(
                        rule_code="DSL_PROPERTY_WRAPPER_DECLARATION",
                        description=f"Type '{t.name}' is defined as a custom @propertyWrapper with encapsulated wrappedValue semantics",
                        weight=weight,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.PROPERTY_WRAPPER_PATTERN,
                        pattern_category=PatternCategory.DECLARATIVE_DSL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=weight, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class ResultBuilderDslRule(BaseRule):
    """Detects `@resultBuilder` definitions and declarative DSL syntax builders."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if any("@resultBuilder" in attr for attr in t.attributes) or any("@_functionBuilder" in attr for attr in t.attributes):
                has_build_block = any(m.name.startswith("buildBlock") for m in t.methods)
                weight = 0.95 if has_build_block else 0.85
                evidences = [
                    Evidence(
                        rule_code="DSL_RESULT_BUILDER_DECLARATION",
                        description=f"Type '{t.name}' defines a @resultBuilder DSL with declarative block transformation methods",
                        weight=weight,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.RESULT_BUILDER_DSL,
                        pattern_category=PatternCategory.DECLARATIVE_DSL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=weight, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class KeyPathDynamicLookupRule(BaseRule):
    """Detects `@dynamicMemberLookup` and KeyPath subscript resolvers."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if any("@dynamicMemberLookup" in attr for attr in t.attributes):
                evidences = [
                    Evidence(
                        rule_code="DSL_DYNAMIC_MEMBER_LOOKUP",
                        description=f"Type '{t.name}' implements @dynamicMemberLookup for type-safe dynamic KeyPath forwarding",
                        weight=0.90,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.KEYPATH_DYNAMIC_LOOKUP,
                        pattern_category=PatternCategory.DECLARATIVE_DSL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=0.90, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class ViewModifierPipelineRule(BaseRule):
    """Detects `ViewModifier` conformance and SwiftUI view styling pipelines."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if "ViewModifier" in t.inherited_types:
                has_body_fn = any(m.name == "body" for m in t.methods)
                weight = 0.95 if has_body_fn else 0.85
                evidences = [
                    Evidence(
                        rule_code="DSL_VIEW_MODIFIER_CONFORMANCE",
                        description=f"Struct '{t.name}' conforms to ViewModifier providing reusable composable view transformation pipeline",
                        weight=weight,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.VIEW_MODIFIER_PIPELINE,
                        pattern_category=PatternCategory.DECLARATIVE_DSL,
                        target_name=t.name,
                        target_kind="struct",
                        confidence=Confidence(score=weight, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections
