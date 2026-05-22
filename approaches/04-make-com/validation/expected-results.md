# Expected Results — Make.com GHAzDO → ADO Integration

## Summary

When fully configured, the Make.com scenario will:

1. **Instantly receive** GHAzDO security alert events via webhook (no polling delay)
2. **Automatically create** ADO work items with rich metadata for new alerts
3. **Automatically close** ADO work items when alerts are resolved
4. **Prevent duplicates** via WIQL tag-based dedup check
5. **Handle all 3 alert types** with correct title prefixes and field mapping

---

## Expected Work Item: Secret Scanning Alert

**Trigger:** `advancedsecurity.alert.created` with `alertType: "secret"`

| Field | Expected Value |
|-------|---------------|
| **Type** | Issue |
| **Title** | `[GHAzDO-Secret] Azure Storage Account Key` |
| **State** | New |
| **Priority** | 1 (critical severity) |
| **Tags** | `GHAzDO;secret;critical;GHAzDO-my-repo-42` |
| **Description** | HTML table with: Alert Type, Severity, Repository, File, Alert ID, link to ADO alert |

---

## Expected Work Item: Code Scanning Alert

**Trigger:** `advancedsecurity.alert.created` with `alertType: "code"`

| Field | Expected Value |
|-------|---------------|
| **Type** | Issue |
| **Title** | `[GHAzDO-CodeScan] SQL Injection vulnerability` |
| **State** | New |
| **Priority** | 1 (high severity) |
| **Tags** | `GHAzDO;code;high;GHAzDO-my-repo-101` |
| **Description** | HTML table with alert details |

---

## Expected Work Item: Dependency Alert

**Trigger:** `advancedsecurity.alert.created` with `alertType: "dependency"`

| Field | Expected Value |
|-------|---------------|
| **Type** | Issue |
| **Title** | `[GHAzDO-Dependency] lodash prototype pollution` |
| **State** | New |
| **Priority** | 2 (medium severity) |
| **Tags** | `GHAzDO;dependency;medium;GHAzDO-my-repo-77` |
| **Description** | HTML table with alert details |

---

## Expected Auto-Close Behavior

**Trigger:** `advancedsecurity.alert.stateChanged` with `state: "fixed"`

| Before | After |
|--------|-------|
| Work item state: `New` or `Active` | Work item state: `Done` |
| No comment | History entry: `Auto-closed: GHAzDO alert resolved/fixed.` |

---

## Expected Dedup Behavior

| Scenario | Result |
|----------|--------|
| First alert (new ID) | Work item created ✅ |
| Same alert (duplicate ID) | No new work item (blocked by filter) ✅ |
| Same alert after close + reopen | New work item created (previous one is Done/Removed) ✅ |

---

## Expected Operation Counts

| Scenario | Operations Used |
|----------|----------------|
| New alert → work item created | 4 |
| Duplicate alert → blocked | 3 |
| Alert resolved → work item closed | 3-4 |
| Full lifecycle (create + close) | 7-8 |
| Monthly capacity (free tier) | ~125-142 full cycles |

---

## Expected Execution Time

| Step | Time |
|------|------|
| Webhook receive | < 1 second |
| JSON parse | < 1 second |
| WIQL HTTP call | 1-3 seconds |
| ADO create/update | 1-3 seconds |
| **Total end-to-end** | **< 10 seconds** |
