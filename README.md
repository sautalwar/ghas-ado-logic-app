# GHAS → ADO Work Item Sync

Automatically create and manage Azure DevOps work items from GitHub Advanced Security (GHAS) vulnerability alerts using an Azure Logic App.

## Overview

When GitHub Advanced Security detects a vulnerability, this Logic App automatically:

1. **Creates an ADO work item** with full vulnerability metadata
2. **Links the work item** back to the GHAS alert via hyperlink
3. **Auto-closes the work item** when the vulnerability is resolved in GHAS

### Supported Alert Types

| Alert Type | Create Trigger | Close Trigger |
|---|---|---|
| Code Scanning (CodeQL) | `created` | `fixed` |
| Dependabot | `created` | `fixed` |
| Secret Scanning | `created` | `resolved` |

### Work Item Fields Auto-Populated

- **Title** — Alert type prefix + vulnerability description
- **Description** — HTML table with severity, repo, file, line, branch, details, and link to GHAS
- **Tags** — `GHAS`, alert type, severity, unique tracking tag
- **Hyperlink** — Direct link to the GHAS alert

## Architecture

```
GitHub Webhooks                    Azure Logic App                 Azure DevOps
┌──────────────────┐    POST     ┌──────────────────────┐        ┌──────────────┐
│ code_scanning     │───────────▶│                      │        │              │
│ dependabot        │            │  Parse & Normalize   │──────▶ │ Create Work  │
│ secret_scanning   │            │  Deduplicate (WIQL)  │        │   Item       │
└──────────────────┘            │  Create or Close     │        │              │
                                │  Work Item           │◀────── │ WIQL Query   │
                                └──────────────────────┘        └──────────────┘
```

## Prerequisites

- **Azure subscription** with permissions to create Logic Apps
- **Azure DevOps** organization and project
- **GitHub repository** with GHAS enabled
- **Azure CLI** installed and authenticated
- **GitHub PAT** with `security_events` and `admin:repo_hook` scopes
- **ADO PAT** with `Work Items (Read & Write)` scope

## Quick Start

### 1. Clone and Configure

```powershell
git clone <this-repo>
cd Logic_app_ADO_learfield
```

Edit `infra/parameters.json` with your ADO organization and project names.

### 2. Deploy

```powershell
$adoPat = Read-Host -AsSecureString "ADO PAT"
$ghPat = Read-Host -AsSecureString "GitHub PAT"
$secret = Read-Host -AsSecureString "Webhook Secret"

.\scripts\deploy.ps1 `
    -ResourceGroupName "rg-ghas-ado-sync" `
    -Location "eastus" `
    -AdoOrganization "brandsafway1" `
    -AdoProject "brandsafway_Engg" `
    -AdoPat $adoPat `
    -GitHubPat $ghPat `
    -WebhookSecret $secret
```

### 3. Configure Webhook

Use the webhook URL from the deployment output:

```powershell
.\scripts\setup-webhooks.ps1 `
    -RepoFullName "owner/repo" `
    -WebhookUrl "<logic-app-trigger-url>" `
    -WebhookSecret $secret `
    -GitHubPat $ghPat
```

### 4. Verify

1. Go to your GitHub repo → **Settings** → **Webhooks** → **Recent Deliveries**
2. Trigger a test alert (e.g., commit a known vulnerability pattern)
3. Check your ADO project for the new work item

## File Structure

```
├── README.md                        # This file
├── infra/
│   ├── main.bicep                   # Main Bicep orchestrator
│   ├── parameters.json              # Deployment parameters
│   ├── modules/
│   │   └── logic-app.bicep          # Logic App resource definition
│   └── workflows/
│       └── ghas-to-ado.json         # Logic App workflow definition
├── scripts/
│   ├── deploy.ps1                   # Azure deployment script
│   └── setup-webhooks.ps1           # GitHub webhook configuration
└── docs/
    └── setup-guide.md               # Detailed setup guide
```

## Deduplication

The Logic App uses a **tag-based deduplication** strategy. Each work item is tagged with a unique identifier:

```
GHAS-{owner}-{repo}-{alert_number}
```

Before creating a new work item, the Logic App queries ADO via WIQL to check if a work item with this tag already exists. This prevents duplicates from webhook retries.

## Auto-Close Behavior

When GHAS marks a vulnerability as `fixed` (code scanning, Dependabot) or `resolved` (secret scanning):

1. The Logic App receives the webhook event
2. Queries ADO for open work items with the matching GHAS tag
3. Transitions the work item to **Closed** state
4. Adds a history comment with the resolution details

> **Note:** The close state is set to "Closed". If your ADO process template uses "Done" instead, update the `System.State` value in `infra/workflows/ghas-to-ado.json`.

## Customization

### Work Item Type

Change the `workItemType` parameter in `parameters.json` (default: `Issue`). Common options: `Bug`, `Task`, `Issue`.

### ADO Process Template

If your process template uses different state names (e.g., "Done" instead of "Closed"), update the `HTTP_CloseWorkItem` action in `infra/workflows/ghas-to-ado.json`.

### Multi-Repo Setup

Run `setup-webhooks.ps1` for each repository you want to monitor. The Logic App handles all repos through a single endpoint.

## Troubleshooting

| Issue | Resolution |
|---|---|
| Webhook returns 401/403 | Verify the Logic App trigger URL is correct and contains the SAS token |
| Work item not created | Check Logic App run history in Azure Portal for errors |
| Duplicate work items | Verify the GHAS tag format matches in WIQL queries |
| Close action fails | Check that your ADO process template supports the "Closed" state |
| "Forbidden" from ADO API | Ensure the ADO PAT has "Work Items: Read & Write" scope |

## Security

- The Logic App trigger URL contains a SAS token for authentication
- PATs are stored as secure parameters in the Logic App (consider Azure Key Vault for production)
- Webhook payloads can be validated via HMAC-SHA256 (webhook secret)

## License

Internal use — Learfield.
