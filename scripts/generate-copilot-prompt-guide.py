#!/usr/bin/env python3
"""
Generate a PDF containing a ready-to-use Copilot prompt that customers can
use to recreate the entire GHAzDO-to-ADO Logic App integration workflow.
"""

import os
from fpdf import FPDF

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
OUTPUT_PDF = os.path.join(DOCS_DIR, "GHAzDO-Copilot-Prompt-Guide.pdf")

MS_BLUE = (0, 120, 212)
DARK_TEXT = (33, 33, 33)
WHITE = (255, 255, 255)
MED_GRAY = (200, 200, 200)
CODE_BG = (240, 240, 240)
SECTION_BG = (230, 242, 255)
TIP_GREEN = (0, 128, 64)
TIP_BG = (232, 245, 233)
WARN_BG = (255, 243, 224)
WARN_BORDER = (230, 126, 34)
PURPLE = (102, 51, 153)
PROMPT_BG = (248, 248, 255)
PROMPT_BORDER = (0, 120, 212)


def safe(text):
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "--",
        "\u2026": "...", "\u2022": "-",
        "\u2192": "->", "\u2190": "<-",
        "\u2713": "[x]", "\u2717": "[ ]",
        "\u00a0": " ", "\u00b7": "-",
        "\u25cf": "*", "\u25cb": "o",
        "\u00bb": ">>",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


class PromptPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*MS_BLUE)
        self.cell(95, 8, safe("GHAzDO-to-ADO | Copilot Prompt Guide"), align="L")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(95, 8, safe("Customer Ready"), align="R")
        self.set_draw_color(*MS_BLUE)
        self.line(10, 14, 200, 14)
        self.ln(8)

    def footer(self):
        if self.page_no() <= 1:
            return
        self.set_y(-15)
        self.set_draw_color(*MED_GRAY)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(95, 10, safe("GHAzDO-to-ADO | Copilot Prompt Guide"), align="L")
        self.cell(95, 10, safe(f"Page {self.page_no()}"), align="R")

    def section_title(self, number, title):
        self.add_page()
        self.set_fill_color(*MS_BLUE)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 15)
        self.cell(0, 11, safe(f"  {number}. {title}"), fill=True,
                  new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
        self.set_text_color(*DARK_TEXT)

    def sub_heading(self, text):
        self.ln(3)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*MS_BLUE)
        self.cell(0, 7, safe(text), new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*DARK_TEXT)
        self.ln(2)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK_TEXT)
        self.multi_cell(0, 5.5, safe(text))
        self.ln(1.5)

    def bullet(self, text, indent=10):
        self.set_x(self.l_margin + indent)
        self.set_font("Helvetica", "", 10)
        w = self.w - self.r_margin - self.get_x()
        self.multi_cell(w, 5.5, safe(f"- {text}"))
        self.ln(0.5)

    def numbered_step(self, number, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*MS_BLUE)
        prefix = f"{number}. "
        self.set_x(self.l_margin + 5)
        self.cell(self.get_string_width(prefix) + 1, 6, prefix)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK_TEXT)
        remaining_w = self.w - self.r_margin - self.get_x()
        self.multi_cell(remaining_w, 6, safe(text))
        self.ln(1)

    def prompt_block(self, title, lines):
        """Render a copyable prompt block with blue left border."""
        self.ln(2)
        self.set_fill_color(*PROMPT_BG)
        self.set_draw_color(*PROMPT_BORDER)

        x0 = self.get_x()
        y0 = self.get_y()

        # Title bar
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*MS_BLUE)
        self.cell(0, 6, safe(f"  PROMPT: {title}"), fill=True,
                  new_x="LMARGIN", new_y="NEXT")

        # Prompt body - use cell per line to avoid width issues
        self.set_font("Courier", "", 8)
        self.set_text_color(*DARK_TEXT)
        for line in lines:
            s = safe(line)
            self.cell(0, 4.5, f"  {s}", fill=True,
                      new_x="LMARGIN", new_y="NEXT")

        y1 = self.get_y()
        # Blue left border
        self.set_draw_color(*PROMPT_BORDER)
        self.set_line_width(0.8)
        self.line(x0, y0, x0, y1)
        self.set_line_width(0.2)
        self.set_draw_color(*MED_GRAY)
        self.ln(3)

    def code_block(self, lines, font_size=8):
        self.ln(1)
        self.set_fill_color(*CODE_BG)
        self.set_font("Courier", "", font_size)
        self.set_text_color(*DARK_TEXT)
        for line in lines:
            s = safe(line.replace("\t", "    "))
            self.cell(0, 4.5, f"  {s}", fill=True,
                      new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def tip_box(self, text):
        self.ln(2)
        self.set_fill_color(*TIP_BG)
        self.set_draw_color(*TIP_GREEN)
        x0 = self.get_x()
        y0 = self.get_y()
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*TIP_GREEN)
        self.cell(0, 5.5, safe("  TIP:"), fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DARK_TEXT)
        self.multi_cell(0, 5, safe(f"  {text}"), fill=True)
        y1 = self.get_y()
        self.line(x0, y0, x0, y1)
        self.set_draw_color(*MED_GRAY)
        self.ln(2)

    def warning_box(self, text):
        self.ln(2)
        self.set_fill_color(*WARN_BG)
        self.set_draw_color(*WARN_BORDER)
        x0 = self.get_x()
        y0 = self.get_y()
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*WARN_BORDER)
        self.cell(0, 5.5, safe("  IMPORTANT:"), fill=True,
                  new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DARK_TEXT)
        self.multi_cell(0, 5, safe(f"  {text}"), fill=True)
        y1 = self.get_y()
        self.line(x0, y0, x0, y1)
        self.set_draw_color(*MED_GRAY)
        self.ln(2)

    def table_row(self, cells, widths, bold=False, fill=False):
        style = "B" if bold else ""
        if fill:
            self.set_fill_color(*SECTION_BG)
        self.set_font("Helvetica", style, 9)
        h = 7
        for cell_text, w in zip(cells, widths):
            self.cell(w, h, safe(f" {cell_text}"), border=1, fill=fill)
        self.ln(h)


def build_pdf():
    pdf = PromptPDF()

    # ===== TITLE PAGE ======================================================
    pdf.add_page()
    pdf.set_fill_color(*MS_BLUE)
    pdf.rect(0, 0, 210, 115, "F")

    pdf.set_y(18)
    pdf.set_font("Helvetica", "B", 30)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 14, safe("GHAzDO-to-ADO"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 12, safe("Copilot Prompt Guide"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 8, safe("Ready-to-Use Prompts for GitHub Copilot"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, safe("to Build the Entire Integration from Scratch"), align="C",
             new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(125)
    pdf.set_text_color(*DARK_TEXT)
    pdf.set_font("Helvetica", "", 11)

    info = [
        ("Document Type", "Customer Copilot Prompt Guide"),
        ("Purpose", "Copy-paste prompts to recreate the full workflow"),
        ("Works With", "GitHub Copilot Chat, Copilot CLI, Copilot in VS Code"),
        ("Prerequisites", "Azure subscription, ADO org with GHAzDO enabled"),
        ("JSON File Needed", "ghazdo-to-ado.json (provided separately)"),
        ("Date", "March 2026"),
    ]
    for label, val in info:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(50, 8, safe(f"  {label}:"))
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, safe(val), new_x="LMARGIN", new_y="NEXT")

    # ===== HOW TO USE THIS GUIDE ===========================================
    pdf.section_title("1", "How to Use This Guide")

    pdf.body(
        "This document contains ready-to-use prompts that you can copy and paste "
        "into GitHub Copilot (Chat, CLI, or VS Code) to build the entire "
        "GHAzDO-to-ADO Logic App integration. Each prompt is self-contained and "
        "includes all the context Copilot needs."
    )

    pdf.sub_heading("How It Works")
    pdf.numbered_step(1, "Open GitHub Copilot Chat (in VS Code, CLI, or browser)")
    pdf.numbered_step(2, "Copy the prompt from this guide (the blue-bordered blocks)")
    pdf.numbered_step(3, "Paste it into Copilot and press Enter")
    pdf.numbered_step(4, "Copilot will execute the steps or guide you through them")
    pdf.numbered_step(5, "Move to the next prompt when ready")

    pdf.sub_heading("Before You Start -- Gather These Values")
    pdf.body("You will need to replace the placeholder values in the prompts with your own:")

    w_val = [55, 65, 70]
    pdf.table_row(["Placeholder", "Replace With", "Example"], w_val, bold=True, fill=True)
    pdf.table_row(["{{ADO_ORG}}", "Your ADO organization name", "mycompany"], w_val)
    pdf.table_row(["{{ADO_PROJECT}}", "Your ADO project name", "MyProject"], w_val)
    pdf.table_row(["{{ADO_PAT}}", "Your ADO Personal Access Token", "(your PAT string)"], w_val)
    pdf.table_row(["{{RESOURCE_GROUP}}", "Azure resource group name", "rg-ghas-ado"], w_val)
    pdf.table_row(["{{LOGIC_APP_NAME}}", "Name for your Logic App", "ghas-ado-sync"], w_val)
    pdf.table_row(["{{REGION}}", "Azure region", "East US"], w_val)
    pdf.table_row(["{{WORK_ITEM_TYPE}}", "ADO work item type to create", "Issue or Bug"], w_val)

    pdf.warning_box(
        "Never share your ADO PAT in public channels. The PAT is a secret credential "
        "that grants access to your ADO organization. Treat it like a password."
    )

    # ===== PROMPT 1: CREATE ADO PAT ========================================
    pdf.section_title("2", "Prompt 1: Create an ADO Personal Access Token")

    pdf.body(
        "Use this prompt to get step-by-step guidance on creating the PAT. "
        "This is a prerequisite for the Logic App."
    )

    pdf.prompt_block("Create ADO PAT", [
        "I need to create a Personal Access Token (PAT) in Azure DevOps",
        "for a Logic App integration that will:",
        "  1. Create Work Items automatically",
        "  2. Query existing Work Items by tag",
        "  3. Update Work Item state (close them)",
        "",
        "My ADO organization is: {{ADO_ORG}}",
        "My ADO project is: {{ADO_PROJECT}}",
        "",
        "Please give me exact step-by-step instructions to:",
        "  1. Navigate to the PAT creation page in ADO",
        "  2. Create a new PAT with the MINIMUM required scopes",
        "  3. Set an appropriate expiration date",
        "  4. Copy and save the token securely",
        "",
        "Tell me exactly which scopes I need (least privilege).",
    ])

    pdf.tip_box(
        "Required PAT scopes: Work Items (Read, Write & Manage) and Code (Read). "
        "Set expiration to 90-180 days and save the PAT in a secure vault."
    )

    # ===== PROMPT 2: CREATE LOGIC APP ======================================
    pdf.section_title("3", "Prompt 2: Create the Azure Logic App")

    pdf.body(
        "This prompt walks you through creating the Logic App resource in Azure Portal."
    )

    pdf.prompt_block("Create Logic App in Azure Portal", [
        "I need to create an Azure Logic App (Standard) in the Azure Portal",
        "for a GHAzDO-to-ADO security alert integration.",
        "",
        "Details:",
        "  - Resource Group: {{RESOURCE_GROUP}} (create if doesn't exist)",
        "  - Logic App Name: {{LOGIC_APP_NAME}}",
        "  - Region: {{REGION}}",
        "  - Plan Type: Workflow Service Plan",
        "  - Workflow Name: ghas-ado-sync",
        "  - Workflow Type: Stateful",
        "",
        "Please give me exact click-by-click steps to:",
        "  1. Navigate to Azure Portal and create the resource",
        "  2. Fill in all required fields",
        "  3. Click Review + Create and wait for deployment",
        "  4. Navigate to the deployed Logic App",
        "  5. Create a new Stateful workflow named 'ghas-ado-sync'",
        "",
        "After creating, I will need to paste a JSON workflow",
        "into Code View.",
    ])

    # ===== PROMPT 3: DEPLOY WORKFLOW =======================================
    pdf.section_title("4", "Prompt 3: Deploy the Workflow JSON")

    pdf.body(
        "This is the core prompt -- it deploys the complete workflow. "
        "You need the ghazdo-to-ado.json file for this step."
    )

    pdf.prompt_block("Deploy Workflow via Code View", [
        "I have an Azure Logic App created with a Stateful workflow.",
        "I need to deploy the GHAzDO-to-ADO workflow JSON.",
        "",
        "Please help me:",
        "  1. Open the workflow in Logic App Designer",
        "  2. Switch to 'Code View' tab",
        "  3. I will paste the contents of ghazdo-to-ado.json",
        "     (218 lines, 4 parameters, ~17 actions)",
        "  4. Save the workflow",
        "  5. Switch to Designer view to verify all components loaded",
        "",
        "After pasting, I need to configure these parameters:",
        "  - adoOrganization: {{ADO_ORG}}",
        "  - adoProject: {{ADO_PROJECT}}",
        "  - adoPat: {{ADO_PAT}} (this is a SecureString parameter)",
        "  - workItemType: {{WORK_ITEM_TYPE}} (default: Issue)",
        "",
        "Then I need to get the Webhook URL from the workflow",
        "Overview page. I will use this URL for ADO Service Hooks.",
        "",
        "The JSON file is called ghazdo-to-ado.json and it contains:",
        "  - 1 HTTP trigger (receives webhooks from ADO Service Hooks)",
        "  - 9 Compose actions (extract fields from webhook payload)",
        "  - 4 HTTP actions (query/create/close ADO Work Items)",
        "  - 4 Conditions (route create vs close, check duplicates)",
    ])

    pdf.tip_box(
        "After saving, go to the workflow Overview page to find the Webhook URL. "
        "Copy it -- you will need it for the next step (ADO Service Hooks)."
    )

    # ===== PROMPT 4: ADO SERVICE HOOKS =====================================
    pdf.section_title("5", "Prompt 4: Configure ADO Service Hooks")

    pdf.body(
        "This prompt sets up the two webhooks in ADO that trigger the Logic App "
        "when GHAzDO finds security issues."
    )

    pdf.prompt_block("Create ADO Service Hooks for GHAzDO", [
        "I need to create TWO Service Hooks in Azure DevOps that send",
        "webhooks to my Logic App when GHAzDO (GitHub Advanced Security",
        "for Azure DevOps) detects security issues.",
        "",
        "My details:",
        "  - ADO Organization: {{ADO_ORG}}",
        "  - ADO Project: {{ADO_PROJECT}}",
        "  - Logic App Webhook URL: {{WEBHOOK_URL}}",
        "",
        "Please give me exact steps to create BOTH hooks:",
        "",
        "Hook 1 - Alert Created:",
        "  1. Go to Project Settings -> Service Hooks",
        "  2. Click '+' to create a new subscription",
        "  3. Select 'Advanced Security' as the service",
        "  4. Trigger: 'Advanced Security alert created'",
        "  5. Repository: Any (or select a specific repo)",
        "  6. Alert type: Any",
        "  7. Action: Web Hooks -> Send notification via HTTP POST",
        "  8. URL: paste the Logic App webhook URL",
        "  9. Test the hook, then click Finish",
        "",
        "Hook 2 - Alert State Changed:",
        "  1. Same steps but trigger: 'Advanced Security alert",
        "     state changed'",
        "  2. Same webhook URL",
        "  3. This hook enables auto-closing Work Items when",
        "     alerts are resolved in GHAzDO",
        "",
        "After creating both hooks, I should see them listed",
        "in the Service Hooks page with status 'Enabled'.",
    ])

    pdf.warning_box(
        "The Service Hook publisher for GHAzDO is 'Advanced Security' in the UI. "
        "If you do not see it, ensure GHAzDO is enabled for your ADO organization. "
        "Go to Organization Settings -> General -> Advanced Security to verify."
    )

    # ===== PROMPT 5: TEST THE INTEGRATION ==================================
    pdf.section_title("6", "Prompt 5: Test the End-to-End Integration")

    pdf.prompt_block("Test GHAzDO-to-ADO Integration", [
        "I have the full GHAzDO-to-ADO integration set up:",
        "  - Logic App deployed with ghazdo-to-ado.json",
        "  - Two ADO Service Hooks (alert created + state changed)",
        "  - Webhook URL configured",
        "",
        "I want to test the end-to-end flow. Please help me with",
        "TWO testing approaches:",
        "",
        "Option A - Simulated webhook (recommended for testing):",
        "  Generate a curl command that sends a test webhook payload",
        "  to my Logic App URL that simulates a GHAzDO secret alert.",
        "  The payload should use eventType:",
        "  'ms.vss-alerts.alert-created-event' with resource fields:",
        "  alertId, alertType (secret), severity (critical),",
        "  repository name, location (file, line), secretType.",
        "",
        "  Webhook URL: {{WEBHOOK_URL}}",
        "",
        "Option B - Real secret push:",
        "  Give me steps to create a test file with a dummy secret",
        "  and push it to my ADO repo so GHAzDO detects it naturally.",
        "  File: test-secrets/config.env",
        "  Content: a dummy database connection string",
        "",
        "After the test, tell me how to verify:",
        "  1. Logic App run history (should show Succeeded)",
        "  2. ADO Work Item created (with correct title, tags,",
        "     priority, description)",
        "  3. Then test auto-close: send a state-changed webhook",
        "     and verify the Work Item moves to 'Done'",
    ])

    pdf.sub_heading("Sample Test Payload (for reference)")
    pdf.code_block([
        '{',
        '  "eventType": "ms.vss-alerts.alert-created-event",',
        '  "resource": {',
        '    "alertId": 999,',
        '    "alertType": "secret",',
        '    "severity": "critical",',
        '    "repository": { "name": "my-repo" },',
        '    "location": {',
        '      "file": "test-secrets/config.env",',
        '      "startLine": 1',
        '    },',
        '    "secretType": "Azure Storage Account Key",',
        '    "link": "https://dev.azure.com/{{ADO_ORG}}/{{ADO_PROJECT}}"',
        '  },',
        '  "resourceContainers": {',
        '    "project": { "name": "{{ADO_PROJECT}}" }',
        '  }',
        '}',
    ])

    # ===== PROMPT 6: CUSTOMIZE FIELDS ======================================
    pdf.section_title("7", "Prompt 6: Add Custom Fields to Work Items")

    pdf.prompt_block("Customize GHAzDO Work Item Fields", [
        "I have a working GHAzDO-to-ADO Logic App integration using",
        "the ghazdo-to-ado.json workflow. I want to customize the",
        "Work Items that get created.",
        "",
        "My current setup creates Work Items with: Title, Description,",
        "Tags, and Priority. I want to add these additional fields:",
        "",
        "Built-in fields (no ADO setup needed):",
        "  - System.AssignedTo = 'security-team@mycompany.com'",
        "  - System.AreaPath = '{{ADO_PROJECT}}\\Security'",
        "  - System.IterationPath = '{{ADO_PROJECT}}\\Sprint 5'",
        "",
        "Custom fields (need to create in ADO first):",
        "  - Custom.SecurityTool = 'GHAzDO' (static text)",
        "  - Custom.AlertCategory = dynamic from webhook alertType",
        "  - Custom.SourceRepo = dynamic from webhook repo name",
        "  - Custom.AlertSeverity = dynamic from webhook severity",
        "  - Custom.FilePath = dynamic from webhook file location",
        "  - Custom.ComplianceTag = 'SOC2' (static text)",
        "",
        "Please help me:",
        "  1. Create these custom fields in ADO (Organization",
        "     Settings -> Process -> my process -> my work item type",
        "     -> New field). Give me step-by-step for each field.",
        "  2. Generate the JSON Patch entries I need to add to the",
        "     HTTP_CreateWorkItem body in ghazdo-to-ado.json",
        "  3. Show me the exact lines to modify in the JSON file",
        "     (around line 153-158 in the body array)",
    ])

    # ===== PROMPT 7: INHERITED PROCESS + CUSTOM TYPES ======================
    pdf.section_title("8", "Prompt 7: Create Custom Work Item Types")

    pdf.body(
        "This is the most advanced prompt -- it creates a fully custom ADO process "
        "with security-specific work item types."
    )

    pdf.prompt_block("Create Inherited Process with Custom Types", [
        "I want to create custom work item types in Azure DevOps for",
        "my GHAzDO security alert tracking. I need your help with the",
        "full process.",
        "",
        "My ADO organization: {{ADO_ORG}}",
        "My ADO project: {{ADO_PROJECT}}",
        "Current process template: Basic (or Agile/Scrum/CMMI)",
        "",
        "Step 1 - Create an Inherited Process Template:",
        "  - Name: 'Security-Process'",
        "  - Inherit from: Basic (or my current template)",
        "  - Give me exact click-by-click steps in Organization",
        "    Settings -> Process",
        "",
        "Step 2 - Create these custom work item types:",
        "",
        "  Type A: SecurityAlert (Red, Shield icon)",
        "    Fields: AlertType (Text), Severity (Picklist:",
        "    critical/high/medium/low), SourceRepository (Text),",
        "    FilePath (Text), SecretType (Text), DetectedDate",
        "    (DateTime), RemediationOwner (Identity)",
        "    States: New -> Triaging -> Remediating -> Verified",
        "    -> Closed",
        "",
        "  Type B: Vulnerability (Orange, Bug icon)",
        "    Fields: CVEID (Text), CVSSScore (Decimal),",
        "    AttackVector (Picklist: Network/Adjacent/Local/Physical),",
        "    AffectedPackage (Text), FixVersion (Text),",
        "    ExploitAvailable (Picklist: Yes/No/Unknown)",
        "",
        "  Type C: ComplianceFinding (Blue, Clipboard icon)",
        "    Fields: ComplianceFramework (Picklist: SOC2/HIPAA/",
        "    PCI-DSS/FedRAMP/ISO27001/NIST/GDPR), ControlID (Text),",
        "    RiskRating (Picklist: Critical/High/Medium/Low/Info),",
        "    DueDate (DateTime), EvidenceLink (Text)",
        "",
        "Step 3 - Assign the process to my project:",
        "  - Change {{ADO_PROJECT}} to use 'Security-Process'",
        "",
        "Step 4 - Update the Logic App JSON:",
        "  - Change workItemType parameter to 'SecurityAlert'",
        "  - Add Custom.* field entries to HTTP_CreateWorkItem body",
        "  - Update HTTP_CloseWorkItem state to 'Closed'",
        "    (instead of 'Done')",
        "",
        "Give me exact steps for each part.",
    ])

    # ===== PROMPT 8: TROUBLESHOOTING =======================================
    pdf.section_title("9", "Prompt 8: Troubleshoot Issues")

    pdf.prompt_block("Troubleshoot GHAzDO-to-ADO Integration", [
        "I have a GHAzDO-to-ADO Logic App integration but I'm",
        "experiencing issues. Here is my setup:",
        "",
        "  - Logic App: {{LOGIC_APP_NAME}} in {{RESOURCE_GROUP}}",
        "  - ADO Org: {{ADO_ORG}}, Project: {{ADO_PROJECT}}",
        "  - Workflow: ghazdo-to-ado.json (218 lines, 4 params)",
        "  - Service Hooks: 2 (alert created + state changed)",
        "",
        "The problem I'm seeing is: [DESCRIBE YOUR ISSUE HERE]",
        "",
        "Common issues to check:",
        "  1. Work Item not created (401 or 400 errors)",
        "  2. Duplicate Work Items being created",
        "  3. Auto-close not working (state not changing to Done)",
        "  4. Service Hook test fails (timeout or 404)",
        "  5. PAT expired or wrong scopes",
        "  6. Push Protection blocking secret pushes",
        "",
        "Please help me:",
        "  1. Check the Logic App run history for errors",
        "  2. Identify the root cause",
        "  3. Give me the exact fix (what to change and where)",
        "  4. Verify the fix works",
    ])

    # ===== PROMPT 9: FULL END-TO-END IN ONE SHOT ===========================
    pdf.section_title("10", "Prompt 9: The Complete One-Shot Prompt")

    pdf.body(
        "This is the MEGA PROMPT -- a single prompt that asks Copilot to do everything "
        "end-to-end. Use this if you want Copilot to handle the entire setup in one go. "
        "Replace all {{PLACEHOLDERS}} with your actual values before pasting."
    )

    pdf.prompt_block("Complete E2E GHAzDO-to-ADO Setup", [
        "I need you to help me set up a complete, end-to-end",
        "GHAzDO-to-ADO Logic App integration that automatically",
        "creates ADO Work Items when GitHub Advanced Security for",
        "Azure DevOps (GHAzDO) detects security alerts (secrets,",
        "vulnerabilities, code scanning findings), and automatically",
        "closes those Work Items when alerts are resolved.",
        "",
        "My environment:",
        "  - Azure subscription (I have access to create resources)",
        "  - ADO Organization: {{ADO_ORG}}",
        "  - ADO Project: {{ADO_PROJECT}}",
        "  - GHAzDO is enabled on my ADO repositories",
        "  - ADO PAT: {{ADO_PAT}}",
        "    (scopes: Work Items Read/Write/Manage, Code Read)",
        "",
        "I have a JSON workflow file called ghazdo-to-ado.json",
        "(218 lines) that I will provide. It contains:",
        "  - 4 parameters: adoOrganization, adoProject, adoPat",
        "    (SecureString), workItemType (default: Issue)",
        "  - 1 HTTP trigger for receiving webhooks",
        "  - 9 Compose actions to extract/compute fields",
        "  - Conditions for create vs close routing",
        "  - HTTP actions to query, create, and close Work Items",
        "  - Tag-based deduplication (GHAzDO-repoName-alertId)",
        "  - Priority mapping: critical/high->1, medium->2, low->3",
        "",
        "Please do the following in order:",
        "",
        "PHASE 1 - Azure Setup:",
        "  1. Create a Logic App (Standard) in Azure Portal",
        "     Name: {{LOGIC_APP_NAME}}",
        "     Resource Group: {{RESOURCE_GROUP}}",
        "     Region: {{REGION}}",
        "  2. Create a Stateful workflow named 'ghas-ado-sync'",
        "  3. Open Code View and paste the ghazdo-to-ado.json",
        "  4. Configure all 4 parameters with my values",
        "  5. Save and get the Webhook URL",
        "",
        "PHASE 2 - ADO Service Hooks:",
        "  6. Create Service Hook 1: Advanced Security alert created",
        "     -> Web Hook -> POST to my Logic App webhook URL",
        "  7. Create Service Hook 2: Advanced Security alert state",
        "     changed -> Web Hook -> same URL",
        "  8. Test both hooks",
        "",
        "PHASE 3 - End-to-End Test:",
        "  9. Send a simulated 'alert created' webhook to verify",
        "     a Work Item gets created with correct title, tags,",
        "     priority, and HTML description",
        "  10. Send a simulated 'alert state changed' webhook to",
        "      verify the Work Item auto-closes to 'Done'",
        "",
        "PHASE 4 - Customization (optional):",
        "  11. Show me how to add custom fields",
        "      (AssignedTo, AreaPath, Custom.SecurityTool)",
        "  12. Show me how to create an inherited process template",
        "      with a custom 'SecurityAlert' work item type",
        "",
        "For each phase, give me exact step-by-step instructions",
        "with the exact buttons to click, fields to fill, and",
        "values to enter. Capture screenshots if possible.",
    ])

    pdf.tip_box(
        "This mega prompt works best with GitHub Copilot CLI (copilot-cli) which "
        "has Playwright browser automation capabilities. In VS Code Copilot Chat, "
        "it will provide step-by-step guidance instead of direct automation."
    )

    # ===== PROMPT QUICK REFERENCE ==========================================
    pdf.section_title("11", "Quick Reference: All Prompts at a Glance")

    w_qr = [15, 60, 115]
    pdf.table_row(["#", "Prompt Name", "What It Does"], w_qr, bold=True, fill=True)
    pdf.table_row(["1", "Create ADO PAT", "Creates a Personal Access Token with correct scopes"], w_qr)
    pdf.table_row(["2", "Create Logic App", "Creates the Azure Logic App resource in Azure Portal"], w_qr)
    pdf.table_row(["3", "Deploy Workflow JSON", "Pastes ghazdo-to-ado.json into Code View, configures params"], w_qr)
    pdf.table_row(["4", "Configure Service Hooks", "Creates 2 ADO webhooks (alert created + state changed)"], w_qr)
    pdf.table_row(["5", "Test Integration", "Sends test webhooks, verifies Work Item create + auto-close"], w_qr)
    pdf.table_row(["6", "Add Custom Fields", "Adds built-in and custom fields to Work Items"], w_qr)
    pdf.table_row(["7", "Custom Work Item Types", "Creates inherited process + SecurityAlert/Vulnerability types"], w_qr)
    pdf.table_row(["8", "Troubleshoot", "Diagnoses and fixes common integration issues"], w_qr)
    pdf.table_row(["9", "Complete One-Shot", "Does everything end-to-end in a single prompt"], w_qr)

    # ===== FILES REFERENCE =================================================
    pdf.section_title("12", "Files You Need")

    pdf.body("To use these prompts, you need the following files:")

    pdf.sub_heading("Required File")
    pdf.code_block([
        "ghazdo-to-ado.json",
        "  - The Logic App workflow JSON (218 lines)",
        "  - Contains 4 parameters you fill with your values",
        "  - Paste into Code View in the Logic App Designer",
        "  - This file should have been provided to you separately",
    ])

    pdf.sub_heading("Reference Documents (this package)")
    pdf.code_block([
        "Demo5-E2E-Setup-Guide.pdf",
        "  - Full step-by-step setup with 21 screenshots",
        "  - Complete walkthrough of every click",
        "",
        "GHAzDO-Customization-Guide.pdf",
        "  - How to add custom fields, types, and processes",
        "  - Inherited process template creation guide",
        "  - Custom states and workflow customization",
        "",
        "GHAzDO-Copilot-Prompt-Guide.pdf  (this file)",
        "  - Ready-to-use prompts for GitHub Copilot",
        "  - Copy, paste, replace placeholders, go",
    ])

    pdf.sub_heading("Other Available Documents")
    pdf.code_block([
        "ADO-Secret-Push-Step-By-Step.pdf",
        "  - How to push secrets and trigger GHAzDO detection",
        "",
        "Webhook-Troubleshooting-Guide.pdf",
        "  - Detailed troubleshooting for 4 common issues",
    ])

    # ===== FINAL PAGE ======================================================
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*MS_BLUE)
    pdf.cell(0, 12, safe("Ready to Go!"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*DARK_TEXT)
    pdf.multi_cell(0, 7, safe(
        "Copy any prompt from this guide, replace the {{PLACEHOLDERS}} "
        "with your actual values, paste it into GitHub Copilot, and let "
        "Copilot walk you through every step. The entire setup can be "
        "completed in under 30 minutes."
    ), align="C")

    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*MS_BLUE)
    pdf.cell(0, 8, safe("Recommended Order"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*DARK_TEXT)
    steps = [
        "Prompt 1: Create PAT  (5 min)",
        "Prompt 2: Create Logic App  (5 min)",
        "Prompt 3: Deploy JSON + Configure  (5 min)",
        "Prompt 4: Create Service Hooks  (5 min)",
        "Prompt 5: Test End-to-End  (5 min)",
        "Prompt 6+: Customize as needed  (optional)",
    ]
    for s in steps:
        pdf.cell(0, 7, safe(f"    {s}"), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*MS_BLUE)
    pdf.cell(0, 7, safe("Or use Prompt 9 (the mega prompt) to do it all at once!"),
             align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(15)
    pdf.set_draw_color(*MED_GRAY)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 6, safe("Confidential - Customer Ready"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, safe("GHAzDO-to-ADO Logic App Integration"), align="C",
             new_x="LMARGIN", new_y="NEXT")

    # ===== OUTPUT ==========================================================
    os.makedirs(DOCS_DIR, exist_ok=True)
    pdf.output(OUTPUT_PDF)
    size_kb = os.path.getsize(OUTPUT_PDF) / 1024
    print(f"PDF generated: {OUTPUT_PDF}")
    print(f"  Size: {size_kb:.0f} KB")


if __name__ == "__main__":
    print("Generating GHAzDO Copilot Prompt Guide PDF...")
    build_pdf()
    print("Done!")
