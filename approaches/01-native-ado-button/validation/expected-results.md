# Expected Results — Approach #1: Native ADO "Add" Button + Work Item Templates

## What Success Looks Like

When this approach is fully implemented, the following should be true:

---

## After Setup (one-time, ~10 minutes)

### ✅ Work Item Template Exists
- A template named **"GHAzDO Security Alert"** is available in the Boards → Templates menu
- The template pre-fills: Tags, Area Path, Priority, Severity, Description
- All team members can access and apply the template

### ✅ Area Path Configured
- A **Security** area path exists under the project root
- The Security team's backlog is filtered to this area path
- New work items created with the template automatically appear in the Security backlog

### ✅ Board Rules Active
- Moving a card to **Active** auto-assigns the mover
- Moving a card to **Closed** auto-sets state to Closed
- Moving a card back from Closed auto-reopens it

### ✅ Dashboard Query Available
- A shared query "GHAzDO Open Security Alerts" exists
- The query returns all open Bugs tagged `GHAzDO`
- A dashboard widget displays the query results

---

## Day-to-Day Operations

### ✅ Creating a Work Item from Any Alert Type

**What the user sees:**
1. Open any GHAzDO alert (secret, code, or dependency)
2. Click the "Create work item" button
3. A new Bug form opens — pre-linked to the alert
4. Apply the template → fields pre-fill instantly
5. Fill in 3-4 alert-specific fields (title, details)
6. Save — work item appears on Security board

**Time per work item:** ~1-2 minutes

### ✅ Work Item Contains

| Field | Expected Value |
|-------|---------------|
| Type | Bug |
| Title | `[GHAzDO] {Alert Type}: {Description}` |
| Tags | `GHAzDO; security; triage` |
| Area Path | `{Project}\Security` |
| Priority | 2 (adjustable) |
| Severity | 2 - High (adjustable) |
| Description | Structured template with details table, remediation steps, acceptance criteria |
| Related Work | Link to GHAzDO alert |
| State | New |

### ✅ GHAzDO Alert Shows Link

After creating a work item:
- The GHAzDO alert detail page displays the linked work item
- Clicking the link opens the work item directly
- This provides bidirectional traceability: alert ↔ work item

### ✅ Board Visibility

- GHAzDO work items appear in the Security team's board
- Items are filterable by `GHAzDO` tag
- Swimlane (if configured) separates security items visually
- WIP limits help manage security triage workload

### ✅ Dashboard Metrics

The dashboard should show:
- Count of open GHAzDO security items
- Priority breakdown (Critical/High/Medium/Low)
- Aging items (open > 7 days)
- Recently closed items (resolution velocity)

---

## What Manual Steps Remain

Even after full setup, these steps are always manual:

| Step | Manual Action Required |
|------|----------------------|
| **Discover alert** | User must check ADO → Repos → Advanced Security |
| **Create work item** | User clicks "Create work item" button |
| **Apply template** | User selects template from ⋯ menu |
| **Fill in details** | User types alert-specific title and details |
| **Close work item** | User manually closes when alert resolves |
| **Verify resolution** | User checks GHAzDO alert is actually resolved |

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|---------------|
| Template adoption | 100% of GHAzDO work items use template | Query: Tags contains `GHAzDO` AND Description contains "GHAzDO Security Alert" |
| Mean time to triage | < 24 hours | CreatedDate to first state change |
| Mean time to resolve | < 7 days (High), < 30 days (Medium) | CreatedDate to ClosedDate |
| Alert coverage | >90% of critical/high alerts have work items | Compare GHAzDO alert count vs work item count |
| Stale items | < 10% open items aged > 14 days | Aging query result count |
