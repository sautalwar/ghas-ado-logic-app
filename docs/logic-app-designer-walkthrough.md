# GHAS → ADO Logic App: Step-by-Step Designer Walkthrough

> **This guide walks through every action visible in the Logic App Designer — exactly how each was built, what expression goes where, and why.**

---

## Overview: What the Designer Shows

Looking at the full designer view, the workflow has **4 layers**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                  When a GHAS webhook is received                    │  ← TRIGGER
├─────────────────────────────────────────────────────────────────────┤
│  Compose EventType │ Compose AlertNumber │ Compose RepoFullName │   │
│  Compose AlertUrl  │ Compose Action                                │  ← LAYER 1 (parallel)
├─────────────────────────────────────────────────────────────────────┤
│  Compose Title │ Compose Severity │ Compose FilePath │              │
│  Compose LineNumber │ Compose Branch │ Compose DetailText │        │
│  Compose GhasTag                                                    │  ← LAYER 2
├─────────────────────────────────────────────────────────────────────┤
│  Compose Tags │ Compose Description                                 │  ← LAYER 3
├─────────────────────────────────────────────────────────────────────┤
│  Condition: IsCreateAction                                          │
│    TRUE  → Query Existing → Create Work Item (if no dupe)          │
│    FALSE → Find Work Item → Close Work Item (if found)             │  ← LAYER 4
└─────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 1: Create the Logic App Resource

### Step 1.1 — Open Azure Portal

Navigate to [portal.azure.com](https://portal.azure.com).

📸 **Screenshot: `screenshots/01-azure-portal-home.png`**

![Azure Portal Home](screenshots/01-azure-portal-home.png)

Click **"Create a resource"** (the **+** icon in Azure services).

---

### Step 1.2 — Select Logic App

On the "Create a resource" page, find **Logic App** in the Popular Azure services list and click **Create**.

📸 **Screenshot: `screenshots/02-create-resource-logic-app.png`**

![Create Resource - Logic App](screenshots/02-create-resource-logic-app.png)

---

### Step 1.3 — Select Consumption (Multi-tenant)

On the hosting plan page:
- Select **Consumption → Multi-tenant** (the first option)
- This gives you: Shared compute, Public cloud networking, **Pay-per-operation** pricing
- Click **Select**

📸 **Screenshot: `screenshots/03-select-consumption-plan.png`**

![Select Consumption Plan](screenshots/03-select-consumption-plan.png)

> **Why Consumption?** For a webhook-triggered workflow, you only pay when GitHub actually sends an alert (~$0.000025 per action). No idle costs.

---

### Step 1.4 — Fill in the Basics Form

Fill in the creation form with these values:

| Field | Value |
|---|---|
| **Subscription** | *(your subscription)* |
| **Resource Group** | `(New) ghas-ado-sync-learfield_group` or select existing |
| **Logic App name** | `ghas-ado-sync-learfield` |
| **Region** | `East US` (or your preferred region) |
| **Enable log analytics** | `No` |
| **Workflow Type** | `Stateful` |

📸 **Screenshot: `screenshots/04-logic-app-basics-form.png`**

![Logic App Basics Form](screenshots/04-logic-app-basics-form.png)

Click **Review + create** → **Create** → Wait for deployment → **Go to resource**

---

### Step 1.5 — Logic App Overview (Deployed)

After deployment, you'll see the Logic App Overview page showing:
- **Resource group**: `rg-ghas-ado-learfield`
- **Location**: East US
- **Status**: Enabled
- **Definition**: 1 trigger, 22 actions (after all steps are complete)

📸 **Screenshot: `screenshots/05-logic-app-overview.png`**

![Logic App Overview](screenshots/05-logic-app-overview.png)

---

## PHASE 2: Open the Designer & Set Up Parameters

### Step 2.1 — Open Logic App Designer

In the left sidebar, expand **Development Tools** → click **Logic app designer**.

---

### Step 2.2 — Create Parameters

Click the **Parameters** button in the top toolbar. Add these 6 parameters:

| Name | Type | Default Value | Purpose |
|---|---|---|---|
| `adoOrganization` | String | *(your ADO org, e.g. `brandsafway1`)* | ADO org URL segment |
| `adoProject` | String | *(your project, e.g. `brandsafway_Engg`)* | ADO project name |
| `adoPat` | String | *(your ADO PAT)* | Auth for ADO REST API |
| `githubPat` | String | *(your GitHub PAT)* | Auth for GitHub API |
| `webhookSecret` | String | *(any secret string)* | Webhook verification |
| `workItemType` | String | `Issue` | ADO work item type to create |

Click **Save** after adding all parameters.

---

## PHASE 3: Add the Trigger

### Step 3.1 — Add HTTP Request Trigger

This is the green box at the very top of the designer: **"When a GHAS webhook is received"**

**How to create it:**
1. In the designer, click **"Add a trigger"**
2. Search for **"HTTP request"**
3. Select **"When an HTTP request is received"** (under Request category)
4. Configure:
   - **Method**: `Default (Allow All Methods)`
   - **Request Body JSON Schema**: `{}` (empty — we handle all 3 GHAS payload formats ourselves)
5. Click the **⋯** menu → **Rename** → type: `When a GHAS webhook is received`
6. Click **Save** — Azure generates your unique webhook URL

📸 **Screenshot: `screenshots/10-trigger-http-request.png`**

![HTTP Trigger Configuration](screenshots/10-trigger-http-request.png)

**What you see in the screenshot:**
- **HTTP URL**: `https://prod-04.eastus.logic.azure.com:443/workflows/...` — this is the webhook URL you'll give to GitHub
- **Method**: Default (Allow All Methods)
- **Request Body JSON Schema**: `{}` — empty because GitHub sends 3 different payload formats (code scanning, Dependabot, secret scanning)

> ⚠️ The info banner says "Changing the trigger name updates the callback URL when you save the workflow." — this is why we rename it first, then save.

---

## PHASE 4: Add Compose Actions — Layer 1 (Parallel)

These 5 actions run **in parallel** immediately after the trigger fires. They extract raw data from the webhook payload.

In the designer, these appear as the first row of purple Compose boxes below the trigger.

**How to add each one:**
1. Click the **+** below the trigger → **Add an action**
2. Search **"Compose"** → select **Compose** (Data Operations)
3. Enter the expression in the **Inputs** field
4. Click **⋯** → **Rename** to the name shown below

---

### 4a. Compose EventType

| Setting | Value |
|---|---|
| **Name** | `Compose EventType` |
| **Inputs** | `@triggerOutputs()?['headers']?['X-GitHub-Event']` |
| **Runs After** | *(trigger — no dependency)* |

**What it does:** Reads the `X-GitHub-Event` HTTP header from the webhook. This tells us which type of alert: `code_scanning_alert`, `dependabot_alert`, or `secret_scanning_alert`.

---

### 4b. Compose AlertNumber

| Setting | Value |
|---|---|
| **Name** | `Compose AlertNumber` |
| **Inputs** | `@triggerBody()?['alert']?['number']` |
| **Runs After** | *(trigger — no dependency)* |

**What it does:** Extracts the alert number from the webhook body (e.g., alert #42).

---

### 4c. Compose RepoFullName

| Setting | Value |
|---|---|
| **Name** | `Compose RepoFullName` |
| **Inputs** | `@triggerBody()?['repository']?['full_name']` |
| **Runs After** | *(trigger — no dependency)* |

**What it does:** Gets the full repository name (e.g., `learfield-corp/fan-portal`).

---

### 4d. Compose AlertUrl

| Setting | Value |
|---|---|
| **Name** | `Compose AlertUrl` |
| **Inputs** | `@coalesce(triggerBody()?['alert']?['html_url'], '')` |
| **Runs After** | *(trigger — no dependency)* |

**What it does:** Gets the URL to the alert in GitHub (used for the hyperlink in the ADO work item). Uses `coalesce` to default to empty string if missing.

---

### 4e. Compose Action

| Setting | Value |
|---|---|
| **Name** | `Compose Action` |
| **Inputs** | `@triggerBody()?['action']` |
| **Runs After** | *(trigger — no dependency)* |

**What it does:** Gets the webhook action — either `created` (new vulnerability found), `fixed`, or `resolved` (vulnerability remediated). This determines whether we CREATE or CLOSE a work item.

---

## PHASE 5: Add Compose Actions — Layer 2 (Depend on EventType)

These actions depend on **Compose EventType** (and sometimes others) because they use conditional logic (`if/equals`) to normalize data differently based on the alert type.

In the designer, these appear as the second row of purple boxes.

---

### 5a. Compose Title

| Setting | Value |
|---|---|
| **Name** | `Compose Title` |
| **Runs After** | `Compose EventType` |
| **Inputs** | *(see expression below)* |

**Expression (paste into Inputs):**
```
@if(equals(outputs('Compose_EventType'), 'code_scanning_alert'),
  concat('[GHAS-CodeScan] ', coalesce(triggerBody()?['alert']?['rule']?['description'], 'Code scanning alert')),
  if(equals(outputs('Compose_EventType'), 'dependabot_alert'),
    concat('[GHAS-Dependabot] ', coalesce(triggerBody()?['alert']?['security_advisory']?['summary'], 'Dependabot alert')),
    concat('[GHAS-Secret] ', coalesce(triggerBody()?['alert']?['secret_type_display_name'], 'Secret scanning alert'))
  )
)
```

**What it does:** Creates a prefixed title like:
- `[GHAS-CodeScan] SQL Injection vulnerability`
- `[GHAS-Dependabot] Prototype Pollution in lodash`
- `[GHAS-Secret] Azure Storage Account Key`

---

### 5b. Compose Severity

| Setting | Value |
|---|---|
| **Name** | `Compose Severity` |
| **Runs After** | `Compose EventType` |
| **Inputs** | *(see expression below)* |

**Expression:**
```
@toLower(
  if(equals(outputs('Compose_EventType'), 'code_scanning_alert'),
    coalesce(triggerBody()?['alert']?['rule']?['security_severity_level'], 'medium'),
    if(equals(outputs('Compose_EventType'), 'dependabot_alert'),
      coalesce(triggerBody()?['alert']?['security_vulnerability']?['severity'], 'medium'),
      'critical'
    )
  )
)
```

**What it does:** Normalizes severity to lowercase. Secret scanning alerts are always `critical`.

---

### 5c. Compose FilePath

| Setting | Value |
|---|---|
| **Name** | `Compose FilePath` |
| **Runs After** | `Compose EventType` |
| **Inputs** | *(see expression below)* |

**Expression:**
```
@if(equals(outputs('Compose_EventType'), 'code_scanning_alert'),
  coalesce(triggerBody()?['alert']?['most_recent_instance']?['location']?['path'], 'N/A'),
  if(equals(outputs('Compose_EventType'), 'dependabot_alert'),
    coalesce(triggerBody()?['alert']?['dependency']?['manifest_path'], 'N/A'),
    'N/A'
  )
)
```

**What it does:** Gets the file path where the vulnerability was found (code scanning → source file, Dependabot → manifest like `package.json`).

---

### 5d. Compose LineNumber

| Setting | Value |
|---|---|
| **Name** | `Compose LineNumber` |
| **Runs After** | `Compose EventType` |
| **Inputs** | *(see expression below)* |

**Expression:**
```
@if(equals(outputs('Compose_EventType'), 'code_scanning_alert'),
  string(coalesce(triggerBody()?['alert']?['most_recent_instance']?['location']?['start_line'], 'N/A')),
  'N/A'
)
```

**What it does:** Gets the line number (only available for code scanning alerts).

---

### 5e. Compose Branch

| Setting | Value |
|---|---|
| **Name** | `Compose Branch` |
| **Runs After** | `Compose EventType` |
| **Inputs** | *(see expression below)* |

**Expression:**
```
@if(equals(outputs('Compose_EventType'), 'code_scanning_alert'),
  coalesce(triggerBody()?['alert']?['most_recent_instance']?['ref'], 'N/A'),
  'N/A'
)
```

**What it does:** Gets the Git branch reference (only for code scanning).

---

### 5f. Compose DetailText

| Setting | Value |
|---|---|
| **Name** | `Compose DetailText` |
| **Runs After** | `Compose EventType` |
| **Inputs** | *(see expression below)* |

**Expression:**
```
@if(equals(outputs('Compose_EventType'), 'code_scanning_alert'),
  coalesce(triggerBody()?['alert']?['most_recent_instance']?['message']?['text'],
           triggerBody()?['alert']?['rule']?['description'], 'No additional details.'),
  if(equals(outputs('Compose_EventType'), 'dependabot_alert'),
    coalesce(triggerBody()?['alert']?['security_advisory']?['description'], 'No additional details.'),
    concat('Secret type: ', coalesce(triggerBody()?['alert']?['secret_type'], 'unknown'),
           '. This secret may have been exposed and should be rotated immediately.')
  )
)
```

**What it does:** Extracts the detailed description/message for the work item body.

---

### 5g. Compose GhasTag

| Setting | Value |
|---|---|
| **Name** | `Compose GhasTag` |
| **Runs After** | `Compose AlertNumber` **AND** `Compose RepoFullName` |
| **Inputs** | *(see expression below)* |

**Expression:**
```
@concat('GHAS-', replace(string(outputs('Compose_RepoFullName')), '/', '-'), '-', string(outputs('Compose_AlertNumber')))
```

**What it does:** Creates a unique deduplication tag like `GHAS-learfield-corp-fan-portal-42`. This tag is used to:
1. Prevent duplicate work items (query by tag before creating)
2. Find the work item to close when the vulnerability is fixed

> ⚠️ **This is the key to the entire dedup/auto-close logic.** Every work item gets this unique tag, and every query searches by this tag.

---

## PHASE 6: Add Compose Actions — Layer 3 (Final Variables)

These are the last two Compose actions before the condition. They depend on multiple upstream actions.

---

### 6a. Compose Tags

| Setting | Value |
|---|---|
| **Name** | `Compose Tags` |
| **Runs After** | `Compose EventType`, `Compose Severity`, `Compose GhasTag` |
| **Inputs** | *(see expression below)* |

**Expression:**
```
@concat('GHAS; ',
  if(equals(outputs('Compose_EventType'), 'code_scanning_alert'), 'CodeScanning',
    if(equals(outputs('Compose_EventType'), 'dependabot_alert'), 'Dependabot', 'SecretScanning')),
  '; ', outputs('Compose_Severity'),
  '; ', outputs('Compose_GhasTag')
)
```

**What it does:** Creates a semicolon-separated tag string: `GHAS; CodeScanning; high; GHAS-org-repo-42`

---

### 6b. Compose Description

| Setting | Value |
|---|---|
| **Name** | `Compose Description` |
| **Runs After** | `Compose EventType`, `Compose AlertUrl`, `Compose GhasTag`, `Compose Severity`, `Compose AlertNumber`, `Compose RepoFullName`, `Compose FilePath`, `Compose LineNumber`, `Compose Branch`, `Compose DetailText` |
| **Inputs** | *(see expression below)* |

**Expression:** *(This builds a full HTML table for the work item description)*
```
@concat('<h3>GitHub Advanced Security Alert</h3>
<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;">
<tr><td><b>Alert Type</b></td><td>',
  if(equals(outputs('Compose_EventType'), 'code_scanning_alert'), 'Code Scanning',
    if(equals(outputs('Compose_EventType'), 'dependabot_alert'), 'Dependabot', 'Secret Scanning')),
'</td></tr>
<tr><td><b>Severity</b></td><td>', toUpper(outputs('Compose_Severity')), '</td></tr>
<tr><td><b>Repository</b></td><td>', string(outputs('Compose_RepoFullName')), '</td></tr>
<tr><td><b>Alert #</b></td><td>', string(outputs('Compose_AlertNumber')), '</td></tr>
<tr><td><b>File</b></td><td>', string(outputs('Compose_FilePath')), '</td></tr>
<tr><td><b>Line</b></td><td>', string(outputs('Compose_LineNumber')), '</td></tr>
<tr><td><b>Branch</b></td><td>', string(outputs('Compose_Branch')), '</td></tr>
</table>
<h4>Details</h4><p>', string(outputs('Compose_DetailText')), '</p>
<p><a href="', string(outputs('Compose_AlertUrl')), '">View in GitHub Advanced Security</a></p>
<hr><p><i>Auto-created by GHAS-ADO Sync | Tag: ', outputs('Compose_GhasTag'), '</i></p>')
```

**What it does:** Builds a rich HTML description with a metadata table, detail text, clickable link back to GHAS, and a footer with the dedup tag.

---

## PHASE 7: Add the Main Condition — Create vs Close

This is the dark box labeled **"Condition IsCreateAction"** at the bottom of the designer, with **True** (green) and **False** (red) branches.

📸 **Screenshot: `screenshots/07-designer-condition-expanded.png`**

![Condition Expanded](screenshots/07-designer-condition-expanded.png)

**How to create it:**
1. Click the **+** below the Compose actions → **Add an action**
2. Search **"Condition"** → select **Condition** (Control)
3. Click **⋯** → **Rename** → `Condition IsCreateAction`
4. Configure the condition:
   - **Left side**: Click "Choose a value" → in the Expression tab type: `outputs('Compose_Action')`
   - **Operator**: `is equal to`
   - **Right side**: `created`

| Runs After | All of: `Compose Action`, `Compose Title`, `Compose Description`, `Compose Tags`, `Compose GhasTag`, `Compose AlertUrl` |

**Logic:** If the webhook action is `created` → we create a new work item (True branch). Otherwise → we check if it's `fixed`/`resolved` and close the work item (False branch).

---

## PHASE 8: Build the TRUE Branch — Create Work Item

📸 **Screenshot: `screenshots/08-designer-true-branch-create.png`**

![True Branch - Create](screenshots/08-designer-true-branch-create.png)

The True branch has 2 steps: **query for duplicates**, then **create if no duplicate exists**.

---

### 8a. HTTP QueryExistingWorkItem

📸 **Screenshot: `screenshots/11-http-query-existing-workitem.png`**

![HTTP Query Existing Work Item](screenshots/11-http-query-existing-workitem.png)

**How to create it:**
1. Inside the **True** branch, click **Add an action**
2. Search **"HTTP"** → select **HTTP** (not the Azure-specific ones)
3. Click **⋯** → **Rename** → `HTTP QueryExistingWorkItem`
4. Configure:

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URI** | `https://dev.azure.com/@{parameters('adoOrganization')}/@{encodeURIComponent(parameters('adoProject'))}/_apis/wit/wiql?api-version=7.1` |
| **Headers** | `Content-Type`: `application/json` |
| | `Authorization`: `@{concat('Basic ', base64(concat(':', parameters('adoPat'))))}` |
| **Body** | *(see below)* |

**Body (WIQL query):**
```json
{
  "query": "SELECT [System.Id] FROM WorkItems WHERE [System.Tags] CONTAINS '@{outputs('Compose_GhasTag')}' AND [System.TeamProject] = '@{parameters('adoProject')}'"
}
```

**What you see in the screenshot:**
- The URI field shows the dynamic content tokens for `adoOrganization` and `encodeURIComponent(...)` as purple/pink pills
- The Authorization header uses `concat(...)` as a dynamic expression
- The Body shows the WIQL query with `Outputs` (Compose_GhasTag) and `adoProject` parameter tokens

**What it does:** Sends a WIQL (Work Item Query Language) query to ADO to check if a work item with this exact GHAS tag already exists. This prevents duplicate work items if GitHub sends the webhook more than once.

---

### 8b. Condition NoExistingWorkItem

**How to create it:**
1. Below `HTTP QueryExistingWorkItem`, click **Add an action** → search **"Condition"**
2. Rename to `Condition NoExistingWorkItem`
3. Configure:
   - **Left side** (Expression): `length(body('HTTP_QueryExistingWorkItem')?['workItems'])`
   - **Operator**: `is equal to`
   - **Right side**: `0`

**Logic:** If the query returned 0 results → no duplicate exists → proceed to create. If results > 0 → skip (do nothing).

---

### 8c. HTTP CreateWorkItem (inside True of NoExistingWorkItem)

**How to create it:**
1. Inside the **True** branch of `Condition NoExistingWorkItem`, click **Add an action**
2. Search **"HTTP"** → select **HTTP**
3. Rename to `HTTP CreateWorkItem`
4. Configure:

| Field | Value |
|---|---|
| **Method** | `PATCH` |
| **URI** | `https://dev.azure.com/@{parameters('adoOrganization')}/@{encodeURIComponent(parameters('adoProject'))}/_apis/wit/workitems/$@{parameters('workItemType')}?api-version=7.1` |
| **Headers** | `Content-Type`: `application/json-patch+json` |
| | `Authorization`: `@{concat('Basic ', base64(concat(':', parameters('adoPat'))))}` |
| **Body** | *(see below)* |

**Body (JSON Patch document):**
```json
[
  {
    "op": "add",
    "path": "/fields/System.Title",
    "value": "@{outputs('Compose_Title')}"
  },
  {
    "op": "add",
    "path": "/fields/System.Description",
    "value": "@{outputs('Compose_Description')}"
  },
  {
    "op": "add",
    "path": "/fields/System.Tags",
    "value": "@{outputs('Compose_Tags')}"
  },
  {
    "op": "add",
    "path": "/relations/-",
    "value": {
      "rel": "Hyperlink",
      "url": "@{outputs('Compose_AlertUrl')}",
      "attributes": {
        "comment": "GitHub Advanced Security Alert"
      }
    }
  }
]
```

**What it does:** Creates a new ADO work item with:
- **Title**: Prefixed alert name (e.g., `[GHAS-CodeScan] SQL Injection vulnerability`)
- **Description**: Rich HTML table with all metadata
- **Tags**: `GHAS; CodeScanning; high; GHAS-org-repo-42`
- **Hyperlink**: Direct link back to the GHAS alert in GitHub

> ⚠️ **Important:** The method is `PATCH` (not POST) — this is required by the ADO Work Item API. The Content-Type must be `application/json-patch+json`.

---

## PHASE 9: Build the FALSE Branch — Auto-Close Work Item

📸 **Screenshot: `screenshots/09-designer-both-branches.png`**

![Both Branches](screenshots/09-designer-both-branches.png)

The False branch handles `fixed` and `resolved` actions — when a vulnerability is remediated in GitHub, we auto-close the corresponding ADO work item.

---

### 9a. Condition IsCloseAction

**How to create it:**
1. Inside the **False** branch, click **Add an action** → search **"Condition"**
2. Rename to `Condition IsCloseAction`
3. Configure with **OR** logic (click "Add row" to add the second condition):
   - Row 1: `outputs('Compose_Action')` **is equal to** `fixed`
   - **OR**
   - Row 2: `outputs('Compose_Action')` **is equal to** `resolved`

**Logic:** Only proceed if the action is `fixed` or `resolved`. Other actions (like `reopened`, `dismissed`) are ignored.

---

### 9b. HTTP FindWorkItemToClose (inside True of IsCloseAction)

**How to create it:**
1. Inside the **True** branch of `Condition IsCloseAction`, add an **HTTP** action
2. Rename to `HTTP FindWorkItemToClose`
3. Configure:

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URI** | `https://dev.azure.com/@{parameters('adoOrganization')}/@{encodeURIComponent(parameters('adoProject'))}/_apis/wit/wiql?api-version=7.1` |
| **Headers** | Same as QueryExistingWorkItem (Content-Type + Authorization) |
| **Body** | *(see below)* |

**Body:**
```json
{
  "query": "SELECT [System.Id], [System.State] FROM WorkItems WHERE [System.Tags] CONTAINS '@{outputs('Compose_GhasTag')}' AND [System.TeamProject] = '@{parameters('adoProject')}' AND [System.State] <> 'Closed' AND [System.State] <> 'Done' AND [System.State] <> 'Removed'"
}
```

**What it does:** Finds the open work item that has the matching GHAS tag. The extra filters (`<> 'Closed'`, `<> 'Done'`, `<> 'Removed'`) ensure we don't try to close an already-closed item.

---

### 9c. Condition WorkItemFound

**How to create it:**
1. Below `HTTP FindWorkItemToClose`, add a **Condition**
2. Rename to `Condition WorkItemFound`
3. Configure:
   - **Left side** (Expression): `length(body('HTTP_FindWorkItemToClose')?['workItems'])`
   - **Operator**: `is greater than`
   - **Right side**: `0`

---

### 9d. HTTP CloseWorkItem (inside True of WorkItemFound)

**How to create it:**
1. Inside the **True** branch, add an **HTTP** action
2. Rename to `HTTP CloseWorkItem`
3. Configure:

| Field | Value |
|---|---|
| **Method** | `PATCH` |
| **URI** | `https://dev.azure.com/@{parameters('adoOrganization')}/@{encodeURIComponent(parameters('adoProject'))}/_apis/wit/workitems/@{body('HTTP_FindWorkItemToClose')?['workItems'][0]?['id']}?api-version=7.1` |
| **Headers** | `Content-Type`: `application/json-patch+json` |
| | `Authorization`: same `concat('Basic ', base64(...))` |
| **Body** | *(see below)* |

**Body:**
```json
[
  {
    "op": "add",
    "path": "/fields/System.State",
    "value": "Done"
  },
  {
    "op": "add",
    "path": "/fields/System.History",
    "value": "Auto-closed by GHAS-ADO Sync: Vulnerability marked as @{outputs('Compose_Action')} in GitHub Advanced Security. View alert: @{outputs('Compose_AlertUrl')}"
  }
]
```

**What it does:** Transitions the work item to **"Done"** state and adds a History comment explaining why it was closed, with a link back to the alert.

> **Note:** We use "Done" instead of "Closed" because the ADO Basic process template uses "Done" as the terminal state.

---

## PHASE 10: Save & Get the Webhook URL

1. Click **Save** in the top toolbar
2. Click on the **trigger** action ("When a GHAS webhook is received")
3. Copy the **HTTP URL** — this is the webhook URL you'll configure in GitHub

📸 **Screenshot: `screenshots/10-trigger-http-request.png`** *(shown earlier — the URL is visible in the HTTP URL field)*

---

## PHASE 11: Configure GitHub Webhook

1. Go to your GitHub repo → **Settings** → **Webhooks** → **Add webhook**
2. **Payload URL**: Paste the Logic App HTTP URL
3. **Content type**: `application/json`
4. **Secret**: *(your webhook secret)*
5. **Events**: Select individual events → check:
   - ☑️ Code scanning alerts
   - ☑️ Dependabot alerts
   - ☑️ Secret scanning alerts

---

## PHASE 12: Verify — Results in ADO

After triggering (either via real GHAS alerts or mock webhooks), work items appear in ADO:

📸 **Screenshot: `screenshots/13-ado-work-items-list.png`**

![ADO Work Items](screenshots/13-ado-work-items-list.png)

**What you see:**
- **#11** `[GHAS-Secret] Azure Storage Account Key` — auto-created by secret scanning alert
- **#10** `[GHAS-Dependabot] Prototype Pollution in lodash < 4.17.21` — auto-created by Dependabot alert
- Items #4-8 are seeded demo data (Learfield Fan Engagement Platform)

---

## PHASE 13: Code View (Reference)

You can also see the entire workflow as JSON by clicking **Logic app code view** in the left sidebar:

📸 **Screenshot: `screenshots/12-logic-app-code-view.png`**

![Logic App Code View](screenshots/12-logic-app-code-view.png)

The code view shows the full JSON definition with triggers, actions, compose expressions, conditions, and HTTP calls — this is what the `infra/workflows/ghas-to-ado.json` file in the repo contains.

---

## Complete Action Summary

| # | Action Name | Type | Purpose |
|---|---|---|---|
| 1 | When a GHAS webhook is received | Trigger (HTTP) | Receive GitHub webhook POST |
| 2 | Compose EventType | Compose | Extract `X-GitHub-Event` header |
| 3 | Compose AlertNumber | Compose | Extract alert number |
| 4 | Compose RepoFullName | Compose | Extract repository full name |
| 5 | Compose AlertUrl | Compose | Extract alert HTML URL |
| 6 | Compose Action | Compose | Extract action (created/fixed/resolved) |
| 7 | Compose GhasTag | Compose | Build dedup tag: `GHAS-org-repo-42` |
| 8 | Compose Title | Compose | Build prefixed title by alert type |
| 9 | Compose Severity | Compose | Normalize severity to lowercase |
| 10 | Compose FilePath | Compose | Extract file path |
| 11 | Compose LineNumber | Compose | Extract line number |
| 12 | Compose Branch | Compose | Extract branch ref |
| 13 | Compose DetailText | Compose | Extract detail description |
| 14 | Compose Tags | Compose | Build ADO tags string |
| 15 | Compose Description | Compose | Build HTML description |
| 16 | Condition IsCreateAction | Condition | Route: create vs close |
| 17 | HTTP QueryExistingWorkItem | HTTP POST | WIQL dedup check |
| 18 | Condition NoExistingWorkItem | Condition | Skip if duplicate |
| 19 | HTTP CreateWorkItem | HTTP PATCH | Create ADO work item |
| 20 | Condition IsCloseAction | Condition | Check if fixed/resolved |
| 21 | HTTP FindWorkItemToClose | HTTP POST | WIQL find open work item |
| 22 | Condition WorkItemFound | Condition | Skip if not found |
| 23 | HTTP CloseWorkItem | HTTP PATCH | Transition to Done |

**Total: 1 trigger + 22 actions = 23 steps**

---

## END-TO-END: What Goes In and What Comes Out

This section shows the **exact webhook payloads** GitHub sends and the **exact ADO work items** the Logic App creates — the full input → output picture for all 3 alert types plus the auto-close flow.

---

### E2E Scenario 1: Code Scanning Alert (Create)

#### INPUT — Webhook GitHub Sends

GitHub fires an HTTP POST to the Logic App URL with:

**Headers:**
```
X-GitHub-Event: code_scanning_alert
Content-Type: application/json
```

**Body:**
```json
{
  "action": "created",
  "alert": {
    "number": 42,
    "html_url": "https://github.com/learfield-corp/fan-portal/security/code-scanning/42",
    "state": "open",
    "rule": {
      "id": "js/sql-injection",
      "severity": "error",
      "security_severity_level": "high",
      "description": "SQL Injection vulnerability in query builder"
    },
    "most_recent_instance": {
      "ref": "refs/heads/main",
      "location": {
        "path": "src/api/queries/userSearch.js",
        "start_line": 47
      },
      "message": {
        "text": "This query depends on a user-provided value and is not parameterized."
      }
    }
  },
  "repository": {
    "full_name": "learfield-corp/fan-portal"
  }
}
```

#### PROCESSING — How Each Compose Action Transforms the Data

| Compose Action | Output Value |
|---|---|
| **EventType** | `code_scanning_alert` |
| **AlertNumber** | `42` |
| **RepoFullName** | `learfield-corp/fan-portal` |
| **AlertUrl** | `https://github.com/learfield-corp/fan-portal/security/code-scanning/42` |
| **Action** | `created` |
| **GhasTag** | `GHAS-learfield-corp-fan-portal-42` |
| **Title** | `[GHAS-CodeScan] SQL Injection vulnerability in query builder` |
| **Severity** | `high` |
| **FilePath** | `src/api/queries/userSearch.js` |
| **LineNumber** | `47` |
| **Branch** | `refs/heads/main` |
| **DetailText** | `This query depends on a user-provided value and is not parameterized.` |
| **Tags** | `GHAS; CodeScanning; high; GHAS-learfield-corp-fan-portal-42` |
| **Description** | *(HTML table — see rendered output below)* |

#### CONDITION EVALUATION

- `Compose Action` = `created` → **Condition IsCreateAction = TRUE**
- `HTTP QueryExistingWorkItem` → WIQL query finds 0 matching work items → **Condition NoExistingWorkItem = TRUE**
- `HTTP CreateWorkItem` → **executes**

#### OUTPUT — ADO Work Item Created

**API Call Made:**
```
PATCH https://dev.azure.com/brandsafway1/brandsafway_Engg/_apis/wit/workitems/$Issue?api-version=7.1
Content-Type: application/json-patch+json
```

**Work Item Created in ADO:**

| Field | Value |
|---|---|
| **ID** | `#9` *(auto-assigned by ADO)* |
| **Type** | Issue |
| **State** | To Do |
| **Title** | `[GHAS-CodeScan] SQL Injection vulnerability in query builder` |
| **Tags** | `GHAS; CodeScanning; high; GHAS-learfield-corp-fan-portal-42` |
| **Hyperlink** | `https://github.com/learfield-corp/fan-portal/security/code-scanning/42` |
| **Description** | *(rendered HTML — see below)* |

**Rendered Description in ADO:**

> ### GitHub Advanced Security Alert
>
> | Field | Value |
> |---|---|
> | **Alert Type** | Code Scanning |
> | **Severity** | HIGH |
> | **Repository** | learfield-corp/fan-portal |
> | **Alert #** | 42 |
> | **File** | src/api/queries/userSearch.js |
> | **Line** | 47 |
> | **Branch** | refs/heads/main |
>
> #### Details
> This query depends on a user-provided value and is not parameterized.
>
> [View in GitHub Advanced Security](https://github.com/learfield-corp/fan-portal/security/code-scanning/42)
>
> *Auto-created by GHAS-ADO Sync | Tag: GHAS-learfield-corp-fan-portal-42*

📸 **Screenshot: `screenshots/13-ado-work-items-list.png`** — shows this work item in the ADO board.

---

### E2E Scenario 2: Dependabot Alert (Create)

#### INPUT — Webhook

**Headers:**
```
X-GitHub-Event: dependabot_alert
Content-Type: application/json
```

**Body:**
```json
{
  "action": "created",
  "alert": {
    "number": 7,
    "html_url": "https://github.com/learfield-corp/fan-portal/security/dependabot/7",
    "security_advisory": {
      "summary": "Prototype Pollution in lodash < 4.17.21",
      "description": "Versions of lodash prior to 4.17.21 are vulnerable to Prototype Pollution via the merge, mergeWith, and defaultsDeep functions."
    },
    "security_vulnerability": {
      "severity": "critical"
    },
    "dependency": {
      "manifest_path": "package.json"
    }
  },
  "repository": {
    "full_name": "learfield-corp/fan-portal"
  }
}
```

#### PROCESSING

| Compose Action | Output Value |
|---|---|
| **EventType** | `dependabot_alert` |
| **GhasTag** | `GHAS-learfield-corp-fan-portal-7` |
| **Title** | `[GHAS-Dependabot] Prototype Pollution in lodash < 4.17.21` |
| **Severity** | `critical` |
| **FilePath** | `package.json` |
| **LineNumber** | `N/A` |
| **Branch** | `N/A` |
| **Tags** | `GHAS; Dependabot; critical; GHAS-learfield-corp-fan-portal-7` |

#### OUTPUT — ADO Work Item

| Field | Value |
|---|---|
| **ID** | `#10` |
| **Title** | `[GHAS-Dependabot] Prototype Pollution in lodash < 4.17.21` |
| **Tags** | `GHAS; Dependabot; critical; GHAS-learfield-corp-fan-portal-7` |
| **Description** | HTML table with Severity=CRITICAL, File=package.json |

---

### E2E Scenario 3: Secret Scanning Alert (Create)

#### INPUT — Webhook

**Headers:**
```
X-GitHub-Event: secret_scanning_alert
Content-Type: application/json
```

**Body:**
```json
{
  "action": "created",
  "alert": {
    "number": 3,
    "html_url": "https://github.com/learfield-corp/fan-portal/security/secret-scanning/3",
    "secret_type": "azure_storage_account_key",
    "secret_type_display_name": "Azure Storage Account Key"
  },
  "repository": {
    "full_name": "learfield-corp/fan-portal"
  }
}
```

#### PROCESSING

| Compose Action | Output Value |
|---|---|
| **EventType** | `secret_scanning_alert` |
| **GhasTag** | `GHAS-learfield-corp-fan-portal-3` |
| **Title** | `[GHAS-Secret] Azure Storage Account Key` |
| **Severity** | `critical` *(always critical for secrets)* |
| **FilePath** | `N/A` |
| **DetailText** | `Secret type: azure_storage_account_key. This secret may have been exposed and should be rotated immediately.` |
| **Tags** | `GHAS; SecretScanning; critical; GHAS-learfield-corp-fan-portal-3` |

#### OUTPUT — ADO Work Item

| Field | Value |
|---|---|
| **ID** | `#11` |
| **Title** | `[GHAS-Secret] Azure Storage Account Key` |
| **Tags** | `GHAS; SecretScanning; critical; GHAS-learfield-corp-fan-portal-3` |
| **Description** | HTML table with Severity=CRITICAL, detail about rotating the secret |

---

### E2E Scenario 4: Auto-Close (Vulnerability Fixed)

#### INPUT — Webhook

When a developer fixes the SQL injection and the code scanning alert is resolved, GitHub sends:

**Headers:**
```
X-GitHub-Event: code_scanning_alert
Content-Type: application/json
```

**Body:**
```json
{
  "action": "fixed",
  "alert": {
    "number": 42,
    "html_url": "https://github.com/learfield-corp/fan-portal/security/code-scanning/42",
    "state": "fixed",
    "rule": {
      "id": "js/sql-injection",
      "description": "SQL Injection vulnerability in query builder"
    }
  },
  "repository": {
    "full_name": "learfield-corp/fan-portal"
  }
}
```

#### CONDITION EVALUATION

- `Compose Action` = `fixed` → **Condition IsCreateAction = FALSE** (not "created")
- Falls to the **False** branch
- `Condition IsCloseAction`: `fixed` equals `fixed` → **TRUE**
- `HTTP FindWorkItemToClose` → WIQL query: `WHERE [System.Tags] CONTAINS 'GHAS-learfield-corp-fan-portal-42' AND [System.State] <> 'Done'` → Finds work item **#9**
- `Condition WorkItemFound`: length > 0 → **TRUE**
- `HTTP CloseWorkItem` → **executes**

#### OUTPUT — ADO Work Item Updated

**API Call Made:**
```
PATCH https://dev.azure.com/brandsafway1/brandsafway_Engg/_apis/wit/workitems/9?api-version=7.1
Content-Type: application/json-patch+json
```

**Work Item #9 — Before vs After:**

| Field | Before | After |
|---|---|---|
| **State** | To Do | **Done** ✅ |
| **History** | *(empty)* | **Auto-closed by GHAS-ADO Sync: Vulnerability marked as fixed in GitHub Advanced Security. View alert: https://github.com/learfield-corp/fan-portal/security/code-scanning/42** |

> The work item is automatically transitioned to "Done" — no human intervention required.

---

### E2E Scenario 5: Deduplication (Duplicate Webhook Ignored)

#### INPUT — Same Webhook Sent Twice

GitHub occasionally retries webhooks. If the same `code_scanning_alert` with `action: "created"` and `alert.number: 42` is sent again:

#### CONDITION EVALUATION

- `Compose Action` = `created` → **Condition IsCreateAction = TRUE**
- `HTTP QueryExistingWorkItem` → WIQL query: `WHERE [System.Tags] CONTAINS 'GHAS-learfield-corp-fan-portal-42'` → **Finds 1 work item**
- `Condition NoExistingWorkItem`: length = 1 ≠ 0 → **FALSE**
- Falls to the empty **False** branch → **does nothing**

#### OUTPUT

**No work item created.** The duplicate is silently ignored. Work item #9 remains unchanged.

---

### Visual Summary: End-to-End Data Flow

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         GITHUB ADVANCED SECURITY                                  │
│                                                                                   │
│   Code Scanning Alert          Dependabot Alert           Secret Scanning Alert   │
│   action: "created"            action: "created"          action: "created"       │
│   rule.description             advisory.summary           secret_type_display_name│
│   file: src/api/query.js       manifest: package.json     (no file info)          │
│   line: 47                     (no line info)             (no line info)           │
│   severity: high               severity: critical         severity: always critical│
└──────────┬───────────────────────────┬──────────────────────────┬─────────────────┘
           │                           │                          │
           ▼                           ▼                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      LOGIC APP: WEBHOOK RECEIVED (HTTP POST)                      │
│                                                                                   │
│  X-GitHub-Event header ──► EventType                                              │
│  body.action ──► Action                                                           │
│  body.alert.number ──► AlertNumber                                                │
│  body.repository.full_name ──► RepoFullName                                       │
│  body.alert.html_url ──► AlertUrl                                                 │
│                                                                                   │
│  ┌─ Normalize by EventType ────────────────────────────────────────────────┐      │
│  │  Title: [GHAS-CodeScan] ... │ [GHAS-Dependabot] ... │ [GHAS-Secret] ...│      │
│  │  Severity: rule.severity    │ vuln.severity          │ always critical  │      │
│  │  FilePath: location.path    │ manifest_path          │ N/A              │      │
│  │  LineNumber: start_line     │ N/A                    │ N/A              │      │
│  │  Branch: ref                │ N/A                    │ N/A              │      │
│  │  DetailText: message.text   │ advisory.description   │ "Secret type..." │      │
│  └─────────────────────────────────────────────────────────────────────────┘      │
│                                                                                   │
│  GhasTag = "GHAS-{owner}-{repo}-{alertNumber}"  ← KEY: enables dedup + auto-close│
│  Tags = "GHAS; {type}; {severity}; {GhasTag}"                                    │
│  Description = HTML table with all metadata + link back to GHAS                   │
└──────────┬───────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         CONDITION: action == "created" ?                           │
│                                                                                   │
│    ┌── TRUE ──────────────────────┐    ┌── FALSE ─────────────────────────────┐   │
│    │                              │    │                                       │   │
│    │  WIQL: Tag exists?           │    │  action == "fixed" or "resolved"?     │   │
│    │    YES → skip (no dupe)      │    │    YES → WIQL: find open WI by tag   │   │
│    │    NO  → Create Work Item    │    │           Found? → Close (→ Done)     │   │
│    │          ├─ Title            │    │           Not found? → skip           │   │
│    │          ├─ Description      │    │    NO  → skip (other action types)    │   │
│    │          ├─ Tags             │    │                                       │   │
│    │          └─ Hyperlink        │    │                                       │   │
│    └──────────────────────────────┘    └───────────────────────────────────────┘   │
└──────────┬─────────────────────────────────────────┬─────────────────────────────┘
           │                                         │
           ▼                                         ▼
┌──────────────────────────────┐    ┌──────────────────────────────────────────────┐
│    AZURE DEVOPS RESULT       │    │    AZURE DEVOPS RESULT                        │
│                              │    │                                               │
│  New Issue Created:          │    │  Existing Issue Updated:                      │
│  ┌────────────────────────┐  │    │  ┌────────────────────────────────────────┐   │
│  │ #9 [GHAS-CodeScan]    │  │    │  │ #9 [GHAS-CodeScan]                    │   │
│  │ SQL Injection vuln... │  │    │  │ SQL Injection vuln...                 │   │
│  │ State: To Do          │  │    │  │ State: To Do → Done  ✅               │   │
│  │ Tags: GHAS; CodeScan..│  │    │  │ History: "Auto-closed by GHAS-ADO     │   │
│  │ Link: → GHAS alert    │  │    │  │          Sync: marked as fixed"       │   │
│  └────────────────────────┘  │    │  └────────────────────────────────────────┘   │
└──────────────────────────────┘    └──────────────────────────────────────────────┘
```

---

### Verified Test Results (From Live Deployment)

These are the actual results from testing against the deployed Logic App (`ghas-ado-sync-nd4zwkrsgpemi`) and ADO project (`brandsafway1/brandsafway_Engg`):

| Test | Webhook Sent | ADO Result | Status |
|---|---|---|---|
| Code Scanning Create | `action: "created"`, alert #42, severity: high | WI **#9** created: `[GHAS-CodeScan] SQL Injection vulnerability` | ✅ Pass |
| Dependabot Create | `action: "created"`, alert #7, severity: critical | WI **#10** created: `[GHAS-Dependabot] Prototype Pollution in lodash` | ✅ Pass |
| Secret Scanning Create | `action: "created"`, alert #3 | WI **#11** created: `[GHAS-Secret] Azure Storage Account Key` | ✅ Pass |
| Auto-Close | `action: "fixed"`, alert #42 | WI **#9** state → **Done**, history comment added | ✅ Pass |
| Deduplication | Duplicate `action: "created"`, alert #42 | No new work item created (tag already exists) | ✅ Pass |
