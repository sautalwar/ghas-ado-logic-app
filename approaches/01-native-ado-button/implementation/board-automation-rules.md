# Board Automation Rules for GHAzDO Security Work Items

## Overview

Azure DevOps Board automation rules trigger actions when work items move between board columns. These complement the Work Item Template by automating state transitions and assignments after work items are created.

> **Important:** Board rules can only react to column changes on the board. They cannot create work items or respond to external events like GHAzDO alerts.

---

## How to Configure Board Rules

### Navigation Path

1. Open your ADO project
2. Go to **Boards** → select the **Security Team** board
3. Click **⚙️ gear icon** (Board Settings) → **Automation** (or **Card rules** depending on process)

---

## Recommended Rules

### Rule 1: Auto-Assign When Work Begins

| Setting | Value |
|---------|-------|
| **Rule Name** | Auto-assign on Active |
| **Trigger** | Work item moved to **Active** column |
| **Action** | Set **Assigned To** = `<current user>` |
| **Purpose** | Ensures whoever picks up a security item is automatically assigned |

**Configuration Steps:**
1. In Board Settings → Automation
2. Find the **Active** column
3. Enable "Set **Assigned To** to the person who moved the item"

---

### Rule 2: Auto-Close When Done

| Setting | Value |
|---------|-------|
| **Rule Name** | Auto-close completed items |
| **Trigger** | Work item moved to **Closed** / **Done** column |
| **Action** | Set **State** = Closed |
| **Purpose** | Ensures board column and work item state stay in sync |

**Configuration Steps:**
1. In Board Settings → Automation
2. Find the **Closed/Done** column
3. Enable "Set **State** when moved to this column"
4. Map to **Closed** state

---

### Rule 3: Reopen When Moved Back

| Setting | Value |
|---------|-------|
| **Rule Name** | Reopen on regression |
| **Trigger** | Work item moved from **Closed** back to **Active** or **New** |
| **Action** | Set **State** = Active |
| **Purpose** | If a security fix regresses, the work item is automatically reopened |

**Configuration Steps:**
1. In Board Settings → Automation
2. Find the **Active** column
3. Enable "Set **State** when moved to this column"
4. Map to **Active** state

---

### Rule 4: Tag-Based Column (Swimlane Alternative)

While board rules cannot auto-move items based on tags, you can use **swimlanes** to separate GHAzDO items visually:

1. In Board Settings → **Swimlanes**
2. Click **+ Swimlane**
3. Name: **Security Alerts**
4. Add a rule: Tag contains `GHAzDO`

This creates a dedicated horizontal lane on the board for all GHAzDO-tagged items.

---

## Board Column Configuration

Recommended board columns for a Security team board:

| Column | State Mapping | WIP Limit | Purpose |
|--------|--------------|-----------|---------|
| **New** | New | 10 | Untriaged security alerts |
| **Triage** | New (or custom) | 5 | Being reviewed/prioritized |
| **Active** | Active | 3 | Fix in progress |
| **Review** | Resolved | 3 | Fix complete, awaiting verification |
| **Closed** | Closed | — | Alert resolved, work item done |

### How to Set Up Columns

1. Board Settings → **Columns**
2. Click **+ Column** to add Triage and Review
3. Map each column to the appropriate work item state
4. Set WIP (Work In Progress) limits as shown above

---

## Limitations of Board Automation Rules

| Capability | Supported? | Notes |
|-----------|-----------|-------|
| Auto-assign on column change | ✅ Yes | Built-in feature |
| Auto-set state on column change | ✅ Yes | Built-in feature |
| Auto-create work items from alerts | ❌ No | Requires Logic App or webhook automation |
| Auto-close when GHAzDO alert resolves | ❌ No | Requires external automation |
| Trigger based on tags | ❌ No | Swimlanes are visual-only alternative |
| Send notifications on column change | ✅ Yes | Via follow/subscription settings |
