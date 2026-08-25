"""Structural design pattern detection rules for Swift."""

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


class AdapterViaExtensionRule(BaseRule):
    """Detects Adapter pattern via retroactive extension conforming an existing type to a domain protocol."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for ext in model.extensions:
            target = ext.extension_target or ext.name
            if ext.inherited_types:
                proto_conformance = [inh for inh in ext.inherited_types if inh not in ("Identifiable", "Equatable", "Hashable", "Sendable")]
                if proto_conformance:
                    evidences = [
                        Evidence(
                            rule_code="STRUCTURAL_ADAPTER_VIA_EXTENSION",
                            description=f"Extension adapts type '{target}' to protocol(s) '{', '.join(proto_conformance)}', implementing Retroactive Adapter pattern",
                            weight=0.85,
                            location=ext.location,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.ADAPTER_VIA_EXTENSION,
                            pattern_category=PatternCategory.STRUCTURAL,
                            target_name=f"{target}:{','.join(proto_conformance)}",
                            target_kind="extension_adapter",
                            confidence=Confidence(score=0.85, evidences=evidences),
                            primary_location=ext.location,
                            evidences=evidences,
                        )
                    )
        return detections


class BridgePatternRule(BaseRule):
    """Detects Bridge pattern decoupling abstraction from implementor protocol."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if "Bridge" in t.name or any("Implementor" in p.type_name or "Renderer" in p.type_name or "Driver" in p.type_name for p in t.properties):
                impl_props = [p for p in t.properties if any(k in p.type_name for k in ("Implementor", "Renderer", "Driver", "Engine"))]
                if impl_props or "Bridge" in t.name:
                    evidences = [
                        Evidence(
                            rule_code="STRUCTURAL_BRIDGE_PATTERN",
                            description=f"Type '{t.name}' decouples abstraction from implementor via '{impl_props[0].name if impl_props else 'implementor'}'",
                            weight=0.85,
                            location=t.location,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.BRIDGE_IMPLEMENTOR,
                            pattern_category=PatternCategory.STRUCTURAL,
                            target_name=t.name,
                            target_kind=t.kind,
                            confidence=Confidence(score=0.85, evidences=evidences),
                            primary_location=t.location,
                            evidences=evidences,
                        )
                    )
        return detections


class DecoratorWrapperRule(BaseRule):
    """Detects Decorator / Wrapper pattern holding an underlying wrapped instance."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if "Decorator" in t.name or "Wrapper" in t.name:
                wrapped_props = [
                    p for p in t.properties
                    if p.name in ("wrapped", "decoratee", "underlying", "base") or any(inh in p.type_name for inh in t.inherited_types)
                ]
                if wrapped_props:
                    evidences = [
                        Evidence(
                            rule_code="STRUCTURAL_DECORATOR_WRAPPER",
                            description=f"Type '{t.name}' decorates underlying '{wrapped_props[0].name}: {wrapped_props[0].type_name}' instance",
                            weight=0.85,
                            location=t.location,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.DECORATOR_WRAPPER,
                            pattern_category=PatternCategory.STRUCTURAL,
                            target_name=t.name,
                            target_kind=t.kind,
                            confidence=Confidence(score=0.85, evidences=evidences),
                            primary_location=t.location,
                            evidences=evidences,
                        )
                    )
        return detections


class CompositeViewHierarchyRule(BaseRule):
    """Detects Composite pattern in SwiftUI views and hierarchical trees."""

    COMPOSITE_PATTERN = re.compile(r"@ViewBuilder\s+(?:let|var)?\s*content\s*:\s*\(\)\s*->\s*Content")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.structs:
            if "View" in t.inherited_types:
                has_generic_content = any("Content" in g for g in t.generic_parameters)
                has_view_builder_prop = any(
                    self.COMPOSITE_PATTERN.search(p.raw_text or "") or "@ViewBuilder" in " ".join(p.attributes)
                    for p in t.properties
                )
                if has_generic_content or has_view_builder_prop or "Composite" in t.name:
                    evidences = [
                        Evidence(
                            rule_code="STRUCTURAL_COMPOSITE_VIEW",
                            description=f"SwiftUI View '{t.name}' implements Composite pattern hosting nested child view hierarchy via @ViewBuilder",
                            weight=0.85,
                            location=t.location,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.COMPOSITE_VIEW_HIERARCHY,
                            pattern_category=PatternCategory.STRUCTURAL,
                            target_name=t.name,
                            target_kind="struct",
                            confidence=Confidence(score=0.85, evidences=evidences),
                            primary_location=t.location,
                            evidences=evidences,
                        )
                    )
        return detections


class FacadeServiceRule(BaseRule):
    """Detects Facade Service orchestrating multiple repositories or subsystem clients."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if t.kind in ("class", "struct", "actor") and ("Facade" in t.name or "Coordinator" in t.name or "Manager" in t.name):
                subsystem_deps = [
                    p for p in t.properties
                    if any(suffix in p.type_name for suffix in ("Repository", "Service", "Client", "Store", "Provider", "Engine"))
                ]
                if len(subsystem_deps) >= 2 or "Facade" in t.name:
                    score = 0.90 if "Facade" in t.name else 0.80
                    evidences = [
                        Evidence(
                            rule_code="STRUCTURAL_FACADE_SERVICE",
                            description=f"Type '{t.name}' coordinates {len(subsystem_deps)} subsystem dependencies as a unified Facade",
                            weight=score,
                            location=t.location,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.FACADE_SERVICE,
                            pattern_category=PatternCategory.STRUCTURAL,
                            target_name=t.name,
                            target_kind=t.kind,
                            confidence=Confidence(score=score, evidences=evidences),
                            primary_location=t.location,
                            evidences=evidences,
                        )
                    )
        return detections


class FlyweightPatternRule(BaseRule):
    """Detects Flyweight pattern sharing instances via dictionary pool or factory cache."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if "Flyweight" in t.name or (any("cache" in p.name.lower() or "pool" in p.name.lower() for p in t.properties) and any(m.name.startswith("get") or m.name.startswith("make") for m in t.methods)):
                evidences = [
                    Evidence(
                        rule_code="STRUCTURAL_FLYWEIGHT_CACHE",
                        description=f"Type '{t.name}' shares fine-grained instances via Flyweight pooling cache",
                        weight=0.85,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.FLYWEIGHT_CACHE,
                        pattern_category=PatternCategory.STRUCTURAL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class ProxyPatternRule(BaseRule):
    """Detects Proxy pattern controlling access to a remote/virtual real subject."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if "Proxy" in t.name:
                evidences = [
                    Evidence(
                        rule_code="STRUCTURAL_PROXY_PATTERN",
                        description=f"Type '{t.name}' acts as surrogate Proxy controlling access to underlying target",
                        weight=0.85,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.PROXY_VIRTUAL_OR_REMOTE,
                        pattern_category=PatternCategory.STRUCTURAL,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections
