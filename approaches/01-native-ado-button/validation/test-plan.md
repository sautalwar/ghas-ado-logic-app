# Test Plan — Approach #1: Native ADO "Add" Button + Work Item Templates

## Overview

This test plan validates that Approach #1 works end-to-end: creating work items from GHAzDO security alerts using the native "Add" button with pre-configured Work Item Templates.

**Total Tests:** 5
**Estimated Time:** 15–20 minutes
**Prerequisites:**
- GHAzDO enabled on at least one repository with active alerts
- Work Item Template "GHAzDO Security Alert" created (see README.md Step 1)
- Area Path "Security" configured (see README.md Step 2)
- Board automation rules configured (see README.md Step 4)

---

## Test 1: Create Work Item from Secret Scanning Alert

### Objective
Verify that a work item can be created from a GHAzDO secret scanning alert and linked correctly.

### Steps
1. Navigate to **Repos → Advanced Security → Secrets** tab
2. Click on an active secret scanning alert
3. Click the **"Create work item"** or **"+"** button
4. In the new work item form, apply the **"GHAzDO Security Alert"** template:
   - Click **⋯** → **Templates** → **GHAzDO Security Alert**
5. Update the Title: `[GHAzDO] Secret Scanning: {secret type} detected in {file}`
6. Fill in the Description table with alert-specific details
7. Click **Save**

### Expected Results
- [ ] Work item created as type **Bug**
- [ ] Tags contain: `GHAzDO`, `security`, `triage`
- [ ] Area Path set to `{Project}\Security`
- [ ] Priority set to 2
- [ ] Description contains the structured template
- [ ] Work item is linked to the GHAzDO alert (visible in "Related Work" section)
- [ ] Alert detail page in GHAzDO shows the linked work item

---

## Test 2: Create Work Item from Code Scanning Alert

### Objective
Verify that code scanning alerts (CodeQL/SARIF results) can generate work items.

### Steps
1. Navigate to **Repos → Advanced Security → Code** tab
2. Click on an active code scanning alert (e.g., SQL injection, XSS)
3. Click the **"Create work item"** / **"+"** button
4. Apply the **"GHAzDO Security Alert"** template
5. Update the Title: `[GHAzDO] Code Scanning: {vulnerability name} in {file}`
6. Fill in alert details including the specific CWE/rule ID
7. Click **Save**

### Expected Results
- [ ] Work item created with correct template fields
- [ ] Tags include `GHAzDO` and `security`
- [ ] Work item linked to the code scanning alert
- [ ] Alert severity matches the Priority adjustment guidelines
- [ ] Description includes remediation steps from the template

---

## Test 3: Create Work Item from Dependency Alert

### Objective
Verify that dependency vulnerability alerts (SCA/Dependabot-style) create proper work items.

### Steps
1. Navigate to **Repos → Advanced Security → Dependencies** tab
2. Click on an active dependency alert (e.g., vulnerable npm/NuGet package)
3. Click the **"Create work item"** / **"+"** button
4. Apply the **"GHAzDO Security Alert"** template
5. Update the Title: `[GHAzDO] Dependency: {package name} {CVE ID}`
6. Fill in alert details including the affected package and version
7. Click **Save**

### Expected Results
- [ ] Work item created with correct template fields
- [ ] Tags include `GHAzDO` and `security`
- [ ] Work item linked to the dependency alert
- [ ] Description includes upgrade/remediation guidance

---

## Test 4: Verify Template Pre-fills Correct Fields

### Objective
Verify that applying the Work Item Template correctly pre-fills all configured fields.

### Steps
1. Create a new Bug work item (without going through GHAzDO — just from Boards)
2. Click **⋯** → **Templates** → **GHAzDO Security Alert**
3. Inspect all fields

### Expected Results
- [ ] **Tags** = `GHAzDO; security; triage`
- [ ] **Area Path** = `{Project}\Security`
- [ ] **Priority** = `2`
- [ ] **Severity** = `2 - High`
- [ ] **Description** contains the full HTML template with:
  - Alert Details table
  - Remediation Steps (6 items)
  - Acceptance Criteria (4 checkboxes)
- [ ] **Repro Steps** contains navigation instructions
- [ ] Fields are editable (user can override template values)

---

## Test 5: Verify Board Automation Rules Trigger Correctly

### Objective
Verify that board automation rules fire when GHAzDO work items move between columns.

### Steps
1. Open the Security team's board
2. Locate a GHAzDO-tagged work item in the **New** column
3. Drag the work item to the **Active** column
4. Check the **Assigned To** field

### Expected Results
- [ ] Work item **State** changed to **Active** automatically
- [ ] **Assigned To** set to the person who moved the card (if rule configured)
5. Drag the work item to the **Closed** column
- [ ] Work item **State** changed to **Closed** automatically
6. Drag it back to **Active**
- [ ] Work item **State** changed back to **Active** (reopen rule)

---

## Test Summary Checklist

| Test | Description | Pass/Fail | Notes |
|------|-------------|-----------|-------|
| 1 | Secret scanning → work item | | |
| 2 | Code scanning → work item | | |
| 3 | Dependency alert → work item | | |
| 4 | Template pre-fills fields | | |
| 5 | Board rules trigger | | |

---

## Troubleshooting

### Template doesn't appear in the menu
- Ensure the template was saved under the correct team
- Templates are team-scoped — check you're on the right team's board

### "Create work item" button not visible
- Ensure GHAzDO is enabled for the repository
- Check user has "Work Item Create" permission
- Button may appear as "+" or link icon depending on ADO version

### Board rules don't trigger
- Rules only fire when items are dragged on the board UI
- API/bulk updates may not trigger board rules
- Verify rules are configured on the correct board (team-specific)

### Area Path not available
- Ensure the Security area path was created under Project Settings
- Verify the security team has the area path assigned
