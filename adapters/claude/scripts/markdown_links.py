#!/usr/bin/env python3
"""Parse Markdown destinations used by the Claude package adapter."""

from __future__ import annotations

import re
from dataclasses import dataclass


INLINE_LINK = re.compile(
    r"(?P<image>!)?\[[^]\n]*\]\(\s*"
    r"(?P<destination><[^>\n]+>|[^\s)]+)"
    r"(?:\s+(?:\"[^\"\n]*\"|'[^'\n]*'|\([^\n)]*\)))?\s*\)"
)
REFERENCE_LINK = re.compile(
    r"(?P<image>!)?\[(?P<text>[^]\n]+)\]\[(?P<label>[^]\n]*)\]"
)
REFERENCE_DEFINITION = re.compile(
    r"^[ \t]{0,3}\[(?P<label>[^]\n]+)\]:[ \t]*"
    r"(?P<destination><[^>\n]+>|[^\s]+)(?:[ \t]+.*)?$",
    re.MULTILINE,
)
SHORTCUT_REFERENCE = re.compile(r"(?P<image>!)?\[(?P<label>[^]\n]+)\]")


@dataclass(frozen=True)
class MarkdownDestination:
    """One resolved Markdown link destination and its source span."""

    raw: str
    start: int
    end: int

    @property
    def target(self) -> str:
        """Return the destination without optional angle brackets."""
        return self.raw[1:-1] if self.raw.startswith("<") and self.raw.endswith(">") else self.raw

    def replace_target(self, target: str) -> str:
        """Preserve angle-bracket destination syntax when replacing a target."""
        return f"<{target}>" if self.raw.startswith("<") and self.raw.endswith(">") else target


@dataclass(frozen=True)
class ParsedMarkdownLinks:
    """Resolved destinations plus explicit unresolved reference labels."""

    destinations: tuple[MarkdownDestination, ...]
    unresolved_references: tuple[str, ...]


def normalized_reference_label(label: str) -> str:
    """Normalize a Markdown reference label for case-insensitive matching."""
    return " ".join(label.split()).casefold()


def _overlaps(span: tuple[int, int], occupied: list[tuple[int, int]]) -> bool:
    return any(span[0] < end and start < span[1] for start, end in occupied)


def parse_markdown_links(text: str) -> ParsedMarkdownLinks:
    """Resolve inline and full, collapsed, or shortcut reference links."""
    definitions: dict[str, re.Match[str]] = {}
    occupied: list[tuple[int, int]] = []
    for match in REFERENCE_DEFINITION.finditer(text):
        definitions.setdefault(normalized_reference_label(match["label"]), match)
        occupied.append(match.span())

    destinations: list[MarkdownDestination] = []
    for match in INLINE_LINK.finditer(text):
        occupied.append(match.span())
        if not match["image"]:
            start, end = match.span("destination")
            destinations.append(MarkdownDestination(match["destination"], start, end))

    referenced_definitions: set[str] = set()
    unresolved: list[str] = []
    for match in REFERENCE_LINK.finditer(text):
        occupied.append(match.span())
        if match["image"]:
            continue
        label = match["label"] or match["text"]
        normalized = normalized_reference_label(label)
        if normalized in definitions:
            referenced_definitions.add(normalized)
        else:
            unresolved.append(label)

    for match in SHORTCUT_REFERENCE.finditer(text):
        if _overlaps(match.span(), occupied) or match["image"]:
            continue
        normalized = normalized_reference_label(match["label"])
        if normalized in definitions:
            referenced_definitions.add(normalized)

    for label in sorted(referenced_definitions):
        definition = definitions[label]
        start, end = definition.span("destination")
        destinations.append(MarkdownDestination(definition["destination"], start, end))

    destinations.sort(key=lambda destination: destination.start)
    return ParsedMarkdownLinks(tuple(destinations), tuple(unresolved))
