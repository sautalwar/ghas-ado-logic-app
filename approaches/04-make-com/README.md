# Approach #4 — Make.com (Free Tier)

> **Zero cost, zero infrastructure, full automation** — GHAzDO security alerts → ADO work items in 45 minutes.

## Overview

| Dimension | Value |
|-----------|-------|
| **Platform** | [Make.com](https://www.make.com/) (formerly Integromat) |
| **Cost** | **FREE** (1,000 operations/month) |
| **Infrastructure** | None — SaaS, sign up like Slack or Jira |
| **Setup Time** | ~45 minutes |
| **Automation Level** | Full (auto-create + auto-close) |
| **Dedup Support** | Partial (requires HTTP module for WIQL query) |

## How It Works

```
ADO Service Hook → Make.com Webhook → Parse JSON → Router
                                                      ├── Alert Created  → WIQL Dedup Check → Create Work Item
                                                      └── State Changed  → WIQL Find Item   → Close Work Item
```

---

## Prerequisites

- [ ] **Make.com account** — [Sign up free](https://www.make.com/en/register) (no credit card required)
- [ ] **Azure DevOps project** with GHAzDO (GitHub Advanced Security for Azure DevOps) enabled
- [ ] **ADO Personal Access Token (PAT)** with scopes:
  - `Work Items: Read & Write`
  - `Project and Team: Read`
- [ ] **ADO Organization URL** — e.g., `https://dev.azure.com/your-org`
- [ ] **ADO Project name** — the project where work items should be created

---

## Step-by-Step Implementation

### Step 1: Sign Up for Make.com

1. Go to [make.com/en/register](https://www.make.com/en/register)
2. Sign up with email or Google/GitHub SSO
3. Verify email address
4. You're on the **Free plan** automatically:
   - **1,000 operations/month**
   - **2 active scenarios**
   - **15-minute minimum interval** (irrelevant — we use webhooks for instant triggers)
   - **100 MB data transfer/month**

> **💡 Tip:** Each GHAzDO alert cycle uses ~4-6 operations (webhook receive + parse + router + HTTP calls). That gives you **~165-250 alerts/month** on the free tier.

### Step 2: Create a New Scenario

1. Click **"Create a new scenario"** on the Make.com dashboard
2. You'll see an empty canvas with a large `+` button

### Step 3: Add Webhook Trigger Module

1. Click the `+` button on the canvas
2. Search for **"Webhooks"** → select **"Custom webhook"**
3. Click **"Add"** next to the webhook dropdown
4. Name it: `GHAzDO Alert Receiver`
5. Click **"Save"**
6. **Copy the webhook URL** — it looks like:
   ```
   https://hook.us1.make.com/abc123xyz...
   ```
7. **Save this URL** — you'll paste it into ADO Service Hooks in Step 8

> ⚠️ **Important:** The webhook URL is unique and secret. Treat it like an API key.

### Step 4: Add JSON Parser Module

After the webhook trigger, the raw payload needs to be parsed into structured fields.

1. Click the `+` after the webhook module
2. Search for **"JSON"** → select **"Parse JSON"**
3. For **"JSON string"**, map it to the webhook's `body` output (the full incoming payload)
4. For **"Data structure"**, click **"Add"** → **"Generator"**
5. Paste the sample GHAzDO payload from `implementation/webhook-payload-schema.json`
6. Click **"Generate"** — Make.com will auto-create the field mapping
7. Click **"Save"**

The parser will now output structured fields:
- `eventType` — `advancedsecurity.alert.created` or `advancedsecurity.alert.stateChanged`
- `resource.alertType` — `secret`, `code`, or `dependency`
- `resource.alertId` — unique alert identifier
- `resource.repository.name` — repository name
- `resource.severity` — `critical`, `high`, `medium`, `low`
- `resource.location.file` — file path (if applicable)

### Step 5: Add Router Module (Branch on Event Type)

1. Click the `+` after the JSON parser
2. Search for **"Flow Control"** → select **"Router"**
3. The router creates two branches automatically — we'll configure each:

**Branch 1 — Alert Created:**
1. Click the wrench icon on the first branch line
2. Set label: `Alert Created`
3. Add filter condition:
   - Field: `eventType` (from JSON parser)
   - Operator: `Text operators: Contains`
   - Value: `created`

**Branch 2 — Alert State Changed:**
1. Click the wrench icon on the second branch line
2. Set label: `State Changed`
3. Add filter condition:
   - Field: `eventType` (from JSON parser)
   - Operator: `Text operators: Contains`
   - Value: `stateChanged`

### Step 6: Branch 1 — Create Work Item (with Dedup)

> **Architecture note:** Make.com's built-in Azure DevOps module supports creating and updating work items, but does NOT support WIQL queries natively. We use an HTTP module for WIQL dedup, then the ADO module for creation.

#### 6a. Add HTTP Module — WIQL Dedup Check

1. On Branch 1, click `+` → search **"HTTP"** → select **"Make a request"**
2. Configure:
   - **URL:** `https://dev.azure.com/{{YOUR_ORG}}/{{YOUR_PROJECT}}/_apis/wit/wiql?api-version=7.1`
   - **Method:** `POST`
   - **Headers:**
     | Key | Value |
     |-----|-------|
     | `Content-Type` | `application/json` |
     | `Authorization` | `Basic {{base64(":" + YOUR_PAT)}}` |
   - **Body type:** `Raw`
   - **Content type:** `JSON (application/json)`
   - **Request content:**
     ```json
     {
       "query": "SELECT [System.Id] FROM WorkItems WHERE [System.Tags] CONTAINS 'GHAzDO-{{resource.repository.name}}-{{resource.alertId}}' AND [System.State] <> 'Removed'"
     }
     ```
3. Click **"Save"**

> **💡 PAT encoding:** In Make.com, use the `base64()` function: `base64(":" + your_pat_value)`. Configure the PAT as a scenario variable (gear icon → Variables) for security.

#### 6b. Add Filter — Only Proceed If No Existing Work Item

1. Click the line between the HTTP module and the next module
2. Add a **filter**:
   - Label: `No Duplicate Found`
   - Condition: `length(HTTP_response.body.workItems)` **equals** `0`
   
   Alternatively, use Make.com's expression:
   - Field: `{{length(HTTP_response.body.workItems)}}`
   - Operator: `Equal to`
   - Value: `0`

#### 6c. Add Azure DevOps Module — Create Work Item

1. Click `+` → search **"Azure DevOps"** → select **"Create a Work Item"**
2. **First time:** Click **"Add"** to create an ADO connection:
   - Connection name: `ADO - GHAzDO Integration`
   - Authentication: **Personal Access Token**
   - Organization: `your-org` (just the org name, not full URL)
   - PAT: paste your token
   - Click **"Save"**
3. Configure the module:
   - **Organization:** Select yours from dropdown
   - **Project:** Select your project
   - **Work Item Type:** `Issue` (or `Bug`, `Task`)
   - **Title:** Use this expression to add the alert-type prefix:
     ```
     {{if(resource.alertType = "secret"; "[GHAzDO-Secret] "; if(resource.alertType = "code"; "[GHAzDO-CodeScan] "; if(resource.alertType = "dependency"; "[GHAzDO-Dependency] "; "[GHAzDO-Alert] ")))}}{{resource.title}}
     ```
   - **Description:** (HTML)
     ```html
     <h3>GHAzDO Security Alert</h3>
     <table border="1" cellpadding="5">
     <tr><td><b>Alert Type</b></td><td>{{resource.alertType}}</td></tr>
     <tr><td><b>Severity</b></td><td>{{resource.severity}}</td></tr>
     <tr><td><b>Repository</b></td><td>{{resource.repository.name}}</td></tr>
     <tr><td><b>File</b></td><td>{{resource.location.file}}</td></tr>
     <tr><td><b>Alert ID</b></td><td>{{resource.alertId}}</td></tr>
     </table>
     <p><a href="{{resource.link}}">View Alert in Azure DevOps</a></p>
     <hr/><p><i>Auto-created by Make.com GHAzDO Integration</i></p>
     ```
   - **Tags:** `GHAzDO;{{resource.alertType}};{{resource.severity}};GHAzDO-{{resource.repository.name}}-{{resource.alertId}}`
   - **Priority:** Use expression:
     ```
     {{if(or(resource.severity = "critical"; resource.severity = "high"); 1; if(resource.severity = "medium"; 2; 3))}}
     ```

### Step 7: Branch 2 — Close Work Item

#### 7a. Add HTTP Module — Find Work Item to Close

1. On Branch 2, click `+` → search **"HTTP"** → select **"Make a request"**
2. Configure identically to Step 6a, but with this WIQL query:
   ```json
   {
     "query": "SELECT [System.Id] FROM WorkItems WHERE [System.Tags] CONTAINS 'GHAzDO-{{resource.repository.name}}-{{resource.alertId}}' AND [System.State] <> 'Done' AND [System.State] <> 'Removed'"
   }
   ```

#### 7b. Add Filter — Only Proceed If Work Item Found

1. Add filter on the connection line:
   - Label: `Work Item Found`
   - Condition: `length(HTTP_response.body.workItems)` **greater than** `0`

#### 7c. Add Azure DevOps Module — Update Work Item

1. Click `+` → search **"Azure DevOps"** → select **"Update a Work Item"**
2. Configure:
   - **Connection:** Use the same ADO connection from Step 6c
   - **Work Item ID:** `{{HTTP_response.body.workItems[0].id}}`
   - **State:** `Done` (or `Closed` depending on your process template)
   - **History/Comment:** `Auto-closed: GHAzDO alert resolved/fixed.`

### Step 8: Configure ADO Service Hook

Now connect Azure DevOps to send events to your Make.com webhook.

1. Go to **ADO → Project Settings → Service hooks**
2. Click **"+ Create subscription"**

**Service Hook #1 — Alert Created:**
1. Select service: **Web Hooks**
2. Trigger: **Advanced Security alert created** (`advancedsecurity.alert.created`)
3. Filters: Leave as default (all repositories, all alert types) or filter to specific repos
4. Action: **Perform a POST request**
   - URL: paste your Make.com webhook URL from Step 3
   - HTTP headers: (leave empty)
   - Resource details to send: `All`
   - Messages to send: `All`
5. Click **"Test"** → verify 200 response
6. Click **"Finish"**

**Service Hook #2 — Alert State Changed:**
1. Repeat steps 1-6 with trigger: **Advanced Security alert state changed** (`advancedsecurity.alert.stateChanged`)
2. Use the **same webhook URL**

### Step 9: Test End-to-End

1. In Make.com, click **"Run once"** (bottom-left of scenario editor)
2. In ADO, trigger a test:
   - **Secret scanning:** Commit a known test secret (e.g., a fake AWS key pattern)
   - **Or** use the Service Hook's built-in **"Test"** button to send a sample event
3. Watch Make.com process the event:
   - Webhook receives payload ✅
   - JSON parser extracts fields ✅
   - Router routes to correct branch ✅
   - WIQL check finds no duplicates ✅
   - Work item created in ADO ✅
4. Verify the work item in ADO:
   - Title has correct prefix: `[GHAzDO-Secret] ...`
   - Description has HTML table
   - Tags include `GHAzDO-{repo}-{alertId}`
   - Priority is set correctly

### Step 10: Activate and Schedule

1. Toggle the scenario switch to **ON** (bottom-left)
2. Set scheduling:
   - For webhooks, choose **"Immediately"** — the scenario runs instantly when a webhook fires
   - This does NOT use the 15-minute interval limit
3. Click **"Save"**

Your scenario is now live! 🎉

---

## Free Tier Limits & Planning

| Resource | Free Tier Limit | Per Alert (Create) | Per Alert (Close) |
|----------|----------------|-------------------|-------------------|
| Operations | 1,000/month | ~4 ops | ~3 ops |
| Scenarios | 2 active | Uses 1 | Same scenario |
| Data transfer | 100 MB/month | ~2 KB | ~1 KB |
| Execution time | 5 min/execution | <5 sec | <5 sec |

### Operations Breakdown

**Alert Created cycle (4 operations):**
1. Webhook receive (1 op)
2. JSON parse (1 op)
3. HTTP — WIQL dedup check (1 op)
4. ADO — Create work item (1 op)

**Alert State Changed cycle (3-4 operations):**
1. Webhook receive (1 op)
2. JSON parse (1 op)
3. HTTP — WIQL find item (1 op)
4. ADO — Update work item (1 op) — only if found

**Monthly capacity on free tier:**
- ~140 full alert cycles (create + close = 7-8 ops per full cycle)
- ~250 create-only events (4 ops each)
- Sufficient for most development teams (< 140 unique security alerts/month)

### What Happens When You Exceed the Limit?

- Scenario **pauses** — no data loss, events queue up
- You receive an email notification
- Options:
  1. Wait until next month (limit resets on billing date)
  2. Upgrade to **Core plan** ($9/month, 10,000 ops/month)
  3. Optimize by removing JSON parse step (save 1 op per event)

---

## Troubleshooting

### Webhook not receiving events
- Verify the webhook URL in ADO Service Hook matches exactly
- Check ADO Service Hook test — should return HTTP 200
- In Make.com, check scenario execution history for errors

### Work item not created
- Check ADO PAT has `Work Items: Read & Write` scope
- Verify PAT hasn't expired
- Check the Organization and Project names are correct
- Look at Make.com execution log — expand each module for input/output

### Duplicate work items
- Ensure the WIQL dedup step is correctly checking tags
- Verify tag format: `GHAzDO-{repoName}-{alertId}`
- Check the filter between WIQL and Create modules

### Auto-close not working
- Verify the state name matches your process template (`Done` vs `Closed` vs `Resolved`)
- Check that the WIQL query excludes already-closed items
- Ensure the work item ID extraction from WIQL response is correct

### Router not branching correctly
- Check filter conditions use `Contains` not `Equals`
- Event type strings: `advancedsecurity.alert.created`, `advancedsecurity.alert.stateChanged`

---

## Architecture Decision: Why HTTP Module for WIQL?

Make.com's built-in Azure DevOps module provides:
- ✅ Create a Work Item
- ✅ Update a Work Item (by ID)
- ✅ Get a Work Item (by ID)
- ✅ List Work Items (basic)
- ❌ **WIQL Query** (not supported natively)
- ❌ **Search by Tag** (not supported natively)

For dedup and auto-close, we need to find work items by tag. The ADO module's "List Work Items" doesn't support tag filtering. Therefore, we use the generic **HTTP module** with the ADO REST API's WIQL endpoint. This costs 1 extra operation per event but enables reliable dedup.

---

## Comparison with Other Approaches

| Feature | Make.com (Free) | Logic App | Power Automate | Native ADO |
|---------|----------------|-----------|---------------|------------|
| Cost | **$0** | $50-100/mo | $15-100/mo | $0 |
| Setup | 45 min | 5 min* | 45-90 min | 0 min |
| Auto-create | ✅ | ✅ | ✅ | ❌ |
| Auto-close | ✅ | ✅ | ✅ | ❌ |
| Dedup | ✅ (via HTTP) | ✅ (native) | ✅ (via HTTP) | N/A |
| Infrastructure | None (SaaS) | Azure | M365/Power Platform | None |
| Maintenance | None | None | Low | None |
| Scale limit | 1K ops/mo free | Unlimited** | Per-license | N/A |

*With one-click deploy button  
**Pay-per-execution

---

## Files in This Approach

```
approaches/04-make-com/
├── README.md                              ← You are here
├── implementation/
│   ├── scenario-blueprint.json            ← Make.com scenario export format
│   ├── webhook-payload-schema.json        ← GHAzDO event payload schema
│   ├── service-hook-config.json           ← ADO Service Hook setup
│   ├── ado-connection-setup.md            ← ADO connection guide for Make.com
│   └── scenario-design.md                 ← Visual flow description
├── validation/
│   ├── test-plan.md                       ← 8 validation tests
│   ├── expected-results.md                ← Expected outcomes
│   └── limitations.md                     ← Free tier limits & gaps
└── Make_Com_Implementation.pdf            ← Complete PDF report
```
