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

### 3. ADO Work Item Linking Strategy (2026-04-14)
**Status:** ADOPTED  
**Owner:** Dallas (Azure DevOps Expert)  
**Summary:** Provide phased adoption path: native ADO linking (simple, free) → Power Automate (if automation needed) → Logic App (if full integration required).

**Approach:**
- **Phase 1:** Use native ADO "Related Work" button (click to create work item from alert, no infrastructure)
- **Phase 2:** If manual workflow insufficient, evaluate Power Automate (low-code, $15–75/month)
- **Phase 3:** If full automation + auto-close required, deploy Logic App (via Deploy button)

**Advantages of Phased Approach:**
- Allows customer to start with zero cost/complexity
- Reduces risk by validating requirements before investment
- Preserves option for full automation without forcing it
- Aligns with "complexity as customer choice" principle

**Key Trade-offs Evaluated:**
| Approach | Setup | Cost | Auto-create | Auto-close | Maintenance |
|----------|-------|------|-------------|-----------|-------------|
| Native ADO | 0 min | Free | Manual click | Manual | None |
| Power Automate | 30 min | $15–75/mo | ✅ Auto | ✅ Auto | Low (UI drift) |
| Logic App | 5 min* | $50–100/mo | ✅ Auto | ✅ Auto | None |
| Azure Functions | 2–4 hrs | $0–10/mo | ✅ Auto | ✅ Auto | High (code) |

*Including one-click deploy button

**Not Recommended:** YAML Pipeline (wrong use case), self-hosted REST API (operational burden)

**Related:** [dallas-ado-alternatives.md](.squad/decisions/inbox/dallas-ado-alternatives.md)

---

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Keep history focused on work, decisions focused on direction
