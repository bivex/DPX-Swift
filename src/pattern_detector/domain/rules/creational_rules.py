"""Creational design pattern detection rules for Swift."""

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


class SingletonSharedInstanceRule(BaseRule):
    """Detects thread-safe Swift Singletons (`static let shared = ...` with `private init()`)."""

    SINGLETON_PATTERN = re.compile(r"\bstatic\s+let\s+(shared|default|current|standard)\s*[:=]")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            has_static_shared = any(
                p.is_static and p.name in ("shared", "default", "current", "standard")
                for p in t.properties
            ) or bool(self.SINGLETON_PATTERN.search(t.raw_text or ""))

            if has_static_shared:
                has_private_init = any(m.name == "init" and m.is_private for m in t.methods) or ("private init(" in t.raw_text)
                score = 0.95 if has_private_init else 0.80
                evidences = [
                    Evidence(
                        rule_code="CREATIONAL_SINGLETON_SHARED_INSTANCE",
                        description=f"Type '{t.name}' defines thread-safe static shared singleton instance with {'private' if has_private_init else 'standard'} initialization",
                        weight=score,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.SINGLETON_SHARED_INSTANCE,
                        pattern_category=PatternCategory.CREATIONAL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=score, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class FactoryMethodRule(BaseRule):
    """Detects Factory Methods producing polymorphic or protocol-typed instances."""

    FACTORY_NAME_PATTERN = re.compile(r"\b(make[A-Z]\w+|create[A-Z]\w+|build[A-Z]\w+)\b")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            for m in t.methods:
                if self.FACTORY_NAME_PATTERN.search(m.name) and (m.is_static or "Factory" in t.name):
                    evidences = [
                        Evidence(
                            rule_code="CREATIONAL_FACTORY_METHOD",
                            description=f"Method '{m.name}' on '{t.name}' encapsulates object creation as a Factory Method returning '{m.return_type}'",
                            weight=0.85,
                            location=m.location,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.FACTORY_METHOD,
                            pattern_category=PatternCategory.CREATIONAL,
                            target_name=f"{t.name}.{m.name}",
                            target_kind="method",
                            confidence=Confidence(score=0.85, evidences=evidences),
                            primary_location=m.location,
                            evidences=evidences,
                        )
                    )
        return detections


class AbstractFactoryRule(BaseRule):
    """Detects Abstract Factory protocols declaring multiple factory creation methods."""

    FACTORY_NAME_PATTERN = re.compile(r"\b(make[A-Z]\w+|create[A-Z]\w+)\b")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for proto in model.protocols:
            creation_methods = [m for m in proto.methods if self.FACTORY_NAME_PATTERN.search(m.name)]
            if len(creation_methods) >= 2 or ("Factory" in proto.name and len(creation_methods) >= 1):
                score = 0.90 if len(creation_methods) >= 2 else 0.80
                evidences = [
                    Evidence(
                        rule_code="CREATIONAL_ABSTRACT_FACTORY",
                        description=f"Protocol '{proto.name}' defines Abstract Factory contract declaring {len(creation_methods)} creation method(s): {', '.join(m.name for m in creation_methods[:3])}",
                        weight=score,
                        location=proto.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.ABSTRACT_FACTORY,
                        pattern_category=PatternCategory.CREATIONAL,
                        target_name=proto.name,
                        target_kind="protocol",
                        confidence=Confidence(score=score, evidences=evidences),
                        primary_location=proto.location,
                        evidences=evidences,
                    )
                )
        return detections


class BuilderFluentChainRule(BaseRule):
    """Detects Builder pattern via fluent method chaining returning `Self` or mutating self."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            chain_methods = [
                m for m in t.methods
                if m.return_type in ("Self", t.name) and not m.is_static and (m.name.startswith("set") or m.name.startswith("with"))
            ]
            if len(chain_methods) >= 2 or "Builder" in t.name:
                score = 0.90 if "Builder" in t.name else 0.80
                evidences = [
                    Evidence(
                        rule_code="CREATIONAL_BUILDER_FLUENT_CHAIN",
                        description=f"Type '{t.name}' implements fluent Builder pattern chaining {len(chain_methods)} configuration step(s)",
                        weight=score,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.BUILDER_FLUENT_CHAIN,
                        pattern_category=PatternCategory.CREATIONAL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=score, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class PrototypeClonableRule(BaseRule):
    """Detects Prototype pattern (`NSCopying` or explicit `clone()` / `copy()` methods)."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            has_nscopying = "NSCopying" in t.inherited_types
            has_clone_method = any(m.name in ("clone", "copy", "deepCopy") for m in t.methods)
            if has_nscopying or has_clone_method:
                evidences = [
                    Evidence(
                        rule_code="CREATIONAL_PROTOTYPE_CLONABLE",
                        description=f"Type '{t.name}' implements Prototype pattern for instance replication",
                        weight=0.85,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.PROTOTYPE_CLONABLE,
                        pattern_category=PatternCategory.CREATIONAL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections
