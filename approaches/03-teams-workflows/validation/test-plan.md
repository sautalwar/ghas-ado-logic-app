# Test Plan — Approach #3: Teams Workflows

## Test Environment Requirements

- Microsoft Teams with Workflows enabled (M365 Business Basic+)
- Azure DevOps organization with GHAzDO enabled
- At least one repository with Advanced Security turned on
- ADO project with work item tracking configured
- Service hook permissions (Project Administrator)

---

## Test 1: Webhook Receives GHAzDO Alert Event

**Objective:** Verify the Teams Workflow webhook endpoint receives and acknowledges the ADO Service Hook payload.

| Item | Detail |
|------|--------|
| **Pre-condition** | Teams Workflow saved and webhook URL copied |
| **Trigger** | ADO Service Hook "Test" button OR manual `Invoke-RestMethod` |
| **Steps** | 1. Go to ADO → Project Settings → Service hooks<br>2. Click Test on the GHAzDO → Webhook subscription<br>3. Check Teams Workflow run history |
| **Expected** | Workflow run appears with status "Succeeded" or "Running" |
| **Pass Criteria** | HTTP 200/202 response from webhook, run visible in history |
| **Failure Action** | Check URL is correct, workflow is not paused, Teams Workflows app is accessible |

### Manual Test Command

```powershell
$webhookUrl = "YOUR_TEAMS_WORKFLOW_WEBHOOK_URL"
$payload = '{"eventType":"advancedsecurity.alert.created","resource":{"alertType":"secret","alertId":1,"severity":"high","secretType":"Test Secret","repository":{"name":"test-repo"},"location":{"file":"test.yml","line":1},"link":"https://dev.azure.com/org/project"},"message":{"text":"Test alert"}}'

Invoke-RestMethod -Uri $webhookUrl -Method POST -Body $payload -ContentType "application/json"
```

---

## Test 2: Workflow Parses Payload Correctly

**Objective:** Verify the Parse JSON step successfully extracts all required fields from the GHAzDO webhook payload.

| Item | Detail |
|------|--------|
| **Pre-condition** | Test 1 passed (webhook received) |
| **Trigger** | Same as Test 1 |
| **Steps** | 1. Open the workflow run in Teams Workflows<br>2. Click on the "Parse JSON" step<br>3. Inspect the outputs |
| **Expected** | All fields extracted: eventType, alertType, alertId, severity, secretType, repository.name, location.file, link |
| **Pass Criteria** | No "null" or missing fields for required properties |
| **Failure Action** | Update the JSON schema to match actual payload structure |

### Validation Checklist

- [ ] `eventType` = "advancedsecurity.alert.created"
- [ ] `resource.alertType` = "secret" (or "code" / "dependency")
- [ ] `resource.alertId` is a number
- [ ] `resource.severity` is one of: critical, high, medium, low
- [ ] `resource.repository.name` is a string
- [ ] `resource.location.file` is a string (or null for dependency alerts)
- [ ] `resource.link` is a valid URL

---

## Test 3: Work Item Created in ADO with Correct Fields

**Objective:** Verify a work item is created in Azure DevOps with the correct title, description, tags, and priority.

| Item | Detail |
|------|--------|
| **Pre-condition** | Tests 1 and 2 passed |
| **Trigger** | Send test payload via Service Hook test or manual POST |
| **Steps** | 1. Send a test secret scanning alert<br>2. Go to ADO Boards → Work Items<br>3. Search for the created work item<br>4. Verify all fields |
| **Expected** | New work item created with fields as specified below |
| **Pass Criteria** | All field checks pass |
| **Failure Action** | Check ADO connector sign-in, permissions, Compose step expressions |

### Field Verification

| Field | Expected Value (Secret Alert Example) |
|-------|--------------------------------------|
| **Type** | Issue |
| **Title** | `[GHAzDO-Secret] Test Secret` |
| **Description** | HTML table with Alert Type, Severity, Repository, File, Alert ID |
| **Tags** | `GHAzDO;secret;high;GHAzDO-test-repo-1` |
| **Priority** | 1 (because severity = high) |
| **State** | New (default) |

---

## Test 4: All 3 Alert Types Handled

**Objective:** Verify the workflow correctly processes secret scanning, code scanning, and dependency alerts with appropriate title prefixes.

| Item | Detail |
|------|--------|
| **Pre-condition** | Test 3 passed for secret alerts |
| **Trigger** | Send three separate test payloads |
| **Steps** | 1. Send secret scanning payload (alertType: "secret")<br>2. Send code scanning payload (alertType: "code")<br>3. Send dependency payload (alertType: "dependency")<br>4. Verify each creates correct work item |

### Test Payloads

**4a. Secret Scanning Alert:**
```json
{
  "eventType": "advancedsecurity.alert.created",
  "resource": {
    "alertType": "secret",
    "alertId": 100,
    "severity": "high",
    "secretType": "Azure Storage Account Key",
    "repository": { "name": "test-repo" },
    "location": { "file": "appsettings.json", "line": 22 },
    "link": "https://dev.azure.com/org/proj/_git/test-repo/alerts/100"
  },
  "message": { "text": "Secret scanning alert" }
}
```
**Expected Title:** `[GHAzDO-Secret] Azure Storage Account Key`

**4b. Code Scanning Alert:**
```json
{
  "eventType": "advancedsecurity.alert.created",
  "resource": {
    "alertType": "code",
    "alertId": 101,
    "severity": "critical",
    "title": "SQL Injection in login handler",
    "rule": { "id": "csharp/sql-injection", "description": "SQL Injection" },
    "repository": { "name": "test-repo" },
    "location": { "file": "Controllers/AuthController.cs", "line": 45 },
    "link": "https://dev.azure.com/org/proj/_git/test-repo/alerts/101"
  },
  "message": { "text": "Code scanning alert" }
}
```
**Expected Title:** `[GHAzDO-CodeScan] SQL Injection in login handler`

**4c. Dependency Alert:**
```json
{
  "eventType": "advancedsecurity.alert.created",
  "resource": {
    "alertType": "dependency",
    "alertId": 102,
    "severity": "medium",
    "title": "lodash prototype pollution",
    "advisoryTitle": "Prototype Pollution in lodash",
    "repository": { "name": "test-repo" },
    "location": { "file": "package-lock.json" },
    "link": "https://dev.azure.com/org/proj/_git/test-repo/alerts/102"
  },
  "message": { "text": "Dependency alert" }
}
```
**Expected Title:** `[GHAzDO-Dependency] lodash prototype pollution`

### Pass Criteria

- [ ] Secret alert: Title starts with `[GHAzDO-Secret]`
- [ ] Code scan alert: Title starts with `[GHAzDO-CodeScan]`
- [ ] Dependency alert: Title starts with `[GHAzDO-Dependency]`
- [ ] All three work items have correct tags with respective alert types
- [ ] Priority maps correctly: critical/high → 1, medium → 2, low → 3

---

## Test 5: State Change Closes Work Item (Optional Auto-Close Workflow)

**Objective:** Verify the auto-close workflow receives a state change event and closes the corresponding work item.

| Item | Detail |
|------|--------|
| **Pre-condition** | Auto-close workflow built (Step 6 in README), work item from Test 3 exists |
| **Trigger** | Send state change payload to auto-close webhook |
| **Steps** | 1. Note the work item ID created in Test 3<br>2. Send state change payload<br>3. Check if work item state changed to Done |

### Test Payload

```json
{
  "eventType": "advancedsecurity.alert.statechanged",
  "resource": {
    "alertType": "secret",
    "alertId": 1,
    "severity": "high",
    "state": "fixed",
    "previousState": "active",
    "newState": "fixed",
    "repository": { "name": "test-repo" },
    "link": "https://dev.azure.com/org/proj/_git/test-repo/alerts/1"
  },
  "message": { "text": "Alert state changed to fixed" }
}
```

### Expected Result

| Field | Expected |
|-------|----------|
| **Work Item State** | Done (or Closed) |
| **History** | "Auto-closed: GHAzDO alert resolved/fixed." |

### Known Limitations for This Test

- ⚠️ Auto-close requires finding the work item by tag, which needs either a saved ADO query or Premium HTTP connector
- ⚠️ Without Premium, the "Get query results" action returns all items from a saved query — filtering happens in the workflow
- ⚠️ If no matching work item found, workflow should succeed but skip the update

---

## Test Summary Matrix

| Test | Description | Priority | License | Status |
|------|-------------|----------|---------|--------|
| T1 | Webhook receives event | P0 - Critical | Standard | ☐ |
| T2 | Payload parsed correctly | P0 - Critical | Standard | ☐ |
| T3 | Work item created correctly | P0 - Critical | Standard | ☐ |
| T4 | All 3 alert types handled | P1 - High | Standard | ☐ |
| T5 | Auto-close on state change | P2 - Medium | Standard* | ☐ |

*Auto-close with full dedup requires Premium for WIQL. Basic close via saved query uses Standard.
