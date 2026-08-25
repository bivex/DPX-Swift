"""High-speed native parser adapter for Swift source code."""

from __future__ import annotations

import re
from pattern_detector.domain.code_model import (
    CodeModel,
    SwiftFile,
    SwiftMethod,
    SwiftProperty,
    SwiftType,
)
from pattern_detector.domain.value_objects import SourceLocation
from pattern_detector.ports.outbound import ParserPort


class NativeSwiftParserAdapter(ParserPort):
    """Linear, robust parser extracting Swift AST declaration semantics."""

    IMPORT_PATTERN = re.compile(r"^\s*import\s+([A-Za-z0-9_.]+)")
    TYPE_HEADER_PATTERN = re.compile(
        r"^(?P<attrs>(?:@\w+(?:\([^)]*\))?\s+)*)"
        r"(?P<modifiers>(?:public|private|fileprivate|internal|open|final|indirect)\s+)*"
        r"(?P<kind>class|struct|enum|actor|protocol|extension)\s+"
        r"(?P<name>[A-Za-z0-9_]+)"
        r"(?:<(?P<generics>[^>]+)>)?"
        r"(?:\s*:\s*(?P<inherits>[^{]+))?"
    )
    METHOD_HEADER_PATTERN = re.compile(
        r"^(?P<attrs>(?:@\w+(?:\([^)]*\))?\s+)*)"
        r"(?P<modifiers>(?:public|private|fileprivate|internal|open|static|class|final|mutating|nonmutating|override)\s+)*"
        r"(?P<kind>func|init)\s*"
        r"(?P<name>[A-Za-z0-9_]+)?"
        r"\s*\((?P<params>[^)]*)\)"
        r"(?:\s*(?P<async>async))?"
        r"(?:\s*(?P<throws>throws|rethrows))?"
        r"(?:\s*->\s*(?P<return_type>[^{]+))?"
    )
    PROPERTY_PATTERN = re.compile(
        r"^(?P<attrs>(?:@\w+(?:\([^)]*\))?\s+)*)"
        r"(?P<modifiers>(?:public|private|fileprivate|internal|open|static|class|final|weak|unowned|lazy)\s+)*"
        r"(?P<mutability>let|var)\s+"
        r"(?P<name>[A-Za-z0-9_]+)"
        r"(?:\s*:\s*(?P<type_name>[^=;\n{]+))?"
        r"(?:\s*=\s*(?P<init>[^;\n{]+))?"
    )
    ASSOCIATED_TYPE_PATTERN = re.compile(r"^\s*associatedtype\s+([A-Za-z0-9_]+)")

    BRANCH_KEYWORDS = re.compile(r"\b(if\s+|guard\s+|switch\s+|case\s+|for\s+|while\s+|catch\b|&&|\|\||\?\s*[^:]+\s*:)")

    def parse_file(self, file_path: str, content: str) -> SwiftFile:
        lines = content.splitlines()
        file_obj = SwiftFile(file_path=file_path, raw_content=content, lines=lines)

        # 1. Imports
        for line in lines:
            m = self.IMPORT_PATTERN.match(line)
            if m:
                file_obj.imports.append(m.group(1))

        # 2. Extract Types and Methods through single-pass state machine
        current_type: SwiftType | None = None
        brace_depth = 0
        type_brace_depth = 0
        method_brace_depth = 0
        current_method: SwiftMethod | None = None
        current_method_body: list[str] = []
        pending_attributes: list[str] = []

        for line_idx, raw_line in enumerate(lines, 1):
            trimmed = raw_line.strip()

            # Skip pure comments
            if trimmed.startswith("//") or trimmed.startswith("/*") or trimmed.startswith("*"):
                continue

            # Capture standalone attribute annotations (e.g. @MainActor, @propertyWrapper)
            if trimmed.startswith("@") and not any(kw in trimmed for kw in ("class", "struct", "enum", "actor", "protocol", "extension", "func", "var", "let")):
                pending_attributes.append(trimmed)
                continue

            # Check Type Header
            type_match = self.TYPE_HEADER_PATTERN.match(trimmed)
            if type_match and brace_depth == 0:
                kind = type_match.group("kind")
                name = type_match.group("name")
                generics_str = type_match.group("generics") or ""
                inherits_str = type_match.group("inherits") or ""
                attrs_str = type_match.group("attrs") or ""

                all_attrs = pending_attributes + [a.strip() for a in attrs_str.split() if a.startswith("@")]
                pending_attributes = []

                generics = [g.strip() for g in generics_str.split(",") if g.strip()]
                inherits = [inh.strip() for inh in inherits_str.split(",") if inh.strip()]

                ext_target = name if kind == "extension" else None

                current_type = SwiftType(
                    name=name,
                    kind=kind,
                    inherited_types=inherits,
                    attributes=all_attrs,
                    generic_parameters=generics,
                    extension_target=ext_target,
                    location=SourceLocation(file_path=file_path, line=line_idx, column=1),
                    raw_text=raw_line,
                )
                type_brace_depth = brace_depth
                file_obj.types.append(current_type)

            # Check Associated Types inside protocols
            if current_type and current_type.kind == "protocol":
                assoc_match = self.ASSOCIATED_TYPE_PATTERN.match(trimmed)
                if assoc_match:
                    current_type.associated_types.append(assoc_match.group(1))

            # Check Property
            prop_match = self.PROPERTY_PATTERN.match(trimmed)
            if prop_match and not trimmed.startswith("func ") and not trimmed.startswith("init"):
                p_name = prop_match.group("name")
                p_mut = prop_match.group("mutability")
                p_type = (prop_match.group("type_name") or "").strip()
                p_init = (prop_match.group("init") or "").strip()
                p_attrs_str = prop_match.group("attrs") or ""
                p_mods_str = prop_match.group("modifiers") or ""

                p_attrs = pending_attributes + [a.strip() for a in p_attrs_str.split() if a.startswith("@")]
                pending_attributes = []

                prop = SwiftProperty(
                    name=p_name,
                    type_name=p_type,
                    is_let=(p_mut == "let"),
                    is_static=("static" in p_mods_str or "class" in p_mods_str),
                    is_weak=("weak" in p_mods_str),
                    is_unowned=("unowned" in p_mods_str),
                    is_private=("private" in p_mods_str or "fileprivate" in p_mods_str),
                    attributes=p_attrs,
                    initializer=p_init or None,
                    location=SourceLocation(file_path=file_path, line=line_idx, column=1),
                    raw_text=raw_line,
                )
                if current_type:
                    current_type.properties.append(prop)
                else:
                    file_obj.global_properties.append(prop)

            # Check Method Header
            method_match = self.METHOD_HEADER_PATTERN.match(trimmed)
            if method_match:
                m_kind = method_match.group("kind")
                m_name = method_match.group("name") or ("init" if m_kind == "init" else "anonymous")
                m_params_str = method_match.group("params") or ""
                m_async = bool(method_match.group("async"))
                m_throws = bool(method_match.group("throws"))
                m_ret = (method_match.group("return_type") or "Void").strip()
                m_attrs_str = method_match.group("attrs") or ""
                m_mods_str = method_match.group("modifiers") or ""

                m_attrs = pending_attributes + [a.strip() for a in m_attrs_str.split() if a.startswith("@")]
                pending_attributes = []

                params: list[tuple[str, str]] = []
                for p in m_params_str.split(","):
                    p_clean = p.strip()
                    if ":" in p_clean:
                        p_name, p_type = p_clean.split(":", 1)
                        params.append((p_name.strip(), p_type.strip()))
                    elif p_clean:
                        params.append((p_clean, "Any"))

                current_method = SwiftMethod(
                    name=m_name,
                    parameters=params,
                    return_type=m_ret,
                    is_static=("static" in m_mods_str or "class" in m_mods_str),
                    is_mutating=("mutating" in m_mods_str),
                    is_async=m_async,
                    is_throwing=m_throws,
                    is_private=("private" in m_mods_str or "fileprivate" in m_mods_str),
                    attributes=m_attrs,
                    location=SourceLocation(file_path=file_path, line=line_idx, column=1),
                    raw_text=raw_line,
                )
                current_method_body = [raw_line]
                method_brace_depth = brace_depth

                if current_type:
                    current_type.methods.append(current_method)
                else:
                    file_obj.global_functions.append(current_method)

            # Accumulate method body and count branch points
            if current_method:
                current_method_body.append(raw_line)
                branches = len(self.BRANCH_KEYWORDS.findall(raw_line))
                current_method.branch_count += branches

            # Track brace depth
            open_braces = raw_line.count("{")
            close_braces = raw_line.count("}")
            brace_depth += open_braces - close_braces

            if current_method and brace_depth <= method_brace_depth and close_braces > 0:
                current_method.body = "\n".join(current_method_body)
                current_method = None
                current_method_body = []

            if current_type and brace_depth <= type_brace_depth and close_braces > 0:
                if current_type.location:
                    current_type.line_count = line_idx - current_type.location.line + 1
                current_type = None

        return file_obj

    def parse_codebase(self, files: list[tuple[str, str]], target_path: str = "") -> CodeModel:
        model = CodeModel(target_path=target_path)
        for fpath, content in files:
            swift_file = self.parse_file(fpath, content)
            model.files.append(swift_file)
        return model
