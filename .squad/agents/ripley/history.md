# Ripley — History

## Project Context
- **Project:** Logic_app_ADO_learfield
- **Stack:** Azure Logic Apps, Azure DevOps (GHAzDO), ARM/JSON templates, Service Hooks
- **What it does:** Automatically creates ADO work items when security vulnerabilities are detected (secret scanning, Dependabot, GHAzDO alerts) via Azure Logic Apps
- **User:** Saurabh

## Learnings

### Session 1: Learfield Simplification Analysis (2025)
- **Issue Identified:** Customer finds current fully-automated Logic App too complex; wants "click a button to create work item from alert" UX instead
- **Asset Inventory Completed:**
  - 2 production-ready Logic App workflows (450+ lines each)
  - 3 Bicep modules for infrastructure (clean, parameterized)
  - 5 PowerShell deployment scripts (production-hardened)
  - 14+ PDF/Markdown docs (high documentation overhead)
  - 40+ visual assets (excellent for reference, may need refresh)
  - ~1500 lines of production code (85% reusable across options)

- **Pain Points:**
  1. Automation is forced, not optional
  2. Webhook deployment requires deep knowledge (Azure + GitHub + ADO)
  3. 14+ guides create analysis paralysis
  4. No UI for user-initiated "create work item" action

- **Strategy Recommended:**
  - **Phase 1:** Option A (One-Click Deploy Button) — wrap Bicep in ARM template, deploy button
  - **Phase 2:** Option B (ADO Extension with "Create Work Item" button) — user stays in ADO, direct control
  - Keep auto-close capability (high-value feature unchanged)
  - Reject Option D (ADO native rules insufficient for payload complexity)

- **Reuse Strategy:**
  - Core workflow logic (JSON) = 100% reusable
  - Bicep infrastructure = reusable with parameterization
  - Scripts = wrap in deploy button (Option A)
  - Documentation = retire most, create focused quickstarts per option

- **Decision Written:** `.squad/decisions/inbox/ripley-simplification-strategy.md`

