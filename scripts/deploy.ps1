<#
.SYNOPSIS
    Deploys the GHAS-ADO Sync Logic App to Azure.

.DESCRIPTION
    Creates a resource group (if needed) and deploys the Bicep templates
    that provision the Logic App for syncing GitHub Advanced Security
    alerts to Azure DevOps work items.

.PARAMETER ResourceGroupName
    Name of the Azure resource group to create/use.

.PARAMETER Location
    Azure region for the resource group and resources.

.PARAMETER AdoOrganization
    Azure DevOps organization name (e.g. "myorg").

.PARAMETER AdoProject
    Azure DevOps project name.

.PARAMETER AdoPat
    Azure DevOps PAT with "Work Items: Read & Write" scope.

.PARAMETER GitHubPat
    GitHub PAT with "security_events" scope.

.PARAMETER WebhookSecret
    Shared secret for GitHub webhook HMAC-SHA256 validation.

.PARAMETER WorkItemType
    ADO work item type to create. Default: "Issue".

.EXAMPLE
    .\deploy.ps1 -ResourceGroupName "rg-ghas-ado" -Location "eastus" `
        -AdoOrganization "myorg" -AdoProject "MyProject" `
        -AdoPat $adoPat -GitHubPat $ghPat -WebhookSecret $secret
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ResourceGroupName,

    [Parameter(Mandatory)]
    [string]$Location,

    [Parameter(Mandatory)]
    [string]$AdoOrganization,

    [Parameter(Mandatory)]
    [string]$AdoProject,

    [Parameter(Mandatory)]
    [SecureString]$AdoPat,

    [Parameter(Mandatory)]
    [SecureString]$GitHubPat,

    [Parameter(Mandatory)]
    [SecureString]$WebhookSecret,

    [string]$WorkItemType = "Issue"
)

$ErrorActionPreference = "Stop"

# Convert SecureStrings to plain text for Bicep parameters
$adoPatPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($AdoPat)
)
$githubPatPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($GitHubPat)
)
$webhookSecretPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($WebhookSecret)
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " GHAS-ADO Sync - Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify Azure CLI is logged in
Write-Host "[1/4] Verifying Azure CLI login..." -ForegroundColor Yellow
try {
    $account = az account show 2>&1 | ConvertFrom-Json
    Write-Host "  Logged in as: $($account.user.name)" -ForegroundColor Green
    Write-Host "  Subscription: $($account.name) ($($account.id))" -ForegroundColor Green
}
catch {
    Write-Error "Not logged in to Azure CLI. Run 'az login' first."
    exit 1
}

# Step 2: Create resource group
Write-Host ""
Write-Host "[2/4] Creating resource group '$ResourceGroupName' in '$Location'..." -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location --output none
Write-Host "  Resource group ready." -ForegroundColor Green

# Step 3: Deploy Bicep template
Write-Host ""
Write-Host "[3/4] Deploying Bicep templates..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$templateFile = Join-Path $scriptDir "..\infra\main.bicep"

$deploymentOutput = az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file $templateFile `
    --parameters `
        adoOrganization=$AdoOrganization `
        adoProject=$AdoProject `
        adoPat=$adoPatPlain `
        githubPat=$githubPatPlain `
        webhookSecret=$webhookSecretPlain `
        workItemType=$WorkItemType `
    --output json 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployment failed:`n$deploymentOutput"
    exit 1
}

$deployment = $deploymentOutput | ConvertFrom-Json
Write-Host "  Deployment succeeded." -ForegroundColor Green

# Step 4: Extract outputs
Write-Host ""
Write-Host "[4/4] Extracting deployment outputs..." -ForegroundColor Yellow

$callbackUrl = $deployment.properties.outputs.logicAppCallbackUrl.value
$logicAppName = $deployment.properties.outputs.logicAppName.value

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Logic App Name:  $logicAppName" -ForegroundColor White
Write-Host ""
Write-Host "Webhook URL (use this in GitHub):" -ForegroundColor White
Write-Host "  $callbackUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Copy the webhook URL above"
Write-Host "  2. Run setup-webhooks.ps1 to configure GitHub webhooks:"
Write-Host "     .\setup-webhooks.ps1 -RepoFullName 'owner/repo' -WebhookUrl '<url>' -WebhookSecret <secret>"
Write-Host "  3. Or manually add the webhook in GitHub repo Settings > Webhooks"
Write-Host ""
