# Approach #2 — Azure Boards App for Teams + Service Hook Notifications

> **The "Hidden Gem" approach:** Zero infrastructure, zero cost, ~15 minutes setup.
> GHAzDO security alerts automatically appear in your Teams channel with one-click work item creation.

---

## Overview

| Dimension | Value |
|-----------|-------|
| **Setup Time** | ~15 minutes |
| **Cost** | Free |
| **Infrastructure** | None (uses existing Teams + ADO) |
| **Automation Level** | Semi-auto: notifications + one-click work item creation |
| **Alert Types** | All 3 (Secret Scanning, Code Scanning, Dependency) |
| **Auto-Create** | No — requires one click from Teams notification |
| **Auto-Close** | No — notification-only for state changes |
| **Deduplication** | No |

### How It Works (End-to-End Flow)

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌──────────────┐
│   Developer   │     │   ADO GHAzDO     │     │  ADO Service    │     │  Microsoft   │
│  pushes code  │────▶│  detects alert   │────▶│  Hook fires     │────▶│  Teams       │
└──────────────┘     └──────────────────┘     └─────────────────┘     │  channel     │
                                                                       │  notification│
                                                                       └──────┬───────┘
                                                                              │
                                                                              ▼
                                                                       ┌──────────────┐
                                                                       │  Team member  │
                                                                       │  clicks       │
                                                                       │  "Create WI"  │
                                                                       │  in Teams     │
                                                                       └──────┬───────┘
                                                                              │
                                                                              ▼
                                                                       ┌──────────────┐
                                                                       │  ADO Work    │
                                                                       │  Item created │
                                                                       └──────────────┘
```

1. A developer pushes code (or a PR is created) in an ADO repo with GHAzDO enabled
2. GHAzDO scans and detects a security alert (secret, vulnerability, or dependency issue)
3. ADO Service Hook fires for the `advancedsecurity.alert.created` event
4. A rich notification appears in the configured Teams channel with alert details
5. A team member reviews the notification and clicks to create a work item via Azure Boards App
6. When the alert is resolved, another notification fires via `advancedsecurity.alert.stateChanged`

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **Azure DevOps** | Organization with GHAzDO (Advanced Security) enabled |
| **ADO Permissions** | Project Administrator or Service Hooks Admin role |
| **Microsoft Teams** | Active Teams workspace with a channel for notifications |
| **Teams Permissions** | Ability to install apps and configure incoming webhooks |
| **Azure Boards App** | Free app from Teams App Store (installed in Step 1) |
| **GHAzDO License** | Advanced Security must be enabled on at least one repository |

---

## Step 1: Install Azure Boards App for Teams

The Azure Boards App enables rich work item interactions directly from Teams.

### Navigation

1. Open **Microsoft Teams**
2. Click the **Apps** icon (bottom-left sidebar, or "+" in the left rail)
3. Search for **"Azure Boards"**
4. Click **Azure Boards** by Microsoft Corporation
5. Click **Add** → Select **Add to a team**
6. Choose the team/channel where you want security alerts (e.g., "Security Alerts")
7. Click **Set up a bot**

### Verify Installation

After installation, you should be able to type `@Azure Boards` in the channel and see auto-complete suggestions. Run:

```
@Azure Boards signin
```

Follow the authentication prompt to connect your ADO account.

> 📖 **Detailed guide:** See [`implementation/boards-app-setup.md`](implementation/boards-app-setup.md)

---

## Step 2: Connect ADO Project to Teams Channel

### Link Your ADO Project

1. In the Teams channel, type:
   ```
   @Azure Boards link https://dev.azure.com/{your-org}/{your-project}
   ```
2. Approve the connection when prompted
3. Verify by typing:
   ```
   @Azure Boards subscriptions
   ```

This enables the one-click work item creation capability from any message in the channel.

---

## Step 3: Configure ADO Service Hooks for GHAzDO Alert Events

This is the core configuration — it creates the automated notification pipeline.

### 3a: Service Hook for Alert Created

1. Go to **Azure DevOps** → Your Project → **Project Settings** (gear icon, bottom-left)
2. Under **General**, click **Service hooks**
3. Click **+ Create subscription**
4. In the service list, select **Microsoft Teams** (or **Web Hooks** if Teams isn't listed)
5. Click **Next**

#### Configure the Trigger

| Field | Value |
|-------|-------|
| **Trigger on this type of event** | `Advanced Security alert created` |
| **Repository** | Select your repository (or leave "Any" for all repos) |
| **Alert type** | Any (covers secret, dependency, and code scanning) |

6. Click **Next**

#### Configure the Action

**If using Microsoft Teams consumer:**

| Field | Value |
|-------|-------|
| **Microsoft Teams webhook URL** | Paste your Teams channel incoming webhook URL |

**To get the Teams webhook URL:**
1. In Teams, click the **"..."** (More options) on the target channel
2. Select **Connectors** (or **Manage channel** → **Connectors**)
3. Find **Incoming Webhook** → Click **Configure**
4. Name it: `GHAzDO Alerts`
5. Optionally upload an icon (use the ADO shield icon)
6. Click **Create** → Copy the webhook URL

7. Paste the webhook URL back in the ADO Service Hook configuration
8. Click **Test** to verify connectivity
9. Click **Finish**

### 3b: Service Hook for Alert State Changed

Repeat Steps 1–9 above with this change:

| Field | Value |
|-------|-------|
| **Trigger on this type of event** | `Advanced Security alert state changed` |
| **Repository** | Same as above |
| **Alert type** | Any |

This will notify the channel when alerts are resolved, dismissed, or reopened.

> 📖 **Configuration JSON:** See [`implementation/service-hook-config.json`](implementation/service-hook-config.json)

---

## Step 4: Notification Format

When a GHAzDO alert fires, the Teams channel receives a notification containing:

| Field | Example |
|-------|---------|
| **Alert Title** | "Secret detected in code" |
| **Alert Type** | Secret / Dependency / Code Scanning |
| **Severity** | Critical / High / Medium / Low |
| **Repository** | `my-project-repo` |
| **File/Location** | `src/config/database.js:42` |
| **State** | New / Active / Dismissed / Fixed |
| **Link** | Direct URL to the alert in ADO |

### Custom Adaptive Card (Optional)

If using **Web Hooks** instead of the native Teams consumer, you can customize the notification format with an Adaptive Card. See [`implementation/adaptive-card-template.json`](implementation/adaptive-card-template.json) for a template that provides:
- Color-coded severity badges
- Alert type icons
- One-click "View in ADO" button
- One-click "Create Work Item" action

---

## Step 5: Create Work Items from Teams Notifications

Once a notification appears in the Teams channel, team members can create work items in two ways:

### Option A: Azure Boards App Action (Recommended)

1. Hover over the notification message in Teams
2. Click the **"..."** (More actions) menu
3. Select **Azure Boards** → **Create Work Item**
4. A dialog appears with pre-filled information:
   - **Title:** Auto-populated from alert title
   - **Work Item Type:** Select (Bug, Task, Issue)
   - **Area Path:** Select your team area
   - **Assigned To:** Assign to a team member
   - **Description:** Alert details are included
5. Click **Create**
6. The work item is created in ADO and linked in the Teams message

### Option B: Direct Command

In the channel, reply to the notification:
```
@Azure Boards create bug "GHAzDO: [Alert Title]"
```

The Boards App will prompt you to fill in details.

---

## Step 6: Set Up a Dedicated "Security Alerts" Channel

For best results, create a dedicated channel:

1. In Teams, right-click your team → **Add channel**
2. Name: `🔒 Security Alerts` (or `GHAzDO Alerts`)
3. Description: "Automated security alert notifications from Azure DevOps Advanced Security"
4. Privacy: **Standard** (so all team members can see alerts)
5. Click **Add**
6. Install the Azure Boards App in this channel (Step 1)
7. Configure the service hooks to point to this channel's webhook (Step 3)

### Recommended Channel Settings

- **Pin** the channel so it's always visible
- **Enable notifications** for all new posts (so team members get desktop alerts)
- Add a **channel description** explaining the workflow
- Set up **channel moderation** if you want to prevent non-bot messages

> 📖 **Full guide:** See [`implementation/teams-channel-setup.md`](implementation/teams-channel-setup.md)

---

## Troubleshooting

### Notifications Not Appearing in Teams

| Issue | Solution |
|-------|----------|
| Webhook URL expired | Regenerate the incoming webhook in Teams channel settings |
| Service hook disabled | Check Project Settings → Service hooks → verify status is "Enabled" |
| Wrong channel | Verify the webhook URL matches the target channel |
| Permissions | Ensure the service hook creator has "Edit subscriptions" permission |
| Firewall/Network | Teams webhook URLs must be reachable from ADO (*.webhook.office.com) |

### Service Hook Test Fails

1. Go to Project Settings → Service hooks
2. Click on the subscription → **Test**
3. Check the response code:
   - **200/202:** Success
   - **400:** Malformed webhook URL
   - **403:** Authentication issue
   - **404:** Webhook was deleted or channel was removed

### Azure Boards App Not Responding

1. Try `@Azure Boards signin` to re-authenticate
2. Verify the app has the correct permissions in ADO
3. Uninstall and reinstall the app if issues persist

### Work Item Creation Fails

1. Verify the linked ADO project is correct: `@Azure Boards subscriptions`
2. Check that the user has "Create work items" permission in ADO
3. Ensure the work item type exists in the project

---

## Files in This Approach

```
approaches/02-teams-boards-app/
├── README.md                              ← You are here
├── implementation/
│   ├── service-hook-config.json           ← Service Hook JSON configuration
│   ├── teams-channel-setup.md             ← Teams channel setup guide
│   ├── adaptive-card-template.json        ← Custom notification card template
│   └── boards-app-setup.md               ← Azure Boards App installation guide
├── validation/
│   ├── test-plan.md                       ← Validation test cases
│   ├── expected-results.md                ← Expected outcomes per test
│   └── limitations.md                     ← Known limitations and gaps
└── Teams_Boards_App_Implementation.pdf    ← Complete PDF report
```

---

## Comparison with Other Approaches

| Feature | Phase 1 (Native ADO) | **Phase 1.5 (This)** | Phase 3 (Logic App) |
|---------|----------------------|----------------------|---------------------|
| Setup | 0 min | **15 min** | 5 min (deploy button) |
| Cost | Free | **Free** | $50–100/mo |
| Infrastructure | None | **None** | Azure Logic App |
| Notifications | None | **Teams channel** | Azure Monitor logs |
| Work Item Creation | Manual in ADO | **One-click in Teams** | Fully automated |
| Auto-Close | No | **No** | Yes |
| Deduplication | No | **No** | Yes |
| Visibility | ADO only | **Teams + ADO** | ADO + Azure Portal |

---

## When to Use This Approach

✅ **Use Phase 1.5 when:**
- Team wants visibility into security alerts without checking ADO
- Zero budget for infrastructure
- Team already uses Teams for collaboration
- "Good enough" automation (notification + one-click) meets needs
- Want to evaluate alert volume before investing in full automation

❌ **Upgrade to Logic App (Phase 3) when:**
- Need fully automated work item creation (no human click)
- Need auto-close when alerts are resolved
- Need deduplication (prevent duplicate work items)
- High alert volume makes manual triage impractical
- Compliance requires automated audit trail
