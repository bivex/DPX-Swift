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


class ChainOfResponsibilityRule(BaseRule):
    """Detects Chain of Responsibility pattern holding `next` handler pointer."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            has_next = any(
                p.name in ("next", "nextHandler", "successor") or p.type_name in (t.name, f"{t.name}?") or "Handler" in p.type_name
                for p in t.properties
            )
            if (has_next and "Handler" in t.name) or "Chain" in t.name:
                evidences = [
                    Evidence(
                        rule_code="BEHAVIORAL_CHAIN_OF_RESPONSIBILITY",
                        description=f"Type '{t.name}' implements Chain of Responsibility delegating unhandled requests along handler chain",
                        weight=0.85,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.CHAIN_OF_RESPONSIBILITY,
                        pattern_category=PatternCategory.BEHAVIORAL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class IteratorProtocolRule(BaseRule):
    """Detects Iterator / Sequence traversal conforming to `IteratorProtocol` or `Sequence`."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            has_iterator = any(inh in ("IteratorProtocol", "Sequence", "AsyncSequence", "AsyncIteratorProtocol") for inh in t.inherited_types)
            has_next_method = any(m.name == "next" for m in t.methods)
            if has_iterator or has_next_method:
                evidences = [
                    Evidence(
                        rule_code="BEHAVIORAL_ITERATOR_PROTOCOL",
                        description=f"Type '{t.name}' conforms to Iterator / Sequence protocol for custom element traversal",
                        weight=0.90,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.ITERATOR_PROTOCOL,
                        pattern_category=PatternCategory.BEHAVIORAL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=0.90, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class MediatorCoordinatorRule(BaseRule):
    """Detects Mediator / Coordinator pattern orchestrating UI flow or subsystem interaction."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if "Coordinator" in t.name or "Mediator" in t.name:
                evidences = [
                    Evidence(
                        rule_code="BEHAVIORAL_MEDIATOR_COORDINATOR",
                        description=f"Type '{t.name}' acts as Mediator / Coordinator decoupling components and managing navigation flows",
                        weight=0.85,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.MEDIATOR_COORDINATOR,
                        pattern_category=PatternCategory.BEHAVIORAL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class InterpreterPatternRule(BaseRule):
    """Detects Interpreter pattern evaluating expression trees via `interpret(context:)` / `evaluate()`."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            has_interpret = any(m.name in ("interpret", "evaluate", "eval") for m in t.methods)
            if "Expression" in t.name or "AST" in t.name or (has_interpret and "Context" in t.raw_text):
                score = 0.90 if has_interpret else 0.80
                evidences = [
                    Evidence(
                        rule_code="BEHAVIORAL_INTERPRETER_EXPRESSION",
                        description=f"Type '{t.name}' implements Interpreter pattern evaluating domain expression AST",
                        weight=score,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.INTERPRETER_EXPRESSION_AST,
                        pattern_category=PatternCategory.BEHAVIORAL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=score, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class TemplateMethodRule(BaseRule):
    """Detects Template Method pattern defining algorithm skeleton with deferred step hooks."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.classes:
            has_template_methods = any(
                m.name.startswith("process") or m.name.startswith("execute") or m.name.startswith("handle")
                for m in t.methods
            )
            has_step_hooks = any(
                m.name.startswith("step") or m.name.startswith("before") or m.name.startswith("after") or m.name.startswith("on")
                for m in t.methods
            )
            if (has_template_methods and has_step_hooks) or "Template" in t.name:
                score = 0.85
                evidences = [
                    Evidence(
                        rule_code="BEHAVIORAL_TEMPLATE_METHOD",
                        description=f"Class '{t.name}' implements Template Method algorithm skeleton coordinating lifecycle step hooks",
                        weight=score,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.TEMPLATE_METHOD_ALGORITHM,
                        pattern_category=PatternCategory.BEHAVIORAL,
                        target_name=t.name,
                        target_kind="class",
                        confidence=Confidence(score=score, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class VisitorPatternRule(BaseRule):
    """Detects Visitor pattern via `accept(visitor:)` double dispatch."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            has_accept = any(m.name == "accept" and any("visitor" in p[0].lower() or "Visitor" in p[1] for p in m.parameters) for m in t.methods)
            if has_accept or "Visitor" in t.name:
                score = 0.90 if has_accept else 0.80
                evidences = [
                    Evidence(
                        rule_code="BEHAVIORAL_VISITOR_PATTERN",
                        description=f"Type '{t.name}' implements Visitor pattern enabling double dispatch operations",
                        weight=score,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.VISITOR_DOUBLE_DISPATCH,
                        pattern_category=PatternCategory.BEHAVIORAL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=score, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections
