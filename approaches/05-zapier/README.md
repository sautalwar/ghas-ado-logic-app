# Approach #5 — Zapier

> **Auto-create ADO work items from GHAzDO security alerts using Zapier**
> Phase 2c in the project's phased adoption strategy

## Overview

Zapier is a popular no-code SaaS automation platform that connects 6,000+ apps. ADO Service Hooks list **Zapier** as a native consumer — making this a first-class integration path for non-Azure-first teams.

| Dimension | Value |
|-----------|-------|
| **Setup Time** | ~45 minutes |
| **Monthly Cost** | $20–50/month (Starter/Professional) |
| **Infrastructure** | None (SaaS) |
| **Automation Level** | Full (create + close) |
| **Deduplication** | Partial (search step in multi-step Zap) |
| **Maintenance** | Minimal — Zapier handles uptime |

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **Zapier Account** | Free account to start; Starter or Professional tier needed (see Pricing) |
| **Azure DevOps** | Project with GHAzDO (Advanced Security) enabled |
| **ADO Permissions** | Project Administrator (to configure Service Hooks) |
| **ADO PAT** | Personal Access Token with `Work Items (Read & Write)` and `Work Item Search` scopes |
| **GHAzDO Alerts** | At least one repo with Advanced Security scanning enabled |

---

## Pricing

| Tier | Price | Zaps | Tasks/Month | Multi-Step | Filters | Webhooks |
|------|-------|------|-------------|-----------|---------|----------|
| **Free** | $0 | 5 | 100 | ❌ Single-step only | ❌ | ❌ |
| **Starter** | $19.99/mo | 20 | 750 | ✅ Yes | ✅ | ✅ |
| **Professional** | $49/mo | Unlimited | 2,000 | ✅ Yes | ✅ | ✅ |
| **Team** | $69/mo | Unlimited | 2,000 | ✅ Yes | ✅ | ✅ |

### Which Tier Is Needed?

**Starter ($19.99/month) is the minimum viable tier:**
- ✅ Multi-step Zaps required (webhook → parse → search → create/update)
- ✅ Webhooks by Zapier trigger (Starter+)
- ✅ Filters (to separate create vs. state-change events)
- ❌ Free tier won't work — single-step Zaps can't handle payload parsing + work item creation + dedup

**Professional ($49/month) recommended if:**
- Alert volume exceeds 750 tasks/month
- You want Autoreplay (auto-retry failed tasks)
- You need custom logic with Paths (branching)

> **Cost optimization:** Each alert cycle (create + eventual close) uses ~3-5 Zapier tasks. With 750 tasks/month on Starter, you can handle ~150-250 alert cycles per month.

---

## Implementation Steps

### Step 1: Sign Up for Zapier

1. Go to [zapier.com](https://zapier.com) and create an account
2. Start with Free tier for initial setup/testing
3. Upgrade to **Starter** before going live (required for multi-step Zaps)

### Step 2: Create Zap #1 — Alert Created → Create Work Item

This Zap handles `advancedsecurity.alert.created` events.

**Trigger:** Webhooks by Zapier → Catch Hook
1. In Zapier, click **Create Zap**
2. Search for **"Webhooks by Zapier"** as the trigger app
3. Select **"Catch Hook"** as the trigger event
4. Zapier generates a unique webhook URL (e.g., `https://hooks.zapier.com/hooks/catch/123456/abcdef/`)
5. **Copy this URL** — you'll need it for ADO Service Hooks (Step 4)
6. Click **Test trigger** — send a test payload from ADO (or use the test button in Service Hooks)

**Action 1: Filter** (Professional tier) or **Code by Zapier** (Starter tier)
- Filter to only process `advancedsecurity.alert.created` events
- Condition: `eventType` → **(Text) Contains** → `created`

**Action 2: Code by Zapier — Parse & Map Fields**
- Language: JavaScript
- Input Data: Map the raw webhook fields
- Code transforms the GHAzDO payload into ADO work item fields

**Action 3: Webhooks by Zapier — Search for Existing Work Item (Dedup)**
- Method: POST
- URL: `https://dev.azure.com/{org}/{project}/_apis/wit/wiql?api-version=7.1`
- Headers: `Content-Type: application/json`, `Authorization: Basic {base64(:PAT)}`
- Body: WIQL query searching by tag

**Action 4: Filter — Only Continue if No Existing Work Item**
- Condition: WIQL result count equals 0

**Action 5: Webhooks by Zapier — Create Work Item**
- Method: PATCH
- URL: `https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Issue?api-version=7.1`
- Headers: `Content-Type: application/json-patch+json`, `Authorization: Basic {base64(:PAT)}`
- Body: JSON patch with title, description, tags, priority

> 📋 **Detailed step-by-step:** See [`implementation/zap-create-work-item.md`](implementation/zap-create-work-item.md)

### Step 3: Create Zap #2 — Alert State Changed → Close Work Item

This Zap handles `advancedsecurity.alert.stateChanged` events where the alert is resolved/fixed.

**Trigger:** Webhooks by Zapier → Catch Hook
- Uses a **separate** webhook URL (or same URL with filtering)

**Action 1: Filter — Only Process "Fixed/Dismissed" States**
- Condition: `resource.state` equals `fixed` OR `dismissed`

**Action 2: Webhooks by Zapier — Search for Work Item by Tag**
- WIQL query: find work item with matching `GHAzDO-{repo}-{alertId}` tag

**Action 3: Filter — Only Continue if Work Item Found**

**Action 4: Webhooks by Zapier — Update Work Item State**
- PATCH to update state to Done/Closed

> 📋 **Detailed step-by-step:** See [`implementation/zap-close-work-item.md`](implementation/zap-close-work-item.md)

### Step 4: Configure ADO Service Hooks

ADO Service Hooks support two paths to Zapier:

#### Option A: Native Zapier Consumer (Recommended for Standard Events)

⚠️ **Important finding:** ADO Service Hooks' native **Zapier** consumer is limited to standard ADO events (work item created/updated, code pushed, build completed, etc.). It does **NOT** support `advancedsecurity.alert.*` events because these are newer GHAzDO-specific event types that haven't been added to the native Zapier consumer.

**Use this option only if:** You want to extend the integration later with standard ADO events.

#### Option B: Web Hooks Consumer → Zapier Catch Hook URL (Required for GHAzDO)

This is the **required path** for GHAzDO alerts:

1. In ADO, go to **Project Settings → Service Hooks**
2. Click **+ Create subscription**
3. Select **Web Hooks** as the consumer
4. Configure trigger:
   - Event: **Advanced Security alert created** (`advancedsecurity.alert.created`)
   - Repository: Select target repo (or "Any")
5. Configure action:
   - URL: Paste Zapier webhook URL from Step 2
   - HTTP headers: (none needed — Zapier accepts any JSON)
   - Resource details to send: **All**
6. Click **Test** → verify Zapier receives the payload
7. Click **Finish**

Repeat for state changes:
- Event: **Advanced Security alert state changed** (`advancedsecurity.alert.stateChanged`)
- URL: Paste Zapier webhook URL from Step 3

> 📋 **Service Hook configurations:** See [`implementation/service-hook-config.json`](implementation/service-hook-config.json)

### Step 5: Test Both Zaps

1. **Test Zap #1 (Create):**
   - Commit a known secret (e.g., `AKIA...` AWS key) to trigger a secret scanning alert
   - Verify: ADO work item created with correct title, description, tags, priority
   
2. **Test Zap #2 (Close):**
   - Dismiss or fix the alert in ADO Advanced Security
   - Verify: ADO work item state changed to Done/Closed

3. **Test dedup:**
   - Re-trigger the same alert
   - Verify: No duplicate work item created

> 📋 **Full test plan:** See [`validation/test-plan.md`](validation/test-plan.md)

### Step 6: Enable and Monitor

1. Turn both Zaps **ON** in the Zapier dashboard
2. Check **Task History** in Zapier for execution logs
3. Set up **Zapier email notifications** for failed tasks
4. Review task usage weekly to stay within plan limits

---

## Zapier Task Usage & Cost Optimization

| Event | Zap Steps Executed | Tasks Consumed |
|-------|-------------------|---------------|
| Alert created (new) | Trigger + Filter + Parse + Search + Create | **5 tasks** |
| Alert created (duplicate) | Trigger + Filter + Parse + Search + Stopped | **4 tasks** |
| Alert state changed (close) | Trigger + Filter + Search + Update | **4 tasks** |
| Alert state changed (ignored) | Trigger + Filter + Stopped | **2 tasks** |

**Full alert lifecycle (create + close) = ~9 tasks**

### Optimization Tips

1. **Use Filters early** — Filters that stop a Zap don't count as tasks
2. **Combine into one Zap with Paths** (Professional tier) — Use branching to handle both create and close in one Zap, saving the duplicate trigger task
3. **Limit Service Hook scope** — Configure hooks for specific repos, not "Any"
4. **Monitor task usage** — Zapier dashboard shows real-time task consumption

### Monthly Capacity Estimates

| Tier | Tasks/Month | Alert Cycles/Month | Alerts/Day |
|------|------------|-------------------|------------|
| Starter ($20) | 750 | ~83 | ~3 |
| Professional ($49) | 2,000 | ~222 | ~7 |
| Team ($69) | 2,000 | ~222 | ~7 |

---

## Architecture Diagram

```
┌─────────────────┐     Service Hook      ┌──────────────────┐
│  Azure DevOps   │─────(Web Hooks)──────▶│     Zapier       │
│  GHAzDO Alert   │                        │                  │
│  (created/       │                        │  Zap #1: Create  │
│   stateChanged)  │                        │  Zap #2: Close   │
└─────────────────┘                        └────────┬─────────┘
                                                     │
                                            ADO REST API
                                            (PAT auth)
                                                     │
                                                     ▼
                                           ┌─────────────────┐
                                           │  Azure DevOps   │
                                           │  Work Items     │
                                           │  (Issue/Bug)    │
                                           └─────────────────┘
```

---

## Comparison with Other Approaches

| Feature | Zapier (This) | Make.com | Logic App | Power Automate |
|---------|--------------|----------|-----------|----------------|
| Setup time | 45 min | 30 min | 5 min* | 45-90 min |
| Monthly cost | $20-50 | Free (1K ops) | $50-100 | $15-100 |
| Infrastructure | None (SaaS) | None (SaaS) | Azure resource | Power Platform |
| Deduplication | Partial | Partial | Full (WIQL) | Full (WIQL) |
| Auto-close | ✅ | ✅ | ✅ | ✅ |
| One-click deploy | ❌ | ❌ | ✅ | ❌ |
| Git-friendly | ❌ | ❌ | ✅ (JSON) | ❌ |

*With deploy button

---

## Files in This Approach

```
approaches/05-zapier/
├── README.md                              ← This file
├── implementation/
│   ├── zap-create-work-item.md            ← Detailed Zap #1 config
│   ├── zap-close-work-item.md             ← Detailed Zap #2 config
│   ├── service-hook-config.json           ← ADO Service Hook configs
│   ├── webhook-payload-schema.json        ← GHAzDO payload schema
│   └── field-mapping.md                   ← GHAzDO → ADO field mapping
├── validation/
│   ├── test-plan.md                       ← 7 validation tests
│   ├── expected-results.md                ← Expected outcomes
│   └── limitations.md                     ← Limits & trade-offs
└── Zapier_Implementation.pdf              ← Complete PDF report
```
