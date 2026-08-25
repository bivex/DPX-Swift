"""In-memory Code Model for Swift AST and declaration semantics."""

from __future__ import annotations

from dataclasses import dataclass, field
from pattern_detector.domain.value_objects import SourceLocation


@dataclass
class SwiftProperty:
    """Represents a property / variable / constant declaration in Swift."""

    name: str
    type_name: str
    is_let: bool = False
    is_static: bool = False
    is_weak: bool = False
    is_unowned: bool = False
    is_private: bool = False
    attributes: list[str] = field(default_factory=list)  # e.g. ["@Published", "@State", "@Binding"]
    initializer: str | None = None
    location: SourceLocation | None = None
    raw_text: str = ""


@dataclass
class SwiftMethod:
    """Represents a function / method / initializer in Swift."""

    name: str
    parameters: list[tuple[str, str]] = field(default_factory=list)  # (param_name, param_type)
    return_type: str = "Void"
    is_static: bool = False
    is_mutating: bool = False
    is_async: bool = False
    is_throwing: bool = False
    is_private: bool = False
    attributes: list[str] = field(default_factory=list)  # e.g. ["@MainActor", "@Sendable"]
    body: str = ""
    branch_count: int = 1
    location: SourceLocation | None = None
    raw_text: str = ""


@dataclass
class SwiftType:
    """Represents a class, struct, enum, actor, protocol, or extension in Swift."""

    name: str
    kind: str  # "class", "struct", "enum", "actor", "protocol", "extension"
    inherited_types: list[str] = field(default_factory=list)  # superclasses & protocol conformances
    attributes: list[str] = field(default_factory=list)  # e.g. ["@MainActor", "@propertyWrapper", "@resultBuilder"]
    generic_parameters: list[str] = field(default_factory=list)
    associated_types: list[str] = field(default_factory=list)
    properties: list[SwiftProperty] = field(default_factory=list)
    methods: list[SwiftMethod] = field(default_factory=list)
    nested_types: list[SwiftType] = field(default_factory=list)
    extension_target: str | None = None  # for extensions: e.g. "extension User : Codable" -> target is "User"
    line_count: int = 1
    location: SourceLocation | None = None
    raw_text: str = ""


@dataclass
class SwiftFile:
    """Represents a parsed Swift source file."""

    file_path: str
    imports: list[str] = field(default_factory=list)
    types: list[SwiftType] = field(default_factory=list)
    global_functions: list[SwiftMethod] = field(default_factory=list)
    global_properties: list[SwiftProperty] = field(default_factory=list)
    raw_content: str = ""
    lines: list[str] = field(default_factory=list)


@dataclass
class CodeModel:
    """Aggregated repository model across all parsed Swift files."""

    files: list[SwiftFile] = field(default_factory=list)
    target_path: str = ""

    @property
    def all_types(self) -> list[SwiftType]:
        result: list[SwiftType] = []
        for f in self.files:
            for t in f.types:
                result.append(t)
                result.extend(t.nested_types)
        return result

    @property
    def protocols(self) -> list[SwiftType]:
        return [t for t in self.all_types if t.kind == "protocol"]

    @property
    def actors(self) -> list[SwiftType]:
        return [t for t in self.all_types if t.kind == "actor"]

    @property
    def classes(self) -> list[SwiftType]:
        return [t for t in self.all_types if t.kind == "class"]

    @property
    def structs(self) -> list[SwiftType]:
        return [t for t in self.all_types if t.kind == "struct"]

    @property
    def extensions(self) -> list[SwiftType]:
        return [t for t in self.all_types if t.kind == "extension"]

    @property
    def all_methods(self) -> list[SwiftMethod]:
        result: list[SwiftMethod] = []
        for f in self.files:
            result.extend(f.global_functions)
            for t in f.types:
                result.extend(t.methods)
                for nested in t.nested_types:
                    result.extend(nested.methods)
        return result
