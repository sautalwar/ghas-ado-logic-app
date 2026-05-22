# Teams Channel Configuration Guide — Security Alerts Channel

## Overview

This guide walks you through setting up a dedicated Microsoft Teams channel for receiving GHAzDO security alert notifications. A dedicated channel keeps security alerts organized and ensures team visibility.

---

## Step 1: Create the Security Alerts Channel

1. In Microsoft Teams, find your team in the left sidebar
2. Right-click the team name → Select **Add channel**
3. Configure the channel:

   | Setting | Recommended Value |
   |---------|-------------------|
   | **Channel name** | `🔒 Security Alerts` |
   | **Description** | Automated GHAzDO security alert notifications from Azure DevOps Advanced Security. One-click work item creation via Azure Boards App. |
   | **Privacy** | Standard — accessible to everyone on the team |

4. Click **Add**

### Alternative Channel Names
- `GHAzDO Alerts`
- `Security Notifications`
- `DevSecOps Alerts`
- `Vulnerability Alerts`

---

## Step 2: Configure Incoming Webhook

The incoming webhook receives notifications from ADO Service Hooks.

### Create the Webhook

1. Open the **🔒 Security Alerts** channel
2. Click the **"..."** (More options) next to the channel name
3. Select **Connectors** (or **Manage channel** → **Edit** → **Connectors**)
   > **Note:** In newer Teams versions, you may need to use **Workflows** instead of Connectors. See the Workflows alternative below.
4. Find **Incoming Webhook** → Click **Configure**
5. Set the webhook details:

   | Setting | Value |
   |---------|-------|
   | **Name** | `GHAzDO Alert Bot` |
   | **Icon** | Upload a security shield icon (optional) |

6. Click **Create**
7. **Copy the webhook URL** — you'll need this for the ADO Service Hook configuration
   > ⚠️ **Save this URL securely.** Anyone with this URL can post to your channel.
8. Click **Done**

### Workflows Alternative (New Teams)

If Connectors are not available (Microsoft is deprecating them in favor of Workflows):

1. Click **"..."** next to the channel name → **Workflows**
2. Select **"Post to a channel when a webhook request is received"**
3. Name the workflow: `GHAzDO Alerts`
4. Select the target channel: **🔒 Security Alerts**
5. Click **Add workflow**
6. Copy the generated **webhook URL**
7. Use this URL in the ADO Service Hook configuration

---

## Step 3: Configure Channel Notifications

Ensure team members are notified of new alerts:

### For the Channel

1. Right-click the **🔒 Security Alerts** channel
2. Select **Channel notifications**
3. Set:
   - **All new posts**: Show in feed (or Banner and feed for high priority)
   - **Channel mentions**: Show in feed

### For Individual Members

Team members should also:
1. Right-click the channel → **Channel notifications**
2. Set to **Banner and feed** if they want desktop notifications for every alert
3. Alternatively, set to **Show in feed** for less intrusive notifications

---

## Step 4: Pin the Channel

Keep the Security Alerts channel visible:

1. Right-click the **🔒 Security Alerts** channel
2. Select **Pin**
3. The channel will now appear at the top of the channel list

---

## Step 5: Set Channel Moderation (Optional)

If you want only bot messages in the channel (no human chatter):

1. Click **"..."** next to the channel name → **Manage channel**
2. Under **Channel settings**, find **Channel moderation**
3. Turn moderation **On**
4. Set **Who can post messages**: Owners (and bots/connectors)
5. Allow **Everyone** to reply to messages (so team members can discuss alerts in threads)

This ensures the channel stays focused on alerts while allowing threaded discussions.

---

## Step 6: Add a Channel Tab (Optional)

Add useful tabs to the Security Alerts channel for quick access:

### ADO Security Dashboard Tab

1. Click the **"+"** (Add a tab) at the top of the channel
2. Select **Azure DevOps**
3. Choose **Dashboard** or **Boards**
4. Link to your project's security-related board or query

### ADO Advanced Security Tab

1. Click **"+"** → **Website**
2. URL: `https://dev.azure.com/{org}/{project}/_git/{repo}/alerts`
3. Tab name: "GHAzDO Alerts Dashboard"

---

## Channel Best Practices

| Practice | Why |
|----------|-----|
| Use a dedicated channel | Keeps alerts separate from general chat |
| Pin the channel | Ensures visibility for all team members |
| Enable banner notifications | Critical/high alerts shouldn't be missed |
| Use channel moderation | Prevents alert messages from being buried |
| Add ADO tab | Quick access to the full alert dashboard |
| Review alerts weekly | Prevents notification fatigue and ensures follow-up |
| Assign a security champion | One person responsible for triage rotation |

---

## Webhook URL Management

### Security Considerations

- Store the webhook URL securely (treat it like an API key)
- Only share with ADO administrators who configure service hooks
- Rotate the webhook URL periodically (delete and recreate)
- Monitor for unexpected posts to the channel

### If the Webhook URL Is Compromised

1. Delete the existing webhook connector
2. Create a new webhook with a new URL
3. Update the ADO Service Hook configurations with the new URL
4. Verify notifications are working with the Test button in ADO

### Monitoring Webhook Health

- Check the ADO Service Hook history: Project Settings → Service hooks → click subscription → History
- Look for failed deliveries (HTTP 4xx/5xx responses)
- Teams will show a system message if a connector is removed or broken
