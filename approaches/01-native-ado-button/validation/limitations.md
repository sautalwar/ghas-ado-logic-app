# Limitations & Capabilities Assessment — Approach #1

## Capabilities Assessment

| Capability | Status | Details |
|-----------|--------|---------|
| Receive a GHAzDO security alert event? | 🟡 **Manual** | User must navigate to ADO Advanced Security and click the button. No automatic notification or trigger. |
| Create an ADO work item with correct details? | ✅ **Yes, with template** | Work Item Template pre-fills tags, area, priority, severity, and structured description. User fills in alert-specific details. |
| Handle all 3 alert types? | ✅ **Yes (manually)** | Works identically for secret scanning, code scanning, and dependency alerts. Same "Create work item" button on all alert types. |
| Auto-close work items when alerts resolve? | ❌ **No** | User must manually check if the GHAzDO alert is resolved and manually close the work item. No automated link between alert state and work item state. |
| Deduplicate alerts? | ❌ **No** | No mechanism to detect if a work item already exists for an alert. User must manually check before creating. Multiple work items could be created for the same alert. |
| **Setup time** | ⏱️ **~10 minutes** | Template: 5 min, Area path: 2 min, Board rules: 2 min, Dashboard: 1 min |
| **Cost** | 💰 **Free** | Included with GHAzDO license. No additional Azure resources, licenses, or subscriptions needed. |
| **Infrastructure required** | 🏗️ **None** | Zero Azure resources. Zero code. Zero deployments. Everything is native ADO configuration. |
| **Maintenance** | 🔧 **None** | No infrastructure to maintain, update, or monitor. Template may need updates if process changes. |

---

## What This Approach CANNOT Do

### 1. ❌ Automatic Work Item Creation
**Gap:** When GHAzDO detects a new vulnerability, nothing happens automatically. No work item is created. No one is notified (unless they're actively checking the Advanced Security page).

**Impact:** Security alerts can go unnoticed for days or weeks if no one is regularly checking the GHAzDO dashboard.

**Workaround:** Establish a daily/weekly security triage routine where a team member reviews the GHAzDO dashboard and creates work items for new alerts.

---

### 2. ❌ Automatic Work Item Closure
**Gap:** When a developer fixes a vulnerability and the GHAzDO alert resolves, the corresponding work item remains open. There is no automated state synchronization between GHAzDO alerts and ADO work items.

**Impact:** Work items become stale. Dashboard metrics become inaccurate. Team may waste time triaging already-resolved alerts.

**Workaround:** Include "Verify GHAzDO alert status" as part of the work item closure checklist. Use the "Aging Security Items" dashboard query to identify potentially stale items.

---

### 3. ❌ Deduplication
**Gap:** If two team members both see the same alert and each clicks "Create work item," two separate work items are created for the same vulnerability. There is no check for existing work items.

**Impact:** Duplicate work items cause confusion, double-counting in metrics, and wasted triage effort.

**Workaround:** Before creating a work item, check the existing GHAzDO query results for a matching item. ADO's alert detail page shows linked work items — if one already exists, it will be visible.

---

### 4. ❌ Real-Time Notifications
**Gap:** No push notification when new alerts are detected. Team must proactively visit the Advanced Security page.

**Impact:** Delayed response to critical security findings (e.g., exposed secrets).

**Workaround:** Consider Phase 1.5 (Teams Notifications + Boards App) for real-time alerts at zero cost. See `approaches/02-teams-boards-app/` for details.

---

### 5. ❌ Bulk Operations
**Gap:** Each work item must be created individually. Cannot select multiple alerts and create work items in batch.

**Impact:** If a repository has many alerts (e.g., after enabling GHAzDO for the first time), creating individual work items is time-consuming.

**Workaround:** For initial bulk creation, consider using the ADO REST API with a script. For ongoing operations, individual creation is usually manageable.

---

### 6. ❌ Custom Field Auto-Population
**Gap:** The "Create work item" button creates a basic work item. While the template fills standard fields, it cannot auto-populate alert-specific data (e.g., CVE ID, affected package, file path) from the GHAzDO alert into work item fields.

**Impact:** User must manually copy alert details into the work item description.

**Workaround:** The structured Description template in the Work Item Template provides placeholders for these fields, making manual entry consistent and fast.

---

### 7. ❌ Cross-Repository Aggregation
**Gap:** Each alert is per-repository. No built-in view to see all security alerts across all repositories in one place.

**Impact:** Organizations with many repositories must check each one individually.

**Workaround:** The WIQL dashboard query aggregates all GHAzDO-tagged work items regardless of source repository, providing a cross-repo view at the work item level.

---

## When to Upgrade to a Higher Phase

| Signal | Recommended Phase |
|--------|-------------------|
| Team misses critical alerts because no one checked ADO | Phase 1.5: Teams Notifications |
| Too many alerts to create work items manually | Phase 3: Logic App (auto-create) |
| Work items go stale because no one closes them | Phase 3: Logic App (auto-close) |
| Duplicate work items causing confusion | Phase 3: Logic App (dedup) |
| Compliance requires SLA tracking on alert response | Phase 3: Logic App + dashboard |
| Need audit trail of alert-to-work-item lifecycle | Phase 3: Logic App with logging |

---

## Comparison with Other Approaches

| Feature | Phase 1 (This) | Phase 1.5 (Teams) | Phase 3 (Logic App) |
|---------|----------------|--------------------|--------------------|
| Setup time | 10 min | 15 min | 5 min (deploy button) |
| Cost | Free | Free | $50-100/mo |
| Auto-create work items | ❌ | ❌ (1-click from Teams) | ✅ |
| Auto-close work items | ❌ | ❌ | ✅ |
| Deduplication | ❌ | ❌ | ✅ |
| Real-time notifications | ❌ | ✅ (Teams channel) | ✅ (via logs) |
| Infrastructure | None | None | Azure Logic App |
| Maintenance | None | None | None (managed) |
| Best for | Zero-complexity start | Visibility + 1-click | Enterprise automation |
