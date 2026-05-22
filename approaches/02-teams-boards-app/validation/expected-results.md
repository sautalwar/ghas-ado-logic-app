# Expected Results — Approach #2: Teams + Boards App

## Test 1: Alert Created → Teams Notification

### Expected Outcome: ✅ PASS

**What you should see:**

A message appears in the **🔒 Security Alerts** Teams channel that looks similar to:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔒 Advanced Security Alert Created

Alert: Secret detected in code
Repository: my-project-repo
Severity: Critical
Type: Secret Scanning
State: Active

View alert: https://dev.azure.com/{org}/{project}/_git/{repo}/alerts/42
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Timing:** 1–5 minutes after the alert is created by GHAzDO.

**If using Web Hooks consumer:** The message format depends on the `detailedMessage` from the service hook payload. It will be rendered as a simple text message or card.

**If using native Teams consumer:** A pre-formatted card is displayed by ADO.

---

## Test 2: Notification Contains Alert Details

### Expected Outcome: ✅ PASS (with notes)

**Required fields present:**

| Field | Status | Notes |
|-------|--------|-------|
| Alert title | ✅ Present | From `message.text` or `detailedMessage.text` |
| Alert type | ✅ Present | Secret / Dependency / Code Scanning |
| Severity | ✅ Present | Critical / High / Medium / Low |
| Repository | ✅ Present | Repository name from `resource.repository.name` |
| Link to ADO | ✅ Present | Clickable URL to the alert |
| State | ✅ Present | Active / New |
| File path | ⚠️ May vary | Included in `detailedMessage` for some alert types; not guaranteed |

**Note on file path:** Secret scanning alerts typically include the file path. Dependency alerts reference the manifest file. Code scanning alerts may reference a file and line number, but this depends on the `detailedMessage` format from ADO.

---

## Test 3: Create Work Item from Notification

### Expected Outcome: ✅ PASS

**What you should see after clicking Create:**

1. A dialog/form appears with fields for the work item
2. The Title field may be pre-populated from the message text
3. After submission, a confirmation card appears:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Work Item Created

Bug #1234: GHAzDO: Secret detected in code
Project: MySecurityProject
State: New
Assigned To: (as selected)

View work item: https://dev.azure.com/{org}/{project}/_workitems/edit/1234
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Important:** The "Create Work Item" action is a standard Azure Boards App feature that works on ANY Teams message. It is not specific to GHAzDO notifications — which means it works immediately without custom configuration.

---

## Test 4: Work Item Has Correct Fields

### Expected Outcome: ✅ PASS (with manual enrichment)

**Work item in ADO after creation:**

| Field | Value | Auto-populated? |
|-------|-------|----------------|
| Title | "GHAzDO: Secret detected in code" | Partially (user edits) |
| Type | Bug | User selected |
| State | New | Default |
| Description | Alert message content from Teams | Yes (from message) |
| Tags | "GHAzDO", "security-alert" | User must add manually |
| Area Path | Team area path | User must select |
| Priority | 1 (Critical) | User must set |
| Link to alert | Not auto-linked | User must paste URL |
| Assigned To | Team member | User must select |

**Key observation:** The work item will NOT automatically contain:
- A hyperlink back to the specific GHAzDO alert
- Auto-mapped priority from severity
- Auto-populated tags

These must be added manually by the user during creation. This is the primary trade-off of this approach vs. the Logic App (Phase 3) which populates all fields automatically.

---

## Test 5: State Change Notification

### Expected Outcome: ✅ PASS

**What you should see when an alert is resolved:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Advanced Security Alert State Changed

Alert: Secret detected in code
Repository: my-project-repo
Previous State: Active
New State: Fixed
Type: Secret Scanning

View alert: https://dev.azure.com/{org}/{project}/_git/{repo}/alerts/42
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**What this does NOT do:**
- ❌ Does NOT automatically close the associated work item
- ❌ Does NOT update any existing work item fields
- ❌ Does NOT link the state change to the previously created work item

The team member must manually:
1. See the "Fixed" notification
2. Find the related work item (by searching for the alert title)
3. Close/resolve the work item manually

---

## Overall Assessment

| Capability | Result | Notes |
|-----------|--------|-------|
| Receive GHAzDO alert events | ✅ YES | Via ADO Service Hooks |
| Notify team in Teams | ✅ YES | Rich notification in channel |
| Contains alert details | ✅ YES | Title, type, severity, repo, link |
| Create ADO work item | ✅ YES | One-click from Teams (Azure Boards App) |
| Auto-populate all fields | ⚠️ PARTIAL | Title/description yes; tags/priority/links are manual |
| Handle all 3 alert types | ✅ YES | Secret, Dependency, Code Scanning |
| State change notifications | ✅ YES | Notifies when fixed/dismissed/reopened |
| Auto-close work items | ❌ NO | Manual close required |
| Deduplication | ❌ NO | No check for existing work items |
| Audit trail | ⚠️ PARTIAL | Teams message history only |

**Bottom line:** This approach delivers **80% of the value at 0% of the cost** compared to the Logic App approach. The trade-off is manual work item creation (one click + field selection) and manual closure.
