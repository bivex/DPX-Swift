"""Protocol-Oriented Programming (POP) rules for Swift."""

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


class ProtocolExtensionDefaultImplRule(BaseRule):
    """Detects protocol extensions providing default implementations (POP mixin)."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        protocols_by_name = {p.name: p for p in model.protocols}

        for ext in model.extensions:
            target = ext.extension_target or ext.name
            if target in protocols_by_name or any(p.name == target for p in model.protocols):
                if ext.methods:
                    evidences = [
                        Evidence(
                            rule_code="POP_PROTOCOL_EXTENSION_DEFAULT_IMPL",
                            description=f"Extension on protocol '{target}' provides default implementation for {len(ext.methods)} method(s): {', '.join(m.name for m in ext.methods[:3])}",
                            weight=0.90,
                            location=ext.location,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.PROTOCOL_EXTENSION_DEFAULT_IMPL,
                            pattern_category=PatternCategory.PROTOCOL_ORIENTED,
                            target_name=target,
                            target_kind="protocol_extension",
                            confidence=Confidence(score=0.90, evidences=evidences),
                            primary_location=ext.location,
                            evidences=evidences,
                        )
                    )
        return detections


class ProtocolCompositionRule(BaseRule):
    """Detects protocol composition using compound protocol types (e.g. `any A & B` or `some A & B`)."""

    COMPOSITION_PATTERN = re.compile(r"(?:any|some|typealias\s+\w+\s*=)?\s*([A-Z]\w+)\s*&\s*([A-Z]\w+)")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for f in model.files:
            for line_idx, line in enumerate(f.lines, 1):
                match = self.COMPOSITION_PATTERN.search(line)
                if match:
                    p1, p2 = match.group(1), match.group(2)
                    evidences = [
                        Evidence(
                            rule_code="POP_PROTOCOL_COMPOSITION",
                            description=f"Protocol composition compound type '{p1} & {p2}' detected, adhering to interface segregation and POP",
                            weight=0.85,
                            location=f.types[0].location if f.types else None,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.PROTOCOL_COMPOSITION,
                            pattern_category=PatternCategory.PROTOCOL_ORIENTED,
                            target_name=f"{p1} & {p2}",
                            target_kind="protocol_composition",
                            confidence=Confidence(score=0.85, evidences=evidences),
                            primary_location=f.types[0].location if f.types else None,
                            evidences=evidences,
                        )
                    )
        return detections


class AssociatedTypePatRule(BaseRule):
    """Detects protocols with associated types (PATs)."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for proto in model.protocols:
            if proto.associated_types:
                evidences = [
                    Evidence(
                        rule_code="POP_ASSOCIATED_TYPE_PAT",
                        description=f"Protocol '{proto.name}' defines associated type(s) ({', '.join(proto.associated_types)}), enabling generic protocol abstraction",
                        weight=0.90,
                        location=proto.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.ASSOCIATED_TYPE_PAT,
                        pattern_category=PatternCategory.PROTOCOL_ORIENTED,
                        target_name=proto.name,
                        target_kind="protocol",
                        confidence=Confidence(score=0.90, evidences=evidences),
                        primary_location=proto.location,
                        evidences=evidences,
                    )
                )
        return detections


class OpaqueReturnTypeRule(BaseRule):
    """Detects opaque return types (`some Protocol`)."""

    OPAQUE_PATTERN = re.compile(r"->\s*some\s+([A-Z]\w+)")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for method in model.all_methods:
            match = self.OPAQUE_PATTERN.search(method.raw_text or "")
            if match:
                proto_name = match.group(1)
                evidences = [
                    Evidence(
                        rule_code="POP_OPAQUE_RETURN_TYPE",
                        description=f"Method '{method.name}' returns opaque type 'some {proto_name}', hiding concrete type implementation while preserving type identity",
                        weight=0.85,
                        location=method.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.OPAQUE_RETURN_TYPE,
                        pattern_category=PatternCategory.PROTOCOL_ORIENTED,
                        target_name=method.name,
                        target_kind="method",
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=method.location,
                        evidences=evidences,
                    )
                )
        return detections


class ExistentialAnyBoxRule(BaseRule):
    """Detects existential type boxes (`any Protocol`)."""

    EXISTENTIAL_PATTERN = re.compile(r"\bany\s+([A-Z]\w+)")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        seen_targets: set[str] = set()
        for f in model.files:
            for match in self.EXISTENTIAL_PATTERN.finditer(f.raw_content):
                proto_name = match.group(1)
                if proto_name in ("View", "Error", "Codable", "Equatable", "Hashable") or proto_name in seen_targets:
                    continue
                seen_targets.add(proto_name)
                evidences = [
                    Evidence(
                        rule_code="POP_EXISTENTIAL_ANY_BOX",
                        description=f"Explicit existential container 'any {proto_name}' used for dynamic runtime polymorphism",
                        weight=0.80,
                        location=f.types[0].location if f.types else None,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.EXISTENTIAL_ANY_BOX,
                        pattern_category=PatternCategory.PROTOCOL_ORIENTED,
                        target_name=f"any {proto_name}",
                        target_kind="existential_type",
                        confidence=Confidence(score=0.80, evidences=evidences),
                        primary_location=f.types[0].location if f.types else None,
                        evidences=evidences,
                    )
                )
        return detections
