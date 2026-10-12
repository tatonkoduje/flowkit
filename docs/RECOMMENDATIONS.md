# Recommendations — from FlowKit & Mermaid to FlowLite

> Why FlowLite exists: what the predecessors do well, where they fall short, and
> the design direction. Input to [`openspec/spec.md`](../openspec/spec.md).

## 1. The problem

Diagrams should be **reviewable** (text, diffable), **regenerable**
(deterministic) and **beautiful enough to present** (gradients, shadows, icons,
clean type). Existing tools force a trade-off: text-first tools look generic,
good-looking tools are heavy or GUI-bound.

## 2. Mermaid

**Strengths:** the de-facto standard; familiar syntax; renders everywhere; broad
diagram coverage.

**Weaknesses for a "beautiful diagram" goal:** JS + Dagre/ELK rendering in the
browser (heavy, hard-to-version SVG); layout is hard to control and reflows
unpredictably; plain defaults (flat fills, no shadows, no icons without registering
packs); theming means fighting `themeVariables`.

Mermaid wins on coverage and ubiquity. It is the wrong tool when deliberate,
presentation-grade aesthetics are the primary goal.

## 3. FlowKit (the predecessor)

**Strengths — keep:** zero dependencies, single-file compilers; presentation-first
rendering (gradient cards, `feDropShadow`, vendored lucide icons, curated themes);
rich shapes (`card`, `db`, `hub`, `hex`, `pill`, `diamond`, `polyN`, `table`);
distinctive layouts (layered + radial with polygon-face docking); real edge
anchoring (ray-casting); design tokens in one place; clickable nodes.

**Weaknesses — fix:** bespoke imperative syntax (manual `layer` placement,
steeper than Mermaid); no automatic layout; look hard-coded in Python; two DSLs
(`.flow` + `.uml`) is more than a minimalist tool should carry; themes/shapes not
extensible as data.

## 4. Direction for FlowLite

Keep FlowKit's **rendering quality and zero-dependency ethos**, borrow Mermaid's
**learnability**.

**Principles**
1. Minimal surface — one DSL, great defaults, no ceremony.
2. Beauty by default — gradients, shadows, curated palettes, a real icon set.
3. Deterministic, reviewable output.
4. Aesthetics as data — themes/icons are files, not code.
5. Familiar where possible — readable to anyone who knows Mermaid.

**Concrete recommendations**
- **One DSL (`.fl`)**, Mermaid-compatible concepts, dotted attributes (`icon=`, `kind=`).
- **Pluggable layout**: directed layout first, then radial/tree; keep manual
  `layer`/`radial` overrides for control.
- **Theme packs as data** with premium presets, replacing hard-coded themes.
- **Icons**: vendor a small curated set (lucide, ISC) + project-local icons; tint by `kind`.
- **Design tokens** exposed per theme (spacing, radii, shadow, fonts).
- **Determinism as a test**: golden-file SVG tests for every example.
- **Accessibility**: escape text, keep contrast checks in CI.

**Non-goals (for now):** matching Mermaid's diagram breadth; a GUI; third-party
runtime dependencies in the core.

## 5. Success criteria

- A newcomer produces a good-looking diagram in under five minutes from the README.
- The same source renders identically everywhere.
- The whole look can change without editing compiler code.
- Every example is covered by a golden-file test.

## 6. Attribution

- **Mermaid** — https://mermaid.js.org (MIT) — syntax-familiarity reference.
- **FlowKit** — internal predecessor; rendering approach.
- **lucide** — https://lucide.dev (ISC) — bundled icon set.
