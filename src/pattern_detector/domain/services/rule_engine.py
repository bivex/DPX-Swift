"""Domain service executing pattern detection rules against Swift CodeModel."""

from __future__ import annotations

from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection
from pattern_detector.domain.rules.base import BaseRule


class RuleEngineService:
    """Evaluates rules against a CodeModel with confidence thresholding and deduplication."""

    def __init__(self, rules: list[BaseRule]) -> None:
        self.rules = rules

    def evaluate(
        self,
        model: CodeModel,
        min_confidence: float = 0.0,
        enabled_patterns: list[str] | None = None,
    ) -> list[Detection]:
        detections: list[Detection] = []
        enabled_set = set(enabled_patterns) if enabled_patterns else None

        for rule in self.rules:
            rule_detections = rule.evaluate(model)
            for d in rule_detections:
                if d.confidence.score < min_confidence:
                    continue
                if enabled_set and d.pattern_type.value not in enabled_set:
                    continue
                detections.append(d)

        return detections
