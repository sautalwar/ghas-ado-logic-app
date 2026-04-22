# Kane — History

## Project Context
- **Project:** Logic_app_ADO_learfield
- **Stack:** Azure Logic Apps, Azure DevOps (GHAzDO), ARM/JSON templates, Service Hooks
- **What it does:** Automatically creates ADO work items when security vulnerabilities are detected (secret scanning, Dependabot, GHAzDO alerts) via Azure Logic Apps
- **User:** Saurabh

## Learnings

- **2025-07-15: Environment Compatibility Audit** — Audited both copies of `ghazdo-to-ado.json` (root + infra/workflows). Found them byte-identical. Key findings: (1) Close state `"Done"` is hardcoded in both the PATCH body and WIQL filter — will break on Agile/CMMI templates that use `"Closed"`. Must parameterize. (2) Work item type `"Issue"` is parameterized (good) but default doesn't work for Scrum template. (3) ADO API v7.1 is current and correct. (4) Tag format uses semicolons to create multiple ADO tags — intentional and useful for filtering. (5) No retry policies on HTTP actions — recommended adding exponential backoff. Full report: `.squad/decisions/inbox/kane-env-compatibility-audit.md`.
- **2025-07-15: Environment Compatibility Fix Applied** — Fixed all issues from the audit: (1) Added `closedState` parameter (default `"Done"`) to both JSON workflow copies and both Bicep files (`ghazdo-logic-app.bicep` + `deploy-full-automation.bicep`). (2) Replaced hardcoded `"Done"` in `HTTP_CloseWorkItem` PATCH body and `HTTP_FindWorkItemToClose` WIQL query with `@{parameters('closedState')}`. (3) Added exponential retry policies (3 retries, PT10S interval) to all 4 HTTP actions in both JSON copies. Workflow now works across Agile (`Closed`), Scrum (`Done`), Basic (`Done`), and CMMI (`Closed`) process templates.

### 2026-04-21: Team Discovery Context
- **Ash's feasibility analysis:** Power Automate CAN replicate the workflow but is NOT recommended for Learfield (premium license, no deploy button, shifts complexity)
- **Parker's deep-dive:** Evaluated 21 automation approaches; identified Teams Notifications + Boards App as Phase 1.5 (zero cost, zero infrastructure, ~15 min setup)
- **Impact on environment audit:** The `closedState` parameterization Kane recommended is now standard in phased approach — supports all ADO process templates for Logic App (Phase 3)
- **Alignment:** Environment compatibility audit ensures Logic App deployment works reliably across all Learfield variants and process templates

