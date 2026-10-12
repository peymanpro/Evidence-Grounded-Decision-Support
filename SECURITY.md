# Security Policy

Evidence-Grounded Decision Support is intended to handle sensitive decision context. Security issues should be treated seriously.

## Reporting

Do not publish credentials, private data, or an exploitable vulnerability in a public issue.

For a private installation, report the issue directly to the repository owner with enough information to reproduce it safely.

## Security expectations

- Keep secrets in environment configuration, never source control.
- Treat external model providers as untrusted boundaries.
- Do not expose an unauthenticated private deployment to the public internet.
- Do not place sensitive decision data in logs or test fixtures.
- Keep database credentials out of documentation and examples.
- Validate and constrain all externally supplied identifiers and URLs before network access is enabled.

## Scope

The project is not currently a regulated financial service, broker, custodian, or autonomous execution system. Security hardening must be completed before any public deployment handling real sensitive data.
