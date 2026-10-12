"""Auto layout: derive layers from the edges (Sugiyama-style).

Given a diagram, build the graph of **top-level items** (standalone nodes,
groups and tables) from its edges, then:

1. drop back edges with a deterministic DFS (cycle-safe),
2. assign each item a layer by longest path from the sources,
3. order items within each layer by a fixed number of barycenter passes to
   reduce edge crossings.

The result is a tuple of :class:`~flowlite.model.Layer` that the existing
``layered`` engine places left-to-right — no new placement math.

Everything is deterministic: declaration-order iteration, fixed pass counts and
stable sorts.
"""

from __future__ import annotations

from ..model import Diagram, Layer

BARYCENTER_PASSES = 4


def _top_item_id(diagram: Diagram, node_id: str) -> str | None:
    """Map a node id to its top-level item id (its group, or itself)."""
    for node in diagram.nodes:
        if node.id == node_id:
            return node.group or node.id
    # A group or table id used directly by an edge.
    for group in diagram.groups:
        if group.id == node_id:
            return group.id
    for table in diagram.tables:
        if table.id == node_id:
            return table.id
    return None


def _item_ids(diagram: Diagram) -> list[str]:
    """Top-level item ids in declaration order (nodes, groups, tables)."""
    ids: list[str] = [n.id for n in diagram.nodes if not n.group]
    ids.extend(g.id for g in diagram.groups)
    ids.extend(t.id for t in diagram.tables)
    return ids


def _graph(diagram: Diagram, items: list[str]) -> dict[str, list[str]]:
    """Adjacency of top-level items from the edges (deduped, no self-loops)."""
    adj: dict[str, list[str]] = {it: [] for it in items}
    seen: set[tuple[str, str]] = set()
    for edge in diagram.edges:
        src = _top_item_id(diagram, edge.src)
        dst = _top_item_id(diagram, edge.dst)
        if src is None or dst is None or src == dst:
            continue
        if (src, dst) in seen:
            continue
        seen.add((src, dst))
        adj[src].append(dst)
    return adj


def _drop_back_edges(items: list[str], adj: dict[str, list[str]]) -> dict[str, list[str]]:
    """Return a DAG: DFS in declaration order, dropping edges to the open stack."""
    forward: dict[str, list[str]] = {it: [] for it in items}
    state: dict[str, int] = {}  # 0=unseen, 1=on stack, 2=done

    def visit(start: str) -> None:
        stack: list[tuple[str, int]] = [(start, 0)]
        state[start] = 1
        while stack:
            node, i = stack[-1]
            if i < len(adj[node]):
                stack[-1] = (node, i + 1)
                nxt = adj[node][i]
                if state.get(nxt, 0) == 1:
                    continue  # back edge: drop it
                forward[node].append(nxt)
                if state.get(nxt, 0) == 0:
                    state[nxt] = 1
                    stack.append((nxt, 0))
                # already done -> forward/cross edge, keep
            else:
                state[node] = 2
                stack.pop()

    for it in items:
        if state.get(it, 0) == 0:
            visit(it)
    return forward


def _longest_path_layers(
    items: list[str], forward: dict[str, list[str]]
) -> dict[str, int]:
    """Longest-path layering on the DAG, via a declaration-order Kahn sort."""
    indeg: dict[str, int] = {it: 0 for it in items}
    for src in items:
        for dst in forward[src]:
            indeg[dst] += 1

    layer: dict[str, int] = {it: 0 for it in items}
    # Seed in declaration order for determinism.
    queue = [it for it in items if indeg[it] == 0]
    head = 0
    while head < len(queue):
        node = queue[head]
        head += 1
        for nxt in forward[node]:
            layer[nxt] = max(layer[nxt], layer[node] + 1)
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)

    # Kahn leaves cyclic remnants unvisited; assign them a completing layer so
    # nothing is silently dropped.
    max_layer = max(layer.values(), default=0)
    for it in items:
        if indeg[it] > 0:
            layer[it] = max_layer + 1
    return layer


def _barycenter(
    columns: list[list[str]], forward: dict[str, list[str]], passes: int
) -> list[list[str]]:
    """Reduce crossings by barycenter sweeps (stable, fixed pass count)."""
    # Neighbours in both directions, by position lookup.
    back: dict[str, list[str]] = {it: [] for col in columns for it in col}
    for src, dsts in forward.items():
        for dst in dsts:
            back[dst].append(src)

    for p in range(passes):
        if p % 2 == 0:
            order = range(1, len(columns))
        else:
            order = range(len(columns) - 2, -1, -1)
        for i in order:
            ref = {it: idx for idx, it in enumerate(columns[i - 1 if p % 2 == 0 else i + 1])}
            neigh = back if p % 2 == 0 else forward
            positions = {it: idx for idx, it in enumerate(columns[i])}

            def key(item: str) -> float:
                ns = [ref[n] for n in neigh.get(item, []) if n in ref]
                return sum(ns) / len(ns) if ns else positions[item]

            columns[i] = sorted(columns[i], key=key)  # stable
    return columns


def derive_layers(diagram: Diagram) -> tuple[Layer, ...]:
    """Derive ordered layers for ``diagram`` from its edges."""
    items = _item_ids(diagram)
    if not items:
        return ()

    adj = _graph(diagram, items)
    connected = {it for it, ns in adj.items() if ns} | {
        n for ns in adj.values() for n in ns
    }

    forward = _drop_back_edges(items, adj)
    layer = _longest_path_layers(items, forward)

    # Disconnected items trail in a final layer, in declaration order.
    trailing = [it for it in items if it not in connected]
    if trailing:
        trail_layer = max(layer.values(), default=-1) + 1 if connected else 0
        for it in trailing:
            layer[it] = trail_layer

    by_layer: dict[int, list[str]] = {}
    for it in items:  # declaration order preserved per layer
        by_layer.setdefault(layer[it], []).append(it)

    columns = [by_layer[k] for k in sorted(by_layer)]
    if connected:
        columns = _barycenter(columns, forward, BARYCENTER_PASSES)

    return tuple(
        Layer(index=i, ids=tuple(col)) for i, col in enumerate(columns)
    )
