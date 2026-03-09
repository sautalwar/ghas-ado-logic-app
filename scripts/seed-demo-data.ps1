<#
.SYNOPSIS
    Seeds Azure DevOps with sample Learfield demo data.

.DESCRIPTION
    Populates the brandsafway1/brandsafway_Engg ADO project with:
    - Git repositories (4 Learfield-themed repos with initial commits)
    - Iterations/Sprints (3 sprints)
    - Work items: Epics, Features, User Stories, Tasks, Bugs
    - Test Plans with Test Suites and Test Cases
    - Pipeline YAML definitions (pushed to repos)

.PARAMETER AdoPat
    Azure DevOps PAT with Full Access scope (needed for repos, work items,
    pipelines, and test plans).

.EXAMPLE
    $pat = Read-Host -AsSecureString "ADO PAT"
    .\seed-demo-data.ps1 -AdoPat $pat
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [SecureString]$AdoPat
)

$ErrorActionPreference = "Stop"

$org = "brandsafway1"
$project = "brandsafway_Engg"
$baseUrl = "https://dev.azure.com/$org"

$patPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($AdoPat)
)
$authHeader = @{
    "Authorization" = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$patPlain"))
    "Content-Type"  = "application/json"
}
$patchHeader = @{
    "Authorization" = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(":$patPlain"))
    "Content-Type"  = "application/json-patch+json"
}

function Invoke-AdoApi {
    param(
        [string]$Uri,
        [string]$Method = "GET",
        [object]$Body,
        [hashtable]$Headers = $authHeader,
        [switch]$IgnoreError
    )
    $params = @{
        Uri     = $Uri
        Method  = $Method
        Headers = $Headers
    }
    if ($Body) {
        if ($Body -is [string]) {
            $params.Body = $Body
        } else {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
    }
    try {
        Invoke-RestMethod @params
    }
    catch {
        if (-not $IgnoreError) {
            $status = $_.Exception.Response.StatusCode.value__
            $detail = $_.ErrorDetails.Message
            Write-Warning "API call failed ($status): $detail"
        }
        $null
    }
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Learfield Demo - ADO Data Seeder           ║" -ForegroundColor Cyan
Write-Host "║   Org: $org                          ║" -ForegroundColor Cyan
Write-Host "║   Project: $project                ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ──────────────────────────────────────────────
# 1. CREATE REPOSITORIES
# ──────────────────────────────────────────────
Write-Host "━━━ [1/6] Creating Repositories ━━━" -ForegroundColor Yellow

$repos = @(
    @{ name = "learfield-fan-portal";    desc = "Fan engagement web portal - React/Next.js frontend" }
    @{ name = "learfield-analytics-api"; desc = "Analytics and reporting API - .NET 8 Web API" }
    @{ name = "learfield-mobile-app";    desc = "Mobile companion app - React Native" }
    @{ name = "learfield-content-cms";   desc = "Content management system - Node.js/Express" }
)

$createdRepos = @{}
foreach ($repo in $repos) {
    $result = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/git/repositories?api-version=7.1" -Method POST -Body @{
        name = $repo.name
    } -IgnoreError
    if ($result) {
        $createdRepos[$repo.name] = $result.id
        Write-Host "  ✓ Created repo: $($repo.name)" -ForegroundColor Green
    } else {
        # Try to get existing repo
        $existing = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/git/repositories/$($repo.name)?api-version=7.1" -IgnoreError
        if ($existing) {
            $createdRepos[$repo.name] = $existing.id
            Write-Host "  ○ Repo already exists: $($repo.name)" -ForegroundColor DarkGray
        }
    }
}

# Push initial README to each repo
foreach ($repo in $repos) {
    $repoId = $createdRepos[$repo.name]
    if (-not $repoId) { continue }

    $readmeContent = @"
# $($repo.name)

$($repo.desc)

## Learfield Digital Platform

This repository is part of the Learfield digital platform ecosystem.

### Getting Started

See the project wiki for setup instructions.

### Contributing

Please follow the branching strategy defined in the project guidelines.
"@

    $encodedContent = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($readmeContent))

    $pushBody = @{
        refUpdates = @(
            @{
                name        = "refs/heads/main"
                oldObjectId = "0000000000000000000000000000000000000000"
            }
        )
        commits = @(
            @{
                comment = "Initial commit - project scaffolding"
                changes = @(
                    @{
                        changeType = "add"
                        item       = @{ path = "/README.md" }
                        newContent = @{
                            content     = $encodedContent
                            contentType = "base64encoded"
                        }
                    }
                )
            }
        )
    }

    $pushResult = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/git/repositories/$repoId/pushes?api-version=7.1" -Method POST -Body $pushBody -IgnoreError
    if ($pushResult) {
        Write-Host "  ✓ Pushed initial commit to $($repo.name)" -ForegroundColor Green
    }
}

# ──────────────────────────────────────────────
# 2. CREATE ITERATIONS / SPRINTS
# ──────────────────────────────────────────────
Write-Host ""
Write-Host "━━━ [2/6] Creating Sprints ━━━" -ForegroundColor Yellow

$today = Get-Date
$sprints = @(
    @{
        name       = "Sprint 25.1 - Platform Foundation"
        startDate  = $today.AddDays(-14).ToString("yyyy-MM-ddT00:00:00Z")
        finishDate = $today.AddDays(-1).ToString("yyyy-MM-ddT23:59:59Z")
    }
    @{
        name       = "Sprint 25.2 - Fan Engagement"
        startDate  = $today.ToString("yyyy-MM-ddT00:00:00Z")
        finishDate = $today.AddDays(13).ToString("yyyy-MM-ddT23:59:59Z")
    }
    @{
        name       = "Sprint 25.3 - Analytics & NIL"
        startDate  = $today.AddDays(14).ToString("yyyy-MM-ddT00:00:00Z")
        finishDate = $today.AddDays(27).ToString("yyyy-MM-ddT23:59:59Z")
    }
)

foreach ($sprint in $sprints) {
    $result = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/wit/classificationnodes/iterations?api-version=7.1" -Method POST -Body @{
        name       = $sprint.name
        attributes = @{
            startDate  = $sprint.startDate
            finishDate = $sprint.finishDate
        }
    } -IgnoreError
    if ($result) {
        Write-Host "  ✓ Created sprint: $($sprint.name)" -ForegroundColor Green
    } else {
        Write-Host "  ○ Sprint may already exist: $($sprint.name)" -ForegroundColor DarkGray
    }
}

# ──────────────────────────────────────────────
# 3. CREATE WORK ITEMS (BACKLOG)
# ──────────────────────────────────────────────
Write-Host ""
Write-Host "━━━ [3/6] Creating Work Items ━━━" -ForegroundColor Yellow

function New-WorkItem {
    param(
        [string]$Type,
        [string]$Title,
        [string]$Description = "",
        [string]$State = "New",
        [string]$IterationPath = "",
        [string]$Tags = "",
        [int]$ParentId = 0,
        [string]$Priority = "",
        [string]$Severity = "",
        [string]$AssignedTo = ""
    )

    $fields = @(
        @{ op = "add"; path = "/fields/System.Title"; value = $Title }
    )
    if ($Description) {
        $fields += @{ op = "add"; path = "/fields/System.Description"; value = $Description }
    }
    if ($State -and $State -ne "New") {
        $fields += @{ op = "add"; path = "/fields/System.State"; value = $State }
    }
    if ($IterationPath) {
        $fields += @{ op = "add"; path = "/fields/System.IterationPath"; value = "$project\$IterationPath" }
    }
    if ($Tags) {
        $fields += @{ op = "add"; path = "/fields/System.Tags"; value = $Tags }
    }
    if ($Priority) {
        $fields += @{ op = "add"; path = "/fields/Microsoft.VSTS.Common.Priority"; value = [int]$Priority }
    }
    if ($ParentId -gt 0) {
        $fields += @{
            op    = "add"
            path  = "/relations/-"
            value = @{
                rel = "System.LinkTypes.Hierarchy-Reverse"
                url = "$baseUrl/$project/_apis/wit/workitems/$ParentId"
            }
        }
    }

    $body = $fields | ConvertTo-Json -Depth 5
    $result = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/wit/workitems/`$$($Type)?api-version=7.1" -Method PATCH -Body $body -Headers $patchHeader -IgnoreError
    if ($result) {
        Write-Host "  ✓ [$Type] $Title (ID: $($result.id))" -ForegroundColor Green
        return $result.id
    } else {
        Write-Host "  ✗ Failed to create [$Type] $Title" -ForegroundColor Red
        return 0
    }
}

# --- EPIC 1: Fan Engagement Platform ---
$epic1 = New-WorkItem -Type "Epic" -Title "Fan Engagement Platform" `
    -Description "<h3>Learfield Fan Engagement Platform</h3><p>Build a comprehensive digital fan engagement platform for collegiate athletics programs. Enable real-time interaction during game days, personalized content delivery, and integrated NIL marketplace.</p><p><b>Key Outcomes:</b></p><ul><li>Increase fan engagement by 40%</li><li>Drive sponsorship revenue through digital channels</li><li>Support NIL athlete marketplace</li></ul>" `
    -Tags "Learfield; Platform; Q1-2025" -Priority "1"

$feat1 = New-WorkItem -Type "Feature" -Title "Live Game Day Experience" `
    -Description "Real-time fan experience during game days including live stats, polls, trivia, and social feeds." `
    -ParentId $epic1 -Tags "GameDay; Fan-Experience" -Priority "1" `
    -IterationPath "Sprint 25.2 - Fan Engagement"

$story1 = New-WorkItem -Type "User Story" -Title "As a fan, I can view real-time game stats on the portal" `
    -Description "<p>Real-time statistics feed integrated with official NCAA data provider. Stats include score, possession, player stats, and play-by-play.</p><p><b>Acceptance Criteria:</b></p><ul><li>Stats update within 5 seconds of live action</li><li>Support football, basketball, and baseball</li><li>Mobile-responsive layout</li></ul>" `
    -ParentId $feat1 -Tags "GameDay; Stats; Frontend" -Priority "1" `
    -IterationPath "Sprint 25.2 - Fan Engagement" -State "Active"

$task1 = New-WorkItem -Type "Task" -Title "Integrate NCAA stats API endpoint" `
    -ParentId $story1 -Tags "API; Integration" -Priority "1" `
    -IterationPath "Sprint 25.2 - Fan Engagement" -State "Active"

$task2 = New-WorkItem -Type "Task" -Title "Build real-time stats React component" `
    -ParentId $story1 -Tags "Frontend; React" -Priority "1" `
    -IterationPath "Sprint 25.2 - Fan Engagement"

$task3 = New-WorkItem -Type "Task" -Title "Implement WebSocket connection for live updates" `
    -ParentId $story1 -Tags "Backend; WebSocket" -Priority "2" `
    -IterationPath "Sprint 25.2 - Fan Engagement"

$story2 = New-WorkItem -Type "User Story" -Title "As a fan, I can participate in live polls during games" `
    -Description "<p>Interactive polling system that allows fans to vote on game predictions, MVP picks, and sponsor-branded questions.</p><p><b>Acceptance Criteria:</b></p><ul><li>Polls appear in real-time during game events</li><li>Results animate live as votes come in</li><li>Sponsors can brand poll questions</li></ul>" `
    -ParentId $feat1 -Tags "GameDay; Polls; Interactive" -Priority "2" `
    -IterationPath "Sprint 25.2 - Fan Engagement"

$story3 = New-WorkItem -Type "User Story" -Title "As a fan, I can earn points for game day engagement" `
    -Description "Gamification system rewarding fans for attending games, participating in polls, and sharing content." `
    -ParentId $feat1 -Tags "Gamification; Loyalty" -Priority "3" `
    -IterationPath "Sprint 25.3 - Analytics & NIL"

$feat2 = New-WorkItem -Type "Feature" -Title "NIL Athlete Marketplace" `
    -Description "Name, Image, and Likeness marketplace connecting athletes with fans and brands for merchandise, autographs, and experiences." `
    -ParentId $epic1 -Tags "NIL; Marketplace" -Priority "2" `
    -IterationPath "Sprint 25.3 - Analytics & NIL"

$story4 = New-WorkItem -Type "User Story" -Title "As an athlete, I can create and manage my NIL profile" `
    -Description "<p>Athletes can set up profiles with bio, photos, social links, and available NIL offerings (merch, appearances, shoutouts).</p>" `
    -ParentId $feat2 -Tags "NIL; Profile; Athletes" -Priority "1" `
    -IterationPath "Sprint 25.3 - Analytics & NIL"

$story5 = New-WorkItem -Type "User Story" -Title "As a fan, I can browse and purchase athlete merchandise" `
    -Description "E-commerce integration for fans to discover and purchase athlete-branded merchandise through the NIL marketplace." `
    -ParentId $feat2 -Tags "NIL; E-Commerce; Fans" -Priority "2" `
    -IterationPath "Sprint 25.3 - Analytics & NIL"

$feat3 = New-WorkItem -Type "Feature" -Title "Fan Authentication & Profile" `
    -Description "Single sign-on authentication with university credentials and social logins. Fan profiles with preferences and engagement history." `
    -ParentId $epic1 -Tags "Auth; Identity" -Priority "1" `
    -IterationPath "Sprint 25.1 - Platform Foundation"

$story6 = New-WorkItem -Type "User Story" -Title "As a fan, I can sign in with my university email or social account" `
    -Description "OAuth 2.0 / OIDC integration with Azure AD B2C supporting Google, Apple, and university SSO." `
    -ParentId $feat3 -Tags "Auth; SSO; Azure-AD-B2C" -Priority "1" `
    -IterationPath "Sprint 25.1 - Platform Foundation" -State "Closed"

$story7 = New-WorkItem -Type "User Story" -Title "As a fan, I can set my favorite teams and notification preferences" `
    -Description "Profile settings page where fans select their favorite school(s), sport(s), and opt into push/email notifications." `
    -ParentId $feat3 -Tags "Profile; Notifications" -Priority "2" `
    -IterationPath "Sprint 25.1 - Platform Foundation" -State "Closed"

# --- EPIC 2: Analytics & Reporting ---
$epic2 = New-WorkItem -Type "Epic" -Title "Analytics & Sponsorship Intelligence" `
    -Description "<h3>Analytics & Sponsorship Intelligence Platform</h3><p>Data-driven insights for sponsorship performance, fan engagement metrics, and revenue attribution. Enable sponsors to see real-time ROI on their collegiate sports investments.</p>" `
    -Tags "Learfield; Analytics; Sponsorship" -Priority "1"

$feat4 = New-WorkItem -Type "Feature" -Title "Sponsorship ROI Dashboard" `
    -Description "Interactive dashboard showing sponsorship performance metrics: impressions, engagement rates, conversion attribution, and revenue impact." `
    -ParentId $epic2 -Tags "Analytics; Dashboard; Sponsors" -Priority "1" `
    -IterationPath "Sprint 25.2 - Fan Engagement"

$story8 = New-WorkItem -Type "User Story" -Title "As a sponsor, I can view campaign performance metrics in real-time" `
    -Description "<p>Dashboard with KPIs: impressions, click-through rates, engagement score, and estimated revenue impact.</p><p><b>Data Sources:</b> Ad server, fan portal analytics, social media APIs</p>" `
    -ParentId $feat4 -Tags "Analytics; Dashboard; KPIs" -Priority "1" `
    -IterationPath "Sprint 25.2 - Fan Engagement" -State "Active"

$story9 = New-WorkItem -Type "User Story" -Title "As a sponsor, I can export performance reports as PDF" `
    -Description "Generate branded PDF reports with charts, tables, and executive summary for sponsor stakeholder meetings." `
    -ParentId $feat4 -Tags "Analytics; Reports; Export" -Priority "2" `
    -IterationPath "Sprint 25.3 - Analytics & NIL"

$feat5 = New-WorkItem -Type "Feature" -Title "Fan Engagement Analytics" `
    -Description "Track and analyze fan behavior across all digital touchpoints: portal visits, app usage, poll participation, and content consumption." `
    -ParentId $epic2 -Tags "Analytics; Fan-Data" -Priority "2" `
    -IterationPath "Sprint 25.3 - Analytics & NIL"

$story10 = New-WorkItem -Type "User Story" -Title "As an admin, I can view fan engagement heatmaps by event" `
    -Description "Visual heatmap showing fan engagement intensity across game events, time of day, and content type." `
    -ParentId $feat5 -Tags "Analytics; Heatmap; Visualization" -Priority "2" `
    -IterationPath "Sprint 25.3 - Analytics & NIL"

# --- EPIC 3: Platform Infrastructure ---
$epic3 = New-WorkItem -Type "Epic" -Title "Platform Infrastructure & DevOps" `
    -Description "<h3>Cloud Infrastructure & DevOps</h3><p>Azure-based infrastructure, CI/CD pipelines, monitoring, and security hardening for the Learfield digital platform.</p>" `
    -Tags "Learfield; Infrastructure; DevOps" -Priority "1"

$feat6 = New-WorkItem -Type "Feature" -Title "CI/CD Pipeline Setup" `
    -Description "Automated build, test, and deployment pipelines for all platform services using Azure DevOps Pipelines." `
    -ParentId $epic3 -Tags "DevOps; CI-CD; Pipelines" -Priority "1" `
    -IterationPath "Sprint 25.1 - Platform Foundation"

$story11 = New-WorkItem -Type "User Story" -Title "As a developer, I have automated CI/CD for the fan portal" `
    -Description "Azure DevOps pipeline with build, lint, test, and deploy stages. Auto-deploy to staging on PR merge, manual approval for production." `
    -ParentId $feat6 -Tags "DevOps; CI-CD; Fan-Portal" -Priority "1" `
    -IterationPath "Sprint 25.1 - Platform Foundation" -State "Closed"

$feat7 = New-WorkItem -Type "Feature" -Title "Security & GHAS Integration" `
    -Description "GitHub Advanced Security integration with automated vulnerability tracking in ADO. Code scanning, dependency scanning, and secret scanning." `
    -ParentId $epic3 -Tags "Security; GHAS; Compliance" -Priority "1" `
    -IterationPath "Sprint 25.2 - Fan Engagement"

$story12 = New-WorkItem -Type "User Story" -Title "As a security engineer, vulnerabilities auto-create ADO work items" `
    -Description "<p>GHAS alerts (code scanning, Dependabot, secret scanning) automatically create work items in ADO with full context. Work items auto-close when vulnerabilities are resolved.</p><p><b>This is the GHAS-ADO Sync Logic App!</b></p>" `
    -ParentId $feat7 -Tags "Security; GHAS; Automation; GHAS-ADO-Sync" -Priority "1" `
    -IterationPath "Sprint 25.2 - Fan Engagement" -State "Active"

# --- BUGS ---
$bug1 = New-WorkItem -Type "Bug" -Title "Dashboard charts fail to render on Safari 17" `
    -Description "<p><b>Steps to Reproduce:</b></p><ol><li>Open sponsorship dashboard in Safari 17</li><li>Navigate to Campaign Performance tab</li><li>Charts show blank white area</li></ol><p><b>Expected:</b> Charts render correctly</p><p><b>Actual:</b> Blank area, console error: 'ResizeObserver loop limit exceeded'</p>" `
    -Tags "Bug; Safari; Dashboard" -Priority "2" `
    -IterationPath "Sprint 25.2 - Fan Engagement"

$bug2 = New-WorkItem -Type "Bug" -Title "Push notifications not delivered on Android 14+" `
    -Description "<p><b>Impact:</b> ~30% of mobile users not receiving game day notifications.</p><p><b>Root Cause:</b> Firebase Cloud Messaging requires updated notification channel configuration for Android 14.</p>" `
    -Tags "Bug; Mobile; Notifications; Android" -Priority "1" `
    -IterationPath "Sprint 25.2 - Fan Engagement" -State "Active"

$bug3 = New-WorkItem -Type "Bug" -Title "Memory leak in WebSocket connection handler" `
    -Description "<p>Fan portal stats page leaks ~2MB/minute when WebSocket reconnects. After 30 minutes, page becomes unresponsive.</p><p><b>Investigation:</b> Event listeners not cleaned up on reconnect.</p>" `
    -Tags "Bug; Performance; WebSocket" -Priority "1" `
    -IterationPath "Sprint 25.2 - Fan Engagement"

# ──────────────────────────────────────────────
# 4. PUSH PIPELINE YAML TO REPOS
# ──────────────────────────────────────────────
Write-Host ""
Write-Host "━━━ [4/6] Creating Pipeline YAML Files ━━━" -ForegroundColor Yellow

$ciYaml = @"
trigger:
  branches:
    include:
      - main
      - develop
  paths:
    exclude:
      - '*.md'
      - docs/**

pool:
  vmImage: 'ubuntu-latest'

variables:
  nodeVersion: '20.x'

stages:
  - stage: Build
    displayName: 'Build & Test'
    jobs:
      - job: BuildJob
        displayName: 'Build Application'
        steps:
          - task: NodeTool@0
            inputs:
              versionSpec: `$(nodeVersion)
            displayName: 'Install Node.js'

          - script: npm ci
            displayName: 'Install dependencies'

          - script: npm run lint
            displayName: 'Run linter'

          - script: npm run test -- --coverage
            displayName: 'Run tests'

          - script: npm run build
            displayName: 'Build application'

          - task: PublishTestResults@2
            inputs:
              testResultsFormat: 'JUnit'
              testResultsFiles: '**/junit.xml'
            condition: always()
            displayName: 'Publish test results'

  - stage: DeployStaging
    displayName: 'Deploy to Staging'
    dependsOn: Build
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployStaging
        displayName: 'Deploy to Staging'
        environment: 'staging'
        strategy:
          runOnce:
            deploy:
              steps:
                - script: echo 'Deploying to staging...'
                  displayName: 'Deploy to Azure App Service (Staging)'
"@

$cdYaml = @"
trigger: none

resources:
  pipelines:
    - pipeline: ci
      source: 'learfield-analytics-api-ci'
      trigger:
        branches:
          include:
            - main

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: DeployProd
    displayName: 'Deploy to Production'
    jobs:
      - deployment: DeployProduction
        displayName: 'Production Deployment'
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - script: echo 'Deploying analytics API to production...'
                  displayName: 'Deploy to Azure Container Apps'
"@

# Push CI YAML to fan-portal repo
$fanPortalRepoId = $createdRepos["learfield-fan-portal"]
if ($fanPortalRepoId) {
    $refs = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/git/repositories/$fanPortalRepoId/refs?filter=heads/main&api-version=7.1" -IgnoreError
    $mainSha = $refs.value[0].objectId
    if ($mainSha) {
        $encodedCi = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($ciYaml))
        $pushBody = @{
            refUpdates = @(@{ name = "refs/heads/main"; oldObjectId = $mainSha })
            commits = @(@{
                comment = "Add CI/CD pipeline definition"
                changes = @(@{
                    changeType = "add"
                    item       = @{ path = "/azure-pipelines.yml" }
                    newContent = @{ content = $encodedCi; contentType = "base64encoded" }
                })
            })
        }
        $result = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/git/repositories/$fanPortalRepoId/pushes?api-version=7.1" -Method POST -Body $pushBody -IgnoreError
        if ($result) {
            Write-Host "  ✓ Pushed azure-pipelines.yml to learfield-fan-portal" -ForegroundColor Green
        }
    }
}

# Push CD YAML to analytics-api repo
$analyticsRepoId = $createdRepos["learfield-analytics-api"]
if ($analyticsRepoId) {
    $refs = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/git/repositories/$analyticsRepoId/refs?filter=heads/main&api-version=7.1" -IgnoreError
    $mainSha = $refs.value[0].objectId
    if ($mainSha) {
        $encodedCd = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($cdYaml))
        $pushBody = @{
            refUpdates = @(@{ name = "refs/heads/main"; oldObjectId = $mainSha })
            commits = @(@{
                comment = "Add release pipeline definition"
                changes = @(@{
                    changeType = "add"
                    item       = @{ path = "/azure-pipelines-release.yml" }
                    newContent = @{ content = $encodedCd; contentType = "base64encoded" }
                })
            })
        }
        $result = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/git/repositories/$analyticsRepoId/pushes?api-version=7.1" -Method POST -Body $pushBody -IgnoreError
        if ($result) {
            Write-Host "  ✓ Pushed azure-pipelines-release.yml to learfield-analytics-api" -ForegroundColor Green
        }
    }
}

# ──────────────────────────────────────────────
# 5. CREATE PIPELINES
# ──────────────────────────────────────────────
Write-Host ""
Write-Host "━━━ [5/6] Registering Pipelines ━━━" -ForegroundColor Yellow

if ($fanPortalRepoId) {
    $result = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/pipelines?api-version=7.1" -Method POST -Body @{
        name          = "learfield-fan-portal-ci"
        folder        = "\\"
        configuration = @{
            type       = "yaml"
            path       = "/azure-pipelines.yml"
            repository = @{
                id   = $fanPortalRepoId
                type = "azureReposGit"
            }
        }
    } -IgnoreError
    if ($result) {
        Write-Host "  ✓ Created pipeline: learfield-fan-portal-ci" -ForegroundColor Green
    } else {
        Write-Host "  ○ Pipeline may already exist: learfield-fan-portal-ci" -ForegroundColor DarkGray
    }
}

if ($analyticsRepoId) {
    $result = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/pipelines?api-version=7.1" -Method POST -Body @{
        name          = "learfield-analytics-api-release"
        folder        = "\\"
        configuration = @{
            type       = "yaml"
            path       = "/azure-pipelines-release.yml"
            repository = @{
                id   = $analyticsRepoId
                type = "azureReposGit"
            }
        }
    } -IgnoreError
    if ($result) {
        Write-Host "  ✓ Created pipeline: learfield-analytics-api-release" -ForegroundColor Green
    } else {
        Write-Host "  ○ Pipeline may already exist: learfield-analytics-api-release" -ForegroundColor DarkGray
    }
}

# ──────────────────────────────────────────────
# 6. CREATE TEST PLANS
# ──────────────────────────────────────────────
Write-Host ""
Write-Host "━━━ [6/6] Creating Test Plans ━━━" -ForegroundColor Yellow

# Create Test Plan
$testPlan = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/testplan/plans?api-version=7.1" -Method POST -Body @{
    name        = "Fan Portal Regression Tests"
    description = "Comprehensive regression test suite for the Learfield fan engagement portal."
    iteration   = "$project"
} -IgnoreError

if ($testPlan) {
    Write-Host "  ✓ Created test plan: Fan Portal Regression Tests (ID: $($testPlan.id))" -ForegroundColor Green
    $planId = $testPlan.id

    # Get the root suite ID
    $rootSuiteId = $testPlan.rootSuite.id

    # Create Test Suites
    $authSuite = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/testplan/Plans/$planId/suites?api-version=7.1" -Method POST -Body @{
        suiteType = "staticTestSuite"
        name      = "Authentication Tests"
        parentSuite = @{ id = $rootSuiteId }
    } -IgnoreError
    if ($authSuite) {
        Write-Host "  ✓ Created test suite: Authentication Tests" -ForegroundColor Green
    }

    $gameDaySuite = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/testplan/Plans/$planId/suites?api-version=7.1" -Method POST -Body @{
        suiteType = "staticTestSuite"
        name      = "Game Day Features"
        parentSuite = @{ id = $rootSuiteId }
    } -IgnoreError
    if ($gameDaySuite) {
        Write-Host "  ✓ Created test suite: Game Day Features" -ForegroundColor Green
    }

    $perfSuite = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/testplan/Plans/$planId/suites?api-version=7.1" -Method POST -Body @{
        suiteType = "staticTestSuite"
        name      = "Performance Tests"
        parentSuite = @{ id = $rootSuiteId }
    } -IgnoreError
    if ($perfSuite) {
        Write-Host "  ✓ Created test suite: Performance Tests" -ForegroundColor Green
    }

    # Create Test Cases (as work items) and add to suites
    $testCases = @(
        @{ title = "Verify SSO login with university email"; suite = $authSuite }
        @{ title = "Verify Google OAuth sign-in flow"; suite = $authSuite }
        @{ title = "Verify session timeout after 30 minutes of inactivity"; suite = $authSuite }
        @{ title = "Verify password reset email delivery"; suite = $authSuite }
        @{ title = "Verify real-time stats update within 5 seconds"; suite = $gameDaySuite }
        @{ title = "Verify live poll creation and voting"; suite = $gameDaySuite }
        @{ title = "Verify poll results animate in real-time"; suite = $gameDaySuite }
        @{ title = "Verify game day notifications are sent"; suite = $gameDaySuite }
        @{ title = "Verify fan points are awarded for poll participation"; suite = $gameDaySuite }
        @{ title = "Verify portal loads within 2 seconds on 3G"; suite = $perfSuite }
        @{ title = "Verify WebSocket reconnects gracefully"; suite = $perfSuite }
        @{ title = "Verify no memory leaks after 1 hour of usage"; suite = $perfSuite }
    )

    foreach ($tc in $testCases) {
        $tcBody = @(
            @{ op = "add"; path = "/fields/System.Title"; value = $tc.title }
        ) | ConvertTo-Json -Depth 5

        $tcResult = Invoke-AdoApi -Uri "$baseUrl/$project/_apis/wit/workitems/`$Test Case?api-version=7.1" -Method PATCH -Body $tcBody -Headers $patchHeader -IgnoreError
        if ($tcResult -and $tc.suite) {
            Write-Host "  ✓ Created test case: $($tc.title)" -ForegroundColor Green

            # Add test case to suite
            $addBody = @(@{
                workItem = @{ id = $tcResult.id }
            }) | ConvertTo-Json -Depth 5
            Invoke-AdoApi -Uri "$baseUrl/$project/_apis/testplan/Plans/$planId/suites/$($tc.suite.id)/TestCase?api-version=7.1" -Method POST -Body $addBody -IgnoreError | Out-Null
        }
    }
} else {
    Write-Host "  ○ Test plan creation skipped (API may not be available or plan exists)" -ForegroundColor DarkGray
}

# ──────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   Demo Data Seeding Complete!                ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "What was created:" -ForegroundColor White
Write-Host "  📁 4 Repositories (with initial commits & pipeline YAML)" -ForegroundColor White
Write-Host "  🏃 3 Sprints (past, current, future)" -ForegroundColor White
Write-Host "  📋 3 Epics, 7 Features, 12 User Stories, 3 Tasks, 3 Bugs" -ForegroundColor White
Write-Host "  🔧 2 Pipeline definitions" -ForegroundColor White
Write-Host "  🧪 1 Test Plan with 3 suites and 12 test cases" -ForegroundColor White
Write-Host ""
Write-Host "View your project:" -ForegroundColor Yellow
Write-Host "  https://dev.azure.com/$org/$project" -ForegroundColor Cyan
Write-Host ""
