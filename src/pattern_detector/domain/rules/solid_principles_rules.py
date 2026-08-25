"""SOLID principles and clean code quality rules for Swift."""

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


class MassiveViewControllerSrpRule(BaseRule):
    """Detects Massive View Controllers / God Classes violating Single Responsibility Principle."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.classes:
            if t.line_count >= 250 or len(t.methods) >= 14 or ("ViewController" in t.name and len(t.methods) >= 10):
                score = 0.90 if t.line_count >= 300 else 0.80
                evidences = [
                    Evidence(
                        rule_code="SRP_MASSIVE_VIEW_CONTROLLER",
                        description=f"Type '{t.name}' is a Massive View Controller / God Class ({t.line_count} lines, {len(t.methods)} methods, {len(t.properties)} properties) violating SRP",
                        weight=score,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.MASSIVE_VIEW_CONTROLLER_SRP,
                        pattern_category=PatternCategory.PRINCIPLE,
                        target_name=t.name,
                        target_kind="class",
                        confidence=Confidence(score=score, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class FatProtocolIspRule(BaseRule):
    """Detects Fat Protocols declaring too many required methods violating ISP."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for proto in model.protocols:
            if len(proto.methods) >= 8:
                evidences = [
                    Evidence(
                        rule_code="ISP_FAT_PROTOCOL",
                        description=f"Protocol '{proto.name}' is a Fat Protocol declaring {len(proto.methods)} required methods; consider splitting into smaller role protocols",
                        weight=0.85,
                        location=proto.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.FAT_PROTOCOL_ISP,
                        pattern_category=PatternCategory.PRINCIPLE,
                        target_name=proto.name,
                        target_kind="protocol",
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=proto.location,
                        evidences=evidences,
                    )
                )
        return detections


class DynamicCastAsCascadeOcpRule(BaseRule):
    """Detects dynamic downcasting cascades (`as?` / `is`) violating Open-Closed Principle."""

    DOWNCAST_CASCADE_PATTERN = re.compile(r"\b(?:if\s+let\s+\w+\s*=\s*\w+\s+as\?|guard\s+let\s+\w+\s*=\s*\w+\s+as\?|\bcase\s+let\s+\w+\s+as\b)")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for m in model.all_methods:
            matches = len(self.DOWNCAST_CASCADE_PATTERN.findall(m.body or ""))
            if matches >= 3:
                evidences = [
                    Evidence(
                        rule_code="OCP_DYNAMIC_CAST_CASCADE",
                        description=f"Method '{m.name}' contains {matches} dynamic downcasts ('as?'); replace with polymorphic protocol dispatch to satisfy OCP",
                        weight=0.85,
                        location=m.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.DYNAMIC_CAST_AS_CASCADE_OCP,
                        pattern_category=PatternCategory.PRINCIPLE,
                        target_name=m.name,
                        target_kind="method",
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=m.location,
                        evidences=evidences,
                    )
                )
        return detections


class KissCyclomaticComplexityRule(BaseRule):
    """Detects functions with excessive cyclomatic complexity."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for m in model.all_methods:
            if m.branch_count >= 9:
                evidences = [
                    Evidence(
                        rule_code="KISS_CYCLOMATIC_COMPLEXITY",
                        description=f"Method '{m.name}' has high cyclomatic complexity ({m.branch_count} branch points), violating KISS",
                        weight=0.88,
                        location=m.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.KISS_CYCLOMATIC_COMPLEXITY,
                        pattern_category=PatternCategory.PRINCIPLE,
                        target_name=m.name,
                        target_kind="method",
                        confidence=Confidence(score=0.88, evidences=evidences),
                        primary_location=m.location,
                        evidences=evidences,
                    )
                )
        return detections


class KissLongParameterListRule(BaseRule):
    """Detects functions/initializers with excessive parameters."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for m in model.all_methods:
            if len(m.parameters) >= 5:
                evidences = [
                    Evidence(
                        rule_code="KISS_LONG_PARAMETER_LIST",
                        description=f"Method '{m.name}' accepts {len(m.parameters)} parameters; consider using a configuration struct or Parameter Object",
                        weight=0.85,
                        location=m.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.KISS_LONG_PARAMETER_LIST,
                        pattern_category=PatternCategory.PRINCIPLE,
                        target_name=m.name,
                        target_kind="method",
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=m.location,
                        evidences=evidences,
                    )
                )
        return detections


class DryDuplicateLogicRule(BaseRule):
    """Detects duplicated identical algorithmic blocks across methods."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        body_map: dict[str, list[tuple[str, str]]] = {}
        for f in model.files:
            for t in f.types:
                for m in t.methods:
                    cleaned = re.sub(r"\s+", " ", m.body).strip()
                    if len(cleaned) >= 50:
                        body_map.setdefault(cleaned, []).append((t.name, m.name))

        for body, occurrences in body_map.items():
            if len(occurrences) >= 2:
                names = [f"{cls}.{fn}" for cls, fn in occurrences]
                evidences = [
                    Evidence(
                        rule_code="DRY_DUPLICATE_CODE",
                        description=f"Identical logic duplicated across {len(occurrences)} method(s): {', '.join(names[:3])}",
                        weight=0.80,
                        location=None,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.DRY_DUPLICATE_LOGIC,
                        pattern_category=PatternCategory.PRINCIPLE,
                        target_name=names[0],
                        target_kind="method",
                        confidence=Confidence(score=0.80, evidences=evidences),
                        primary_location=None,
                        evidences=evidences,
                    )
                )
        return detections


class DemeterLawTrainWreckRule(BaseRule):
    """Detects Law of Demeter violations (deep object navigation dot chains `a.b.c.d.e`)."""

    DOT_CHAIN_PATTERN = re.compile(r"\b[a-zA-Z_]\w*\.[a-zA-Z_]\w*\.[a-zA-Z_]\w*\.[a-zA-Z_]\w*\.[a-zA-Z_]\w*\b")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for m in model.all_methods:
            matches = self.DOT_CHAIN_PATTERN.findall(m.body or "")
            if matches:
                evidences = [
                    Evidence(
                        rule_code="DEMETER_LAW_TRAIN_WRECK",
                        description=f"Method '{m.name}' violates Law of Demeter with deep navigation chain: '{matches[0]}'",
                        weight=0.80,
                        location=m.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.DEMETER_LAW_TRAIN_WRECK,
                        pattern_category=PatternCategory.PRINCIPLE,
                        target_name=m.name,
                        target_kind="method",
                        confidence=Confidence(score=0.80, evidences=evidences),
                        primary_location=m.location,
                        evidences=evidences,
                    )
                )
        return detections
