"""
Generates the Logic App Designer Walkthrough PDF using fpdf2.
Covers the end-to-end flow: webhook input → Logic App processing → ADO output.
"""

from fpdf import FPDF
from pathlib import Path
import os

REPO_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS = REPO_ROOT / "docs" / "screenshots"
PDF_FILE = REPO_ROOT / "docs" / "Logic-App-Designer-Walkthrough.pdf"

BLUE = (0, 120, 212)
DARK = (30, 30, 30)
GRAY = (100, 100, 100)
LIGHT_BG = (240, 246, 255)
CODE_BG = (245, 245, 245)
WHITE = (255, 255, 255)
TABLE_HEADER_BG = (0, 120, 212)
TABLE_ALT_BG = (248, 249, 250)
TIP_BG = (255, 249, 235)
TIP_BORDER = (255, 183, 0)
GREEN = (16, 124, 16)
GREEN_BG = (232, 255, 232)
RED = (200, 30, 30)
RED_BG = (255, 235, 235)
SECTION_LINE = (208, 208, 208)
PURPLE = (100, 50, 150)


class WalkthroughPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(20, 20, 20)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*GRAY)
            self.cell(0, 5, "GHAS-ADO Logic App - Designer Walkthrough", align="R")
            self.ln(2)
            self.set_draw_color(*SECTION_LINE)
            self.line(20, self.get_y(), 190, self.get_y())
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def phase_title(self, num, title):
        self.ln(4)
        if self.get_y() > 245:
            self.add_page()
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*BLUE)
        self.cell(0, 12, f"Phase {num}: {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*BLUE)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(4)

    def step_title(self, title):
        self.ln(2)
        if self.get_y() > 255:
            self.add_page()
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*DARK)
        self.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def sub_step(self, title):
        self.ln(1)
        if self.get_y() > 260:
            self.add_page()
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(60, 60, 60)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bold(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def click_step(self, num, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*BLUE)
        x = self.get_x()
        self.cell(8, 6, f"{num}.", align="R")
        self.set_x(x + 10)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        self.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def info_box(self, title, text):
        self.ln(2)
        if self.get_y() > 240:
            self.add_page()
        y_start = self.get_y()
        self.set_fill_color(*LIGHT_BG)
        self.set_font("Helvetica", "", 9.5)
        lines = len(text) / 80 + text.count('\n') + 2
        h = max(lines * 5 + 12, 16)
        self.rect(20, y_start, 170, h, "F")
        self.set_fill_color(*BLUE)
        self.rect(20, y_start, 1.5, h, "F")
        self.set_xy(24, y_start + 2)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*BLUE)
        self.cell(0, 5, title)
        self.set_xy(24, y_start + 8)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(50, 50, 50)
        self.multi_cell(162, 5, text)
        self.set_y(y_start + h + 2)

    def warn_box(self, text):
        self.ln(2)
        if self.get_y() > 240:
            self.add_page()
        y_start = self.get_y()
        self.set_fill_color(*TIP_BG)
        self.set_font("Helvetica", "", 9.5)
        lines = len(text) / 80 + text.count('\n') + 2
        h = max(lines * 5 + 8, 14)
        self.rect(20, y_start, 170, h, "F")
        self.set_fill_color(*TIP_BORDER)
        self.rect(20, y_start, 1.5, h, "F")
        self.set_xy(24, y_start + 3)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(180, 130, 0)
        self.cell(6, 5, "!")
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(80, 60, 0)
        self.multi_cell(158, 5, text)
        self.set_y(y_start + h + 2)

    def success_box(self, text):
        self.ln(2)
        if self.get_y() > 240:
            self.add_page()
        y_start = self.get_y()
        self.set_fill_color(*GREEN_BG)
        self.set_font("Helvetica", "", 9.5)
        lines = len(text) / 80 + text.count('\n') + 2
        h = max(lines * 5 + 8, 14)
        self.rect(20, y_start, 170, h, "F")
        self.set_fill_color(*GREEN)
        self.rect(20, y_start, 1.5, h, "F")
        self.set_xy(24, y_start + 3)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*GREEN)
        self.cell(6, 5, "+")
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(20, 80, 20)
        self.multi_cell(158, 5, text)
        self.set_y(y_start + h + 2)

    def code_block(self, text):
        self.ln(1)
        if self.get_y() > 245:
            self.add_page()
        y_start = self.get_y()
        self.set_fill_color(*CODE_BG)
        self.set_font("Courier", "", 8)
        lines = text.split('\n')
        h = len(lines) * 4.2 + 6
        if y_start + h > 270:
            self.add_page()
            y_start = self.get_y()
        self.rect(22, y_start, 166, h, "F")
        self.set_xy(25, y_start + 3)
        self.set_text_color(60, 60, 60)
        for line in lines:
            if self.get_y() > 275:
                self.add_page()
                self.set_x(25)
            self.cell(0, 4.2, line, new_x="LMARGIN", new_y="NEXT")
            self.set_x(25)
        self.set_y(y_start + h + 2)

    def table(self, headers, rows, col_widths=None):
        self.ln(1)
        if self.get_y() > 240:
            self.add_page()
        if col_widths is None:
            w = 170 / len(headers)
            col_widths = [w] * len(headers)
        self.set_fill_color(*TABLE_HEADER_BG)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 8.5)
        for ri, row in enumerate(rows):
            if self.get_y() > 268:
                self.add_page()
                self.set_fill_color(*TABLE_HEADER_BG)
                self.set_text_color(*WHITE)
                self.set_font("Helvetica", "B", 9)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 7, h, border=1, fill=True)
                self.ln()
                self.set_font("Helvetica", "", 8.5)
            if ri % 2 == 1:
                self.set_fill_color(*TABLE_ALT_BG)
            else:
                self.set_fill_color(*WHITE)
            self.set_text_color(*DARK)
            x_start = self.get_x()
            y_start = self.get_y()
            max_y = y_start
            for i, cell in enumerate(row):
                self.set_xy(x_start + sum(col_widths[:i]), y_start)
                self.multi_cell(col_widths[i], 5, str(cell), border=1, fill=True)
                max_y = max(max_y, self.get_y())
            self.set_y(max_y)
        self.ln(2)

    def add_screenshot(self, filename, caption=""):
        img_path = SCREENSHOTS / filename
        if not img_path.exists():
            self.body(f"[Screenshot not found: {filename}]")
            return
        if self.get_y() > 140:
            self.add_page()
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GRAY)
        if caption:
            self.cell(0, 5, caption, new_x="LMARGIN", new_y="NEXT")
        self.image(str(img_path), x=22, w=166)
        self.ln(4)

    def separator(self):
        self.ln(3)
        self.set_draw_color(*SECTION_LINE)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(5)


def build_pdf():
    pdf = WalkthroughPDF()
    pdf.alias_nb_pages()

    # ===== COVER PAGE =====
    pdf.add_page()
    pdf.ln(35)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 15, "GHAS to ADO Logic App", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 10, "Designer Walkthrough", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 8, "Step-by-step guide with screenshots and end-to-end examples", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    pdf.set_draw_color(*BLUE)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*DARK)
    details = [
        ("Logic App", "ghas-ado-sync-learfield (Consumption tier)"),
        ("Resource Group", "rg-ghas-ado-learfield (East US)"),
        ("Actions", "1 trigger + 22 actions = 23 total steps"),
        ("Alert Types", "Code Scanning, Dependabot, Secret Scanning"),
        ("ADO Target", "brandsafway1 / brandsafway_Engg"),
    ]
    for label, val in details:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*BLUE)
        pdf.cell(45, 7, label + ":", align="R")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*DARK)
        pdf.cell(0, 7, "  " + val, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, "Learfield Customer Demo", align="C", new_x="LMARGIN", new_y="NEXT")

    # ===== TABLE OF CONTENTS =====
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    toc = [
        ("Phase 1", "Create the Logic App Resource"),
        ("Phase 2", "Open Designer & Set Up Parameters"),
        ("Phase 3", "Add the HTTP Trigger"),
        ("Phase 4", "Compose Actions - Layer 1 (Parallel)"),
        ("Phase 5", "Compose Actions - Layer 2 (Normalized)"),
        ("Phase 6", "Compose Actions - Layer 3 (Final Variables)"),
        ("Phase 7", "Main Condition - Create vs Close"),
        ("Phase 8", "TRUE Branch - Create Work Item"),
        ("Phase 9", "FALSE Branch - Auto-Close Work Item"),
        ("Phase 10", "Save & Get Webhook URL"),
        ("Phase 11", "Configure GitHub Webhook"),
        ("Phase 12", "Verify Results in ADO"),
        ("E2E 1", "Code Scanning Alert (Create)"),
        ("E2E 2", "Dependabot Alert (Create)"),
        ("E2E 3", "Secret Scanning Alert (Create)"),
        ("E2E 4", "Auto-Close (Vulnerability Fixed)"),
        ("E2E 5", "Deduplication (Duplicate Ignored)"),
        ("Summary", "Complete Action Reference Table"),
    ]
    for num, title in toc:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*BLUE)
        pdf.cell(25, 7, num)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*DARK)
        pdf.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")

    # ===== OVERVIEW =====
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 10, "Overview: What the Designer Shows", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.body("Looking at the Logic App Designer, the workflow has 4 layers:")
    pdf.code_block(
        "TRIGGER:  When a GHAS webhook is received (HTTP POST)\n"
        "            |\n"
        "LAYER 1:  Compose EventType | AlertNumber | RepoFullName | AlertUrl | Action\n"
        "          (all run in parallel - no dependencies on each other)\n"
        "            |\n"
        "LAYER 2:  Compose Title | Severity | FilePath | LineNumber | Branch |\n"
        "          DetailText | GhasTag  (depend on EventType and/or others)\n"
        "            |\n"
        "LAYER 3:  Compose Tags | Compose Description\n"
        "          (depend on multiple Layer 1 and Layer 2 outputs)\n"
        "            |\n"
        "LAYER 4:  Condition IsCreateAction\n"
        "          TRUE  -> Query Existing -> Create Work Item (if no dupe)\n"
        "          FALSE -> Is Close? -> Find WI -> Close Work Item"
    )

    # ===== PHASE 1: CREATE LOGIC APP =====
    pdf.phase_title(1, "Create the Logic App Resource")

    pdf.step_title("1.1 - Open Azure Portal")
    pdf.body("Navigate to portal.azure.com and click 'Create a resource'.")
    pdf.add_screenshot("01-azure-portal-home.png", "Azure Portal Home - Click 'Create a resource'")

    pdf.step_title("1.2 - Select Logic App")
    pdf.body("Find Logic App in the Popular Azure services list and click Create.")
    pdf.add_screenshot("02-create-resource-logic-app.png", "Create a resource - Select Logic App")

    pdf.step_title("1.3 - Select Consumption Plan")
    pdf.body("Select Consumption (Multi-tenant) for serverless pay-per-execution pricing.")
    pdf.add_screenshot("03-select-consumption-plan.png", "Select Consumption (Multi-tenant)")
    pdf.info_box("Why Consumption?",
                 "For a webhook-triggered workflow, you only pay when GitHub sends an alert "
                 "(~$0.000025 per action). No idle costs. Standard plan is overkill for this use case.")

    pdf.step_title("1.4 - Fill in the Basics Form")
    pdf.table(
        ["Field", "Value", "Why"],
        [
            ["Subscription", "(your subscription)", "Billing"],
            ["Resource Group", "rg-ghas-ado-learfield", "Organize related resources"],
            ["Logic App name", "ghas-ado-sync-learfield", "Descriptive name"],
            ["Region", "East US", "Close to ADO instance"],
            ["Enable log analytics", "No", "Not needed for demo"],
        ],
        [50, 55, 65]
    )
    pdf.add_screenshot("04-logic-app-basics-form.png", "Logic App creation form - Basics tab")
    pdf.body("Click Review + create > Create > Wait ~30 seconds > Go to resource.")

    pdf.step_title("1.5 - Logic App Overview (Deployed)")
    pdf.body("After deployment, the Overview page shows Status: Enabled, and after all steps are complete, 1 trigger + 22 actions.")
    pdf.add_screenshot("05-logic-app-overview.png", "Logic App Overview - Status: Enabled")

    # ===== PHASE 2: PARAMETERS =====
    pdf.phase_title(2, "Open Designer & Set Up Parameters")
    pdf.body("In the left sidebar, expand Development Tools and click Logic app designer. Then click the Parameters button in the top toolbar.")
    pdf.table(
        ["Parameter Name", "Type", "Purpose"],
        [
            ["adoOrganization", "String", "ADO org (e.g. brandsafway1)"],
            ["adoProject", "String", "ADO project name"],
            ["adoPat", "String", "ADO Personal Access Token"],
            ["githubPat", "String", "GitHub PAT"],
            ["webhookSecret", "String", "Webhook verification secret"],
            ["workItemType", "String", "Work item type (default: Issue)"],
        ],
        [45, 25, 100]
    )

    # ===== PHASE 3: TRIGGER =====
    pdf.phase_title(3, "Add the HTTP Trigger")
    pdf.body("This is the green box at the top of the designer: 'When a GHAS webhook is received'.")
    pdf.click_step(1, "In the designer, click 'Add a trigger'")
    pdf.click_step(2, "Search for 'HTTP request'")
    pdf.click_step(3, "Select 'When an HTTP request is received' (Request category)")
    pdf.click_step(4, "Leave Request Body JSON Schema as {} (empty)")
    pdf.click_step(5, "Click the ... menu > Rename > type: When a GHAS webhook is received")
    pdf.click_step(6, "Click Save - Azure generates your unique webhook URL")
    pdf.add_screenshot("10-trigger-http-request.png", "HTTP Trigger - Webhook URL generated after saving")
    pdf.info_box("Why empty schema?",
                 "GitHub sends 3 different payload formats (code scanning, Dependabot, secret scanning). "
                 "By leaving the schema empty, we accept ALL of them and handle differences in the Compose actions.")

    # ===== PHASE 4: COMPOSE LAYER 1 =====
    pdf.phase_title(4, "Compose Actions - Layer 1 (Parallel)")
    pdf.body("These 5 actions run in parallel immediately after the trigger. They extract raw data from the webhook payload. "
             "In the designer, these appear as the first row of purple Compose boxes.")
    pdf.bold("How to add each: Click + below trigger > Add an action > search 'Compose' > select Compose (Data Operations) > "
             "enter expression in Inputs > click ... > Rename.")

    for name, expr, desc in [
        ("Compose EventType",
         "@triggerOutputs()?['headers']?['X-GitHub-Event']",
         "Reads the X-GitHub-Event HTTP header. Values: code_scanning_alert, dependabot_alert, or secret_scanning_alert."),
        ("Compose AlertNumber",
         "@triggerBody()?['alert']?['number']",
         "Extracts the alert number from the webhook body (e.g., alert #42)."),
        ("Compose RepoFullName",
         "@triggerBody()?['repository']?['full_name']",
         "Gets the full repository name (e.g., learfield-corp/fan-portal)."),
        ("Compose AlertUrl",
         "@coalesce(triggerBody()?['alert']?['html_url'], '')",
         "Gets the URL to the alert in GitHub. Uses coalesce to default to empty string if missing."),
        ("Compose Action",
         "@triggerBody()?['action']",
         "Gets the webhook action: 'created' (new vuln), 'fixed', or 'resolved'. Determines create vs close path."),
    ]:
        pdf.sub_step(name)
        pdf.code_block(expr)
        pdf.body(desc)

    # ===== PHASE 5: COMPOSE LAYER 2 =====
    pdf.phase_title(5, "Compose Actions - Layer 2 (Depend on EventType)")
    pdf.body("These actions depend on Compose EventType because they use conditional logic (if/equals) "
             "to normalize data differently based on the alert type.")

    pdf.sub_step("Compose Title")
    pdf.body("Runs After: Compose EventType")
    pdf.code_block(
        "@if(equals(outputs('Compose_EventType'),\n"
        "    'code_scanning_alert'),\n"
        "  concat('[GHAS-CodeScan] ',\n"
        "    coalesce(triggerBody()?['alert']?['rule']\n"
        "      ?['description'], 'Code scanning alert')),\n"
        "  if(equals(outputs('Compose_EventType'),\n"
        "      'dependabot_alert'),\n"
        "    concat('[GHAS-Dependabot] ',\n"
        "      coalesce(triggerBody()?['alert']\n"
        "        ?['security_advisory']?['summary'],\n"
        "        'Dependabot alert')),\n"
        "    concat('[GHAS-Secret] ',\n"
        "      coalesce(triggerBody()?['alert']\n"
        "        ?['secret_type_display_name'],\n"
        "        'Secret scanning alert'))\n"
        "  )\n"
        ")"
    )
    pdf.body("Creates a prefixed title: [GHAS-CodeScan] SQL Injection..., [GHAS-Dependabot] lodash..., or [GHAS-Secret] Azure Storage Key.")

    pdf.sub_step("Compose Severity")
    pdf.body("Runs After: Compose EventType. Normalizes severity to lowercase. Secret scanning is always 'critical'.")
    pdf.code_block(
        "@toLower(if(equals(outputs('Compose_EventType'),\n"
        "    'code_scanning_alert'),\n"
        "  coalesce(triggerBody()?['alert']?['rule']\n"
        "    ?['security_severity_level'], 'medium'),\n"
        "  if(equals(outputs('Compose_EventType'),\n"
        "      'dependabot_alert'),\n"
        "    coalesce(triggerBody()?['alert']\n"
        "      ?['security_vulnerability']?['severity'],\n"
        "      'medium'),\n"
        "    'critical')))"
    )

    pdf.sub_step("Compose FilePath")
    pdf.body("Runs After: Compose EventType. Gets file path: code scanning = source file, Dependabot = manifest, secret = N/A.")
    pdf.code_block(
        "@if(equals(outputs('Compose_EventType'),\n"
        "    'code_scanning_alert'),\n"
        "  coalesce(triggerBody()?['alert']\n"
        "    ?['most_recent_instance']?['location']?['path'],\n"
        "    'N/A'),\n"
        "  if(equals(outputs('Compose_EventType'),\n"
        "      'dependabot_alert'),\n"
        "    coalesce(triggerBody()?['alert']\n"
        "      ?['dependency']?['manifest_path'], 'N/A'),\n"
        "    'N/A'))"
    )

    pdf.sub_step("Compose LineNumber")
    pdf.body("Runs After: Compose EventType. Only available for code scanning alerts.")
    pdf.code_block(
        "@if(equals(outputs('Compose_EventType'),\n"
        "    'code_scanning_alert'),\n"
        "  string(coalesce(triggerBody()?['alert']\n"
        "    ?['most_recent_instance']?['location']\n"
        "    ?['start_line'], 'N/A')),\n"
        "  'N/A')"
    )

    pdf.sub_step("Compose Branch")
    pdf.body("Runs After: Compose EventType. Gets Git branch ref (only for code scanning).")
    pdf.code_block(
        "@if(equals(outputs('Compose_EventType'),\n"
        "    'code_scanning_alert'),\n"
        "  coalesce(triggerBody()?['alert']\n"
        "    ?['most_recent_instance']?['ref'], 'N/A'),\n"
        "  'N/A')"
    )

    pdf.sub_step("Compose DetailText")
    pdf.body("Runs After: Compose EventType. Extracts detailed description for the work item body.")
    pdf.code_block(
        "@if(equals(outputs('Compose_EventType'),\n"
        "    'code_scanning_alert'),\n"
        "  coalesce(triggerBody()?['alert']\n"
        "    ?['most_recent_instance']?['message']?['text'],\n"
        "    triggerBody()?['alert']?['rule']?['description'],\n"
        "    'No additional details.'),\n"
        "  if(equals(outputs('Compose_EventType'),\n"
        "      'dependabot_alert'),\n"
        "    coalesce(triggerBody()?['alert']\n"
        "      ?['security_advisory']?['description'],\n"
        "      'No additional details.'),\n"
        "    concat('Secret type: ',\n"
        "      coalesce(triggerBody()?['alert']\n"
        "        ?['secret_type'], 'unknown'),\n"
        "      '. This secret may have been exposed\n"
        "       and should be rotated immediately.')))"
    )

    pdf.sub_step("Compose GhasTag")
    pdf.body("Runs After: Compose AlertNumber AND Compose RepoFullName. "
             "Creates a unique deduplication tag like GHAS-learfield-corp-fan-portal-42.")
    pdf.code_block(
        "@concat('GHAS-',\n"
        "  replace(string(outputs('Compose_RepoFullName')),\n"
        "    '/', '-'),\n"
        "  '-',\n"
        "  string(outputs('Compose_AlertNumber')))"
    )
    pdf.warn_box("This is the KEY to the entire dedup/auto-close logic. Every work item gets this unique tag. "
                 "Queries search by this tag to prevent duplicates and find work items to close.")

    # ===== PHASE 6: COMPOSE LAYER 3 =====
    pdf.phase_title(6, "Compose Actions - Layer 3 (Final Variables)")
    pdf.body("The last two Compose actions before the condition. They depend on multiple upstream outputs.")

    pdf.sub_step("Compose Tags")
    pdf.body("Runs After: Compose EventType, Compose Severity, Compose GhasTag.")
    pdf.code_block(
        "@concat('GHAS; ',\n"
        "  if(equals(outputs('Compose_EventType'),\n"
        "      'code_scanning_alert'), 'CodeScanning',\n"
        "    if(equals(outputs('Compose_EventType'),\n"
        "        'dependabot_alert'), 'Dependabot',\n"
        "      'SecretScanning')),\n"
        "  '; ', outputs('Compose_Severity'),\n"
        "  '; ', outputs('Compose_GhasTag'))"
    )
    pdf.body("Result example: GHAS; CodeScanning; high; GHAS-org-repo-42")

    pdf.sub_step("Compose Description")
    pdf.body("Runs After: 10 upstream actions. Builds a rich HTML table for the ADO work item description "
             "with alert type, severity, repository, file, line, branch, detail text, and a clickable link back to GHAS.")
    pdf.info_box("HTML Output Preview",
                 "The description renders in ADO as a formatted table with:\n"
                 "- Alert Type, Severity (uppercase), Repository, Alert #\n"
                 "- File path, Line number, Branch\n"
                 "- Detail text with full vulnerability description\n"
                 "- Clickable 'View in GitHub Advanced Security' link\n"
                 "- Footer: 'Auto-created by GHAS-ADO Sync | Tag: GHAS-...'")

    # ===== PHASE 7: CONDITION =====
    pdf.phase_title(7, "Main Condition - Create vs Close")
    pdf.body("The dark box labeled 'Condition IsCreateAction' with True (green) and False (red) branches.")
    pdf.add_screenshot("07-designer-condition-expanded.png", "Condition IsCreateAction - True (2 Actions) / False (1 Action)")
    pdf.click_step(1, "Click + below the Compose actions > Add an action > search 'Condition'")
    pdf.click_step(2, "Rename to 'Condition IsCreateAction'")
    pdf.click_step(3, "Configure: outputs('Compose_Action')  is equal to  'created'")
    pdf.body("Logic: If action is 'created' -> TRUE branch (create work item). Otherwise -> FALSE branch (check if fixed/resolved and close).")

    # ===== PHASE 8: TRUE BRANCH =====
    pdf.phase_title(8, "TRUE Branch - Create Work Item")
    pdf.add_screenshot("08-designer-true-branch-create.png", "True branch: Query existing + Condition + Create")

    pdf.step_title("8a. HTTP QueryExistingWorkItem")
    pdf.add_screenshot("11-http-query-existing-workitem.png", "WIQL query for deduplication - dynamic content tokens visible")
    pdf.table(
        ["Field", "Value"],
        [
            ["Method", "POST"],
            ["URI", "https://dev.azure.com/{adoOrganization}/{adoProject}/_apis/wit/wiql?api-version=7.1"],
            ["Content-Type", "application/json"],
            ["Authorization", "Basic {base64(':' + adoPat)}"],
        ],
        [40, 130]
    )
    pdf.bold("Body (WIQL query):")
    pdf.code_block(
        '{\n'
        '  "query": "SELECT [System.Id] FROM WorkItems\n'
        '    WHERE [System.Tags] CONTAINS\n'
        "      '{outputs('Compose_GhasTag')}'\n"
        "    AND [System.TeamProject] =\n"
        "      '{parameters('adoProject')}'\"\n"
        '}'
    )
    pdf.body("Checks if a work item with this GHAS tag already exists. Prevents duplicates if GitHub retries the webhook.")

    pdf.step_title("8b. Condition NoExistingWorkItem")
    pdf.body("If QueryExistingWorkItem returns 0 results -> TRUE (no duplicate, proceed to create). "
             "If results > 0 -> FALSE (skip, do nothing).")
    pdf.code_block("length(body('HTTP_QueryExistingWorkItem')\n  ?['workItems'])  is equal to  0")

    pdf.step_title("8c. HTTP CreateWorkItem")
    pdf.table(
        ["Field", "Value"],
        [
            ["Method", "PATCH (required by ADO API)"],
            ["URI", "https://dev.azure.com/{org}/{project}/_apis/wit/workitems/$Issue?api-version=7.1"],
            ["Content-Type", "application/json-patch+json"],
        ],
        [40, 130]
    )
    pdf.bold("Body (JSON Patch document):")
    pdf.code_block(
        '[\n'
        '  {"op":"add", "path":"/fields/System.Title",\n'
        '   "value":"{outputs(\'Compose_Title\')}"},\n'
        '  {"op":"add", "path":"/fields/System.Description",\n'
        '   "value":"{outputs(\'Compose_Description\')}"},\n'
        '  {"op":"add", "path":"/fields/System.Tags",\n'
        '   "value":"{outputs(\'Compose_Tags\')}"},\n'
        '  {"op":"add", "path":"/relations/-",\n'
        '   "value":{"rel":"Hyperlink",\n'
        '     "url":"{outputs(\'Compose_AlertUrl\')}",\n'
        '     "attributes":{"comment":\n'
        '       "GitHub Advanced Security Alert"}}}\n'
        ']'
    )
    pdf.body("Creates an ADO work item with Title, Description (HTML), Tags, and a Hyperlink back to the GHAS alert.")
    pdf.warn_box("The method is PATCH (not POST) - this is required by the ADO Work Item API. "
                 "The Content-Type must be application/json-patch+json (not application/json).")

    # ===== PHASE 9: FALSE BRANCH =====
    pdf.phase_title(9, "FALSE Branch - Auto-Close Work Item")
    pdf.add_screenshot("09-designer-both-branches.png", "Both branches visible - True (create) and False (close)")

    pdf.step_title("9a. Condition IsCloseAction")
    pdf.body("Uses OR logic to check if the action is 'fixed' OR 'resolved'.")
    pdf.code_block(
        "outputs('Compose_Action') is equal to 'fixed'\n"
        "  OR\n"
        "outputs('Compose_Action') is equal to 'resolved'"
    )

    pdf.step_title("9b. HTTP FindWorkItemToClose")
    pdf.bold("WIQL Query (similar to dedup check but filters out already-closed items):")
    pdf.code_block(
        "SELECT [System.Id], [System.State]\n"
        "FROM WorkItems\n"
        "WHERE [System.Tags] CONTAINS '{GhasTag}'\n"
        "  AND [System.TeamProject] = '{adoProject}'\n"
        "  AND [System.State] <> 'Closed'\n"
        "  AND [System.State] <> 'Done'\n"
        "  AND [System.State] <> 'Removed'"
    )

    pdf.step_title("9c. Condition WorkItemFound")
    pdf.code_block("length(body('HTTP_FindWorkItemToClose')\n  ?['workItems'])  is greater than  0")

    pdf.step_title("9d. HTTP CloseWorkItem")
    pdf.bold("Body:")
    pdf.code_block(
        '[\n'
        '  {"op":"add",\n'
        '   "path":"/fields/System.State",\n'
        '   "value":"Done"},\n'
        '  {"op":"add",\n'
        '   "path":"/fields/System.History",\n'
        '   "value":"Auto-closed by GHAS-ADO Sync:\n'
        '     Vulnerability marked as {Action}\n'
        '     in GitHub Advanced Security.\n'
        '     View alert: {AlertUrl}"}\n'
        ']'
    )
    pdf.body("Transitions the work item to 'Done' and adds a History comment with context.")
    pdf.info_box("Why 'Done' instead of 'Closed'?",
                 "The ADO Basic process template uses 'Done' as the terminal state. "
                 "If your project uses the Agile or Scrum template, change this to 'Closed'.")

    # ===== PHASE 10-12 =====
    pdf.phase_title(10, "Save & Get Webhook URL")
    pdf.click_step(1, "Click Save in the top toolbar")
    pdf.click_step(2, "Click on the trigger action ('When a GHAS webhook is received')")
    pdf.click_step(3, "Copy the HTTP URL - this is the webhook URL for GitHub")

    pdf.phase_title(11, "Configure GitHub Webhook")
    pdf.click_step(1, "Go to your GitHub repo > Settings > Webhooks > Add webhook")
    pdf.click_step(2, "Payload URL: Paste the Logic App HTTP URL")
    pdf.click_step(3, "Content type: application/json")
    pdf.click_step(4, "Secret: (your webhook secret)")
    pdf.click_step(5, "Events: Select individual events > check: Code scanning alerts, Dependabot alerts, Secret scanning alerts")

    pdf.phase_title(12, "Verify Results in ADO")
    pdf.body("After triggering (via real GHAS alerts or mock webhooks), work items appear in Azure DevOps:")
    pdf.add_screenshot("13-ado-work-items-list.png", "ADO Board - GHAS-created issues alongside seeded demo data")

    # ===== E2E SCENARIOS =====
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 14, "End-to-End: What Goes In, What Comes Out", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(*BLUE)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)
    pdf.body("This section shows the exact webhook payloads GitHub sends and the exact ADO work items the Logic App creates.")

    # --- E2E 1: Code Scanning ---
    pdf.step_title("E2E Scenario 1: Code Scanning Alert (Create)")
    pdf.bold("INPUT - Webhook GitHub Sends:")
    pdf.body("Headers: X-GitHub-Event: code_scanning_alert")
    pdf.code_block(
        '{\n'
        '  "action": "created",\n'
        '  "alert": {\n'
        '    "number": 42,\n'
        '    "html_url": "https://github.com/learfield-corp/\n'
        '      fan-portal/security/code-scanning/42",\n'
        '    "rule": {\n'
        '      "id": "js/sql-injection",\n'
        '      "security_severity_level": "high",\n'
        '      "description": "SQL Injection vulnerability\n'
        '        in query builder"\n'
        '    },\n'
        '    "most_recent_instance": {\n'
        '      "ref": "refs/heads/main",\n'
        '      "location": {\n'
        '        "path": "src/api/queries/userSearch.js",\n'
        '        "start_line": 47\n'
        '      },\n'
        '      "message": {\n'
        '        "text": "This query depends on a\n'
        '          user-provided value and is not\n'
        '          parameterized."\n'
        '      }\n'
        '    }\n'
        '  },\n'
        '  "repository": {\n'
        '    "full_name": "learfield-corp/fan-portal"\n'
        '  }\n'
        '}'
    )
    pdf.bold("PROCESSING - Compose Action Outputs:")
    pdf.table(
        ["Compose Action", "Output Value"],
        [
            ["EventType", "code_scanning_alert"],
            ["AlertNumber", "42"],
            ["RepoFullName", "learfield-corp/fan-portal"],
            ["Action", "created"],
            ["GhasTag", "GHAS-learfield-corp-fan-portal-42"],
            ["Title", "[GHAS-CodeScan] SQL Injection vulnerability in query builder"],
            ["Severity", "high"],
            ["FilePath", "src/api/queries/userSearch.js"],
            ["LineNumber", "47"],
            ["Branch", "refs/heads/main"],
            ["Tags", "GHAS; CodeScanning; high; GHAS-learfield-corp-fan-portal-42"],
        ],
        [40, 130]
    )
    pdf.bold("CONDITION EVALUATION:")
    pdf.body("Action = 'created' -> IsCreateAction = TRUE\n"
             "QueryExistingWorkItem finds 0 matches -> NoExistingWorkItem = TRUE\n"
             "HTTP CreateWorkItem -> EXECUTES")
    pdf.bold("OUTPUT - ADO Work Item Created:")
    pdf.table(
        ["Field", "Value"],
        [
            ["ID", "#9 (auto-assigned by ADO)"],
            ["Type", "Issue"],
            ["State", "To Do"],
            ["Title", "[GHAS-CodeScan] SQL Injection vulnerability in query builder"],
            ["Tags", "GHAS; CodeScanning; high; GHAS-learfield-corp-fan-portal-42"],
            ["Hyperlink", "https://github.com/.../security/code-scanning/42"],
            ["Description", "HTML table: Severity=HIGH, File=userSearch.js, Line=47, Branch=main"],
        ],
        [30, 140]
    )
    pdf.success_box("Work item #9 created successfully with full metadata, tags, and hyperlink back to GHAS.")

    # --- E2E 2: Dependabot ---
    pdf.separator()
    pdf.step_title("E2E Scenario 2: Dependabot Alert (Create)")
    pdf.bold("INPUT - Webhook:")
    pdf.body("Headers: X-GitHub-Event: dependabot_alert")
    pdf.code_block(
        '{\n'
        '  "action": "created",\n'
        '  "alert": {\n'
        '    "number": 7,\n'
        '    "html_url": "https://github.com/learfield-corp/\n'
        '      fan-portal/security/dependabot/7",\n'
        '    "security_advisory": {\n'
        '      "summary": "Prototype Pollution in\n'
        '        lodash < 4.17.21"\n'
        '    },\n'
        '    "security_vulnerability": {\n'
        '      "severity": "critical"\n'
        '    },\n'
        '    "dependency": {\n'
        '      "manifest_path": "package.json"\n'
        '    }\n'
        '  },\n'
        '  "repository": {\n'
        '    "full_name": "learfield-corp/fan-portal"\n'
        '  }\n'
        '}'
    )
    pdf.bold("OUTPUT - ADO Work Item:")
    pdf.table(
        ["Field", "Value"],
        [
            ["ID", "#10"],
            ["Title", "[GHAS-Dependabot] Prototype Pollution in lodash < 4.17.21"],
            ["Severity", "CRITICAL"],
            ["FilePath", "package.json"],
            ["Tags", "GHAS; Dependabot; critical; GHAS-learfield-corp-fan-portal-7"],
        ],
        [30, 140]
    )
    pdf.success_box("Work item #10 created - Dependabot alert with manifest path and critical severity.")

    # --- E2E 3: Secret Scanning ---
    pdf.separator()
    pdf.step_title("E2E Scenario 3: Secret Scanning Alert (Create)")
    pdf.bold("INPUT - Webhook:")
    pdf.body("Headers: X-GitHub-Event: secret_scanning_alert")
    pdf.code_block(
        '{\n'
        '  "action": "created",\n'
        '  "alert": {\n'
        '    "number": 3,\n'
        '    "html_url": "https://github.com/learfield-corp/\n'
        '      fan-portal/security/secret-scanning/3",\n'
        '    "secret_type": "azure_storage_account_key",\n'
        '    "secret_type_display_name":\n'
        '      "Azure Storage Account Key"\n'
        '  },\n'
        '  "repository": {\n'
        '    "full_name": "learfield-corp/fan-portal"\n'
        '  }\n'
        '}'
    )
    pdf.bold("OUTPUT - ADO Work Item:")
    pdf.table(
        ["Field", "Value"],
        [
            ["ID", "#11"],
            ["Title", "[GHAS-Secret] Azure Storage Account Key"],
            ["Severity", "CRITICAL (always critical for secrets)"],
            ["DetailText", "Secret type: azure_storage_account_key. Rotate immediately."],
            ["Tags", "GHAS; SecretScanning; critical; GHAS-learfield-corp-fan-portal-3"],
        ],
        [30, 140]
    )
    pdf.success_box("Work item #11 created - Secret scanning alert always tagged as critical.")

    # --- E2E 4: Auto-Close ---
    pdf.separator()
    pdf.step_title("E2E Scenario 4: Auto-Close (Vulnerability Fixed)")
    pdf.bold("INPUT - Webhook:")
    pdf.body("When a developer fixes the SQL injection, GitHub sends:")
    pdf.code_block(
        '{\n'
        '  "action": "fixed",\n'
        '  "alert": {\n'
        '    "number": 42,\n'
        '    "html_url": "https://github.com/learfield-corp/\n'
        '      fan-portal/security/code-scanning/42",\n'
        '    "state": "fixed"\n'
        '  },\n'
        '  "repository": {\n'
        '    "full_name": "learfield-corp/fan-portal"\n'
        '  }\n'
        '}'
    )
    pdf.bold("CONDITION EVALUATION:")
    pdf.body(
        "Action = 'fixed' -> IsCreateAction = FALSE (not 'created')\n"
        "Falls to FALSE branch\n"
        "IsCloseAction: 'fixed' equals 'fixed' -> TRUE\n"
        "FindWorkItemToClose: WIQL finds WI #9 (tag: GHAS-learfield-corp-fan-portal-42)\n"
        "WorkItemFound: length > 0 -> TRUE\n"
        "CloseWorkItem -> EXECUTES"
    )
    pdf.bold("OUTPUT - Work Item #9 Updated:")
    pdf.table(
        ["Field", "Before", "After"],
        [
            ["State", "To Do", "Done"],
            ["History", "(empty)", "Auto-closed by GHAS-ADO Sync: Vulnerability marked as fixed. View alert: (link)"],
        ],
        [30, 60, 80]
    )
    pdf.success_box("Work item #9 automatically transitioned from 'To Do' to 'Done' with audit trail.")

    # --- E2E 5: Deduplication ---
    pdf.separator()
    pdf.step_title("E2E Scenario 5: Deduplication (Duplicate Ignored)")
    pdf.bold("INPUT: Same code_scanning_alert webhook sent twice (GitHub retry).")
    pdf.body(
        "Action = 'created' -> IsCreateAction = TRUE\n"
        "QueryExistingWorkItem: WIQL finds 1 match (tag exists from first time)\n"
        "NoExistingWorkItem: length = 1 (not 0) -> FALSE\n"
        "Falls to empty FALSE branch -> DOES NOTHING"
    )
    pdf.success_box("No duplicate work item created. The retry is silently ignored. Work item #9 unchanged.")

    # ===== VERIFIED TEST RESULTS =====
    pdf.separator()
    pdf.step_title("Verified Test Results (Live Deployment)")
    pdf.body("Tested against: ghas-ado-sync-nd4zwkrsgpemi / brandsafway1 / brandsafway_Engg")
    pdf.table(
        ["Test", "Webhook Sent", "ADO Result", "Status"],
        [
            ["Code Scan Create", "action: created, alert #42", "WI #9: [GHAS-CodeScan] SQL Injection", "PASS"],
            ["Dependabot Create", "action: created, alert #7", "WI #10: [GHAS-Dependabot] lodash", "PASS"],
            ["Secret Scan Create", "action: created, alert #3", "WI #11: [GHAS-Secret] Azure Key", "PASS"],
            ["Auto-Close", "action: fixed, alert #42", "WI #9 -> Done + history", "PASS"],
            ["Deduplication", "duplicate created, #42", "No new WI (tag exists)", "PASS"],
        ],
        [30, 50, 55, 35]
    )

    # ===== COMPLETE ACTION SUMMARY =====
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 12, "Complete Action Reference", new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*BLUE)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)
    pdf.table(
        ["#", "Action Name", "Type", "Purpose"],
        [
            ["1", "When a GHAS webhook is received", "Trigger", "Receive GitHub webhook POST"],
            ["2", "Compose EventType", "Compose", "Extract X-GitHub-Event header"],
            ["3", "Compose AlertNumber", "Compose", "Extract alert number"],
            ["4", "Compose RepoFullName", "Compose", "Extract repository full name"],
            ["5", "Compose AlertUrl", "Compose", "Extract alert HTML URL"],
            ["6", "Compose Action", "Compose", "Extract action (created/fixed)"],
            ["7", "Compose GhasTag", "Compose", "Build dedup tag"],
            ["8", "Compose Title", "Compose", "Build prefixed title"],
            ["9", "Compose Severity", "Compose", "Normalize severity"],
            ["10", "Compose FilePath", "Compose", "Extract file path"],
            ["11", "Compose LineNumber", "Compose", "Extract line number"],
            ["12", "Compose Branch", "Compose", "Extract branch ref"],
            ["13", "Compose DetailText", "Compose", "Extract description"],
            ["14", "Compose Tags", "Compose", "Build ADO tags string"],
            ["15", "Compose Description", "Compose", "Build HTML description"],
            ["16", "Condition IsCreateAction", "Condition", "Route: create vs close"],
            ["17", "HTTP QueryExistingWorkItem", "HTTP POST", "WIQL dedup check"],
            ["18", "Condition NoExistingWorkItem", "Condition", "Skip if duplicate"],
            ["19", "HTTP CreateWorkItem", "HTTP PATCH", "Create ADO work item"],
            ["20", "Condition IsCloseAction", "Condition", "Check if fixed/resolved"],
            ["21", "HTTP FindWorkItemToClose", "HTTP POST", "Find open work item"],
            ["22", "Condition WorkItemFound", "Condition", "Skip if not found"],
            ["23", "HTTP CloseWorkItem", "HTTP PATCH", "Transition to Done"],
        ],
        [10, 65, 30, 65]
    )
    pdf.ln(4)
    pdf.bold("Total: 1 trigger + 22 actions = 23 steps")

    # ===== GENERATE =====
    pdf.output(str(PDF_FILE))
    size_kb = os.path.getsize(PDF_FILE) / 1024
    print(f"PDF generated: {PDF_FILE}")
    print(f"Size: {size_kb:.0f} KB, Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()
