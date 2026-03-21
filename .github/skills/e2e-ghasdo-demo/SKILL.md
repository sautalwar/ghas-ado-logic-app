---
name: e2e-ghasdo-demo
description: End-to-end demo of GHAzDO (GitHub Advanced Security for Azure DevOps) integration with ADO Work Items via Azure Logic Apps. Creates a Logic App using Designer-only approach (no Code View), configures ADO Service Hooks, and demonstrates automatic work item creation/closure when security alerts are detected. Use this skill when demonstrating GHAzDO alerting, Logic App Designer workflows, or ADO service hook integrations to customers.
---

# E2E GHAzDO → ADO Work Items Demo

This skill guides you through creating a complete end-to-end demo showing how GHAzDO security alerts automatically create and close work items in Azure DevOps Boards using Azure Logic Apps.

## Overview

**What this demo shows:**
1. A Logic App receives GHAzDO alert webhooks via ADO Service Hooks
2. When a new security alert is detected → automatically creates a work item with tags, priority, and description
3. When an alert is resolved/dismissed → automatically closes the corresponding work item with a comment
4. Deduplication: won't create duplicate work items for the same alert

**Architecture:**
```
ADO Repo → GHAzDO Scanner → Service Hook → Logic App Webhook → ADO Work Items API
```

## Prerequisites

| Requirement | Details |
|------------|---------|
| Azure subscription | With permissions to create Logic Apps |
| ADO organization | With Advanced Security enabled |
| ADO PAT | With Work Items (Read/Write) and Code (Read) scopes |
| Resource Group | e.g., `rg-ghas-ado-learfield` |
| Region | East US (or your preferred region) |

## Parameters

When reproducing this demo, you'll need:
- `adoOrganization`: Your ADO org name (e.g., `brandsafway1`)
- `adoProject`: Your ADO project name (e.g., `brandsafway_Engg`)
- `adoPat`: A PAT with Work Items and Code permissions
- `logicAppName`: Name for the Logic App (e.g., `ghas-ado-sync-demo3`)
- `resourceGroup`: Azure resource group name
- `region`: Azure region (e.g., `eastus`)

## Workflow Components (21 Total)

The Logic App workflow has 1 trigger + 20 actions:

### Trigger
1. **When_a_GHAzDO_alert_is_received** — HTTP Request trigger that receives webhooks from ADO Service Hooks

### Field Extractors (8 Compose Actions)
2. **Compose_EventType** — `triggerBody()?['eventType']`
3. **Compose_AlertType** — `coalesce(triggerBody()?['resource']?['alertType'], 'unknown')`
4. **Compose_Severity** — `toLower(coalesce(triggerBody()?['resource']?['severity'], 'medium'))`
5. **Compose_AlertId** — `coalesce(triggerBody()?['resource']?['alertId'], triggerBody()?['resource']?['id'], 0)`
6. **Compose_RepoName** — `coalesce(triggerBody()?['resource']?['repository']?['name'], 'unknown-repo')`
7. **Compose_FilePath** — `coalesce(triggerBody()?['resource']?['location']?['file'], ...)`
8. **Compose_LineNumber** — `coalesce(triggerBody()?['resource']?['location']?['line'], 'N/A')`
9. **Compose_AlertUrl** — `coalesce(triggerBody()?['resource']?['link'], ...)`

### Computed Fields (5 Compose Actions)
10. **Compose_GhasTag** — `concat('GHAzDO-', repoName, '-', alertId)` — unique tag for deduplication
11. **Compose_Title** — Alert-type-specific title (Secret/CodeScan/Dependency)
12. **Compose_Tags** — Semicolon-separated tags: `GHAzDO;alertType;severity;GhasTag`
13. **Compose_Description** — HTML table with all alert details
14. **Compose_IsCreateEvent** — Boolean: is this a "created" event?

### Branching Logic
15. **Condition_IsCreateAction** — Routes to create or close branch

### True Branch (Alert Created → Create Work Item)
16. **HTTP_QueryExistingWorkItem** — WIQL query to check for duplicates
17. **Condition_NoExistingWorkItem** — Only create if no duplicate exists
18. **HTTP_CreateWorkItem** — PATCH to `/_apis/wit/workitems/$Issue` with JSON Patch body

### False Branch (Alert State Changed → Close Work Item)
19. **HTTP_FindWorkItemToClose** — WIQL query to find matching work item
20. **Condition_FoundWorkItemToClose** — Only close if work item exists
21. **HTTP_CloseWorkItem** — PATCH to set State=Done and add History comment

## Step-by-Step Demo Flow

### Phase 1: Create Logic App Resource
1. Azure Portal → Create Resource → Logic App (Consumption)
2. Set name, resource group, region
3. Deploy

### Phase 2: Build Workflow in Designer
1. Open Logic App Designer
2. Add HTTP Request trigger → rename to "When_a_GHAzDO_alert_is_received"
3. Add 8 Compose field extractors (one at a time: + New step → search "Compose" → add → rename → set expression)
4. Add 5 computed field Compose actions
5. Add Condition → set expression for IsCreateEvent check
6. Build True branch: HTTP query → Condition → HTTP create
7. Build False branch: HTTP find → Condition → HTTP close
8. Save workflow → copy webhook URL from trigger

### Phase 3: Configure ADO Service Hooks
1. ADO Project Settings → Service Hooks → + New
2. Hook 1: "Advanced Security alert created" → Web Hooks → paste webhook URL → Test → Finish
3. Hook 2: "Advanced Security alert state changed" → Web Hooks → paste webhook URL → Test → Finish

### Phase 4: E2E Test
1. Trigger webhook with simulated alert payload (or push a secret if push protection allows)
2. Verify Logic App run succeeds
3. Verify work item created in ADO Boards
4. Trigger state-change event
5. Verify work item auto-closed with comment

## Reference Files

| File | Description |
|------|-------------|
| `ghazdo-to-ado.json` | Complete workflow definition (ADO-native format) |
| `ghas-to-ado.json` | Original GitHub webhook format (for reference) |
| `infra/workflows/ghazdo-to-ado.json` | Workflow in infra directory |
| `scripts/generate-qa-guide-pdf.py` | PDF generator for Q&A guide |
| `docs/Webhook-Troubleshooting-Guide.pdf` | Troubleshooting guide for common issues |
| `screenshots/` | All demo screenshots (01-14) |

## Common Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| Push Protection blocks test | Push rejected with SEC101 error | Use simulated webhook payload instead |
| Auth failure (302 redirect) | HTTP action gets redirect to sign-in | Check Base64 PAT encoding, compare character by character |
| "Invalid patch document" (400) | Work item creation fails | Wrap body `concat()` with `json()` function |
| JSON parse error in body | Template evaluation fails | Remove double quotes from HTML in Description field |

## ADO Service Hook Payload Format

```json
{
  "eventType": "ms.vss-code.advancedsecurity.alert.created",
  "resource": {
    "alertId": 1003,
    "alertType": "secret",
    "severity": "critical",
    "repository": { "name": "repo-name" },
    "location": { "file": "path/to/file", "line": 5 },
    "link": "https://dev.azure.com/org/project/_git/repo/alerts/1003"
  },
  "resourceContainers": {
    "project": { "id": "project-name" },
    "account": { "id": "org-name" }
  }
}
```

## Tags Strategy

| Tag | Purpose |
|-----|---------|
| `GHAzDO` | Master tag — filter all GHAzDO-created work items |
| `secret` / `code` / `dependency` | Alert type for triage |
| `critical` / `high` / `medium` / `low` | Severity for prioritization |
| `GHAzDO-{repo}-{alertId}` | Unique fingerprint for deduplication |
