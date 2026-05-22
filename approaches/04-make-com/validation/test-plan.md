# Test Plan — Make.com GHAzDO → ADO Integration

## Overview

8 validation tests covering the full Make.com scenario: webhook reception, JSON parsing, routing, work item creation (all 3 alert types), auto-close, dedup, and free tier operation counting.

---

## Test 1: Webhook Receives GHAzDO Alert Event

**Objective:** Verify Make.com webhook correctly receives HTTP POST from ADO Service Hook.

**Steps:**
1. In Make.com, open the scenario and click **"Run once"**
2. In ADO, go to Project Settings → Service hooks
3. Find the "Alert Created" service hook → click **"Test"**
4. Observe Make.com scenario execution

**Expected Result:**
- Make.com shows webhook module executed successfully (green checkmark)
- Input shows the full JSON payload from ADO
- HTTP response was 200 to ADO

**Failure Indicators:**
- ADO test shows non-200 response → check webhook URL
- Make.com shows no execution → webhook URL mismatch or scenario not in "Run once" mode

---

## Test 2: JSON Parser Extracts All Fields Correctly

**Objective:** Verify the JSON Parse module correctly maps all GHAzDO payload fields.

**Steps:**
1. After Test 1 succeeds, click on the JSON Parse module in the execution history
2. Expand the **Output** panel
3. Verify each field is populated

**Expected Result:**
| Field | Expected Value |
|-------|---------------|
| `eventType` | `advancedsecurity.alert.created` |
| `resource.alertType` | `secret`, `code`, or `dependency` |
| `resource.alertId` | Numeric ID |
| `resource.repository.name` | Repository name string |
| `resource.severity` | `critical`, `high`, `medium`, or `low` |
| `resource.title` | Alert description text |
| `resource.link` | Valid ADO URL |

**Failure Indicators:**
- Fields show as `null` or empty → data structure needs regeneration from a fresh sample payload
- Parse error → payload format has changed; update the data structure

---

## Test 3: Router Branches Correctly on Event Type

**Objective:** Verify the router sends `created` events to Branch 1 and `stateChanged` events to Branch 2.

**Steps:**
1. Send a test "Alert Created" event (via ADO Service Hook test)
2. Verify Branch 1 executes, Branch 2 is skipped
3. Send a test "Alert State Changed" event
4. Verify Branch 2 executes, Branch 1 is skipped

**Expected Result:**
- Created event → only Branch 1 modules execute (WIQL check → Create Work Item)
- State Changed event → only Branch 2 modules execute (WIQL find → Update Work Item)
- No crossover between branches

**Failure Indicators:**
- Both branches execute → filter conditions are wrong (check Contains vs Equals)
- Neither branch executes → eventType field mapping is incorrect

---

## Test 4: Work Item Created with Correct Fields

**Objective:** Verify the Azure DevOps "Create Work Item" module produces a correctly formatted work item.

**Steps:**
1. Trigger a secret scanning alert (or use ADO Service Hook test)
2. Let the scenario execute through Branch 1
3. Go to ADO → Boards → Work Items
4. Find the newly created work item

**Expected Result:**
| Work Item Field | Expected Value |
|----------------|---------------|
| **Title** | `[GHAzDO-Secret] Azure Storage Account Key` (example) |
| **Description** | HTML table with alert type, severity, repo, file, alert ID |
| **Tags** | `GHAzDO;secret;critical;GHAzDO-my-repo-42` |
| **Priority** | `1` (for critical/high), `2` (medium), `3` (low) |
| **State** | `New` (default) |
| **Work Item Type** | `Issue` |

**Failure Indicators:**
- Work item not created → check ADO connection, PAT scopes, project name
- Title missing prefix → check the if/else expression in title mapping
- Tags malformed → check tag concatenation expression

---

## Test 5: All 3 Alert Types Handled with Correct Prefix

**Objective:** Verify each alert type produces the correct title prefix.

**Steps:**
1. Send test events for each alert type (modify the test payload or trigger real alerts):
   - Secret scanning alert
   - Code scanning alert
   - Dependency alert

**Expected Result:**
| Alert Type | Title Prefix |
|------------|-------------|
| `secret` | `[GHAzDO-Secret]` |
| `code` | `[GHAzDO-CodeScan]` |
| `dependency` | `[GHAzDO-Dependency]` |
| Unknown/missing | `[GHAzDO-Alert]` |

**Failure Indicators:**
- All alerts get `[GHAzDO-Alert]` prefix → alertType field not being parsed correctly
- Wrong prefix → check the nested if() expression order

---

## Test 6: State Change Closes Existing Work Item

**Objective:** Verify that when a GHAzDO alert state changes to "fixed", the corresponding ADO work item is closed.

**Prerequisites:** A work item must already exist (from Test 4) with the correct GHAzDO tag.

**Steps:**
1. Note the work item created in Test 4 and its tag (e.g., `GHAzDO-my-repo-42`)
2. Trigger a state change event for the same alert (fix the alert in ADO, or use Service Hook test)
3. Let the scenario execute through Branch 2
4. Check the work item in ADO

**Expected Result:**
- Work item state changed from `New` → `Done`
- History/comment added: `Auto-closed: GHAzDO alert resolved/fixed.`
- Work item ID matches the one found by WIQL query

**Failure Indicators:**
- Work item not found → WIQL tag search not matching (check tag format consistency)
- State not changed → "Done" may not be valid; try "Closed" or "Resolved" based on process template
- Multiple work items found → first one is updated (by design)

---

## Test 7: Dedup Check — No Duplicate Work Items

**Objective:** Verify that sending the same alert twice does not create duplicate work items.

**Steps:**
1. Send a "created" event for alert ID 42 in repo "my-repo"
2. Verify work item is created with tag `GHAzDO-my-repo-42`
3. Send the SAME "created" event again (identical payload)
4. Check ADO for work items

**Expected Result:**
- First event: work item created ✅
- Second event: WIQL finds existing work item → filter blocks creation → no duplicate ✅
- Only 1 work item exists with tag `GHAzDO-my-repo-42`

**Failure Indicators:**
- Duplicate created → WIQL query or filter condition is wrong
- Error on second run → check WIQL response parsing
- Filter not blocking → verify the `length(workItems) equals 0` condition

---

## Test 8: Free Tier Operation Count

**Objective:** Verify the number of operations consumed per alert cycle matches expectations.

**Steps:**
1. Before testing, note the current operation count in Make.com (Organization → Usage)
2. Send one "Alert Created" event → let scenario complete
3. Note the new operation count
4. Send one "Alert State Changed" event → let scenario complete
5. Note the final operation count

**Expected Result:**

| Event | Expected Operations | Breakdown |
|-------|-------------------|-----------|
| Alert Created (new) | 4 | Webhook(1) + Parse(1) + HTTP-WIQL(1) + Create(1) |
| Alert Created (duplicate) | 3 | Webhook(1) + Parse(1) + HTTP-WIQL(1) + [blocked] |
| State Changed (found) | 4 | Webhook(1) + Parse(1) + HTTP-WIQL(1) + Update(1) |
| State Changed (not found) | 3 | Webhook(1) + Parse(1) + HTTP-WIQL(1) + [blocked] |
| **Full cycle (create + close)** | **7-8** | |

**Monthly capacity (1,000 ops):**
- ~125-142 full alert cycles (create + close)
- ~250 create-only events
- ~333 duplicate/no-op events

**Failure Indicators:**
- More operations than expected → check if additional modules are running (e.g., error handlers)
- Router counts as 0 operations (it's a flow control, not an execution module)

---

## Test Execution Checklist

| Test | Status | Date | Notes |
|------|--------|------|-------|
| Test 1: Webhook receives event | ⬜ | | |
| Test 2: JSON parser extracts fields | ⬜ | | |
| Test 3: Router branches correctly | ⬜ | | |
| Test 4: Work item created correctly | ⬜ | | |
| Test 5: All 3 alert types handled | ⬜ | | |
| Test 6: State change closes work item | ⬜ | | |
| Test 7: Dedup prevents duplicates | ⬜ | | |
| Test 8: Free tier ops count verified | ⬜ | | |
