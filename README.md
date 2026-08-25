# 🍏 DPX-Swift: Protocol-Oriented Pattern Scanner, Actor Concurrency & SwiftUI Clean Architecture Static Analyzer

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Swift Version](https://img.shields.io/badge/Swift-5.5%20--%206.0+-F05138?logo=swift&logoColor=white)](https://www.swift.org/)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Architecture: Hexagonal DDD](https://img.shields.io/badge/Architecture-Hexagonal%20DDD-blueviolet)](https://alistair.cockburn.us/hexagonal-architecture/)
[![CLI: Typer & Rich](https://img.shields.io/badge/CLI-Typer%20%26%20Rich-009688)](https://typer.tiangolo.com)
[![SARIF OASIS v2.1.0](https://img.shields.io/badge/SARIF-OASIS%20v2.1.0-blue)](https://sarifweb.azurewebsites.net)

**DPX-Swift** is an enterprise-grade static analysis engine and architectural pattern detector for Swift codebases. Designed for **iOS, macOS, visionOS, watchOS, and Server-Side Swift (Vapor)**, it analyzes **Protocol-Oriented Programming (POP)**, **Swift Concurrency & Actor Isolation**, **SwiftUI Declarative DSLs**, **GoF Patterns**, and **ARC Memory Leaks & Retain Cycle Hazards**.

[Features](#-key-features) • [Installation](#-installation) • [CLI Usage](#-cli-usage) • [Supported Rules](#-supported-pattern-rules--checks) • [The DPX Suite Family](#-the-dpx-suite-family)

</div>

---

## 🌟 Key Features

- 🧬 **Protocol-Oriented Programming (POP):** Detects protocol default extensions, Protocols with Associated Types (PATs), compound protocol composition (`any A & B`), and opaque return types (`some View`).
- ⚡ **Swift Concurrency & Actors (Swift 5.5 - 6.0+):** Full inspection of `actor` data isolation, `@MainActor` UI synchronization, structured `withTaskGroup`, `AsyncStream` event sequences, and `Sendable` thread-safety boundaries.
- 🎨 **SwiftUI & Declarative DSLs:** Detects `@propertyWrapper` state abstractions, `@resultBuilder` syntax builders, `@dynamicMemberLookup` KeyPath forwarding, and `ViewModifier` pipelines.
- 🛡️ **ARC Memory Safety & Hazard Auditing:** Automatically detects strong `self` in escaping closures (Retain Cycles), strong delegate properties, unsafe force-unwrapping (`!`, `as!`, `try!`), and main-thread blocking calls.
- 📊 **Interactive Architecture Observability HUD:** Generates zero-dependency interactive HTML dashboards with instant fuzzy search, KPI metrics, and a built-in **`🤖 Copy AI Context Prompt`** generator for LLMs (Claude, GPT-4, Gemini).
- 🚀 **Blazing Fast Linear Parser:** High-throughput native parser processing thousands of lines of Swift per millisecond.
- 🔒 **CI/CD & GitHub Security Ready:** Exports standardized **OASIS SARIF v2.1.0**, JSON, and Markdown reports.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/bivex/DPX-Swift.git
cd DPX-Swift

# Install dependencies using uv or pip
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

---

## 💻 CLI Usage

### 1. Scan a Swift Project or Package
```bash
# Terminal scan with Rich formatting
dpx-swift scan /path/to/ios/project

# Generate interactive HTML HUD Dashboard
dpx-swift scan /path/to/ios/project -H reports/swift_hud.html

# Generate AI Context Prompt for LLMs
dpx-swift scan /path/to/ios/project --llm

# Filter for specific concurrency or hazard patterns
dpx-swift scan /path/to/ios/project -p actor_model_isolation -p retain_cycle_strong_self

# Export SARIF for GitHub Code Scanning
dpx-swift scan /path/to/ios/project -S reports/results.sarif
```

### 2. Inspect Supported Architectural Rules
```bash
dpx-swift rules
```

### 3. Query Deep Pattern Documentation
```bash
dpx-swift info actor_model_isolation
dpx-swift info retain_cycle_strong_self
```

---

## 📋 Supported Pattern Rules & Checks

### 1. 🧬 Protocol-Oriented Programming (POP)
- `protocol_extension_default_impl`: Protocol extensions providing default method implementations.
- `protocol_composition`: Compound protocol conformance (`any A & B` / `some A & B`).
- `associated_type_pat`: Protocols with Associated Types (`associatedtype`).
- `opaque_return_type`: Opaque return types (`some Protocol`).
- `existential_any_box`: Dynamic existential containers (`any Protocol`).

### 2. ⚡ Concurrency & Actors
- `actor_model_isolation`: Actor data isolation protecting mutable state from data races.
- `main_actor_ui_binding`: `@MainActor` annotation guaranteeing main UI thread dispatch.
- `task_group_concurrency`: Structured concurrency with `withTaskGroup` / `withThrowingTaskGroup`.
- `async_stream_sequence`: Asynchronous event streams (`AsyncStream`, `AsyncSequence`).
- `sendable_thread_safety`: `Sendable` protocol boundaries across actor domains.

### 3. 🎨 SwiftUI & Declarative DSL
- `property_wrapper_pattern`: Custom `@propertyWrapper` declarations (`wrappedValue`).
- `result_builder_dsl`: Declarative `@resultBuilder` block transformers.
- `keypath_dynamic_lookup`: `@dynamicMemberLookup` with KeyPath subscripts.
- `view_modifier_pipeline`: Composable `ViewModifier` decorators.

### 4. 🏛️ GoF Creational Patterns
- `singleton_shared_instance`: Thread-safe `static let shared` with `private init()`.
- `factory_method`: Static / polymorphic factory methods (`make...`, `create...`).
- `abstract_factory`: Factory protocols declaring families of creation methods.
- `builder_fluent_chain`: Fluent chaining returning `Self` or mutating structs.
- `prototype_clonable`: Instance cloning via `NSCopying` / `clone()`.

### 5. 🧱 GoF Structural Patterns
- `adapter_via_extension`: Retroactive protocol adaptation via extensions.
- `bridge_implementor`: Decoupling abstraction from implementor protocols.
- `composite_view_hierarchy`: Hierarchical tree / `@ViewBuilder` composite structures.
- `decorator_wrapper`: Decorator types wrapping underlying conforming instances.
- `facade_service`: Unified coordinator orchestrating multiple subsystem clients.
- `flyweight_cache`: Sharing fine-grained immutable instances via pooling caches.
- `proxy_virtual_or_remote`: Surrogate proxy controlling access to underlying targets.

### 6. 🎯 GoF Behavioral Patterns
- `chain_of_responsibility`: Linked handlers delegating requests along a chain.
- `command_encapsulation`: Command objects with `execute()` / `undo()`.
- `delegate_pattern_weak`: Safe `weak var delegate: ...Delegate?` contracts.
- `iterator_protocol`: Custom traversal conforming to `IteratorProtocol` / `Sequence`.
- `mediator_coordinator`: App Coordinators and Mediators managing UI flows.
- `memento_codable_snapshot`: State capture via Codable snapshots.
- `observer_combine_published`: Combine `@Published` and `ObservableObject` reactive publishers.
- `state_enum_associated_values`: Type-safe Enum State Machines with associated values.
- `strategy_protocol_injection`: Interchangeable algorithm strategy injection.
- `visitor_double_dispatch`: Double dispatch operations via `accept(visitor:)`.

### 7. 🛡️ Resilience, Hazards & Memory Safety
- `retain_cycle_strong_self`: Escaping closures strongly capturing `self` without `[weak self]`.
- `force_unwrapping_hazard`: Unsafe force-unwraps (`!`, `as!`, `try!`) causing fatal crashes.
- `strong_delegate_retain_cycle`: Strong delegate properties missing `weak` modifier.
- `main_thread_blocking_call`: Synchronous blocking calls (`Thread.sleep`) in UI contexts.
- `unhandled_try_swallow`: Silent error discard via `try?` in critical paths.

### 8. 📐 SOLID & Code Quality Principles
- `massive_view_controller_srp`: Massive View Controller / God Class SRP violations.
- `fat_protocol_isp`: Fat protocols declaring too many required methods.
- `dynamic_cast_as_cascade_ocp`: Dynamic `as?` casting cascades violating OCP.
- `kiss_cyclomatic_complexity`: High cyclomatic complexity (> 8 branch points).
- `kiss_long_parameter_list`: Functions with excessive parameters (>= 5).
- `dry_duplicate_logic`: Duplicated algorithmic logic across methods.
- `demeter_law_train_wreck`: Law of Demeter deep dot-chain navigation (`a.b.c.d.e`).

---

## 🌐 The DPX Suite Family

Cross-language architectural static analysis across all modern programming languages:

| Repository | Language / Ecosystem | Primary Paradigms & Focus |
|---|---|---|
| **[`DPX-Mojo`](https://github.com/bivex/DPX-Mojo)** | **Mojo** (24.x - 25.x+) | **SIMD Vectorization, Ownership, Memory Safety, GoF 23, AI Acceleration** |
| **[`DPX-Julia`](https://github.com/bivex/DPX-Julia)** | **Julia** (1.6 - 1.11+) | **Multiple Dispatch, Holy Traits, Metaprogramming, Tasks, GoF 23** |
| **[`DPX-Kotlin`](https://github.com/bivex/DPX-Kotlin)** | **Kotlin** (1.8 - 2.0+) | **Coroutines, Flow, Jetpack Compose, Multiplatform, GoF 23** |
| **[`DPX-Swift`](https://github.com/bivex/DPX-Swift)** | **Swift** (5.5 - 6.0+) | **Protocol-Oriented, Actor Concurrency, SwiftUI, ARC Safety** |
| **[`DPX-CSharp`](https://github.com/bivex/DPX-CSharp)** | **C#** (10 - 13 / .NET 8-9) | **Clean Architecture, CQRS MediatR, Channel Pipelines** |
| **[`DPX-TypeScript`](https://github.com/bivex/DPX-TypeScript)** | **TypeScript / JavaScript** | **Hexagonal DI, Decorator Meta, Reactive Streams, React/NestJS** |
| **[`DPX-Rust`](https://github.com/bivex/DPX-Rust)** | **Rust** (Edition 2021/2024) | **Zero-Cost Abstractions, RAII Lifetimes, Typestate Pattern** |
| **[`DPX-Go`](https://github.com/bivex/DPX-Go)** | **Go** (1.18 - 1.24+) | **Goroutine Channels, CSP Concurrency, Pipeline Streaming** |
| **[`DPX-Py`](https://github.com/bivex/DPX-Py)** | **Python** (3.8 - 3.13+) | **Multi-Paradigm Hexagonal, Data Flow Engine, AsyncIO** |
| **[`DPX-Php`](https://github.com/bivex/DPX-Php)** | **PHP** (8.1 - 8.4+) | **Attribute-driven DDD, Fiber Concurrency, Laravel/Symfony** |
| **[`DPX-Haskell`](https://github.com/bivex/DPX-Haskell)** | **Haskell** (GHC 9.2 - 9.12+) | **Category Theory, Monad Transformers, Free Monads, Optics** |
| **[`DPX-OCaml`](https://github.com/bivex/DPX-OCaml)** | **OCaml** (4.14 - 5.3+ Multicore) | **Functor Modules, Effect Handlers, GADTs, Railway Monads** |
| **[`DPX-Elixir`](https://github.com/bivex/DPX-Elixir)** | **Elixir** (OTP 25 - 27+) | **GenServer, DynamicSupervisor, Actor Fault Tolerance** |
| **[`DPX-Erlang`](https://github.com/bivex/DPX-Erlang)** | **Erlang/OTP** (24 - 27+) | **OTP Behaviors, Supervision Trees, Message Passing** |
| **[`DPX-C`](https://github.com/bivex/DPX-C)** | **C** (C99 - C23) | **Opaque Structs, VTables, MISRA/CERT Safety, Arena Allocators** |
| **[`DPX-Cpp`](https://github.com/bivex/DPX-Cpp)** | **C++** (C++14 - C++20) | **CRTP, Policy-Based Design, RAII Memory Safety, ANTLR4 AST** |
| **[`DPX-Java`](https://github.com/bivex/DPX-Java)** | **Java** (17 - 23+) | **Virtual Threads, Spring Boot / Jakarta EE, GoF Patterns** |
| **[`DPX`](https://github.com/bivex/DPX)** | **Clojure** / Meta Engine | **Pure Functional, Multimethods, Homoiconic Macro Architecture** |
 **Julia** (1.6 - 1.11+) | **Multiple Dispatch, Holy Traits, Metaprogramming, Tasks, GoF 23** |
| **[`DPX-Kotlin`](https://github.com/bivex/DPX-Kotlin)** | **Kotlin** (1.8 - 2.0+) | **Coroutines, Flow, Jetpack Compose, Multiplatform, GoF 23** |
| **[`DPX-Swift`](https://github.com/bivex/DPX-Swift)** | **Swift** (5.5 - 6.0+) | **Protocol-Oriented, Actor Concurrency, SwiftUI, ARC Safety** |
| **[`DPX-CSharp`](https://github.com/bivex/DPX-CSharp)** | **C#** (10 - 13 / .NET 8-9) | **Clean Architecture, CQRS MediatR, Channel Pipelines** |
| **[`DPX-TypeScript`](https://github.com/bivex/DPX-TypeScript)** | **TypeScript / JavaScript** | **Hexagonal DI, Decorator Meta, Reactive Streams, React/NestJS** |
| **[`DPX-Rust`](https://github.com/bivex/DPX-Rust)** | **Rust** (Edition 2021/2024) | **Zero-Cost Abstractions, RAII Lifetimes, Typestate Pattern** |
| **[`DPX-Go`](https://github.com/bivex/DPX-Go)** | **Go** (1.18 - 1.24+) | **Goroutine Channels, CSP Concurrency, Pipeline Streaming** |
| **[`DPX-Py`](https://github.com/bivex/DPX-Py)** | **Python** (3.8 - 3.13+) | **Multi-Paradigm Hexagonal, Data Flow Engine, AsyncIO** |
| **[`DPX-Php`](https://github.com/bivex/DPX-Php)** | **PHP** (8.1 - 8.4+) | **Attribute-driven DDD, Fiber Concurrency, Laravel/Symfony** |
| **[`DPX-Haskell`](https://github.com/bivex/DPX-Haskell)** | **Haskell** (GHC 9.2 - 9.12+) | **Category Theory, Monad Transformers, Free Monads, Optics** |
| **[`DPX-OCaml`](https://github.com/bivex/DPX-OCaml)** | **OCaml** (4.14 - 5.3+ Multicore) | **Functor Modules, Effect Handlers, GADTs, Railway Monads** |
| **[`DPX-Elixir`](https://github.com/bivex/DPX-Elixir)** | **Elixir** (OTP 25 - 27+) | **GenServer, DynamicSupervisor, Actor Fault Tolerance** |
| **[`DPX-Erlang`](https://github.com/bivex/DPX-Erlang)** | **Erlang/OTP** (24 - 27+) | **OTP Behaviors, Supervision Trees, Message Passing** |
| **[`DPX-C`](https://github.com/bivex/DPX-C)** | **C** (C99 - C23) | **Opaque Structs, VTables, MISRA/CERT Safety, Arena Allocators** |
| **[`DPX-Cpp`](https://github.com/bivex/DPX-Cpp)** | **C++** (C++14 - C++20) | **CRTP, Policy-Based Design, RAII Memory Safety, ANTLR4 AST** |
| **[`DPX-Java`](https://github.com/bivex/DPX-Java)** | **Java** (17 - 23+) | **Virtual Threads, Spring Boot / Jakarta EE, GoF Patterns** |
| **[`DPX`](https://github.com/bivex/DPX)** | **Clojure** / Meta Engine | **Pure Functional, Multimethods, Homoiconic Macro Architecture** |

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
