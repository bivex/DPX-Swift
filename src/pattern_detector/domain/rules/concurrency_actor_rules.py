"""Swift Concurrency & Actor Model detection rules."""

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


class ActorModelIsolationRule(BaseRule):
    """Detects `actor` declarations providing data-race-free state isolation."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for actor in model.actors:
            evidences = [
                Evidence(
                    rule_code="CONCURRENCY_ACTOR_ISOLATION",
                    description=f"Actor '{actor.name}' guarantees data isolation and thread safety via the Swift Actor model",
                    weight=0.95,
                    location=actor.location,
                )
            ]
            detections.append(
                Detection(
                    pattern_type=PatternType.ACTOR_MODEL_ISOLATION,
                    pattern_category=PatternCategory.CONCURRENCY,
                    target_name=actor.name,
                    target_kind="actor",
                    confidence=Confidence(score=0.95, evidences=evidences),
                    primary_location=actor.location,
                    evidences=evidences,
                )
            )
        return detections


class MainActorUiBindingRule(BaseRule):
    """Detects `@MainActor` annotations binding classes/methods to the main UI thread."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if any("@MainActor" in attr for attr in t.attributes):
                evidences = [
                    Evidence(
                        rule_code="CONCURRENCY_MAIN_ACTOR_BINDING",
                        description=f"Type '{t.name}' is bound to @MainActor ensuring all state updates and UI interactions dispatch safely on the main thread",
                        weight=0.95,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.MAIN_ACTOR_UI_BINDING,
                        pattern_category=PatternCategory.CONCURRENCY,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=0.95, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections


class TaskGroupConcurrencyRule(BaseRule):
    """Detects structured concurrency task groups (`withTaskGroup` / `withThrowingTaskGroup`)."""

    TASK_GROUP_PATTERN = re.compile(r"\b(withTaskGroup|withThrowingTaskGroup|withDiscardingTaskGroup)\b")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for method in model.all_methods:
            match = self.TASK_GROUP_PATTERN.search(method.body or "")
            if match:
                tg_func = match.group(1)
                evidences = [
                    Evidence(
                        rule_code="CONCURRENCY_TASK_GROUP",
                        description=f"Method '{method.name}' utilizes structured concurrency '{tg_func}' for dynamic parallel task fan-out and collection",
                        weight=0.90,
                        location=method.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.TASK_GROUP_CONCURRENCY,
                        pattern_category=PatternCategory.CONCURRENCY,
                        target_name=method.name,
                        target_kind="method",
                        confidence=Confidence(score=0.90, evidences=evidences),
                        primary_location=method.location,
                        evidences=evidences,
                    )
                )
        return detections


class AsyncStreamSequenceRule(BaseRule):
    """Detects `AsyncStream`, `AsyncThrowingStream`, or `AsyncSequence` conformance."""

    ASYNC_STREAM_PATTERN = re.compile(r"\b(AsyncStream|AsyncThrowingStream|AsyncSequence|AsyncIteratorProtocol)\b")

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if any(self.ASYNC_STREAM_PATTERN.search(inh) for inh in t.inherited_types):
                evidences = [
                    Evidence(
                        rule_code="CONCURRENCY_ASYNC_SEQUENCE",
                        description=f"Type '{t.name}' conforms to AsyncSequence/AsyncStream for asynchronous reactive event streaming",
                        weight=0.90,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.ASYNC_STREAM_SEQUENCE,
                        pattern_category=PatternCategory.CONCURRENCY,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=0.90, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        for method in model.all_methods:
            if self.ASYNC_STREAM_PATTERN.search(method.return_type or "") or self.ASYNC_STREAM_PATTERN.search(method.body or ""):
                evidences = [
                    Evidence(
                        rule_code="CONCURRENCY_ASYNC_STREAM_CREATOR",
                        description=f"Method '{method.name}' creates or returns an AsyncStream for streaming asynchronous events with backpressure",
                        weight=0.85,
                        location=method.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.ASYNC_STREAM_SEQUENCE,
                        pattern_category=PatternCategory.CONCURRENCY,
                        target_name=method.name,
                        target_kind="method",
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=method.location,
                        evidences=evidences,
                    )
                )
        return detections


class SendableThreadSafetyRule(BaseRule):
    """Detects `Sendable` protocol conformance and `@Sendable` closures."""

    def evaluate(self, model: CodeModel) -> list[Detection]:
        detections: list[Detection] = []
        for t in model.all_types:
            if "Sendable" in t.inherited_types or any("@Sendable" in attr for attr in t.attributes):
                evidences = [
                    Evidence(
                        rule_code="CONCURRENCY_SENDABLE_CONFORMANCE",
                        description=f"Type '{t.name}' conforms to Sendable, establishing thread-safe concurrency boundaries across actors",
                        weight=0.85,
                        location=t.location,
                    )
                ]
                detections.append(
                    Detection(
                        pattern_type=PatternType.SENDABLE_THREAD_SAFETY,
                        pattern_category=PatternCategory.CONCURRENCY,
                        target_name=t.name,
                        target_kind=t.kind,
                        confidence=Confidence(score=0.85, evidences=evidences),
                        primary_location=t.location,
                        evidences=evidences,
                    )
                )
        return detections
