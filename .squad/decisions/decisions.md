# Team Decisions

## Container Security Demo Infrastructure (2026-05-21)

### Dallas Decision — GitHub Container Scanning Demo Pattern

**Status:** ✅ Accepted  

**Summary:** For the `ghas-ado-logic-app` demo, use a lightweight Docker image plus Trivy SARIF uploads so container findings appear in GitHub Security's code scanning experience.

**Decision:**
- Build a simple demo image from `Dockerfile`
- Seed the image with intentionally outdated packages for reliable demo findings
- Use GitHub Actions with Trivy to scan both the built image and the Dockerfile configuration
- Upload findings with `github/codeql-action/upload-sarif@v3`
- Keep the demo workflow non-blocking (`exit-code: 0`) so the run stays presentation-friendly while still surfacing alerts
- Enable Dependabot for the root Dockerfile so base image updates can be shown as follow-on remediation

**Rationale:** Gives Saurabh a single repo demo that is easy to trigger, easy to explain, and aligned with the existing GHAS-to-ADO automation narrative. Avoids needing a full application stack just to demonstrate container scanning.

**Implementation Files:**
- `Dockerfile`
- `container-demo/requirements.txt`
- `.github/workflows/container-scan.yml`
- `.github/dependabot.yml`
- `docs/container-scanning-demo.md`

---

### Dallas Decision — PHP Security Demo Scanning Pattern

**Status:** ✅ Accepted  

**Summary:** Use a legacy PHP 7.4 Apache container plus SARIF-first workflows to demonstrate container scanning, external VM scanning, markdown review, and secret scanning in one GitHub-native security story.

**Decision:**
- Switch the container demo from static Python content to a realistic legacy PHP app running on `php:7.4-apache`
- Use outdated Composer packages so Trivy can surface both OS and PHP library findings
- Keep the external-VM pattern centered on **Trivy CLI + SARIF upload**, matching customer external scanner mental model
- Treat secret scanning enablement as a **GitHub setting/API concern**, not a repo file, using a custom demo token pattern for safe walkthroughs
- Treat markdown instruction files as review-worthy security artifacts, publishing findings through SARIF into GitHub Security

**Rationale:** Keeps the demo aligned with the customer's actual PHP estate and their external scanner workflow, while landing every signal back in the GitHub Security experience. Avoids using real credentials in source control while preserving a realistic secret-scanning walkthrough.

**Implementation Files:**
- `Dockerfile` (PHP 7.4)
- `container-demo/composer.json`
- `container-demo/index.php`
- `container-demo/config-example.php`
- `.github/workflows/external-vm-scan.yml`
- `scripts/external-scan.sh`
- `docs/secret-scanning-demo.md`
- `.github/workflows/markdown-security-scan.yml`
- `scripts/scan-markdown-security.py`
- `docs/markdown-security-scanning-demo.md`

---

## Archive

*All prior decisions from .squad/decisions/inbox have been consolidated into this file.*
