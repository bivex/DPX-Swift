"""Domain value objects for Swift Pattern Detector."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PatternCategory(str, Enum):
    """Categorization of Swift patterns, idioms, and quality rules."""

    PROTOCOL_ORIENTED = "protocol_oriented"
    CONCURRENCY = "concurrency"
    DECLARATIVE_DSL = "declarative_dsl"
    CREATIONAL = "creational"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    RESILIENCE = "resilience"
    PRINCIPLE = "principle"


class PatternType(str, Enum):
    """Specific pattern types, idioms, and anti-patterns in Swift."""

    # 1. Protocol-Oriented Programming (POP)
    PROTOCOL_EXTENSION_DEFAULT_IMPL = "protocol_extension_default_impl"
    PROTOCOL_COMPOSITION = "protocol_composition"
    ASSOCIATED_TYPE_PAT = "associated_type_pat"
    OPAQUE_RETURN_TYPE = "opaque_return_type"
    EXISTENTIAL_ANY_BOX = "existential_any_box"

    # 2. Concurrency & Actor Model (Swift 5.5 - 6.0+)
    ACTOR_MODEL_ISOLATION = "actor_model_isolation"
    MAIN_ACTOR_UI_BINDING = "main_actor_ui_binding"
    TASK_GROUP_CONCURRENCY = "task_group_concurrency"
    ASYNC_STREAM_SEQUENCE = "async_stream_sequence"
    SENDABLE_THREAD_SAFETY = "sendable_thread_safety"

    # 3. SwiftUI & Declarative DSL
    PROPERTY_WRAPPER_PATTERN = "property_wrapper_pattern"
    RESULT_BUILDER_DSL = "result_builder_dsl"
    KEYPATH_DYNAMIC_LOOKUP = "keypath_dynamic_lookup"
    VIEW_MODIFIER_PIPELINE = "view_modifier_pipeline"

    # 4. GoF Creational
    SINGLETON_SHARED_INSTANCE = "singleton_shared_instance"
    FACTORY_METHOD = "factory_method"
    ABSTRACT_FACTORY = "abstract_factory"
    BUILDER_FLUENT_CHAIN = "builder_fluent_chain"
    PROTOTYPE_CLONABLE = "prototype_clonable"

    # 5. GoF Structural
    ADAPTER_VIA_EXTENSION = "adapter_via_extension"
    BRIDGE_IMPLEMENTOR = "bridge_implementor"
    COMPOSITE_VIEW_HIERARCHY = "composite_view_hierarchy"
    DECORATOR_WRAPPER = "decorator_wrapper"
    FACADE_SERVICE = "facade_service"
    FLYWEIGHT_CACHE = "flyweight_cache"
    PROXY_VIRTUAL_OR_REMOTE = "proxy_virtual_or_remote"

    # 6. GoF Behavioral
    CHAIN_OF_RESPONSIBILITY = "chain_of_responsibility"
    COMMAND_ENCAPSULATION = "command_encapsulation"
    DELEGATE_PATTERN_WEAK = "delegate_pattern_weak"
    ITERATOR_PROTOCOL = "iterator_protocol"
    MEDIATOR_COORDINATOR = "mediator_coordinator"
    MEMENTO_CODABLE_SNAPSHOT = "memento_codable_snapshot"
    OBSERVER_COMBINE_PUBLISHED = "observer_combine_published"
    STATE_ENUM_ASSOCIATED_VALUES = "state_enum_associated_values"
    STRATEGY_PROTOCOL_INJECTION = "strategy_protocol_injection"
    VISITOR_DOUBLE_DISPATCH = "visitor_double_dispatch"

    # 7. Resilience, Memory Safety & Hazards
    RETAIN_CYCLE_STRONG_SELF = "retain_cycle_strong_self"
    FORCE_UNWRAPPING_HAZARD = "force_unwrapping_hazard"
    STRONG_DELEGATE_RETAIN_CYCLE = "strong_delegate_retain_cycle"
    MAIN_THREAD_BLOCKING_CALL = "main_thread_blocking_call"
    UNHANDLED_TRY_SWALLOW = "unhandled_try_swallow"

    # 8. SOLID & Clean Architecture Principles
    MASSIVE_VIEW_CONTROLLER_SRP = "massive_view_controller_srp"
    FAT_PROTOCOL_ISP = "fat_protocol_isp"
    DYNAMIC_CAST_AS_CASCADE_OCP = "dynamic_cast_as_cascade_ocp"
    KISS_CYCLOMATIC_COMPLEXITY = "kiss_cyclomatic_complexity"
    KISS_LONG_PARAMETER_LIST = "kiss_long_parameter_list"
    DRY_DUPLICATE_LOGIC = "dry_duplicate_logic"
    DEMETER_LAW_TRAIN_WRECK = "demeter_law_train_wreck"


class ConfidenceLevel(str, Enum):
    """Categorized confidence rating for a detected pattern."""

    VERY_HIGH = "VERY_HIGH"  # >= 85%
    HIGH = "HIGH"            # >= 70%
    MEDIUM = "MEDIUM"        # >= 50%
    LOW = "LOW"              # < 50%


@dataclass(frozen=True)
class SourceLocation:
    """Source file coordinates."""

    file_path: str
    line: int = 1
    column: int = 1

    def __str__(self) -> str:
        return f"{self.file_path}:{self.line}:{self.column}"

    def to_dict(self) -> dict[str, object]:
        return {
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
        }


@dataclass(frozen=True)
class Evidence:
    """A granular piece of evidence contributing to pattern detection."""

    rule_code: str
    description: str
    weight: float  # typically 0.1 to 1.0
    location: SourceLocation | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "rule_code": self.rule_code,
            "description": self.description,
            "weight": self.weight,
            "location": self.location.to_dict() if self.location else None,
        }


@dataclass
class Confidence:
    """Aggregated score and evidence trail."""

    score: float
    evidences: list[Evidence] = field(default_factory=list)

    @property
    def level(self) -> ConfidenceLevel:
        if self.score >= 0.85:
            return ConfidenceLevel.VERY_HIGH
        if self.score >= 0.70:
            return ConfidenceLevel.HIGH
        if self.score >= 0.50:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    @property
    def percentage(self) -> int:
        return min(100, max(0, int(round(self.score * 100))))

    @property
    def percentage_str(self) -> str:
        return f"{self.percentage}%"

    def to_dict(self) -> dict[str, object]:
        return {
            "score": self.score,
            "level": self.level.value,
            "percentage": self.percentage,
            "percentage_str": self.percentage_str,
            "evidences": [e.to_dict() for e in self.evidences],
        }
