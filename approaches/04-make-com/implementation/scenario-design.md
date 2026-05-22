# Make.com Scenario Design — GHAzDO → ADO Work Items

## Scenario Name
`GHAzDO Security Alert → ADO Work Item`

## Visual Flow

```
┌──────────────────┐
│  1. WEBHOOK      │ ← ADO Service Hook sends GHAzDO alert event
│  Custom Webhook  │
│  (Instant)       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  2. JSON PARSE   │ Parse raw webhook body into structured fields
│  Parse JSON      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  3. ROUTER       │ Branch based on eventType
│  Flow Control    │
└────┬────────┬────┘
     │        │
     ▼        ▼
  Branch 1  Branch 2
  "Created" "StateChanged"
     │        │
     ▼        ▼
┌─────────┐ ┌─────────┐
│ 4a. HTTP│ │ 5a. HTTP│  WIQL query to find existing work item
│ Dedup   │ │ Find WI │
│ Check   │ │         │
└────┬────┘ └────┬────┘
     │           │
  [Filter:    [Filter:
   count=0]    count>0]
     │           │
     ▼           ▼
┌─────────┐ ┌─────────┐
│ 4b. ADO │ │ 5b. ADO │
│ Create  │ │ Update  │  Create new / Close existing work item
│ Work    │ │ Work    │
│ Item    │ │ Item    │
└─────────┘ └─────────┘
```

---

## Module Details

### Module 1: Custom Webhook (Trigger)

| Setting | Value |
|---------|-------|
| **Type** | Webhooks → Custom webhook |
| **Name** | `GHAzDO Alert Receiver` |
| **Data structure** | Auto-generated from sample payload |
| **Queue** | Yes (Make.com queues events if scenario is busy) |
| **Scheduling** | Immediately (instant trigger, not polled) |

**Output:** Raw JSON body from ADO Service Hook

---

### Module 2: Parse JSON

| Setting | Value |
|---------|-------|
| **Type** | JSON → Parse JSON |
| **JSON String** | `{{1.body}}` (webhook body) |
| **Data Structure** | Generated from `webhook-payload-schema.json` examples |

**Output fields used downstream:**
- `eventType` — routing decision
- `resource.alertType` — title prefix (secret/code/dependency)
- `resource.alertId` — dedup tag
- `resource.repository.name` — dedup tag
- `resource.severity` — priority mapping
- `resource.title` / `resource.secretType` — work item title
- `resource.link` — alert URL in description
- `resource.location.file` — file path in description
- `resource.location.line` — line number in description

---

### Module 3: Router

| Setting | Value |
|---------|-------|
| **Type** | Flow Control → Router |
| **Branches** | 2 |

**Branch 1 Filter — "Alert Created":**
| Field | Operator | Value |
|-------|----------|-------|
| `eventType` | Text operators: Contains | `created` |

**Branch 2 Filter — "State Changed":**
| Field | Operator | Value |
|-------|----------|-------|
| `eventType` | Text operators: Contains | `stateChanged` |

---

### Module 4a: HTTP — WIQL Dedup Check (Branch 1)

| Setting | Value |
|---------|-------|
| **Type** | HTTP → Make a request |
| **URL** | `https://dev.azure.com/{{vars.adoOrganization}}/{{vars.adoProject}}/_apis/wit/wiql?api-version=7.1` |
| **Method** | POST |
| **Headers** | `Content-Type: application/json` |
| | `Authorization: Basic {{base64(":" + vars.adoPat)}}` |
| **Body** | See below |

**Request body:**
```json
{
  "query": "SELECT [System.Id] FROM WorkItems WHERE [System.Tags] CONTAINS 'GHAzDO-{{2.resource.repository.name}}-{{2.resource.alertId}}' AND [System.State] <> 'Removed'"
}
```

**Output:** `body.workItems` — array of matching work items

**Filter after this module:**
- Label: `No Duplicate Found`
- Condition: `{{length(4a.body.workItems)}}` equals `0`

---

### Module 4b: Azure DevOps — Create Work Item (Branch 1)

| Setting | Value |
|---------|-------|
| **Type** | Azure DevOps → Create a Work Item |
| **Connection** | `ADO - GHAzDO Integration` |
| **Organization** | (select from dropdown) |
| **Project** | (select from dropdown) |
| **Work Item Type** | `Issue` |

**Field mappings:**

| ADO Field | Make.com Expression |
|-----------|-------------------|
| **Title** | `{{if(2.resource.alertType = "secret"; "[GHAzDO-Secret] " + ifempty(2.resource.secretType; "Secret detected"); if(2.resource.alertType = "code"; "[GHAzDO-CodeScan] " + ifempty(2.resource.title; "Code scanning alert"); if(2.resource.alertType = "dependency"; "[GHAzDO-Dependency] " + ifempty(2.resource.title; "Dependency alert"); "[GHAzDO-Alert] " + ifempty(2.resource.title; "Security alert"))))}}` |
| **Description** | HTML table (see README Step 6c) |
| **Tags** | `GHAzDO;{{2.resource.alertType}};{{2.resource.severity}};GHAzDO-{{2.resource.repository.name}}-{{2.resource.alertId}}` |
| **Priority** | `{{if(or(2.resource.severity = "critical"; 2.resource.severity = "high"); 1; if(2.resource.severity = "medium"; 2; 3))}}` |

---

### Module 5a: HTTP — Find Work Item to Close (Branch 2)

| Setting | Value |
|---------|-------|
| **Type** | HTTP → Make a request |
| **URL** | Same as Module 4a |
| **Method** | POST |
| **Body** | Same WIQL but also excludes `Done` state |

**Request body:**
```json
{
  "query": "SELECT [System.Id] FROM WorkItems WHERE [System.Tags] CONTAINS 'GHAzDO-{{2.resource.repository.name}}-{{2.resource.alertId}}' AND [System.State] <> 'Done' AND [System.State] <> 'Removed'"
}
```

**Filter after this module:**
- Label: `Work Item Found`
- Condition: `{{length(5a.body.workItems)}}` greater than `0`

---

### Module 5b: Azure DevOps — Update Work Item (Branch 2)

| Setting | Value |
|---------|-------|
| **Type** | Azure DevOps → Update a Work Item |
| **Connection** | `ADO - GHAzDO Integration` |
| **Work Item ID** | `{{5a.body.workItems[0].id}}` |

**Field mappings:**

| ADO Field | Value |
|-----------|-------|
| **State** | `Done` |
| **History** | `Auto-closed: GHAzDO alert resolved/fixed.` |

---

## Scenario Settings

| Setting | Value |
|---------|-------|
| **Sequential processing** | No (parallel OK for independent alerts) |
| **Max number of cycles** | 1 |
| **Error handler** | Break (stop on error, notify via email) |
| **Scheduling** | Immediately (webhook-triggered) |

## Variables (Scenario-Level)

| Variable | Description | Example |
|----------|-------------|---------|
| `adoOrganization` | ADO org name | `my-org` |
| `adoProject` | ADO project name | `my-project` |
| `adoPat` | ADO Personal Access Token | `(encrypted)` |
