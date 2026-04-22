# Call — History

## Project Context
- **Project:** Logic_app_ADO_learfield
- **Stack:** Azure Logic Apps, Azure DevOps (GHAzDO), ARM/JSON templates, Service Hooks
- **Description:** Automatically creates ADO work items when security vulnerabilities are detected. Originally built with Logic Apps, now exploring simpler no-code alternatives.
- **User:** Saurabh
- **Customer:** Michael Hubicka — pushed back on Logic App approach (too much infrastructure). Wants simplest path possible.
- **Joined:** 2026-04-21

## Core Context
- Main project goal: GHAzDO security alert → auto-create ADO work item → auto-close when resolved
- Customer wants ZERO or near-zero infrastructure
- Parker identified Make.com free tier (1,000 ops/month) as a genuine zero-cost automation option
- Zapier is a strong SaaS alternative — ADO Service Hooks natively support Zapier as a consumer
- ADO Service Hooks have 17+ built-in consumers
- GHAzDO alert events: `advancedsecurity.alert.created` and `advancedsecurity.alert.stateChanged`
- Current workflow (Logic App): HTTP trigger → parse alert → compose work item → check dedup via WIQL → create/close via ADO REST API
- Work item needs: title with alert type prefix, HTML description table, tags for dedup (GHAzDO-{repo}-{alertId}), priority based on severity
- Existing Logic App JSON: `ghazdo-to-ado.json` in repo root

## Learnings

### Make.com ADO Module Capabilities (2026-04-21)
- Make.com's Azure DevOps module supports: Create Work Item, Update Work Item, Get Work Item (by ID), List Work Items (basic)
- Make.com's ADO module does NOT support: WIQL queries, tag-based search, or advanced filtering
- Workaround for dedup/auto-close: Use generic HTTP module with ADO REST API WIQL endpoint
- This costs 1 extra operation per event but enables reliable tag-based dedup and work item lookup
- PAT must be stored as scenario variable and base64-encoded for HTTP module Authorization header
- ADO module connection uses PAT directly (no manual encoding needed)

### Make.com Free Tier Operations Math
- Webhook receive = 1 op, JSON parse = 1 op, HTTP request = 1 op, ADO create/update = 1 op
- Router = 0 ops (flow control, not counted)
- Full create cycle: 4 ops; Full close cycle: 3-4 ops; Full lifecycle: 7-8 ops
- Free tier (1,000 ops/month) = ~125-142 full alert cycles/month
- Sufficient for most dev teams with < 100 unique security alerts/month

### Make.com Implementation Delivered (2026-04-21)
- Complete approach at `approaches/04-make-com/`
- 10 files: README, scenario blueprint, webhook schema, service hook config, ADO connection guide, scenario design, test plan, expected results, limitations, PDF report
- Key architecture: Webhook -> JSON Parse -> Router -> (Branch 1: WIQL dedup + Create) / (Branch 2: WIQL find + Close)
- PDF report generated: `Make_Com_Implementation.pdf`

### ADO Native Zapier Consumer Does NOT Support GHAzDO Events (2026-04-21)
- ADO Service Hooks list Zapier as a native consumer, but it only supports standard events (work item, code push, build, release)
- GHAzDO `advancedsecurity.alert.*` events are NOT available through the native Zapier consumer
- Workaround: Use Web Hooks consumer pointing to Zapier's Catch Hook URL — functionally identical
- This is a critical finding for any team considering the "native" Zapier path

### Zapier Implementation Delivered (2026-04-21)
- Complete approach at `approaches/05-zapier/`
- 10 files: README, zap-create-work-item.md, zap-close-work-item.md, service-hook-config.json, webhook-payload-schema.json, field-mapping.md, test-plan.md, expected-results.md, limitations.md, PDF report
- Key architecture: ADO Service Hook (Web Hooks) -> Zapier Catch Hook -> Code by Zapier (parse) -> WIQL dedup search -> Create/Close work item
- Two Zaps needed: Zap #1 (alert created -> create work item, 5-6 steps), Zap #2 (state changed -> close work item, 5-6 steps)
- Starter tier ($20/mo) minimum — free tier cannot handle multi-step Zaps or webhooks
- Full alert lifecycle costs ~9-10 Zapier tasks; Starter supports ~75 cycles/month
- PDF report generated: `Zapier_Implementation.pdf`

### 2026-04-22 — Fleet Implementation Session
- Orchestrated parallel implementation of 5 approaches spanning Dallas, Brett, and Call agents
- Approach #4 (Make.com): 1167s, 10 files + PDF — confirmed HTTP workaround for WIQL, zero-cost full automation
- Approach #5 (Zapier): 1140s, 10 files + PDF — confirmed native consumer limitation, Web Hooks workaround identical
- Consolidated 5 decision records into central decisions.md; all findings merged and deduplicated
- Created orchestration logs and session log documenting fleet outcomes
- Updated Call history to reflect both Approach #4 and #5 completions

