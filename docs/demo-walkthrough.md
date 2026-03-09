# Learfield Demo Walkthrough: GHAS → ADO Logic App

> **Audience:** Customer demo for Learfield
> **Duration:** ~20 minutes
> **Goal:** Show how GHAS vulnerabilities automatically create/close ADO work items

---

## Pre-Demo Checklist

Before the demo, ensure you have:

- [ ] Azure Portal access ([portal.azure.com](https://portal.azure.com))
- [ ] ADO access ([dev.azure.com/brandsafway1](https://dev.azure.com/brandsafway1/brandsafway_Engg))
- [ ] A GitHub repo with GHAS enabled (code scanning, Dependabot, secret scanning)
- [ ] ADO PAT with **Work Items: Read & Write** scope
- [ ] GitHub PAT with **security_events** scope
- [ ] A webhook secret string (any random string, e.g., `LearfieldDemo2025!`)

---

## Part 1: Show the Problem (2 min)

> **Talking Point:** *"Today, when GHAS finds a vulnerability, someone has to manually go to ADO, create a work item, copy all the details, and link it back. Let me show you what that looks like..."*

### Step 1.1 — Show a GHAS alert in GitHub

1. Open your GitHub repository
2. Click **Security** tab → **Code scanning alerts** (or Dependabot / Secret scanning)
3. Click on any open alert
4. Point out: *"Here's the vulnerability — severity, file, line number, description. Now a developer would have to manually go to ADO and create a work item..."*

### Step 1.2 — Show ADO Boards (empty or unlinked)

1. Open [https://dev.azure.com/brandsafway1/brandsafway_Engg/_boards](https://dev.azure.com/brandsafway1/brandsafway_Engg/_boards)
2. Show that there's no automatic link between GHAS and ADO
3. *"There's no connection. No traceability. Security loses context, developers lose time."*

---

## Part 2: Build the Logic App (12 min)

> **Talking Point:** *"Let me show you how we solve this with an Azure Logic App — zero code, fully automated."*

### Step 2.1 — Create a Resource Group

1. Open **Azure Portal** → [portal.azure.com](https://portal.azure.com)

![Azure Portal Home](screenshots/01-azure-portal-home.png)

2. Search for **"Resource groups"** in the top search bar
3. Click **+ Create**
4. Fill in:

   | Field | Value |
   |---|---|
   | Subscription | *(your subscription)* |
   | Resource group | `rg-ghas-ado-learfield` |
   | Region | `East US` |

5. Click **Review + Create** → **Create**

> 📸 *Screenshot opportunity: Resource group creation form*

### Step 2.2 — Create the Logic App

1. In Azure Portal, search for **"Logic App"** in the top search bar
2. Click **+ Add** (or **Create**)

![Create a Resource - Logic App visible](screenshots/02-create-resource-logic-app.png)

3. Select **Consumption** (pay-per-execution, serverless)

![Select Consumption Plan](screenshots/03-select-consumption-plan.png)

4. Fill in:

   | Field | Value |
   |---|---|
   | Subscription | *(your subscription)* |
   | Resource Group | `rg-ghas-ado-learfield` |
   | Logic App name | `ghas-ado-sync-learfield` |
   | Region | `East US` |
   | Enable log analytics | `No` (for demo) |

![Logic App Basics Form Filled](screenshots/04-logic-app-basics-form.png)

5. Click **Review + Create** → **Create**
6. Wait for deployment to complete (~30 seconds)
7. Click **Go to resource**

> 📸 *Screenshot opportunity: Logic App creation form*

### Step 2.3 — View the Logic App Overview

After deployment, you'll see the Logic App overview page showing key details:

![Logic App Overview - Status: Enabled, 1 trigger, 22 actions](screenshots/05-logic-app-overview.png)

Key information visible:
- **Status**: Enabled
- **Definition**: 1 trigger, 22 actions
- **Workflow URL**: The trigger endpoint (with SAS token)
- **Tags**: `purpose: GHAS-ADO-Sync`, `managedBy: Bicep`

### Step 2.4 — Open the Logic App Designer

1. On the Logic App overview page, click **Logic App Designer** (left sidebar under Development Tools)
2. The designer opens showing the full workflow:

![Full workflow in the Logic App Designer](screenshots/06-designer-full-workflow.png)

> **Talking Point:** *"This is the complete automation. GitHub sends a webhook, we extract the metadata, check if it's a new alert or a fix, and route accordingly."*

### Step 2.5 — Configure the HTTP Trigger

1. Click on the **"When a GHAS webhook is received"** trigger block
2. The trigger configuration panel opens showing:
   - The **HTTP POST URL** (auto-generated with SAS token)
   - **Method**: Default (Allow All Methods)
   - **Request Body JSON Schema**: `{}` (accepts any payload)

![HTTP Request Trigger Configuration](screenshots/10-trigger-http-request.png)

> **Talking Point:** *"GitHub sends different payload formats for code scanning, Dependabot, and secret scanning alerts. We leave the schema open and normalize everything in the workflow."*

### Step 2.6 — Metadata Extraction Actions

The workflow includes Compose actions that extract and normalize metadata from all 3 GHAS alert types:

- **Compose EventType** — Reads `X-GitHub-Event` header (code_scanning_alert / dependabot_alert / secret_scanning_alert)
- **Compose AlertNumber** — Alert number for deduplication
- **Compose RepoFullName** — Repository owner/name
- **Compose Title** — Normalized title with alert type prefix
- **Compose Severity** — Normalized severity across all alert types
- **Compose FilePath / LineNumber / Branch** — Code location (when available)
- **Compose GhasTag** — Unique tag for deduplication (e.g., `GHAS-owner-repo-42`)
- **Compose Description** — Rich HTML description with all metadata in a table
- **Compose Tags** — Combined tags string

### Step 2.7 — Condition: Create vs Close

The main **Condition IsCreateAction** branches on the webhook `action` field:

![Condition expanded showing True (create) and False (close) branches](screenshots/07-designer-condition-expanded.png)

- **True** (action = "created") → Check for duplicates → Create work item
- **False** (action = "fixed"/"resolved") → Find existing work item → Close it

### Step 2.8 — True Branch: Create the ADO Work Item

Inside the **True** branch, the workflow:
1. Runs a **WIQL query** to check for existing work items with the same GHAS tag
2. If no duplicate exists, creates a new work item via ADO REST API

![True branch showing HTTP QueryExistingWorkItem and nested Condition](screenshots/08-designer-true-branch-create.png)

The HTTP action uses the ADO WIQL API to search for duplicates:

![HTTP QueryExistingWorkItem action configuration](screenshots/11-http-query-existing-workitem.png)

> **Talking Point:** *"Before creating a work item, we check if one already exists using the unique GHAS tag. This prevents duplicates if the webhook fires twice."*

### Step 2.9 — False Branch: Auto-Close Work Items

When GHAS marks a vulnerability as fixed or resolved, the **False** branch:
1. Runs a nested **Condition IsCloseAction** (checks for "fixed" or "resolved")
2. Queries ADO for the matching open work item by GHAS tag
3. PATCHes the work item state to "Closed" with a comment

![Both branches visible - True (create) and False (close with Condition IsCloseAction)](screenshots/09-designer-both-branches.png)

> **Talking Point:** *"This is the 'huge value' feature — when the vulnerability is fixed in GitHub, the ADO work item automatically closes. Full lifecycle, zero manual work."*

### Step 2.10 — Code View

You can also view the entire workflow as JSON in the code view:

![Logic App Code View showing the full JSON definition](screenshots/12-logic-app-code-view.png)

### Step 2.11 — Save and Get the Webhook URL

1. Click **Save** (top toolbar)
2. Click on the **"When a GHAS webhook is received"** trigger block
3. The **HTTP POST URL** field shows your webhook URL
4. Click the **📋 copy** icon to copy it

> *"This URL is what we give to GitHub. It includes a security token so only authorized callers can trigger it."*

---

## Part 3: Connect GitHub to the Logic App (3 min)

### Step 3.1 — Create the GitHub Webhook

1. Open your GitHub repository → **Settings** → **Webhooks**
2. Click **Add webhook**
3. Fill in:

   | Field | Value |
   |---|---|
   | Payload URL | *(paste the Logic App trigger URL)* |
   | Content type | `application/json` |
   | Secret | `LearfieldDemo2025!` |
   | SSL verification | ✅ Enable |

4. Under **Which events would you like to trigger this webhook?**:
   - Select **"Let me select individual events"**
   - ✅ Check **Code scanning alerts**
   - ✅ Check **Dependabot alerts**
   - ✅ Check **Secret scanning alerts**
   - Uncheck everything else

5. Ensure **Active** is checked
6. Click **Add webhook**

> 📸 *Screenshot opportunity: GitHub webhook configuration with the 3 events selected*

> **Talking Point:** *"Now GitHub will automatically POST to our Logic App whenever a new vulnerability is detected — code scanning, Dependabot, or secret scanning."*

---

## Part 4: Live Demo — Trigger a Vulnerability (3 min)

> **Talking Point:** *"Let me show you this working end-to-end, live."*

### Step 4.1 — Trigger a Code Scanning Alert

**Option A — Commit a vulnerable code pattern:**

1. In your repo, create or edit a file (e.g., `test-vuln.py`):
   ```python
   import subprocess
   user_input = input("Enter command: ")
   subprocess.call(user_input, shell=True)  # Command injection
   ```
2. Commit and push to a branch scanned by CodeQL

**Option B — Use a pre-existing open alert:**

1. If the repo already has open GHAS alerts, dismiss and reopen one to trigger the webhook

### Step 4.2 — Show the Logic App Run

1. Go to Azure Portal → your Logic App → **Runs history** (left sidebar under "Overview")
2. Click on the most recent run (should show **Succeeded** ✅)
3. Click through each action to show:
   - The webhook payload received from GitHub
   - The WIQL deduplication check (empty result → new alert)
   - The work item creation response (with the new work item ID)

> 📸 *Screenshot opportunity: Logic App run history showing successful execution*
> 📸 *Screenshot opportunity: Expanded "Create Work Item" action showing inputs/outputs*

### Step 4.3 — Show the Created Work Item in ADO

1. Open [https://dev.azure.com/brandsafway1/brandsafway_Engg/_workitems](https://dev.azure.com/brandsafway1/brandsafway_Engg/_workitems)
2. The new work item should appear with:
   - **Title** prefixed with `[GHAS]`
   - **Tags:** `GHAS`, `Security`, unique tracking tag
   - **Description:** HTML table with severity, repo, file, line, link
   - **Hyperlink:** Click to jump directly to the GHAS alert

> **Talking Point:** *"And there it is. The work item was created automatically — title, description, severity, file and line number, and a direct hyperlink back to the vulnerability. Zero manual work. Full traceability."*

> 📸 *Screenshot opportunity: ADO work item with GHAS metadata*
> 📸 *Screenshot opportunity: Click the hyperlink to show it links back to GHAS*

---

## Part 5: Show Auto-Close (Optional, 2 min)

> **Talking Point:** *"And when the developer fixes the vulnerability and GHAS marks it as resolved — the work item automatically closes."*

### Step 5.1 — Fix the Vulnerability

1. Fix the vulnerable code (remove the `subprocess.call` line)
2. Commit and push
3. Wait for CodeQL to rescan (~2-5 minutes)

### Step 5.2 — Show the Closed Work Item

1. The GHAS alert will show as **Fixed**
2. The webhook fires again with action `fixed`
3. The Logic App finds the work item by tag and closes it
4. Show the work item in ADO — state is now **Closed** with a history comment:
   > *"Auto-closed by GHAS-ADO Sync: Vulnerability marked as fixed in GitHub Advanced Security."*

> 📸 *Screenshot opportunity: ADO work item in Closed state with auto-close comment*

---

## Demo Script — Key Talking Points

| Moment | Say This |
|---|---|
| **Opening** | *"What if every GHAS vulnerability automatically became a tracked work item in ADO?"* |
| **Problem** | *"Today it's manual — context switching, copy-paste, lost details, no traceability."* |
| **Logic App creation** | *"Zero code. We use Azure Logic App as the glue between GitHub and ADO."* |
| **Field mapping** | *"Title, severity, file, line number, branch — all auto-populated from the GHAS API."* |
| **Deduplication** | *"We tag every work item with a unique ID. No duplicates, ever."* |
| **Hyperlink** | *"One click from the work item takes you straight to the vulnerability in GitHub."* |
| **Live trigger** | *"Let me show you this happening in real-time..."* |
| **Auto-close** | *"When the dev fixes it, the work item closes automatically. Full lifecycle."* |
| **Closing** | *"Security stays in the loop, developers stay in their flow, and everything is traceable."* |

---

## Appendix: Generating the Base64 Auth Header

For the ADO `Authorization` header, you need `Basic base64(:pat)`:

```powershell
$pat = "your-ado-pat-here"
$base64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$pat"))
Write-Host "Basic $base64"
```

Use the output as the `Authorization` header value in the Logic App HTTP actions.

---

## Appendix: Pre-Built Alternative

If you prefer to deploy the complete Logic App via script instead of building it manually in the designer:

```powershell
cd C:\Users\sautalwar\Downloads\repos\Logic_app_ADO_learfield
$pat = Read-Host -AsSecureString "ADO PAT"
$ghPat = Read-Host -AsSecureString "GitHub PAT"
$secret = Read-Host -AsSecureString "Webhook Secret"

.\scripts\deploy.ps1 `
    -ResourceGroupName "rg-ghas-ado-learfield" `
    -Location "eastus" `
    -AdoOrganization "brandsafway1" `
    -AdoProject "brandsafway_Engg" `
    -AdoPat $pat -GitHubPat $ghPat -WebhookSecret $secret
```

This deploys the full Logic App (all 3 alert types, deduplication, auto-close) in one command. You can then open the Logic App Designer in the portal to walk through the workflow visually.
