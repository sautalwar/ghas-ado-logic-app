# Subject: Full Automation for GHAzDO Security Alerts — One-Click Deploy, Zero Maintenance

---

Hi [Customer Contact],

I heard you loud and clear — you want **full automation**, not manual clicking. When a security alert fires, a work item should appear automatically. When the vulnerability is fixed, the work item should close itself. No human in the loop.

We built exactly that, and we've made deployment as simple as possible.

## How It Works

**Step 1 — Deploy (3 minutes)**
Click the **"Deploy to Azure"** button in our repo → fill in 3 fields (subscription, resource group, ADO PAT) → click Create. That's it. Azure provisions a fully configured Logic App that handles both work item creation and auto-close.

**Step 2 — Connect ADO (2 minutes)**
Configure two service hooks in your ADO project settings so alerts flow to the Logic App automatically. This is the one manual step — we have a [step-by-step guide](ado-service-hook-setup.md) that takes about 2 minutes.

After that, everything is hands-off:

✓ **Alert fires** → work item created automatically with full details (severity, description, remediation)  
✓ **Alert resolved** → linked work item closed automatically  
✓ **Zero ongoing maintenance** — Microsoft-managed Logic App, no servers to patch  
✓ **Cost** → ~$50–100/month depending on alert volume  

## Bonus: Native ADO Button

ADO also shipped a native **"Add" button** in the Advanced Security alerts UI for ad-hoc, manual work item linking. This is a great complement — your developers can use it to manually link alerts that need special attention, while the Logic App handles the bulk automation in the background.

## Next Steps

I'd love to walk you through the setup live — it genuinely takes under 5 minutes end to end. **Can we schedule a 15-minute call this week?** I'll deploy it in your environment and we'll have it running before the call ends.

Looking forward to it.

Best,  
Saurabh  
GitHub/Microsoft Advanced Security Team
