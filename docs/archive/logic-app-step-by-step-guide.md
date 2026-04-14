# GHAS → ADO Logic App: Complete Step-by-Step Build Guide

> **Purpose:** This guide walks you through building the Logic App from scratch in the Azure Portal GUI — every click, every field, and why we do each step.
>
> **Audience:** Someone with no prior Logic App experience
>
> **End Result:** A fully automated workflow that creates ADO work items when GitHub finds vulnerabilities, and auto-closes them when the vulnerability is fixed.

---

## Table of Contents

1. [What We're Building and Why](#1-what-were-building-and-why)
2. [Prerequisites](#2-prerequisites)
3. [Create the Resource Group](#3-create-the-resource-group)
4. [Create the Logic App](#4-create-the-logic-app)
5. [Set Up Parameters](#5-set-up-parameters)
6. [Add the HTTP Trigger](#6-add-the-http-trigger)
7. [Add Compose Actions — Extract Metadata](#7-add-compose-actions--extract-metadata)
8. [Add the Main Condition — Create vs Close](#8-add-the-main-condition--create-vs-close)
9. [Build the TRUE Branch — Create Work Item](#9-build-the-true-branch--create-work-item)
10. [Build the FALSE Branch — Auto-Close Work Item](#10-build-the-false-branch--auto-close-work-item)
11. [Save and Get the Webhook URL](#11-save-and-get-the-webhook-url)
12. [Connect GitHub to the Logic App](#12-connect-github-to-the-logic-app)
13. [Test End-to-End](#13-test-end-to-end)
14. [Architecture Summary](#14-architecture-summary)

---

## 1. What We're Building and Why

### The Problem
When GitHub Advanced Security (GHAS) finds a vulnerability — a code scanning alert, a Dependabot dependency issue, or an exposed secret — someone has to **manually** go to Azure DevOps, create a work item, copy all the details, and link it back. This is slow, error-prone, and breaks traceability.

### The Solution
We build an **Azure Logic App** (a serverless workflow engine) that:
1. **Receives** a webhook from GitHub whenever GHAS finds or fixes a vulnerability
2. **Normalizes** the metadata (because each alert type has a different payload format)
3. **Checks for duplicates** so the same alert doesn't create multiple work items
4. **Creates** an ADO work item with title, description, severity, tags, and a hyperlink back to the GHAS alert
5. **Auto-closes** the work item when the vulnerability is marked as fixed in GitHub

### Why Logic App?
- **No code** — visual drag-and-drop designer
- **Serverless** — pay only per execution (~$0.000025 per action)
- **Built-in retry** — handles transient failures automatically
- **Audit trail** — every run is logged with inputs and outputs

---

## 2. Prerequisites

Before you begin, make sure you have:

| Item | How to Get It |
|---|---|
| **Azure subscription** | [portal.azure.com](https://portal.azure.com) |
| **Azure DevOps organization & project** | [dev.azure.com](https://dev.azure.com) |
| **ADO Personal Access Token (PAT)** | ADO → User Settings → Personal Access Tokens → New Token → Scope: **Work Items: Read & Write** |
| **GitHub repo with GHAS enabled** | Repo → Settings → Security → Enable code scanning, Dependabot, secret scanning |
| **GitHub PAT** | GitHub → Settings → Developer settings → Personal Access Tokens → Scope: **security_events** |
| **A webhook secret string** | Any random string, e.g. `LearfieldDemo2025!` |

---

## 3. Create the Resource Group

**Why:** A resource group is a container that holds related Azure resources. We create one specifically for this project so everything is organized and easy to find/delete later.

### Steps in Azure Portal:

1. Open **[portal.azure.com](https://portal.azure.com)**
2. In the top search bar, type **"Resource groups"** and click the result
3. Click the **"+ Create"** button at the top
4. Fill in the form:

   | Field | Value | Why |
   |---|---|---|
   | **Subscription** | *(select yours)* | Where the billing goes |
   | **Resource group** | `rg-ghas-ado-learfield` | `rg-` prefix is an Azure naming convention for resource groups |
   | **Region** | `East US` | Choose a region close to your ADO instance for low latency |

5. Click **"Review + Create"** → then **"Create"**

> **What just happened:** You created an empty container in Azure. Think of it like creating a folder on your desktop before putting files in it.

---

## 4. Create the Logic App

**Why:** The Logic App is the actual workflow engine. We use the **Consumption** plan because it's serverless (no infrastructure to manage) and you only pay per execution.

### Steps in Azure Portal:

1. In the top search bar, type **"Logic App"** and click **"Logic Apps"** in the results
2. Click **"+ Add"** (or **"Create"**)
3. You'll see plan options — select **"Consumption"**

   > **Why Consumption?** There are two Logic App plans:
   > - **Consumption** = Serverless, pay-per-execution, simpler. Best for webhook-triggered workflows.
   > - **Standard** = Always-on, more features, higher cost. Overkill for this use case.

4. Fill in the creation form:

   | Field | Value | Why |
   |---|---|---|
   | **Subscription** | *(same as before)* | Billing |
   | **Resource Group** | `rg-ghas-ado-learfield` | Put it in the group we just created |
   | **Logic App name** | `ghas-ado-sync-learfield` | Descriptive name — shows up in the portal |
   | **Region** | `East US` | Same region as the resource group |
   | **Enable log analytics** | `No` | Not needed for a demo; enable in production for monitoring |

5. Click **"Review + Create"** → then **"Create"**
6. Wait ~30 seconds for deployment
7. Click **"Go to resource"**

> **What just happened:** Azure provisioned a Logic App instance. It's like creating an empty flowchart canvas — no steps yet, just the engine ready to be configured.

---

## 5. Set Up Parameters

**Why:** Parameters let you inject values (like your ADO organization, project name, and PAT) at deployment time without hardcoding them in the workflow. Secrets (like PATs) are stored as **SecureString** so they're encrypted and hidden from anyone viewing the Logic App.

### Steps in the Logic App Designer:

1. On the Logic App resource page, click **"Logic app designer"** in the left sidebar (under "Development Tools")
2. If prompted to start with a common trigger, click **"Blank Logic App"** to start from scratch
3. Once the designer opens, click **"Parameters"** button in the top toolbar (it looks like a settings icon or you may see "Parameters" text)
4. Click **"+ Add parameter"** and create each parameter:

   | Name | Type | Why |
   |---|---|---|
   | `adoOrganization` | String | Your ADO org URL segment (e.g., `brandsafway1` from `dev.azure.com/brandsafway1`) |
   | `adoProject` | String | ADO project name (e.g., `brandsafway_Engg`) |
   | `adoPat` | String | ADO Personal Access Token — used to authenticate API calls to ADO |
   | `githubPat` | String | GitHub PAT — used if we need to call GitHub APIs |
   | `webhookSecret` | String | Shared secret for verifying the webhook came from GitHub |
   | `workItemType` | String | The ADO work item type to create (default: `Issue`). Could also be `Bug` or `Task` |

   > **Note:** In the portal designer, you type the parameter name, select the type, and optionally set a default value. For `workItemType`, set the default to `Issue`.

   > **Important:** When deploying via Bicep/Infrastructure-as-Code, the `adoPat`, `githubPat`, and `webhookSecret` are defined as **SecureString** type, which means Azure encrypts them. In the portal designer, you enter them as regular strings but the Bicep template ensures they're secure.

5. After adding all 6 parameters, fill in the **values** for each:
   - `adoOrganization` → `brandsafway1`
   - `adoProject` → `brandsafway_Engg`
   - `adoPat` → *(paste your ADO PAT)*
   - `githubPat` → *(paste your GitHub PAT)*
   - `webhookSecret` → `LearfieldDemo2025!`
   - `workItemType` → `Issue`

6. Click **"Save"** (top toolbar)

> **What just happened:** You defined 6 variables that the workflow will reference throughout. The PATs are stored securely in Azure and never appear in plain text in the workflow definition or run history.

---

## 6. Add the HTTP Trigger

**Why:** Every Logic App starts with a **trigger** — the event that kicks off the workflow. We use an HTTP Request trigger because GitHub webhooks send HTTP POST requests. When GitHub detects a vulnerability, it POSTs a JSON payload to our URL.

### Steps in the Designer:

1. In the designer canvas, you should see a **"Add a trigger"** box (or click the **"+"** at the top)
2. In the search box, type **"HTTP request"**
3. Select **"When an HTTP request is received"** (under the "Request" category)
4. Leave the **"Request Body JSON Schema"** field as `{}` (empty curly braces)

   > **Why empty schema?** GitHub sends **three different payload formats**:
   > - Code scanning alerts have `alert.rule.description`
   > - Dependabot alerts have `alert.security_advisory.summary`
   > - Secret scanning alerts have `alert.secret_type_display_name`
   >
   > By leaving the schema empty, we accept ALL of them and handle the differences ourselves in the Compose actions below.

5. Click **"Save"** — Azure will now generate a unique **Webhook URL**

   > **What just happened:** Azure created an HTTPS endpoint with a SAS (Shared Access Signature) token baked into the URL. This URL is publicly accessible but secured by the token — only someone with the full URL can trigger the Logic App.

---

## 7. Add Compose Actions — Extract Metadata

**Why:** GitHub sends raw webhook payloads with deeply nested data. Each alert type (code scanning, Dependabot, secret scanning) puts data in different locations. We use **Compose actions** to extract and normalize this data into clean variables that the rest of the workflow can use.

> **What is a Compose action?** It's the simplest Logic App action — it takes an expression and outputs a value. Think of it like assigning a variable: `eventType = headers['X-GitHub-Event']`.

### How to add a Compose action:

1. Click the **"+"** button below the trigger → **"Add an action"**
2. Search for **"Compose"** → select **"Compose"** (under "Data Operations")
3. In the **"Inputs"** field, enter the expression
4. Click the **three dots (...)** on the action's title bar → **"Rename"** → give it a descriptive name

Repeat this process for each of the following:

---

### 7a. Compose: EventType

- **Rename to:** `Compose_EventType`
- **Input expression:** `@triggerOutputs()?['headers']?['X-GitHub-Event']`
- **What it does:** Reads the `X-GitHub-Event` HTTP header from the incoming webhook
- **Why:** This header tells us which type of alert it is: `code_scanning_alert`, `dependabot_alert`, or `secret_scanning_alert`. We need this to know where to look for data in the payload.
- **Example output:** `code_scanning_alert`

---

### 7b. Compose: Action

- **Rename to:** `Compose_Action`
- **Input expression:** `@triggerBody()?['action']`
- **What it does:** Reads the `action` field from the JSON body
- **Why:** The action tells us what happened — `created` (new vulnerability found), `fixed` (vulnerability resolved), `dismissed` (manually dismissed), etc. This drives the main condition later.
- **Example output:** `created`

---

### 7c. Compose: AlertNumber

- **Rename to:** `Compose_AlertNumber`
- **Input expression:** `@triggerBody()?['alert']?['number']`
- **What it does:** Gets the unique alert number within the repository
- **Why:** Combined with the repo name, this gives us a unique ID for deduplication.
- **Example output:** `42`

---

### 7d. Compose: RepoFullName

- **Rename to:** `Compose_RepoFullName`
- **Input expression:** `@triggerBody()?['repository']?['full_name']`
- **What it does:** Gets the repository's full name (owner/repo format)
- **Why:** We stamp this on the ADO work item so you know which repo the vulnerability came from.
- **Example output:** `sautalwar/my-app`

---

### 7e. Compose: GhasTag ⭐ (Critical for Deduplication)

- **Rename to:** `Compose_GhasTag`
- **Input expression:** `@concat('GHAS-', replace(string(outputs('Compose_RepoFullName')), '/', '-'), '-', string(outputs('Compose_AlertNumber')))`
- **What it does:** Creates a unique tag like `GHAS-sautalwar-my-app-42`
- **Why:** This is the **key to the entire system**. We stamp this tag on every ADO work item we create. Later, when we need to check for duplicates or find a work item to close, we search by this tag. Without it, we'd have no way to link a GHAS alert to its ADO work item.
- **Depends on:** Must run AFTER `Compose_AlertNumber` and `Compose_RepoFullName` (select these in "Run after" settings — click **...** → **Configure run after**)
- **Example output:** `GHAS-sautalwar-my-app-42`

---

### 7f. Compose: AlertUrl

- **Rename to:** `Compose_AlertUrl`
- **Input expression:** `@coalesce(triggerBody()?['alert']?['html_url'], '')`
- **What it does:** Gets the URL to the alert in GitHub
- **Why:** We add this as a hyperlink on the ADO work item so developers can click directly to the vulnerability.
- **What is `coalesce`?** It returns the first non-null value. If `html_url` doesn't exist, it returns an empty string instead of failing.
- **Example output:** `https://github.com/sautalwar/my-app/security/code-scanning/42`

---

### 7g. Compose: Title

- **Rename to:** `Compose_Title`
- **Input expression:**
```
@if(equals(outputs('Compose_EventType'), 'code_scanning_alert'),
    concat('[GHAS-CodeScan] ', coalesce(triggerBody()?['alert']?['rule']?['description'], 'Code scanning alert')),
    if(equals(outputs('Compose_EventType'), 'dependabot_alert'),
        concat('[GHAS-Dependabot] ', coalesce(triggerBody()?['alert']?['security_advisory']?['summary'], 'Dependabot alert')),
        concat('[GHAS-Secret] ', coalesce(triggerBody()?['alert']?['secret_type_display_name'], 'Secret scanning alert'))
    )
)
```
- **What it does:** Creates a human-readable title with a prefix showing the alert type
- **Why:** When developers see `[GHAS-CodeScan] SQL Injection in login.py` in their ADO board, they immediately know what type of vulnerability it is and where it came from.
- **How the logic works:**
  - Is it a code scanning alert? → Use `rule.description`
  - Is it a Dependabot alert? → Use `security_advisory.summary`
  - Otherwise (secret scanning) → Use `secret_type_display_name`
- **Depends on:** `Compose_EventType`
- **Example output:** `[GHAS-CodeScan] SQL injection vulnerability in database query`

---

### 7h. Compose: Severity

- **Rename to:** `Compose_Severity`
- **Input expression:**
```
@toLower(if(equals(outputs('Compose_EventType'), 'code_scanning_alert'),
    coalesce(triggerBody()?['alert']?['rule']?['security_severity_level'], 'medium'),
    if(equals(outputs('Compose_EventType'), 'dependabot_alert'),
        coalesce(triggerBody()?['alert']?['security_vulnerability']?['severity'], 'medium'),
        'critical'
    )
))
```
- **What it does:** Extracts the severity and normalizes it to lowercase
- **Why:** Each alert type stores severity in a different field. We normalize to a single value. Secret scanning alerts default to `critical` because an exposed secret is always urgent.
- **Depends on:** `Compose_EventType`
- **Example output:** `high`

---

### 7i. Compose: FilePath

- **Rename to:** `Compose_FilePath`
- **Input expression:**
```
@if(equals(outputs('Compose_EventType'), 'code_scanning_alert'),
    coalesce(triggerBody()?['alert']?['most_recent_instance']?['location']?['path'], 'N/A'),
    if(equals(outputs('Compose_EventType'), 'dependabot_alert'),
        coalesce(triggerBody()?['alert']?['dependency']?['manifest_path'], 'N/A'),
        'N/A'
    )
)
```
- **What it does:** Gets the file path where the vulnerability exists
- **Why:** Developers need to know which file to look at. Code scanning gives a specific file; Dependabot gives the manifest (package.json, requirements.txt); secret scanning doesn't have a file path.
- **Example output:** `src/database/queries.py`

---

### 7j. Compose: LineNumber

- **Rename to:** `Compose_LineNumber`
- **Input expression:**
```
@if(equals(outputs('Compose_EventType'), 'code_scanning_alert'),
    string(coalesce(triggerBody()?['alert']?['most_recent_instance']?['location']?['start_line'], 'N/A')),
    'N/A'
)
```
- **What it does:** Gets the line number for code scanning alerts
- **Why:** Only code scanning provides line-level precision. Dependabot and secret scanning don't have line numbers.
- **Example output:** `47`

---

### 7k. Compose: Branch

- **Rename to:** `Compose_Branch`
- **Input expression:**
```
@if(equals(outputs('Compose_EventType'), 'code_scanning_alert'),
    coalesce(triggerBody()?['alert']?['most_recent_instance']?['ref'], 'N/A'),
    'N/A'
)
```
- **What it does:** Gets the branch where the vulnerability was detected
- **Why:** Helps developers know which branch needs the fix.
- **Example output:** `refs/heads/main`

---

### 7l. Compose: DetailText

- **Rename to:** `Compose_DetailText`
- **Input expression:**
```
@if(equals(outputs('Compose_EventType'), 'code_scanning_alert'),
    coalesce(triggerBody()?['alert']?['most_recent_instance']?['message']?['text'],
             triggerBody()?['alert']?['rule']?['description'],
             'No additional details.'),
    if(equals(outputs('Compose_EventType'), 'dependabot_alert'),
        coalesce(triggerBody()?['alert']?['security_advisory']?['description'], 'No additional details.'),
        concat('Secret type: ', coalesce(triggerBody()?['alert']?['secret_type'], 'unknown'),
               '. This secret may have been exposed and should be rotated immediately.')
    )
)
```
- **What it does:** Gets the detailed description/explanation of the vulnerability
- **Why:** Provides context in the work item so developers understand what the issue is and how to fix it.

---

### 7m. Compose: Tags

- **Rename to:** `Compose_Tags`
- **Input expression:**
```
@concat('GHAS; ',
    if(equals(outputs('Compose_EventType'), 'code_scanning_alert'), 'CodeScanning',
        if(equals(outputs('Compose_EventType'), 'dependabot_alert'), 'Dependabot', 'SecretScanning')),
    '; ', outputs('Compose_Severity'),
    '; ', outputs('Compose_GhasTag'))
```
- **What it does:** Creates a semicolon-separated tag string
- **Why:** ADO uses tags for filtering and search. We add: `GHAS` (identifies it as auto-created), the alert type, the severity, and the unique tracking tag.
- **Depends on:** `Compose_EventType`, `Compose_Severity`, `Compose_GhasTag`
- **Example output:** `GHAS; CodeScanning; high; GHAS-sautalwar-my-app-42`

---

### 7n. Compose: Description (HTML Body)

- **Rename to:** `Compose_Description`
- **Input expression:** A long `concat()` that builds an HTML table (see full expression in the workflow JSON)
- **What it does:** Creates a rich HTML description for the ADO work item containing:
  - Alert type, severity, repository, alert number
  - File path, line number, branch
  - Detailed text about the vulnerability
  - A clickable link back to the GHAS alert
  - A footer with the tracking tag
- **Why:** ADO work item descriptions support HTML. A formatted table is much more readable than plain text for developers triaging vulnerabilities.
- **Depends on:** ALL previous Compose actions (this is the final aggregation step)

---

## 8. Add the Main Condition — Create vs Close

**Why:** GitHub sends webhooks for many events — `created`, `fixed`, `resolved`, `dismissed`, `reopened`, etc. We need to decide: should we **create** a new ADO work item, or should we **close** an existing one?

### Steps in the Designer:

1. Click **"+"** below the Compose actions → **"Add an action"**
2. Search for **"Condition"** → select **"Condition"** (under "Control")
3. This adds a condition block with **True** and **False** branches
4. **Rename** it to `Condition_IsCreateAction`
5. Configure the condition:
   - **Left side:** Click "Choose a value" → switch to **Expression** tab → type: `outputs('Compose_Action')`
   - **Operator:** `is equal to`
   - **Right side:** `created`

6. Configure **"Run after"** (click **...** → **Configure run after**):
   - Check: `Compose_Action`, `Compose_Title`, `Compose_Description`, `Compose_Tags`, `Compose_GhasTag`, `Compose_AlertUrl`
   - This ensures ALL the metadata extraction is complete before we hit the condition

> **What just happened:** The workflow now branches:
> - **True** = the action is "created" → a new vulnerability was found → create a work item
> - **False** = the action is something else → check if it's "fixed"/"resolved" → close the work item

---

## 9. Build the TRUE Branch — Create Work Item

This branch handles: *"A new vulnerability was just found. Create an ADO work item for it."*

But first, we need to check: *"Does a work item already exist for this alert?"* (Deduplication)

### Step 9a: Add WIQL Query — Check for Duplicates

**Why:** Webhooks can fire multiple times (retries, network issues). Without deduplication, you'd get 2 or 3 identical work items for the same alert. We search ADO by the unique `GhasTag` to see if one already exists.

1. Inside the **True** branch, click **"Add an action"**
2. Search for **"HTTP"** → select **"HTTP"** (the generic HTTP action, NOT an ADO connector)
3. **Rename** to `HTTP_QueryExistingWorkItem`

   > **Why HTTP instead of the ADO connector?** The built-in ADO connector doesn't support WIQL queries. The HTTP action lets us call any REST API directly.

4. Configure:

   | Field | Value |
   |---|---|
   | **Method** | `POST` |
   | **URI** | `https://dev.azure.com/@{parameters('adoOrganization')}/@{encodeURIComponent(parameters('adoProject'))}/_apis/wit/wiql?api-version=7.1` |
   | **Headers** | `Content-Type`: `application/json` |
   | **Headers** | `Authorization`: `@{concat('Basic ', base64(concat(':', parameters('adoPat'))))}` |
   | **Body** | See below |

   **Body (JSON):**
   ```json
   {
     "query": "SELECT [System.Id] FROM WorkItems WHERE [System.Tags] CONTAINS '@{outputs('Compose_GhasTag')}' AND [System.TeamProject] = '@{parameters('adoProject')}'"
   }
   ```

   > **What is WIQL?** Work Item Query Language — it's like SQL but for ADO work items. This query says: "Find any work item that has our unique GHAS tag in its tags."

   > **How does the Authorization work?** ADO uses Basic authentication. The format is `Basic base64(':PAT')` — note the colon before the PAT with an empty username. The `concat(':', parameters('adoPat'))` builds `:your-pat-here`, then `base64()` encodes it.

---

### Step 9b: Add Condition — No Existing Work Item

**Why:** If the WIQL query returned results, a work item already exists and we should skip creation. If it returned 0 results, we proceed.

1. Below `HTTP_QueryExistingWorkItem`, click **"+"** → **"Add an action"** → search **"Condition"**
2. **Rename** to `Condition_NoExistingWorkItem`
3. Configure:
   - **Left side (Expression):** `length(body('HTTP_QueryExistingWorkItem')?['workItems'])`
   - **Operator:** `is equal to`
   - **Right side:** `0`
4. Set **"Run after"** to `HTTP_QueryExistingWorkItem → Succeeded`

> **What this checks:** The WIQL response has a `workItems` array. If its length is 0, no duplicate exists → proceed to create.

---

### Step 9c: Add HTTP Action — Create the Work Item

**Why:** This is the core action — actually creating the ADO work item with all the metadata we extracted.

1. Inside the **True** branch of `Condition_NoExistingWorkItem`, click **"Add an action"**
2. Search for **"HTTP"** → select **"HTTP"**
3. **Rename** to `HTTP_CreateWorkItem`
4. Configure:

   | Field | Value |
   |---|---|
   | **Method** | `PATCH` |
   | **URI** | `https://dev.azure.com/@{parameters('adoOrganization')}/@{encodeURIComponent(parameters('adoProject'))}/_apis/wit/workitems/$@{parameters('workItemType')}?api-version=7.1` |
   | **Headers** | `Content-Type`: `application/json-patch+json` |
   | **Headers** | `Authorization`: `@{concat('Basic ', base64(concat(':', parameters('adoPat'))))}` |

   > **Why PATCH, not POST?** ADO's work item creation API uses PATCH with JSON Patch format. This is an ADO API design choice, not a Logic App thing.

   > **Why `application/json-patch+json`?** This is a special content type that tells ADO the body contains JSON Patch operations (add, replace, remove fields).

   **Body (JSON array of patch operations):**
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

   > **What each patch operation does:**
   >
   > 1. **System.Title** — Sets the work item title (e.g., `[GHAS-CodeScan] SQL injection vulnerability`)
   > 2. **System.Description** — Sets the rich HTML description with the metadata table
   > 3. **System.Tags** — Adds the tags including the unique GHAS tracking tag
   > 4. **/relations/-** — Adds a **hyperlink** to the GHAS alert. The `-` means "append to the relations array." This creates a clickable link in the ADO work item that takes you straight to the vulnerability in GitHub.

---

## 10. Build the FALSE Branch — Auto-Close Work Item

This branch handles: *"The action is NOT 'created' — maybe the vulnerability was fixed. If so, find the existing work item and close it."*

### Step 10a: Add Condition — Is it a Close Action?

**Why:** Not every non-"created" action should trigger a close. We only close on `fixed` or `resolved`. We ignore `dismissed`, `reopened`, etc.

1. Inside the **False** branch of `Condition_IsCreateAction`, click **"Add an action"**
2. Search for **"Condition"** → select **"Condition"**
3. **Rename** to `Condition_IsCloseAction`
4. Configure with **OR** logic (click **"Add row"** then change **"And"** to **"Or"**):
   - Row 1: `outputs('Compose_Action')` is equal to `fixed`
   - Row 2: `outputs('Compose_Action')` is equal to `resolved`

   > **Why OR?** Different alert types use different words: code scanning uses `fixed`, some alert types use `resolved`. We handle both.

---

### Step 10b: Add HTTP Action — Find the Open Work Item

**Why:** Before we can close a work item, we need to find it. We search by the unique GHAS tag, and we filter out already-closed items.

1. Inside the **True** branch of `Condition_IsCloseAction`, click **"Add an action"**
2. Search for **"HTTP"** → select **"HTTP"**
3. **Rename** to `HTTP_FindWorkItemToClose`
4. Configure:

   | Field | Value |
   |---|---|
   | **Method** | `POST` |
   | **URI** | Same WIQL endpoint as Step 9a |
   | **Headers** | Same Authorization header |

   **Body:**
   ```json
   {
     "query": "SELECT [System.Id], [System.State] FROM WorkItems WHERE [System.Tags] CONTAINS '@{outputs('Compose_GhasTag')}' AND [System.TeamProject] = '@{parameters('adoProject')}' AND [System.State] <> 'Closed' AND [System.State] <> 'Done' AND [System.State] <> 'Removed'"
   }
   ```

   > **What's different from the create-branch query?** We add `State <> 'Closed' AND State <> 'Done' AND State <> 'Removed'` to only find **open** work items. No point closing something that's already closed.

---

### Step 10c: Add Condition — Was a Work Item Found?

1. Below `HTTP_FindWorkItemToClose`, add a **Condition**
2. **Rename** to `Condition_WorkItemFound`
3. Configure:
   - **Expression:** `length(body('HTTP_FindWorkItemToClose')?['workItems'])`
   - **Operator:** `is greater than`
   - **Right side:** `0`

---

### Step 10d: Add HTTP Action — Close the Work Item

1. Inside the **True** branch of `Condition_WorkItemFound`, click **"Add an action"**
2. Search for **"HTTP"** → select **"HTTP"**
3. **Rename** to `HTTP_CloseWorkItem`
4. Configure:

   | Field | Value |
   |---|---|
   | **Method** | `PATCH` |
   | **URI** | `https://dev.azure.com/@{parameters('adoOrganization')}/@{encodeURIComponent(parameters('adoProject'))}/_apis/wit/workitems/@{body('HTTP_FindWorkItemToClose')?['workItems'][0]?['id']}?api-version=7.1` |
   | **Headers** | Same `json-patch+json` Content-Type and Authorization |

   > **Key detail in the URI:** `['workItems'][0]?['id']` — we grab the **first** matching work item's ID and inject it into the URL.

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

   > **What each operation does:**
   > 1. **System.State → "Done"** — Transitions the work item to the Done state (we use "Done" instead of "Closed" because the ADO Basic process template uses "Done" as the terminal state)
   > 2. **System.History** — Adds a comment to the work item's discussion/history explaining why it was closed, with a link back to the GHAS alert for audit trail

---

## 11. Save and Get the Webhook URL

1. Click **"Save"** in the top toolbar of the designer
2. Click on the **"When a GHAS webhook is received"** trigger block
3. The **HTTP POST URL** field shows your webhook URL
4. Click the **📋 copy** icon to copy it

The URL looks like:
```
https://prod-04.eastus.logic.azure.com:443/workflows/{id}/triggers/When_a_GHAS_webhook_is_received/paths/invoke?api-version=2019-05-01&sp=...&sv=1.0&sig=...
```

> **Security note:** This URL contains a SAS signature (`sig=...`). Anyone with this URL can trigger your Logic App. Treat it like a password — don't commit it to source control.

---

## 12. Connect GitHub to the Logic App

**Why:** Now we need to tell GitHub to send webhooks to our Logic App URL whenever a GHAS alert is created or resolved.

### Steps in GitHub:

1. Open your GitHub repository → **Settings** → **Webhooks** (left sidebar)
2. Click **"Add webhook"**
3. Fill in:

   | Field | Value | Why |
   |---|---|---|
   | **Payload URL** | *(paste the Logic App trigger URL)* | Where GitHub sends the webhook |
   | **Content type** | `application/json` | We need JSON, not form-encoded |
   | **Secret** | `LearfieldDemo2025!` | Must match the `webhookSecret` parameter — used for HMAC verification |
   | **SSL verification** | ✅ Enable | Always use SSL in production |

4. Under **"Which events would you like to trigger this webhook?"**:
   - Select **"Let me select individual events"**
   - ✅ Check **Code scanning alerts**
   - ✅ Check **Dependabot alerts**
   - ✅ Check **Secret scanning alerts**
   - Uncheck everything else

5. Ensure **Active** is checked
6. Click **"Add webhook"**

> **What just happened:** GitHub will now POST to your Logic App URL whenever any of the 3 GHAS alert types fires. The webhook payload includes all the alert metadata that our Compose actions extract.

---

## 13. Test End-to-End

### Option A: Trigger a Real Alert

1. Commit vulnerable code to the repo (e.g., a SQL injection pattern)
2. Wait for CodeQL to scan (~2-5 minutes)
3. A GHAS alert is created → webhook fires → Logic App runs → ADO work item appears

### Option B: Send a Mock Webhook

Use PowerShell to simulate a GitHub webhook:

```powershell
$body = @{
    action = "created"
    alert = @{
        number = 99
        html_url = "https://github.com/your-org/your-repo/security/code-scanning/99"
        rule = @{
            description = "Test: SQL injection vulnerability"
            security_severity_level = "high"
        }
        most_recent_instance = @{
            location = @{ path = "src/db.py"; start_line = 42 }
            ref = "refs/heads/main"
            message = @{ text = "User input used in SQL query without sanitization" }
        }
    }
    repository = @{ full_name = "your-org/your-repo" }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "YOUR_LOGIC_APP_URL_HERE" `
    -Method POST `
    -ContentType "application/json" `
    -Headers @{ "X-GitHub-Event" = "code_scanning_alert" } `
    -Body $body
```

### Verify in Azure Portal:

1. Go to your Logic App → **Overview** → **Runs history**
2. Click the most recent run — it should show **Succeeded** ✅
3. Click each action to see inputs/outputs

### Verify in ADO:

1. Go to `https://dev.azure.com/brandsafway1/brandsafway_Engg/_workitems`
2. Look for the new work item with the `[GHAS-CodeScan]` prefix

---

## 14. Architecture Summary

```
┌──────────────────┐         ┌─────────────────────────────────────────┐         ┌──────────────┐
│                  │  HTTP   │           Azure Logic App               │  REST   │              │
│  GitHub GHAS     │  POST   │                                         │  API    │  Azure DevOps│
│                  ├────────►│  Trigger → Extract → Condition          │────────►│              │
│  • Code Scanning │         │           Metadata    ├─ Create ──► WI  │         │  Work Items  │
│  • Dependabot    │         │                       └─ Close  ──► WI  │         │  Board       │
│  • Secret Scan   │         │                                         │         │  Backlog     │
└──────────────────┘         └─────────────────────────────────────────┘         └──────────────┘
```

### Key Design Decisions:

| Decision | Reasoning |
|---|---|
| **Consumption plan** | Pay-per-execution, serverless, no infrastructure to manage |
| **HTTP trigger (not GitHub connector)** | GitHub connector doesn't support GHAS webhook events |
| **Empty JSON schema** | Accept all 3 alert type payloads without modification |
| **Compose actions for normalization** | Each alert type has different field paths — normalize once, use everywhere |
| **WIQL deduplication** | Prevent duplicate work items from webhook retries |
| **Unique GHAS tag** | Single source of truth linking GHAS alerts to ADO work items |
| **HTTP actions (not ADO connector)** | Full control over WIQL queries and JSON Patch operations |
| **"Done" not "Closed"** | ADO Basic process template uses "Done" as the terminal state |
| **Hyperlink relation** | Creates a clickable link in the ADO work item back to the GHAS alert |

---

*Generated for the Learfield customer demo — GHAS → ADO Logic App*
