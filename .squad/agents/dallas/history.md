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

