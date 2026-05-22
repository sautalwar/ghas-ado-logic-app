---
updated_at: 2026-05-22T07:28:00Z
focus_area: GitHub Container Security Demo for Learfield
active_issues: []
---

# What We're Focused On

Building a comprehensive GitHub Advanced Security demo for Learfield (Michael Hubicka) — customer runs PHP applications in containers.

## Current State (2026-05-22)

### Completed This Session
1. **Container Scanning** — PHP 7.4 Dockerfile + Trivy workflow (`container-scan.yml`), verified live on GitHub Actions
2. **External VM Scanning** — `external-vm-scan.yml` + `scripts/external-scan.sh` (VM scans container, uploads SARIF to GHAS)
3. **Secret Scanning** — Docs + custom pattern scripts (`scripts/create-secret-scanning-pattern.sh`)
4. **Markdown/Instruction File Security** — `markdown-security-scan.yml` + `scripts/scan-markdown-security.py` (flags AI instruction files for security review)
5. **HTML Overview** — `GitHub_Container_Security_Demo.html` (polished dark-theme overview page)

### In Progress
- Nothing — all deliverables complete and pushed.

### Also Completed
6. **Step-by-step Walkthrough HTML** — `GitHub_Container_Security_Walkthrough.html` (26 steps, [DO]/[SAY]/[SHOW]/[WHY] tags, sidebar nav, progress bar)

### Repo Status
- All changes pushed to GitHub ✅
- Repo set to **private** ✅
- Secrets cleaned from git history (filter-branch) ✅
- Session transcript file removed (contained ADO PAT patterns)

### Key Files
- `Dockerfile` — PHP 7.4 Apache with intentional vulnerabilities
- `container-demo/` — PHP demo app (index.php, requirements.txt)
- `.github/workflows/container-scan.yml` — Trivy container scanning
- `.github/workflows/external-vm-scan.yml` — External VM scan pattern
- `.github/workflows/markdown-security-scan.yml` — MD file security scanner
- `scripts/external-scan.sh` — VM-side scanning script
- `scripts/scan-markdown-security.py` — Python markdown scanner
- `docs/container-scanning-demo.md` — Container scanning docs
- `docs/secret-scanning-demo.md` — Secret scanning docs
- `docs/markdown-security-scanning-demo.md` — Markdown security docs
- `GitHub_Container_Security_Demo.html` — Overview HTML
- `GitHub_Container_Security_Walkthrough.html` — 26-step live demo runbook
- Live workflow run: https://github.com/sautalwar/ghas-ado-logic-app/actions/runs/26240845316

### Customer Context
- Customer: Learfield / Michael Hubicka
- Stack: PHP applications in containers
- Use case: External VM scans PHP containers, uploads SARIF to GitHub Advanced Security
- Also wants: Secret scanning + markdown/instruction file security scanning
- Repo: https://github.com/sautalwar/ghas-ado-logic-app

### Resume Instructions
1. All deliverables are complete and pushed — no pending work
2. Ask Saurabh what's next: run the demo, adjust content, or start a new feature
3. Both HTML files are ready to open in browser for the customer demo
