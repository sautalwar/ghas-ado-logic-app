# One-Click Work Item Creation from GHAzDO Security Alerts

## What This Does
Create ADO work items directly from security alerts with a single click — no Logic Apps needed.

---

## Where to Find It

1. Go to your **ADO project** → **Repos** → **Advanced Security**
2. Open any security alert (code scanning, dependency, or secret scanning)
3. Look for the **"Related Work"** section in the alert details
4. Click **"Add"** to create a new work item or link to an existing one

---

## Creating a New Work Item

1. Click **"Add"** in the Related Work section
2. Select work item type: **Bug**, **Task**, or **Issue**
3. Fields auto-populate from alert data (title, description, severity)
4. Click **"Save"**

---

## Linking to an Existing Work Item

1. Click **"Add"** in the Related Work section
2. Search for the existing work item
3. Click to link it — the bidirectional connection is created instantly

---

## Bidirectional Navigation

- **From alert:** Click the linked work item to jump to Boards
- **From work item:** Click the linked alert to jump back to Advanced Security
- **From Boards:** Edit a work item → **Add Link** → select **"Advanced Security Alert"** as link type → search for the alert

---

## What Auto-Populates

The link creates a bidirectional connection. Alert metadata (type, severity, repo, file) is available in the alert view. Linked work items appear in the Related Work section of both the alert and the work item.

---

## Permissions

- You can only link alerts and work items you have access to
- Requires **GHAzDO enabled** on the repository
- No special permissions needed — same access rules as the alert itself

---

## Auto-Close Work Items on Fix (Optional)

If you also want work items to **auto-close when vulnerabilities are fixed**, deploy the optional Logic App for auto-closure (see README for one-click deploy button).

---

## Learn More

- **MS Blog:** [Work Item Linking for Advanced Security Alerts Now Available](https://devblogs.microsoft.com/devops/work-item-linking-for-advanced-security-alerts-now-available/)
- **Official Docs:** [Link Work Items to Advanced Security Alerts](https://learn.microsoft.com/en-us/azure/devops/boards/backlogs/add-link?view=azure-devops&tabs=browser#link-work-items-to-advanced-security-alerts)

---

**That's it.** No configuration, no Logic Apps. Just click and link.
