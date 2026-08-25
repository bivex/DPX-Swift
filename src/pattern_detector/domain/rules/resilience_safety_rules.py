"""Resilience, Memory Safety & Hazard detection rules for Swift."""

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
    SourceLocation,
)


class RetainCycleStrongSelfRule(BaseRule):
    """Detects escaping closures or Task blocks strongly capturing `self` without `[weak self]`."""

    ESCAPING_CLOSURE_PATTERN = re.compile(
        r"(?:Task(?:\.detached)?|\.sink|\.bind|\.onReceive|\.subscribe|dispatchQueue\.async|DispatchQueue\.\w+\.async)\s*\{\s*(?!\[weak\s+self|\[unowned\s+self)(?:[^}]*?\bself\.\w+)"
    )

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for f in model.files:
            for line_idx, line in enumerate(f.lines, 1):
                if ("Task {" in line or ".sink {" in line or "DispatchQueue." in line) and "[weak self]" not in line and "[unowned self]" not in line:
                    # check next few lines for self. usage
                    window = "\n".join(f.lines[line_idx - 1 : min(len(f.lines), line_idx + 15)])
                    if "self." in window and "[weak self]" not in window and "[unowned self]" not in window:
                        loc = SourceLocation(file_path=f.file_path, line=line_idx, column=1)
                        evidences = [
                            Evidence(
                                rule_code="HAZARD_RETAIN_CYCLE_STRONG_SELF",
                                description="Escaping closure or async Task strongly captures 'self' without '[weak self]', risking ARC memory leak / retain cycle",
                                weight=0.85,
                                location=loc,
                            )
                        ]
                        detections.append(
                            Detection(
                                pattern_type=PatternType.RETAIN_CYCLE_STRONG_SELF,
                                pattern_category=PatternCategory.RESILIENCE,
                                target_name=f"{f.file_path}:{line_idx}",
                                target_kind="closure",
                                confidence=Confidence(score=0.85, evidences=evidences),
                                primary_location=loc,
                                evidences=evidences,
                            )
                        )
        return detections


class ForceUnwrappingHazardRule(BaseRule):
    """Detects unsafe force-unwrapping (`!`, `as!`, `try!`) causing runtime fatal crashes."""

    FORCE_UNWRAP_PATTERN = re.compile(r"(\w+!\b|\bas!\b|\btry!\b)")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for f in model.files:
            force_occurrences: list[tuple[int, str]] = []
            for line_idx, line in enumerate(f.lines, 1):
                trimmed = line.strip()
                if trimmed.startswith("//") or trimmed.startswith("/*") or trimmed.startswith("*"):
                    continue
                match = self.FORCE_UNWRAP_PATTERN.search(trimmed)
                if match:
                    force_occurrences.append((line_idx, match.group(1)))

            if len(force_occurrences) >= 3:
                loc = SourceLocation(file_path=f.file_path, line=force_occurrences[0][0], column=1)
                evidences = [
                    Evidence(
                        rule_code="HAZARD_FORCE_UNWRAPPING",
                        description=f"Multiple force-unwraps/force-casts ({len(force_occurrences)} occurrences: {', '.join(k for _, k in force_occurrences[:4])}) risking fatal runtime crashes",
                        weight=0.85,
                        location=loc,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.FORCE_UNWRAPPING_HAZARD,
                        pattern_category=PatternCategory.RESILIENCE,
                        target_name=f.file_path,
                        target_kind="file",
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=loc,
                        evidences=evidences,
                    )
                )
        return detections


class StrongDelegateRetainCycleRule(BaseRule):
    """Detects delegate property without `weak` modifier causing memory leaks."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.classes:
            for p in t.properties:
                if "delegate" in p.name.lower() and not p.is_weak and not p.is_let and p.type_name.endswith("?"):
                    evidences = [
                        Evidence(
                            rule_code="HAZARD_STRONG_DELEGATE",
                            description=f"Delegate property '{t.name}.{p.name}' declared without 'weak' keyword, risking strong reference retain cycle",
                            weight=0.90,
                            location=p.location or t.location,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.STRONG_DELEGATE_RETAIN_CYCLE,
                            pattern_category=PatternCategory.RESILIENCE,
                            target_name=f"{t.name}.{p.name}",
                            target_kind="property",
                            confidence=Confidence(score=0.90, evidences=evidences),
                            primary_location=p.location or t.location,
                            evidences=evidences,
                        )
                    )
        return detections


class MainThreadBlockingCallRule(BaseRule):
    """Detects blocking synchronous calls (`Thread.sleep`, semaphore `wait()`) inside UI or `@MainActor` contexts."""

    BLOCKING_PATTERN = re.compile(r"\b(Thread\.sleep|usleep|sleep\(|\.wait\(\))\b")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            is_ui = any("@MainActor" in attr for attr in t.attributes) or "ViewController" in t.name or "View" in t.inherited_types
            for m in t.methods:
                if (is_ui or any("@MainActor" in attr for attr in m.attributes)) and self.BLOCKING_PATTERN.search(m.body or ""):
                    evidences = [
                        Evidence(
                            rule_code="HAZARD_MAIN_THREAD_BLOCKING",
                            description=f"Synchronous blocking call detected in main UI thread context '{t.name}.{m.name}', risking UI freeze (ANR)",
                            weight=0.90,
                            location=m.location or t.location,
                        )
                    ]
                    detections.append(
                        Detection(
                            pattern_type=PatternType.MAIN_THREAD_BLOCKING_CALL,
                            pattern_category=PatternCategory.RESILIENCE,
                            target_name=f"{t.name}.{m.name}",
                            target_kind="method",
                            confidence=Confidence(score=0.90, evidences=evidences),
                            primary_location=m.location or t.location,
                            evidences=evidences,
                        )
                    )
        return detections


class UnhandledTrySwallowRule(BaseRule):
    """Detects `try?` in critical methods silently swallowing domain errors."""

    TRY_SWALLOW_PATTERN = re.compile(r"\btry\?\s+\w+")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for f in model.files:
            swallow_count = len(self.TRY_SWALLOW_PATTERN.findall(f.raw_content))
            if swallow_count >= 3:
                loc = f.types[0].location if f.types else None
                evidences = [
                    Evidence(
                        rule_code="HAZARD_SILENT_ERROR_SWALLOW",
                        description=f"Frequent silent error discarding via 'try?' ({swallow_count} instances) in '{f.file_path}', obscuring root causes",
                        weight=0.80,
                        location=loc,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.UNHANDLED_TRY_SWALLOW,
                        pattern_category=PatternCategory.RESILIENCE,
                        target_name=f.file_path,
                        target_kind="file",
                        confidence=Confidence(score=0.80, evidences=evidences),
                        primary_location=loc,
                        evidences=evidences,
                    )
                )
        return detections
