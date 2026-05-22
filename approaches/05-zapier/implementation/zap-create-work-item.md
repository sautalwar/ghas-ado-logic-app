# Zap #1 — Alert Created → Create ADO Work Item

> Detailed step-by-step configuration for the "Create Work Item" Zap

## Zap Summary

| Property | Value |
|----------|-------|
| **Name** | GHAzDO Alert → Create ADO Work Item |
| **Trigger** | Webhooks by Zapier → Catch Hook |
| **Steps** | 5 (Trigger + Filter + Code + Search + Create) |
| **Tasks per run** | 4-5 (Filter stops don't count) |
| **Tier required** | Starter ($19.99/mo) minimum |

---

## Step 1: Trigger — Catch Hook

1. Open [zapier.com](https://zapier.com) and click **+ Create**
2. Click **Zaps** from the dropdown
3. For the **Trigger** step:
   - App: **Webhooks by Zapier**
   - Event: **Catch Hook**
   - Click **Continue**
4. **Pick off a Child Key** (optional): Leave blank to receive the full payload
5. Click **Continue** → Zapier generates your webhook URL:
   ```
   https://hooks.zapier.com/hooks/catch/123456/abcdef/
   ```
6. **Copy this URL** — you'll paste it into ADO Service Hooks later
7. Click **Test trigger**
   - You'll need to send a test payload. Either:
     - Configure the ADO Service Hook first (Step 4 in README) and use its Test button, OR
     - Use curl/Postman to POST a sample payload to the webhook URL
   - Once Zapier receives data, click **Continue with selected record**

### Sample Test Payload

Send this to your Catch Hook URL to test:

```json
{
  "subscriptionId": "test-sub-001",
  "notificationId": 1,
  "eventType": "advancedsecurity.alert.created",
  "resource": {
    "alertId": 42,
    "alertType": "secret",
    "title": "AWS Access Key detected",
    "secretType": "Amazon AWS Access Key ID",
    "severity": "critical",
    "state": "active",
    "repository": {
      "name": "my-app",
      "id": "repo-guid-001"
    },
    "location": {
      "file": "config/settings.py",
      "line": 15
    },
    "link": "https://dev.azure.com/myorg/myproject/_git/my-app/alerts/42",
    "url": "https://dev.azure.com/myorg/myproject/_git/my-app/alerts/42"
  },
  "message": {
    "text": "A secret was detected in my-app"
  }
}
```

---

## Step 2: Filter — Only Process "Created" Events

1. Click **+** to add a step
2. App: **Filter by Zapier** (built-in)
3. Configure:
   - **Only continue if...**
   - Field: Select `eventType` from the trigger data
   - Condition: **(Text) Contains**
   - Value: `created`
4. Click **Continue**

> 💡 Filters that stop a Zap don't consume a task — this saves cost when state-change events hit this Zap by mistake.

---

## Step 3: Code by Zapier — Parse & Map Fields

1. Click **+** to add a step
2. App: **Code by Zapier**
3. Event: **Run JavaScript**
4. **Input Data** — map these fields from the trigger:

| Key | Value (from trigger) |
|-----|---------------------|
| `eventType` | `{{eventType}}` |
| `alertId` | `{{resource__alertId}}` |
| `alertType` | `{{resource__alertType}}` |
| `title` | `{{resource__title}}` |
| `secretType` | `{{resource__secretType}}` |
| `severity` | `{{resource__severity}}` |
| `repoName` | `{{resource__repository__name}}` |
| `filePath` | `{{resource__location__file}}` |
| `lineNumber` | `{{resource__location__line}}` |
| `alertUrl` | `{{resource__link}}` |
| `advisoryTitle` | `{{resource__advisoryTitle}}` |
| `ruleDescription` | `{{resource__rule__description}}` |

5. **Code:**

```javascript
// Parse GHAzDO alert payload and map to ADO work item fields
const alertType = (inputData.alertType || 'unknown').toLowerCase();
const severity = (inputData.severity || 'medium').toLowerCase();
const repoName = inputData.repoName || 'unknown-repo';
const alertId = inputData.alertId || '0';
const filePath = inputData.filePath || 'N/A';
const lineNumber = inputData.lineNumber || 'N/A';
const alertUrl = inputData.alertUrl || '';

// Build unique tag for deduplication
const ghasTag = `GHAzDO-${repoName}-${alertId}`;

// Build title with alert type prefix
let workItemTitle;
if (alertType === 'secret') {
  workItemTitle = `[GHAzDO-Secret] ${inputData.secretType || 'Secret detected'}`;
} else if (alertType === 'code') {
  workItemTitle = `[GHAzDO-CodeScan] ${inputData.title || inputData.ruleDescription || 'Code scanning alert'}`;
} else if (alertType === 'dependency') {
  workItemTitle = `[GHAzDO-Dependency] ${inputData.title || inputData.advisoryTitle || 'Dependency alert'}`;
} else {
  workItemTitle = `[GHAzDO-Alert] ${inputData.title || 'Security alert'}`;
}

// Build tags string
const tags = `GHAzDO;${alertType};${severity};${ghasTag}`;

// Map severity to priority (1=Critical/High, 2=Medium, 3=Low)
let priority;
if (severity === 'critical' || severity === 'high') {
  priority = 1;
} else if (severity === 'medium') {
  priority = 2;
} else {
  priority = 3;
}

// Build HTML description
const description = `<h3>GHAzDO Security Alert</h3>
<table border="1" cellpadding="5">
<tr><td><b>Alert Type</b></td><td>${alertType}</td></tr>
<tr><td><b>Severity</b></td><td>${severity}</td></tr>
<tr><td><b>Repository</b></td><td>${repoName}</td></tr>
<tr><td><b>File</b></td><td>${filePath}</td></tr>
<tr><td><b>Line</b></td><td>${lineNumber}</td></tr>
<tr><td><b>Alert ID</b></td><td>${alertId}</td></tr>
<tr><td><b>Tag</b></td><td>${ghasTag}</td></tr>
</table>
<p><a href="${alertUrl}">View Alert in Azure DevOps</a></p>
<hr/><p><i>Auto-created by GHAzDO Zapier Integration</i></p>`;

// Build JSON patch body for ADO REST API
const patchBody = JSON.stringify([
  { op: "add", path: "/fields/System.Title", value: workItemTitle },
  { op: "add", path: "/fields/System.Description", value: description },
  { op: "add", path: "/fields/System.Tags", value: tags },
  { op: "add", path: "/fields/Microsoft.VSTS.Common.Priority", value: priority }
]);

// Build WIQL query for dedup search
const wiqlQuery = JSON.stringify({
  query: `SELECT [System.Id] FROM WorkItems WHERE [System.Tags] CONTAINS '${ghasTag}' AND [System.State] <> 'Removed'`
});

output = {
  workItemTitle,
  description,
  tags,
  ghasTag,
  priority: String(priority),
  patchBody,
  wiqlQuery,
  alertType,
  severity,
  repoName,
  alertId
};
```

6. Click **Test step** → verify the output contains all mapped fields

---

## Step 4: Webhooks by Zapier — Search for Existing Work Item (Dedup)

1. Click **+** to add a step
2. App: **Webhooks by Zapier**
3. Event: **Custom Request**
4. Configure:

| Field | Value |
|-------|-------|
| **Method** | POST |
| **URL** | `https://dev.azure.com/{YOUR_ORG}/{YOUR_PROJECT}/_apis/wit/wiql?api-version=7.1` |
| **Headers** | `Content-Type: application/json` |
| | `Authorization: Basic {BASE64_OF_COLON_PAT}` |
| **Body** | Use the `wiqlQuery` output from Step 3 |

> ⚠️ **Authorization header:** The value must be `Basic ` followed by the Base64 encoding of `:{YOUR_PAT}`. Generate this in advance:
> ```
> echo -n ":your-pat-here" | base64
> ```
> Example result: `Basic OnlvdXItcGF0LWhlcmU=`

5. Click **Test step** → verify response contains `workItems` array

---

## Step 5: Filter — Only Continue if No Existing Work Item

1. Click **+** to add a step
2. App: **Filter by Zapier**
3. Configure:
   - **Only continue if...**
   - Field: From Step 4 response, navigate to the response body
   - Use **Code by Zapier** (optional sub-step) to check: `JSON.parse(response).workItems.length === 0`
   
   **Alternative (simpler):** Use a **Formatter by Zapier** step to extract the workItems count, then filter on count = 0.

   **Simplest approach:** Check if the response body text contains `"workItems":[]` (empty array):
   - Field: Step 4 response body
   - Condition: **(Text) Contains**
   - Value: `"workItems":[]`

---

## Step 6: Webhooks by Zapier — Create Work Item

1. Click **+** to add a step
2. App: **Webhooks by Zapier**
3. Event: **Custom Request**
4. Configure:

| Field | Value |
|-------|-------|
| **Method** | PATCH |
| **URL** | `https://dev.azure.com/{YOUR_ORG}/{YOUR_PROJECT}/_apis/wit/workitems/$Issue?api-version=7.1` |
| **Headers** | `Content-Type: application/json-patch+json` |
| | `Authorization: Basic {BASE64_OF_COLON_PAT}` |
| **Body** | Use the `patchBody` output from Step 3 |

5. Click **Test step** → verify ADO work item is created

---

## Final Zap Configuration

1. **Name the Zap:** `GHAzDO Alert Created → Create ADO Work Item`
2. **Review all steps** — ensure data flows correctly
3. **Turn on** the Zap
4. Verify in Zapier Task History that test executions succeeded

---

## Zap Flow Diagram

```
┌─────────────────────────┐
│ 1. Catch Hook (Trigger) │
│    Webhook URL from ADO  │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ 2. Filter               │
│    eventType contains   │
│    "created"            │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ 3. Code by Zapier       │
│    Parse payload →      │
│    Map to ADO fields    │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ 4. Custom Request       │
│    WIQL search for      │
│    existing work item   │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ 5. Filter               │
│    Only if no duplicate │
│    found                │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ 6. Custom Request       │
│    PATCH → Create       │
│    ADO Work Item        │
└─────────────────────────┘
```
