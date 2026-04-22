# Brett — History

## Project Context
- **Project:** Logic_app_ADO_learfield
- **Stack:** Azure Logic Apps, Azure DevOps (GHAzDO), ARM/JSON templates, Service Hooks, Microsoft Teams
- **Description:** Automatically creates ADO work items when security vulnerabilities are detected. Originally built with Logic Apps, now exploring simpler alternatives including Teams-based integrations.
- **User:** Saurabh
- **Customer:** Michael Hubicka — pushed back on Logic App approach (too much infrastructure). Wants simplest path possible.
- **Joined:** 2026-04-21

## Core Context
- Main project goal: GHAzDO security alert → auto-create ADO work item → auto-close when resolved
- Customer wants ZERO infrastructure — Teams-based approach is attractive because they already use Teams
- Parker identified Azure Boards App for Teams + Service Hook Notifications as a "hidden gem" (zero cost, ~15 min setup)
- Teams Workflows are simplified Power Automate flows built into Teams — many teams don't know they exist
- ADO Service Hooks have 17+ built-in consumers including Teams, Slack, Zapier, Trello
- Current workflow (Logic App): HTTP trigger → parse alert → compose work item → check dedup → create/close via ADO REST API
- Existing Logic App JSON: `ghazdo-to-ado.json` in repo root

## Learnings

### 2026-04-21 — Approach #2 Implementation Complete
- Built full implementation of Phase 1.5: Azure Boards App for Teams + Service Hook Notifications
- Created 8 deliverables: README, service-hook-config.json, adaptive-card-template.json, boards-app-setup.md, teams-channel-setup.md, test-plan.md, expected-results.md, limitations.md
- Generated 17-page professional PDF report (Teams_Boards_App_Implementation.pdf)
- Key finding: fpdf2 requires latin-1 safe characters when using core fonts (no Unicode bullets/emojis)
- ADO Service Hook event types: `ms.vss-code.advancedsecurity-alert-created-event` and `ms.vss-code.advancedsecurity-alert-statechanged-event`
- The "Create Work Item" action in Azure Boards App works on ANY Teams message — not specific to service hook notifications
- Microsoft is deprecating Office 365 Connectors in Teams; Workflows (Power Automate) is the replacement for incoming webhooks
- This approach delivers ~80% of Logic App value at 0% cost — the primary trade-offs are manual work item creation and no auto-close/dedup

### 2026-04-21 — Approach #3: Teams Workflows Implementation Complete
- Built full implementation of Phase 2b: Teams Workflows (simplified Power Automate in Teams)
- Created 9 deliverables: README.md, webhook-payload-schema.json, workflow-definition.json, service-hook-config.json, workflow-steps.md, test-plan.md, expected-results.md, limitations.md, PDF report
- **Critical licensing finding:** ADO "Create a work item" connector is Standard (free with M365). HTTP connector for WIQL dedup is Premium ($15/user/mo). This means work item creation is free but deduplication requires paid license.
- Teams Workflows use "When a Teams webhook request is received" trigger — generates a unique HTTPS endpoint URL
- ADO connector in Teams Workflows uses OAuth sign-in (more secure than PATs, no expiration)
- Auto-close is the weakest point: requires finding work items by tag, which needs WIQL (Premium) or saved queries (coarse-grained)
- Recommended hybrid approach: Teams Workflow for creation (free) + Logic App for auto-close only
- Expression editor in Teams Workflows is basic — complex nested expressions should be built incrementally via multiple Compose steps
- Tag convention `GHAzDO-{repo}-{alertId}` enables manual dedup even without automated WIQL
- Rate limits (6,000 API calls/day per user) are sufficient for typical GHAzDO volumes (<100 alerts/day)

### 2026-04-22 — Fleet Implementation Session
- Orchestrated parallel implementation of 5 approaches spanning Dallas, Brett, and supporting cast agents
- Approach #1 (Native ADO): 934s, 8 files + PDF — confirmed Phase 1 zero-cost viability
- Approach #2 (Teams + Boards): 961s, 9 files + PDF — identified as compelling Phase 1.5 with zero infrastructure
- Approach #3 (Teams Workflows): 1045s, 9 files + PDF — confirmed free work item creation with Premium required for dedup
- Consolidated 5 decision records into central decisions.md; all decision findings merged and deduplicated
- Updated agent histories across Dallas, Brett, Call to reflect fleet outcomes
- Created orchestration logs and session log for fleet tracking
