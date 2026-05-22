# Expected Results — Zapier Integration

> What a successful Zapier implementation looks like

## End-to-End Flow: Alert Created

**Input:** GHAzDO detects a secret in `config/settings.py` line 15

**Expected ADO Work Item:**

| Field | Expected Value |
|-------|---------------|
| **Title** | `[GHAzDO-Secret] Amazon AWS Access Key ID` |
| **Description** | HTML table (see below) |
| **Tags** | `GHAzDO;secret;critical;GHAzDO-my-app-42` |
| **Priority** | 1 (Critical) |
| **State** | New |
| **Type** | Issue |

**Expected Description HTML:**
```html
<h3>GHAzDO Security Alert</h3>
<table border="1" cellpadding="5">
  <tr><td><b>Alert Type</b></td><td>secret</td></tr>
  <tr><td><b>Severity</b></td><td>critical</td></tr>
  <tr><td><b>Repository</b></td><td>my-app</td></tr>
  <tr><td><b>File</b></td><td>config/settings.py</td></tr>
  <tr><td><b>Line</b></td><td>15</td></tr>
  <tr><td><b>Alert ID</b></td><td>42</td></tr>
  <tr><td><b>Tag</b></td><td>GHAzDO-my-app-42</td></tr>
</table>
<p><a href="https://dev.azure.com/myorg/myproject/_git/my-app/alerts/42">View Alert in Azure DevOps</a></p>
<hr/><p><i>Auto-created by GHAzDO Zapier Integration</i></p>
```

---

## End-to-End Flow: Alert Resolved

**Input:** Alert 42 in my-app is fixed (state changes from `active` → `fixed`)

**Expected Result:**

| Field | Before | After |
|-------|--------|-------|
| **State** | New / Active | Done |
| **History** | (empty) | "Auto-closed: GHAzDO alert resolved/fixed." |

---

## End-to-End Flow: Duplicate Alert

**Input:** Same alert 42 fires again (re-scan detects same secret)

**Expected Result:**
- ❌ No new work item created
- ✅ Existing work item unchanged
- ✅ Zapier Task History shows Zap stopped at dedup filter

---

## Expected Zapier Task History

### Successful Create
```
✅ Trigger: Catch Hook — received webhook
✅ Filter: eventType contains "created" — PASSED
✅ Code: Parse & Map — completed
✅ Custom Request: WIQL Search — 200 OK (0 results)
✅ Filter: No existing work item — PASSED
✅ Custom Request: Create Work Item — 200 OK
```

### Successful Close
```
✅ Trigger: Catch Hook — received webhook
✅ Filter: state is "fixed" — PASSED
✅ Code: Build search query — completed
✅ Custom Request: WIQL Search — 200 OK (1 result)
✅ Filter: Work item found — PASSED
✅ Custom Request: Update Work Item — 200 OK
```

### Duplicate Blocked
```
✅ Trigger: Catch Hook — received webhook
✅ Filter: eventType contains "created" — PASSED
✅ Code: Parse & Map — completed
✅ Custom Request: WIQL Search — 200 OK (1 result)
🛑 Filter: No existing work item — STOPPED (duplicate found)
```

### Wrong Event Type
```
✅ Trigger: Catch Hook — received webhook
🛑 Filter: eventType contains "created" — STOPPED
```

---

## Performance Expectations

| Metric | Expected |
|--------|----------|
| **Webhook delivery** | < 5 seconds (ADO → Zapier) |
| **Zap execution** | 10-30 seconds per Zap |
| **End-to-end** | < 60 seconds from alert to work item |
| **Zapier uptime** | 99.9% (SaaS SLA) |
| **Task consumption** | ~9-10 tasks per full create+close cycle |

---

## Alert Type Expected Outputs

### Secret Scanning Alert
| Field | Value |
|-------|-------|
| Title | `[GHAzDO-Secret] Amazon AWS Access Key ID` |
| Tags | `GHAzDO;secret;critical;GHAzDO-my-app-42` |
| Priority | 1 |

### Code Scanning Alert
| Field | Value |
|-------|-------|
| Title | `[GHAzDO-CodeScan] SQL Injection vulnerability in query builder` |
| Tags | `GHAzDO;code;high;GHAzDO-my-app-87` |
| Priority | 1 |

### Dependency Alert
| Field | Value |
|-------|-------|
| Title | `[GHAzDO-Dependency] Prototype Pollution in lodash` |
| Tags | `GHAzDO;dependency;medium;GHAzDO-my-app-103` |
| Priority | 2 |
