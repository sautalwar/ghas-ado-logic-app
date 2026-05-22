# Test Plan — Zapier Integration

> 7 validation tests for the GHAzDO → Zapier → ADO Work Item integration

## Test Environment

| Component | Requirement |
|-----------|-------------|
| ADO Organization | With GHAzDO (Advanced Security) enabled |
| ADO Project | With at least one repo configured for Advanced Security scanning |
| Zapier Account | Starter tier or higher (multi-step Zaps required) |
| Both Zaps | Created and turned ON |
| Service Hooks | Both configured (alert created + state changed) |

---

## Test 1: Service Hook Fires → Zap Triggers

**Objective:** Verify ADO Service Hook successfully delivers webhook payload to Zapier.

**Steps:**
1. In ADO, go to Project Settings → Service Hooks
2. Find the "Alert Created" service hook
3. Click the **Test** button
4. ADO sends a sample payload to the Zapier webhook URL

**Expected Result:**
- ✅ Zapier shows the test event in the Zap's Task History
- ✅ HTTP response from Zapier is `200 OK`
- ✅ Payload appears in the Catch Hook trigger output

**Failure Indicators:**
- ❌ HTTP 404 — Webhook URL is incorrect
- ❌ HTTP 410 — Zap is turned off or deleted
- ❌ No response — Network/firewall issue

---

## Test 2: Zap Parses GHAzDO Payload Correctly

**Objective:** Verify the Code by Zapier step correctly extracts and transforms all fields.

**Steps:**
1. Send a test payload (use sample from `webhook-payload-schema.json`)
2. Run Zap #1 in test mode (click "Test step" on the Code step)
3. Inspect the Code step output

**Expected Result:**
- ✅ `workItemTitle` has correct prefix: `[GHAzDO-Secret]`, `[GHAzDO-CodeScan]`, or `[GHAzDO-Dependency]`
- ✅ `tags` contains `GHAzDO;{alertType};{severity};GHAzDO-{repo}-{alertId}`
- ✅ `ghasTag` matches pattern `GHAzDO-{repoName}-{alertId}`
- ✅ `priority` is correctly mapped (critical/high→1, medium→2, low→3)
- ✅ `description` contains valid HTML with all fields populated
- ✅ `patchBody` is valid JSON array

**Failure Indicators:**
- ❌ Missing fields → Input Data mapping is wrong
- ❌ `undefined` in output → Nested field path incorrect (check `__` separators)
- ❌ Invalid JSON → String escaping issue in Code step

---

## Test 3: Work Item Created with Correct Fields

**Objective:** Verify Zap #1 creates an ADO work item with all fields correctly populated.

**Steps:**
1. Trigger a real GHAzDO alert (e.g., commit a test secret like `AKIAIOSFODNN7EXAMPLE`)
2. Wait for Service Hook to fire and Zap to execute
3. Check ADO Boards → Work Items for the new item

**Expected Result:**
- ✅ Work item exists in ADO
- ✅ Title: `[GHAzDO-Secret] Amazon AWS Access Key ID` (or similar)
- ✅ Description: HTML table with alert type, severity, repo, file, line, alert ID, tag
- ✅ Tags: `GHAzDO;secret;critical;GHAzDO-my-app-42`
- ✅ Priority: 1 (for critical severity)
- ✅ State: New (default)
- ✅ Work item type: Issue (or configured type)

**Failure Indicators:**
- ❌ No work item → Check Zapier Task History for errors
- ❌ 401 Unauthorized → PAT is invalid or expired
- ❌ 400 Bad Request → JSON patch body is malformed (check Content-Type header)
- ❌ 404 Not Found → Organization/project name is wrong in URL

---

## Test 4: All 3 Alert Types Handled

**Objective:** Verify the integration handles secret scanning, code scanning, and dependency alerts.

**Steps:**
1. Trigger each alert type:
   - **Secret:** Commit a known secret pattern (e.g., AWS key)
   - **Code scan:** Introduce a known vulnerability (e.g., SQL injection pattern)
   - **Dependency:** Add a package with known CVE to dependencies
2. Wait for each Service Hook to fire
3. Check ADO for three work items

**Expected Results:**

| Alert Type | Expected Title Prefix | Expected Tag |
|------------|----------------------|--------------|
| Secret | `[GHAzDO-Secret]` | `GHAzDO;secret;{severity};GHAzDO-{repo}-{id}` |
| Code | `[GHAzDO-CodeScan]` | `GHAzDO;code;{severity};GHAzDO-{repo}-{id}` |
| Dependency | `[GHAzDO-Dependency]` | `GHAzDO;dependency;{severity};GHAzDO-{repo}-{id}` |

- ✅ Three distinct work items created
- ✅ Each has correct title prefix
- ✅ Each has appropriate alert-type-specific fields populated

---

## Test 5: State Change → Work Item Closed

**Objective:** Verify Zap #2 closes the work item when the alert is resolved.

**Steps:**
1. Ensure a work item exists from Test 3 (with the dedup tag)
2. In ADO Advanced Security, dismiss or fix the alert
3. Wait for the stateChanged Service Hook to fire
4. Check the work item in ADO

**Expected Result:**
- ✅ Work item state changed to `Done`
- ✅ History comment: `"Auto-closed: GHAzDO alert resolved/fixed."` (or dismissed variant)
- ✅ Zapier Task History shows successful execution of Zap #2

**Failure Indicators:**
- ❌ Work item not closed → WIQL search didn't find it (check tag format matches)
- ❌ 400 error on PATCH → State transition not allowed (check workflow rules)
- ❌ Zap stopped at filter → Alert state was not `fixed` or `dismissed`

---

## Test 6: Deduplication — No Duplicate Work Items

**Objective:** Verify the WIQL search step prevents duplicate work items for the same alert.

**Steps:**
1. Ensure a work item already exists for alert ID 42 in repo "my-app" (from Test 3)
2. Re-trigger the same alert (or resend the test webhook payload)
3. Check ADO for work items with tag `GHAzDO-my-app-42`

**Expected Result:**
- ✅ Only ONE work item exists with tag `GHAzDO-my-app-42`
- ✅ Zapier Task History shows Zap #1 stopped at the dedup filter step
- ✅ No new work item was created

**Failure Indicators:**
- ❌ Duplicate created → WIQL query is wrong or filter condition is incorrect
- ❌ WIQL returns empty → Tag format mismatch between create and search
- ❌ Race condition → Two hooks fired simultaneously (rare; see Limitations)

---

## Test 7: Task Count per Alert Cycle

**Objective:** Verify task consumption matches expectations for Zapier billing.

**Steps:**
1. Reset or note current task count in Zapier dashboard
2. Execute one full alert lifecycle:
   a. Trigger a new alert (create event)
   b. Fix/dismiss the alert (state change event)
3. Check Zapier task count after both Zaps complete

**Expected Result:**

| Event | Steps Executed | Tasks |
|-------|---------------|-------|
| Alert created (new, no duplicate) | Trigger → Filter → Code → Search → Filter → Create | **5** |
| Alert state changed (close) | Trigger → Filter → Code → Search → Filter → Update | **5** |
| **Total for full lifecycle** | | **~10** |

- ✅ Total tasks for one full create+close cycle: ~9-10 tasks
- ✅ Starter tier (750 tasks/month) supports ~75 full cycles per month
- ✅ Professional tier (2,000 tasks/month) supports ~200 full cycles per month

**Note:** Filter steps that STOP the Zap do NOT count as tasks. Only filter steps that PASS count.

---

## Test Execution Checklist

| # | Test | Status | Date | Notes |
|---|------|--------|------|-------|
| 1 | Service Hook fires → Zap triggers | ⬜ | | |
| 2 | Payload parsed correctly | ⬜ | | |
| 3 | Work item created with correct fields | ⬜ | | |
| 4 | All 3 alert types handled | ⬜ | | |
| 5 | State change → work item closed | ⬜ | | |
| 6 | Dedup — no duplicates | ⬜ | | |
| 7 | Task count per cycle | ⬜ | | |
