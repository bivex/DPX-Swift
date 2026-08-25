"""Catalog and metadata definitions for Swift design patterns and rules."""

from __future__ import annotations

from dataclasses import dataclass
from pattern_detector.domain.value_objects import PatternCategory, PatternType


@dataclass(frozen=True)
class PatternDefinition:
    """Catalog metadata for a detected pattern or quality rule."""

    type: PatternType
    category: PatternCategory
    name: str
    description: str
    gof_equivalent: str | None = None
    swift_version: str = "5.5+"
    recommendation: str | None = None


PATTERN_CATALOG: dict[PatternType, PatternDefinition] = {
    # 1. Protocol-Oriented Programming (POP)
    PatternType.PROTOCOL_EXTENSION_DEFAULT_IMPL: PatternDefinition(
        type=PatternType.PROTOCOL_EXTENSION_DEFAULT_IMPL,
        category=PatternCategory.PROTOCOL_ORIENTED,
        name="Protocol Extension Default Implementation",
        description="Protocol extended with default method implementations, enabling mixin-style composition without class inheritance hierarchies.",
        gof_equivalent="Template Method / Trait",
    ),
    PatternType.PROTOCOL_COMPOSITION: PatternDefinition(
        type=PatternType.PROTOCOL_COMPOSITION,
        category=PatternCategory.PROTOCOL_ORIENTED,
        name="Protocol Composition (any / some &)",
        description="Composition of multiple protocols (e.g. `Codable & Identifiable`) using compound protocol types.",
        gof_equivalent="Composite Interface",
    ),
    PatternType.ASSOCIATED_TYPE_PAT: PatternDefinition(
        type=PatternType.ASSOCIATED_TYPE_PAT,
        category=PatternCategory.PROTOCOL_ORIENTED,
        name="Protocol with Associated Types (PAT)",
        description="Parametric protocol abstraction using `associatedtype` for generic interface contracts.",
        gof_equivalent="Generic Interface / Type Class",
    ),
    PatternType.OPAQUE_RETURN_TYPE: PatternDefinition(
        type=PatternType.OPAQUE_RETURN_TYPE,
        category=PatternCategory.PROTOCOL_ORIENTED,
        name="Opaque Return Type (`some Protocol`)",
        description="Encapsulates concrete return types behind opaque protocol abstractions without runtime existential overhead.",
        gof_equivalent="Abstract Type Encapsulation",
    ),
    PatternType.EXISTENTIAL_ANY_BOX: PatternDefinition(
        type=PatternType.EXISTENTIAL_ANY_BOX,
        category=PatternCategory.PROTOCOL_ORIENTED,
        name="Existential Type Container (`any Protocol`)",
        description="Dynamic runtime polymorphism box holding any concrete type conforming to a protocol.",
        gof_equivalent="Dynamic Polymorphic Container",
    ),

    # 2. Concurrency & Actor Model
    PatternType.ACTOR_MODEL_ISOLATION: PatternDefinition(
        type=PatternType.ACTOR_MODEL_ISOLATION,
        category=PatternCategory.CONCURRENCY,
        name="Actor Model Isolation",
        description="Actor-based data isolation protecting mutable state from data races in concurrent environments.",
        gof_equivalent="Active Object / Monitor",
    ),
    PatternType.MAIN_ACTOR_UI_BINDING: PatternDefinition(
        type=PatternType.MAIN_ACTOR_UI_BINDING,
        category=PatternCategory.CONCURRENCY,
        name="@MainActor UI Binding",
        description="Global actor synchronization ensuring state mutations and UI renders execute exclusively on the main dispatch queue.",
        gof_equivalent="UI Thread Synchronization / Dispatcher",
    ),
    PatternType.TASK_GROUP_CONCURRENCY: PatternDefinition(
        type=PatternType.TASK_GROUP_CONCURRENCY,
        category=PatternCategory.CONCURRENCY,
        name="Structured TaskGroup Concurrency",
        description="Parallel task fan-out and structured collection using `withTaskGroup` or `withThrowingTaskGroup`.",
        gof_equivalent="Fork-Join / Parallel Pipeline",
    ),
    PatternType.ASYNC_STREAM_SEQUENCE: PatternDefinition(
        type=PatternType.ASYNC_STREAM_SEQUENCE,
        category=PatternCategory.CONCURRENCY,
        name="AsyncSequence / AsyncStream",
        description="Asynchronous data stream emitting sequential values over time with backpressure and cancellation support.",
        gof_equivalent="Reactive Streams / Iterator",
    ),
    PatternType.SENDABLE_THREAD_SAFETY: PatternDefinition(
        type=PatternType.SENDABLE_THREAD_SAFETY,
        category=PatternCategory.CONCURRENCY,
        name="Sendable Concurrency Boundary",
        description="Type-safe concurrency marker guaranteeing thread-safe transfer across actor boundaries.",
        gof_equivalent="Immutable Value Object",
    ),

    # 3. SwiftUI & Declarative DSL
    PatternType.PROPERTY_WRAPPER_PATTERN: PatternDefinition(
        type=PatternType.PROPERTY_WRAPPER_PATTERN,
        category=PatternCategory.DECLARATIVE_DSL,
        name="Property Wrapper Pattern",
        description="Custom property wrapper (`@propertyWrapper`) encapsulating property access, validation, or persistence logic.",
        gof_equivalent="Decorator / Proxy",
    ),
    PatternType.RESULT_BUILDER_DSL: PatternDefinition(
        type=PatternType.RESULT_BUILDER_DSL,
        category=PatternCategory.DECLARATIVE_DSL,
        name="Result Builder DSL",
        description="Domain-specific declarative syntax builder (`@resultBuilder`) transforming code blocks into composite data structures.",
        gof_equivalent="Builder / Interpreter",
    ),
    PatternType.KEYPATH_DYNAMIC_LOOKUP: PatternDefinition(
        type=PatternType.KEYPATH_DYNAMIC_LOOKUP,
        category=PatternCategory.DECLARATIVE_DSL,
        name="KeyPath Dynamic Member Lookup",
        description=r"Type-safe property forwarding and dynamic member resolution using `\Type.property` KeyPaths.",
        gof_equivalent="Dynamic Proxy / Property Accessor",
    ),
    PatternType.VIEW_MODIFIER_PIPELINE: PatternDefinition(
        type=PatternType.VIEW_MODIFIER_PIPELINE,
        category=PatternCategory.DECLARATIVE_DSL,
        name="ViewModifier Pipeline",
        description="Composable UI decorator pipeline conforming to `ViewModifier` or fluent view extension chains.",
        gof_equivalent="Decorator Pipeline",
    ),

    # 4. Creational
    PatternType.SINGLETON_SHARED_INSTANCE: PatternDefinition(
        type=PatternType.SINGLETON_SHARED_INSTANCE,
        category=PatternCategory.CREATIONAL,
        name="Thread-Safe Swift Singleton",
        description="Thread-safe shared singleton instance via `static let shared` with `private init()`.",
        gof_equivalent="Singleton",
    ),
    PatternType.FACTORY_METHOD: PatternDefinition(
        type=PatternType.FACTORY_METHOD,
        category=PatternCategory.CREATIONAL,
        name="Factory Method",
        description="Static or protocol-based factory method for instantiating polymorphic types.",
        gof_equivalent="Factory Method",
    ),
    PatternType.ABSTRACT_FACTORY: PatternDefinition(
        type=PatternType.ABSTRACT_FACTORY,
        category=PatternCategory.CREATIONAL,
        name="Abstract Factory",
        description="Factory protocol declaring creation methods for families of related or dependent objects.",
        gof_equivalent="Abstract Factory",
    ),
    PatternType.BUILDER_FLUENT_CHAIN: PatternDefinition(
        type=PatternType.BUILDER_FLUENT_CHAIN,
        category=PatternCategory.CREATIONAL,
        name="Fluent Builder Chain",
        description="Method chaining builder returning `Self` or mutating struct instance step-by-step.",
        gof_equivalent="Builder",
    ),
    PatternType.PROTOTYPE_CLONABLE: PatternDefinition(
        type=PatternType.PROTOTYPE_CLONABLE,
        category=PatternCategory.CREATIONAL,
        name="Prototype / Clone Pattern",
        description="Instance cloning mechanism via `NSCopying` or explicit `clone()` / `copy()` methods.",
        gof_equivalent="Prototype",
    ),

    # 5. Structural
    PatternType.ADAPTER_VIA_EXTENSION: PatternDefinition(
        type=PatternType.ADAPTER_VIA_EXTENSION,
        category=PatternCategory.STRUCTURAL,
        name="Adapter via Protocol Extension",
        description="Retroactive modeling adopting third-party or system types to domain protocols via extensions.",
        gof_equivalent="Adapter",
    ),
    PatternType.BRIDGE_IMPLEMENTOR: PatternDefinition(
        type=PatternType.BRIDGE_IMPLEMENTOR,
        category=PatternCategory.STRUCTURAL,
        name="Bridge Pattern",
        description="Decouples an abstraction from its implementation by delegating to a separate implementor protocol.",
        gof_equivalent="Bridge",
    ),
    PatternType.COMPOSITE_VIEW_HIERARCHY: PatternDefinition(
        type=PatternType.COMPOSITE_VIEW_HIERARCHY,
        category=PatternCategory.STRUCTURAL,
        name="Composite View / Component Tree",
        description="Hierarchical tree composite grouping child views and components uniformly.",
        gof_equivalent="Composite",
    ),
    PatternType.DECORATOR_WRAPPER: PatternDefinition(
        type=PatternType.DECORATOR_WRAPPER,
        category=PatternCategory.STRUCTURAL,
        name="Decorator / Wrapper Type",
        description="Struct or class wrapping an underlying conforming instance to inject supplementary behavior.",
        gof_equivalent="Decorator",
    ),
    PatternType.FACADE_SERVICE: PatternDefinition(
        type=PatternType.FACADE_SERVICE,
        category=PatternCategory.STRUCTURAL,
        name="Facade Service Coordinator",
        description="Unified simplified entry point coordinating multiple low-level subsystems, repositories, or APIs.",
        gof_equivalent="Facade",
    ),
    PatternType.FLYWEIGHT_CACHE: PatternDefinition(
        type=PatternType.FLYWEIGHT_CACHE,
        category=PatternCategory.STRUCTURAL,
        name="Flyweight Cache",
        description="Sharing fine-grained immutable instances via factory pooling / dictionary cache to minimize memory.",
        gof_equivalent="Flyweight",
    ),
    PatternType.PROXY_VIRTUAL_OR_REMOTE: PatternDefinition(
        type=PatternType.PROXY_VIRTUAL_OR_REMOTE,
        category=PatternCategory.STRUCTURAL,
        name="Proxy Pattern",
        description="Surrogate or placeholder object controlling access to an underlying resource or remote endpoint.",
        gof_equivalent="Proxy",
    ),

    # 6. Behavioral
    PatternType.CHAIN_OF_RESPONSIBILITY: PatternDefinition(
        type=PatternType.CHAIN_OF_RESPONSIBILITY,
        category=PatternCategory.BEHAVIORAL,
        name="Chain of Responsibility",
        description="Sequence of handler objects processing a request or passing it to the next handler in the chain.",
        gof_equivalent="Chain of Responsibility",
    ),
    PatternType.COMMAND_ENCAPSULATION: PatternDefinition(
        type=PatternType.COMMAND_ENCAPSULATION,
        category=PatternCategory.BEHAVIORAL,
        name="Command Encapsulation",
        description="Encapsulates an operation, its receiver, and parameters into an executable command object.",
        gof_equivalent="Command",
    ),
    PatternType.DELEGATE_PATTERN_WEAK: PatternDefinition(
        type=PatternType.DELEGATE_PATTERN_WEAK,
        category=PatternCategory.BEHAVIORAL,
        name="Weak Delegate Pattern",
        description="One-to-one delegation contract holding a `weak` reference to prevent retain cycles.",
        gof_equivalent="Observer / Mediator",
    ),
    PatternType.ITERATOR_PROTOCOL: PatternDefinition(
        type=PatternType.ITERATOR_PROTOCOL,
        category=PatternCategory.BEHAVIORAL,
        name="Iterator Protocol / Sequence",
        description="Sequential element traversal conforming to `IteratorProtocol` or `Sequence`.",
        gof_equivalent="Iterator",
    ),
    PatternType.MEDIATOR_COORDINATOR: PatternDefinition(
        type=PatternType.MEDIATOR_COORDINATOR,
        category=PatternCategory.BEHAVIORAL,
        name="Mediator / App Coordinator",
        description="Centralized coordinator orchestrating navigation and interactions between disparate components.",
        gof_equivalent="Mediator",
    ),
    PatternType.MEMENTO_CODABLE_SNAPSHOT: PatternDefinition(
        type=PatternType.MEMENTO_CODABLE_SNAPSHOT,
        category=PatternCategory.BEHAVIORAL,
        name="Codable Memento Snapshot",
        description="Captures and externalizes an object's internal state into a Codable snapshot without violating encapsulation.",
        gof_equivalent="Memento",
    ),
    PatternType.OBSERVER_COMBINE_PUBLISHED: PatternDefinition(
        type=PatternType.OBSERVER_COMBINE_PUBLISHED,
        category=PatternCategory.BEHAVIORAL,
        name="Combine @Published / Observable",
        description="Reactive observer publisher notifying subscribed observers upon state mutations.",
        gof_equivalent="Observer",
    ),
    PatternType.STATE_ENUM_ASSOCIATED_VALUES: PatternDefinition(
        type=PatternType.STATE_ENUM_ASSOCIATED_VALUES,
        category=PatternCategory.BEHAVIORAL,
        name="Enum State Machine with Associated Values",
        description="Type-safe finite state machine modeling distinct lifecycle states with payload data.",
        gof_equivalent="State",
    ),
    PatternType.STRATEGY_PROTOCOL_INJECTION: PatternDefinition(
        type=PatternType.STRATEGY_PROTOCOL_INJECTION,
        category=PatternCategory.BEHAVIORAL,
        name="Strategy Protocol / Closure Injection",
        description="Interchangeable algorithm strategy encapsulated in protocol abstraction or closure property.",
        gof_equivalent="Strategy",
    ),
    PatternType.VISITOR_DOUBLE_DISPATCH: PatternDefinition(
        type=PatternType.VISITOR_DOUBLE_DISPATCH,
        category=PatternCategory.BEHAVIORAL,
        name="Visitor Double Dispatch",
        description="Separates an algorithm from the object structure on which it operates via `accept(visitor:)` dispatch.",
        gof_equivalent="Visitor",
    ),

    # 7. Resilience, Safety & Hazards
    PatternType.RETAIN_CYCLE_STRONG_SELF: PatternDefinition(
        type=PatternType.RETAIN_CYCLE_STRONG_SELF,
        category=PatternCategory.RESILIENCE,
        name="Retain Cycle Hazard (Strong Self in Closure)",
        description="Escaping or asynchronous closure strongly captures `self` without `[weak self]` or `[unowned self]`, risking memory leaks.",
        recommendation="Capture `[weak self]` inside escaping closures and guard unwrapping.",
    ),
    PatternType.FORCE_UNWRAPPING_HAZARD: PatternDefinition(
        type=PatternType.FORCE_UNWRAPPING_HAZARD,
        category=PatternCategory.RESILIENCE,
        name="Force Unwrapping Hazard (`!` / `as!` / `try!`)",
        description="Unsafe force-unwrapping of optionals or force-casting that causes runtime fatal crashes if nil or invalid.",
        recommendation="Use `if let`, `guard let`, optional chaining (`?.`), or `nil-coalescing (`??`).",
    ),
    PatternType.STRONG_DELEGATE_RETAIN_CYCLE: PatternDefinition(
        type=PatternType.STRONG_DELEGATE_RETAIN_CYCLE,
        category=PatternCategory.RESILIENCE,
        name="Strong Delegate Reference (Memory Leak Hazard)",
        description="Delegate property declared without `weak` modifier, creating mutual strong reference cycle between parent and child.",
        recommendation="Mark protocol as `AnyObject` and declare `weak var delegate: SomeDelegate?`.",
    ),
    PatternType.MAIN_THREAD_BLOCKING_CALL: PatternDefinition(
        type=PatternType.MAIN_THREAD_BLOCKING_CALL,
        category=PatternCategory.RESILIENCE,
        name="Main Thread Blocking Hazard",
        description="Synchronous blocking operations (e.g. `Thread.sleep`, sync network I/O, heavy semaphore waits) executed on `@MainActor` or UI thread.",
        recommendation="Offload blocking work to background tasks via `Task.detached` or `async/await` non-blocking calls.",
    ),
    PatternType.UNHANDLED_TRY_SWALLOW: PatternDefinition(
        type=PatternType.UNHANDLED_TRY_SWALLOW,
        category=PatternCategory.RESILIENCE,
        name="Silent Error Swallowing (`try?` in Critical Paths)",
        description="Critical error silently discarded using `try?` without logging, propagation, or fallback.",
        recommendation="Use structured `do { try ... } catch { ... }` blocks with domain error handling.",
    ),

    # 8. SOLID & Clean Architecture Principles
    PatternType.MASSIVE_VIEW_CONTROLLER_SRP: PatternDefinition(
        type=PatternType.MASSIVE_VIEW_CONTROLLER_SRP,
        category=PatternCategory.PRINCIPLE,
        name="SRP Violation: Massive View Controller / God Class",
        description="Class or struct exceeding responsibility limits with high line/method counts mixing networking, persistence, and UI.",
        recommendation="Extract business logic into ViewModels / Interactors and networking into Service Repositories.",
    ),
    PatternType.FAT_PROTOCOL_ISP: PatternDefinition(
        type=PatternType.FAT_PROTOCOL_ISP,
        category=PatternCategory.PRINCIPLE,
        name="ISP Violation: Fat Protocol",
        description="Protocol declaring excessive required methods forcing implementors into unnecessary dependencies.",
        recommendation="Segregate into smaller role protocols or provide default implementations in extensions.",
    ),
    PatternType.DYNAMIC_CAST_AS_CASCADE_OCP: PatternDefinition(
        type=PatternType.DYNAMIC_CAST_AS_CASCADE_OCP,
        category=PatternCategory.PRINCIPLE,
        name="OCP Violation: Dynamic Type Casting Cascade (`is` / `as?`)",
        description="Repeated `if let ... as? Type` or `switch type` checks instead of polymorphic protocol dispatch.",
        recommendation="Delegate behavior to polymorphic protocol methods.",
    ),
    PatternType.KISS_CYCLOMATIC_COMPLEXITY: PatternDefinition(
        type=PatternType.KISS_CYCLOMATIC_COMPLEXITY,
        category=PatternCategory.PRINCIPLE,
        name="KISS Violation: High Cyclomatic Complexity",
        description="Function containing deeply nested conditionals, loops, and excessive branching points.",
        recommendation="Decompose into focused helper functions or table-driven lookups.",
    ),
    PatternType.KISS_LONG_PARAMETER_LIST: PatternDefinition(
        type=PatternType.KISS_LONG_PARAMETER_LIST,
        category=PatternCategory.PRINCIPLE,
        name="KISS Violation: Long Parameter List",
        description="Function or initializer accepting excessive arguments, increasing cognitive load and error risk.",
        recommendation="Group parameters into a configuration struct or builder.",
    ),
    PatternType.DRY_DUPLICATE_LOGIC: PatternDefinition(
        type=PatternType.DRY_DUPLICATE_LOGIC,
        category=PatternCategory.PRINCIPLE,
        name="DRY Violation: Duplicate Code Logic",
        description="Duplicated algorithmic sequences across multiple functions or types.",
        recommendation="Extract common functionality into shared protocol extensions or helper utilities.",
    ),
    PatternType.DEMETER_LAW_TRAIN_WRECK: PatternDefinition(
        type=PatternType.DEMETER_LAW_TRAIN_WRECK,
        category=PatternCategory.PRINCIPLE,
        name="Law of Demeter Violation (Train Wreck Dot Chains)",
        description="Deep navigation across indirect object graphs (e.g. `a.b.c.d.doSomething()`), tightly coupling subsystems.",
        recommendation="Introduce facade methods or delegate properties directly on intermediate objects.",
    ),
}
