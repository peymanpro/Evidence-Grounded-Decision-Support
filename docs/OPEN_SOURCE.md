# Public Release and Maintenance

This repository is public and uses the MIT License.

## Public repository practices

- Keep credentials, private decision data, production database dumps, and real personal financial records out of Git.
- Use synthetic data in tests and examples.
- Keep implemented behavior distinct from roadmap intentions in documentation.
- Run the CI checks on changes to application code.
- Keep security reporting instructions visible and do not disclose exploitable issues in public issues.
- Keep external-provider calls explicitly configured and credential-driven.

## Before handling real user data

Public source availability is separate from production readiness. Before deploying a hosted instance with real or sensitive data, review the full Git history for accidentally committed secrets or private data; review dependencies and licenses; verify authentication, authorization, data isolation, logging hygiene, backups, and deployment configuration; and complete deeper adversarial and security testing.

If a credential is found in Git history, revoke or rotate it immediately. Removing the current file does not invalidate a credential that may already have been exposed.
