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

---

## 🌐 The DPX Multi-Language Static Analysis Family (33 Languages)

| # | Language | Repository | Ecosystem & Focus |
|:---:|---|---|---|
| 1 | **Ada** | [`bivex/DPX-Ada`](https://github.com/bivex/DPX-Ada) | Ada 2012/2022, SPARK Contracts, Ravenscar Tasking, DO-178C Safety |
| 2 | **Clojure** | [`bivex/DPX`](https://github.com/bivex/DPX) | Lisp S-Expressions, Protocols, Multimethods |
| 3 | **C** | [`bivex/DPX-C`](https://github.com/bivex/DPX-C) | Memory Safety, Struct VTables, Idiomatic C11/C23 |
| 4 | **Cairo** | [`bivex/DPX-Cairo`](https://github.com/bivex/DPX-Cairo) | Starknet Smart Contracts, ZK-Rollup Invariants |
| 5 | **C++** | [`bivex/DPX-Cpp`](https://github.com/bivex/DPX-Cpp) | RAII, CRTP, Concepts, Modern C++20/23 |
| 6 | **C#** | [`bivex/DPX-CSharp`](https://github.com/bivex/DPX-CSharp) | .NET 9, Roslyn AST, Linq, Records |
| 7 | **Dart** | [`bivex/DPX-Dart`](https://github.com/bivex/DPX-Dart) | Dart 3.x, Flutter, BLoC, Riverpod, Isolates |
| 8 | **Elixir** | [`bivex/DPX-Elixir`](https://github.com/bivex/DPX-Elixir) | BEAM OTP, GenServer, Supervisors |
| 9 | **Erlang** | [`bivex/DPX-Erlang`](https://github.com/bivex/DPX-Erlang) | Fault Tolerance, Actor Model, OTP Behaviors |
| 10 | **Gleam** | [`bivex/DPX-Gleam`](https://github.com/bivex/DPX-Gleam) | Type-Safe BEAM, Actor Concurrency |
| 11 | **Go** | [`bivex/DPX-Go`](https://github.com/bivex/DPX-Go) | Goroutines, Channels, Composition, Interfaces |
| 12 | **Haskell** | [`bivex/DPX-Haskell`](https://github.com/bivex/DPX-Haskell) | Pure Functional, Monads, Typeclasses, Arrows |
| 13 | **Huff** | [`bivex/DPX-Huff`](https://github.com/bivex/DPX-Huff) | Low-Level EVM Bytecode & Opcodes |
| 14 | **Idris 2** | [`bivex/DPX-Idris2`](https://github.com/bivex/DPX-Idris2) | Dependent Types, QTT Linear Protocols, Totality, Proofs |
| 15 | **Java** | [`bivex/DPX-Java`](https://github.com/bivex/DPX-Java) | Spring Boot, Enterprise Java, JVM Invariants |
| 16 | **Julia** | [`bivex/DPX-Julia`](https://github.com/bivex/DPX-Julia) | Multiple Dispatch, Scientific Computing |
| 17 | **Kotlin** | [`bivex/DPX-Kotlin`](https://github.com/bivex/DPX-Kotlin) | Coroutines, Multiplatform, Functional DSLs |
| 18 | **Lua** | [`bivex/DPX-Lua`](https://github.com/bivex/DPX-Lua) | Metatables, Coroutines, LuaJIT, Neovim |
| 19 | **Mojo** | [`bivex/DPX-Mojo`](https://github.com/bivex/DPX-Mojo) | SIMD Hardware, Memory Lifetimes, AI Systems |
| 20 | **Move** | [`bivex/DPX-Move`](https://github.com/bivex/DPX-Move) | Aptos & Sui Resource Safety, Linear Types |
| 21 | **OCaml** | [`bivex/DPX-OCaml`](https://github.com/bivex/DPX-OCaml) | Algebraic Data Types, Functors, Polymorphism |
| 22 | **PHP** | [`bivex/DPX-Php`](https://github.com/bivex/DPX-Php) | Modern PHP 8.4, Attributes, Traits, Laravel |
| 23 | **Prolog** | [`bivex/DPX-Prolog`](https://github.com/bivex/DPX-Prolog) | ISO Prolog, SWI-Prolog, DCG, CLP(FD/R/Q), CHR, Meta-Interpreters |
| 24 | **Puppet** | [`bivex/DPX-Puppet`](https://github.com/bivex/DPX-Puppet) | Puppet DSL, Roles/Profiles, IaC Security, Hiera |
| 25 | **Python** | [`bivex/DPX-Py`](https://github.com/bivex/DPX-Py) | Metaprogramming, Protocols, Hexagonal DDD |
| 26 | **Ruby** | [`bivex/DPX-Ruby`](https://github.com/bivex/DPX-Ruby) | Ruby 3.x, Rails, Metaprogramming, Dry-RB, Security |
| 27 | **Rust** | [`bivex/DPX-Rust`](https://github.com/bivex/DPX-Rust) | Zero-Cost Abstractions, Borrow Checker, Traits |
| 28 | **Solidity** | [`bivex/DPX-Solidity`](https://github.com/bivex/DPX-Solidity) | DeFi Security, Reentrancy, EVM Yul/Assembly |
| 29 | **SQL** | [`bivex/DPX-SQL`](https://github.com/bivex/DPX-SQL) | PostgreSQL, MySQL, SQLite, T-SQL, PL/SQL |
| 30 | **Swift** | [`bivex/DPX-Swift`](https://github.com/bivex/DPX-Swift) | Protocol-Oriented Programming, Actors |
| 31 | **TypeScript** | [`bivex/DPX-TypeScript`](https://github.com/bivex/DPX-TypeScript) | Generics, Conditional Types, Clean Architecture |
| 32 | **Yul** | [`bivex/DPX-Yul`](https://github.com/bivex/DPX-Yul) | EVM Intermediate Representation Optimization |
| 33 | **Zig** | [`bivex/DPX-Zig`](https://github.com/bivex/DPX-Zig) | Comptime, Manual Memory Allocators, C ABI |

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
