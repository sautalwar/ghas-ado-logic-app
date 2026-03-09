# Detailed Setup Guide

This guide walks through the complete setup of the GHAS-ADO Sync Logic App.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1: Create Personal Access Tokens](#step-1-create-personal-access-tokens)
- [Step 2: Deploy the Logic App](#step-2-deploy-the-logic-app)
- [Step 3: Configure GitHub Webhooks](#step-3-configure-github-webhooks)
- [Step 4: Verify the Integration](#step-4-verify-the-integration)
- [Step 5: Production Hardening](#step-5-production-hardening)
- [Appendix: Manual Webhook Setup](#appendix-manual-webhook-setup)
- [Appendix: ADO Process Templates](#appendix-ado-process-templates)
- [Appendix: Finding Work Items from GHAS](#appendix-finding-work-items-from-ghas)

---

## Prerequisites

### Azure

- An Azure subscription
- Permissions to create resource groups and Logic Apps
- Azure CLI installed (`az`) — [Install guide](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- Logged in: `az login`

### Azure DevOps

- An ADO organization and project
- A user with permissions to create work items

### GitHub

- A repository with GitHub Advanced Security enabled
- Admin access to the repository (for webhook configuration)

---

## Step 1: Create Personal Access Tokens

### Azure DevOps PAT

1. Go to `https://dev.azure.com/brandsafway1/_usersSettings/tokens`
2. Click **+ New Token**
3. Set a descriptive name: `GHAS-ADO Sync`
4. Set expiration (recommend: 90 days, then rotate)
5. Under **Scopes**, select:
   - **Work Items**: `Read & Write`
6. Click **Create** and copy the token

### GitHub PAT (Fine-Grained)

1. Go to `https://github.com/settings/personal-access-tokens/new`
2. Set a descriptive name: `GHAS-ADO Webhook`
3. Select the target repository or organization
4. Under **Repository permissions**, enable:
   - **Security events**: `Read` (to read GHAS alerts)
   - **Webhooks**: `Read and write` (to create webhooks)
5. Click **Generate token** and copy it

### Webhook Secret

Generate a random secret for webhook payload validation:

```powershell
# Generate a random 32-character secret
$webhookSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object { [char]$_ })
Write-Host "Webhook Secret: $webhookSecret"
# Save this securely — you'll need it for both deployment and webhook setup
```

---

## Step 2: Deploy the Logic App

### Option A: Scripted Deployment (Recommended)

```powershell
# Store secrets securely
$adoPat = Read-Host -AsSecureString "Enter ADO PAT"
$ghPat = Read-Host -AsSecureString "Enter GitHub PAT"
$secret = Read-Host -AsSecureString "Enter Webhook Secret"

# Deploy
.\scripts\deploy.ps1 `
    -ResourceGroupName "rg-ghas-ado-sync" `
    -Location "eastus" `
    -AdoOrganization "brandsafway1" `
    -AdoProject "brandsafway_Engg" `
    -AdoPat $adoPat `
    -GitHubPat $ghPat `
    -WebhookSecret $secret `
    -WorkItemType "Issue"
```

The script outputs the **Logic App Webhook URL**. Save this — you need it for Step 3.

### Option B: Manual Azure CLI Deployment

```powershell
# Create resource group
az group create --name rg-ghas-ado-sync --location eastus

# Deploy Bicep
az deployment group create `
    --resource-group rg-ghas-ado-sync `
    --template-file infra/main.bicep `
    --parameters `
        adoOrganization=your-ado-org `
        adoProject=your-ado-project `
        adoPat=<your-ado-pat> `
        githubPat=<your-github-pat> `
        webhookSecret=<your-secret> `
        workItemType=Issue
```

### Retrieve the Webhook URL

If you lose the webhook URL, retrieve it from the Azure Portal:

1. Go to **Azure Portal** → **Logic Apps** → your Logic App
2. Click **Logic App Designer**
3. Click the **When a HTTP request is received** trigger
4. Copy the **HTTP POST URL**

---

## Step 3: Configure GitHub Webhooks

### Option A: Scripted Setup (Recommended)

```powershell
.\scripts\setup-webhooks.ps1 `
    -RepoFullName "your-org/your-repo" `
    -WebhookUrl "<logic-app-trigger-url>" `
    -WebhookSecret $secret `
    -GitHubPat $ghPat
```

### Option B: Manual Setup

See [Appendix: Manual Webhook Setup](#appendix-manual-webhook-setup).

### Multi-Repository Setup

Run the webhook setup script for each repository:

```powershell
$repos = @("org/repo1", "org/repo2", "org/repo3")

foreach ($repo in $repos) {
    .\scripts\setup-webhooks.ps1 `
        -RepoFullName $repo `
        -WebhookUrl $webhookUrl `
        -WebhookSecret $secret `
        -GitHubPat $ghPat
}
```

---

## Step 4: Verify the Integration

### Check Webhook Delivery

1. Navigate to `https://github.com/{owner}/{repo}/settings/hooks`
2. Click on the webhook
3. Go to **Recent Deliveries**
4. Look for a `ping` event with a **200** or **202** response

### Trigger a Test Alert

The easiest way to test is to commit a known vulnerable pattern:

**Code Scanning (CodeQL):**
```python
# test_vuln.py — DO NOT MERGE, for testing only
import subprocess
user_input = input("Enter command: ")
subprocess.call(user_input, shell=True)  # CodeQL: py/shell-command-injection
```

**Dependabot:**
Add a known vulnerable dependency to your manifest file.

**Secret Scanning:**
Commit a test secret pattern (e.g., a fake AWS key format).

### Verify in ADO

1. Go to your ADO project → **Boards** → **Work Items**
2. Search for tag: `GHAS`
3. Verify the work item was created with correct metadata

### Check Logic App Run History

1. Azure Portal → Logic Apps → your Logic App
2. Click **Runs history**
3. Click on a run to see detailed execution with inputs/outputs for each action

---

## Step 5: Production Hardening

### Use Azure Key Vault for Secrets

Instead of passing PATs directly, store them in Key Vault:

```powershell
# Create Key Vault
az keyvault create --name kv-ghas-ado --resource-group rg-ghas-ado-sync --location eastus

# Store secrets
az keyvault secret set --vault-name kv-ghas-ado --name ado-pat --value "<your-ado-pat>"
az keyvault secret set --vault-name kv-ghas-ado --name github-pat --value "<your-github-pat>"
az keyvault secret set --vault-name kv-ghas-ado --name webhook-secret --value "<your-secret>"
```

Then reference Key Vault secrets in the Bicep parameters file.

### Set Up Monitoring & Alerts

Configure Azure Monitor alerts for Logic App failures:

```powershell
az monitor metrics alert create `
    --name "ghas-ado-sync-failures" `
    --resource-group rg-ghas-ado-sync `
    --scopes "/subscriptions/{sub}/resourceGroups/rg-ghas-ado-sync/providers/Microsoft.Logic/workflows/{logic-app-name}" `
    --condition "total RunsFailed > 0" `
    --window-size 5m `
    --action-group "/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Insights/actionGroups/{ag}"
```

### PAT Rotation Schedule

Set calendar reminders to rotate PATs before expiration:

| Secret | Location | Rotation |
|---|---|---|
| ADO PAT | Logic App parameters | Every 90 days |
| GitHub PAT | Logic App parameters + webhook config | Every 90 days |
| Webhook Secret | Logic App parameters + GitHub webhook | As needed |

---

## Appendix: Manual Webhook Setup

1. Go to `https://github.com/{owner}/{repo}/settings/hooks`
2. Click **Add webhook**
3. Configure:
   - **Payload URL**: Paste the Logic App trigger URL
   - **Content type**: `application/json`
   - **Secret**: Enter the webhook secret
   - **SSL verification**: Enable
4. Under **Which events would you like to trigger this webhook?**
   - Select **Let me select individual events**
   - Check:
     - ✅ Code scanning alerts
     - ✅ Dependabot alerts
     - ✅ Secret scanning alerts
   - Uncheck all other events
5. Ensure **Active** is checked
6. Click **Add webhook**

---

## Appendix: ADO Process Templates

The auto-close feature transitions work items to the "Closed" state. This works for:

| Process Template | Work Item Type | Valid Close State |
|---|---|---|
| Agile | Issue | Closed ✓ |
| Agile | Bug | Closed ✓ |
| Scrum | Issue | Done (change needed) |
| Scrum | Bug | Done (change needed) |
| CMMI | Issue | Closed ✓ |
| Basic | Issue | Done (change needed) |

If your process uses "Done" instead of "Closed", update the `HTTP_CloseWorkItem` action in `infra/workflows/ghas-to-ado.json`:

```json
{
  "op": "add",
  "path": "/fields/System.State",
  "value": "Done"
}
```

---

## Appendix: Finding Work Items from GHAS

Each work item is tagged with a unique identifier: `GHAS-{owner}-{repo}-{alert_number}`

To find the ADO work item for a specific GHAS alert:

1. Note the alert number from the GHAS alert URL (e.g., `/security/code-scanning/42`)
2. In ADO, search work items with the tag: `GHAS-owner-repo-42`
3. Or use this WIQL query in ADO:
   ```
   SELECT [System.Id], [System.Title], [System.State]
   FROM WorkItems
   WHERE [System.Tags] CONTAINS 'GHAS-owner-repo-42'
   ```

The work item's description also contains a direct hyperlink back to the GHAS alert.
