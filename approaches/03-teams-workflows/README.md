# Approach #3: Teams Workflows (Simplified Power Automate in Teams)

> **Phase 2b** in our phased adoption strategy | Setup: ~30 minutes | Cost: Free with M365 license*

## Overview

**Teams Workflows** are a simplified Power Automate engine built directly into Microsoft Teams. Many teams don't know this feature exists. Instead of opening the Power Automate portal, you create flows right inside Teams — with a guided experience and pre-built templates.

For GHAzDO → ADO work item integration, Teams Workflows can:
- ✅ Receive webhook payloads from ADO Service Hooks
- ✅ Parse GHAzDO security alert data
- ✅ Create ADO work items with correct fields, tags, and priority
- ✅ Handle all 3 alert types (secret scanning, code scanning, dependency)
- ⚠️ Auto-close requires a second workflow (possible but limited)
- ❌ Deduplication via WIQL requires Premium license (HTTP connector)

### What Makes This Different from Power Automate?

| Feature | Teams Workflows | Power Automate |
|---------|----------------|----------------|
| **Access** | Built into Teams app | Separate portal (make.powerautomate.com) |
| **License** | M365 Business Basic+ | Separate license for Premium |
| **Trigger** | "When a Teams webhook request is received" | Full HTTP Request trigger (Premium) |
| **Connectors** | Standard connectors included | Standard + Premium (paid) |
| **ADO Create Work Item** | ✅ Standard connector | ✅ Standard connector |
| **HTTP Actions (WIQL)** | ❌ Premium required | ❌ Premium required |
| **Complexity** | Low — guided templates | Medium — full designer |
| **Export/Version Control** | Limited | Solution packages |

---

## Prerequisites

### Required
- **Microsoft 365 license**: Business Basic, Business Standard, Business Premium, E3, or E5
- **Microsoft Teams**: Desktop or web client
- **Azure DevOps organization** with:
  - GitHub Advanced Security for Azure DevOps (GHAzDO) enabled
  - A project where work items will be created
  - Service Hooks permission (Project Administrator or "Edit subscriptions")
- **ADO Personal Access Token (PAT)** with scope: `Work Items: Read & Write`
  - *Or* use the ADO connector's OAuth sign-in (recommended for Teams Workflows)

### Recommended
- A dedicated Teams channel for security alerts (e.g., `#security-alerts`)
- ADO work item type decided (Issue, Bug, or Task)

---

## Step-by-Step Implementation

### Step 1: Create a New Workflow in Teams

1. Open **Microsoft Teams** (desktop or web)
2. Click the **three-dot menu (⋯)** in the left sidebar (or search bar)
3. Search for **"Workflows"** and open the Workflows app
4. Alternatively: Right-click any **channel** → select **"Workflows"**
5. Click **"+ New flow"** or browse templates

> 💡 **Tip:** You can also access Workflows from any channel by clicking the **⚡ lightning bolt** icon in the message compose area, then selecting "Create a workflow."

### Step 2: Select the Webhook Trigger Template

1. In the Workflows gallery, search for **"webhook"**
2. Select the template: **"When a Teams webhook request is received"**
   - If not visible, click **"Create from blank"** and add this trigger manually
3. Click **"Next"** to configure

> ⚠️ **Important:** This trigger generates a unique webhook URL. This URL is what ADO Service Hooks will send alerts to.

### Step 3: Configure the Workflow

#### 3a. Set Up the Trigger

The "When a Teams webhook request is received" trigger automatically:
- Creates an HTTPS endpoint
- Accepts POST requests with JSON payloads
- Provides the webhook URL after saving

No additional configuration needed for the trigger itself.

#### 3b. Parse the GHAzDO Webhook Payload

1. Click **"+ New step"** → search for **"Parse JSON"** (Data Operation)
2. Set **Content** to: `triggerBody()` (the incoming webhook body)
3. Use the JSON schema from [`implementation/webhook-payload-schema.json`](implementation/webhook-payload-schema.json)
4. Click **"Use sample payload to generate schema"** and paste the sample from the schema file

#### 3c. Add a Compose Action — Determine Alert Type

1. Click **"+ New step"** → search for **"Compose"** (Data Operation)
2. Name it: **"Compose_AlertType"**
3. Set Inputs to expression:
   ```
   coalesce(body('Parse_JSON')?['resource']?['alertType'], 'unknown')
   ```

#### 3d. Add a Compose Action — Build Work Item Title

1. Click **"+ New step"** → search for **"Compose"**
2. Name it: **"Compose_Title"**
3. Set Inputs to expression:
   ```
   if(
     equals(outputs('Compose_AlertType'), 'secret'),
     concat('[GHAzDO-Secret] ', coalesce(body('Parse_JSON')?['resource']?['secretType'], 'Secret detected')),
     if(
       equals(outputs('Compose_AlertType'), 'code'),
       concat('[GHAzDO-CodeScan] ', coalesce(body('Parse_JSON')?['resource']?['title'], 'Code scanning alert')),
       if(
         equals(outputs('Compose_AlertType'), 'dependency'),
         concat('[GHAzDO-Dependency] ', coalesce(body('Parse_JSON')?['resource']?['title'], 'Dependency alert')),
         concat('[GHAzDO-Alert] ', coalesce(body('Parse_JSON')?['resource']?['title'], 'Security alert'))
       )
     )
   )
   ```

#### 3e. Add a Compose Action — Build Tags for Tracking

1. Click **"+ New step"** → search for **"Compose"**
2. Name it: **"Compose_Tags"**
3. Set Inputs to expression:
   ```
   concat(
     'GHAzDO;',
     outputs('Compose_AlertType'), ';',
     coalesce(body('Parse_JSON')?['resource']?['severity'], 'medium'), ';',
     'GHAzDO-',
     coalesce(body('Parse_JSON')?['resource']?['repository']?['name'], 'unknown'),
     '-',
     string(coalesce(body('Parse_JSON')?['resource']?['alertId'], body('Parse_JSON')?['resource']?['id'], 0))
   )
   ```

> 💡 The tag format `GHAzDO-{repo}-{alertId}` enables manual dedup searches even without automated WIQL.

#### 3f. Add a Compose Action — Build Description (HTML)

1. Click **"+ New step"** → search for **"Compose"**
2. Name it: **"Compose_Description"**
3. Set Inputs to expression:
   ```
   concat(
     '<h3>GHAzDO Security Alert</h3>',
     '<table border="1" cellpadding="5">',
     '<tr><td><b>Alert Type</b></td><td>', outputs('Compose_AlertType'), '</td></tr>',
     '<tr><td><b>Severity</b></td><td>', coalesce(body('Parse_JSON')?['resource']?['severity'], 'medium'), '</td></tr>',
     '<tr><td><b>Repository</b></td><td>', coalesce(body('Parse_JSON')?['resource']?['repository']?['name'], 'unknown'), '</td></tr>',
     '<tr><td><b>File</b></td><td>', coalesce(body('Parse_JSON')?['resource']?['location']?['file'], 'N/A'), '</td></tr>',
     '<tr><td><b>Alert ID</b></td><td>', string(coalesce(body('Parse_JSON')?['resource']?['alertId'], 0)), '</td></tr>',
     '</table>',
     '<p><a href="', coalesce(body('Parse_JSON')?['resource']?['link'], ''), '">View Alert in Azure DevOps</a></p>',
     '<hr/><p><i>Auto-created by Teams Workflow Integration</i></p>'
   )
   ```

#### 3g. Create ADO Work Item

1. Click **"+ New step"** → search for **"Azure DevOps"**
2. Select **"Create a work item"** action
3. Configure:
   - **Organization Name**: Your ADO org (e.g., `contoso`)
   - **Project Name**: Your ADO project
   - **Work Item Type**: `Issue` (or `Bug`, `Task`)
   - **Title**: Select `Compose_Title` output from dynamic content
   - Click **"Show advanced options"**:
     - **Description**: Select `Compose_Description` output
     - **Tags**: Select `Compose_Tags` output
     - **Priority**: Use expression:
       ```
       if(
         or(
           equals(coalesce(body('Parse_JSON')?['resource']?['severity'],'medium'), 'critical'),
           equals(coalesce(body('Parse_JSON')?['resource']?['severity'],'medium'), 'high')
         ), 1,
         if(equals(coalesce(body('Parse_JSON')?['resource']?['severity'],'medium'), 'medium'), 2, 3)
       )
       ```

4. Sign in to the ADO connector when prompted (OAuth — no PAT needed!)

> ✅ **Key Advantage:** The ADO connector uses OAuth sign-in, not a PAT. This is more secure and doesn't expire like PATs do.

### Step 4: Save and Copy the Webhook URL

1. Click **"Save"** in the top-right corner
2. The workflow will display the **Webhook URL** — copy this URL
3. It looks like: `https://prod-XX.westus.logic.azure.com:443/workflows/...`

> ⚠️ **Store this URL securely.** Anyone with this URL can trigger the workflow. Treat it like a secret.

### Step 5: Configure ADO Service Hook

1. Go to **Azure DevOps** → Your Project → **Project Settings** (gear icon, bottom-left)
2. Under **General**, click **Service hooks**
3. Click **+ Create subscription**
4. Select **Web Hooks** as the service
5. Configure the trigger:
   - **Event**: `Code scanning alert created` (maps to `advancedsecurity.alert.created`)
   - **Repository**: Select your repository (or `[Any]` for all repos)
   - **Alert severity**: `[Any]` (handle all severities in the workflow)
6. Click **Next**
7. Configure the action:
   - **URL**: Paste the Teams Workflow webhook URL from Step 4
   - **HTTP headers**: Leave empty (Teams Workflows accept the default)
   - **Resource details to send**: `All`
   - **Messages to send**: `All`
8. Click **Test** to verify connectivity
9. Click **Finish** to save

> 📋 See [`implementation/service-hook-config.json`](implementation/service-hook-config.json) for the exact configuration.

### Step 6: (Optional) Auto-Close Workflow

To automatically close work items when alerts are resolved, create a **second workflow**:

1. Repeat Steps 1–2 to create another webhook-triggered workflow
2. Parse the incoming payload (same schema)
3. Check if `eventType` equals `advancedsecurity.alert.statechanged`
4. Check if new state indicates resolution (`fixed`, `dismissed`, `closed`)
5. Use **"Update a work item"** ADO connector action:
   - **Work Item Id**: ⚠️ This is the limitation — you need the ADO work item ID
   - **State**: Set to `Done` or `Closed`

#### The Auto-Close Challenge

The ADO connector's "Update a work item" requires the **work item ID**. To find it by tag, you'd need:
- **Option A:** WIQL query via HTTP connector → **Premium license required** ❌
- **Option B:** Store the work item ID in a SharePoint list or Excel → adds complexity
- **Option C:** Use the "Get work items" connector with a simple query → **Limited filtering**
- **Option D:** Include the work item ID in the service hook state change payload → Not available from GHAzDO

**Recommended approach for auto-close without Premium:**
1. Use the **ADO connector "Get query results"** action with a saved ADO query
2. Pre-create a saved query in ADO: `Tags Contains "GHAzDO-{repo}-{alertId}"`
3. The workflow extracts the tag from the webhook, constructs the query name, and fetches results
4. This is manual to set up per-repo but avoids Premium licensing

> ⚠️ **Honest assessment:** Auto-close is the weakest point of Teams Workflows. If auto-close is critical, consider the Logic App approach (Approach #3 in the main project) which handles this natively.

---

## Testing the End-to-End Flow

### Quick Test via ADO Service Hook

1. Go to **Project Settings → Service hooks** in ADO
2. Find your webhook subscription and click **Test**
3. ADO sends a sample payload to your Teams Workflow
4. Check the workflow run history in Teams (Workflows → Your flow → Run history)
5. Verify a work item was created in ADO Boards

### Manual Test via curl/PowerShell

```powershell
# Replace with your actual webhook URL
$webhookUrl = "https://prod-XX.westus.logic.azure.com:443/workflows/..."

$testPayload = @{
    eventType = "advancedsecurity.alert.created"
    resource = @{
        alertType = "secret"
        alertId = 42
        severity = "high"
        secretType = "GitHub PAT detected"
        repository = @{ name = "my-repo" }
        location = @{ file = "config/secrets.yml"; line = 15 }
        link = "https://dev.azure.com/myorg/myproject/_git/my-repo/alerts/42"
    }
    message = @{ text = "A secret scanning alert was created" }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri $webhookUrl -Method POST -Body $testPayload -ContentType "application/json"
```

### Verify Results

- [ ] Workflow triggered (check run history in Teams)
- [ ] JSON parsed correctly (check Parse JSON output)
- [ ] Work item created in ADO Boards
- [ ] Title has correct prefix: `[GHAzDO-Secret] GitHub PAT detected`
- [ ] Tags include: `GHAzDO;secret;high;GHAzDO-my-repo-42`
- [ ] Priority set to 1 (high severity)
- [ ] Description contains HTML table with alert details

---

## Limitations and Workarounds

| Limitation | Impact | Workaround |
|-----------|--------|-----------|
| **No WIQL without Premium** | Cannot deduplicate work items automatically | Use tag-based convention + manual check, or pre-create saved queries |
| **Auto-close requires work item ID** | Cannot look up work items by tag without HTTP/Premium | Store mapping in SharePoint list, or use saved ADO queries |
| **Webhook URL is a secret** | URL exposure = unauthorized triggers | Rotate by recreating workflow; restrict ADO service hook access |
| **Limited error handling** | No retry policies in Teams Workflows | Failures visible in run history; manual re-run available |
| **No version control** | Workflow definitions not in Git | Export manually; keep workflow-definition.json as reference |
| **Expression editor is basic** | Complex expressions harder to enter in Teams UI | Build expressions in Compose steps, test incrementally |
| **Rate limits** | M365 standard throttling applies | Sufficient for typical GHAzDO alert volumes (<100/day) |

### Licensing Clarification ⚠️

| Capability | License Required | Included in M365? |
|-----------|-----------------|-------------------|
| Teams Workflows (webhook trigger) | M365 Business Basic+ | ✅ Yes |
| ADO "Create a work item" action | Standard connector | ✅ Yes |
| ADO "Update a work item" action | Standard connector | ✅ Yes |
| ADO "Get query results" action | Standard connector | ✅ Yes |
| HTTP action (raw REST calls/WIQL) | Premium connector | ❌ No — requires Power Automate Premium ($15/user/mo) |
| Dataverse connector | Premium connector | ❌ No |

**Bottom line:** Creating work items is free with M365. Deduplication via WIQL and advanced auto-close require Premium. For most teams, the free tier is sufficient — duplicates can be managed manually via tag searches in ADO.

---

## When to Use This Approach

### ✅ Good Fit
- Team already uses Microsoft Teams daily
- M365 license available (Business Basic or higher)
- Want automated work item creation without Azure infrastructure
- Alert volume is moderate (<100/day)
- Manual dedup/close is acceptable or auto-close isn't critical

### ❌ Not Ideal
- Need guaranteed deduplication (use Logic App approach)
- Need full auto-close lifecycle (use Logic App approach)
- Team doesn't use Microsoft Teams
- Require version-controlled infrastructure-as-code
- Enterprise audit/compliance requirements for the integration

---

## File Reference

| File | Description |
|------|-------------|
| [`implementation/webhook-payload-schema.json`](implementation/webhook-payload-schema.json) | GHAzDO webhook payload JSON schema |
| [`implementation/workflow-definition.json`](implementation/workflow-definition.json) | Exportable Teams Workflow definition |
| [`implementation/service-hook-config.json`](implementation/service-hook-config.json) | ADO Service Hook configuration |
| [`implementation/workflow-steps.md`](implementation/workflow-steps.md) | Detailed step-by-step with field values |
| [`validation/test-plan.md`](validation/test-plan.md) | End-to-end test plan |
| [`validation/expected-results.md`](validation/expected-results.md) | Expected test outcomes |
| [`validation/limitations.md`](validation/limitations.md) | Full limitations analysis |
