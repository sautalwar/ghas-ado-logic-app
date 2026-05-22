# Email: Re: GHAzDO Testing Feedback — Here's What We Built, What We Learned, and What's Next

---

**To:** michael.holder@learfield.com  
**CC:** Pupun Das, Saurabh Talwar  
**Subject:** Re: The GHAS testing feedback — you're right, and here's the simpler path

---

Hi Michael,

Thank you for that clear feedback on the GHAS testing. You're absolutely right — and your message helped us realize we should give you two better paths forward instead of just one. Let me walk you through where we started, what we learned from you, and what we're suggesting now.

---

## Section 1: What We Originally Built For You

We created that Logic App automation (`ghazdo-to-ado.json`) to solve the exact problem you described — the multi-step manual workflow that adds friction to your security response process. Here's what it does:

- **Automatically creates a work item** the moment a GHAzDO alert appears in your ADO project
- **Automatically closes the work item** when the alert is resolved
- **Bidirectionally links** everything, so your team sees the full context without extra clicks

We built it because that's the "lights-out" automation story — one thing happens upstream (an alert), and everything downstream flows automatically. No manual steps. Complete hands-off.

But you gave us crucial feedback: **"I do believe that simplifying the work item creation process would be most beneficial"** — and then you said the quiet part out loud: "Logic Apps add complexity your team shouldn't need to worry about." You're absolutely right. Maintaining another piece of infrastructure (Logic App, service hooks, error handling) is overhead you don't need if there's a simpler way.

---

## Section 2: What We're Now Suggesting — Two Paths

Based on your feedback, we're proposing two options that both eliminate manual toil, but in different ways.

### **Option A: Native ADO Button (Instant Win, Zero Setup)**

Azure DevOps now ships with a native **"Add" / "Related Work" button** directly in the GHAzDO alerts page. This is exactly what you asked for: click a button to create a work item from the alert.

**How it works:**
1. Open a GHAzDO alert in your ADO project
2. Click **"Add"** in the alert details (Related Work section)
3. Select your work item type (Bug, Issue, Task — your choice)
4. ADO creates a new work item with alert details pre-populated and auto-links it bidirectionally

**What you get:**
- **Zero setup** (it's already there)
- **Zero cost** (built into ADO)
- **Zero ongoing maintenance** (Microsoft manages it)
- **Instant availability** (use it today)

**How Option A eliminates your manual steps:**

| Your Current Manual Process | With Native ADO Button |
|---|---|
| Scan to receive an alert | ✅ Same — alerts appear in GHAzDO |
| Create a work item | ❌ **Eliminated** — click "Add" right from the alert |
| Attach it to the alert | ❌ **Eliminated** — auto-linked bidirectionally |

---

### **Option B: Full Hands-Free Automation (Optional Upgrade for Maximum Efficiency)**

If your team decides you want **zero clicks** — fully automatic creation and closure without any manual intervention — we've simplified the Logic App deployment into a genuine one-click experience:

**How it works:**
1. Click a single **"Deploy to Azure" button** (in our repo)
2. Enter just **3 fields**: your ADO org name, project name, and a Personal Access Token
3. **Done.** The Logic App deploys in ~5 minutes. From then on:
   - Every alert **automatically creates** a work item
   - When the alert is resolved, the work item **automatically closes**
   - Everything is **bidirectionally linked**

**What it costs:**
- Setup time: ~5 minutes
- Monthly cost: ~$50–100 (Logic App hosting)
- Ongoing maintenance: Zero — Microsoft handles all updates

**How Option B eliminates your manual steps:**

| Your Current Manual Process | With Full Automation |
|---|---|
| Scan to receive an alert | ❌ **Eliminated** — automatic |
| Create a work item | ❌ **Eliminated** — automatic |
| Attach it to the alert | ❌ **Eliminated** — auto-tagged and linked |
| *Bonus:* Close work item when fixed | ❌ **Eliminated** — auto-closed when alert resolves |

---

## Section 3: A Few Quick Environment Questions

To make sure everything works smoothly in your environment, could you help me confirm a few things?

1. **What ADO process template are you using?** (Agile, Scrum, Basic, or CMMI?) — This affects how work items behave and what types are available when you click the "Add" button.

2. **Is "brandsafway1" still the correct ADO organization name?** I want to make sure we have the right details on file.

3. **When you create work items from alerts, what type do you prefer?** (Bug, Issue, Task?) — This becomes your default when you click the button.

4. **Do you have an Azure subscription available?** (Just in case you decide to explore the full automation path later.)

---

## Section 4: Next Steps

Here's what I'd love to do:

**Immediate:** I'd like to walk you through the native "Add" button on a **15-minute call** — we can click through it together in your actual ADO environment so you can see it works exactly as described. No setup required; it's already there.

**Optional:** While we're talking, we can also discuss whether the full automation option (Option B) makes sense for your workflow down the road. But no pressure — many teams find the native button strikes the perfect balance between simplicity and automation.

I'm attaching **Dallas_Automation_Strategy.pdf** for reference if you want to dig deeper into the full automation approach.

**Are you available for a quick call this week?** I'm flexible — just let me know what works for your schedule.

Thanks again for the thoughtful feedback. It really does make a difference in shaping how we build and explain this.

Best,  
Saurabh  
GitHub/Microsoft Advanced Security Team

---

### Attachments

- `Dallas_Automation_Strategy.pdf` (Reference for full automation approach, if you want to explore it)
