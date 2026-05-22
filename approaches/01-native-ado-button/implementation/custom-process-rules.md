# Custom Process Rules for GHAzDO Security Work Items

## Overview

Azure DevOps Process Rules are server-side rules that automatically set or validate field values when work items are created or modified. Unlike Board rules (which only trigger on column moves), Process rules fire on any work item state change, field change, or creation.

> **Prerequisite:** Process rules require an **Inherited Process** (not the default Agile/Scrum/CMMI). If you're using a system process, you must first create an inherited process.

---

## How to Access Process Rules

### Navigation Path

1. Go to **Organization Settings** (⚙️ bottom-left → Organization settings)
2. Under **Boards**, click **Process**
3. Click on your inherited process (e.g., "Learfield Agile")
4. Click on the work item type: **Bug**
5. Click the **Rules** tab
6. Click **+ New rule**

### Creating an Inherited Process (if needed)

If you're using a default system process:

1. Go to **Organization Settings** → **Process**
2. Click the **⋯** menu on "Agile" (or your current process)
3. Select **Create inherited process**
4. Name it: e.g., "Learfield Agile"
5. Go to **Project Settings** → **Overview** → change the process to your inherited one

---

## Recommended Rules

### Rule 1: Auto-Prioritize Security Items

**Purpose:** Any work item tagged `security` automatically gets Priority 2 (High) when created.

| Setting | Value |
|---------|-------|
| **Name** | Auto-prioritize security alerts |
| **Condition** | `A work item is created` AND `Tags contains security` |
| **Action** | Set **Priority** = `2` |

**Steps:**
1. Click **+ New rule**
2. Set condition: **A work item is created**
3. Add condition: **Tags** → **contains** → `security`
4. Set action: **Set the value of** → **Priority** → `2`
5. Save

---

### Rule 2: Auto-Assign Security Lead on Creation

**Purpose:** New GHAzDO-tagged items are automatically assigned to the security team lead.

| Setting | Value |
|---------|-------|
| **Name** | Auto-assign GHAzDO to security lead |
| **Condition** | `A work item is created` AND `Tags contains GHAzDO` |
| **Action** | Set **Assigned To** = `{security-lead@company.com}` |

**Steps:**
1. Click **+ New rule**
2. Set condition: **A work item is created**
3. Add condition: **Tags** → **contains** → `GHAzDO`
4. Set action: **Set the value of** → **Assigned To** → `{Security Lead email}`
5. Save

---

### Rule 3: Require Justification When Closing Security Items

**Purpose:** When closing a GHAzDO work item, require the "Resolved Reason" field to be filled in.

| Setting | Value |
|---------|-------|
| **Name** | Require resolution reason for security items |
| **Condition** | `State changed to Closed` AND `Tags contains GHAzDO` |
| **Action** | Make **Resolved Reason** required |

**Steps:**
1. Click **+ New rule**
2. Set condition: **A work item state changes to** → **Closed**
3. Add condition: **Tags** → **contains** → `GHAzDO`
4. Set action: **Make required** → **Resolved Reason**
5. Save

---

### Rule 4: Auto-Set Area Path for Security Tags

**Purpose:** Ensure GHAzDO items always go to the Security area path.

| Setting | Value |
|---------|-------|
| **Name** | Route GHAzDO to Security area |
| **Condition** | `A work item is created` AND `Tags contains GHAzDO` |
| **Action** | Set **Area Path** = `{Project}\Security` |

**Steps:**
1. Click **+ New rule**
2. Set condition: **A work item is created**
3. Add condition: **Tags** → **contains** → `GHAzDO`
4. Set action: **Set the value of** → **Area Path** → `{Project}\Security`
5. Save

---

### Rule 5: Prevent Closing Without Verification

**Purpose:** Don't allow closing unless the alert has been verified as resolved.

| Setting | Value |
|---------|-------|
| **Name** | Require verification for security closure |
| **Condition** | `State changed to Closed` AND `Tags contains security` |
| **Action** | Make **Description** required (ensures user has documented verification) |

> **Note:** ADO doesn't have a built-in "verification" field, but making Description required ensures the user documents what was verified before closing.

---

## Custom Fields (Optional Enhancement)

For more structured tracking, add custom fields to your inherited process:

### Add "GHAzDO Alert Type" Field

1. In the Bug work item type, click **+ New field**
2. Configure:
   - **Name:** GHAzDO Alert Type
   - **Type:** Picklist (string)
   - **Values:** Secret Scanning, Code Scanning, Dependency Alert
3. Add to the work item layout in a "Security Details" group

### Add "GHAzDO Alert URL" Field

1. Click **+ New field**
2. Configure:
   - **Name:** GHAzDO Alert URL
   - **Type:** Text (single line)
3. Add to the "Security Details" group

### Add "Security Verified" Field

1. Click **+ New field**
2. Configure:
   - **Name:** Security Verified
   - **Type:** Boolean (checkbox)
3. Add a rule: State cannot change to Closed unless Security Verified = True

---

## Process Rules vs Board Rules — When to Use Which

| Feature | Process Rules | Board Rules |
|---------|--------------|-------------|
| **Triggers on** | Create, state change, field change | Board column change only |
| **Scope** | All work items in the process | Only items on a specific board |
| **Can set fields** | ✅ Yes | ✅ Yes (limited) |
| **Can make fields required** | ✅ Yes | ❌ No |
| **Can validate values** | ✅ Yes | ❌ No |
| **Applies automatically** | ✅ Yes (server-side) | Only when board is used |
| **Requires inherited process** | ✅ Yes | ❌ No |

**Recommendation:** Use Process Rules for enforcement (auto-assign, required fields) and Board Rules for convenience (state sync on column move).
