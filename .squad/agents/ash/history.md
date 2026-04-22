# Ash — History

## Project Context
- **Project:** Logic_app_ADO_learfield
- **Stack:** Azure Logic Apps, Azure DevOps (GHAzDO), ARM/JSON templates, Service Hooks, Power Automate
- **Description:** Automatically creates ADO work items when security vulnerabilities are detected (secret scanning, Dependabot, GHAzDO alerts). Originally built with Logic Apps, now exploring Power Automate as alternative.
- **User:** Saurabh
- **Customer:** Michael Hubicka — pushed back on Logic App approach (too much infrastructure). Looking for simpler alternatives.
- **Joined:** 2026-04-21

## Core Context
- Customer prefers native ADO features and minimal infrastructure
- Logic App approach already built and functional but customer found it heavyweight
- Need to evaluate if Power Automate can deliver same functionality with less overhead
- Key workflow: GHAzDO alert → service hook → trigger → create ADO work item → auto-close on resolution

## Learnings

### Power Automate Feasibility Analysis (2026-04-21)
- **Verdict:** Power Automate CAN replicate the Logic App workflow, but with significant caveats
- **Key finding:** The HTTP Request trigger (webhook receiver) requires a Premium license ($15/user/month or $100/flow/month)
- **Key finding:** Power Automate has native ADO connectors but WIQL queries require the HTTP connector (Premium)
- **Key finding:** No "Deploy to Azure" button equivalent — customer must manually build the flow in the PA designer or import from a shared solution
- **Key finding:** ADO connector supports create/update work items natively, but custom field patches (json-patch+json) still need HTTP action
- **Architecture pattern:** The Logic App's HTTP → parse → compose → condition → HTTP pattern maps to PA's "When HTTP request received" → Parse JSON → Compose → Condition → HTTP actions
- **Customer context:** Michael Hubicka wants LESS infrastructure, not different infrastructure. Power Automate shifts complexity from Azure portal to Power Platform admin — not a net reduction
- **Decision:** Power Automate is technically feasible but NOT recommended over Logic App for this customer. Logic App with one-click deploy is simpler end-to-end
- **Key files:** ghazdo-to-ado.json (Logic App definition), Customer_Reply_Michael_Hubicka_Short.html (customer feedback)

### Team Discovery: Phase 1.5 Identified (2026-04-21)
- **Parker's deep-dive discovery:** Azure Boards App for Teams + ADO Service Hook Notifications provides compelling middle ground
- **Impact on recommendations:** Teams Notifications + Boards App is now Phase 1.5 in phased approach (zero cost, zero infrastructure, ~15 min setup)
- **Rationale:** While Power Automate is not recommended for Learfield, the phased approach now offers multiple free automation options (Phase 1.5, Make.com free tier, Teams Workflows)
- **Alignment:** Power Automate remains valid option only for orgs already invested in Power Platform ecosystem — confirms feasibility analysis conclusion
