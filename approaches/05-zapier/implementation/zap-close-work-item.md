# Zap #2 — Alert State Changed → Close ADO Work Item

> Detailed step-by-step configuration for the "Close Work Item" Zap

## Zap Summary

| Property | Value |
|----------|-------|
| **Name** | GHAzDO Alert Resolved → Close ADO Work Item |
| **Trigger** | Webhooks by Zapier → Catch Hook |
| **Steps** | 5 (Trigger + Filter + Code + Search + Update) |
| **Tasks per run** | 3-4 (Filter stops don't count) |
| **Tier required** | Starter ($19.99/mo) minimum |

---

## Step 1: Trigger — Catch Hook

1. In Zapier, click **+ Create → Zaps**
2. For the **Trigger** step:
   - App: **Webhooks by Zapier**
   - Event: **Catch Hook**
   - Click **Continue**
3. Zapier generates a **new** webhook URL:
   ```
   https://hooks.zapier.com/hooks/catch/123456/ghijkl/
   ```
4. **Copy this URL** — it goes into the ADO Service Hook for `stateChanged` events
5. Click **Test trigger** — send a test state-change payload (see below)

### Sample Test Payload

```json
{
  "subscriptionId": "test-sub-002",
  "notificationId": 2,
  "eventType": "advancedsecurity.alert.stateChanged",
  "resource": {
    "alertId": 42,
    "alertType": "secret",
    "title": "AWS Access Key detected",
    "severity": "critical",
    "state": "fixed",
    "previousState": "active",
    "repository": {
      "name": "my-app",
      "id": "repo-guid-001"
    },
    "link": "https://dev.azure.com/myorg/myproject/_git/my-app/alerts/42"
  },
  "message": {
    "text": "Alert state changed from active to fixed"
  }
}
```

---

## Step 2: Filter — Only Process Resolved/Fixed States

1. Click **+** to add a step
2. App: **Filter by Zapier**
3. Configure:
   - **Only continue if...**
   - Field: `resource__state` (from trigger data)
   - Condition: **(Text) Is in**
   - Value: `fixed,dismissed`
   
   **Alternative:** Two OR conditions:
   - `resource__state` **(Text) Exactly matches** `fixed`
   - **OR** `resource__state` **(Text) Exactly matches** `dismissed`

> 💡 This prevents the Zap from running when alerts transition to other states (e.g., `active` → `inProgress`) — saving tasks and avoiding incorrect closures.

### States That Should Trigger Close

| State | Action | Rationale |
|-------|--------|-----------|
| `fixed` | ✅ Close work item | Alert was resolved by fixing the code |
| `dismissed` | ✅ Close work item | Alert was reviewed and dismissed as non-issue |
| `active` | ❌ Skip | New or reopened — don't close |
| `inProgress` | ❌ Skip | Being worked on — don't close |

---

## Step 3: Code by Zapier — Build Search Query

1. Click **+** to add a step
2. App: **Code by Zapier**
3. Event: **Run JavaScript**
4. **Input Data:**

| Key | Value (from trigger) |
|-----|---------------------|
| `alertId` | `{{resource__alertId}}` |
| `repoName` | `{{resource__repository__name}}` |
| `state` | `{{resource__state}}` |

5. **Code:**

```javascript
const repoName = inputData.repoName || 'unknown-repo';
const alertId = inputData.alertId || '0';
const state = inputData.state || 'fixed';

// Build the same dedup tag used during creation
const ghasTag = `GHAzDO-${repoName}-${alertId}`;

// WIQL to find open work items with this tag
const wiqlQuery = JSON.stringify({
  query: `SELECT [System.Id] FROM WorkItems WHERE [System.Tags] CONTAINS '${ghasTag}' AND [System.State] <> 'Done' AND [System.State] <> 'Closed' AND [System.State] <> 'Removed'`
});

// Determine close reason based on alert state
const closeComment = state === 'dismissed'
  ? 'Auto-closed: GHAzDO alert dismissed as non-issue.'
  : 'Auto-closed: GHAzDO alert resolved/fixed.';

output = {
  ghasTag,
  wiqlQuery,
  closeComment,
  alertState: state
};
```

6. Click **Test step** → verify output

---

## Step 4: Webhooks by Zapier — Search for Work Item

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
| **Body** | Use `wiqlQuery` from Step 3 |

5. Click **Test step** → verify the response returns a work item ID

### Extracting the Work Item ID

The WIQL response looks like:
```json
{
  "workItems": [
    { "id": 123, "url": "..." }
  ]
}
```

You'll need the first work item's `id` for the next step. Use **Code by Zapier** or **Formatter** to extract it:

**Quick Code step (optional):**
```javascript
const response = JSON.parse(inputData.responseBody);
const workItems = response.workItems || [];
output = {
  workItemId: workItems.length > 0 ? String(workItems[0].id) : '',
  found: workItems.length > 0 ? 'true' : 'false'
};
```

---

## Step 5: Filter — Only Continue if Work Item Found

1. Click **+** to add a step
2. App: **Filter by Zapier**
3. Configure:
   - **Only continue if...**
   - Field: `found` (from the extraction step)
   - Condition: **(Text) Exactly matches**
   - Value: `true`

> 💡 If the work item was already closed or never created, the Zap stops here — no wasted tasks.

---

## Step 6: Webhooks by Zapier — Update Work Item to Closed

1. Click **+** to add a step
2. App: **Webhooks by Zapier**
3. Event: **Custom Request**
4. Configure:

| Field | Value |
|-------|-------|
| **Method** | PATCH |
| **URL** | `https://dev.azure.com/{YOUR_ORG}/{YOUR_PROJECT}/_apis/wit/workitems/{WORK_ITEM_ID}?api-version=7.1` |
| **Headers** | `Content-Type: application/json-patch+json` |
| | `Authorization: Basic {BASE64_OF_COLON_PAT}` |
| **Body** | See below |

**URL:** Replace `{WORK_ITEM_ID}` with the `workItemId` extracted in Step 4.

**Body:**
```json
[
  {
    "op": "add",
    "path": "/fields/System.State",
    "value": "Done"
  },
  {
    "op": "add",
    "path": "/fields/System.History",
    "value": "Auto-closed: GHAzDO alert resolved/fixed."
  }
]
```

> Use the `closeComment` from Step 3 for the History value to differentiate between fixed and dismissed.

5. Click **Test step** → verify the work item state changes to Done in ADO

---

## Final Zap Configuration

1. **Name the Zap:** `GHAzDO Alert Resolved → Close ADO Work Item`
2. Review all steps
3. **Turn on** the Zap
4. Verify in Zapier Task History

---

## Zap Flow Diagram

```
┌──────────────────────────┐
│ 1. Catch Hook (Trigger)  │
│    stateChanged webhook  │
└───────────┬──────────────┘
            ▼
┌──────────────────────────┐
│ 2. Filter                │
│    state = fixed OR      │
│    state = dismissed     │
└───────────┬──────────────┘
            ▼
┌──────────────────────────┐
│ 3. Code by Zapier        │
│    Build search query    │
│    + close comment       │
└───────────┬──────────────┘
            ▼
┌──────────────────────────┐
│ 4. Custom Request        │
│    WIQL search for       │
│    matching work item    │
└───────────┬──────────────┘
            ▼
┌──────────────────────────┐
│ 5. Filter                │
│    Only if work item     │
│    found                 │
└───────────┬──────────────┘
            ▼
┌──────────────────────────┐
│ 6. Custom Request        │
│    PATCH → Update state  │
│    to Done/Closed        │
└──────────────────────────┘
```

---

## Advanced: Single Zap with Paths (Professional Tier)

If you have Professional tier ($49/mo), you can combine both Zaps into one using **Paths**:

1. Single Catch Hook trigger (one webhook URL for both events)
2. **Path A:** `eventType` contains `created` → Create flow
3. **Path B:** `eventType` contains `stateChanged` AND `state` is `fixed` or `dismissed` → Close flow

**Benefits:**
- Single webhook URL to configure in ADO
- Single Service Hook needed
- Saves ~1 task per event (shared trigger)
- Easier to manage

**Trade-off:**
- Requires Professional tier ($49/mo vs $20/mo Starter)
- More complex Zap to debug
