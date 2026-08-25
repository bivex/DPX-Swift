"""Behavioral design pattern detection rules for Swift."""

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


class DelegatePatternWeakRule(BaseRule):
    """Detects Weak Delegate pattern (`weak var delegate: SomeDelegate?`)."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            for p in t.properties:
                if "delegate" in p.name.lower() and p.is_weak:
                    evidences = [
                        Evidence(
                            rule_code="BEHAVIORAL_DELEGATE_PATTERN_WEAK",
                            description=f"Property '{t.name}.{p.name}' implements safe Weak Delegate pattern avoiding retain cycles",
                            weight=0.90,
                            location=p.location or t.location,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.DELEGATE_PATTERN_WEAK,
                            pattern_category=PatternCategory.BEHAVIORAL,
                            target_name=f"{t.name}.{p.name}",
                            target_kind="property",
                            confidence=Confidence(score=0.90, evidences=evidences),
                            primary_location=p.location or t.location,
                            evidences=evidences,
                        )
                    )
        return detections


class ObserverCombinePublishedRule(BaseRule):
    """Detects Combine reactive observer pattern (`@Published`, `PassthroughSubject`, `ObservableObject`)."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            is_observable = "ObservableObject" in t.inherited_types or any("@Observable" in attr for attr in t.attributes)
            published_props = [
                p for p in t.properties
                if any("@Published" in attr for attr in p.attributes) or "Subject" in p.type_name
            ]
            if is_observable or published_props:
                score = 0.95 if published_props and is_observable else 0.85
                evidences = [
                    Evidence(
                        rule_code="BEHAVIORAL_OBSERVER_COMBINE",
                        description=f"Type '{t.name}' acts as Reactive Observer Subject with {len(published_props)} @Published / Subject property(ies)",
                        weight=score,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.OBSERVER_COMBINE_PUBLISHED,
                        pattern_category=PatternCategory.BEHAVIORAL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=score, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class StrategyProtocolInjectionRule(BaseRule):
    """Detects Strategy pattern via protocol-typed dependency injection."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if t.kind in ("class", "struct", "actor"):
                strategy_props = [
                    p for p in t.properties
                    if "Strategy" in p.type_name or "Strategy" in p.name or "Formatter" in p.type_name or "Validator" in p.type_name
                ]
                if strategy_props or "Strategy" in t.name:
                    score = 0.90 if "Strategy" in t.name else 0.80
                    evidences = [
                        Evidence(
                            rule_code="BEHAVIORAL_STRATEGY_INJECTION",
                            description=f"Type '{t.name}' injects interchangeable Strategy algorithm via property '{strategy_props[0].name if strategy_props else 'strategy'}'",
                            weight=score,
                            location=t.location,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.STRATEGY_PROTOCOL_INJECTION,
                            pattern_category=PatternCategory.BEHAVIORAL,
                            target_name=t.name,
                            target_kind=t.kind,
                            confidence=Confidence(score=score, evidences=evidences),
                            primary_location=t.location,
                            evidences=evidences,
                        )
                    )
        return detections


class StateEnumAssociatedValuesRule(BaseRule):
    """Detects State Machine pattern modeled via Swift enums with associated values."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if t.kind == "enum" and ("State" in t.name or "Status" in t.name or "Phase" in t.name):
                has_associated = "(" in (t.raw_text or "")
                score = 0.90 if has_associated else 0.80
                evidences = [
                    Evidence(
                        rule_code="BEHAVIORAL_STATE_ENUM",
                        description=f"Enum '{t.name}' models type-safe State Machine with associated lifecycle states",
                        weight=score,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.STATE_ENUM_ASSOCIATED_VALUES,
                        pattern_category=PatternCategory.BEHAVIORAL,
                        target_name=t.name,
                        target_kind="enum",
                        confidence=Confidence(score=score, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class CommandEncapsulationRule(BaseRule):
    """Detects Command pattern encapsulating operations into executable command objects."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if "Command" in t.name or any("Command" in inh for inh in t.inherited_types):
                has_execute = any(m.name in ("execute", "run", "perform", "undo") for m in t.methods)
                if has_execute or "Command" in t.name:
                    score = 0.90 if has_execute else 0.80
                    evidences = [
                        Evidence(
                            rule_code="BEHAVIORAL_COMMAND_ENCAPSULATION",
                            description=f"Type '{t.name}' encapsulates executable operation as a Command object",
                            weight=score,
                            location=t.location,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.COMMAND_ENCAPSULATION,
                            pattern_category=PatternCategory.BEHAVIORAL,
                            target_name=t.name,
                            target_kind=t.kind,
                            confidence=Confidence(score=score, evidences=evidences),
                            primary_location=t.location,
                            evidences=evidences,
                        )
                    )
        return detections


class MementoCodableSnapshotRule(BaseRule):
    """Detects Memento pattern using `Codable` snapshot and state encoding."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if "Snapshot" in t.name or "Memento" in t.name or ("Codable" in t.inherited_types and any(m.name in ("createSnapshot", "restoreSnapshot", "saveState") for m in t.methods)):
                evidences = [
                    Evidence(
                        rule_code="BEHAVIORAL_MEMENTO_SNAPSHOT",
                        description=f"Type '{t.name}' captures and externalizes object state as a Memento Snapshot",
                        weight=0.85,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.MEMENTO_CODABLE_SNAPSHOT,
                        pattern_category=PatternCategory.BEHAVIORAL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections
