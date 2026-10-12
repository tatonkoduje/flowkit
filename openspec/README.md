# OpenSpec — spec-driven development

This folder is the living specification for FlowLite, using
[OpenSpec](https://github.com/Fission-AI/OpenSpec) conventions.

```
openspec/
├── project.md                 # project context
├── spec.md                    # the current, agreed specification
└── changes/                   # in-flight change proposals
    └── <change-id>/
        ├── proposal.md        # why, what, scope
        ├── design.md          # technical approach
        └── tasks.md           # implementation checklist
```

## How it works

Significant changes are agreed **before** code: create
`openspec/changes/<change-id>/`, review it, then implement. When done, fold the
requirements into `spec.md` and remove the proposal. Trivial fixes skip this.

Requirements are plain Markdown, each with at least one scenario:

```markdown
### Requirement: Deterministic rendering
The renderer SHALL produce byte-identical SVG for identical input.

#### Scenario: Recompiling an unchanged source
- **WHEN** the same source is compiled twice
- **THEN** the two SVG files are byte-for-byte identical
```

## Current changes

| Change | Status |
|---|---|
| [0001 walking-skeleton](changes/archive/0001-walking-skeleton/proposal.md) | done (archived) |
| [0002 shapes](changes/archive/0002-shapes/proposal.md) | done (archived) |
| [0003 edge styling](changes/archive/0003-edge-styling/proposal.md) | done (archived) |

FlowLite is built as a **sequence of small changes**; see
[`changes/README.md`](changes/README.md) for the roadmap.

The [OpenSpec CLI](https://github.com/Fission-AI/OpenSpec) is optional
(`npm i -g @fission-ai/openspec`); this repo works by following the folder
conventions directly.
