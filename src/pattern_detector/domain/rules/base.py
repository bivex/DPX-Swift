"""Base class for Swift pattern detection rules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pattern_detector.domain.code_model import CodeModel
from pattern_detector.domain.detection import Detection


class BaseRule(ABC):
    """Abstract base class for all Swift pattern detection and quality rules."""

    @abstractmethod
    def evaluate(self, model: CodeModel) -> list[Detection]:
        """Evaluate rule against the parsed CodeModel and produce detections."""
        ...
