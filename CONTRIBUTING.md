# Contributing to FlowLite

Thanks for your interest. FlowLite is built **spec-first**: we agree on *what*
to build before writing code.

## Ground rules

- **Be minimal.** FlowLite values a small surface area. A new feature must earn
  its place by removing more complexity than it adds.
- **Be deterministic.** Given the same source, the compiler must produce
  byte-identical SVG (no timestamps, no randomness, stable ordering).
- **Stay dependency-free.** The core uses the Python 3 standard library only.
  Optional PNG export shells out to whatever is installed — never import third-party packages in the core.
- **Beauty is a feature.** Changes to default colors, spacing or typography are
  API changes; treat them as such.

## Workflow

1. **Discuss first.** Open a GitHub Discussion or Issue for anything beyond a
   trivial fix. For significant work, propose it in `openspec/changes/` (see below).
2. **Fork and branch.** `git checkout -b feature/<short-name>`.
3. **Implement with tests.** `python3 -m pytest`.
4. **Keep the diff tight.** One logical change per pull request.
5. **Open a PR** using the template and link the related issue/change.

## Spec-driven changes (OpenSpec)

Significant features, refactors and architectural changes need a proposal
before code. Create `openspec/changes/<change-id>/` containing:

- `proposal.md` — why, what, and scope.
- `design.md` — technical approach.
- `tasks.md` — implementation checklist.

Requirements (with scenarios) fold into [`openspec/spec.md`](openspec/spec.md)
when the change lands.

See [`openspec/README.md`](openspec/README.md) and the example proposal in
[`openspec/changes/`](openspec/changes/).

## Development

```bash
# run the CLI against an example
PYTHONPATH=src python3 -m flowlite examples/hello.fl -o build/hello.svg --png

# run the test suite
python3 -m pytest

# lint / format (optional, if the tooling is present)
ruff check .
ruff format .
```

## Code style

- Target Python 3.10+.
- No third-party imports in `src/flowlite/`.
- Pure functions for parsing, measuring, layout and rendering where practical.
- Keep files focused; the renderer should be readable top-to-bottom.

## Commit messages

Use short, imperative subjects (`Add radial dock layout`, `Fix edge anchor for hex`).
Reference issues where relevant (`Fixes #12`).

## Code of Conduct

By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

By contributing you agree your contributions are licensed under the MIT License.
