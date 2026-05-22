# Teams Workflow — Detailed Step Configuration

> This document provides exact field values for each workflow step. Use alongside the README for setup.

---

## Workflow 1: GHAzDO Alert → Create ADO Work Item

### Step 1: Trigger — "When a Teams webhook request is received"

| Setting | Value |
|---------|-------|
| **Type** | Automated (instant) |
| **Trigger** | When a Teams webhook request is received |
| **Method** | POST |
| **URL** | Auto-generated after save |

**What this does:** Creates an HTTPS endpoint that ADO Service Hooks will POST to.

---

### Step 2: Parse JSON

| Setting | Value |
|---------|-------|
| **Action** | Data Operation → Parse JSON |
| **Content** | `triggerBody()` (select from expression tab) |
| **Schema** | Paste contents of `webhook-payload-schema.json` |

**Alternative:** Click "Use sample payload to generate schema" and paste this sample:

```json
{
  "eventType": "advancedsecurity.alert.created",
  "resource": {
    "alertType": "secret",
    "alertId": 42,
    "severity": "high",
    "state": "active",
    "secretType": "GitHub PAT",
    "title": "Secret detected",
    "location": { "file": "config.yml", "line": 10 },
    "repository": { "name": "my-repo" },
    "link": "https://dev.azure.com/org/project/_git/repo/alerts/42"
  },
  "message": { "text": "A secret scanning alert was created" }
}
```

---

### Step 3: Compose — Alert Type

| Setting | Value |
|---------|-------|
| **Action** | Data Operation → Compose |
| **Name** | Compose_AlertType |
| **Inputs** | Expression: `coalesce(body('Parse_JSON')?['resource']?['alertType'], 'unknown')` |

**How to enter:** Click the Inputs field → switch to "Expression" tab → type the expression → click OK.

---

### Step 4: Compose — Alert ID

| Setting | Value |
|---------|-------|
| **Action** | Data Operation → Compose |
| **Name** | Compose_AlertId |
| **Inputs** | Expression: `coalesce(body('Parse_JSON')?['resource']?['alertId'], body('Parse_JSON')?['resource']?['id'], 0)` |

---

### Step 5: Compose — Repository Name

| Setting | Value |
|---------|-------|
| **Action** | Data Operation → Compose |
| **Name** | Compose_RepoName |
| **Inputs** | Expression: `coalesce(body('Parse_JSON')?['resource']?['repository']?['name'], 'unknown-repo')` |

---

### Step 6: Compose — Severity

| Setting | Value |
|---------|-------|
| **Action** | Data Operation → Compose |
| **Name** | Compose_Severity |
| **Inputs** | Expression: `toLower(coalesce(body('Parse_JSON')?['resource']?['severity'], 'medium'))` |

---

### Step 7: Compose — Tracking Tag

| Setting | Value |
|---------|-------|
| **Action** | Data Operation → Compose |
| **Name** | Compose_GhasTag |
| **Inputs** | Expression: `concat('GHAzDO-', outputs('Compose_RepoName'), '-', string(outputs('Compose_AlertId')))` |

**Purpose:** Creates a unique tag like `GHAzDO-my-repo-42` for tracking and manual dedup.

---

### Step 8: Compose — Work Item Title

| Setting | Value |
|---------|-------|
| **Action** | Data Operation → Compose |
| **Name** | Compose_Title |
| **Inputs** | Expression (long — enter carefully): |

```
if(equals(outputs('Compose_AlertType'), 'secret'), concat('[GHAzDO-Secret] ', coalesce(body('Parse_JSON')?['resource']?['secretType'], 'Secret detected')), if(equals(outputs('Compose_AlertType'), 'code'), concat('[GHAzDO-CodeScan] ', coalesce(body('Parse_JSON')?['resource']?['title'], 'Code scanning alert')), if(equals(outputs('Compose_AlertType'), 'dependency'), concat('[GHAzDO-Dependency] ', coalesce(body('Parse_JSON')?['resource']?['title'], 'Dependency alert')), concat('[GHAzDO-Alert] ', coalesce(body('Parse_JSON')?['resource']?['title'], 'Security alert')))))
```

**Title examples by alert type:**
- Secret: `[GHAzDO-Secret] GitHub Personal Access Token`
- Code scan: `[GHAzDO-CodeScan] SQL Injection vulnerability in login handler`
- Dependency: `[GHAzDO-Dependency] lodash prototype pollution`

---

### Step 9: Compose — Tags

| Setting | Value |
|---------|-------|
| **Action** | Data Operation → Compose |
| **Name** | Compose_Tags |
| **Inputs** | Expression: `concat('GHAzDO;', outputs('Compose_AlertType'), ';', outputs('Compose_Severity'), ';', outputs('Compose_GhasTag'))` |

**Example output:** `GHAzDO;secret;high;GHAzDO-my-repo-42`

---

### Step 10: Compose — HTML Description

| Setting | Value |
|---------|-------|
| **Action** | Data Operation → Compose |
| **Name** | Compose_Description |
| **Inputs** | Expression: |

```
concat('<h3>GHAzDO Security Alert</h3>', '<table border="1" cellpadding="5">', '<tr><td><b>Alert Type</b></td><td>', outputs('Compose_AlertType'), '</td></tr>', '<tr><td><b>Severity</b></td><td>', outputs('Compose_Severity'), '</td></tr>', '<tr><td><b>Repository</b></td><td>', outputs('Compose_RepoName'), '</td></tr>', '<tr><td><b>File</b></td><td>', coalesce(body('Parse_JSON')?['resource']?['location']?['file'], 'N/A'), '</td></tr>', '<tr><td><b>Alert ID</b></td><td>', string(outputs('Compose_AlertId')), '</td></tr>', '<tr><td><b>Tag</b></td><td>', outputs('Compose_GhasTag'), '</td></tr>', '</table>', '<p><a href="', coalesce(body('Parse_JSON')?['resource']?['link'], ''), '">View Alert in Azure DevOps</a></p>', '<hr/><p><i>Auto-created by Teams Workflow</i></p>')
```

---

### Step 11: Create Work Item (ADO Connector)

| Setting | Value |
|---------|-------|
| **Action** | Azure DevOps → Create a work item |
| **Connection** | Sign in with OAuth when prompted |
| **Organization Name** | Your ADO organization (e.g., `contoso`) |
| **Project Name** | Your ADO project |
| **Work Item Type** | `Issue` (or `Bug` / `Task` per your preference) |
| **Title** | Dynamic content → `Compose_Title` output |
| **Description** | Dynamic content → `Compose_Description` output |
| **Tags** | Dynamic content → `Compose_Tags` output |
| **Priority** | Expression: `if(or(equals(outputs('Compose_Severity'),'critical'),equals(outputs('Compose_Severity'),'high')), 1, if(equals(outputs('Compose_Severity'),'medium'), 2, 3))` |

**OAuth Sign-in:**
When you add the Azure DevOps connector, Teams will prompt you to sign in. Use an account that has work item creation permissions in the target project. This OAuth connection is stored securely by Teams and doesn't expire like PATs.

---

## Workflow 2: Auto-Close (Optional)

> ⚠️ This workflow has limitations — see README Step 6 and `validation/limitations.md`

### Step 1: Trigger — Webhook (same as Workflow 1)

Create a new workflow with "When a Teams webhook request is received" trigger.

### Step 2: Parse JSON (same schema as Workflow 1)

### Step 3: Check Event Type

| Setting | Value |
|---------|-------|
| **Action** | Control → Condition |
| **Condition** | `body('Parse_JSON')?['eventType']` is equal to `advancedsecurity.alert.statechanged` |

### Step 4: Check New State

| Setting | Value |
|---------|-------|
| **Action** | Control → Condition (nested in Yes branch) |
| **Condition** | `body('Parse_JSON')?['resource']?['newState']` is equal to `fixed` OR is equal to `dismissed` |

### Step 5: Get Query Results (Find Work Item by Tag)

| Setting | Value |
|---------|-------|
| **Action** | Azure DevOps → Get query results |
| **Organization** | Your ADO org |
| **Project** | Your ADO project |
| **Query Name** | A pre-saved query (see below) |

**Pre-requisite — Create a Saved Query in ADO:**
1. Go to ADO → Boards → Queries → New Query
2. Set filter: `Tags Contains GHAzDO` AND `State <> Done` AND `State <> Removed`
3. Save as "GHAzDO Active Alerts"
4. Reference this query name in the workflow step

> ⚠️ **Limitation:** The "Get query results" action runs a saved query — it cannot dynamically filter by the specific `GHAzDO-{repo}-{alertId}` tag. You'll get ALL active GHAzDO work items and need to filter in the workflow, which adds complexity.

### Step 6: Apply to Each + Condition (Filter by Tag)

| Setting | Value |
|---------|-------|
| **Action** | Control → Apply to each |
| **Input** | Output of "Get query results" |
| **Nested Condition** | Work item Tags contains `outputs('Compose_GhasTag')` |

### Step 7: Update Work Item

| Setting | Value |
|---------|-------|
| **Action** | Azure DevOps → Update a work item |
| **Organization** | Your ADO org |
| **Project** | Your ADO project |
| **Work Item Id** | Dynamic content from the matching work item |
| **State** | `Done` (or `Closed` depending on your process) |
| **History** | `Auto-closed: GHAzDO alert resolved/fixed.` |

---

## Expression Quick Reference

| Expression | Purpose | Example Output |
|-----------|---------|---------------|
| `coalesce(a, b, 'default')` | First non-null value | `"secret"` |
| `concat(a, b, c)` | String concatenation | `"GHAzDO-repo-42"` |
| `if(condition, true, false)` | Conditional value | `1` |
| `equals(a, b)` | Equality check | `true` |
| `or(a, b)` | Logical OR | `true` |
| `toLower(s)` | Lowercase string | `"high"` |
| `string(n)` | Convert to string | `"42"` |
| `body('Step')?['key']` | Access parsed JSON | `"secret"` |
| `outputs('Step')` | Get step output | `"GHAzDO-repo-42"` |
