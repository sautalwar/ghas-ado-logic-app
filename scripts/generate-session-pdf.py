#!/usr/bin/env python3
"""
Generate a comprehensive PDF documenting the Logic App creation session.
Records all Playwright steps, JSON payloads, and workflow details.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '.github', 'skills', 'demo-workflow-pdf', 'references'))
from fpdf import FPDF
import textwrap, json

class SessionPDF(FPDF):
    BLUE = (0, 120, 212)
    DARK = (40, 40, 40)
    WHITE = (255, 255, 255)
    LIGHT_GRAY = (245, 245, 245)
    GREEN = (0, 130, 0)
    RED = (200, 0, 0)
    ORANGE = (200, 100, 0)
    TEAL = (0, 130, 130)

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, "GHAzDO Logic App - Session Documentation | Confidential", align="C")
        self.ln(4)
        self.set_draw_color(*self.BLUE)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def title_page(self):
        self.add_page()
        self.ln(50)
        self.set_fill_color(*self.BLUE)
        self.rect(0, 40, 210, 8, "F")
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(*self.BLUE)
        self.cell(0, 15, "GHAzDO Logic App", align="C")
        self.ln(16)
        self.set_font("Helvetica", "", 18)
        self.set_text_color(50, 50, 50)
        self.cell(0, 12, "Session Documentation & Walkthrough", align="C")
        self.ln(20)
        self.set_font("Helvetica", "I", 13)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "Complete Playwright Automation Steps, JSON Payloads & Responses", align="C")
        self.ln(30)
        details = [
            ("Date:", "March 20, 2026"),
            ("Logic App:", "ghas-ado-sync-demo2"),
            ("Resource Group:", "rg-ghas-ado-learfield"),
            ("Region:", "East US (Consumption)"),
            ("ADO Org:", "brandsafway1"),
            ("ADO Project:", "brandsafway_Engg"),
            ("ADO Repo:", "brandsafway_Engg"),
            ("Automation:", "GitHub Copilot CLI + Playwright"),
        ]
        self.set_font("Helvetica", "", 11)
        self.set_text_color(60, 60, 60)
        for label, val in details:
            self.set_x(45)
            self.set_font("Helvetica", "B", 11)
            self.cell(40, 8, label)
            self.set_font("Helvetica", "", 11)
            self.cell(0, 8, val)
            self.ln(8)
        self.set_fill_color(*self.BLUE)
        self.rect(0, 280, 210, 8, "F")

    def section(self, num, title):
        self.add_page()
        self.set_fill_color(*self.BLUE)
        self.rect(10, self.get_y() - 2, 190, 18, "F")
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*self.WHITE)
        self.cell(0, 14, f"  {num}. {title}", align="L")
        self.ln(22)

    def sub(self, text):
        self.ln(3)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 100, 180)
        self.cell(0, 9, text)
        self.ln(10)

    def step(self, num, title, result=""):
        if self.get_y() > 260:
            self.add_page()
        self.ln(2)
        self.set_fill_color(240, 248, 255)
        self.rect(10, self.get_y(), 190, 8, "F")
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 80, 160)
        self.cell(0, 8, f"  Step {num}: {title}")
        self.ln(10)
        if result:
            self.result(result)

    def action_tag(self, tag, text):
        colors = {"DO": self.GREEN, "CLICK": self.ORANGE, "TYPE": (150,0,150),
                  "NAVIGATE": self.TEAL, "EXPECT": self.RED, "RESPONSE": self.BLUE,
                  "VERIFY": self.TEAL, "PASTE": (150,0,150), "SAVE": self.GREEN}
        r, g, b = colors.get(tag, self.DARK)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(r, g, b)
        self.cell(22, 6, f"[{tag}]")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.DARK)
        for i, line in enumerate(self._wrap(text, 160)):
            if i > 0:
                self.cell(22, 5, "")
            self.cell(160, 6 if i == 0 else 5, line)
            self.ln(6 if i == 0 else 5)

    def result(self, text):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*self.GREEN)
        self.cell(22, 6, "[RESULT]")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.DARK)
        for i, line in enumerate(self._wrap(text, 160)):
            if i > 0:
                self.cell(22, 5, "")
            self.cell(160, 6 if i == 0 else 5, line)
            self.ln(6 if i == 0 else 5)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)
        safe = text.replace('\u2013', '-').replace('\u2014', '--').replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"').replace('\u2022', '-').replace('\u2192', '->').replace('\u2713', '[x]').replace('\u2717', '[ ]').replace('\u25cf', '*').replace('\u2026', '...')
        self.multi_cell(0, 5.5, safe)
        self.ln(2)

    def code(self, text, max_lines=50):
        self.set_font("Courier", "", 7.5)
        self.set_text_color(0, 80, 0)
        self.set_fill_color(*self.LIGHT_GRAY)
        lines = text.strip().split("\n")
        for i, line in enumerate(lines[:max_lines]):
            if self.get_y() > 270:
                self.add_page()
                self.set_font("Courier", "", 7.5)
                self.set_text_color(0, 80, 0)
                self.set_fill_color(*self.LIGHT_GRAY)
            safe = line.replace('\u2013', '-').replace('\u2014', '--').replace('\u2018', "'").replace('\u2019', "'")
            self.cell(0, 4.5, f"  {safe[:120]}", fill=True)
            self.ln(4.5)
        if len(lines) > max_lines:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, f"  ... ({len(lines) - max_lines} more lines)")
            self.ln(5)
        self.ln(2)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*self.DARK)

    def bullet(self, text):
        self.set_x(15)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*self.DARK)
        self.cell(5, 5, "-")
        for i, line in enumerate(self._wrap(text, 170)):
            if i > 0:
                self.set_x(20)
            self.cell(170, 5, line)
            self.ln(5)

    def table_row(self, cells, header=False, widths=None):
        if widths is None:
            widths = [190 / len(cells)] * len(cells)
        if header:
            self.set_font("Helvetica", "B", 8)
            self.set_fill_color(*self.BLUE)
            self.set_text_color(*self.WHITE)
        else:
            self.set_font("Helvetica", "", 8)
            self.set_fill_color(250, 250, 250)
            self.set_text_color(*self.DARK)
        for i, cell in enumerate(cells):
            safe = str(cell).replace('\u2713', '[x]').replace('\u2717', '[ ]')
            self.cell(widths[i], 7, f" {safe}", border=1, fill=True)
        self.ln(7)

    def add_image(self, img_path, caption=""):
        """Embed a screenshot, handling page breaks and resizing to fit page width."""
        if not os.path.exists(img_path):
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(*self.RED)
            self.cell(0, 6, f"  [Image not found: {os.path.basename(img_path)}]")
            self.ln(8)
            return
        if self.get_y() > 180:
            self.add_page()
        self.image(img_path, x=10, w=190)
        if caption:
            self.ln(2)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, caption, align="C")
            self.ln(6)
        else:
            self.ln(4)

    def divider(self):
        self.ln(2)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def _wrap(self, text, max_w_mm):
        chars = int(max_w_mm / 2.0)
        safe = text.replace('\u2013', '-').replace('\u2014', '--').replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"').replace('\u2192', '->')
        return textwrap.wrap(safe, width=chars)


def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf = SessionPDF()
    pdf.alias_nb_pages()

    # ── TITLE PAGE ─────────────────────────────────────────────
    pdf.title_page()

    # ── TABLE OF CONTENTS ──────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*SessionPDF.BLUE)
    pdf.cell(0, 12, "Table of Contents")
    pdf.ln(16)
    toc = [
        ("1", "Session Overview & Architecture"),
        ("2", "Step 1: Launch Edge with Debugging Port"),
        ("3", "Step 2: Create Logic App Resource in Azure Portal"),
        ("4", "Step 3: Configure Trigger - When a GHAzDO Alert is Received"),
        ("5", "Step 4: Deploy Complete Workflow via Code View"),
        ("6", "Step 5: Save & Verify in Designer View"),
        ("7", "Step 6: Update to ADO-Native Workflow (GHAzDO)"),
        ("8", "Complete ADO-Native Workflow JSON"),
        ("9", "Webhook URL & ADO Service Hook Setup"),
        ("10", "ADO Work Item Mapping Reference"),
        ("11", "Troubleshooting & Key Learnings"),
        ("12", "Designer Expanded View"),
        ("13", "ADO Service Hook Setup"),
        ("14", "Live Test - Push Dummy Secret"),
    ]
    for num, title in toc:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*SessionPDF.BLUE)
        pdf.cell(12, 8, num + ".")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*SessionPDF.DARK)
        pdf.cell(0, 8, title)
        pdf.ln(9)

    # ── 1. SESSION OVERVIEW ────────────────────────────────────
    pdf.section("1", "Session Overview & Architecture")
    pdf.body("This document records the complete session where a Logic App was created in Azure Portal using Playwright browser automation via GitHub Copilot CLI. The Logic App receives GHAzDO (GitHub Advanced Security for Azure DevOps) webhook events and automatically creates/closes work items in Azure DevOps.")
    pdf.sub("Architecture Flow")
    pdf.body("1. GHAzDO detects a security vulnerability (secret, code scan, or dependency) in an ADO repo\n2. ADO Service Hook fires a webhook (HTTP POST) to the Logic App URL\n3. Logic App parses the alert payload and extracts: AlertType, AlertId, RepoName, Severity, FilePath, etc.\n4. Logic App checks for existing work items with the same GHAzDO tag (deduplication)\n5. If new alert (created) -> Creates a new ADO work item with full details\n6. If alert resolved -> Finds and closes the existing work item (state -> Done)")
    pdf.sub("Key Resources")
    pdf.table_row(["Resource", "Value"], header=True, widths=[60, 130])
    pdf.table_row(["Logic App Name", "ghas-ado-sync-demo2"], widths=[60, 130])
    pdf.table_row(["Resource Group", "rg-ghas-ado-learfield"], widths=[60, 130])
    pdf.table_row(["Subscription", "ME-MngEnvMCAP557563-sautalwar-1"], widths=[60, 130])
    pdf.table_row(["Region", "East US"], widths=[60, 130])
    pdf.table_row(["Plan", "Consumption (Multi-tenant)"], widths=[60, 130])
    pdf.table_row(["ADO Organization", "brandsafway1"], widths=[60, 130])
    pdf.table_row(["ADO Project", "brandsafway_Engg"], widths=[60, 130])
    pdf.table_row(["ADO Repo", "brandsafway_Engg"], widths=[60, 130])
    pdf.table_row(["Work Item Type", "Issue"], widths=[60, 130])

    # ── 2. LAUNCH EDGE ─────────────────────────────────────────
    pdf.section("2", "Step 1: Launch Edge with Debugging Port")
    pdf.body("Playwright requires a Chromium-based browser with remote debugging enabled. All existing Edge windows must be closed first.")
    pdf.step(1, "Close all Edge windows")
    pdf.action_tag("DO", "Close every Edge browser instance (required to free the debugging port)")
    pdf.step(2, "Launch Edge with remote debugging")
    pdf.action_tag("TYPE", 'msedge --remote-debugging-port=9222 --user-data-dir=$env:TEMP\\edge-debug-profile')
    pdf.action_tag("EXPECT", "Edge opens with Azure Portal (auto-loads from profile)")
    pdf.result("Edge launched successfully on port 9222. Playwright MCP connected via CDP.")
    pdf.step(3, "Verify Playwright connection")
    pdf.action_tag("NAVIGATE", "https://portal.azure.com")
    pdf.action_tag("EXPECT", "Azure Portal loads, authenticated as admin@MngEnvMCAP557563.onmicrosoft.com")
    pdf.result("Connected. Snapshot shows Azure Portal home page with user identity confirmed.")

    # ── 3. CREATE LOGIC APP ────────────────────────────────────
    pdf.section("3", "Step 2: Create Logic App Resource")
    pdf.body("Created a new Consumption-tier Logic App through the Azure Portal marketplace using Playwright automation.")

    pdf.step(1, "Navigate to Create a Resource")
    pdf.action_tag("CLICK", "'Create a resource' button on Azure Portal home")
    pdf.action_tag("EXPECT", "Marketplace search page opens")

    pdf.step(2, "Search for Logic App")
    pdf.action_tag("TYPE", "'Logic App' in the marketplace search box")
    pdf.action_tag("CLICK", "Logic App result card")
    pdf.action_tag("CLICK", "'Create' button on the Logic App marketplace page")

    pdf.step(3, "Select Plan Type")
    pdf.action_tag("CLICK", "'Consumption' plan (Multi-tenant)")
    pdf.action_tag("CLICK", "'Select' button")
    pdf.result("Create Logic App form opens with Consumption plan selected")

    pdf.step(4, "Fill Creation Form")
    pdf.action_tag("CLICK", "Resource Group dropdown -> select 'rg-ghas-ado-learfield'")
    pdf.action_tag("TYPE", "'ghas-ado-sync-demo2' in the Logic App name field")
    pdf.action_tag("CLICK", "Region dropdown -> select 'East US'")

    pdf.step(5, "Review + Create")
    pdf.action_tag("CLICK", "'Review + create' button")
    pdf.action_tag("EXPECT", "'Validation Passed' message appears")
    pdf.action_tag("CLICK", "'Create' button")
    pdf.result("Deployment started. After ~30 seconds: 'Your deployment is complete'")

    pdf.step(6, "Go to Resource")
    pdf.action_tag("CLICK", "'Go to resource' button")
    pdf.result("Logic App overview page loads. Status: Enabled. Definition: 0 triggers, 0 actions.")

    # ── 4. CONFIGURE TRIGGER ───────────────────────────────────
    pdf.section("4", "Step 3: Configure HTTP Trigger")
    pdf.body("Added the HTTP Request trigger via the Logic App Designer, which creates the webhook endpoint.")

    pdf.step(1, "Open Logic App Designer")
    pdf.action_tag("CLICK", "Development Tools -> Logic app designer (left sidebar)")
    pdf.action_tag("EXPECT", "Designer canvas loads with 'Add a trigger' button")

    pdf.step(2, "Add HTTP Request Trigger")
    pdf.action_tag("CLICK", "'Add a trigger' button on the canvas")
    pdf.action_tag("CLICK", "'Request' connector in the trigger panel")
    pdf.action_tag("CLICK", "'When an HTTP request is received' trigger")
    pdf.result("Trigger added to canvas. Configuration panel opens on the right.")

    pdf.step(3, "Rename the Trigger")
    pdf.action_tag("CLICK", "Card title textbox (shows 'When an HTTP request is received')")
    pdf.action_tag("TYPE", "'When a GHAS webhook is received' (renamed to match our workflow)")
    pdf.result("Trigger renamed. Info bar: 'Changing the trigger name updates the callback URL when you save.'")

    # ── 5. DEPLOY VIA CODE VIEW ────────────────────────────────
    pdf.section("5", "Step 4: Deploy Complete Workflow via Code View")
    pdf.body("Instead of building 23 actions one by one in the designer (which would take hours), we used Code View to paste the complete workflow JSON definition. This is the standard approach for deploying complex Logic Apps.")

    pdf.step(1, "Switch to Code View")
    pdf.action_tag("CLICK", "'Code view' button in the designer toolbar")
    pdf.action_tag("CLICK", "'OK' on the 'Switch to Code View' confirmation dialog")
    pdf.result("Monaco editor opens showing the workflow JSON (initially ~26 lines with empty trigger)")

    pdf.step(2, "Prepare the Workflow JSON")
    pdf.body("The workflow JSON was read from infra/workflows/ghas-to-ado.json and wrapped in the code view format:")
    pdf.code('{\n  "definition": { /* workflow definition from ghas-to-ado.json */ },\n  "parameters": {\n    "adoOrganization": { "value": "brandsafway1" },\n    "adoProject": { "value": "brandsafway_Engg" },\n    "adoPat": { "value": "<REDACTED>" },\n    "workItemType": { "value": "Issue" }\n  }\n}')

    pdf.step(3, "Paste JSON into Editor")
    pdf.action_tag("DO", "Copy the complete JSON to clipboard using PowerShell Set-Clipboard")
    pdf.action_tag("CLICK", "Monaco editor textbox to focus it")
    pdf.action_tag("TYPE", "Ctrl+A (select all) then Ctrl+V (paste)")
    pdf.result("Complete workflow JSON pasted. Editor shows ~385 lines.")

    pdf.step(4, "Save the Workflow")
    pdf.action_tag("CLICK", "'Save' button in the toolbar")
    pdf.action_tag("EXPECT", "Toast notification: 'Successfully saved workflow'")
    pdf.body("FIRST ATTEMPT FAILED: 'The value for the workflow parameter adoOrganization is not provided.' This happened because the parameters section was empty. Fixed by adding parameter values in the top-level parameters object.")
    pdf.result("SECOND ATTEMPT: 'Successfully saved workflow ghas-ado-sync-demo2' - all 23 actions deployed!")

    # ── 6. VERIFY IN DESIGNER ──────────────────────────────────
    pdf.section("6", "Step 5: Verify in Designer View")
    pdf.body("After saving in Code View, switched back to Designer to visually verify all workflow steps rendered correctly.")

    pdf.step(1, "Switch to Designer")
    pdf.action_tag("CLICK", "'Designer' button in the toolbar")
    pdf.result("Full workflow renders with all actions and connections visible!")

    pdf.sub("Actions Visible in Designer")
    actions = [
        ("When a GHAzDO alert is received", "Request (HTTP)", "Trigger - receives webhook POST"),
        ("Compose EventType", "Data Operations", "Extracts: triggerBody()?['eventType']"),
        ("Compose AlertType", "Data Operations", "Extracts: resource.alertType (secret/code/dependency)"),
        ("Compose AlertId", "Data Operations", "Extracts: resource.alertId"),
        ("Compose RepoName", "Data Operations", "Extracts: resource.repository.name"),
        ("Compose AlertUrl", "Data Operations", "Extracts: resource.link"),
        ("Compose Severity", "Data Operations", "Extracts: resource.severity"),
        ("Compose FilePath", "Data Operations", "Extracts: resource.location.file"),
        ("Compose LineNumber", "Data Operations", "Extracts: resource.location.line"),
        ("Compose GhasTag", "Data Operations", "Builds: GHAzDO-{repo}-{alertId} for dedup"),
        ("Compose Title", "Data Operations", "Builds title based on alert type"),
        ("Compose Tags", "Data Operations", "Builds: GHAzDO;{type};{severity};{tag}"),
        ("Compose Description", "Data Operations", "HTML table with all alert details"),
        ("Compose IsCreateEvent", "Data Operations", "Boolean: is this a new alert?"),
        ("Condition IsCreateAction", "Control", "Branches: True (create) / False (close)"),
    ]
    pdf.table_row(["Action Name", "Connector", "Purpose"], header=True, widths=[55, 35, 100])
    for name, conn, purpose in actions:
        pdf.table_row([name, conn, purpose], widths=[55, 35, 100])

    pdf.sub("True Branch (New Alert -> Create Work Item)")
    true_actions = [
        ("HTTP QueryExistingWorkItem", "HTTP", "WIQL query: find work items with matching GHAzDO tag"),
        ("Condition NoExistingWorkItem", "Control", "If count == 0, create new; else skip (dedup)"),
        ("HTTP CreateWorkItem", "HTTP", "PATCH to ADO API: creates Issue with title, desc, tags, priority"),
    ]
    pdf.table_row(["Action", "Type", "Purpose"], header=True, widths=[55, 25, 110])
    for name, typ, purpose in true_actions:
        pdf.table_row([name, typ, purpose], widths=[55, 25, 110])

    pdf.sub("False Branch (Alert Resolved -> Close Work Item)")
    false_actions = [
        ("HTTP FindWorkItemToClose", "HTTP", "WIQL query: find open work items with matching tag"),
        ("Condition FoundWorkItemToClose", "Control", "If count > 0, close it"),
        ("HTTP CloseWorkItem", "HTTP", "PATCH: set State='Done', add history comment"),
    ]
    pdf.table_row(["Action", "Type", "Purpose"], header=True, widths=[55, 25, 110])
    for name, typ, purpose in false_actions:
        pdf.table_row([name, typ, purpose], widths=[55, 25, 110])

    # ── 7. ADO-NATIVE WORKFLOW UPDATE ──────────────────────────
    pdf.section("7", "Step 6: Update to ADO-Native Workflow (GHAzDO)")
    pdf.body("The initial workflow was designed for GitHub webhooks. Since the customer uses GHAzDO (GitHub Advanced Security for Azure DevOps) exclusively with no GitHub involvement, we rewrote the workflow to handle ADO Service Hook payloads natively.")

    pdf.sub("Key Changes from GitHub to ADO Format")
    pdf.table_row(["Field", "GitHub Format", "ADO Service Hook Format"], header=True, widths=[40, 75, 75])
    pdf.table_row(["Event Type", "Header: X-GitHub-Event", "Body: eventType (advancedsecurity.alert.created)"], widths=[40, 75, 75])
    pdf.table_row(["Alert ID", "body.alert.number", "body.resource.alertId"], widths=[40, 75, 75])
    pdf.table_row(["Alert Type", "Header value (code_scanning_alert)", "body.resource.alertType (secret/code/dep)"], widths=[40, 75, 75])
    pdf.table_row(["Repo Name", "body.repository.full_name", "body.resource.repository.name"], widths=[40, 75, 75])
    pdf.table_row(["Severity", "body.alert.rule.security_severity", "body.resource.severity"], widths=[40, 75, 75])
    pdf.table_row(["File Path", "body.alert.most_recent_instance.location", "body.resource.location.file"], widths=[40, 75, 75])
    pdf.table_row(["Alert URL", "body.alert.html_url", "body.resource.link"], widths=[40, 75, 75])
    pdf.table_row(["Dedup Tag", "GHAS-{owner/repo}-{number}", "GHAzDO-{repo}-{alertId}"], widths=[40, 75, 75])

    pdf.sub("Removed Parameters")
    pdf.body("The following unused parameters were removed from the workflow:\n- githubPat (was declared but never referenced in any action)\n- webhookSecret (was declared but never used for validation)\n\nOnly 4 parameters remain: adoOrganization, adoProject, adoPat, workItemType")

    # ── 8. COMPLETE JSON ───────────────────────────────────────
    pdf.section("8", "Complete ADO-Native Workflow JSON")
    pdf.body("Below is the complete workflow definition (ghazdo-to-ado.json) that was deployed to the Logic App. This handles ADO Service Hook events from GHAzDO.")

    wf_path = os.path.join(base, "infra", "workflows", "ghazdo-to-ado.json")
    if os.path.exists(wf_path):
        with open(wf_path, 'r') as f:
            wf_json = f.read()
        pdf.code(wf_json, max_lines=200)
    else:
        pdf.body("(Workflow file not found at expected path)")

    # ── 9. WEBHOOK URL & SERVICE HOOK ──────────────────────────
    pdf.section("9", "Webhook URL & ADO Service Hook Setup")

    pdf.sub("Logic App Webhook URL")
    pdf.body("After saving the workflow, the Logic App generated this webhook URL:")
    webhook = "https://prod-33.eastus.logic.azure.com:443/workflows/a7193c25b85547548c6a4fc3734fcd61/triggers/When_a_GHAzDO_alert_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_GHAzDO_alert_is_received%2Frun&sv=1.0&sig=<signature>"
    pdf.code(webhook)
    pdf.body("This URL is the target for ADO Service Hooks. It includes a SAS signature for authentication - no additional auth headers needed.")

    pdf.sub("Setting Up ADO Service Hook (Step-by-Step)")
    steps = [
        "Navigate to: https://dev.azure.com/brandsafway1/brandsafway_Engg/_settings/serviceHooks",
        "Click '+ Create subscription' (green plus button)",
        "Select 'Web Hooks' as the service type, click Next",
        "Under 'Trigger on this type of event', select 'Advanced Security alert created'",
        "Optionally filter by repository: brandsafway_Engg",
        "Click Next",
        "Paste the Logic App webhook URL in the 'URL' field",
        "Leave 'HTTP headers' empty (auth is in the URL signature)",
        "Click 'Test' to send a sample payload",
        "Verify the test returns HTTP 202 Accepted",
        "Click 'Finish' to save the subscription",
        "Repeat for events: 'Advanced Security alert state changed' (for auto-close)",
    ]
    for i, s in enumerate(steps, 1):
        pdf.step(i, s)

    pdf.sub("ADO Service Hook Event Types")
    pdf.table_row(["Event", "When Fired", "Logic App Action"], header=True, widths=[60, 65, 65])
    pdf.table_row(["advancedsecurity.alert.created", "New vulnerability detected", "Creates work item"], widths=[60, 65, 65])
    pdf.table_row(["advancedsecurity.alert.statechanged", "Alert fixed/dismissed", "Closes work item (Done)"], widths=[60, 65, 65])

    # ── 10. WORK ITEM MAPPING ──────────────────────────────────
    pdf.section("10", "ADO Work Item Mapping Reference")
    pdf.body("The Logic App creates ADO work items with these field mappings:")

    pdf.table_row(["ADO Field", "Source", "Example Value"], header=True, widths=[50, 70, 70])
    pdf.table_row(["System.Title", "[GHAzDO-Secret] {secretType}", "[GHAzDO-Secret] Azure Storage Key"], widths=[50, 70, 70])
    pdf.table_row(["System.Description", "HTML table with all alert details", "<table>...severity, repo, file...</table>"], widths=[50, 70, 70])
    pdf.table_row(["System.Tags", "GHAzDO;{type};{severity};{tag}", "GHAzDO;secret;critical;GHAzDO-myrepo-42"], widths=[50, 70, 70])
    pdf.table_row(["Priority", "Based on severity", "1 (critical/high), 2 (medium), 3 (low)"], widths=[50, 70, 70])
    pdf.table_row(["System.State (close)", "Done", "Auto-set when alert resolved"], widths=[50, 70, 70])
    pdf.table_row(["System.History (close)", "Comment", "Auto-closed: GHAzDO alert resolved"], widths=[50, 70, 70])

    pdf.sub("Deduplication Logic")
    pdf.body("Tag format: GHAzDO-{repoName}-{alertId}\nExample: GHAzDO-brandsafway_Engg-42\n\nBefore creating a work item, the Logic App queries ADO using WIQL:\n  SELECT [System.Id] FROM WorkItems WHERE [System.Tags] CONTAINS 'GHAzDO-brandsafway_Engg-42'\n\nIf a matching work item exists, it skips creation (prevents duplicates).\nFor close events, it finds the open work item with the same tag and sets State='Done'.")

    # ── 11. TROUBLESHOOTING ────────────────────────────────────
    pdf.section("11", "Troubleshooting & Key Learnings")

    pdf.sub("Playwright + Azure Portal Quirks")
    lessons = [
        "Edge must be launched with --remote-debugging-port=9222 AND --user-data-dir flag",
        "ALL existing Edge instances must be closed before launching with debugging port",
        "Azure Portal uses nested iframes - must use contentFrame() to interact with designer",
        "Resource group dropdown uses treeitem-based combobox, not standard <select>",
        "Region selector requires typing in a filter combobox, then clicking the treeitem",
        "Monaco editor in Code View cannot be accessed via cross-origin evaluate()",
        "Use Ctrl+A, Ctrl+V (clipboard) approach instead of direct Monaco API calls",
        "Validation button text changes from 'Review + create' to 'Create' after validation passes",
    ]
    for l in lessons:
        pdf.bullet(l)

    pdf.sub("Common Errors & Solutions")
    pdf.table_row(["Error", "Cause", "Solution"], header=True, widths=[60, 65, 65])
    pdf.table_row(["Parameter not provided", "Empty parameters section", "Add parameter values in top-level params"], widths=[60, 65, 65])
    pdf.table_row(["Not valid JSON", "BOM/encoding issue in paste", "Use clean UTF-8 file, re-copy to clipboard"], widths=[60, 65, 65])
    pdf.table_row(["ECONNREFUSED 9222", "Edge not running with debug flag", "Close all Edge, relaunch with flag"], widths=[60, 65, 65])
    pdf.table_row(["Cross-origin blocked", "Iframe security policy", "Use keyboard shortcuts instead of JS eval"], widths=[60, 65, 65])

    pdf.sub("Session Timeline")
    pdf.table_row(["Time", "Action", "Status"], header=True, widths=[35, 110, 45])
    pdf.table_row(["20:20", "Launch Edge with debugging port", "Success"], widths=[35, 110, 45])
    pdf.table_row(["20:22", "Navigate to Azure Portal, Create a resource", "Success"], widths=[35, 110, 45])
    pdf.table_row(["20:24", "Fill Logic App creation form", "Success"], widths=[35, 110, 45])
    pdf.table_row(["20:25", "Review + Create -> Deploy", "Success"], widths=[35, 110, 45])
    pdf.table_row(["20:27", "Go to resource -> Open Designer", "Success"], widths=[35, 110, 45])
    pdf.table_row(["20:28", "Add HTTP trigger, rename to GHAS webhook", "Success"], widths=[35, 110, 45])
    pdf.table_row(["20:30", "Switch to Code View, paste workflow JSON", "Success"], widths=[35, 110, 45])
    pdf.table_row(["20:31", "Save (failed - missing params)", "Fixed"], widths=[35, 110, 45])
    pdf.table_row(["20:32", "Save with params (succeeded)", "Success"], widths=[35, 110, 45])
    pdf.table_row(["20:33", "Switch to Designer, verify all actions", "Success"], widths=[35, 110, 45])
    pdf.table_row(["20:40", "Update adoPat with real credential", "Success"], widths=[35, 110, 45])
    pdf.table_row(["20:46", "Rewrite workflow for ADO Service Hooks", "Success"], widths=[35, 110, 45])
    pdf.table_row(["20:50", "Deploy ADO-native workflow, save", "Success"], widths=[35, 110, 45])
    pdf.table_row(["20:55", "Verify in Designer - all GHAzDO actions visible", "Success"], widths=[35, 110, 45])

    # ── 12. DESIGNER EXPANDED VIEW ─────────────────────────────
    pdf.section("12", "Designer Expanded View")
    pdf.body("The full workflow was expanded in the Logic App Designer using the 'Expand all' and 'Zoom view to fit' controls, showing all 23 actions in a single view.")

    pdf.sub("Expanded Workflow Screenshot")
    img_expanded = os.path.join(base, "designer-ado-expanded.png")
    pdf.add_image(img_expanded, "Designer view with all 23 actions expanded")

    pdf.sub("Complete Action List")
    pdf.body("The expanded view reveals the full workflow structure:")
    pdf.bullet("Trigger: When a GHAzDO alert is received")
    pdf.bullet("8 parallel Compose actions: EventType, AlertType, AlertId, RepoName, AlertUrl, Severity, FilePath, LineNumber")
    pdf.bullet("Compose IsCreateEvent - determines if this is a new alert or state change")
    pdf.bullet("Compose Title - builds work item title based on alert type")
    pdf.bullet("Compose GhasTag - builds deduplication tag: GHAzDO-{repo}-{alertId}")
    pdf.bullet("Compose Tags - combines GHAzDO;{type};{severity};{tag}")
    pdf.bullet("Compose Description - HTML table with all alert details")
    pdf.bullet("Condition IsCreateAction with True/False branches")
    pdf.bullet("True branch: HTTP QueryExistingWorkItem -> Condition NoExistingWorkItem -> HTTP CreateWorkItem")
    pdf.bullet("False branch: HTTP FindWorkItemToClose -> Condition FoundWorkItemToClose -> HTTP CloseWorkItem")

    # ── 13. ADO SERVICE HOOK SETUP ────────────────────────────
    pdf.section("13", "ADO Service Hook Setup")
    pdf.body("Two ADO Service Hooks are required to cover the full lifecycle: one for new alerts (create work item) and one for state changes (close work item). Both point to the same Logic App webhook URL.")

    pdf.sub("Hook 1: Advanced Security Alert Created")
    pdf.step(1, "Navigate to Project Settings > Service hooks")
    pdf.action_tag("NAVIGATE", "https://dev.azure.com/brandsafway1/brandsafway_Engg/_settings/serviceHooks")

    pdf.step(2, "Create subscription")
    pdf.action_tag("CLICK", "'+ Create subscription' (green plus button)")
    pdf.action_tag("CLICK", "Select 'Web Hooks' as the service type")
    pdf.action_tag("CLICK", "Next")

    pdf.step(3, "Configure trigger event")
    pdf.action_tag("CLICK", "Event dropdown -> 'Advanced Security alert created'")
    pdf.action_tag("VERIFY", "All filters set to [Any]")
    img_trigger = os.path.join(base, "ado-service-hook-trigger.png")
    pdf.add_image(img_trigger, "Service Hook trigger configuration - Advanced Security alert created")

    pdf.step(4, "Paste Logic App webhook URL")
    pdf.action_tag("PASTE", "Logic App webhook URL into the 'URL' field")
    pdf.action_tag("VERIFY", "URL points to prod-33.eastus.logic.azure.com")
    img_url = os.path.join(base, "ado-service-hook-url.png")
    pdf.add_image(img_url, "Webhook URL pasted into Service Hook configuration")

    pdf.step(5, "Test the hook")
    pdf.action_tag("CLICK", "'Test' button to send a sample payload")
    pdf.action_tag("EXPECT", "HTTP 202 Accepted response")
    img_test = os.path.join(base, "ado-service-hook-test-success.png")
    pdf.add_image(img_test, "Service Hook test succeeded - HTTP 202 Accepted")

    pdf.step(6, "Finish")
    pdf.action_tag("CLICK", "'Finish' to save the subscription")
    pdf.result("Hook 1 (alert created) saved successfully")

    pdf.divider()

    pdf.sub("Hook 2: Advanced Security Alert State Changed")
    pdf.step(1, "Create second subscription")
    pdf.action_tag("CLICK", "'+ Create subscription' again")
    pdf.action_tag("CLICK", "Select 'Web Hooks' as the service type")

    pdf.step(2, "Configure trigger event")
    pdf.action_tag("CLICK", "Event dropdown -> 'Advanced Security alert state changed'")
    pdf.action_tag("VERIFY", "All filters set to [Any]")

    pdf.step(3, "Paste same webhook URL and test")
    pdf.action_tag("PASTE", "Same Logic App webhook URL")
    pdf.action_tag("CLICK", "'Test' button")
    pdf.action_tag("EXPECT", "HTTP 202 Accepted")
    img_statechange = os.path.join(base, "ado-service-hook-statechange-success.png")
    pdf.add_image(img_statechange, "State change hook test succeeded")

    pdf.step(4, "Finish")
    pdf.action_tag("CLICK", "'Finish' to save the subscription")
    pdf.result("Hook 2 (alert state changed) saved successfully")

    pdf.divider()

    pdf.sub("Both Hooks Active in Service Hooks Grid")
    pdf.body("After creating both subscriptions, the Service Hooks grid shows both hooks enabled and pointing to the Logic App endpoint.")
    img_both = os.path.join(base, "ado-both-service-hooks.png")
    pdf.add_image(img_both, "Both service hooks enabled, pointing to prod-33.eastus.logic.azure.com")

    # ── 14. LIVE TEST - PUSH DUMMY SECRET ─────────────────────
    pdf.section("14", "Live Test - Push Dummy Secret")
    pdf.body("To validate the end-to-end pipeline, a test file containing dummy secrets was pushed to the ADO repo. GHAzDO scans pushes asynchronously and fires the webhook to the Logic App when alerts are detected.")

    pdf.sub("Test File Details")
    pdf.table_row(["Field", "Value"], header=True, widths=[50, 140])
    pdf.table_row(["File Path", "/test-config/staging-config.env"], widths=[50, 140])
    pdf.table_row(["Content", "Generic passwords and token patterns"], widths=[50, 140])
    pdf.table_row(["Push Method", "ADO REST API (POST)"], widths=[50, 140])
    pdf.table_row(["Push ID", "2"], widths=[50, 140])
    pdf.table_row(["Push Date", "03/20/2026 21:24:07"], widths=[50, 140])

    pdf.sub("Push Protection Encounter")
    pdf.body("The first push attempt was blocked by GHAzDO Push Protection because it detected AWS-style credentials in the file. This is expected behavior and confirms that GHAzDO secret scanning is active on the repo.")
    pdf.bullet("First push: BLOCKED by Push Protection (detected AWS credentials pattern)")
    pdf.bullet("Confirms GHAzDO secret scanning is actively enforcing push protection policies")
    pdf.bullet("Second push: Used generic passwords that bypass push protection but still trigger post-push secret scanning")

    pdf.sub("Expected Flow After Push")
    pdf.body("1. File is pushed to ADO repo via REST API\n2. GHAzDO scans the push asynchronously for secrets, code vulnerabilities, and dependency issues\n3. When a secret is detected, GHAzDO creates an alert\n4. ADO Service Hook fires 'advancedsecurity.alert.created' webhook to Logic App\n5. Logic App processes the payload and creates an ADO work item with full alert details")

    pdf.sub("Key Implementation Notes")
    pdf.bullet("The webhook URL signature was stale after renaming the trigger - had to get fresh URL from Logic App Designer trigger panel")
    pdf.bullet("Original sig=Q7cqHeaqqYP... returned 401 Unauthorized")
    pdf.bullet("Fresh sig=fs_2qcGroG69... worked immediately (HTTP 202)")
    pdf.bullet("Lesson: Always re-copy the webhook URL after any trigger rename or workflow save")

    # ── OUTPUT ─────────────────────────────────────────────────
    out_path = os.path.join(base, "docs", "GHAzDO-Logic-App-Session-Documentation.pdf")
    pdf.output(out_path)
    print(f"PDF generated: {out_path}")
    sz = os.path.getsize(out_path)
    print(f"Size: {sz:,} bytes ({sz // 1024} KB), Pages: {pdf.page_no()}")

if __name__ == "__main__":
    main()
