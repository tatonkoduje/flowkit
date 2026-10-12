"""FlowLite diagram model.

Frozen dataclasses represent a parsed diagram. Every stage of the pipeline
(parse -> measure -> layout -> render) reads and returns these; nothing here
depends on the other stages.
"""

from __future__ import annotations

from dataclasses import dataclass, field

_AMP = chr(38)  # &


def esc(text: str) -> str:
    """XML-escape text for safe inclusion in SVG.

    Entities are built at runtime so this module's source stays free of literal
    markup characters.
    """
    return (
        text.replace(_AMP, _AMP + "amp;")
        .replace("<", _AMP + "lt;")
        .replace(">", _AMP + "gt;")
        .replace('"', _AMP + "quot;")
    )


@dataclass(frozen=True)
class Node:
    """A single shape in the diagram."""

    id: str
    label: str
    kind: str = "default"
    shape: str = "card"
    group: str = ""
    icon: str = ""
    link: str = ""
    # Assigned by measurement (0 until measured).
    width: float = 0.0
    height: float = 0.0
    # Assigned by layout (0 until placed).
    x: float = 0.0
    y: float = 0.0


@dataclass(frozen=True)
class Group:
    """A translucent background frame containing member nodes."""

    id: str
    title: str
    kind: str = "default"
    # Assigned by measurement/layout.
    width: float = 0.0
    height: float = 0.0
    x: float = 0.0
    y: float = 0.0


@dataclass(frozen=True)
class Table:
    """A titled grid of rows, rendered with a header and cell grid."""

    id: str
    title: str
    kind: str = "default"
    header: tuple[str, ...] = ()
    rows: tuple[tuple[str, ...], ...] = ()
    # Assigned by measurement (0 until measured).
    width: float = 0.0
    height: float = 0.0
    # Assigned by layout (0 until placed).
    x: float = 0.0
    y: float = 0.0

    @property
    def columns(self) -> int:
        """Column count: the header width, or the widest row if headerless."""
        if self.header:
            return len(self.header)
        return max((len(row) for row in self.rows), default=0)


@dataclass(frozen=True)
class Layer:
    """An ordered column of node/group ids for the layered layout."""

    index: int
    ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Radial:
    """Radial (hub-and-spoke) layout parameters."""

    hub: str
    radius: float | None = None  # None -> derived from hub size + gap
    start: float = -90.0  # degrees; first spoke, clockwise
    dock: bool = False
    gap: float = 70.0


@dataclass(frozen=True)
class Edge:
    """A connector between two nodes."""

    src: str
    dst: str
    label: str = ""
    style: str = "normal"  # normal | dashed | bold
    arrow: str = "normal"  # normal | dot | none
    curve: str = "bezier"  # bezier | straight


@dataclass(frozen=True)
class Diagram:
    """A whole diagram: header, nodes, groups and edges, in declaration order."""

    title: str = "Diagram"
    subtitle: str = ""
    theme: str = "midnight"
    nodes: tuple[Node, ...] = field(default_factory=tuple)
    groups: tuple["Group", ...] = field(default_factory=tuple)
    edges: tuple[Edge, ...] = field(default_factory=tuple)
    layers: tuple[Layer, ...] = field(default_factory=tuple)
    radial: "Radial | None" = None
    tables: tuple[Table, ...] = field(default_factory=tuple)
    auto_layout: bool = False
