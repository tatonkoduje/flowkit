# Security Policy

## Supported versions

FlowLite is pre-1.0. Security fixes are applied to the latest release and the
`main` branch.

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Report privately using GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
("Security" tab → "Report a vulnerability"), or email the maintainers.

Include:

- A description of the issue and its impact.
- Steps to reproduce (a minimal `.fl` source is ideal).
- Affected versions/commit.

You can expect an acknowledgement within a few days. We will keep you informed
as we work on a fix and credit you in the advisory unless you prefer otherwise.

## Scope notes

FlowLite parses untrusted text and renders SVG. Areas of interest:

- XML/HTML escaping in labels (SVG injection).
- `link=` handling (clickable anchors) — arbitrary URLs in output.
- PNG export — it shells out to external tools; treat source input as untrusted.
