# Squad Decisions

## Active Decisions

### 1. Full Automation Approach (2026-04-14)
**Status:** ADOPTED  
**Owner:** Dallas (Azure DevOps Expert)  
**Summary:** Pivot from hybrid integration to full automation for GHAZDO-to-ADO Logic App. Full automation (auto-create + auto-close work items) determined optimal for reliability and cost. Logic App uses Designer-only approach (no Code View) for customer simplicity.

**Rationale:**
- 6 automation approaches evaluated (native ADO, Power Automate, Azure Functions, REST API, custom extension, YAML)
- Full automation superior to alternatives for use case fit, cost, and maintainability
- ADO native linking for manual creation (backup), Logic App for automation

**Decisions:**
- ✅ Deploy Logic App with ADO service hooks for full automation
- ✅ Designer-only workflow (no Code View editing) for customer UX
- ✅ Native ADO "Related Work" as optional lightweight alternative
- ✅ One-click "Deploy to Azure" button for simplified deployment

**Related:** [dallas-automation-approach.md](.squad/decisions/inbox/dallas-automation-approach.md), [dallas-ado-alternatives.md](.squad/decisions/inbox/dallas-ado-alternatives.md)

---

### 2. Deployment Strategy: "Deploy and Forget" (2026-04-14)
**Status:** ADOPTED  
**Owner:** Dallas (Azure DevOps Expert)  
**Summary:** Implement hybrid architecture combining native ADO for manual work item creation with one-click Logic App deployment for full automation. Minimizes maintenance burden while preserving feature richness.

**Key Architecture:**
- **Tier 1 (Manual):** Native ADO "Related Work" button (free, no infrastructure)
- **Tier 2 (Automated):** Logic App via Deploy button (one-click setup, Microsoft-managed)
- **Service Hook:** ADO webhook triggers Logic App; workflow handles create + auto-close

**Decision Details:**
- ✅ Use Bicep (not ARM) for infrastructure-as-code
- ✅ Deploy button in README for one-click customer setup (~5 minutes)
- ✅ Deployment outputs trigger URL for manual service hook configuration
- ✅ Create one-page ADO service hook setup guide (copy/paste instructions)
- ✅ Rejected alternatives: Power Automate (UI drift), Azure Functions (code maintenance), self-hosted (operational burden)

**Outcomes:**
- Complexity: Low for deployment (no CLI required)
- Maintenance: Zero ongoing (Microsoft-managed Logic App)
- Cost: ~$50–100/month fixed
- Time-to-value: 5 minutes initial setup

**Related:** [ripley-simplification-strategy.md](.squad/decisions/inbox/ripley-simplification-strategy.md)

---

### 3. ADO Work Item Linking Strategy (2026-04-14) — UPDATED 2026-04-21
**Status:** ADOPTED (revised with Phase 1.5)  
**Owner:** Dallas (Azure DevOps Expert)  
**Summary:** Provide phased adoption path: native ADO linking (simple, free) → Phase 1.5: Teams Notifications + Boards App (15 min, free) → Power Automate/Zapier/Make.com (if full automation needed) → Logic App (if enterprise grade + dedup + auto-close required).

**Revised Phased Approach:**

| Phase | Approach | Setup | Cost | Automation | Best For |
|-------|----------|-------|------|-----------|---------|
| **1** | Native ADO "Add" button | 0 min | Free | Manual click | Teams wanting zero complexity |
| **1.5** | Teams Notifications + Boards App | 15 min | Free | Notify + 1-click create | Teams wanting visibility without infra |
| **2a** | Make.com free tier | 30 min | Free (1K ops/mo) | Full automation | Low-volume alert teams |
| **2b** | Teams Workflows | 30 min | Free (M365) | Full automation | M365-native teams |
| **2c** | Zapier | 30 min | $10–50/mo | Full automation | Non-Azure-first teams |
| **2d** | Power Automate | 45–90 min | $15–75/mo | Full automation | Premium orgs, UI drift tolerance |
| **3** | Logic App | 5 min* | $50–100/mo | Full automation + dedup + auto-close | Enterprise, hardened requirements |
| **Alternative** | Azure Functions | 2–4 hrs | $0–10/mo | Full automation + dedup | Dev teams with code maintenance budget |

*Including one-click deploy button

**Key Advantages of Revised Phased Approach:**
- Allows customer to start with zero cost/complexity
- Introduces **Phase 1.5** (Teams + Boards) as compelling middle ground (zero infrastructure, automated notifications)
- Reduces risk by validating requirements before investment
- Preserves option for full automation without forcing it
- Aligns with "complexity as customer choice" principle
- Provides **three free automation paths** (Phase 1.5, Make.com, Teams Workflows)

**Why Phase 1.5 Matters (NEW):**
- ADO Service Hooks have 17+ built-in consumers; Teams is one of the simplest
- Azure Boards App for Teams enables one-click work item creation from notification messages
- Zero Azure infrastructure to deploy or maintain
- Eliminates manual checking of ADO alerts — team sees them automatically in Teams
- ~15 minutes total setup (just configure service hook)
- Natural bridge between pure-manual (Phase 1) and full automation (Phase 3)

**Not Recommended:** YAML Pipeline (wrong use case), self-hosted REST API (operational burden)

**Related:** 
- [ash-power-automate-feasibility.md](.squad/decisions/inbox/ash-power-automate-feasibility.md) — Power Automate detailed evaluation
- [parker-automation-alternatives.md](.squad/decisions/inbox/parker-automation-alternatives.md) — 14 approaches ranked
- [parker-deep-dive-simplest.md](.squad/decisions/inbox/parker-deep-dive-simplest.md) — 21 approaches evaluated; Phase 1.5 discovered

---

---

### 4. Power Automate NOT Recommended Despite Feasibility (2026-04-21)
**Status:** EVALUATED — NOT RECOMMENDED  
**Owner:** Ash (Power Automate Expert)  
**Date:** 2026-04-21  
**Summary:** Power Automate can technically replicate every step of the Logic App workflow (parse webhooks, compose expressions, create/close work items, dedup via WIQL, retry on failure). However, it is NOT recommended for Learfield because it doesn't reduce complexity, costs the same or more, and loses the one-click deploy advantage.

**Technical Feasibility:** ✅ YES  
Every Logic App step maps to Power Automate:
- HTTP Request trigger → "When HTTP request received" (Premium)
- Parse JSON, Compose, Conditional logic → identical capabilities
- Create/close work items → HTTP actions (Premium) or ADO connector (Standard for basic fields only)
- WIQL queries → HTTP actions (Premium; no native connector)

**Licensing Requirement:** 🔴 PREMIUM  
- HTTP Request trigger (webhook receiver) — Premium only ($15/user/mo or $100/flow/mo unattended)
- HTTP actions (WIQL queries, json-patch+json patches) — Premium only
- ADO connector (Standard) covers basic create/update but needs HTTP for advanced fields

**Key Gaps:**
1. **No one-click deploy** — Customer must manually build flow in designer or import Solution package
2. **Premium license required** — Minimum $15-100/month (same as Logic App, no advantage)
3. **No Managed Identity** — Logic App can use Azure Managed Identity; Power Automate cannot
4. **Version control friction** — Power Automate flows live in Dataverse (solution zip), not Git
5. **Environment dependency** — Requires Power Platform environment with Premium capacity
6. **UI drift risk** — Power Automate designer updates may require periodic re-validation

**Recommendation:** Stick with phased approach:
- **Tier 1:** Native ADO "Add" button (free, zero setup)
- **Tier 1.5:** Teams Notifications + Boards App (free, 15 min setup) — NEW
- **Tier 2:** Logic App with one-click deploy (if automation needed)
- **Tier 3 (deprioritized):** Power Automate only if customer is already invested in Power Platform

**Related:** [ash-power-automate-feasibility.md](.squad/decisions/inbox/ash-power-automate-feasibility.md)

---

### 5. Comprehensive Automation Alternatives: 14 Approaches Evaluated (2026-04-21)
**Status:** COMPLETED — DECISION RECORD  
**Owner:** Parker (Automation Architect)  
**Date:** 2026-04-21  
**Summary:** Evaluated 14 distinct automation approaches for GHAzDO→ADO work item integration, expanding Dallas's original 6 approaches. Confirmed phased strategy while identifying 7 new alternatives and hidden gems.

**14 Approaches Ranked by Simplicity:**

1. ✅ **Native ADO "Add" Button** (0 min, Free) — Best for teams wanting zero complexity
2. ✅ **ADO Service Hooks → Zapier** (30 min, $20–50/mo) — Strong Phase 2 for non-Azure teams
3. ⭐ **Power Automate** (45–90 min, $15–75/mo) — Feasible but not recommended (see Decision #4)
4. ✅ **Azure Logic App** (5 min*, $50–100/mo) — Best for enterprise + dedup + auto-close
5. ⭐ **Azure Automation Runbook** (2–3 hrs, $5–15/mo) — For teams with existing Automation accounts
6. ✅ **Azure Functions** (3–4 hrs, $0–10/mo) — Cheapest option; high code maintenance
7. ✅ **Scheduled Polling Script** (2–3 hrs, Free–$5/mo) — Familiar to ops teams; not real-time
8. ❌ **GitHub Actions** (3 hrs, Free) — Only works for GitHub repos, not ADO repos
9. ⭐ **Custom Webhook Receiver** (4+ hrs, $5–30/mo) — For teams with existing hosting
10. ✅ **Microsoft Sentinel + Playbook** (4+ hrs, $50–200+/mo) — For enterprise with Sentinel
11. ⭐ **Azure Event Grid + Function** (4 hrs, $0–15/mo) — For event-driven architectures
12. ❌ **YAML Pipeline** (2–3 hrs, Free) — CI/CD only; limited for alert response
13. ❌ **Custom ADO Extension** (weeks, custom cost) — Commercial product ambitions only
14. ⭐ **Third-Party ITSM** (4+ hrs, $50–500+/mo) — For enterprises with ServiceNow/PagerDuty

**Hidden Gems Found:**
- **Zapier:** Surprisingly simple no-code alternative with native ADO Service Hooks support
- **ADO Work Item Templates:** Can enhance Phase 1 by pre-filling tags, area path, priority in the "Add" button

**Confirmed Decision:**
Phased approach (Native ADO → Power Automate/Zapier → Logic App) is correct strategy for Learfield.

**Related:** [parker-automation-alternatives.md](.squad/decisions/inbox/parker-automation-alternatives.md)

---

### 6. Hidden Gem: Phase 1.5 — Teams Notifications + Boards App (2026-04-21)
**Status:** PROPOSED — RECOMMEND  
**Owner:** Parker (Automation Architect)  
**Date:** 2026-04-21  
**Summary:** After evaluating 21 automation approaches (expanded from 14), discovered Teams Notifications + Azure Boards App as compelling Phase 1.5: Automated alerts in Teams + one-click work item creation, zero infrastructure, zero cost, ~15 minutes setup.

**Why This Is the Right Answer for Michael Hubicka's Team:**

| Dimension | Phase 1.5 | Phase 1 | Phase 3 |
|-----------|-----------|---------|---------|
| **Setup** | 15 min | 0 min | 5 min* |
| **Cost** | Free | Free | $50–100/mo |
| **Infrastructure** | None | None | Azure Logic App |
| **Automation** | Alerts + 1-click | Manual | Full + dedup + auto-close |
| **Visibility** | Teams channel | ADO only | Logs + Monitor |
| **Maintenance** | None | None | None |

*With deploy button

**How It Works:**
1. ADO Project Settings → Service Hooks → Teams (built-in consumer)
2. Configure webhook: GHAzDO alert events → Teams channel
3. Alerts automatically appear in Teams as rich messages
4. Azure Boards App for Teams enables one-click work item creation from notification
5. Team gets instant visibility + triage capability without infrastructure

**Why Phase 1.5 Fills the Gap:**
- **Phase 1** (native "Add" button) = pure manual; team doesn't know alerts exist until they check ADO
- **Phase 1.5** (Teams) = alerts delivered to team + one-click creation from notification
- **Phase 3** (Logic App) = full automation + dedup + auto-close for enterprise requirements

**21 Approaches Now Evaluated:**

New approaches added in deep dive:
- ✅ Make.com free tier (1K ops/mo free — genuine zero-cost automation)
- ✅ Teams Workflows (Power Automate inside Teams without license)
- ⭐ **Azure Boards for Teams + Service Hook Notifications** (hidden gem)
- ✅ n8n (open-source workflow automation)
- ❌ Browser Bookmarklet (manual; not practical)
- ❌ Tampermonkey Userscript (local workaround; not for teams)
- ❌ Email/ITSM chain (unreliable; legacy approach)

**Key Findings:**
- ADO Service Hooks have **17+ built-in consumers** (Teams, Slack, Zapier, Trello, Office 365, Service Bus, Storage Queue, etc.)
- **Things confirmed NOT to exist:** GHAzDO auto-create work items, ADO email-to-work-item (cloud), Board rules that create items, Copilot auto-triage, GHAzDO marketplace extensions for this use case

**Recommendation:**
Revised phased approach (see Decision #3) now includes Phase 1.5 as standard recommendation for Learfield.
- Start with Phase 1 (native "Add" button) — zero friction
- Implement Phase 1.5 (Teams) immediately after — no additional cost, massive visibility improvement
- Phase 3 (Logic App) only if Phase 1.5 doesn't fully satisfy automation needs

**Deliverable:** `Parker_Automation_Alternatives_Report.pdf` — Comprehensive analysis of all 21 approaches with comparison tables, pros/cons, customer fit analysis

**Related:** [parker-deep-dive-simplest.md](.squad/decisions/inbox/parker-deep-dive-simplest.md)

---

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
