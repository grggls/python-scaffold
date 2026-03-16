# Security Policy

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, email the maintainers directly at: **you@example.com**

Include the following in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if any)

## Response Timeline

- **Acknowledgment**: Within 48 hours of receipt
- **Initial assessment**: Within 5 business days
- **Resolution target**: Within 30 days for critical issues

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | ✅        |

## Security Update Process

1. Security patches are released as soon as possible after verification
2. A security advisory is published on GitHub
3. The fix is included in the next release

## Security Practices

This project enforces security through:

- **Static analysis**: Ruff `S` (bandit) and `B` (bugbear) rules catch common security issues
- **SAST**: Semgrep runs in CI with taint-tracking and data-flow analysis
- **Dependency scanning**: `pip-audit` checks for known CVEs in dependencies
- **Secret detection**: gitleaks pre-commit hook blocks committed secrets
- **Type safety**: mypy strict mode prevents implicit `Any` from hiding untrusted data
- **Container security**: Non-root Docker user, multi-stage builds, HEALTHCHECK
- **CI least privilege**: GitHub Actions workflow uses `permissions: contents: read`
