"""Detection and Report domain entities for Swift Pattern Detector."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pattern_detector.domain.pattern import PATTERN_CATALOG
from pattern_detector.domain.value_objects import (
    Confidence,
    ConfidenceLevel,
    Evidence,
    PatternCategory,
    PatternType,
    SourceLocation,
)


@dataclass
class Detection:
    """Represents an identified Swift design pattern, idiom, or quality violation."""

    pattern_type: PatternType
    pattern_category: PatternCategory
    target_name: str
    target_kind: str  # "class", "struct", "protocol", "actor", "method", "property", "extension"
    confidence: Confidence
    primary_location: SourceLocation | None = None
    evidences: list[Evidence] = field(default_factory=list)
    related_locations: list[SourceLocation] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    summary: str = ""

    def __post_init__(self) -> None:
        if not self.summary:
            if self.evidences:
                self.summary = self.evidences[0].description
            else:
                pdef = PATTERN_CATALOG.get(self.pattern_type)
                pname = pdef.name if pdef else self.pattern_type.value
                self.summary = f"Detected {pname} on {self.target_kind} '{self.target_name}'"
        if not self.evidences and self.confidence.evidences:
            self.evidences = list(self.confidence.evidences)

    @property
    def level(self) -> ConfidenceLevel:
        return self.confidence.level

    def to_dict(self) -> dict[str, object]:
        return {
            "pattern_type": self.pattern_type.value,
            "pattern_category": self.pattern_category.value,
            "target_name": self.target_name,
            "target_kind": self.target_kind,
            "confidence": self.confidence.to_dict(),
            "primary_location": self.primary_location.to_dict() if self.primary_location else None,
            "related_locations": [loc.to_dict() for loc in self.related_locations],
            "summary": self.summary,
            "evidences": [e.to_dict() for e in self.evidences],
            "metadata": self.metadata,
        }


@dataclass
class DetectionReport:
    """Aggregated findings report of a Swift codebase scan."""

    project_path: str
    scanned_files_count: int
    detections: list[Detection] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    @property
    def total_detections_count(self) -> int:
        return len(self.detections)

    @property
    def summary_by_category(self) -> dict[str, int]:
        counts: dict[str, int] = {c.value: 0 for c in PatternCategory}
        for d in self.detections:
            cat = d.pattern_category.value
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    @property
    def summary_by_type(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for d in self.detections:
            ptype = d.pattern_type.value
            counts[ptype] = counts.get(ptype, 0) + 1
        return counts

    @property
    def summary_by_confidence_level(self) -> dict[str, int]:
        counts: dict[str, int] = {lvl.value: 0 for lvl in ConfidenceLevel}
        for d in self.detections:
            counts[d.level.value] = counts.get(d.level.value, 0) + 1
        return counts

    def to_dict(self) -> dict[str, object]:
        return {
            "project_path": self.project_path,
            "scanned_files_count": self.scanned_files_count,
            "total_detections_count": self.total_detections_count,
            "elapsed_seconds": self.elapsed_seconds,
            "summary_by_category": self.summary_by_category,
            "summary_by_type": self.summary_by_type,
            "summary_by_confidence_level": self.summary_by_confidence_level,
            "detections": [d.to_dict() for d in self.detections],
        }
