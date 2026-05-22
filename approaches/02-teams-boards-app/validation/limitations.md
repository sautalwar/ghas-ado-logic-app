# Known Limitations — Approach #2: Teams + Boards App

## Summary

This approach provides **notification + one-click creation** but does NOT provide full automation. It is best characterized as "semi-automated" — alerts arrive automatically, but work item creation requires a human click.

---

## What This Approach CANNOT Do

### 1. ❌ Fully Automated Work Item Creation

**Limitation:** Work items are NOT auto-created. A team member must manually click "Create Work Item" from the Teams notification.

**Impact:** If no one monitors the Teams channel, alerts may go unaddressed. High-volume alert environments may find the manual step burdensome.

**Workaround:** Assign a daily "security triage" rotation to review the channel and create work items.

**Upgrade path:** Use Logic App (Phase 3) for fully automated creation.

---

### 2. ❌ Auto-Close Work Items When Alerts Are Resolved

**Limitation:** When a GHAzDO alert state changes to "Fixed" or "Dismissed," a notification appears in Teams, but the associated work item is NOT automatically closed.

**Impact:** Work items may remain open after the underlying alert is resolved, creating stale items in the backlog.

**Workaround:** Manually close work items when you see "Fixed" notifications. Use a weekly review of open "GHAzDO" tagged items.

**Upgrade path:** Logic App (Phase 3) auto-closes work items via WIQL query matching.

---

### 3. ❌ Deduplication

**Limitation:** There is no check for existing work items. If multiple team members create work items from the same notification, or if the same alert fires multiple times, duplicate work items will be created.

**Impact:** Duplicate work items clutter the backlog and waste effort.

**Workaround:**
- Use the Teams channel as the coordination point — reply to a notification before creating a work item ("I'll create the WI for this one")
- Search ADO for existing items before creating: `@Azure Boards search "GHAzDO: [alert title]"`

**Upgrade path:** Logic App (Phase 3) uses WIQL queries to check for existing work items before creating.

---

### 4. ❌ Automatic Field Mapping

**Limitation:** Work items created via the Boards App do not automatically map:
- Severity → Priority (user must set manually)
- Alert URL → Work item hyperlink (user must paste)
- Alert type → Tags (user must add)
- Repository → Area path (user must select)

**Impact:** Inconsistent work item quality depending on who creates the item and how diligent they are about filling in fields.

**Workaround:** Create a "Security Bug" work item template in ADO with pre-filled tags and default priority. Train the team on the expected fields.

**Upgrade path:** Logic App (Phase 3) maps all fields automatically using JSON expressions.

---

### 5. ❌ Bi-Directional Linking

**Limitation:** The created work item has no automatic link back to the GHAzDO alert, and the GHAzDO alert has no link to the work item.

**Impact:** Traceability between alerts and work items requires manual effort.

**Workaround:** Paste the alert URL in the work item description when creating it. Paste the work item URL in a comment on the alert.

**Upgrade path:** Logic App (Phase 3) embeds the alert URL in the work item description automatically.

---

### 6. ⚠️ Webhook URL Management

**Limitation:** Teams incoming webhook URLs can expire or break if:
- The channel is deleted or renamed
- The webhook connector is removed
- Teams admin policies change

**Impact:** Notifications silently stop. No built-in health monitoring.

**Workaround:** Periodically check Service Hook history in ADO for failed deliveries. Set a calendar reminder to verify monthly.

---

### 7. ⚠️ Notification Fatigue

**Limitation:** In repositories with many security alerts, the Teams channel can become noisy. There's limited filtering — service hooks can filter by repository and alert type, but not by severity alone in all configurations.

**Impact:** Team members may mute the channel, defeating the purpose.

**Workaround:**
- Use separate channels for different severity levels
- Configure service hook filters to only fire for Critical/High severity
- Review and resolve alerts promptly to reduce volume

---

### 8. ⚠️ Microsoft Connectors Deprecation

**Limitation:** Microsoft is deprecating Office 365 Connectors in Teams in favor of Workflows (Power Automate-based). Incoming webhooks may be affected.

**Impact:** The webhook URL creation method may change. Existing webhooks continue to work but new ones may need to be created via Workflows.

**Workaround:** Use the Teams Workflows approach for new webhook creation. See `teams-channel-setup.md` for the Workflows alternative.

**Timeline:** Microsoft has announced deprecation starting late 2024; migration period through 2025. Check current status at the time of implementation.

---

## Limitations Comparison

| Limitation | Phase 1 (Native ADO) | Phase 1.5 (This) | Phase 3 (Logic App) |
|-----------|----------------------|-------------------|---------------------|
| No notifications | ❌ | ✅ Fixed | ✅ Fixed |
| Manual WI creation | Manual in ADO | One-click in Teams | ✅ Automated |
| No auto-close | ❌ | ❌ | ✅ Fixed |
| No dedup | ❌ | ❌ | ✅ Fixed |
| No field mapping | ❌ | ❌ | ✅ Fixed |
| No bi-directional link | ❌ | ❌ | ✅ Fixed |
| Infrastructure cost | None | None | $50–100/mo |
| Setup time | 0 min | 15 min | 5 min (deploy btn) |

---

## When to Stay on Phase 1.5 vs. Upgrade

### Stay on Phase 1.5 if:
- Alert volume is low (< 20/week)
- Team actively monitors the Teams channel
- One-click creation is acceptable
- Zero cost is a hard requirement
- The team is evaluating whether full automation is needed

### Upgrade to Phase 3 (Logic App) if:
- Alert volume is high (> 20/week)
- Need zero-touch automation (no human in the loop)
- Need auto-close when alerts are resolved
- Need deduplication to prevent duplicate work items
- Need full field mapping and audit trail
- Compliance requires automated, consistent work item creation
