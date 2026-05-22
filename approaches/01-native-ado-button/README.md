# Approach #1 — Native ADO "Add" Button + Work Item Templates

## Overview

The simplest possible approach to creating Azure DevOps work items from GHAzDO (GitHub Advanced Security for Azure DevOps) security alerts. **Zero infrastructure, zero code, zero cost.**

This approach uses ADO's built-in "Add" button on the Advanced Security alerts page combined with pre-configured Work Item Templates to ensure consistent, well-structured work items for every security finding.

| Dimension | Value |
|-----------|-------|
| **Setup Time** | ~10 minutes |
| **Cost** | Free (included with GHAzDO license) |
| **Infrastructure** | None |
| **Automation Level** | Manual (user clicks "Add" button) |
| **Alert Types Supported** | Secret Scanning, Code Scanning, Dependency Alerts |
| **Auto-Close on Resolution** | ❌ No |
| **Deduplication** | ❌ No (manual awareness) |
| **Best For** | Teams wanting zero complexity, immediate adoption |

---

## Prerequisites

1. **Azure DevOps Organization** with a project enabled
2. **GitHub Advanced Security for Azure DevOps (GHAzDO)** enabled on at least one repository
   - Requires Azure DevOps Services (cloud) — not supported on Azure DevOps Server
   - Requires GHAzDO license (per active committer billing)
3. **Permissions required:**
   - **Project Collection Administrator** or **Project Administrator** — to customize process and create templates
   - **Work Item Create** permission — for users who will create work items from alerts
4. **At least one security alert** present (secret scanning, code scanning, or dependency) to test the workflow

---

## Step-by-Step Setup Instructions

### Step 1: Create a Custom Work Item Template (5 minutes)

Work Item Templates pre-fill fields when creating new work items, ensuring every security alert work item has consistent tags, area path, and description.

#### 1.1 Navigate to Work Item Templates

1. Open your ADO project in the browser
2. Click **Boards** in the left navigation
3. Click **Boards** → select your team's board (e.g., "Security Team")
4. Click the **⚙️ gear icon** (Board Settings) in the top-right
5. Select **Templates** tab

> **Alternative path:** You can also create templates from any work item form:
> 1. Create a new Bug or Task
> 2. Fill in the template fields (see below)
> 3. Click the **⋯** menu → **Templates** → **Capture template**

#### 1.2 Create the "GHAzDO Security Alert" Template

Click **+ New template** and select the work item type **Bug** (recommended for security findings).

Fill in the following fields:

| Field | Value | Why |
|-------|-------|-----|
| **Title** | `[GHAzDO] {Alert Type}: {Brief Description}` | Naming convention for easy filtering |
| **Tags** | `GHAzDO; security; triage` | Enables filtering and dashboard queries |
| **Area Path** | `{Project}\Security` | Routes to security team's backlog |
| **Iteration Path** | `{Project}\{Current Sprint}` | Places in current sprint for immediate triage |
| **Priority** | `2 - High` | Default for security findings (adjust per alert) |
| **Severity** | `2 - High` | Matches priority for security context |
| **Assigned To** | `{Security Team Lead}` | Or leave blank for triage assignment |
| **Description** | *(see template below)* | Structured description for consistency |

#### 1.3 Description Template

Use this HTML/markdown in the Description field:

```html
<h2>🔒 GHAzDO Security Alert</h2>

<h3>Alert Details</h3>
<table>
  <tr><td><b>Alert Type:</b></td><td>[Secret Scanning / Code Scanning / Dependency]</td></tr>
  <tr><td><b>Repository:</b></td><td>[repo name]</td></tr>
  <tr><td><b>Alert Severity:</b></td><td>[Critical / High / Medium / Low]</td></tr>
  <tr><td><b>Alert URL:</b></td><td>[paste link from GHAzDO]</td></tr>
  <tr><td><b>File/Location:</b></td><td>[affected file path]</td></tr>
  <tr><td><b>Date Detected:</b></td><td>[date]</td></tr>
</table>

<h3>Remediation Steps</h3>
<ol>
  <li>Review the alert in GHAzDO Advanced Security</li>
  <li>Determine if the finding is a true positive or false positive</li>
  <li>If true positive: implement the fix</li>
  <li>If false positive: dismiss the alert with justification</li>
  <li>Verify the alert is resolved in GHAzDO</li>
  <li>Close this work item</li>
</ol>

<h3>Acceptance Criteria</h3>
<ul>
  <li>[ ] Alert reviewed and triaged</li>
  <li>[ ] Fix implemented OR false positive documented</li>
  <li>[ ] GHAzDO alert status is "Closed" or "Dismissed"</li>
  <li>[ ] No regression introduced</li>
</ul>
```

#### 1.4 Save the Template

1. Name the template: **GHAzDO Security Alert**
2. Click **Save**
3. The template is now available to all team members

---

### Step 2: Configure Area Path for Security Team (2 minutes)

#### 2.1 Create the Security Area Path

1. Go to **Project Settings** (gear icon, bottom-left)
2. Under **Boards**, click **Project configuration**
3. Click the **Areas** tab
4. Click **+ New child** under the root area
5. Name it: **Security**
6. Click **Save and close**

#### 2.2 Assign the Security Team

1. Go to **Project Settings** → **Teams**
2. Select your security team (or create one: click **+ New team**, name it "Security Team")
3. Under the team's **Areas** configuration, add the **Security** area path
4. Set it as the default area path for the team

---

### Step 3: Using the Native "Add" Button from GHAzDO (per alert)

This is the day-to-day workflow for creating work items from security alerts.

#### 3.1 Navigate to GHAzDO Advanced Security

1. Open your ADO project
2. Go to **Repos** → **Advanced Security** (in the left navigation under Repos)
3. You'll see three tabs: **Secrets**, **Code**, **Dependencies**

#### 3.2 Create a Work Item from an Alert

1. Click on any alert to open its detail view
2. In the alert detail view, look for the **"Create work item"** or **"+"** button
   - This is typically in the top-right area of the alert detail
3. Click the button — a new work item form opens
4. The alert details are automatically linked to the work item

#### 3.3 Apply the Work Item Template

1. In the new work item form, click the **⋯** (more actions) menu
2. Select **Templates** → **GHAzDO Security Alert**
3. The template pre-fills: Tags, Area Path, Priority, Severity, and Description
4. Fill in the remaining details:
   - Update the **Title** with the specific alert name
   - Fill in the alert-specific fields in the Description table
   - Adjust **Priority** and **Severity** based on the actual alert
5. Click **Save**

#### 3.4 Verify the Link

After saving:
- The work item appears in the Security team's backlog
- The GHAzDO alert shows a link back to the work item
- The work item has a "Related Work" link to the alert

---

### Step 4: Set Up Board Automation Rules (2 minutes)

Board automation rules can auto-assign and auto-update work items based on column changes.

#### 4.1 Navigate to Board Rules

1. Go to **Boards** → select the Security team's board
2. Click **⚙️ Board Settings**
3. Select the **Automation** section (under Card rules or as a separate tab depending on your process)

#### 4.2 Recommended Automation Rules

| Rule | Trigger | Action | Purpose |
|------|---------|--------|---------|
| Auto-assign on Active | Card moved to **Active** | Set **Assigned To** = person who moved it | Ensures ownership |
| Auto-set In Progress | Card moved to **Active** | Set **State** = Active | Syncs board column with state |
| Auto-close Done | Card moved to **Done/Closed** | Set **State** = Closed | Ensures completion state |
| Tag-based assignment | Work item tagged `GHAzDO` | Set **Assigned To** = Security Lead | Routes security items |

> **Note:** Board automation rules are limited to column-change triggers. They cannot automatically create work items or respond to GHAzDO alert events.

See `implementation/board-automation-rules.md` for detailed configuration.

---

### Step 5: Create Custom Process Rules (Optional, 1 minute)

If you're using a custom (inherited) process, you can add rules that fire automatically.

#### 5.1 Navigate to Process Customization

1. Go to **Organization Settings** (not Project Settings)
2. Under **Boards**, click **Process**
3. Find your process (e.g., "Agile" or your inherited process)
4. Click on the work item type (e.g., **Bug**)
5. Click the **Rules** tab

#### 5.2 Recommended Rules

| Rule Name | Condition | Action |
|-----------|-----------|--------|
| Auto-prioritize security | Tag contains `security` | Set Priority = 2 |
| Require security tag justification | State changed to Closed AND Tag contains `GHAzDO` | Make "Resolved Reason" required |
| Auto-assign security team | Tag contains `GHAzDO` AND State = New | Set Assigned To = Security Lead |

See `implementation/custom-process-rules.md` for detailed configuration.

---

### Step 6: Create Dashboard Queries and Widgets (1 minute)

#### 6.1 Create the WIQL Query

1. Go to **Boards** → **Queries**
2. Click **+ New query**
3. Set up the query:
   - **Work Item Type** = Bug
   - **Tags** contains `GHAzDO`
   - **State** ≠ Closed, Removed
4. Save as: **GHAzDO Open Security Alerts**
5. Save under **Shared Queries** for team visibility

See `implementation/dashboard-query.wiql` for the exact WIQL.

#### 6.2 Add Dashboard Widget

1. Go to **Overview** → **Dashboards**
2. Click **+ Add a widget**
3. Add **Query Results** widget
4. Configure it to use the "GHAzDO Open Security Alerts" query
5. Optionally add:
   - **Chart for Work Items** widget for trend visualization
   - **Query Tile** for a count of open security items

---

## Day-to-Day Workflow Summary

```
┌─────────────────────────────────────────────────────┐
│  1. GHAzDO detects a security alert                 │
│     (secret, code vulnerability, or dependency)     │
├─────────────────────────────────────────────────────┤
│  2. Team member opens ADO → Repos → Advanced        │
│     Security and reviews the alert                  │
├─────────────────────────────────────────────────────┤
│  3. Clicks "Create work item" / "+" button          │
│     on the alert                                    │
├─────────────────────────────────────────────────────┤
│  4. Applies "GHAzDO Security Alert" template        │
│     (pre-fills tags, area, priority, description)   │
├─────────────────────────────────────────────────────┤
│  5. Fills in alert-specific details, saves          │
├─────────────────────────────────────────────────────┤
│  6. Work item appears on Security team board        │
│     Board rules auto-assign and manage state        │
├─────────────────────────────────────────────────────┤
│  7. Developer fixes the vulnerability               │
├─────────────────────────────────────────────────────┤
│  8. Manually verifies alert is resolved in GHAzDO   │
├─────────────────────────────────────────────────────┤
│  9. Manually closes the work item                   │
└─────────────────────────────────────────────────────┘
```

---

## Files in This Approach

| File | Description |
|------|-------------|
| `implementation/work-item-template.json` | Exportable Work Item Template definition |
| `implementation/board-automation-rules.md` | Board automation rules configuration guide |
| `implementation/custom-process-rules.md` | Process customization rules guide |
| `implementation/dashboard-query.wiql` | WIQL query for security dashboard |
| `validation/test-plan.md` | 5-step validation test plan |
| `validation/expected-results.md` | What success looks like |
| `validation/limitations.md` | Capabilities assessment and limitations |
| `Native_ADO_Button_Implementation.pdf` | Complete PDF report |
