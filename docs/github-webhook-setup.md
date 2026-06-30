# GHAS → Azure Boards: Webhook Setup

How to wire **GitHub Advanced Security (GHAS)** alerts to **Azure Boards** work items using the
`ghas-to-ado.json` Logic App. The Logic App creates a work item when GitHub reports a security
problem and **auto-closes** it when GitHub reports the problem is gone.

> **Source vs. destination.** The companion `ghazdo-to-ado.json` flow is for shops whose code *and*
> boards are both in Azure DevOps. This GHAS flow is the opposite: code (and the alerts) live in
> **GitHub**, while the work items are created in **Azure Boards**.

## What it covers

GitHub sends three webhook event types; together they cover all four GHAS categories:

| GitHub webhook event    | Covers                              | Create on                                  | Close on                                              |
|-------------------------|-------------------------------------|--------------------------------------------|-------------------------------------------------------|
| `secret_scanning_alert` | **Secrets**                         | `created`, `reopened`                       | `resolved`                                            |
| `code_scanning_alert`   | **Code security + Code quality**    | `created`, `reopened`, `reopened_by_user`, `appeared_in_branch` | `fixed`, `closed_by_user`             |
| `dependabot_alert`      | **Dependabot** (dependencies)       | `created`, `reopened`, `reintroduced`       | `fixed`, `dismissed`, `auto_dismissed`               |

> **Code quality** is delivered through the **same `code_scanning_alert` webhook** as code security —
> there is no separate event — so enabling code scanning covers both.

**Start with secrets** to prove the loop end-to-end, then enable the other events with no workflow change.

## Prerequisites

- GHAS enabled on the target repositories: **Secret scanning** (start here), and later **Code scanning**
  and **Dependabot alerts**.
- An Azure DevOps **PAT** with `Work Items: Read & Write` scope.
- Permission to add a webhook at the repo, org, or enterprise level (see scope below).

## Step 1 — Deploy the Logic App

```bash
az group create --name <rg> --location eastus

az deployment group create \
  --resource-group <rg> \
  --template-file infra/deploy-ghas-automation.bicep \
  --parameters infra/parameters.ghas.json \
  --parameters adoOrganization=<org> adoProject=<project> adoPat=<pat> closedState=<Done|Closed>
```

Copy the **`webhookPayloadUrl`** output — that is the GitHub webhook Payload URL.

> **`closedState` must match your ADO process** — this is the setting that determines whether work items
> actually close: **Agile / CMMI = `Closed`**, **Scrum / Basic = `Done`**.

## Step 2 — Configure the GitHub webhook

Add a webhook at the level that matches how the customer wants to manage it (see scope below).

1. Go to **Settings → Webhooks → Add webhook**.
2. **Payload URL:** the `webhookPayloadUrl` from Step 1.
3. **Content type:** `application/json`.
4. **Secret:** the same value you passed as `webhookSecret` (optional — see Security note).
5. **Which events?** Choose **"Let me select individual events"**, then check:
   - ☑ **Secret scanning alerts** (start with just this)
   - ☐ Code scanning alerts *(add when ready)*
   - ☐ Dependabot alerts *(add when ready)*
6. Ensure **Active** is checked and click **Add webhook**.

GitHub sends a `ping`; then real alerts will POST automatically.

## Scope: repo vs. org vs. enterprise

This answers "does it have to be configured per repository, or can it be managed at an org/enterprise level?"

| Level          | Where to add the webhook                                   | Use when                                                   |
|----------------|------------------------------------------------------------|------------------------------------------------------------|
| **Repository** | `https://github.com/<owner>/<repo>/settings/hooks`         | A single repo, or a quick proof of concept.                |
| **Organization** | **Org Settings → Webhooks**                              | One webhook covers **every repo in the org** — recommended for most customers. |
| **Enterprise** | **Enterprise settings → Webhooks** (global webhooks)       | Centrally manage across **all orgs** in the enterprise.    |

You configure **one** webhook at the chosen level — you do **not** need one per repository. A single
deployed Logic App can back an org- or enterprise-level webhook. GHAS itself must still be **enabled on
the repos** (org/enterprise security policies can enable it broadly).

## Step 3 — Verify the loop

1. **Create:** trigger or wait for a GHAS alert (e.g., commit a test secret to a scanned repo).
2. Open the Logic App **Run history** in the Azure Portal — confirm a successful run.
3. Confirm a new **work item** appears in Azure Boards, tagged `GHAS`, `SecretScanning`, the severity,
   and a dedup tag like `GHAS-<owner>-<repo>-secret-<n>`.
4. **Close:** resolve the alert in GitHub. A follow-up run should move the work item to your `closedState`
   and add an auto-close note in **Discussion/History**.

## How de-duplication works

Every work item carries a unique tag: `GHAS-{owner}-{repo}-{type}-{alertNumber}` where `{type}` is
`secret`, `code`, or `dep`. Before creating, the workflow runs a WIQL query for that tag and skips
creation if a matching open work item already exists. The type segment prevents collisions between, e.g.,
secret alert #1 and code alert #1 in the same repo. The close path finds the same tag and updates state.

## Security note

The Logic App trigger URL is **SAS-signed** (an unguessable shared-access signature), which is the primary
access control. The `webhookSecret` parameter is accepted and can be set on the GitHub webhook, but HMAC
**signature verification** is not enforced inside the Consumption Logic App (it would require an Azure
Function or a Standard Logic App). Treat the payload URL as a secret. HMAC enforcement is a future
enhancement.

## Related

- `infra/deploy-ghas-automation.bicep` — entry point for this flow.
- `infra/workflows/ghas-to-ado.json` — the workflow definition (edit alert behavior here).
- `docs/ado-service-hook-setup.md` — the ADO-sourced (GHAzDO) equivalent.
