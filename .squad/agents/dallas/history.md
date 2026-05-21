# Dallas — History

## Project Context
- **Project:** Logic_app_ADO_learfield
- **Stack:** Azure Logic Apps, Azure DevOps (GHAzDO), ARM/JSON templates, Service Hooks
- **What it does:** Automatically creates ADO work items when security vulnerabilities are detected (secret scanning, Dependabot, GHAzDO alerts) via Azure Logic Apps
- **User:** Saurabh

## Learnings

### GHAzDO Alert-to-ADO Work Item Alternatives (2025)

**Researched 6 viable alternatives** to Logic Apps for creating ADO work items from GHAzDO security alerts:

1. **ADO Native "Related Work" Linking** (NEW in 2024-2025, RECOMMENDED)
   - Built-in button in GHAzDO alert UI to create/link work items
   - Zero maintenance, free, exact UX customer wants ("click a button")
   - Trade-off: manual (not automatic like Logic App)
   - Quick rollout: enable GHAzDO, use button

2. **Power Automate** (RECOMMENDED if automation needed)
   - Lower complexity than Logic Apps, business-friendly UI
   - $15–75/month, much simpler setup (30 min vs Logic App weeks)
   - Achieves full automation but not "click a button" UX
   - Better choice if customer rejects manual workflow

3. **Azure Functions + GitHub Webhooks**
   - Cheapest (~$0/month), requires code (C#/Python/Node)
   - Medium maintenance burden, high developer overhead
   - No UI button—fully automatic
   - Not recommended unless team has spare dev resources

4. **Service Hooks + REST API Scripts**
   - Self-hosted (VM/Heroku/Lambda), requires scripting
   - High operational burden, not suitable for Learfield
   - Only if customer insists on no cloud dependencies

5. **Custom ADO Extension**
   - Would add perfect "button" UX but overkill now that ADO has native linking
   - 2–4 week dev, high maintenance, not worth it
   - Only viable if Marketplace commercialization goal

6. **YAML Pipeline Approach**
   - Wrong use case—only works on code push, not retroactive alerts
   - Not suitable for GHAzDO scanning workflow

**Decision:** Recommend ADO native linking + Power Automate fallback. Document stored in `.squad/decisions/inbox/dallas-ado-alternatives.md`.

**Key insight:** Microsoft just shipped native work item linking in ADO Advanced Security (2024-2025), making it the simplest solution. Learfield can likely decommission Logic App entirely if manual workflow acceptable.

### Deployment & Maintenance Strategy Research (2025)

**Research Focus:** How to achieve "deploy once, never touch again" for full GHAzDO→ADO automation (auto-create + auto-close).

**Evaluated 5 deployment approaches:**

1. **"Deploy to Azure" Button** ✅ RECOMMENDED
   - One-click deployment from README badge
   - Works with existing Bicep templates (no conversion needed)
   - Already have working `deploy-autoclose.bicep` (28 lines, 3 params)
   - Outputs trigger URL automatically → customer pastes into ADO service hook (2 min manual setup)
   - **First-time setup: 5 minutes, zero ongoing maintenance**
   - Implementation: Add 1 markdown line + 1-page ADO setup guide to docs

2. **ADO Service Hook Auto-Configuration** (HYBRID APPROACH RECOMMENDED)
   - Full automation via Bicep extensions: NOT viable (Microsoft moving away from Bicep extensions)
   - Hybrid approach: Deploy button provisions Logic App + outputs trigger URL, customer manually adds service hook (2 clicks, 2 min)
   - Better than full auto because: simpler, more transparent, no hidden state drift

3. **Power Automate Alternative** ❌ NOT RECOMMENDED
   - Simpler UX (drag-drop), but UI-based (no version control)
   - No "Deploy to Azure" equivalent—requires manual flow import
   - Cloud-state drift over time (updates change flow behavior unpredictably)
   - Cost: $15–75/month (vs Logic App ~$50–100)
   - Better for ad-hoc automation, not "deploy and forget"

4. **Azure Functions Alternative** ❌ NOT RECOMMENDED
   - Cheapest (~$0–10/month), but requires code (Python/C#/Node)
   - High operational burden: code testing, CI/CD, debugging, logs
   - Learfield stated no bandwidth for maintenance
   - Better for teams with dev resources, not operators

5. **Self-Hosted REST Scripts** ❌ NOT RECOMMENDED
   - Customer's server runs webhook listener + ADO API calls
   - High ops burden: patching, monitoring, restarts, security
   - Contradicts "deploy and forget" goal

**Key Findings:**
- Current `deploy-autoclose.bicep` is 90% ready for "Deploy to Azure" button
- Deployment outputs (trigger URL) are already configured
- Needs: (1) button markdown in README, (2) 1-page ADO service hook setup guide, (3) e2e testing
- Logic App is BETTER than alternatives for "deploy and forget" because: IaC (version-controlled), no code, Microsoft-managed, fully automated initial deploy
- Hybrid approach (button + 2-min manual service hook) = best UX+ops balance

**Document:** `.squad/decisions/inbox/dallas-automation-approach.md`

### Approach #1 Implementation — Native ADO Button + Work Item Templates (2026)

**Implemented full deliverable set** for Approach #1 (Phase 1 of phased strategy):

**Files created in `approaches/01-native-ado-button/`:**
- `README.md` — Complete step-by-step guide with exact ADO navigation paths for template creation, area path setup, using the Add button, board automation rules, custom process rules, and dashboard queries
- `implementation/work-item-template.json` — Exportable template definition with tags (GHAzDO; security; triage), area path, priority 2, severity 2-High, and structured HTML description with remediation steps and acceptance criteria
- `implementation/board-automation-rules.md` — Auto-assign on Active, auto-close on Done, auto-reopen, swimlane configuration, recommended board columns with WIP limits
- `implementation/custom-process-rules.md` — 5 process rules (auto-prioritize, auto-assign security lead, require closure justification, route to Security area, prevent closing without verification) plus optional custom fields (Alert Type picklist, Alert URL, Security Verified checkbox)
- `implementation/dashboard-query.wiql` — 4 WIQL queries: open items, priority breakdown, recently closed (30d), aging items (>7d)
- `validation/test-plan.md` — 5 tests covering all 3 alert types, template pre-fill verification, and board rule triggers
- `validation/expected-results.md` — Success metrics (template adoption, triage SLA, resolution time, coverage, stale items)
- `validation/limitations.md` — Full capabilities assessment with 7 documented limitations and upgrade signals
- `Native_ADO_Button_Implementation.pdf` — 15-section professional PDF comprehensive enough for standalone implementation

**Key design decisions:**
- Used Bug type (not Task) for security findings — aligns with severity/priority fields and standard security triage workflows
- Template includes acceptance criteria checklist for consistent closure verification
- Priority mapping: Critical→1, High→2 (default), Medium→3, Low→4
- Recommended inherited process for full rule enforcement but documented board-only path as simpler alternative

**Fleet Implementation:** Orchestrated 2026-04-22 with teams Dallas (Approach #1), Brett (Approaches #2-3), and Call (Approaches #4-5) to deliver complete phased automation strategy. Approach #1 confirms Phase 1 viability as zero-cost, ~10-minute entry point.

### Container Scanning Demo Setup (2026)

**Implemented demo-ready GitHub container scanning** for `sautalwar/ghas-ado-logic-app` using a simple Docker image, Trivy SARIF uploads, and Dependabot monitoring.

**Architecture decisions and patterns:**
- Use **Trivy + SARIF + `github/codeql-action/upload-sarif@v3`** so container findings land in **GitHub Security → Code scanning alerts** instead of living only in workflow logs.
- Keep the workflow **demo-friendly and non-blocking** with `exit-code: "0"`, allowing alerts to appear in the Security tab without failing the run.
- Trigger on both **`main` and `master`** because the live repo default branch is `master`, while demo instructions may still reference `main`.
- Split the workflow into **image scanning** and **Dockerfile config scanning** so the demo can show both package CVEs and configuration findings.
- Intentionally use an **older Python bullseye image plus outdated Python packages** to make findings visible immediately during a live demo.

**Key file paths:**
- `Dockerfile` — demo image definition
- `container-demo/requirements.txt` — intentionally outdated packages for scanning
- `.github/workflows/container-scan.yml` — build + Trivy + SARIF workflow
- `.github/dependabot.yml` — Docker base image monitoring
- `docs/container-scanning-demo.md` — live demo walkthrough

**User preference captured:** Saurabh asked for a clear, working, demo-ready GitHub container scanning setup tied back to the existing ADO/Logic App story.

