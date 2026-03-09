<#
.SYNOPSIS
    Configures GitHub webhooks for GHAS-ADO Sync.

.DESCRIPTION
    Uses the GitHub REST API to create a webhook on the specified
    repository that sends GHAS alert events to the Logic App.

.PARAMETER RepoFullName
    GitHub repository in "owner/repo" format.

.PARAMETER WebhookUrl
    The Logic App HTTP trigger URL (from deployment output).

.PARAMETER WebhookSecret
    Shared secret for HMAC-SHA256 payload validation.

.PARAMETER GitHubPat
    GitHub PAT with "admin:repo_hook" scope.

.EXAMPLE
    .\setup-webhooks.ps1 -RepoFullName "myorg/myrepo" `
        -WebhookUrl "https://prod-00.eastus.logic.azure.com/..." `
        -WebhookSecret $secret -GitHubPat $pat
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$RepoFullName,

    [Parameter(Mandatory)]
    [string]$WebhookUrl,

    [Parameter(Mandatory)]
    [SecureString]$WebhookSecret,

    [Parameter(Mandatory)]
    [SecureString]$GitHubPat
)

$ErrorActionPreference = "Stop"

$webhookSecretPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($WebhookSecret)
)
$githubPatPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($GitHubPat)
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " GHAS-ADO Sync - Webhook Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository: $RepoFullName" -ForegroundColor White
Write-Host ""

$headers = @{
    "Authorization" = "Bearer $githubPatPlain"
    "Accept"        = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

$body = @{
    name   = "web"
    active = $true
    events = @(
        "code_scanning_alert"
        "dependabot_alert"
        "secret_scanning_alert"
    )
    config = @{
        url          = $WebhookUrl
        content_type = "json"
        secret       = $webhookSecretPlain
        insecure_ssl = "0"
    }
} | ConvertTo-Json -Depth 4

$apiUrl = "https://api.github.com/repos/$RepoFullName/hooks"

Write-Host "[1/2] Creating webhook on $RepoFullName..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $body -ContentType "application/json"
    Write-Host "  Webhook created successfully!" -ForegroundColor Green
    Write-Host "  Webhook ID: $($response.id)" -ForegroundColor White
    Write-Host "  Events:     $($response.events -join ', ')" -ForegroundColor White
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 422) {
        Write-Host "  Webhook may already exist (HTTP 422). Check GitHub repo settings." -ForegroundColor Yellow
    }
    else {
        Write-Error "Failed to create webhook (HTTP $statusCode): $_"
        exit 1
    }
}

# Step 2: Verify webhook by sending a ping
Write-Host ""
Write-Host "[2/2] Webhook configured for events:" -ForegroundColor Yellow
Write-Host "  - code_scanning_alert  (Code Scanning / CodeQL)" -ForegroundColor White
Write-Host "  - dependabot_alert     (Dependabot)" -ForegroundColor White
Write-Host "  - secret_scanning_alert (Secret Scanning)" -ForegroundColor White

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Webhook Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "The webhook will fire when GHAS detects new vulnerabilities." -ForegroundColor White
Write-Host "To verify, check the 'Recent Deliveries' tab in:" -ForegroundColor White
Write-Host "  https://github.com/$RepoFullName/settings/hooks" -ForegroundColor Cyan
Write-Host ""
