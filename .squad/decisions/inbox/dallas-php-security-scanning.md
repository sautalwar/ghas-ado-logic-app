# Dallas Decision — PHP Security Demo Scanning Pattern

## Status
Proposed

## Summary
Use a legacy PHP 7.4 Apache container plus SARIF-first workflows to demonstrate container scanning, external VM scanning, markdown review, and secret scanning in one GitHub-native security story.

## Decision
- Switch the container demo from static Python content to a realistic legacy PHP app running on `php:7.4-apache`
- Use outdated Composer packages so Trivy can surface both OS and PHP library findings
- Keep the external-VM pattern centered on **Trivy CLI + SARIF upload**, because that matches how customers often run scanners outside GitHub Actions
- Treat secret scanning enablement as a **GitHub setting/API concern**, not a repo file, and use a custom demo token pattern for safe walkthroughs
- Treat markdown instruction files as review-worthy security artifacts and publish their findings through SARIF into GitHub Security

## Why
This keeps the demo aligned with the customer's actual PHP estate and their external scanner mental model, while still landing every signal back in the GitHub Security experience. It also avoids using real credentials in source control while preserving a realistic secret-scanning walkthrough.

## Files
- `Dockerfile`
- `container-demo/composer.json`
- `container-demo/index.php`
- `container-demo/config-example.php`
- `.github/workflows/external-vm-scan.yml`
- `scripts/external-scan.sh`
- `docs/secret-scanning-demo.md`
- `.github/workflows/markdown-security-scan.yml`
- `scripts/scan-markdown-security.py`
- `docs/markdown-security-scanning-demo.md`
