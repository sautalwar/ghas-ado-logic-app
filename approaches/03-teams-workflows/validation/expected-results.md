# Expected Results — Approach #3: Teams Workflows

## Work Item Creation Results

### Secret Scanning Alert → Work Item

| Field | Expected Value |
|-------|---------------|
| **Type** | Issue |
| **Title** | `[GHAzDO-Secret] {secretType}` (e.g., `[GHAzDO-Secret] GitHub Personal Access Token`) |
| **State** | New |
| **Priority** | 1 (if severity = critical/high), 2 (if medium), 3 (if low) |
| **Tags** | `GHAzDO;secret;{severity};GHAzDO-{repoName}-{alertId}` |
| **Description** | HTML table with: Alert Type, Severity, Repository, File, Line, Alert ID, Tag, plus link to alert |

### Code Scanning Alert → Work Item

| Field | Expected Value |
|-------|---------------|
| **Type** | Issue |
| **Title** | `[GHAzDO-CodeScan] {alertTitle}` (e.g., `[GHAzDO-CodeScan] SQL Injection in login handler`) |
| **State** | New |
| **Priority** | Based on severity |
| **Tags** | `GHAzDO;code;{severity};GHAzDO-{repoName}-{alertId}` |
| **Description** | HTML table with alert details |

### Dependency Alert → Work Item

| Field | Expected Value |
|-------|---------------|
| **Type** | Issue |
| **Title** | `[GHAzDO-Dependency] {alertTitle}` (e.g., `[GHAzDO-Dependency] lodash prototype pollution`) |
| **State** | New |
| **Priority** | Based on severity |
| **Tags** | `GHAzDO;dependency;{severity};GHAzDO-{repoName}-{alertId}` |
| **Description** | HTML table with alert details |

---

## Priority Mapping

| GHAzDO Severity | ADO Priority | Reasoning |
|-----------------|-------------|-----------|
| critical | 1 - Critical | Immediate action required |
| high | 1 - Critical | Immediate action required |
| medium | 2 - High | Address in current sprint |
| low | 3 - Medium | Schedule for future sprint |
| note | 3 - Medium | Informational, review at convenience |

---

## Tag Format

**Format:** `GHAzDO;{alertType};{severity};GHAzDO-{repoName}-{alertId}`

**Examples:**
- `GHAzDO;secret;high;GHAzDO-my-repo-42`
- `GHAzDO;code;critical;GHAzDO-api-service-101`
- `GHAzDO;dependency;medium;GHAzDO-frontend-200`

**Purpose of each tag segment:**
- `GHAzDO` — Identifies all work items from this integration
- `{alertType}` — Enables filtering by alert category
- `{severity}` — Enables filtering by severity
- `GHAzDO-{repo}-{id}` — Unique identifier for manual dedup searches

---

## Auto-Close Results (Optional Workflow)

### State Change: Fixed

| Field | Before | After |
|-------|--------|-------|
| **State** | New / Active | Done |
| **History** | — | "Auto-closed: GHAzDO alert resolved/fixed." |

### State Change: Dismissed

| Field | Before | After |
|-------|--------|-------|
| **State** | New / Active | Done |
| **History** | — | "Auto-closed: GHAzDO alert resolved/fixed." |

---

## Workflow Run History Expected Outputs

### Successful Create Flow

| Step | Status | Output |
|------|--------|--------|
| Trigger (webhook received) | Succeeded | HTTP 200/202 |
| Parse_JSON | Succeeded | All fields extracted |
| Compose_AlertType | Succeeded | `"secret"` / `"code"` / `"dependency"` |
| Compose_AlertId | Succeeded | Numeric ID (e.g., `42`) |
| Compose_RepoName | Succeeded | Repository name string |
| Compose_Severity | Succeeded | Lowercase severity |
| Compose_GhasTag | Succeeded | `"GHAzDO-{repo}-{id}"` |
| Compose_Title | Succeeded | `"[GHAzDO-{Type}] {title}"` |
| Compose_Tags | Succeeded | Semicolon-separated tag string |
| Compose_Description | Succeeded | HTML string |
| Create Work Item | Succeeded | ADO work item ID in response |

### Expected HTTP Response from Webhook

```json
{
  "statusCode": 202,
  "body": "Accepted"
}
```

---

## Performance Expectations

| Metric | Expected |
|--------|----------|
| **Webhook response time** | < 5 seconds |
| **End-to-end (alert → work item)** | < 30 seconds |
| **Workflow run duration** | 5–15 seconds |
| **Concurrent alert handling** | Sequential (one at a time per workflow instance) |
| **Daily throughput capacity** | Hundreds of alerts (M365 standard throttle limits) |

---

## Error Scenarios

| Scenario | Expected Behavior |
|----------|------------------|
| Invalid JSON payload | Parse JSON step fails; workflow run shows "Failed" |
| Missing required fields (alertType) | Coalesce defaults to "unknown"; work item still created |
| ADO connector token expired | Create Work Item step fails; re-authenticate in workflow |
| ADO project permissions insufficient | Create Work Item returns 403; check OAuth account permissions |
| Webhook URL expired/changed | Service hook test fails; recreate workflow or update URL |
| Duplicate alert (same alertId) | Work item created (no dedup in Standard tier); use tag search to find duplicates |
