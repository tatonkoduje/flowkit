# Design — 0004 Groups

## Model

```python
@dataclass(frozen=True)
class Group:
    id: str
    title: str
    kind: str = "default"
    # assigned by layout
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0
```

`Node` gains `group: str = ""`. `Diagram` gains `groups: tuple[Group, ...]`.

Membership is stored on the node; the parser attaches members to groups and
warns on an unknown group id (falling back to no group), matching the shapes
convention.

## Layout

Two-level: **top-level items** are standalone nodes *and* groups. Members are
removed from the top-level list (they live inside their group).

1. Measure each node (0002).
2. Measure each group from its members:
   - `mw, mh` = max member width/height.
   - `ncol = 1 if one member else 2`; `nrow = ceil(n / ncol)`.
   - `g.width = max(220, ncol*mw + (ncol+1)*GAP)`;
     `g.height = TITLE_BAR + nrow*mh + (nrow-1)*ROW_GAP + GAP`.
3. Stack top-level items vertically (single centered column, as now).
4. After a group is positioned, place its members in a grid inside the frame
   (using the same grid math), centered within the member area.

`stack.py` grows a `_place_members(group, members)` helper; the top-level engine
treats each group as a single box.

## Rendering

Order: background → title → **group frames** → edges → nodes.

A frame is a rounded rect, `fill=<kind first color>` at low opacity, dashed
border, with the group title in the kind color at the top-left (inside the
frame). Frames are drawn before edges so edges sit on top.

Edge anchoring to a group uses the rectangle border logic (group has x/y/w/h).

## Determinism

Declaration order drives member order, grid order and top-level order. No
generated ids.

## Test strategy

- Parser: `group` parsed; `in=` attaches; unknown `in=` warns + detaches.
- Layout: group sized to fit members (frame strictly contains member boxes).
- Render: frame `<rect ... stroke-dasharray>` emitted before nodes; group title
  present; edges to a group id render.
- Golden: `layers.fl`.
