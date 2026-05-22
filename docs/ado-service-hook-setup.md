# Configure ADO Service Hooks (2-Minute Setup)

This is the **one manual step** after clicking "Deploy to Azure." You need **two** service hooks — one to auto-create work items, one to auto-close them.

## Prerequisites

- ADO project with **GitHub Advanced Security** enabled
- **Logic App trigger URL** (copied from the Azure deployment outputs)

## Steps

### Service Hook 1: Auto-Create Work Items

1. Go to your **ADO Project → Project Settings → Service Hooks**
2. Click **"+ Create subscription"**
3. Select **"Web Hooks"** as the service → **Next**
4. Under trigger, select **"Advanced Security alert created"** → **Next**
5. *(Optional)* Filter to a specific repository if desired
6. In the **URL** field, paste your **Logic App trigger URL** from the deployment outputs
7. Click **"Test"** — you should see a `200 OK` response
8. Click **"Finish"** to save

### Service Hook 2: Auto-Close Work Items

**Repeat the exact same steps**, but in step 4 select:

> **"Advanced Security alert state changed"**

This fires when an alert is resolved/dismissed, allowing the Logic App to auto-close the linked work item.

## Why Two Hooks?

| Hook | Trigger Event | What It Does |
|------|--------------|--------------|
| Hook 1 | Alert **created** | Creates a new ADO work item |
| Hook 2 | Alert **state changed** | Closes the work item when the alert is resolved |

Both hooks point to the **same** Logic App URL — the Logic App inspects the payload to determine which action to take.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| **403 Forbidden** | PAT scope insufficient | Ensure the PAT has `Work Items: Read & Write` scope |
| **Timeout / no response** | Logic App not running | Check the Logic App is in **Enabled** state in the Azure Portal |
| **Test returns 200 but no work item** | Payload mismatch | Check the Logic App run history for errors in the Azure Portal |

## Screenshots

Refer to the existing screenshots in the repo root for visual reference:
- `ado-service-hook-trigger.png` — Selecting the trigger event
- `ado-service-hook-url.png` — Pasting the Logic App URL
- `ado-service-hook-test-success.png` — Successful test result
- `ado-service-hook-created.png` — Completed service hook
- `ado-both-service-hooks.png` — Both hooks configured
