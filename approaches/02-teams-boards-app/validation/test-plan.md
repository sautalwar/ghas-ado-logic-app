# Validation Test Plan — Approach #2: Teams + Boards App

## Test Environment Prerequisites

| Item | Required |
|------|----------|
| ADO Organization with GHAzDO enabled | ✅ |
| At least one repository with Advanced Security | ✅ |
| Microsoft Teams with Azure Boards App installed | ✅ |
| Dedicated Teams channel with incoming webhook | ✅ |
| Two ADO Service Hooks configured (alert created + state changed) | ✅ |
| Test user with Contributor access to ADO project | ✅ |

---

## Test 1: Service Hook Fires on GHAzDO Alert Created → Notification Appears in Teams

**Objective:** Verify that when a new GHAzDO security alert is detected, a notification appears in the Teams channel.

**Steps:**

1. Navigate to the ADO repository with GHAzDO enabled
2. Commit a known secret to trigger a secret scanning alert:
   ```
   # test-secret.txt (to be committed and immediately removed)
   AZURE_STORAGE_KEY=dGVzdC1zZWNyZXQta2V5LWZvci12YWxpZGF0aW9u
   ```
   > ⚠️ Use a test/dummy value, not a real credential
3. Push the commit
4. Wait 1–5 minutes for GHAzDO to scan and detect the alert
5. Check the **🔒 Security Alerts** Teams channel

**Expected Result:**
- A notification message appears in the Teams channel
- The message is posted within 1–5 minutes of the alert being created
- No errors in the Service Hook history

**Pass Criteria:** Notification visible in Teams channel within 5 minutes of alert creation.

---

## Test 2: Notification Contains Alert Details

**Objective:** Verify the Teams notification includes sufficient alert details for triage.

**Steps:**

1. Using the notification from Test 1, examine the message content
2. Verify the following information is present:

**Expected Fields:**

| Field | Present | Example Value |
|-------|---------|---------------|
| Alert title/description | ✅ | "Secret detected in code" |
| Alert type | ✅ | Secret Scanning / Dependency / Code |
| Severity level | ✅ | Critical / High / Medium / Low |
| Repository name | ✅ | "my-project-repo" |
| File/location | ⚠️ | "src/config/db.js" (may not be in all notification formats) |
| Link to alert in ADO | ✅ | Clickable URL to alert detail page |
| State | ✅ | "Active" / "New" |

**Pass Criteria:** At minimum, alert title, type, severity, repository, and a link to ADO must be present.

**Notes:**
- The native Teams service hook consumer provides a standard format; custom adaptive cards provide richer detail
- File path may not be included in the default notification; this is a known limitation

---

## Test 3: User Can Create Work Item from Teams Notification

**Objective:** Verify that a team member can create an ADO work item directly from the Teams notification.

**Steps:**

1. Locate the GHAzDO alert notification from Test 1 in Teams
2. **Method A — Message Action:**
   - Hover over the notification message
   - Click **"..."** (More actions)
   - Select **More actions** → **Azure Boards** → **Create Work Item**
   - Fill in the work item dialog:
     - Type: Bug
     - Title: "GHAzDO: [Alert Title]"
     - Area Path: (your team area)
     - Tags: "GHAzDO", "security-alert"
   - Click **Create**
3. **Method B — Bot Command:**
   - Reply to the notification message
   - Type: `@Azure Boards create bug "GHAzDO: Secret detected in test-secret.txt"`
   - Fill in prompted fields
   - Confirm creation

**Expected Result:**
- A work item creation dialog/prompt appears
- The dialog is pre-filled with relevant information from the message
- After clicking Create, a confirmation card appears with:
  - Work item ID and title
  - Direct link to the work item in ADO
  - Status indicator (Created successfully)

**Pass Criteria:** Work item is created in ADO and confirmation appears in Teams.

---

## Test 4: Work Item Has Correct Fields Populated

**Objective:** Verify the created work item contains accurate and useful information.

**Steps:**

1. From the confirmation in Test 3, click the work item link to open it in ADO
2. Verify the following fields:

**Expected Work Item Fields:**

| Field | Expected Value |
|-------|----------------|
| **Title** | Contains alert title (e.g., "GHAzDO: Secret detected in code") |
| **Work Item Type** | Bug (or as selected during creation) |
| **State** | New |
| **Description** | Contains alert details from the Teams notification |
| **Tags** | "GHAzDO", "security-alert" (if added during creation) |
| **Area Path** | Matches what was selected in the dialog |
| **Created By** | The Teams user who clicked Create |

3. Verify the work item is in the correct project and area path
4. Verify the description contains enough context to act on the alert

**Pass Criteria:** Work item exists in ADO with correct type, title, and description.

**Notes:**
- The work item will NOT automatically contain a link back to the GHAzDO alert (this requires manual copy/paste of the alert URL)
- Fields available depend on the project's process template (Agile, Scrum, Basic, CMMI)

---

## Test 5: State Change Notification Appears When Alert Is Resolved

**Objective:** Verify that resolving a GHAzDO alert triggers a state change notification in Teams.

**Steps:**

1. Navigate to the GHAzDO alert created in Test 1
2. Resolve the alert by one of these methods:
   - **Fix the code:** Remove the committed secret, push the fix
   - **Dismiss the alert:** In ADO, go to the alert → Click Dismiss → Select a reason
3. Wait 1–5 minutes for the state change event to fire
4. Check the **🔒 Security Alerts** Teams channel

**Expected Result:**
- A new notification appears indicating the alert state changed
- The notification includes:
  - Alert ID/title
  - Previous state (e.g., "Active")
  - New state (e.g., "Fixed" or "Dismissed")
  - Repository name
  - Link to the alert

**Pass Criteria:** State change notification visible in Teams channel within 5 minutes.

---

## Test Summary Table

| Test | Description | Priority | Duration |
|------|-------------|----------|----------|
| Test 1 | Alert created → Teams notification | P0 (Critical) | 5 min |
| Test 2 | Notification has alert details | P0 (Critical) | 2 min |
| Test 3 | Create work item from notification | P0 (Critical) | 3 min |
| Test 4 | Work item fields correct | P1 (High) | 3 min |
| Test 5 | State change notification | P1 (High) | 5 min |

**Total estimated validation time:** ~20 minutes (including wait times for alert detection)

---

## Rollback Plan

If validation fails:

1. **Service Hook not firing:** Check Project Settings → Service hooks → click the subscription → view History for error details
2. **Webhook URL invalid:** Regenerate the Teams incoming webhook and update the service hook
3. **Boards App not working:** Uninstall and reinstall the Azure Boards App; re-authenticate with `@Azure Boards signin`
4. **Alert not detected:** Verify GHAzDO is enabled on the repository (Repos → Advanced Security)
