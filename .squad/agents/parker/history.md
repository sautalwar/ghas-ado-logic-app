# Parker — History

## Project Context
- **Project:** Logic_app_ADO_learfield
- **Stack:** Azure Logic Apps, Azure DevOps (GHAzDO), ARM/JSON templates, Service Hooks
- **Description:** Automatically creates ADO work items when security vulnerabilities are detected. Originally built with Logic Apps, now exploring all automation alternatives.
- **User:** Saurabh
- **Customer:** Michael Hubicka — pushed back on Logic App approach (too much infrastructure to maintain). Wants simpler path.
- **Joined:** 2026-04-21

## Core Context
- Customer feedback: Logic App adds infrastructure their team has to maintain — not ideal
- Native ADO "Add" button already recommended as Phase 1 (zero setup)
- Team already evaluated 6 approaches in decisions.md (native ADO, Power Automate, Azure Functions, REST API, custom extension, YAML)
- Need fresh evaluation with customer simplicity as #1 priority
- Key question: What's the SIMPLEST way to automate GHAzDO alert → ADO work item for a team that wants minimal maintenance?

## Learnings

### 2026-04-21: Comprehensive Automation Alternatives Analysis
- Evaluated **14 approaches** (expanded from Dallas's original 6) for GHAzDO → ADO work item automation
- **New approaches identified:** Zapier, Azure Automation Runbook, Scheduled Polling Script, GitHub Actions, Sentinel Playbook, Event Grid + Function, Third-Party ITSM
- **Key finding:** Zapier is a strong Phase 2 alternative — ADO Service Hooks natively support Zapier, no Azure infra needed, SaaS model aligns with Michael's "no infrastructure" preference
- **Hidden gem:** ADO Work Item Templates can enhance the native "Add" button experience by pre-filling fields (tags, area path, priority)
- **ADO Custom Process Rules** can auto-set fields on security-tagged work items but CANNOT create work items from alerts
- **Confirmed:** Phased approach (Native ADO → Power Automate/Zapier → Logic App) is correct strategy
- **Decision output:** `.squad/decisions/inbox/parker-automation-alternatives.md`
- **Key customer file:** `Customer_Reply_Michael_Hubicka_Short.html` — the reply already sent recommending native button
- **Existing workflow definition:** `ghazdo-to-ado.json` — full Logic App with dedup, severity mapping, auto-close

### 2026-04-21: Deep Dive — 21 Approaches Evaluated
- Expanded from 14 to **21 approaches** after creative deep dive
- **HIDDEN GEM FOUND:** Azure Boards App for Teams + Service Hook Notifications = automated alerts + one-click work item creation, zero cost, zero infrastructure, ~15 min setup
- **New approaches added:** Azure Boards for Teams combo (#15), Teams Workflows (#16), Make.com (#17), n8n (#18), Browser Bookmarklet (#19), Tampermonkey Userscript (#20), Email/ITSM Chain (#21)
- **Make.com free tier** is a genuine zero-cost automation option (1,000 ops/month free — enough for most security alert volumes)
- **Teams Workflows** = Power Automate inside Teams without separate license — many teams don't know this exists
- **Things confirmed NOT to exist:** GHAzDO auto-create work items, ADO email-to-work-item (cloud), Board rules that create items, Copilot auto-triage, GHAzDO marketplace extensions for this use case
- **ADO Service Hooks have 17+ built-in consumers** including Teams, Slack, Zapier, Trello, Office 365, Service Bus, Storage Queue
- **Revised recommendation:** Native "Add" Button → Teams Notifications + Boards App (new Phase 1.5) → Make.com/Zapier/Logic App (Phase 2)
- **PDF report generated:** `Parker_Automation_Alternatives_Report.pdf`
- **Decision output:** `.squad/decisions/inbox/parker-deep-dive-simplest.md`

### 2026-04-21: Team Coordination
- **Team updates:** Decision records now in `.squad/decisions.md` with full detail for Ash (Power Automate findings) and Kane (environment compatibility)
- **Phased approach revised:** Phase 1.5 (Teams Notifications + Boards App) inserted between Phase 1 (native button) and Phase 2 (full automation)
- **Impact:** Learfield now has multiple zero-cost automation pathways (Phase 1.5, Make.com free tier, Teams Workflows) in addition to Logic App
- **Customer messaging:** Phase 1.5 should be emphasized in next communication with Michael — zero infrastructure, zero cost, immediate team notification benefit

### 2026-04-22: Final Comparative Analysis PDF Created
- Generated `Final_Comparison_All_Approaches.pdf` — comprehensive side-by-side comparison of all 5 approaches
- **All 5 approach READMEs read and synthesized** into 7-section analysis document
- **Key deliverable sections:** Executive Summary, Comparison Matrix (10 criteria x 5 approaches), Validation Assessment (7 criteria), Recommendation Tiers (3 tiers), Decision Flowchart, Migration Path, Key Findings & Gotchas
- **Validation scorecard:** Make.com (#4) and Zapier (#5) both score 7/7; Native ADO (#1) scores 4/7; Teams+Boards (#2) scores 4.5/7; Teams Workflows (#3) scores 5/7
- **Recommended path confirmed:** #1 Native ADO (today, 10 min, free) → #2 Teams+Boards (this week, 15 min, free) → #4 Make.com (when ready, 45 min, free)
- **8 critical gotchas documented** including: ADO Zapier consumer doesn't support GHAzDO events, Make.com ADO module lacks WIQL, Teams Workflows dedup requires Premium, Zapier free tier can't handle webhooks
- **Decision output:** `.squad/decisions/inbox/parker-final-comparison.md`
