# Azure Boards App for Teams — Installation & Setup Guide

## Overview

The **Azure Boards App** for Microsoft Teams allows you to:
- Create, view, and update work items directly from Teams
- Subscribe to work item notifications in channels
- Create work items from any Teams message (including service hook notifications)
- Link ADO projects to Teams channels for rich integration

---

## Step 1: Install the Azure Boards App

### From Teams Desktop or Web

1. Open **Microsoft Teams**
2. Click the **Apps** icon in the left sidebar (bottom)
3. In the search bar, type **"Azure Boards"**
4. Find **Azure Boards** by **Microsoft Corporation**
   - Verify the publisher is Microsoft (blue checkmark)
5. Click the app card → Click **Add**
6. Choose **Add to a team** from the dropdown
7. In the dialog:
   - Search for your team name
   - Select the specific **channel** (e.g., "🔒 Security Alerts")
8. Click **Set up a bot**

### From Teams Admin Center (Organization-wide)

If your Teams admin has restricted app installations:

1. Go to [Teams Admin Center](https://admin.teams.microsoft.com)
2. Navigate to **Teams apps** → **Manage apps**
3. Search for "Azure Boards"
4. Set the app status to **Allowed**
5. Users can then install it from the Apps store

---

## Step 2: Sign In to Azure DevOps

1. In the Teams channel where you installed the app, type:
   ```
   @Azure Boards signin
   ```
2. Click the **Sign in** button in the response card
3. You'll be redirected to Azure DevOps authentication
4. Sign in with your ADO credentials
5. Grant the requested permissions:
   - Read/write work items
   - Read project information
6. Return to Teams — you should see "✅ Successfully signed in"

### Verify Sign-In

```
@Azure Boards help
```

This should show available commands. If it says "Please sign in first," repeat the signin process.

---

## Step 3: Link an ADO Project

Link your ADO project to enable work item creation and subscriptions:

1. In the channel, type:
   ```
   @Azure Boards link https://dev.azure.com/{your-organization}/{your-project}
   ```
   
   **Example:**
   ```
   @Azure Boards link https://dev.azure.com/learfield/MySecurityProject
   ```

2. Confirm the link when prompted
3. Verify the link:
   ```
   @Azure Boards subscriptions
   ```

### Multiple Projects

You can link multiple projects to the same channel:
```
@Azure Boards link https://dev.azure.com/learfield/ProjectA
@Azure Boards link https://dev.azure.com/learfield/ProjectB
```

---

## Step 4: Configure Subscriptions (Optional)

The Azure Boards App can also send its own notifications for work item changes. This is separate from the GHAzDO service hooks but useful for tracking the work items you create:

### Subscribe to Work Item Updates

```
@Azure Boards subscriptions
```

From the subscription management card, you can:
- Add subscriptions for work item created/updated/deleted events
- Filter by area path, work item type, or assigned to
- Remove subscriptions you don't need

### Recommended Subscriptions for Security Workflow

| Subscription | Purpose |
|-------------|---------|
| Work item created (type = Bug, tag = "GHAzDO") | Track new security work items |
| Work item state changed | Track remediation progress |

---

## Step 5: Using the Boards App with GHAzDO Notifications

### Creating a Work Item from a Notification

When a GHAzDO alert notification appears in your channel (via service hook):

1. **Hover** over the notification message
2. Click the **"..."** (More actions) menu that appears
3. Select **More actions** → **Azure Boards** → **Create work item**
4. In the dialog that opens:

   | Field | Recommended Value |
   |-------|-------------------|
   | **Project** | Your linked ADO project |
   | **Work Item Type** | Bug (for vulnerabilities) or Task (for remediation) |
   | **Title** | Auto-filled from message; edit to add "GHAzDO: " prefix |
   | **Area Path** | Your team's area path |
   | **Iteration** | Current sprint |
   | **Assigned To** | Security champion or team lead |
   | **Tags** | Add "GHAzDO", "security-alert" |
   | **Priority** | Map from severity: Critical→1, High→2, Medium→3, Low→4 |
   | **Description** | Auto-filled from message content |

5. Click **Create**
6. A confirmation card appears with a link to the new work item

### Quick Create via Command

Reply to any message with:
```
@Azure Boards create bug "GHAzDO: [paste alert title here]"
```

The app will prompt you to fill in required fields.

---

## Useful Commands Reference

| Command | Description |
|---------|-------------|
| `@Azure Boards signin` | Sign in to Azure DevOps |
| `@Azure Boards signout` | Sign out |
| `@Azure Boards link [url]` | Link an ADO project to the channel |
| `@Azure Boards unlink [url]` | Unlink a project |
| `@Azure Boards subscriptions` | Manage notification subscriptions |
| `@Azure Boards create [type] "[title]"` | Create a work item |
| `@Azure Boards search [query]` | Search for work items |
| `@Azure Boards help` | Show available commands |

---

## Permissions Required

| Action | ADO Permission Needed |
|--------|----------------------|
| Sign in | Basic access level (or higher) |
| Link project | Project Reader (or higher) |
| Create work items | Contributor role in the project |
| Manage subscriptions | Project Reader + channel member in Teams |

---

## Troubleshooting

### "App not found" in Teams Store
- Your Teams admin may have blocked third-party apps
- Contact your Teams administrator to allow the Azure Boards app

### "Sign in failed"
- Ensure pop-ups are allowed in your browser
- Try signing out first: `@Azure Boards signout`, then sign in again
- Verify your ADO account has an active license (Basic or higher)

### "Unable to link project"
- Verify the project URL is correct (must include organization and project name)
- Ensure you have at least Reader access to the project
- Check that the project exists and is not disabled

### "Create work item failed"
- Verify you have Contributor access to the target project
- Check that required fields are populated (some projects have custom required fields)
- Ensure the work item type exists in the project's process template
