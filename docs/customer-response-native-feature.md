# Subject: Great News — Native Work Item Creation from Security Alerts Now Available

---

Hi [Customer Contact],

Thank you for that honest feedback about Logic Apps. You were absolutely right—adding middleware complexity just to create work items felt like the wrong approach. I'm excited to share that ADO has now shipped exactly what you asked for: a native **"Add" button** directly in the Advanced Security alerts interface.

## The Solution

When you open any GitHub Advanced Security alert in Azure DevOps, you'll see a new **"Related Work" section** with an **"Add"** button. One click creates a new work item pre-populated with the alert details (severity, description, remediation guidance), and the link flows both directions—the alert links to the work item, the work item links back to the alert. No external systems, no middleware, no setup required.

## What This Means for Your Workflow

✓ No Logic App infrastructure for work item creation  
✓ No ongoing maintenance or monitoring  
✓ One-click work item creation from any alert  
✓ Alerts and work items stay in sync through native linking  

## What About Auto-Close?

The one piece Logic Apps *was* useful for is auto-closing work items when vulnerabilities are remediated. If that workflow is valuable to your team, we can deploy a **tiny, optional Logic App** (literally one action) that watches for resolved alerts and closes the linked work item. It's a one-click deploy and completely optional—your team can decide if it's worth it.

## Next Steps

1. **Try it now**: Go to Advanced Security → open an alert → look for the "Related Work" section
2. **We'll send**: A quick-start guide with screenshots and a 5-minute walkthrough
3. **Optional call**: If you'd like to see it in action or discuss the optional auto-close Logic App, I'm happy to hop on a brief call

This is much closer to what you were looking for. Looking forward to your feedback.

Best,  
Saurabh  
GitHub/Microsoft Advanced Security Team
