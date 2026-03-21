"""
Generates the Logic App step-by-step PDF guide using fpdf2.
Pure Python — no external system libraries needed.
"""

from fpdf import FPDF
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_FILE = REPO_ROOT / "docs" / "Logic-App-Step-by-Step-Guide.pdf"

# Azure blue
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
SECTION_LINE = (208, 208, 208)


class GuidePDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(20, 20, 20)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*GRAY)
            self.cell(0, 5, "GHAS to ADO Logic App - Complete Build Guide", align="R")
            self.ln(2)
            self.set_draw_color(*SECTION_LINE)
            self.line(20, self.get_y(), 190, self.get_y())
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, num, title):
        self.ln(4)
        if self.get_y() > 245:
            self.add_page()
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*BLUE)
        self.cell(0, 12, f"Step {num}: {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*BLUE)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(4)

    def sub_section(self, title):
        self.ln(2)
        if self.get_y() > 255:
            self.add_page()
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*DARK)
        self.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def sub_sub_section(self, title):
        self.ln(1)
        if self.get_y() > 260:
            self.add_page()
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(60, 60, 60)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bold_text(self, text):
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

    def tip_box(self, title, text):
        self.ln(2)
        if self.get_y() > 245:
            self.add_page()
        y_start = self.get_y()
        self.set_fill_color(*LIGHT_BG)
        # Estimate height
        self.set_font("Helvetica", "", 9.5)
        lines = len(text) / 85 + text.count('\n') + 2
        h = max(lines * 5 + 12, 16)
        self.rect(20, y_start, 170, h, "F")
        self.set_draw_color(*BLUE)
        self.line(20, y_start, 20, y_start + h)
        self.line(20, y_start, 20.5, y_start + h)
        self.rect(20, y_start, 1.5, h, "F")
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

    def warning_box(self, text):
        self.ln(2)
        if self.get_y() > 245:
            self.add_page()
        y_start = self.get_y()
        self.set_fill_color(*TIP_BG)
        self.set_font("Helvetica", "", 9.5)
        lines = len(text) / 85 + text.count('\n') + 2
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

    def code_block(self, text):
        self.ln(1)
        if self.get_y() > 250:
            self.add_page()
        y_start = self.get_y()
        self.set_fill_color(*CODE_BG)
        self.set_font("Courier", "", 8.5)
        lines = text.split('\n')
        h = len(lines) * 4.5 + 6
        self.rect(22, y_start, 166, h, "F")
        self.set_xy(25, y_start + 3)
        self.set_text_color(60, 60, 60)
        for line in lines:
            self.cell(0, 4.5, line, new_x="LMARGIN", new_y="NEXT")
            self.set_x(25)
        self.set_y(y_start + h + 2)

    def table(self, headers, rows, col_widths=None):
        self.ln(1)
        if self.get_y() > 240:
            self.add_page()
        if col_widths is None:
            w = 170 / len(headers)
            col_widths = [w] * len(headers)
        # Header
        self.set_fill_color(*TABLE_HEADER_BG)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True)
        self.ln()
        # Rows
        self.set_font("Helvetica", "", 9)
        for ri, row in enumerate(rows):
            if self.get_y() > 270:
                self.add_page()
            if ri % 2 == 1:
                self.set_fill_color(*TABLE_ALT_BG)
            else:
                self.set_fill_color(*WHITE)
            self.set_text_color(*DARK)
            max_lines = 1
            for i, cell in enumerate(row):
                lines_needed = max(1, len(str(cell)) * 1.0 / (col_widths[i] / 2.1))
                max_lines = max(max_lines, lines_needed)
            rh = max(6, int(max_lines) * 5 + 1)
            x_start = self.get_x()
            y_start = self.get_y()
            for i, cell in enumerate(row):
                self.set_xy(x_start + sum(col_widths[:i]), y_start)
                self.multi_cell(col_widths[i], 5, str(cell), border=1, fill=True)
            self.set_y(max(self.get_y(), y_start + rh))
        self.ln(2)

    def separator(self):
        self.ln(3)
        self.set_draw_color(*SECTION_LINE)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(5)


def build_pdf():
    pdf = GuidePDF()
    pdf.alias_nb_pages()

    # =========== COVER PAGE ===========
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 15, "GHAS to ADO Logic App", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 10, "Complete Step-by-Step Build Guide", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_draw_color(*BLUE)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(12)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 8, "Build a Logic App from scratch in the Azure Portal", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "that automatically syncs GitHub security alerts", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "to Azure DevOps work items.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(12)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, "No prior Logic App experience required.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Every click, every field, every value is documented.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, "Prepared for: Learfield Customer Demo", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "ADO Instance: brandsafway1 / brandsafway_Engg", align="C", new_x="LMARGIN", new_y="NEXT")

    # =========== TABLE OF CONTENTS ===========
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 12, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    toc_items = [
        ("Step 1", "What is a Logic App? (Background)", 3),
        ("Step 2", "What You Need Before Starting (Prerequisites)", 3),
        ("Step 3", "Create a Resource Group in Azure", 4),
        ("Step 4", "Create the Logic App", 5),
        ("Step 5", "Open the Designer and Add Parameters", 6),
        ("Step 6", "Add the HTTP Trigger (Webhook Receiver)", 8),
        ("Step 7", "Add Compose Actions (Extract Data from Webhook)", 9),
        ("Step 8", "Add the Main Condition (Create vs Close)", 15),
        ("Step 9", "Build the Create Branch (Make an ADO Work Item)", 16),
        ("Step 10", "Build the Close Branch (Auto-Close Work Items)", 19),
        ("Step 11", "Save and Get the Webhook URL", 22),
        ("Step 12", "Connect GitHub Webhooks", 22),
        ("Step 13", "Test It End-to-End", 23),
        ("Step 14", "Complete Flow Diagram", 24),
    ]
    for step, title, pg in toc_items:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*BLUE)
        pdf.cell(18, 7, step)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*DARK)
        pdf.cell(135, 7, title)
        pdf.set_text_color(*GRAY)
        pdf.cell(0, 7, str(pg), align="R", new_x="LMARGIN", new_y="NEXT")

    # =========== STEP 1: WHAT IS A LOGIC APP ===========
    pdf.add_page()
    pdf.section_title(1, "What is a Logic App?")

    pdf.body_text(
        "Before we start building, let's understand what a Logic App actually is.\n\n"
        "An Azure Logic App is a cloud service that lets you automate workflows visually. "
        "Think of it like a flowchart that Azure runs for you:\n\n"
        "  - WHEN something happens (a \"trigger\")...\n"
        "  - THEN do these actions in order...\n"
        "  - IF this condition is true, do this... ELSE do that...\n\n"
        "You build the entire workflow by clicking buttons and filling in forms in the Azure Portal. "
        "There is no traditional programming language. Everything is configured through a visual designer."
    )

    pdf.sub_section("Key Concepts You Need to Know")

    pdf.bold_text("1. Trigger")
    pdf.body_text(
        "The event that starts the workflow. In our case, it's an HTTP request "
        "(a webhook from GitHub). Every Logic App must have exactly one trigger."
    )

    pdf.bold_text("2. Action")
    pdf.body_text(
        "A step in the workflow that does something. Examples: extract a value from data, "
        "call an API, check a condition. Our workflow has about 22 actions."
    )

    pdf.bold_text("3. Condition")
    pdf.body_text(
        "A yes/no decision point that splits the flow into two paths: "
        "a True branch and a False branch. Like an IF/ELSE in programming."
    )

    pdf.bold_text("4. Compose")
    pdf.body_text(
        "The simplest action type. It takes an input expression and outputs a value. "
        "Think of it as creating a variable. Example: \"Read the alert title from the webhook data.\""
    )

    pdf.bold_text("5. HTTP Action")
    pdf.body_text(
        "Calls an external API. We use this to call the Azure DevOps REST API to "
        "create and close work items."
    )

    pdf.bold_text("6. Parameters")
    pdf.body_text(
        "Configuration values (like your ADO organization name, PAT, etc.) that you set once "
        "and reference throughout the workflow. Secrets are encrypted."
    )

    pdf.bold_text("7. Expression")
    pdf.body_text(
        "A formula that Logic App evaluates at runtime. Written with @ syntax. "
        "Example: @triggerBody()?['action'] reads the 'action' field from the incoming JSON."
    )

    pdf.tip_box("What is the @ syntax?",
        "In Logic App expressions, @ marks a dynamic value. The ?[] syntax safely reads "
        "nested JSON fields. If a field doesn't exist, it returns null instead of crashing. "
        "Example: @triggerBody()?['alert']?['number'] means: from the trigger body, "
        "get the 'alert' object, then get its 'number' field.")

    # =========== STEP 2: PREREQUISITES ===========
    pdf.add_page()
    pdf.section_title(2, "What You Need Before Starting")

    pdf.body_text("Gather these items before you begin. Each one takes a few minutes to set up.")

    pdf.table(
        ["Item", "Where to Get It", "What It's For"],
        [
            ["Azure subscription", "portal.azure.com", "Hosts the Logic App"],
            ["ADO organization & project", "dev.azure.com", "Where work items will be created"],
            ["ADO Personal Access Token", "ADO > User Settings >\nPersonal Access Tokens >\nNew Token", "Authenticates API calls to ADO.\nScope needed: Work Items Read & Write"],
            ["GitHub repo with GHAS", "GitHub repo > Settings >\nSecurity", "Source of vulnerability alerts"],
            ["GitHub PAT", "GitHub > Settings >\nDeveloper settings > PATs", "Scope needed: security_events"],
            ["Webhook secret string", "Make one up", "Any random string, e.g.\nLearfieldDemo2025!"],
        ],
        [40, 55, 75]
    )

    pdf.tip_box("How to create an ADO PAT",
        "1. Go to dev.azure.com and sign in\n"
        "2. Click the User Settings icon (person with gear) in the top-right\n"
        "3. Click 'Personal access tokens'\n"
        "4. Click '+ New Token'\n"
        "5. Name: GHAS-ADO-Sync\n"
        "6. Organization: brandsafway1 (or your org)\n"
        "7. Expiration: 90 days (or custom)\n"
        "8. Scopes: Click 'Show all scopes', then check 'Work Items > Read & Write'\n"
        "9. Click Create and COPY the token immediately (you won't see it again)")

    # =========== STEP 3: RESOURCE GROUP ===========
    pdf.add_page()
    pdf.section_title(3, "Create a Resource Group")

    pdf.tip_box("What is a Resource Group?",
        "A resource group is like a folder in Azure. It holds related resources together. "
        "We create one for this project so the Logic App and any future resources are organized "
        "and can be easily found or deleted as a unit.")

    pdf.sub_section("Click-by-Click Instructions")
    pdf.click_step(1, "Open your browser and go to portal.azure.com")
    pdf.click_step(2, "Sign in with your Azure account")
    pdf.click_step(3, "In the search bar at the very top of the page, type: Resource groups")
    pdf.click_step(4, "Click \"Resource groups\" in the search results")
    pdf.click_step(5, "Click the \"+ Create\" button near the top-left of the page")
    pdf.click_step(6, "Fill in the form with these EXACT values:")

    pdf.table(
        ["Field", "What to Type/Select", "Why This Value"],
        [
            ["Subscription", "(select your subscription)", "This is where Azure bills you"],
            ["Resource group", "rg-ghas-ado-learfield", "rg- prefix is Azure naming\nconvention for resource groups"],
            ["Region", "East US", "Choose a region close to your\nADO instance for low latency"],
        ],
        [40, 55, 75]
    )

    pdf.click_step(7, "Click the \"Review + Create\" button at the bottom")
    pdf.click_step(8, "Review the summary, then click \"Create\"")
    pdf.click_step(9, "Wait a few seconds. You'll see \"Resource group created\" notification.")

    pdf.tip_box("What just happened?",
        "You created an empty container in Azure. Think of it like creating a new folder "
        "on your desktop before putting files in it. The Logic App we create next will go "
        "inside this resource group.")

    # =========== STEP 4: CREATE LOGIC APP ===========
    pdf.add_page()
    pdf.section_title(4, "Create the Logic App")

    pdf.tip_box("What are we creating?",
        "The Logic App is the actual workflow engine - the thing that will receive webhooks "
        "from GitHub and create work items in ADO. We use the 'Consumption' plan which means:\n"
        "- Serverless: no servers to manage\n"
        "- Pay-per-execution: costs about $0.000025 per action (essentially free for demos)\n"
        "- Auto-scales: handles 1 or 1,000 webhooks without configuration")

    pdf.sub_section("Click-by-Click Instructions")
    pdf.click_step(1, "In the Azure Portal search bar at the top, type: Logic App")
    pdf.click_step(2, "Click \"Logic Apps\" in the search results")
    pdf.click_step(3, "Click \"+ Add\" (or \"+ Create\") near the top-left")
    pdf.click_step(4, "You'll see hosting plan options. Click \"Consumption\" to select it.")

    pdf.tip_box("Why Consumption, not Standard?",
        "Standard plan: Always-on, more features, higher cost. Good for enterprise.\n"
        "Consumption plan: Serverless, pay-per-use, simpler. Perfect for webhook workflows.\n"
        "For this demo, Consumption is the right choice.")

    pdf.click_step(5, "Fill in the creation form with these EXACT values:")

    pdf.table(
        ["Field", "What to Type/Select", "Why"],
        [
            ["Subscription", "(same as before)", "Billing"],
            ["Resource Group", "rg-ghas-ado-learfield", "Put it in the group we just created"],
            ["Logic App name", "ghas-ado-sync-learfield", "Descriptive name visible in portal"],
            ["Region", "East US", "Same region as resource group"],
            ["Enable log analytics", "No", "Not needed for demo.\nEnable in production."],
        ],
        [40, 55, 75]
    )

    pdf.click_step(6, "Click \"Review + Create\"")
    pdf.click_step(7, "Review the summary, then click \"Create\"")
    pdf.click_step(8, "Wait about 30 seconds for deployment to complete")
    pdf.click_step(9, "When you see \"Your deployment is complete\", click \"Go to resource\"")

    pdf.tip_box("What just happened?",
        "Azure created a Logic App instance. Right now it's empty - no workflow, no trigger, "
        "no actions. Think of it as a blank canvas. In the next steps, we'll open the designer "
        "and build the entire workflow step by step.")

    # =========== STEP 5: PARAMETERS ===========
    pdf.add_page()
    pdf.section_title(5, "Open the Designer and Add Parameters")

    pdf.tip_box("What are Parameters?",
        "Parameters are configuration values that the workflow uses. Things like your ADO "
        "organization name, project name, and authentication tokens (PATs). By using parameters "
        "instead of typing these values directly into each action, you:\n"
        "1. Only need to change them in one place\n"
        "2. Keep secrets encrypted (Azure hides SecureString values)\n"
        "3. Can reuse the same workflow for different projects by changing parameter values")

    pdf.sub_section("Open the Logic App Designer")
    pdf.click_step(1, "You should be on the Logic App overview page. Look at the LEFT sidebar.")
    pdf.click_step(2, "Under \"Development Tools\", click \"Logic app designer\"")
    pdf.click_step(3, "If you see a \"Templates\" screen, click \"Blank Logic App\" to start from scratch.")
    pdf.body_text("You should now see the visual designer - a white canvas with a \"+\" button or a prompt to add a trigger.")

    pdf.sub_section("Add Parameters")
    pdf.click_step(1, "In the top toolbar of the designer, look for \"Parameters\" (it may look like a gear or list icon). Click it.")
    pdf.click_step(2, "A Parameters panel opens on the right side. Click \"+ Add parameter\" (or \"Create parameter\").")
    pdf.click_step(3, "Create each parameter listed below. For each one, type the Name, select the Type, and optionally set a Default Value. Then click \"+ Add parameter\" again for the next one.")

    pdf.table(
        ["Parameter Name", "Type", "Default Value", "Purpose"],
        [
            ["adoOrganization", "String", "(leave blank)", "Your ADO org (e.g. brandsafway1)"],
            ["adoProject", "String", "(leave blank)", "ADO project name"],
            ["adoPat", "String", "(leave blank)", "ADO Personal Access Token"],
            ["githubPat", "String", "(leave blank)", "GitHub Personal Access Token"],
            ["webhookSecret", "String", "(leave blank)", "Shared secret for webhook verification"],
            ["workItemType", "String", "Issue", "Type of work item to create (Issue, Bug, Task)"],
        ],
        [35, 20, 30, 85]
    )

    pdf.click_step(4, "Now fill in the VALUE for each parameter:")

    pdf.table(
        ["Parameter", "Value to Enter"],
        [
            ["adoOrganization", "brandsafway1"],
            ["adoProject", "brandsafway_Engg"],
            ["adoPat", "(paste your ADO PAT here)"],
            ["githubPat", "(paste your GitHub PAT here)"],
            ["webhookSecret", "LearfieldDemo2025!"],
            ["workItemType", "Issue"],
        ],
        [50, 120]
    )

    pdf.click_step(5, "Click \"Save\" in the top toolbar.")

    pdf.warning_box(
        "IMPORTANT: When you paste your PATs, double-check there are no extra spaces before or "
        "after the token. Even one extra space will cause authentication to fail silently.")

    # =========== STEP 6: HTTP TRIGGER ===========
    pdf.add_page()
    pdf.section_title(6, "Add the HTTP Trigger")

    pdf.tip_box("What is a Trigger?",
        "Every Logic App starts with exactly one trigger - the event that kicks off the workflow. "
        "A trigger is like a doorbell: when someone rings it (sends a webhook), the workflow starts. "
        "We use an HTTP Request trigger because GitHub sends webhooks as HTTP POST requests. "
        "Azure will give us a unique URL - we'll give that URL to GitHub later.")

    pdf.sub_section("Click-by-Click Instructions")
    pdf.click_step(1, "In the designer canvas, you should see a box that says \"Add a trigger\" (or a \"+\" icon). Click it.")
    pdf.click_step(2, "A panel opens showing available triggers. In the search box, type: When a HTTP request is received")
    pdf.click_step(3, "Click \"When a HTTP request is received\" from the results (it's under the \"Request\" category).")
    pdf.click_step(4, "The trigger block appears on the canvas. It has a few fields:")

    pdf.body_text(
        "  - Request Body JSON Schema: This defines what format of data the trigger expects."
    )

    pdf.click_step(5, "In the \"Request Body JSON Schema\" field, type exactly:  {}")
    pdf.body_text(
        "  That's just an opening and closing curly brace. Nothing else."
    )

    pdf.tip_box("Why do we leave the schema as {} (empty)?",
        "GitHub sends THREE different payload formats depending on the alert type:\n"
        "- Code scanning alerts have fields like alert.rule.description\n"
        "- Dependabot alerts have fields like alert.security_advisory.summary\n"
        "- Secret scanning alerts have fields like alert.secret_type_display_name\n\n"
        "If we defined a specific schema, the trigger would reject payloads that don't match. "
        "By leaving it empty, we accept ALL formats and handle the differences ourselves "
        "in the Compose actions we'll add next.")

    pdf.click_step(6, "Click \"Save\" in the top toolbar. After saving, a URL will appear in the trigger block.")

    pdf.tip_box("What just happened?",
        "Azure generated a unique HTTPS URL with a security token (called a SAS signature) "
        "embedded in it. This URL is your webhook endpoint. Anyone with this URL can trigger "
        "your Logic App, so treat it like a password. The URL looks like:\n"
        "https://prod-04.eastus.logic.azure.com:443/workflows/.../triggers/.../invoke?...")

    # =========== STEP 7: COMPOSE ACTIONS ===========
    pdf.add_page()
    pdf.section_title(7, "Add Compose Actions (Extract Data)")

    pdf.tip_box("What are Compose Actions and Why Do We Need Them?",
        "When GitHub sends a webhook, it sends a big blob of JSON data. Different fields are "
        "buried at different depths. A Compose action lets you extract ONE specific piece of data "
        "and give it a name. It's like saying:\n"
        "  'From all this data, grab the alert title and call it Title'\n"
        "  'From all this data, grab the severity and call it Severity'\n\n"
        "We create 14 Compose actions that extract everything we need. After this step, "
        "the rest of the workflow just references these clean, named values.")

    pdf.sub_section("How to Add Each Compose Action")
    pdf.body_text("For EACH of the Compose actions below, repeat these steps:")
    pdf.click_step(1, "Click the \"+\" button below the last action (or below the trigger for the first one)")
    pdf.click_step(2, "Click \"Add an action\"")
    pdf.click_step(3, "In the search box, type: Compose")
    pdf.click_step(4, "Click \"Compose\" from the results (it's under \"Data Operations\")")
    pdf.click_step(5, "A new Compose block appears. Click the three dots (...) on its title bar")
    pdf.click_step(6, "Click \"Rename\" and type the name shown below")
    pdf.click_step(7, "In the \"Inputs\" field, switch to Expression mode by clicking \"Expression\" (or the fx icon)")
    pdf.click_step(8, "Type (or paste) the expression shown below, then click \"OK\" or \"Add\"")
    pdf.body_text("Repeat for each Compose action listed below.")

    pdf.separator()

    # 7a EventType
    pdf.sub_sub_section("Compose Action #1: Compose_EventType")
    pdf.table(
        ["Property", "Value"],
        [
            ["Rename to", "Compose_EventType"],
            ["Expression", "@triggerOutputs()?['headers']?['X-GitHub-Event']"],
        ],
        [35, 135]
    )
    pdf.tip_box("What does this do?",
        "Reads the X-GitHub-Event HTTP header from the incoming webhook. "
        "GitHub sets this header to tell us which type of alert it is:\n"
        "  - code_scanning_alert (CodeQL found a vulnerability in your code)\n"
        "  - dependabot_alert (a dependency has a known vulnerability)\n"
        "  - secret_scanning_alert (a secret/token was committed to the repo)\n"
        "We need this to know where to look for data in the payload, because each alert type "
        "stores its data in different fields.")

    # 7b Action
    pdf.sub_sub_section("Compose Action #2: Compose_Action")
    pdf.table(
        ["Property", "Value"],
        [
            ["Rename to", "Compose_Action"],
            ["Expression", "@triggerBody()?['action']"],
        ],
        [35, 135]
    )
    pdf.tip_box("What does this do?",
        "Reads the 'action' field from the webhook JSON body. This tells us WHAT happened:\n"
        "  - 'created' = a NEW vulnerability was found\n"
        "  - 'fixed' = the vulnerability was resolved\n"
        "  - 'resolved' = same as fixed (used by some alert types)\n"
        "  - 'dismissed' = someone manually dismissed it\n"
        "This value drives the main decision: create a work item, or close one?")

    # 7c AlertNumber
    pdf.sub_sub_section("Compose Action #3: Compose_AlertNumber")
    pdf.table(
        ["Property", "Value"],
        [
            ["Rename to", "Compose_AlertNumber"],
            ["Expression", "@triggerBody()?['alert']?['number']"],
        ],
        [35, 135]
    )
    pdf.body_text("Reads the unique alert number within the repository (e.g., alert #42). Combined with the repo name, this gives us a globally unique identifier.")

    # 7d RepoFullName
    pdf.sub_sub_section("Compose Action #4: Compose_RepoFullName")
    pdf.table(
        ["Property", "Value"],
        [
            ["Rename to", "Compose_RepoFullName"],
            ["Expression", "@triggerBody()?['repository']?['full_name']"],
        ],
        [35, 135]
    )
    pdf.body_text("Gets the repository's full name in owner/repo format (e.g., sautalwar/my-app). We stamp this on the ADO work item so you know which repo the vulnerability came from.")

    # 7e GhasTag
    pdf.add_page()
    pdf.sub_sub_section("Compose Action #5: Compose_GhasTag  [CRITICAL]")
    pdf.table(
        ["Property", "Value"],
        [
            ["Rename to", "Compose_GhasTag"],
            ["Expression", "@concat('GHAS-', replace(string(outputs(\n'Compose_RepoFullName')), '/', '-'),\n'-', string(outputs('Compose_AlertNumber')))"],
        ],
        [35, 135]
    )
    pdf.tip_box("THIS IS THE MOST IMPORTANT ACTION",
        "This creates a unique tag like GHAS-sautalwar-my-app-42 that links a GHAS alert "
        "to its ADO work item. It's used for:\n"
        "1. DEDUPLICATION: Before creating a work item, we search ADO for this tag. "
        "If found, we skip creation (prevents duplicates if webhook fires twice).\n"
        "2. AUTO-CLOSE: When a vulnerability is fixed, we search ADO for this tag "
        "to find the matching work item and close it.\n"
        "Without this tag, there would be NO way to connect a GHAS alert to its ADO work item.")

    pdf.warning_box(
        "DEPENDENCY: This action uses outputs from Compose_AlertNumber and Compose_RepoFullName, "
        "so it MUST run after those two. In the designer, click the three dots (...) on this action, "
        "click 'Configure run after', and check both Compose_AlertNumber and Compose_RepoFullName.")

    # 7f AlertUrl
    pdf.sub_sub_section("Compose Action #6: Compose_AlertUrl")
    pdf.table(
        ["Property", "Value"],
        [
            ["Rename to", "Compose_AlertUrl"],
            ["Expression", "@coalesce(triggerBody()?['alert']?['html_url'], '')"],
        ],
        [35, 135]
    )
    pdf.tip_box("What does coalesce mean?",
        "coalesce() returns the first non-null value. If html_url exists, use it. "
        "If it doesn't exist (null), use an empty string instead of crashing. "
        "This is a safety net for unexpected payload formats.")

    # 7g Title
    pdf.sub_sub_section("Compose Action #7: Compose_Title")
    pdf.body_text("Rename to: Compose_Title")
    pdf.body_text("Expression (this is long - type it carefully or paste it):")
    pdf.code_block(
        "@if(equals(outputs('Compose_EventType'),\n"
        "    'code_scanning_alert'),\n"
        "  concat('[GHAS-CodeScan] ',\n"
        "    coalesce(triggerBody()?['alert']?['rule']\n"
        "      ?['description'],\n"
        "      'Code scanning alert')),\n"
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
    pdf.tip_box("How this expression works (nested IF/ELSE)",
        "This is a nested if/else that creates a different title based on alert type:\n"
        "  - Is it code_scanning_alert? -> [GHAS-CodeScan] + rule description\n"
        "  - Is it dependabot_alert?    -> [GHAS-Dependabot] + advisory summary\n"
        "  - Otherwise (secret scan)    -> [GHAS-Secret] + secret type name\n"
        "The prefix in brackets helps developers instantly identify what type of "
        "security issue the work item represents when scanning their ADO board.")
    pdf.body_text("Depends on: Compose_EventType (set in Run After)")

    # 7h Severity
    pdf.add_page()
    pdf.sub_sub_section("Compose Action #8: Compose_Severity")
    pdf.body_text("Rename to: Compose_Severity")
    pdf.body_text("Expression:")
    pdf.code_block(
        "@toLower(\n"
        "  if(equals(outputs('Compose_EventType'),\n"
        "      'code_scanning_alert'),\n"
        "    coalesce(triggerBody()?['alert']?['rule']\n"
        "      ?['security_severity_level'], 'medium'),\n"
        "    if(equals(outputs('Compose_EventType'),\n"
        "        'dependabot_alert'),\n"
        "      coalesce(triggerBody()?['alert']\n"
        "        ?['security_vulnerability']\n"
        "        ?['severity'], 'medium'),\n"
        "      'critical'\n"
        "    )\n"
        "  )\n"
        ")"
    )
    pdf.body_text("Each alert type stores severity differently. Code scanning uses rule.security_severity_level, Dependabot uses security_vulnerability.severity. Secret scanning always defaults to 'critical' because an exposed secret is always urgent. toLower() normalizes to lowercase.")
    pdf.body_text("Depends on: Compose_EventType")

    # 7i FilePath
    pdf.sub_sub_section("Compose Action #9: Compose_FilePath")
    pdf.body_text("Rename to: Compose_FilePath")
    pdf.body_text("Expression:")
    pdf.code_block(
        "@if(equals(outputs('Compose_EventType'),\n"
        "    'code_scanning_alert'),\n"
        "  coalesce(triggerBody()?['alert']\n"
        "    ?['most_recent_instance']?['location']\n"
        "    ?['path'], 'N/A'),\n"
        "  if(equals(outputs('Compose_EventType'),\n"
        "      'dependabot_alert'),\n"
        "    coalesce(triggerBody()?['alert']\n"
        "      ?['dependency']?['manifest_path'], 'N/A'),\n"
        "    'N/A'\n"
        "  )\n"
        ")"
    )
    pdf.body_text("Gets the file path where the vulnerability exists. Code scanning gives a specific file (e.g. src/db.py). Dependabot gives the manifest file (e.g. package.json). Secret scanning has no file path so we use 'N/A'.")

    # 7j LineNumber
    pdf.sub_sub_section("Compose Action #10: Compose_LineNumber")
    pdf.table(
        ["Property", "Value"],
        [
            ["Rename to", "Compose_LineNumber"],
            ["Expression", "@if(equals(outputs('Compose_EventType'),\n'code_scanning_alert'),\nstring(coalesce(triggerBody()?['alert']\n?['most_recent_instance']?['location']\n?['start_line'], 'N/A')), 'N/A')"],
        ],
        [35, 135]
    )
    pdf.body_text("Only code scanning provides line-level precision. Others get 'N/A'.")

    # 7k Branch
    pdf.sub_sub_section("Compose Action #11: Compose_Branch")
    pdf.table(
        ["Property", "Value"],
        [
            ["Rename to", "Compose_Branch"],
            ["Expression", "@if(equals(outputs('Compose_EventType'),\n'code_scanning_alert'),\ncoalesce(triggerBody()?['alert']\n?['most_recent_instance']?['ref'], 'N/A'),\n'N/A')"],
        ],
        [35, 135]
    )
    pdf.body_text("Gets the Git branch where the vulnerability was detected. Helps developers know which branch needs the fix.")

    # 7l DetailText
    pdf.add_page()
    pdf.sub_sub_section("Compose Action #12: Compose_DetailText")
    pdf.body_text("Rename to: Compose_DetailText")
    pdf.body_text("Expression:")
    pdf.code_block(
        "@if(equals(outputs('Compose_EventType'),\n"
        "    'code_scanning_alert'),\n"
        "  coalesce(\n"
        "    triggerBody()?['alert']\n"
        "      ?['most_recent_instance']?['message']\n"
        "      ?['text'],\n"
        "    triggerBody()?['alert']?['rule']\n"
        "      ?['description'],\n"
        "    'No additional details.'),\n"
        "  if(equals(outputs('Compose_EventType'),\n"
        "      'dependabot_alert'),\n"
        "    coalesce(triggerBody()?['alert']\n"
        "      ?['security_advisory']?['description'],\n"
        "      'No additional details.'),\n"
        "    concat('Secret type: ',\n"
        "      coalesce(triggerBody()?['alert']\n"
        "        ?['secret_type'], 'unknown'),\n"
        "      '. This secret may have been exposed',\n"
        "      ' and should be rotated immediately.')\n"
        "  )\n"
        ")"
    )
    pdf.body_text("Gets the detailed description of the vulnerability. Provides context so developers understand what the issue is.")

    # 7m Tags
    pdf.sub_sub_section("Compose Action #13: Compose_Tags")
    pdf.body_text("Rename to: Compose_Tags")
    pdf.body_text("Expression:")
    pdf.code_block(
        "@concat('GHAS; ',\n"
        "  if(equals(outputs('Compose_EventType'),\n"
        "      'code_scanning_alert'),\n"
        "    'CodeScanning',\n"
        "    if(equals(outputs('Compose_EventType'),\n"
        "        'dependabot_alert'),\n"
        "      'Dependabot', 'SecretScanning')),\n"
        "  '; ', outputs('Compose_Severity'),\n"
        "  '; ', outputs('Compose_GhasTag'))"
    )
    pdf.body_text("Creates ADO tags like: GHAS; CodeScanning; high; GHAS-owner-repo-42")
    pdf.body_text("These tags let you filter and search work items in ADO boards.")
    pdf.body_text("Depends on: Compose_EventType, Compose_Severity, Compose_GhasTag")

    # 7n Description
    pdf.sub_sub_section("Compose Action #14: Compose_Description")
    pdf.body_text("Rename to: Compose_Description")
    pdf.body_text("This is the longest expression. It builds an HTML table that becomes the work item description in ADO. The expression uses concat() to join together HTML tags with the values from all previous Compose actions.")
    pdf.body_text("Expression: A large concat() that builds an HTML table with these fields: Alert Type, Severity, Repository, Alert #, File, Line, Branch, Details text, and a link back to the GHAS alert.")
    pdf.tip_box("Tip: Copy from the source file",
        "This expression is very long. Instead of typing it, open the file:\n"
        "  infra/workflows/ghas-to-ado.json\n"
        "Find the 'Compose_Description' action (around line 141) and copy the 'inputs' value. "
        "Paste it into the Expression field in the designer.")
    pdf.body_text("Depends on: ALL previous Compose actions (EventType, AlertUrl, GhasTag, Severity, AlertNumber, RepoFullName, FilePath, LineNumber, Branch, DetailText)")

    pdf.warning_box(
        "IMPORTANT - RUN AFTER DEPENDENCIES: For Compose_Description, you need to set 'Run After' to "
        "include ALL 13 previous Compose actions. Click the three dots (...), click 'Configure run after', "
        "and check every single Compose action. This ensures all data is extracted before we build the description.")

    # =========== STEP 8: MAIN CONDITION ===========
    pdf.add_page()
    pdf.section_title(8, "Add the Main Condition (Create vs Close)")

    pdf.tip_box("What is this Condition doing?",
        "This is the main decision point of the entire workflow. It asks ONE simple question:\n\n"
        "  'Did GitHub say a NEW vulnerability was CREATED?'\n\n"
        "If YES (action = 'created'): We create a new ADO work item.\n"
        "If NO (action = anything else): We check if it was 'fixed' or 'resolved', and if so, "
        "we find and close the matching work item.\n\n"
        "This is like an IF/ELSE statement in programming.")

    pdf.sub_section("Click-by-Click Instructions")
    pdf.click_step(1, "Click the \"+\" button below the last Compose action")
    pdf.click_step(2, "Click \"Add an action\"")
    pdf.click_step(3, "In the search box, type: Condition")
    pdf.click_step(4, "Click \"Condition\" from the results (it's under the \"Control\" category)")
    pdf.click_step(5, "A Condition block appears with True and False branches. Rename it:")
    pdf.body_text("    Click the three dots (...) > Rename > Type: Condition_IsCreateAction")
    pdf.click_step(6, "Configure the condition expression:")
    pdf.body_text("    In the condition box, you'll see three fields: a left value, an operator, and a right value.")

    pdf.table(
        ["Field", "What to Enter", "How to Enter It"],
        [
            ["Left value", "outputs('Compose_Action')", "Click the field, switch to\n\"Expression\" tab, type:\noutputs('Compose_Action')\nthen click OK"],
            ["Operator", "is equal to", "Select from the dropdown"],
            ["Right value", "created", "Just type the word: created"],
        ],
        [30, 50, 90]
    )

    pdf.click_step(7, "Configure Run After: Click the three dots (...) > Configure run after. Check these actions: Compose_Action, Compose_Title, Compose_Description, Compose_Tags, Compose_GhasTag, Compose_AlertUrl")

    pdf.tip_box("What the designer looks like now",
        "You should see a Condition block with two branches:\n"
        "  LEFT side (True):  This is where we'll build the 'create work item' logic\n"
        "  RIGHT side (False): This is where we'll build the 'close work item' logic\n"
        "Each branch has its own '+' button to add actions inside it.")

    # =========== STEP 9: TRUE BRANCH ===========
    pdf.add_page()
    pdf.section_title(9, "Build the Create Branch")

    pdf.body_text("We're now working INSIDE the True branch of the condition. This is the path that runs when a NEW vulnerability is found (action = 'created').")
    pdf.body_text("We need to do two things:\n  1. Check if a work item already exists for this alert (deduplication)\n  2. If not, create one")

    pdf.sub_section("9a. Add the Deduplication Query")

    pdf.tip_box("Why check for duplicates?",
        "Webhooks can fire multiple times due to network retries or GitHub processing. "
        "Without this check, the same alert could create 2 or 3 identical work items in ADO. "
        "We search ADO by the unique GhasTag to see if a work item already exists.")

    pdf.click_step(1, "Inside the TRUE branch, click the \"+\" button > \"Add an action\"")
    pdf.click_step(2, "Search for: HTTP")
    pdf.click_step(3, "Click \"HTTP\" from the results (the generic HTTP action, NOT an Azure DevOps connector)")

    pdf.tip_box("Why HTTP action instead of the ADO connector?",
        "The built-in ADO connector in Logic Apps doesn't support WIQL (Work Item Query Language) "
        "queries. The generic HTTP action lets us call ANY REST API directly, giving us full "
        "control over the ADO API.")

    pdf.click_step(4, "Rename it to: HTTP_QueryExistingWorkItem")
    pdf.click_step(5, "Fill in these fields:")

    pdf.table(
        ["Field", "Value to Enter"],
        [
            ["Method", "POST (select from dropdown)"],
            ["URI", "https://dev.azure.com/\n@{parameters('adoOrganization')}/\n@{encodeURIComponent(\nparameters('adoProject'))}/_apis/wit/\nwiql?api-version=7.1"],
        ],
        [30, 140]
    )

    pdf.body_text("For the URI: Click in the field, then switch between regular text and Expression mode to build it piece by piece. Or type the full string with the @{...} expressions inline.")

    pdf.click_step(6, "Add Headers (click \"+ Add new parameter\" > check \"Headers\"):")

    pdf.table(
        ["Header Name", "Header Value"],
        [
            ["Content-Type", "application/json"],
            ["Authorization", "@{concat('Basic ', base64(\nconcat(':', parameters('adoPat'))))}"],
        ],
        [40, 130]
    )

    pdf.tip_box("How does the Authorization header work?",
        "Azure DevOps uses Basic authentication. The format is:\n"
        "  Basic base64(':your-pat-here')\n"
        "Note the colon (:) before the PAT with NO username. The expression:\n"
        "  concat(':', parameters('adoPat'))  -->  builds  :your-pat-here\n"
        "  base64(...)                        -->  encodes it to base64\n"
        "  concat('Basic ', ...)              -->  adds the 'Basic ' prefix")

    pdf.click_step(7, "Add Body (click \"+ Add new parameter\" > check \"Body\"):")

    pdf.code_block(
        '{\n'
        '  "query": "SELECT [System.Id] FROM WorkItems\n'
        '    WHERE [System.Tags] CONTAINS\n'
        "    '@{outputs('Compose_GhasTag')}'\n"
        '    AND [System.TeamProject] =\n'
        "    '@{parameters('adoProject')}'\"\n"
        '}'
    )

    pdf.tip_box("What is WIQL?",
        "WIQL = Work Item Query Language. It's like SQL but for Azure DevOps work items.\n"
        "This query says: 'Find any work item whose Tags field contains our unique GHAS tag "
        "in this project.' If it returns results, a work item already exists.")

    pdf.separator()

    pdf.sub_section("9b. Add the 'No Duplicate' Condition")
    pdf.click_step(1, "Below HTTP_QueryExistingWorkItem (still inside True branch), add another Condition")
    pdf.click_step(2, "Rename to: Condition_NoExistingWorkItem")
    pdf.click_step(3, "Configure the condition:")

    pdf.table(
        ["Field", "What to Enter"],
        [
            ["Left value (Expression)", "length(body(\n'HTTP_QueryExistingWorkItem')\n?['workItems'])"],
            ["Operator", "is equal to"],
            ["Right value", "0"],
        ],
        [45, 125]
    )

    pdf.body_text("This checks: does the WIQL response have 0 work items? If yes (True), no duplicate exists, so we create one.")

    pdf.separator()

    pdf.sub_section("9c. Add the Create Work Item Action")

    pdf.click_step(1, "Inside the TRUE branch of Condition_NoExistingWorkItem, click \"+\" > \"Add an action\"")
    pdf.click_step(2, "Search for HTTP, click \"HTTP\"")
    pdf.click_step(3, "Rename to: HTTP_CreateWorkItem")
    pdf.click_step(4, "Configure:")

    pdf.table(
        ["Field", "Value"],
        [
            ["Method", "PATCH"],
            ["URI", "https://dev.azure.com/\n@{parameters('adoOrganization')}/\n@{encodeURIComponent(\nparameters('adoProject'))}/_apis/wit/\nworkitems/$@{parameters(\n'workItemType')}?api-version=7.1"],
            ["Header: Content-Type", "application/json-patch+json"],
            ["Header: Authorization", "@{concat('Basic ', base64(\nconcat(':', parameters('adoPat'))))}"],
        ],
        [45, 125]
    )

    pdf.tip_box("Why PATCH and why json-patch+json?",
        "ADO's work item creation API uses PATCH (not POST) with JSON Patch format. "
        "This is an ADO API design choice. JSON Patch is a standard (RFC 6902) that describes "
        "changes to a JSON document as a list of operations (add, replace, remove).")

    pdf.click_step(5, "Set the Body to this JSON array (4 operations):")

    pdf.code_block(
        '[\n'
        '  {\n'
        '    "op": "add",\n'
        '    "path": "/fields/System.Title",\n'
        "    \"value\": \"@{outputs('Compose_Title')}\"\n"
        '  },\n'
        '  {\n'
        '    "op": "add",\n'
        '    "path": "/fields/System.Description",\n'
        "    \"value\": \"@{outputs('Compose_Description')}\"\n"
        '  },\n'
        '  {\n'
        '    "op": "add",\n'
        '    "path": "/fields/System.Tags",\n'
        "    \"value\": \"@{outputs('Compose_Tags')}\"\n"
        '  },\n'
        '  {\n'
        '    "op": "add",\n'
        '    "path": "/relations/-",\n'
        '    "value": {\n'
        '      "rel": "Hyperlink",\n'
        "      \"url\": \"@{outputs('Compose_AlertUrl')}\",\n"
        '      "attributes": {\n'
        '        "comment": "GitHub Advanced Security"\n'
        '      }\n'
        '    }\n'
        '  }\n'
        ']'
    )

    pdf.tip_box("What each operation does",
        "1. System.Title: Sets the title (e.g. [GHAS-CodeScan] SQL injection)\n"
        "2. System.Description: Sets the rich HTML body with the metadata table\n"
        "3. System.Tags: Adds tags for filtering (GHAS; CodeScanning; high; GHAS-tag)\n"
        "4. /relations/-: Adds a HYPERLINK to the GHAS alert. The '-' means 'append'. "
        "This creates a clickable link in the ADO work item that takes you directly to "
        "the vulnerability in GitHub.")

    # =========== STEP 10: FALSE BRANCH ===========
    pdf.add_page()
    pdf.section_title(10, "Build the Close Branch")

    pdf.body_text("Now we build the FALSE branch of Condition_IsCreateAction. This handles ALL non-'created' actions (fixed, resolved, dismissed, etc.).")
    pdf.body_text("We only want to close a work item when the vulnerability is actually FIXED. So we add another condition.")

    pdf.sub_section("10a. Add the Close Action Condition")

    pdf.click_step(1, "Inside the FALSE branch of Condition_IsCreateAction, click \"+\" > \"Add an action\"")
    pdf.click_step(2, "Search for Condition, click \"Condition\"")
    pdf.click_step(3, "Rename to: Condition_IsCloseAction")
    pdf.click_step(4, "This condition needs OR logic (either 'fixed' OR 'resolved'):")

    pdf.body_text("  In the condition editor:")
    pdf.click_step(5, "First row: Left = outputs('Compose_Action'), Operator = is equal to, Right = fixed")
    pdf.click_step(6, "Click \"+ Add\" > \"Add row\"")
    pdf.click_step(7, "Change the \"And\" dropdown to \"Or\" (click the And/Or toggle)")
    pdf.click_step(8, "Second row: Left = outputs('Compose_Action'), Operator = is equal to, Right = resolved")

    pdf.tip_box("Why check for both 'fixed' and 'resolved'?",
        "Different GHAS alert types use different words:\n"
        "  - Code scanning uses 'fixed' when CodeQL no longer detects the issue\n"
        "  - Some alert types use 'resolved'\n"
        "By checking both with OR logic, we handle all cases.")

    pdf.separator()

    pdf.sub_section("10b. Find the Open Work Item")

    pdf.click_step(1, "Inside the TRUE branch of Condition_IsCloseAction, click \"+\" > \"Add an action\"")
    pdf.click_step(2, "Search for HTTP, click \"HTTP\"")
    pdf.click_step(3, "Rename to: HTTP_FindWorkItemToClose")
    pdf.click_step(4, "Configure: Method = POST, same URI and Headers as Step 9a")
    pdf.click_step(5, "Set the Body to:")

    pdf.code_block(
        '{\n'
        '  "query": "SELECT [System.Id],\n'
        '    [System.State] FROM WorkItems\n'
        '    WHERE [System.Tags] CONTAINS\n'
        "    '@{outputs('Compose_GhasTag')}'\n"
        '    AND [System.TeamProject] =\n'
        "    '@{parameters('adoProject')}'\n"
        "    AND [System.State] <> 'Closed'\n"
        "    AND [System.State] <> 'Done'\n"
        "    AND [System.State] <> 'Removed'\"\n"
        '}'
    )

    pdf.tip_box("What's different from the create-branch query?",
        "We added three extra conditions:\n"
        "  State <> 'Closed' AND State <> 'Done' AND State <> 'Removed'\n"
        "This ensures we only find OPEN work items. There's no point closing something "
        "that's already closed.")

    pdf.separator()

    pdf.sub_section("10c. Check if a Work Item Was Found")

    pdf.click_step(1, "Below HTTP_FindWorkItemToClose, add another Condition")
    pdf.click_step(2, "Rename to: Condition_WorkItemFound")
    pdf.click_step(3, "Configure:")

    pdf.table(
        ["Field", "What to Enter"],
        [
            ["Left value (Expression)", "length(body(\n'HTTP_FindWorkItemToClose')\n?['workItems'])"],
            ["Operator", "is greater than"],
            ["Right value", "0"],
        ],
        [45, 125]
    )

    pdf.separator()

    pdf.sub_section("10d. Close the Work Item")

    pdf.click_step(1, "Inside the TRUE branch of Condition_WorkItemFound, add an HTTP action")
    pdf.click_step(2, "Rename to: HTTP_CloseWorkItem")
    pdf.click_step(3, "Configure:")

    pdf.table(
        ["Field", "Value"],
        [
            ["Method", "PATCH"],
            ["URI", "https://dev.azure.com/\n@{parameters('adoOrganization')}/\n@{encodeURIComponent(\nparameters('adoProject'))}/_apis/wit/\nworkitems/@{body(\n'HTTP_FindWorkItemToClose')\n?['workItems'][0]?['id']}\n?api-version=7.1"],
            ["Header: Content-Type", "application/json-patch+json"],
            ["Header: Authorization", "(same as before)"],
        ],
        [45, 125]
    )

    pdf.tip_box("Key detail in the URI",
        "Notice: ['workItems'][0]?['id']\n"
        "This grabs the ID of the FIRST matching work item from the WIQL query results "
        "and injects it into the URL. The [0] means 'first item in the array'.")

    pdf.click_step(4, "Set the Body to:")

    pdf.code_block(
        '[\n'
        '  {\n'
        '    "op": "add",\n'
        '    "path": "/fields/System.State",\n'
        '    "value": "Done"\n'
        '  },\n'
        '  {\n'
        '    "op": "add",\n'
        '    "path": "/fields/System.History",\n'
        '    "value": "Auto-closed by GHAS-ADO Sync:\n'
        '      Vulnerability marked as\n'
        "      @{outputs('Compose_Action')} in GitHub\n"
        '      Advanced Security. View alert:\n'
        "      @{outputs('Compose_AlertUrl')}\"\n"
        '  }\n'
        ']'
    )

    pdf.tip_box("What each operation does",
        "1. System.State -> 'Done': Changes the work item status to Done. We use 'Done' "
        "instead of 'Closed' because the ADO Basic process template uses 'Done' as the "
        "final state. If your project uses a different process template, change this.\n\n"
        "2. System.History: Adds a comment to the work item's discussion thread explaining "
        "why it was closed, with a link back to the GHAS alert. This creates an audit trail "
        "so anyone looking at the work item later can see it was auto-closed by the system.")

    # =========== STEP 11: SAVE AND GET URL ===========
    pdf.add_page()
    pdf.section_title(11, "Save and Get the Webhook URL")

    pdf.click_step(1, "Click \"Save\" in the top toolbar of the designer")
    pdf.click_step(2, "Click on the \"When a HTTP request is received\" trigger block at the top of the workflow")
    pdf.click_step(3, "Look for the \"HTTP POST URL\" field - it shows your webhook URL")
    pdf.click_step(4, "Click the copy icon next to the URL to copy it to your clipboard")

    pdf.body_text("The URL looks like:")
    pdf.code_block(
        "https://prod-04.eastus.logic.azure.com:443\n"
        "  /workflows/{workflow-id}\n"
        "  /triggers/When_a_GHAS_webhook_is_received\n"
        "  /paths/invoke?api-version=2019-05-01\n"
        "  &sp=...&sv=1.0&sig=..."
    )

    pdf.warning_box(
        "SECURITY: This URL contains a SAS signature (sig=...). Anyone with this URL can "
        "trigger your Logic App. Treat it like a password. Do NOT commit it to source control "
        "or share it in chat/email without encryption.")

    # =========== STEP 12: CONNECT GITHUB ===========
    pdf.section_title(12, "Connect GitHub Webhooks")

    pdf.body_text("Now we tell GitHub to send webhooks to our Logic App URL whenever a GHAS alert fires.")

    pdf.sub_section("Click-by-Click Instructions")
    pdf.click_step(1, "Open your GitHub repository in the browser")
    pdf.click_step(2, "Click \"Settings\" (tab at the top of the repo)")
    pdf.click_step(3, "In the left sidebar, click \"Webhooks\"")
    pdf.click_step(4, "Click \"Add webhook\"")
    pdf.click_step(5, "Fill in:")

    pdf.table(
        ["Field", "Value", "Why"],
        [
            ["Payload URL", "(paste the Logic App URL\nyou copied in Step 11)", "Where GitHub sends the data"],
            ["Content type", "application/json", "We need JSON format"],
            ["Secret", "LearfieldDemo2025!", "Must match your webhookSecret\nparameter exactly"],
            ["SSL verification", "Enable (checked)", "Always use SSL"],
        ],
        [35, 70, 65]
    )

    pdf.click_step(6, "Under \"Which events would you like to trigger this webhook?\":")
    pdf.click_step(7, "Select \"Let me select individual events\"")
    pdf.click_step(8, "Scroll down and check ONLY these three boxes:")
    pdf.body_text("    [x] Code scanning alerts\n    [x] Dependabot alerts\n    [x] Secret scanning alerts")
    pdf.click_step(9, "Make sure \"Active\" is checked at the bottom")
    pdf.click_step(10, "Click \"Add webhook\"")

    pdf.tip_box("What just happened?",
        "GitHub will now send an HTTP POST to your Logic App URL whenever any of the 3 "
        "GHAS alert types fires. The webhook payload includes all the alert metadata that "
        "our Compose actions extract.")

    # =========== STEP 13: TEST ===========
    pdf.add_page()
    pdf.section_title(13, "Test It End-to-End")

    pdf.sub_section("Option A: Trigger a Real Alert")
    pdf.body_text("1. Commit vulnerable code to the repo (e.g. a SQL injection pattern)")
    pdf.body_text("2. Wait for CodeQL to scan (~2-5 minutes)")
    pdf.body_text("3. A GHAS alert is created -> webhook fires -> Logic App runs -> ADO work item appears")

    pdf.sub_section("Option B: Send a Mock Webhook (Faster)")
    pdf.body_text("Open PowerShell and run this command (replace YOUR_URL with the Logic App URL):")
    pdf.code_block(
        '$body = @{\n'
        '  action = "created"\n'
        '  alert = @{\n'
        '    number = 99\n'
        '    html_url = "https://github.com/org/repo/\n'
        '      security/code-scanning/99"\n'
        '    rule = @{\n'
        '      description = "Test: SQL injection"\n'
        '      security_severity_level = "high"\n'
        '    }\n'
        '    most_recent_instance = @{\n'
        '      location = @{ path = "src/db.py";\n'
        '        start_line = 42 }\n'
        '      ref = "refs/heads/main"\n'
        '      message = @{ text = "User input\n'
        '        in SQL query" }\n'
        '    }\n'
        '  }\n'
        '  repository = @{\n'
        '    full_name = "your-org/your-repo" }\n'
        '} | ConvertTo-Json -Depth 10\n'
        '\n'
        'Invoke-RestMethod -Uri "YOUR_URL"\n'
        '  -Method POST\n'
        '  -ContentType "application/json"\n'
        '  -Headers @{\n'
        '    "X-GitHub-Event" =\n'
        '      "code_scanning_alert" }\n'
        '  -Body $body'
    )

    pdf.sub_section("Verify in Azure Portal")
    pdf.click_step(1, "Go to your Logic App in the Azure Portal")
    pdf.click_step(2, "Click \"Overview\" in the left sidebar")
    pdf.click_step(3, "Scroll down to \"Runs history\"")
    pdf.click_step(4, "Click the most recent run - it should show Succeeded (green checkmark)")
    pdf.click_step(5, "Click each action to expand it and see the inputs/outputs")

    pdf.sub_section("Verify in ADO")
    pdf.click_step(1, "Go to dev.azure.com/brandsafway1/brandsafway_Engg/_workitems")
    pdf.click_step(2, "Look for a new work item with [GHAS-CodeScan] in the title")
    pdf.click_step(3, "Click it to see the full description, tags, and hyperlink")

    # =========== STEP 14: FLOW DIAGRAM ===========
    pdf.add_page()
    pdf.section_title(14, "Complete Flow Diagram")

    pdf.body_text("Here is the complete workflow from start to finish:")
    pdf.ln(3)
    pdf.code_block(
        "GitHub Webhook POST\n"
        "       |\n"
        "       v\n"
        "+---------------------+\n"
        "|  HTTP Trigger       |\n"
        "+----------+----------+\n"
        "           v\n"
        "+---------------------+\n"
        "|  Extract Metadata   | (14 Compose actions)\n"
        "|  EventType, Title,  | (run in parallel)\n"
        "|  Severity, Tags...  |\n"
        "+----------+----------+\n"
        "           v\n"
        "    +-----------+\n"
        "    | action =  |\n"
        "    | 'created'?|\n"
        "    +--+-----+--+\n"
        "   YES |     | NO\n"
        "       v     v\n"
        "  +------+  +----------------+\n"
        "  | WIQL:|  | action =       |\n"
        "  |Exists|  | fixed/resolved?|\n"
        "  +-+--+-+  +--+----------+--+\n"
        "  NO|  |YES  YES|          |NO\n"
        "    v  +>skip    v          +> ignore\n"
        "  +------+  +--------+\n"
        "  |CREATE|  | FIND   |\n"
        "  | Work |  | Open WI|\n"
        "  | Item |  +---+----+\n"
        "  +------+      v\n"
        "            +--------+\n"
        "            | CLOSE  |\n"
        "            | Work   |\n"
        "            | Item   |\n"
        "            +--------+"
    )

    pdf.ln(5)
    pdf.sub_section("Key Design Decisions Summary")
    pdf.table(
        ["Decision", "Reasoning"],
        [
            ["Consumption plan", "Serverless, pay-per-execution, no infra to manage"],
            ["HTTP trigger", "GitHub connector doesn't support GHAS events"],
            ["Empty JSON schema", "Accept all 3 alert type payloads"],
            ["14 Compose actions", "Normalize different field paths across alert types"],
            ["WIQL deduplication", "Prevent duplicate work items from webhook retries"],
            ["Unique GHAS tag", "Links GHAS alerts to ADO work items bidirectionally"],
            ["HTTP actions (not connector)", "Full control over WIQL and JSON Patch APIs"],
            ["'Done' not 'Closed'", "ADO Basic process template terminal state"],
            ["Hyperlink relation", "Clickable link from ADO back to GHAS alert"],
        ],
        [50, 120]
    )

    # Save
    pdf.output(str(PDF_FILE))
    size_kb = PDF_FILE.stat().st_size / 1024
    print(f"PDF generated: {PDF_FILE}")
    print(f"Size: {size_kb:.0f} KB")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()
