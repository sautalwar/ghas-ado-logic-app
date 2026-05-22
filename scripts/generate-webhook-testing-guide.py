#!/usr/bin/env python3
"""
Generate a beginner-friendly PDF guide for the Simulated Webhook testing method.
Explains every field, how to fill it, and how to run the curl command.
"""

import os
from fpdf import FPDF

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
OUTPUT_PDF = os.path.join(DOCS_DIR, "Simulated-Webhook-Testing-Guide.pdf")

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
FIELD_BG = (245, 248, 255)
FIELD_BORDER = (0, 90, 180)
PURPLE = (102, 51, 153)


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


class WebhookPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*MS_BLUE)
        self.cell(95, 8, safe("GHAzDO | Simulated Webhook Testing Guide"), align="L")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(95, 8, safe("Beginner-Friendly Guide"), align="R")
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
        self.cell(95, 10, safe("Simulated Webhook Testing Guide"), align="L")
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

    def blue_banner(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(*MS_BLUE)
        self.set_text_color(*WHITE)
        self.cell(0, 7, safe(f"  {text}"), fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*DARK_TEXT)
        self.ln(2)

    def field_card(self, field_name, json_key, field_type, required, description, example, what_it_does):
        """Render a visually distinct card explaining one JSON field."""
        self.ln(2)
        # Check space
        if self.get_y() > 230:
            self.add_page()

        # Card header
        self.set_fill_color(*FIELD_BG)
        self.set_draw_color(*FIELD_BORDER)
        x0 = self.get_x()
        y0 = self.get_y()

        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*FIELD_BORDER)
        req_tag = " (REQUIRED)" if required else " (optional)"
        self.cell(0, 6, safe(f"  {field_name}{req_tag}"), fill=True,
                  new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DARK_TEXT)

        # Use stacked layout: label on own line, value indented below
        items = [
            ("JSON Key:", json_key),
            ("Type:", field_type),
            ("Description:", description),
            ("Example:", example),
            ("What It Does:", what_it_does),
        ]
        for label, val in items:
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(*FIELD_BORDER)
            self.cell(0, 5, safe(f"  {label}"), fill=True,
                      new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "", 9)
            self.set_text_color(*DARK_TEXT)
            self.set_x(self.l_margin + 6)
            w = self.w - self.r_margin - self.get_x()
            self.multi_cell(w, 5, safe(val), fill=True)

        y1 = self.get_y()
        self.set_line_width(0.6)
        self.line(x0, y0, x0, y1)
        self.set_line_width(0.2)
        self.set_draw_color(*MED_GRAY)
        self.ln(2)


def build_pdf():
    pdf = WebhookPDF()

    # ===== TITLE PAGE ======================================================
    pdf.add_page()
    pdf.set_fill_color(*MS_BLUE)
    pdf.rect(0, 0, 210, 115, "F")

    pdf.set_y(18)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 14, safe("Simulated Webhook"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 12, safe("Testing Guide"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 8, safe("How to Test Your GHAzDO-to-ADO Integration"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, safe("Without Pushing Real Secrets"), align="C",
             new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(125)
    pdf.set_text_color(*DARK_TEXT)
    pdf.set_font("Helvetica", "", 11)
    info = [
        ("Document Type", "Beginner-Friendly Testing Guide"),
        ("Audience", "Anyone testing the Logic App integration"),
        ("Skill Level", "No prior curl or API experience needed"),
        ("Tools Needed", "curl (built into Windows/Mac/Linux), or Postman"),
        ("Time to Complete", "5-10 minutes"),
        ("Date", "March 2026"),
    ]
    for label, val in info:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(50, 8, safe(f"  {label}:"))
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, safe(val), new_x="LMARGIN", new_y="NEXT")

    # ===== SECTION 1: WHAT IS A SIMULATED WEBHOOK ==========================
    pdf.section_title("1", "What is a Simulated Webhook?")

    pdf.body(
        "When GHAzDO (GitHub Advanced Security for Azure DevOps) detects a security "
        "issue in your code -- like an exposed secret, a vulnerable dependency, or a "
        "code scanning finding -- it sends a message called a WEBHOOK to your Logic App. "
        "This webhook is just an HTTP request containing information about the alert."
    )

    pdf.body(
        "A SIMULATED webhook is when YOU send that same HTTP request manually, "
        "pretending to be GHAzDO. This lets you test that your Logic App is working "
        "correctly WITHOUT having to actually push real secrets to your repository."
    )

    pdf.sub_heading("Why Use Simulated Webhooks?")
    pdf.bullet("SAFER -- No real secrets are exposed in your codebase")
    pdf.bullet("FASTER -- No waiting for GHAzDO to scan (instant results)")
    pdf.bullet("REPEATABLE -- Same test every time, predictable results")
    pdf.bullet("DEMO-FRIENDLY -- Perfect for customer demonstrations")
    pdf.bullet("NO PUSH PROTECTION ISSUES -- GHAzDO may block real secret pushes")

    pdf.sub_heading("How It Works (Simple Diagram)")
    pdf.code_block([
        "Normal Flow:",
        "  You push code -> GHAzDO scans -> GHAzDO sends webhook -> Logic App",
        "",
        "Simulated Flow:",
        "  You run a curl command -> sends webhook directly -> Logic App",
        "",
        "The Logic App cannot tell the difference! It processes both",
        "the same way and creates the same ADO Work Item.",
    ])

    # ===== SECTION 2: WHAT YOU NEED ========================================
    pdf.section_title("2", "What You Need Before Starting")

    pdf.body("Before you can send a simulated webhook, gather these three things:")

    pdf.blue_banner("Item 1: Your Logic App Webhook URL")
    pdf.body(
        "This is the URL that your Logic App listens on. You got this when you "
        "deployed the Logic App workflow. It looks like this:"
    )
    pdf.code_block([
        "https://prod-XX.eastus.logic.azure.com:443/workflows/...",
        "  /triggers/When_a_GHAzDO_alert_is_received/paths/invoke",
        "  ?api-version=2019-05-01&sp=...&sv=1.0&sig=...",
    ])
    pdf.body("How to find it if you lost it:")
    pdf.numbered_step(1, "Go to portal.azure.com")
    pdf.numbered_step(2, "Open your Logic App resource")
    pdf.numbered_step(3, "Click on Workflows -> your workflow name")
    pdf.numbered_step(4, 'Click "Overview"')
    pdf.numbered_step(5, 'Find "Workflow URL" -- copy the entire URL')

    pdf.warning_box(
        "This URL is a SECRET. Anyone with this URL can trigger your Logic App. "
        "Do not share it in emails, chat, or public channels. Treat it like a password."
    )

    pdf.blue_banner("Item 2: A Terminal / Command Prompt")
    pdf.body("You need a way to run the curl command:")
    pdf.bullet("Windows: Open PowerShell or Command Prompt (search 'cmd' or 'PowerShell')")
    pdf.bullet("Mac: Open Terminal (Applications -> Utilities -> Terminal)")
    pdf.bullet("Linux: Open your terminal emulator")
    pdf.bullet("Alternative: Use Postman (a free GUI tool) -- see Section 8")

    pdf.blue_banner("Item 3: Your Test Values")
    pdf.body(
        "Decide what values to put in your test webhook. The next section explains "
        "every field in detail so you know exactly what to fill in."
    )

    # ===== SECTION 3: THE COMPLETE PAYLOAD EXPLAINED =======================
    pdf.section_title("3", "The Webhook Payload -- Every Field Explained")

    pdf.body(
        "The simulated webhook is a JSON object (a structured data format) that you "
        "send to the Logic App. Below is the COMPLETE payload with every field "
        "explained. Fields you MUST fill in are marked REQUIRED. Fields you CAN "
        "change are marked optional."
    )

    pdf.sub_heading("The Full JSON Payload")
    pdf.code_block([
        '{',
        '  "eventType": "ms.vss-alerts.alert-created-event",',
        '  "resource": {',
        '    "alertId": 999,',
        '    "alertType": "secret",',
        '    "severity": "critical",',
        '    "repository": { "name": "my-repo" },',
        '    "location": {',
        '      "file": "test-config.env",',
        '      "startLine": 1',
        '    },',
        '    "secretType": "Azure Storage Account Key",  <-- just a label!',
        '    "link": "https://dev.azure.com/myorg/myproject"',
        '  },',
        '  "resourceContainers": {',
        '    "project": { "name": "MyProject" }',
        '  }',
        '}',
    ])

    pdf.warning_box(
        'IMPORTANT: "secretType" is just a TEXT LABEL, not a real secret! '
        'You are NOT putting an actual Azure Storage key in the JSON. '
        'The value "Azure Storage Account Key" is simply a description that '
        'will appear in the Work Item title. You can change it to anything you want, '
        'like "Test Secret" or "Database Password".'
    )

    pdf.body("Now let us go through EVERY field one by one:")

    # --- Field cards ---
    pdf.field_card(
        field_name="eventType",
        json_key='"eventType"',
        field_type="Text string",
        required=True,
        description="Tells the Logic App what kind of event happened.",
        example='"ms.vss-alerts.alert-created-event"',
        what_it_does=(
            "The Logic App checks this value to decide whether to CREATE a new "
            "Work Item or CLOSE an existing one. Use the exact value shown."
        ),
    )

    pdf.body("Allowed values for eventType:")
    w_ev = [90, 100]
    pdf.table_row(["eventType Value", "What It Does"], w_ev, bold=True, fill=True)
    pdf.table_row([
        "ms.vss-alerts.alert-created-event",
        "Creates a NEW Work Item in ADO"
    ], w_ev)
    pdf.table_row([
        "ms.vss-alerts.alert-state-changed-event",
        "Closes an EXISTING Work Item (auto-close)"
    ], w_ev)

    pdf.field_card(
        field_name="alertId",
        json_key='"resource" -> "alertId"',
        field_type="Number (integer)",
        required=True,
        description="A unique number identifying this specific alert.",
        example="999 (any number you choose)",
        what_it_does=(
            "Used to create the unique tag 'GHAzDO-repoName-999' on the Work Item. "
            "This tag prevents duplicates and enables auto-close. Use a different number "
            "each time you test to create separate Work Items."
        ),
    )

    pdf.tip_box(
        "Use a different alertId each time you run a test. If you use the same alertId "
        "and repo name, the Logic App will detect a duplicate and skip creating a new "
        "Work Item. Try 999, 1000, 1001, etc."
    )

    pdf.field_card(
        field_name="alertType",
        json_key='"resource" -> "alertType"',
        field_type="Text string",
        required=True,
        description="The category of security alert that was found.",
        example='"secret"',
        what_it_does=(
            "Determines the Work Item title prefix and tag. "
            "secret -> [GHAzDO-Secret], code -> [GHAzDO-CodeScan], "
            "dependency -> [GHAzDO-Dependency]."
        ),
    )

    pdf.body("Allowed values for alertType:")
    w_at = [40, 60, 90]
    pdf.table_row(["alertType", "Title Prefix", "When GHAzDO Uses It"], w_at, bold=True, fill=True)
    pdf.table_row(["secret", "[GHAzDO-Secret]", "Exposed API keys, passwords, tokens, etc."], w_at)
    pdf.table_row(["code", "[GHAzDO-CodeScan]", "Code scanning / SAST findings"], w_at)
    pdf.table_row(["dependency", "[GHAzDO-Dependency]", "Vulnerable packages / SCA findings"], w_at)

    pdf.field_card(
        field_name="severity",
        json_key='"resource" -> "severity"',
        field_type="Text string",
        required=True,
        description="How severe / urgent is this security issue.",
        example='"critical"',
        what_it_does=(
            "Maps to the Work Item Priority field. "
            "critical/high -> Priority 1, medium -> Priority 2, low -> Priority 3. "
            "Also added as a tag for filtering."
        ),
    )

    pdf.body("Allowed values for severity:")
    w_sv = [40, 50, 100]
    pdf.table_row(["severity", "ADO Priority", "Meaning"], w_sv, bold=True, fill=True)
    pdf.table_row(["critical", "1 - Critical", "Immediate action required (exposed production key)"], w_sv)
    pdf.table_row(["high", "1 - Critical", "Urgent action needed (high-risk vulnerability)"], w_sv)
    pdf.table_row(["medium", "2 - High", "Should be addressed soon"], w_sv)
    pdf.table_row(["low", "3 - Medium", "Plan to address (informational)"], w_sv)

    pdf.field_card(
        field_name="repository name",
        json_key='"resource" -> "repository" -> "name"',
        field_type="Text string",
        required=True,
        description="The name of the ADO repository where the alert was found.",
        example='"my-repo" (use your actual repo name)',
        what_it_does=(
            "Appears in the Work Item description and is part of the unique tag "
            "(GHAzDO-reponame-alertId). Use your real repo name for realistic tests."
        ),
    )

    pdf.field_card(
        field_name="file",
        json_key='"resource" -> "location" -> "file"',
        field_type="Text string",
        required=False,
        description="The file path where the security issue was found.",
        example='"test-config.env" or "src/database/connection.py"',
        what_it_does=(
            "Shows up in the Work Item description so the developer knows exactly "
            "which file to fix. Use a realistic file path for demos."
        ),
    )

    pdf.field_card(
        field_name="startLine",
        json_key='"resource" -> "location" -> "startLine"',
        field_type="Number (integer)",
        required=False,
        description="The line number in the file where the issue was found.",
        example="1 (or any line number)",
        what_it_does=(
            "Shows in the Work Item description. Helps developers find the exact "
            "location of the issue. Use 1 for simple tests."
        ),
    )

    pdf.field_card(
        field_name="secretType",
        json_key='"resource" -> "secretType"',
        field_type="Text string",
        required=False,
        description=(
            "This is just a LABEL that describes what KIND of secret was found. "
            "You do NOT need an actual Azure Storage key or any real secret. "
            "This is simply a text description that appears in the Work Item title."
        ),
        example=(
            '"Azure Storage Account Key" -- This is just a label/name. '
            "You are NOT pasting a real key here. You can type anything, "
            'like "Test Secret" or "Database Password".'
        ),
        what_it_does=(
            "Becomes part of the Work Item title for secret alerts. "
            'Example: the title will be "[GHAzDO-Secret] Azure Storage Account Key". '
            "This helps the security team instantly see what type of secret was leaked. "
            "You can use ANY text here -- pick from the list below or make up your own."
        ),
    )

    pdf.warning_box(
        'The "secretType" field is NOT a real secret! It is just a description/label. '
        "You do NOT need to go find an Azure Storage Account Key or any real credential. "
        'Just type a text description like "Azure Storage Account Key" or "API Token" '
        "and it will show up in the Work Item title."
    )

    pdf.body("Common secretType label values you can use (pick any one):")
    w_st = [95, 95]
    pdf.table_row(["secretType Label", "What It Describes"], w_st, bold=True, fill=True)
    pdf.table_row(["Azure Storage Account Key", "A leaked Azure storage access key"], w_st)
    pdf.table_row(["Azure AD Client Secret", "A leaked app registration credential"], w_st)
    pdf.table_row(["AWS Access Key ID", "A leaked Amazon Web Services key"], w_st)
    pdf.table_row(["GitHub Personal Access Token", "A leaked GitHub API token"], w_st)
    pdf.table_row(["SQL Connection String", "A leaked database connection string"], w_st)
    pdf.table_row(["Stripe Live API Key", "A leaked payment processing API key"], w_st)
    pdf.table_row(["SendGrid API Key", "A leaked email service API key"], w_st)
    pdf.table_row(["Generic Password", "Any exposed password in code"], w_st)
    pdf.table_row(["My Test Secret", "You can use ANY text you want!"], w_st)

    pdf.field_card(
        field_name="link",
        json_key='"resource" -> "link"',
        field_type="Text string (a URL)",
        required=False,
        description=(
            "A URL that links back to the alert details page in GHAzDO. "
            "For testing, you can use ANY URL or a placeholder."
        ),
        example=(
            '"https://dev.azure.com/myorg/myproject/_git/myrepo/alerts/999" '
            "-- Replace myorg, myproject, myrepo with your real values, or just "
            'use "https://dev.azure.com" as a placeholder.'
        ),
        what_it_does=(
            "Creates a clickable link in the Work Item description that says "
            "'View Alert in Azure DevOps'. When someone clicks it, they go to "
            "the GHAzDO alert page. For tests, the URL does not need to be valid "
            "-- it just shows up as a link in the description."
        ),
    )

    pdf.field_card(
        field_name="project name",
        json_key='"resourceContainers" -> "project" -> "name"',
        field_type="Text string",
        required=False,
        description=(
            "Your ADO project name. This is the same project where the Work Item "
            "will be created. Used for reference/logging."
        ),
        example=(
            '"MyProject" -- Replace with YOUR actual ADO project name '
            "(the same one you configured in the Logic App parameters)."
        ),
        what_it_does=(
            "Used for informational logging in the Logic App. Does not affect "
            "the Work Item creation. Use your real project name for clarity."
        ),
    )

    # ===== SECTION 4: STEP-BY-STEP CURL ====================================
    pdf.section_title("4", 'Step-by-Step: Running the curl Command')

    pdf.body(
        "Now that you understand every field, let us build and run the actual curl "
        "command. Follow these steps exactly."
    )

    pdf.sub_heading("Step 1: Open Your Terminal")
    pdf.body("Open PowerShell (Windows), Terminal (Mac), or your terminal (Linux).")

    pdf.sub_heading("Step 2: Copy This Command")
    pdf.body(
        "Copy the ENTIRE command below. Then replace the two placeholder values "
        "(marked with << >>)."
    )

    pdf.blue_banner("For Windows PowerShell")
    pdf.code_block([
        '$webhookUrl = "<<PASTE YOUR WEBHOOK URL HERE>>"',
        "",
        '$body = @"',
        "{",
        '  "eventType": "ms.vss-alerts.alert-created-event",',
        '  "resource": {',
        '    "alertId": 999,',
        '    "alertType": "secret",',
        '    "severity": "critical",',
        '    "repository": { "name": "<<YOUR-REPO-NAME>>" },',
        '    "location": {',
        '      "file": "test-secrets/config.env",',
        '      "startLine": 1',
        "    },",
        '    "secretType": "Azure Storage Account Key",',
        '    "link": "https://dev.azure.com/your-org/your-project"',
        "  },",
        '  "resourceContainers": {',
        '    "project": { "name": "<<YOUR-PROJECT-NAME>>" }',
        "  }",
        "}",
        '"@',
        "",
        "Invoke-RestMethod -Uri $webhookUrl ``",
        '  -Method POST ``',
        '  -ContentType "application/json" ``',
        "  -Body $body",
    ])

    pdf.blue_banner("For Mac / Linux / Git Bash")
    pdf.code_block([
        "curl -X POST '<<PASTE YOUR WEBHOOK URL HERE>>' \\",
        '  -H "Content-Type: application/json" \\',
        "  -d '{",
        '  \"eventType\": \"ms.vss-alerts.alert-created-event\",',
        '  \"resource\": {',
        '    \"alertId\": 999,',
        '    \"alertType\": \"secret\",',
        '    \"severity\": \"critical\",',
        '    \"repository\": { \"name\": \"<<YOUR-REPO-NAME>>\" },',
        '    \"location\": {',
        '      \"file\": \"test-secrets/config.env\",',
        '      \"startLine\": 1',
        "    },",
        '    \"secretType\": \"Azure Storage Account Key\",',
        '    \"link\": \"https://dev.azure.com/your-org/your-project\"',
        "  },",
        '  \"resourceContainers\": {',
        '    \"project\": { \"name\": \"<<YOUR-PROJECT-NAME>>\" }',
        "  }",
        "}'",
    ])

    pdf.sub_heading("Step 3: Replace the Placeholders")
    pdf.body("You need to replace THREE things in the command:")

    w_ph = [55, 55, 80]
    pdf.table_row(["Placeholder", "Replace With", "Example"], w_ph, bold=True, fill=True)
    pdf.table_row([
        "<<WEBHOOK URL>>",
        "Your Logic App webhook URL",
        "https://prod-93.eastus..."
    ], w_ph)
    pdf.table_row([
        "<<YOUR-REPO-NAME>>",
        "Your ADO repository name",
        "brandsafwy_repo"
    ], w_ph)
    pdf.table_row([
        "<<YOUR-PROJECT-NAME>>",
        "Your ADO project name",
        "brandsafway_Engg"
    ], w_ph)

    pdf.sub_heading("Step 4: Run the Command")
    pdf.body(
        "Paste the modified command into your terminal and press Enter. "
        "You should see a response within a few seconds."
    )

    pdf.sub_heading("Step 5: Check the Response")
    pdf.body("What you see after running the command:")

    w_resp = [60, 130]
    pdf.table_row(["Response", "What It Means"], w_resp, bold=True, fill=True)
    pdf.table_row([
        "Empty / 202 Accepted",
        "SUCCESS! Logic App received the webhook and is processing it."
    ], w_resp)
    pdf.table_row([
        "404 Not Found",
        "Wrong URL. Re-copy the webhook URL from Logic App Overview."
    ], w_resp)
    pdf.table_row([
        "401 / 403 Unauthorized",
        "URL signature expired. Get a new URL from Logic App Overview."
    ], w_resp)
    pdf.table_row([
        "Connection refused",
        "Logic App may be disabled. Enable it in Azure Portal."
    ], w_resp)

    # ===== SECTION 5: VERIFY RESULTS =======================================
    pdf.section_title("5", "Verifying the Results")

    pdf.body(
        "After running the curl command successfully, verify that the Work Item was "
        "created in ADO."
    )

    pdf.sub_heading("Check 1: Logic App Run History")
    pdf.numbered_step(1, "Go to portal.azure.com -> your Logic App")
    pdf.numbered_step(2, "Click Workflows -> your workflow")
    pdf.numbered_step(3, 'Click "Run History" (or "Monitor")')
    pdf.numbered_step(4, 'You should see a run with Status = "Succeeded" and a green checkmark')
    pdf.numbered_step(5, "Click the run to see details of each action")

    pdf.body("If the run shows 'Failed' (red X), click on it to see which action failed and the error message.")

    pdf.sub_heading("Check 2: ADO Work Item")
    pdf.numbered_step(1, "Go to dev.azure.com/{your-org}/{your-project}")
    pdf.numbered_step(2, 'Click "Boards" in the left sidebar')
    pdf.numbered_step(3, 'Click "Work Items"')
    pdf.numbered_step(4, "Look for a new Work Item with the title:")
    pdf.code_block([
        "[GHAzDO-Secret] Azure Storage Account Key",
    ])
    pdf.numbered_step(5, "Click to open it and verify:")
    pdf.bullet("Title contains [GHAzDO-Secret] and the secret type")
    pdf.bullet("Tags include: GHAzDO, secret, critical, GHAzDO-my-repo-999")
    pdf.bullet("Priority = 1 (since severity was 'critical')")
    pdf.bullet("Description has an HTML table with alert details")
    pdf.bullet("State = To Do (or New)")

    # ===== SECTION 6: TESTING AUTO-CLOSE ===================================
    pdf.section_title("6", "Testing Auto-Close (Alert State Changed)")

    pdf.body(
        "Now let us test the second half of the integration: when a GHAzDO alert is "
        "resolved (the secret is removed or rotated), the Work Item should automatically "
        "close. To simulate this, send a DIFFERENT webhook with the 'state changed' event type."
    )

    pdf.sub_heading("The Auto-Close Payload")
    pdf.body(
        "This payload is SIMPLER than the create payload. The key difference is the "
        "eventType value."
    )

    pdf.code_block([
        '{',
        '  "eventType": "ms.vss-alerts.alert-state-changed-event",',
        '  "resource": {',
        '    "alertId": 999,',
        '    "alertType": "secret",',
        '    "severity": "critical",',
        '    "repository": { "name": "my-repo" },',
        '    "state": "fixed"',
        '  },',
        '  "resourceContainers": {',
        '    "project": { "name": "MyProject" }',
        '  }',
        '}',
    ])

    pdf.warning_box(
        "The alertId and repository name MUST MATCH the ones you used in the 'alert "
        "created' webhook (Step 4). The Logic App uses these to find the matching Work "
        "Item via the tag GHAzDO-my-repo-999. If they don't match, the Logic App won't "
        "find the Work Item to close."
    )

    pdf.sub_heading("Auto-Close Command (PowerShell)")
    pdf.code_block([
        '$webhookUrl = "<<SAME WEBHOOK URL AS BEFORE>>"',
        "",
        '$body = @"',
        "{",
        '  "eventType": "ms.vss-alerts.alert-state-changed-event",',
        '  "resource": {',
        '    "alertId": 999,',
        '    "alertType": "secret",',
        '    "severity": "critical",',
        '    "repository": { "name": "<<SAME-REPO-NAME>>" },',
        '    "state": "fixed"',
        "  },",
        '  "resourceContainers": {',
        '    "project": { "name": "<<YOUR-PROJECT-NAME>>" }',
        "  }",
        "}",
        '"@',
        "",
        "Invoke-RestMethod -Uri $webhookUrl ``",
        '  -Method POST ``',
        '  -ContentType "application/json" ``',
        "  -Body $body",
    ])

    pdf.sub_heading("Auto-Close Command (Mac / Linux / Git Bash)")
    pdf.code_block([
        "curl -X POST '<<SAME WEBHOOK URL>>' \\",
        '  -H "Content-Type: application/json" \\',
        "  -d '{",
        '  \"eventType\": \"ms.vss-alerts.alert-state-changed-event\",',
        '  \"resource\": {',
        '    \"alertId\": 999,',
        '    \"alertType\": \"secret\",',
        '    \"severity\": \"critical\",',
        '    \"repository\": { \"name\": \"<<SAME-REPO-NAME>>\" },',
        '    \"state\": \"fixed\"',
        "  },",
        '  \"resourceContainers\": {',
        '    \"project\": { \"name\": \"<<YOUR-PROJECT-NAME>>\" }',
        "  }",
        "}'",
    ])

    pdf.sub_heading("Verify Auto-Close")
    pdf.numbered_step(1, "Go back to the Work Item you found in Section 5")
    pdf.numbered_step(2, 'State should now be "Done"')
    pdf.numbered_step(3, 'Check the History/Comments -- you should see: "Auto-closed: GHAzDO alert resolved/fixed."')

    # ===== SECTION 7: DIFFERENT TEST SCENARIOS =============================
    pdf.section_title("7", "Ready-Made Test Scenarios")

    pdf.body(
        "Here are several pre-built test payloads for different scenarios. "
        "Just copy the JSON, replace the webhook URL, and run."
    )

    pdf.sub_heading("Scenario A: Exposed AWS Key (Critical)")
    pdf.code_block([
        '{',
        '  "eventType": "ms.vss-alerts.alert-created-event",',
        '  "resource": {',
        '    "alertId": 1001,',
        '    "alertType": "secret",',
        '    "severity": "critical",',
        '    "repository": { "name": "backend-api" },',
        '    "location": { "file": "deploy/aws-config.yml", "startLine": 12 },',
        '    "secretType": "AWS Access Key ID",',
        '    "link": "https://dev.azure.com/myorg/myproject"',
        '  },',
        '  "resourceContainers": { "project": { "name": "MyProject" } }',
        '}',
    ])

    pdf.sub_heading("Scenario B: Vulnerable NPM Package (High)")
    pdf.code_block([
        '{',
        '  "eventType": "ms.vss-alerts.alert-created-event",',
        '  "resource": {',
        '    "alertId": 1002,',
        '    "alertType": "dependency",',
        '    "severity": "high",',
        '    "repository": { "name": "web-frontend" },',
        '    "location": { "file": "package-lock.json", "startLine": 458 },',
        '    "title": "Prototype Pollution in lodash < 4.17.21",',
        '    "advisoryTitle": "CVE-2021-23337",',
        '    "link": "https://dev.azure.com/myorg/myproject"',
        '  },',
        '  "resourceContainers": { "project": { "name": "MyProject" } }',
        '}',
    ])

    pdf.sub_heading("Scenario C: SQL Injection Code Finding (Medium)")
    pdf.code_block([
        '{',
        '  "eventType": "ms.vss-alerts.alert-created-event",',
        '  "resource": {',
        '    "alertId": 1003,',
        '    "alertType": "code",',
        '    "severity": "medium",',
        '    "repository": { "name": "api-service" },',
        '    "location": { "file": "src/db/queries.py", "startLine": 42 },',
        '    "title": "SQL Injection via string concatenation",',
        '    "rule": { "description": "Potential SQL injection" },',
        '    "link": "https://dev.azure.com/myorg/myproject"',
        '  },',
        '  "resourceContainers": { "project": { "name": "MyProject" } }',
        '}',
    ])

    pdf.sub_heading("Scenario D: Low-Severity Info Leak")
    pdf.code_block([
        '{',
        '  "eventType": "ms.vss-alerts.alert-created-event",',
        '  "resource": {',
        '    "alertId": 1004,',
        '    "alertType": "secret",',
        '    "severity": "low",',
        '    "repository": { "name": "docs-repo" },',
        '    "location": { "file": "examples/sample.env", "startLine": 3 },',
        '    "secretType": "Generic Password",',
        '    "link": "https://dev.azure.com/myorg/myproject"',
        '  },',
        '  "resourceContainers": { "project": { "name": "MyProject" } }',
        '}',
    ])

    # ===== SECTION 8: USING POSTMAN ========================================
    pdf.section_title("8", "Alternative: Using Postman (No Command Line)")

    pdf.body(
        "If you prefer a graphical interface instead of the command line, you can use "
        "Postman (a free tool) to send the simulated webhook."
    )

    pdf.numbered_step(1, "Download and install Postman from https://www.postman.com/downloads/")
    pdf.numbered_step(2, "Open Postman and click 'New' -> 'HTTP Request'")
    pdf.numbered_step(3, "Set the method to POST (dropdown on the left)")
    pdf.numbered_step(4, "Paste your Logic App webhook URL in the URL field")
    pdf.numbered_step(5, 'Click the "Headers" tab and add:')
    pdf.code_block([
        "Key:   Content-Type",
        "Value: application/json",
    ])
    pdf.numbered_step(6, 'Click the "Body" tab')
    pdf.numbered_step(7, 'Select "raw" and choose "JSON" from the dropdown')
    pdf.numbered_step(8, "Paste the JSON payload (from Section 3 or Section 7)")
    pdf.numbered_step(9, 'Click the blue "Send" button')
    pdf.numbered_step(10, 'You should see "202 Accepted" in the response area')

    pdf.tip_box(
        "Postman lets you SAVE requests for reuse. Create a collection called "
        "'GHAzDO Tests' and save each scenario as a separate request. This makes "
        "demos quick and repeatable."
    )

    # ===== SECTION 9: TROUBLESHOOTING ======================================
    pdf.section_title("9", "Troubleshooting")

    pdf.sub_heading("Problem: 'curl is not recognized'")
    pdf.body("On Windows, use PowerShell with Invoke-RestMethod instead of curl. "
             "Or install curl from https://curl.se/download.html")

    pdf.sub_heading("Problem: 'The request body must not be empty'")
    pdf.body("The -d flag (body) is missing or empty. Make sure you copied the full command.")

    pdf.sub_heading("Problem: Logic App ran but no Work Item created")
    pdf.body("Check the Logic App run history. Click on the failed run and expand each action. "
             "The most common cause is an expired or invalid ADO PAT.")

    pdf.sub_heading("Problem: Duplicate Work Item not created (expected)")
    pdf.body(
        "This is CORRECT behavior! If you use the same alertId + repo name twice, "
        "the Logic App detects the duplicate via the tag and skips creation. "
        "Use a different alertId to create a new Work Item."
    )

    pdf.sub_heading("Problem: Auto-close did not work")
    pdf.body(
        "Make sure the alertId and repository name in the state-changed webhook "
        "EXACTLY match the ones in the alert-created webhook. The Logic App searches "
        "by tag (GHAzDO-reponame-alertId) and both must match."
    )

    # ===== FINAL PAGE ======================================================
    pdf.add_page()
    pdf.ln(25)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*MS_BLUE)
    pdf.cell(0, 12, safe("Quick Cheat Sheet"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*DARK_TEXT)

    steps_summary = [
        ("1.", "Get your webhook URL from Logic App Overview"),
        ("2.", "Open PowerShell (Windows) or Terminal (Mac/Linux)"),
        ("3.", "Copy the curl/PowerShell command from Section 4"),
        ("4.", "Replace <<WEBHOOK URL>>, <<REPO-NAME>>, <<PROJECT-NAME>>"),
        ("5.", "Run the command -- you should get 202 Accepted"),
        ("6.", "Check ADO Boards -> Work Items for the new item"),
        ("7.", "To test auto-close: run the state-changed command (Section 6)"),
        ("8.", "Verify the Work Item state changed to 'Done'"),
    ]
    for num, text in steps_summary:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*MS_BLUE)
        pdf.cell(10, 7, safe(num))
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*DARK_TEXT)
        pdf.cell(0, 7, safe(text), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(15)
    pdf.set_draw_color(*MED_GRAY)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 6, safe("Confidential - Customer Guide"), align="C",
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
    print("Generating Simulated Webhook Testing Guide PDF...")
    build_pdf()
    print("Done!")
