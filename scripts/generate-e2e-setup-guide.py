#!/usr/bin/env python3
"""
Generate the Demo5 GHAzDO-to-ADO End-to-End Setup Guide PDF.
Uses fpdf2 to produce a professional, screenshot-rich customer-facing document.
ALL text is ASCII-safe (no Unicode curly quotes, em dashes, or special bullets).
"""

import os
import sys
from fpdf import FPDF

# -- Paths ------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOTS_DIR = os.path.join(REPO_ROOT, "screenshots", "demo5")
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
OUTPUT_PDF = os.path.join(DOCS_DIR, "Demo5-E2E-Setup-Guide.pdf")

# -- Colors -----------------------------------------------------------------
MS_BLUE = (0, 120, 212)
DARK_TEXT = (33, 33, 33)
WHITE = (255, 255, 255)
LIGHT_GRAY = (245, 245, 245)
MED_GRAY = (200, 200, 200)
SECTION_BG = (230, 242, 255)
CODE_BG = (240, 240, 240)
WARN_RED = (200, 0, 0)
TIP_GREEN = (0, 128, 64)
TIP_BG = (232, 245, 233)


def safe(text):
    """Replace common Unicode characters with ASCII equivalents."""
    replacements = {
        "\u2018": "'", "\u2019": "'",  # curly single quotes
        "\u201c": '"', "\u201d": '"',  # curly double quotes
        "\u2013": "-", "\u2014": "--",  # en/em dash
        "\u2026": "...",               # ellipsis
        "\u2022": "-",                 # bullet
        "\u2192": "->",               # right arrow
        "\u2190": "<-",               # left arrow
        "\u2713": "[x]",              # checkmark
        "\u2717": "[ ]",              # x mark
        "\u00a0": " ",               # non-breaking space
        "\u00b7": "-",               # middle dot
        "\u25cf": "*",               # black circle
        "\u25cb": "o",               # white circle
        "\u00bb": ">>",              # right guillemet
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


class SetupGuidePDF(FPDF):
    """Custom PDF class for the E2E setup guide."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=25)
        self.toc_entries = []
        self.current_section = ""

    # -- Header / Footer ----------------------------------------------------
    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*MS_BLUE)
        self.cell(95, 8, safe("GHAzDO-to-ADO Integration | Setup Guide"), align="L")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(95, 8, safe("Confidential - Prepared for Customer"), align="R")
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
        self.cell(95, 10, safe("GHAzDO-to-ADO Integration | Setup Guide"), align="L")
        self.cell(95, 10, safe(f"Page {self.page_no()}"), align="R")

    # -- Helpers ------------------------------------------------------------
    def section_title(self, number, title):
        self.add_page()
        self.current_section = safe(f"Section {number}: {title}")
        self.toc_entries.append((self.current_section, self.page_no()))
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

    def sub_sub_heading(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(60, 60, 60)
        self.cell(0, 6, safe(text), new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*DARK_TEXT)
        self.ln(1)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK_TEXT)
        self.multi_cell(0, 5.5, safe(text))
        self.ln(1.5)

    def bullet(self, text, indent=10):
        self.set_x(self.l_margin + indent)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK_TEXT)
        w = self.w - self.r_margin - self.get_x()
        self.multi_cell(w, 5.5, safe(f"- {text}"))
        self.ln(0.5)

    def bold_bullet(self, label, desc, indent=10):
        self.set_font("Helvetica", "B", 10)
        prefix = safe(f"- {label}: ")
        self.set_x(self.l_margin + indent)
        self.cell(self.get_string_width(prefix) + 1, 5.5, prefix)
        self.set_font("Helvetica", "", 10)
        remaining_w = self.w - self.r_margin - self.get_x()
        if remaining_w < 20:
            self.ln(5.5)
            self.set_x(self.l_margin + indent + 4)
            self.multi_cell(self.w - self.r_margin - self.get_x(), 5.5, safe(desc))
        else:
            self.multi_cell(remaining_w, 5.5, safe(desc))
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

    def code_block_mixed(self, lines, highlights=None, font_size=8):
        """Code block with highlighted lines (yellow background with >> prefix)."""
        if highlights is None:
            highlights = set()
        self.ln(1)
        self.set_font("Courier", "", font_size)
        for i, line in enumerate(lines):
            s = safe(line.replace("\t", "    "))
            if i in highlights:
                self.set_fill_color(255, 255, 180)  # bright yellow
                self.set_font("Courier", "B", font_size)
                self.cell(0, 4.5, f">> {s}", fill=True,
                          new_x="LMARGIN", new_y="NEXT")
                self.set_font("Courier", "", font_size)
            else:
                self.set_fill_color(*CODE_BG)
                self.cell(0, 4.5, f"   {s}", fill=True,
                          new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*DARK_TEXT)
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
        warn_bg = (255, 243, 224)
        warn_border = (230, 126, 34)
        self.set_fill_color(*warn_bg)
        self.set_draw_color(*warn_border)
        x0 = self.get_x()
        y0 = self.get_y()
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*warn_border)
        self.cell(0, 5.5, safe("  IMPORTANT:"), fill=True,
                  new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DARK_TEXT)
        self.multi_cell(0, 5, safe(f"  {text}"), fill=True)
        y1 = self.get_y()
        self.line(x0, y0, x0, y1)
        self.set_draw_color(*MED_GRAY)
        self.ln(2)

    def add_screenshot(self, filename, caption="", width=190):
        path = os.path.join(SCREENSHOTS_DIR, filename)
        if not os.path.exists(path):
            print(f"  WARNING: Screenshot not found: {filename}")
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(*WARN_RED)
            self.cell(0, 6, safe(f"[Screenshot not available: {filename}]"),
                      new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(*DARK_TEXT)
            return
        if self.get_y() > 195:
            self.add_page()
        self.ln(2)
        try:
            self.image(path, x=10, w=width)
        except Exception as e:
            print(f"  ERROR loading {filename}: {e}")
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(*WARN_RED)
            self.cell(0, 6, safe(f"[Error loading {filename}: {e}]"),
                      new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(*DARK_TEXT)
            return
        if caption:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, safe(caption), align="C",
                      new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(*DARK_TEXT)
        self.ln(3)

    def table_row(self, cells, widths, bold=False, fill=False):
        style = "B" if bold else ""
        if fill:
            self.set_fill_color(*SECTION_BG)
        self.set_font("Helvetica", style, 9)
        h = 7
        for cell_text, w in zip(cells, widths):
            self.cell(w, h, safe(f" {cell_text}"), border=1, fill=fill)
        self.ln(h)

    def check_space(self, needed_mm=60):
        if self.get_y() > (297 - 25 - needed_mm):
            self.add_page()


# ===========================================================================
# BUILD THE PDF
# ===========================================================================
def build_pdf():
    pdf = SetupGuidePDF()

    # ===== TITLE PAGE ======================================================
    pdf.add_page()
    pdf.set_fill_color(*MS_BLUE)
    pdf.rect(0, 0, 210, 105, "F")

    pdf.set_y(22)
    pdf.set_font("Helvetica", "B", 30)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 14, safe("GHAzDO-to-ADO"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 12, safe("Logic App Integration"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, safe("Complete End-to-End Setup Guide"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(*WHITE)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 13)
    pdf.cell(0, 8, safe("Demo 5 -- Standard Workflow"), align="C",
             new_x="LMARGIN", new_y="NEXT")

    # Info box below the blue banner
    pdf.set_y(120)
    pdf.set_text_color(*DARK_TEXT)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, safe("Document Details"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(*MED_GRAY)

    info = [
        ("Audience", "DevSecOps Engineers, Security Administrators"),
        ("Date", "March 2026"),
        ("Version", "1.0"),
        ("Workflow File", "ghazdo-to-ado.json"),
        ("Classification", "Customer-Facing"),
    ]
    pdf.set_font("Helvetica", "", 10)
    for label, val in info:
        pdf.set_x(40)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(45, 7, safe(f"{label}:"), align="R")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(80, 7, safe(f"  {val}"), align="L")
        pdf.ln(7)

    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 6, safe("This guide walks through every step of deploying the GHAzDO-to-ADO"),
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, safe("Logic App integration from scratch, including screenshots."),
             align="C", new_x="LMARGIN", new_y="NEXT")

    # ===== TABLE OF CONTENTS ===============================================
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*MS_BLUE)
    pdf.cell(0, 12, safe("Table of Contents"), align="L",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*MS_BLUE)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)
    toc_page = pdf.page_no()

    toc_items = [
        ("Section 1", "Prerequisites", "3"),
        ("Section 2", "Create the Logic App in Azure Portal", "5"),
        ("Section 3", "Deploy the Workflow via Code View", "8"),
        ("Section 4", "Configure Parameters", "11"),
        ("Section 5", "Get the Webhook URL", "13"),
        ("Section 6", "Configure ADO Service Hooks", "14"),
        ("Section 7", "Understanding the Workflow", "18"),
        ("Section 8", "Testing the Integration", "21"),
        ("Section 9", "Verifying Results", "23"),
        ("Section 10", "Customization Guide", "25"),
        ("Section 11", "Troubleshooting", "27"),
        ("Section 12", "Architecture Summary", "29"),
        ("Appendix", "JSON File Reference", "30"),
    ]
    for sec, title, page_ref in toc_items:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*MS_BLUE)
        pdf.cell(28, 7, safe(sec))
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*DARK_TEXT)
        dots = "." * (80 - len(title))
        pdf.cell(140, 7, safe(f"  {title}  {dots}"))
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(20, 7, safe(page_ref), align="R")
        pdf.ln(8)

    # ===== SECTION 1: PREREQUISITES ========================================
    pdf.section_title("1", "Prerequisites")

    pdf.body("Before you begin, ensure you have the following resources and permissions in place.")

    pdf.sub_heading("Azure Requirements")
    pdf.bullet("An active Azure subscription with permissions to create Logic Apps")
    pdf.bullet("Access to the Azure Portal (portal.azure.com)")
    pdf.bullet("Contributor or Owner role on a Resource Group (or permission to create one)")

    pdf.sub_heading("Azure DevOps Requirements")
    pdf.bullet("An Azure DevOps (ADO) organization and project")
    pdf.bullet("GitHub Advanced Security for Azure DevOps (GHAzDO) enabled on the project")
    pdf.bullet("At least one repository to monitor for secrets/vulnerabilities")
    pdf.bullet("Permission to create Service Hooks in the project")
    pdf.bullet("Permission to create and modify Work Items")

    pdf.sub_heading("ADO Personal Access Token (PAT)")
    pdf.body(
        "You will need an ADO Personal Access Token (PAT) with the correct scopes. "
        "The Logic App uses this token to authenticate REST API calls to create and "
        "update Work Items."
    )
    pdf.body("Required PAT scopes:")
    pdf.bullet("Work Items -- Read, Write & Manage")
    pdf.bullet("Code -- Read")

    pdf.sub_heading("Step-by-Step: Create an ADO PAT")
    pdf.numbered_step(1, "Go to dev.azure.com/{your-org}")
    pdf.numbered_step(2, "Click the User Settings icon (gear icon, top right) -> Personal Access Tokens")
    pdf.numbered_step(3, 'Click "+ New Token"')
    pdf.numbered_step(4, 'Set the Name to "GHAzDO Logic App Integration" (or any descriptive name)')
    pdf.numbered_step(5, "Set Organization to your ADO organization (or All accessible organizations)")
    pdf.numbered_step(6, "Set Expiration to a suitable date (e.g., 90 days or custom)")
    pdf.numbered_step(7, 'Under Scopes, click "Show all scopes"')
    pdf.numbered_step(8, "Check: Work Items -> Read, Write, & Manage")
    pdf.numbered_step(9, "Check: Code -> Read")
    pdf.numbered_step(10, 'Click "Create"')
    pdf.numbered_step(11, "COPY the token immediately -- you will not be able to see it again!")

    pdf.warning_box(
        "Store the PAT securely. You will paste it into the Logic App parameters. "
        "If you lose it, you must create a new one."
    )

    pdf.sub_heading("Workflow JSON File")
    pdf.body(
        "You will need the workflow JSON file: ghazdo-to-ado.json. This file contains "
        "the complete Logic App workflow definition. It is included in the project files."
    )

    # ===== SECTION 2: CREATE LOGIC APP =====================================
    pdf.section_title("2", "Create the Logic App in Azure Portal")

    pdf.body(
        "In this section, you will create a new Logic App in the Azure Portal. "
        "This Logic App will host the workflow that processes GHAzDO alerts and "
        "creates/updates ADO Work Items automatically."
    )

    pdf.sub_heading("Step-by-Step: Create the Logic App")
    pdf.numbered_step(1, "Open your browser and go to portal.azure.com")
    pdf.numbered_step(2, 'Click "Create a resource" (the big + icon in the top left)')
    pdf.numbered_step(3, 'In the search box, type "Logic App" and press Enter')
    pdf.numbered_step(4, 'Select "Logic App" from the results and click "Create"')
    pdf.numbered_step(5, 'Select "Consumption" plan type (recommended) or "Standard" if preferred')
    pdf.numbered_step(6, "Fill in the creation form:")

    pdf.set_x(pdf.l_margin + 15)
    pdf.set_font("Helvetica", "", 10)

    form_fields = [
        ("Subscription", "Select your Azure subscription"),
        ("Resource Group", 'Create new or select existing (e.g., "rg-ghas-ado-learfield")'),
        ("Logic App name", '"ghas-ado-sync-demo5" (or your chosen name)'),
        ("Region", "East US (or your preferred Azure region)"),
        ("Plan type", "Consumption (pay-per-execution) or Standard"),
        ("Enable log analytics", "Yes (recommended for troubleshooting)"),
    ]
    widths = [45, 140]
    pdf.table_row(["Field", "Value"], widths, bold=True, fill=True)
    for field, val in form_fields:
        pdf.table_row([field, val], widths)

    pdf.ln(3)
    pdf.add_screenshot("01-create-form-filled.png",
                       "Figure 2.1: Logic App creation form filled out")

    pdf.check_space(80)
    pdf.numbered_step(7, 'Click "Review + Create" at the bottom of the form')
    pdf.numbered_step(8, "Review all settings -- ensure they are correct")

    pdf.add_screenshot("02-review-create.png",
                       "Figure 2.2: Review + Create confirmation screen")

    pdf.check_space(80)
    pdf.numbered_step(9, 'Click "Create" to start the deployment')
    pdf.numbered_step(10, "Wait for the deployment to complete (usually 1-2 minutes)")

    pdf.add_screenshot("03-deployment-complete.png",
                       "Figure 2.3: Deployment complete screen")

    pdf.check_space(80)
    pdf.numbered_step(11, 'Click "Go to resource" to open the Logic App')

    pdf.add_screenshot("04-logic-app-overview.png",
                       "Figure 2.4: Logic App overview blade")

    pdf.tip_box(
        "Note the Logic App name and resource group. You will need these later "
        "for reference and when setting up monitoring or alerts."
    )

    # ===== SECTION 3: DEPLOY WORKFLOW ======================================
    pdf.section_title("3", "Deploy the Workflow via Code View")

    pdf.body(
        "Now that the Logic App is created, you need to deploy the workflow definition. "
        "The easiest method is to paste the JSON directly into the Code View editor."
    )

    pdf.sub_heading("Step-by-Step: Deploy via Code View")
    pdf.numbered_step(1, "In the Logic App resource, click on 'Logic app designer' in the left menu (for Consumption) or navigate to Workflows (for Standard)")
    pdf.numbered_step(2, "For Standard: Click '+ Add' to create a new workflow, name it 'ghas-ado-sync', type: Stateful, then click Create")
    pdf.numbered_step(3, "Open the workflow and click the 'Code View' tab (or 'Logic app code view' for Consumption)")
    pdf.numbered_step(4, "You will see an empty JSON template (or minimal default workflow)")

    pdf.add_screenshot("05-code-view-empty.png",
                       "Figure 3.1: Empty Code View editor")

    pdf.check_space(80)
    pdf.numbered_step(5, "Open the ghazdo-to-ado.json file from the project files")
    pdf.numbered_step(6, "Select ALL the content in the JSON file (Ctrl+A) and Copy it (Ctrl+C)")
    pdf.numbered_step(7, "In the Code View editor, select ALL existing content (Ctrl+A)")
    pdf.numbered_step(8, "Paste the copied JSON (Ctrl+V)")

    pdf.add_screenshot("06-code-view-pasted.png",
                       "Figure 3.2: JSON pasted into Code View")

    pdf.check_space(80)
    pdf.numbered_step(9, 'Click "Save" in the toolbar')
    pdf.numbered_step(10, "Wait for the save confirmation")

    pdf.add_screenshot("07-code-view-saved.png",
                       "Figure 3.3: Code View after saving successfully")

    pdf.check_space(80)
    pdf.numbered_step(11, 'Click the "Designer" tab to verify the workflow loaded correctly')
    pdf.numbered_step(12, "You should see all workflow components laid out visually")

    pdf.add_screenshot("08-designer-view.png",
                       "Figure 3.4: Designer view showing all workflow components")

    pdf.check_space(60)
    pdf.tip_box(
        "If the Designer shows errors, switch back to Code View and verify the JSON "
        "is valid. Ensure you copied the entire file content."
    )

    pdf.add_screenshot("09-code-view-with-json.png",
                       "Figure 3.5: Code View with full JSON visible")

    # ===== SECTION 4: CONFIGURE PARAMETERS =================================
    pdf.section_title("4", "Configure Parameters")

    pdf.body(
        "The workflow has four parameters that MUST be configured before it will work. "
        "These parameters tell the Logic App which ADO organization and project to target, "
        "and provide authentication credentials."
    )

    pdf.sub_heading("Parameter Reference")
    widths = [38, 25, 75, 50]
    pdf.table_row(["Parameter", "Type", "Description", "Example"], widths, bold=True, fill=True)
    pdf.table_row(["adoOrganization", "String", "Your ADO org name", '"learfield"'], widths)
    pdf.table_row(["adoProject", "String", "Your ADO project name", '"SecurityDemo"'], widths)
    pdf.table_row(["adoPat", "SecureString", "Your ADO PAT token", "(paste your PAT)"], widths)
    pdf.table_row(["workItemType", "String", "Work item type to create", '"Issue" or "Bug"'], widths)

    pdf.sub_heading("How to Set Parameters")
    pdf.numbered_step(1, "In the Logic App, go to Code View")
    pdf.numbered_step(2, 'Find the "parameters" section near the top of the JSON')
    pdf.numbered_step(3, "You will see four parameter definitions with defaultValue fields")
    pdf.numbered_step(4, "Update ONLY the defaultValue lines with your actual values")

    pdf.warning_box(
        'DO NOT TOUCH the "type" lines or the structure! Only change the '
        '"defaultValue" values. The highlighted lines below show EXACTLY '
        "which lines you need to change."
    )

    pdf.body("BEFORE (default JSON -- placeholder values you must replace):")
    pdf.code_block_mixed([
        '"parameters": {',
        '    "adoOrganization": {',
        '        "type": "String",               <-- DO NOT TOUCH',
        '        "defaultValue": "your-org-name"  <-- CHANGE THIS',
        '    },',
        '    "adoProject": {',
        '        "type": "String",               <-- DO NOT TOUCH',
        '        "defaultValue": "your-project-name"  <-- CHANGE THIS',
        '    },',
        '    "adoPat": {',
        '        "type": "SecureString",          <-- DO NOT TOUCH',
        '        "defaultValue": "your-pat-token-here"  <-- CHANGE THIS',
        '    },',
        '    "workItemType": {',
        '        "type": "String",               <-- DO NOT TOUCH',
        '        "defaultValue": "Issue"          <-- CHANGE if needed',
        '    }',
        '}',
    ], highlights={3, 7, 11, 15})

    pdf.body(
        "AFTER (example with real values filled in -- "
        "highlighted lines are the ones you changed):"
    )
    pdf.code_block_mixed([
        '"parameters": {',
        '    "adoOrganization": {',
        '        "type": "String",',
        '        "defaultValue": "brandsafway1"       <-- YOUR org name',
        '    },',
        '    "adoProject": {',
        '        "type": "String",',
        '        "defaultValue": "brandsafwy_Engg"    <-- YOUR project',
        '    },',
        '    "adoPat": {',
        '        "type": "SecureString",',
        '        "defaultValue": "ghp_abc123..."       <-- YOUR PAT token',
        '    },',
        '    "workItemType": {',
        '        "type": "String",',
        '        "defaultValue": "Issue"               <-- or "Bug"',
        '    }',
        '}',
    ], highlights={3, 7, 11, 15})

    pdf.body("Where to find each value:")
    w_param = [40, 150]
    pdf.table_row(["Parameter", "Where to Find It"], w_param, bold=True, fill=True)
    pdf.table_row(
        ["adoOrganization",
         "Your ADO URL: https://dev.azure.com/{THIS-PART}"],
        w_param)
    pdf.table_row(
        ["adoProject",
         "Your ADO URL: https://dev.azure.com/org/{THIS-PART}"],
        w_param)
    pdf.table_row(
        ["adoPat",
         "ADO > User Settings (top-right) > Personal Access Tokens > New Token"],
        w_param)
    pdf.table_row(
        ["workItemType",
         '"Issue" for Basic process, "Bug" for Agile/Scrum (see table below)'],
        w_param)

    pdf.numbered_step(5, "Click Save after updating all parameters")

    pdf.warning_box(
        "The adoPat parameter is a SecureString. After saving, the value will be hidden "
        "in the portal. Make sure you have the PAT stored securely elsewhere."
    )

    pdf.sub_heading("Work Item Type Selection")
    pdf.body("The workItemType parameter depends on your ADO process template:")
    widths2 = [50, 50, 90]
    pdf.table_row(["Process Template", "Recommended Type", "Notes"], widths2, bold=True, fill=True)
    pdf.table_row(["Basic", "Issue", "Use 'Issue' for the Basic process"], widths2)
    pdf.table_row(["Agile", "Bug or User Story", "Both are available in Agile"], widths2)
    pdf.table_row(["Scrum", "Bug or PBI", "Product Backlog Item also works"], widths2)
    pdf.table_row(["CMMI", "Bug or Requirement", "Choose based on team practice"], widths2)

    # ===== SECTION 5: GET WEBHOOK URL ======================================
    pdf.section_title("5", "Get the Webhook URL")

    pdf.body(
        "The Logic App exposes a unique webhook URL that ADO Service Hooks will call. "
        "You need to copy this URL for the next section."
    )

    pdf.sub_heading("Step-by-Step: Get the URL")
    pdf.numbered_step(1, "In the Logic App, navigate to the workflow")
    pdf.numbered_step(2, 'Click "Overview" in the left menu')
    pdf.numbered_step(3, 'Find the "Workflow URL" field (or "Callback URL" for Consumption plans)')
    pdf.numbered_step(4, "Click the copy icon next to the URL to copy it to your clipboard")

    pdf.body("The URL will look something like this (DO NOT TOUCH -- just copy it):")
    pdf.code_block_mixed([
        "https://prod-XX.eastus.logic.azure.com:443/workflows/",
        "  .../triggers/When_a_GHAzDO_alert_is_received/",
        "  paths/invoke?api-version=2016-10-01",
        "  &sp=%2Ftriggers%2FWhen_a_GHAzDO_alert_is_received",
        "  &sv=1.0&sig=<your-unique-signature>",
        "",
        "  This entire URL is auto-generated by the Logic App.",
        "  DO NOT TOUCH or edit any part of it. Just COPY and PASTE.",
    ], highlights={6, 7})

    pdf.warning_box(
        "Keep this URL secret! Anyone with this URL can trigger your Logic App. "
        "Do not share it in public repositories, emails, or chat messages. "
        "If compromised, regenerate the URL from the Logic App settings."
    )

    # ===== SECTION 6: CONFIGURE ADO SERVICE HOOKS ==========================
    pdf.section_title("6", "Configure ADO Service Hooks")

    pdf.body(
        "You need to create TWO service hooks in Azure DevOps -- one for new alerts "
        "(alert created) and one for state changes (alert resolved/fixed). Both hooks "
        "will point to the same Logic App webhook URL."
    )

    pdf.sub_heading("Hook 1: Alert Created")
    pdf.body("This hook fires when GHAzDO detects a new security alert (secret, dependency, or code scanning).")

    pdf.numbered_step(1, "Go to dev.azure.com/{your-org}/{your-project}")
    pdf.numbered_step(2, "Click Project Settings (gear icon, bottom-left corner)")
    pdf.numbered_step(3, 'Click "Service hooks" under the General section')

    pdf.add_screenshot("10-ado-service-hooks-page.png",
                       "Figure 6.1: ADO Service Hooks settings page")

    pdf.check_space(40)
    pdf.numbered_step(4, 'Click the green "+" button (Create subscription)')
    pdf.numbered_step(5, 'Select "Advanced Security" as the service type')
    pdf.numbered_step(6, "Click Next")
    pdf.numbered_step(7, 'Set Trigger to "Advanced Security alert created"')
    pdf.numbered_step(8, "Repository: Select your target repository (or leave as [Any])")
    pdf.numbered_step(9, "Alert type: Leave as [Any] to catch all types (secrets, dependencies, code)")

    pdf.add_screenshot("11-service-hook-trigger.png",
                       "Figure 6.2: Service Hook trigger configuration")

    pdf.check_space(40)
    pdf.numbered_step(10, "Click Next")
    pdf.numbered_step(11, 'Action: Select "Web Hooks" -> "Send notification via HTTP POST"')
    pdf.numbered_step(12, "URL: Paste the Logic App Webhook URL from Section 5")

    pdf.add_screenshot("12-service-hook-url.png",
                       "Figure 6.3: Service Hook URL configuration")

    pdf.check_space(80)
    pdf.numbered_step(13, 'Click "Test" to verify connectivity')
    pdf.body("A successful test will show a 2xx status code and confirm the webhook is reachable.")

    pdf.add_screenshot("13-service-hook-test-result.png",
                       "Figure 6.4: Service Hook test result -- success")

    pdf.check_space(40)
    pdf.numbered_step(14, 'Click "Finish" to create the service hook')

    pdf.add_screenshot("14-hook1-created.png",
                       "Figure 6.5: First service hook created successfully")

    pdf.sub_heading("Hook 2: Alert State Changed")
    pdf.body(
        "This hook fires when a GHAzDO alert changes state (e.g., from Active to Fixed). "
        "This enables auto-closing of Work Items when secrets are remediated."
    )

    pdf.numbered_step(1, 'Repeat: Go to Project Settings -> Service hooks -> Click "+"')
    pdf.numbered_step(2, 'Select "Advanced Security" as the service type -> Click Next')
    pdf.numbered_step(3, 'Set Trigger to "Advanced Security alert state changed"')
    pdf.numbered_step(4, "Repository: Select the same repository as Hook 1")
    pdf.numbered_step(5, "Click Next")
    pdf.numbered_step(6, "Action: Web Hooks -> Send notification via HTTP POST")
    pdf.numbered_step(7, "URL: Paste the SAME Logic App Webhook URL")

    pdf.add_screenshot("15-hook2-state-changed.png",
                       "Figure 6.6: Second hook - state changed configuration")

    pdf.check_space(40)
    pdf.numbered_step(8, 'Click "Test" to verify -> then click "Finish"')

    pdf.add_screenshot("16-hook2-created.png",
                       "Figure 6.7: Second hook created successfully")

    pdf.check_space(80)
    pdf.sub_heading("Verify Both Hooks")
    pdf.body("After creating both hooks, you should see them listed in the Service Hooks page:")

    pdf.add_screenshot("17-all-service-hooks.png",
                       "Figure 6.8: All service hooks listed")

    pdf.tip_box(
        "You should see exactly two service hooks: one for 'alert created' and one for "
        "'alert state changed'. Both should point to the same Logic App webhook URL."
    )

    # ===== SECTION 7: UNDERSTANDING THE WORKFLOW ===========================
    pdf.section_title("7", "Understanding the Workflow")

    pdf.body(
        "This section explains what the Logic App does when it receives webhook "
        "notifications from ADO. Understanding the workflow helps with troubleshooting "
        "and customization."
    )

    pdf.sub_heading("Flow 1: New Alert Created")
    pdf.body("When GHAzDO detects a new secret, vulnerability, or code issue:")

    pdf.numbered_step(1, "The ADO Service Hook sends an HTTP POST to the Logic App webhook URL")
    pdf.numbered_step(2, "The Logic App trigger fires and receives the JSON payload")
    pdf.numbered_step(3, "Extractor actions parse key fields from the payload:")
    pdf.bullet("Alert ID (unique identifier)", indent=15)
    pdf.bullet("Alert type (secret, dependency, or code)", indent=15)
    pdf.bullet("Severity (critical, high, medium, low)", indent=15)
    pdf.bullet("Repository name", indent=15)
    pdf.bullet("File path and line number", indent=15)
    pdf.bullet("Secret type (e.g., Azure Storage Account Key)", indent=15)
    pdf.bullet("Alert URL (link back to GHAzDO)", indent=15)

    pdf.numbered_step(4, "Compute actions calculate derived fields:")
    pdf.bullet("Title: '[GHAzDO] {alertType}: {secretType} in {repoName}'", indent=15)
    pdf.bullet("Tags: 'GHAzDO-{repoName}-{alertId}' (used for deduplication)", indent=15)
    pdf.bullet("Priority: critical/high -> 1, medium -> 2, low -> 3", indent=15)
    pdf.bullet("Description: HTML-formatted with all alert details", indent=15)

    pdf.numbered_step(5, "Creates a Work Item in ADO via REST API (PATCH request)")
    pdf.numbered_step(6, "The Work Item includes: Title, Description, Tags, Priority, Area Path")

    pdf.sub_heading("Flow 2: Alert State Changed (Auto-Close)")
    pdf.body("When a GHAzDO alert is resolved (e.g., the secret is removed/rotated):")

    pdf.numbered_step(1, "The ADO Service Hook sends an HTTP POST with the state change event")
    pdf.numbered_step(2, "The Logic App extracts the alert ID, repo name, and new state")
    pdf.numbered_step(3, "It searches for an existing Work Item using the tag: GHAzDO-{repoName}-{alertId}")
    pdf.numbered_step(4, 'If a matching Work Item is found AND the new state is "fixed" or "resolved":')
    pdf.bullet("Updates the Work Item state to 'Done' (or 'Closed')", indent=15)
    pdf.bullet("Adds a comment: 'Auto-closed: GHAzDO alert was resolved'", indent=15)
    pdf.numbered_step(5, "If no matching Work Item is found, or the state is not resolved, it does nothing")

    pdf.sub_heading("Workflow File Statistics")
    widths3 = [80, 110]
    pdf.table_row(["Property", "Value"], widths3, bold=True, fill=True)
    pdf.table_row(["File name", "ghazdo-to-ado.json"], widths3)
    pdf.table_row(["Approximate size", "~218 lines"], widths3)
    pdf.table_row(["Configurable parameters", "4"], widths3)
    pdf.table_row(["Total actions", "~17 (Compose, HTTP, Condition)"], widths3)
    pdf.table_row(["Authentication", "Base64-encoded PAT via REST API"], widths3)
    pdf.table_row(["Interpolation", "@{...} expression syntax"], widths3)

    # ===== SECTION 8: TESTING THE INTEGRATION ==============================
    pdf.section_title("8", "Testing the Integration")

    pdf.body(
        "After setting up the Logic App and Service Hooks, you should test the integration "
        "to verify everything works end-to-end."
    )

    pdf.sub_heading("Option A: Push a Real Secret (Live Test)")
    pdf.body(
        "If GHAzDO push protection allows it (or is in report-only mode), you can push a "
        "real secret to trigger the full flow."
    )

    pdf.numbered_step(1, "In your monitored ADO repository, create a test file")
    pdf.numbered_step(2, "Add a test secret (e.g., an Azure Storage Account Key format string)")

    pdf.code_block([
        "# test-secrets/config.env",
        "AZURE_STORAGE_KEY=sv=2021-06-08&ss=bfqt&srt=sco...",
        "AWS_SECRET_KEY=AKIAIOSFODNN7EXAMPLE/wJalrXUtnFEMI...",
    ])

    pdf.numbered_step(3, "Commit and push the file to the repository")
    pdf.numbered_step(4, "GHAzDO will scan the push and create a security alert")
    pdf.numbered_step(5, "The Service Hook fires -> Logic App creates a Work Item")

    pdf.add_screenshot("18-ado-repo.png",
                       "Figure 8.1: ADO repository view")

    pdf.check_space(80)
    pdf.add_screenshot("19-secret-file-in-repo.png",
                       "Figure 8.2: Secret file visible in repository")

    pdf.check_space(80)
    pdf.sub_heading("Option B: Simulated Webhook (Recommended for Demos)")
    pdf.body(
        "You can send a test payload directly to the webhook URL using curl, Postman, "
        "or any HTTP client. This is safer and more predictable for demos."
    )

    pdf.code_block_mixed([
        'curl -X POST "<your-webhook-url>" \\',
        '  -H "Content-Type: application/json" \\',
        '  -d \'{',
        '  "eventType": "ms.vss-alerts.alert-created-event",',
        '  "resource": {',
        '    "alertId": 999,                          <-- CHANGE: unique test ID',
        '    "alertType": "secret",                   <-- DO NOT TOUCH',
        '    "severity": "critical",                  <-- CHANGE if needed',
        '    "repository": { "name": "my-repo" },     <-- CHANGE: your repo name',
        '    "location": {',
        '      "file": "test-config.env",',
        '      "startLine": 1',
        '    },',
        '    "secretType": "Azure Storage Account Key",  <-- just a LABEL',
        '    "link": "https://dev.azure.com/..."      <-- any URL is fine',
        '  },',
        '  "resourceContainers": {',
        '    "project": { "name": "MyProject" }       <-- CHANGE: your project',
        '  }',
        "}'"
    ], highlights={0, 5, 7, 8, 13, 14, 17}, font_size=7)

    pdf.add_screenshot("20-advanced-security-alerts.png",
                       "Figure 8.3: GHAzDO Advanced Security alerts page")

    # ===== SECTION 9: VERIFYING RESULTS ====================================
    pdf.section_title("9", "Verifying Results")

    pdf.body(
        "After the webhook fires (either from a real alert or simulated payload), "
        "verify the integration worked correctly."
    )

    pdf.sub_heading("Check Logic App Run History")
    pdf.numbered_step(1, "In the Azure Portal, go to your Logic App")
    pdf.numbered_step(2, "Navigate to the workflow -> Run History (or Overview for Consumption)")
    pdf.numbered_step(3, "You should see a new run entry with status 'Succeeded'")
    pdf.numbered_step(4, "Click on the run to see details of each action")
    pdf.numbered_step(5, "Verify: Trigger received the payload, all actions completed successfully")

    pdf.sub_heading("Check ADO Work Item")
    pdf.numbered_step(1, "In ADO, go to Boards -> Work Items (or Queries)")
    pdf.numbered_step(2, "Find the newly created Work Item")
    pdf.numbered_step(3, "Verify these fields are populated correctly:")
    pdf.bullet("Title: Should include alert type, secret type, and repo name")
    pdf.bullet("Tags: Should include the GHAzDO-{repoName}-{alertId} tag")
    pdf.bullet("Priority: Should map to severity (critical/high=1, medium=2, low=3)")
    pdf.bullet("Description: Should contain HTML-formatted alert details with a link to GHAzDO")

    pdf.sub_heading("Test Auto-Close (State Change)")
    pdf.numbered_step(1, "Resolve the alert in GHAzDO (fix the secret, or dismiss the alert)")
    pdf.numbered_step(2, "The second Service Hook fires -> Logic App processes the state change")
    pdf.numbered_step(3, 'Go to the Work Item in ADO -> Verify state changed to "Done"')
    pdf.numbered_step(4, 'Check for auto-close comment: "Auto-closed: GHAzDO alert was resolved"')

    pdf.check_space(80)
    pdf.add_screenshot("21-workitem-created-and-closed.png",
                       "Figure 9.1: Work Item auto-created and then auto-closed")

    # ===== SECTION 10: CUSTOMIZATION GUIDE =================================
    pdf.section_title("10", "Customization Guide - Adding Your Own Fields")

    pdf.body(
        "One of the biggest advantages of this Logic App approach is that YOU control "
        "exactly what data goes into your ADO Work Items. The workflow JSON is fully "
        "customizable -- you can add, remove, or change any field. This section walks "
        "you through every customization option step by step."
    )

    # --- 10.1: Where to customize in the JSON ---
    pdf.sub_heading("10.1  Where Exactly to Customize in the JSON")

    pdf.body(
        'Open ghazdo-to-ado.json in any text editor. The section you need to modify is '
        'the "HTTP_CreateWorkItem" action (around line 144-161). This is where the Logic '
        'App tells ADO what fields to set on the new Work Item. It uses the ADO REST API '
        '"JSON Patch" format -- an array of operations.'
    )

    pdf.body("Here is the DEFAULT body that ships with the JSON:")
    pdf.body(
        "All 4 fields below are BUILT-IN ADO fields (they exist in every ADO project). "
        "These are NOT custom fields -- you do NOT need to create them in ADO."
    )

    pdf.code_block_mixed([
        '"body": [',
        '  // BUILT-IN FIELD: System.Title (exists in every ADO project)',
        '  { "op": "add", "path": "/fields/System.Title",',
        '    "value": "@{outputs(\'Compose_Title\')}" },',
        '',
        '  // BUILT-IN FIELD: System.Description (exists in every ADO project)',
        '  { "op": "add", "path": "/fields/System.Description",',
        '    "value": "@{outputs(\'Compose_Description\')}" },',
        '',
        '  // BUILT-IN FIELD: System.Tags (exists in every ADO project)',
        '  { "op": "add", "path": "/fields/System.Tags",',
        '    "value": "@{outputs(\'Compose_Tags\')}" },',
        '',
        '  // BUILT-IN FIELD: Microsoft.VSTS.Common.Priority',
        '  { "op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority",',
        '    "value": "@if(...severity mapping...)" }',
        ']',
        '',
        '// ALL 4 fields above are BUILT-IN -- they work immediately.',
        '// "System.*" and "Microsoft.VSTS.*" = built-in ADO fields.',
        '// "Custom.*" = custom fields YOU create (see Section 10.3).',
    ], highlights={1, 5, 9, 13, 18, 19, 20})

    pdf.body(
        "Each item in this array is one field. To add YOUR OWN fields, simply add more "
        "items to this array. Each item needs three things:"
    )

    pdf.numbered_step(1, '"op": "add" -- This tells ADO to set the field value')
    pdf.numbered_step(2, '"path": "/fields/FIELD.NAME" -- The ADO field reference name')
    pdf.numbered_step(3, '"value": "YOUR VALUE" -- The value to set (text, number, etc.)')

    # --- 10.2: Built-in ADO fields catalog ---
    pdf.sub_heading("10.2  Complete Catalog of Built-in ADO Fields You Can Use")

    pdf.body(
        "These fields already exist in ADO -- you do NOT need to create them. "
        "Just add the JSON Patch entry and they will work immediately."
    )

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*MS_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, safe("  Assignment & Ownership Fields"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(2)

    w_field = [80, 110]
    pdf.table_row(["Field Path", "What It Does"], w_field, bold=True, fill=True)
    pdf.table_row(["/fields/System.AssignedTo", "Assign to a person (email or display name)"], w_field)
    pdf.table_row(["/fields/System.AreaPath", "Route to a team area (e.g., Project\\\\Security)"], w_field)
    pdf.table_row(["/fields/System.IterationPath", "Assign to a sprint (e.g., Project\\\\Sprint 5)"], w_field)
    pdf.table_row(["/fields/System.CreatedBy", "Override creator (usually auto-set)"], w_field)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*MS_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, safe("  Classification & Tracking Fields"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(2)

    pdf.table_row(["Field Path", "What It Does"], w_field, bold=True, fill=True)
    pdf.table_row(["/fields/System.State", "Set initial state (To Do, Active, etc.)"], w_field)
    pdf.table_row(["/fields/System.Reason", "Reason for the current state"], w_field)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.Priority", "Priority: 1(Critical) to 4(Low)"], w_field)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.Severity", "Severity: 1-Critical to 4-Low"], w_field)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.ValueArea", "Business or Architectural"], w_field)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.Risk", "Risk level: 1-High, 2-Medium, 3-Low"], w_field)
    pdf.table_row(["/fields/System.Tags", "Semicolon-separated tags (already used)"], w_field)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*MS_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, safe("  Planning & Effort Fields"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(2)

    pdf.table_row(["Field Path", "What It Does"], w_field, bold=True, fill=True)
    pdf.table_row(["/fields/Microsoft.VSTS.Scheduling.Effort", "Story points or effort estimate"], w_field)
    pdf.table_row(["/fields/Microsoft.VSTS.Scheduling.StoryPoints", "Story points (Agile template)"], w_field)
    pdf.table_row(["/fields/Microsoft.VSTS.Scheduling.OriginalEstimate", "Original time estimate (hours)"], w_field)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.Activity", "Activity type (Development, Testing)"], w_field)

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*MS_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, safe("  Description & History Fields"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(2)

    pdf.table_row(["Field Path", "What It Does"], w_field, bold=True, fill=True)
    pdf.table_row(["/fields/System.Description", "Rich text description (already used)"], w_field)
    pdf.table_row(["/fields/System.History", "Add a comment (discussion entry)"], w_field)
    pdf.table_row(["/fields/Microsoft.VSTS.TCM.ReproSteps", "Repro steps (Bug work items)"], w_field)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.AcceptanceCriteria", "Acceptance criteria text"], w_field)

    # --- Example: How to use a built-in field in the JSON ---
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*MS_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, safe("  Example: How to Add a Built-in Field to the JSON"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(2)

    pdf.body(
        "The tables above are your menu of built-in fields. To use any of them, "
        "you add a JSON Patch entry to the body array. Here is a step-by-step "
        "example using System.AssignedTo (built-in -- no ADO setup needed)."
    )

    pdf.body(
        "GOAL: Auto-assign every security Work Item to your security team email."
    )

    pdf.body("BEFORE (original 4 fields only):")
    pdf.code_block_mixed([
        '"body": [',
        '  { "op": "add", "path": "/fields/System.Title",  ... },',
        '  { "op": "add", "path": "/fields/System.Description",  ... },',
        '  { "op": "add", "path": "/fields/System.Tags",  ... },',
        '  { "op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority",',
        '    "value": "..." }            <-- last entry, NO comma',
        ']',
    ], highlights={5})

    pdf.body("AFTER (added 2 built-in fields -- highlighted with >>):")
    pdf.code_block_mixed([
        '"body": [',
        '  { "op": "add", "path": "/fields/System.Title",  ... },',
        '  { "op": "add", "path": "/fields/System.Description",  ... },',
        '  { "op": "add", "path": "/fields/System.Tags",  ... },',
        '  { "op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority",',
        '    "value": "..." },           <-- ADDED comma here!',
        '',
        '  // NEW: Built-in field -- assign to security team',
        '  { "op": "add",',
        '    "path": "/fields/System.AssignedTo",',
        '    "value": "security-team@company.com" },',
        '',
        '  // NEW: Built-in field -- route to Security area',
        '  { "op": "add",',
        '    "path": "/fields/System.AreaPath",',
        '    "value": "MyProject\\\\Security" }   <-- last entry: NO comma',
        ']',
    ], highlights={5, 7, 8, 9, 10, 12, 13, 14, 15})

    pdf.tip_box(
        'These are BUILT-IN fields (System.* and Microsoft.VSTS.*). '
        'They work immediately -- no ADO setup needed. Just add the entry and save. '
        'For CUSTOM fields (Custom.*), you must create the field in ADO first '
        '(see Section 10.3 below).'
    )

    pdf.body("How to tell the difference:")
    w_diff = [55, 55, 80]
    pdf.table_row(["Field Prefix", "Type", "Do You Need to Create It?"],
                  w_diff, bold=True, fill=True)
    pdf.table_row(
        ["System.*", "BUILT-IN", "NO -- exists in every ADO project automatically"],
        w_diff)
    pdf.table_row(
        ["Microsoft.VSTS.*", "BUILT-IN", "NO -- exists in every ADO project automatically"],
        w_diff)
    pdf.table_row(
        ["Custom.*", "CUSTOM", "YES -- you must create it in ADO first (Section 10.3)"],
        w_diff)

    # --- 10.3: Adding custom fields step by step ---
    pdf.sub_heading("10.3  How to Create YOUR OWN Custom Fields in ADO")

    pdf.body(
        "If the built-in fields above are not enough, you can create completely custom "
        "fields in ADO. For example: SecurityTool, VulnerabilityCategory, ComplianceTag, "
        "RemediationOwner, etc. Here is how to create them:"
    )

    pdf.numbered_step(1,
        "Go to dev.azure.com/{your-org} and click the gear icon (bottom-left) "
        "to open Organization Settings"
    )
    pdf.numbered_step(2,
        'Under "Boards", click "Process"'
    )
    pdf.numbered_step(3,
        "Find your process template (Basic, Agile, Scrum, or CMMI). "
        "If it says 'System' next to it, you need to create a custom inherited process first: "
        "Click '...' -> 'Create inherited process' -> Give it a name -> Click Create"
    )
    pdf.numbered_step(4,
        "Click on your process template name to open it"
    )
    pdf.numbered_step(5,
        "Click on the Work Item type you are using (e.g., Issue, Bug, Task)"
    )
    pdf.numbered_step(6,
        'Click "New field" at the top of the Layout tab'
    )
    pdf.numbered_step(7,
        "Fill in the field details:"
    )

    pdf.code_block_mixed([
        "Name:        SecurityTool              <-- YOUR field name (change this)",
        "Type:        Text (single line)         <-- pick from: Text, Picklist,",
        "             Integer, Decimal, DateTime, Boolean, Identity",
        "Description: The security scanning tool that detected this issue",
        "Add to page: Details (or create a new group called 'Security')",
    ], highlights={0, 1})

    pdf.numbered_step(8,
        'Click "Add field" to save. The field is now available on all Work Items of that type.'
    )

    pdf.warning_box(
        "IMPORTANT: The field reference name is auto-generated as 'Custom.FieldName' "
        "(e.g., Custom.SecurityTool). You MUST use this exact reference name in the JSON. "
        "Once created, the reference name CANNOT be changed."
    )

    # --- 10.4: Example custom fields for security ---
    pdf.sub_heading("10.4  Recommended Custom Fields for Security Teams")

    pdf.body(
        "Here are custom fields we recommend creating for security alert tracking. "
        "Create each one in ADO (Section 10.3), then add the corresponding JSON entry."
    )

    pdf.ln(3)
    w_rec = [45, 30, 55, 60]
    pdf.table_row(["Field Name", "Type", "Reference Name", "Example Value"], w_rec, bold=True, fill=True)
    pdf.table_row(["SecurityTool", "Text", "Custom.SecurityTool", "GHAzDO"], w_rec)
    pdf.table_row(["AlertCategory", "Text", "Custom.AlertCategory", "secret / code / dependency"], w_rec)
    pdf.table_row(["SourceRepo", "Text", "Custom.SourceRepo", "my-app-repo"], w_rec)
    pdf.table_row(["AlertSeverity", "Text", "Custom.AlertSeverity", "critical / high / medium / low"], w_rec)
    pdf.table_row(["FilePath", "Text", "Custom.FilePath", "src/config.env"], w_rec)
    pdf.table_row(["SecretType", "Text", "Custom.SecretType", "Azure Storage Account Key"], w_rec)
    pdf.table_row(["RemediationOwner", "Identity", "Custom.RemediationOwner", "security-team@co.com"], w_rec)
    pdf.table_row(["ComplianceTag", "Text", "Custom.ComplianceTag", "SOC2 / HIPAA / PCI-DSS"], w_rec)
    pdf.table_row(["SLADueDate", "DateTime", "Custom.SLADueDate", "2026-04-01T00:00:00Z"], w_rec)
    pdf.table_row(["AutoDetected", "Boolean", "Custom.AutoDetected", "true"], w_rec)

    # --- 10.5: Complete JSON example with custom fields ---
    pdf.sub_heading("10.5  Complete Example: JSON Body with Custom Fields Added")

    pdf.body(
        "Here is what the HTTP_CreateWorkItem body looks like after adding all the "
        "recommended custom fields. Lines with >> are NEW additions. "
        "Lines without >> are the original defaults -- DO NOT TOUCH."
    )

    pdf.code_block_mixed([
        '"body": [',
        '  // --- Standard fields (DO NOT TOUCH -- already included) ---',
        '  { "op": "add", "path": "/fields/System.Title",',
        '    "value": "@{outputs(\'Compose_Title\')}" },',
        '  { "op": "add", "path": "/fields/System.Description",',
        '    "value": "@{outputs(\'Compose_Description\')}" },',
        '  { "op": "add", "path": "/fields/System.Tags",',
        '    "value": "@{outputs(\'Compose_Tags\')}" },',
        '  { "op": "add",',
        '    "path": "/fields/Microsoft.VSTS.Common.Priority",',
        '    "value": "@if(or(equals(...severity...)),1,',
        '              if(equals(...,\'medium\'),2,3))" },',
        '',
        '  // --- NEW: Assignment fields (built-in, no ADO setup) ---',
        '  { "op": "add", "path": "/fields/System.AssignedTo",',
        '    "value": "security-team@company.com" },  <-- CHANGE: your email',
        '  { "op": "add", "path": "/fields/System.AreaPath",',
        '    "value": "MyProject\\\\Security" },        <-- CHANGE: your path',
        '  { "op": "add", "path": "/fields/System.IterationPath",',
        '    "value": "MyProject\\\\Sprint 5" },        <-- CHANGE: your sprint',
        '',
        '  // --- NEW: Custom fields (create in ADO first! Sec 10.3) ---',
        '  { "op": "add", "path": "/fields/Custom.SecurityTool",',
        '    "value": "GHAzDO" },                     <-- static (you chose this)',
        '  { "op": "add", "path": "/fields/Custom.AlertCategory",',
        '    "value": "@{outputs(\'Compose_AlertType\')}" },  <-- from ADO (not hardcoded)',
        '  { "op": "add", "path": "/fields/Custom.SourceRepo",',
        '    "value": "@{outputs(\'Compose_RepoName\')}" },   <-- from ADO (not hardcoded)',
        '  { "op": "add", "path": "/fields/Custom.AlertSeverity",',
        '    "value": "@{outputs(\'Compose_Severity\')}" },   <-- from ADO (not hardcoded)',
        '  { "op": "add", "path": "/fields/Custom.FilePath",',
        '    "value": "@{outputs(\'Compose_FilePath\')}" },   <-- from ADO (not hardcoded)',
        '  { "op": "add", "path": "/fields/Custom.ComplianceTag",',
        '    "value": "SOC2" }                        <-- static (CHANGE: your tag)',
        ']',
    ], highlights={13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33})

    pdf.body(
        "IMPORTANT: The @{outputs('Compose_...')} values are NOT hardcoded! "
        "They are automatically pulled from the data ADO sends in the webhook payload. "
        "Each time a different alert fires, these values change automatically. "
        "For example, @{outputs('Compose_AlertType')} might be 'secret' for one alert "
        "and 'dependency' for the next -- you do not type these values yourself."
    )

    pdf.body(
        "Static values like 'GHAzDO' or 'SOC2' DO stay the same for every work item -- "
        "these are labels YOU chose. But anything with @{...} is live data from ADO."
    )

    # --- 10.6: Why the work item has so many fields ---
    pdf.sub_heading("10.6  Why Does the Work Item Have So Many Fields?")

    pdf.body(
        "You may notice the auto-created Work Item has many fields populated. "
        "Here is WHY each field matters:"
    )

    pdf.ln(2)
    w_why = [50, 60, 80]
    pdf.table_row(["Field", "Value Example", "Why It Matters"], w_why, bold=True, fill=True)
    pdf.table_row(["Title", "[GHAzDO-Secret] Azure Key", "Instantly tells you what was found and where"], w_why)
    pdf.table_row(["Description", "HTML table with all details", "Full context without opening ADO Security"], w_why)
    pdf.table_row(["Tags (GHAzDO)", "GHAzDO", "Filter all security items across the board"], w_why)
    pdf.table_row(["Tags (type)", "secret / code / dependency", "Filter by alert category"], w_why)
    pdf.table_row(["Tags (severity)", "critical / high / medium", "Filter by urgency level"], w_why)
    pdf.table_row(["Tags (unique)", "GHAzDO-reponame-42", "Dedup tag: prevents duplicate work items"], w_why)
    pdf.table_row(["Priority", "1 (Critical)", "Drives board ordering and SLA tracking"], w_why)
    pdf.table_row(["State", "To Do -> Done", "Tracks lifecycle: auto-closes when resolved"], w_why)

    # --- 10.7: Understanding the tags ---
    pdf.sub_heading("10.7  Understanding Why There Are So Many Tags")

    pdf.body(
        "The workflow creates FOUR tags on every Work Item, separated by semicolons. "
        "Each tag serves a specific purpose:"
    )

    pdf.code_block([
        "Tags = GHAzDO;secret;critical;GHAzDO-my-repo-42",
        "",
        "  Tag 1: GHAzDO           -> Master filter: find ALL GHAzDO items",
        "  Tag 2: secret            -> Alert type filter (secret/code/dependency)",
        "  Tag 3: critical          -> Severity filter (critical/high/medium/low)",
        "  Tag 4: GHAzDO-my-repo-42 -> Unique ID for deduplication & auto-close",
    ])

    pdf.body(
        "Tag 4 is the most important -- it is a unique identifier combining the repo "
        "name and alert ID. This is how the auto-close flow finds the right Work Item "
        "to close when the alert is resolved. Without this tag, the Logic App would not "
        "know which Work Item corresponds to which alert."
    )

    pdf.body(
        "You can ADD more tags by modifying the Compose_Tags action in the JSON. "
        "For example, to add a team tag:"
    )

    pdf.code_block([
        '// In ghazdo-to-ado.json, find Compose_Tags (line ~73-80):',
        '"Compose_Tags": {',
        '  "inputs": "@concat(\'GHAzDO;\', outputs(\'Compose_AlertType\'),',
        '    \';\', outputs(\'Compose_Severity\'),',
        '    \';\', outputs(\'Compose_GhasTag\'),',
        '    \';SecurityTeam\')"     <-- ADD YOUR EXTRA TAG HERE',
        '}',
    ])

    # --- 10.8: Priority mapping ---
    pdf.sub_heading("10.8  Changing Priority Mapping")
    pdf.body(
        "The workflow maps GHAzDO severity to ADO priority. The default mapping is:"
    )

    widths_p = [60, 60, 70]
    pdf.table_row(["GHAzDO Severity", "ADO Priority", "Meaning"], widths_p, bold=True, fill=True)
    pdf.table_row(["critical", "1 - Critical", "Immediate action needed"], widths_p)
    pdf.table_row(["high", "1 - Critical", "Immediate action needed"], widths_p)
    pdf.table_row(["medium", "2 - High", "Address soon"], widths_p)
    pdf.table_row(["low", "3 - Medium", "Plan to address"], widths_p)
    pdf.table_row(["(other)", "3 - Medium", "Default fallback"], widths_p)

    pdf.body(
        "To change this mapping, find the priority expression in HTTP_CreateWorkItem "
        "(line ~157). The expression uses nested @if() calls:"
    )
    pdf.code_block([
        '// Current priority logic:',
        '@if(or(equals(severity,"critical"),equals(severity,"high")),',
        '    1,                    <-- Priority for critical/high',
        '    if(equals(severity,"medium"),',
        '        2,                <-- Priority for medium',
        '        3))               <-- Priority for low/other',
        '',
        '// To make high = Priority 2 instead:',
        '@if(equals(severity,"critical"),',
        '    1,',
        '    if(equals(severity,"high"),',
        '        2,',
        '        if(equals(severity,"medium"),',
        '            3,',
        '            4)))',
    ])

    # --- 10.9: Assigning to team members ---
    pdf.sub_heading("10.9  Auto-Assigning to Specific Team Members")
    pdf.body(
        "Add an AssignedTo field in the Work Item creation body to automatically route "
        "security alerts to the right person or team. You can use either an email "
        "address or a display name:"
    )
    pdf.code_block([
        '// Assign to a specific person:',
        '{ "op": "add",',
        '  "path": "/fields/System.AssignedTo",',
        '  "value": "jane.doe@company.com" }',
        '',
        '// Assign based on alert type (advanced):',
        '// Add this as a Compose action before HTTP_CreateWorkItem:',
        '"Compose_AssignTo": {',
        '  "type": "Compose",',
        '  "inputs": "@if(equals(outputs(\'Compose_AlertType\'),\'secret\'),',
        '    \'secrets-team@company.com\',',
        '    if(equals(outputs(\'Compose_AlertType\'),\'dependency\'),',
        '      \'sca-team@company.com\',',
        '      \'appsec-team@company.com\'))"',
        '}',
    ])

    # --- 10.10: Changing work item type ---
    pdf.sub_heading("10.10  Changing the Work Item Type")
    pdf.body(
        'The default workItemType parameter is "Issue" (for the Basic process template). '
        "If your ADO project uses a different process template, change this parameter:"
    )

    w_wit = [50, 50, 90]
    pdf.table_row(["Process Template", "Recommended Type", "Other Options"], w_wit, bold=True, fill=True)
    pdf.table_row(["Basic", "Issue", "Epic, Task"], w_wit)
    pdf.table_row(["Agile", "Bug", "User Story, Task, Epic"], w_wit)
    pdf.table_row(["Scrum", "Bug", "Product Backlog Item, Task"], w_wit)
    pdf.table_row(["CMMI", "Bug", "Requirement, Task, Change Request"], w_wit)

    pdf.body(
        "To change: In Code View, find the parameters section at the top of the JSON "
        'and change the defaultValue of workItemType from "Issue" to your preferred type.'
    )

    # --- 10.11: Creating an inherited process template ---
    pdf.sub_heading("10.11  Creating an Inherited Process Template in ADO")

    pdf.body(
        "Azure DevOps ships with four SYSTEM process templates: Basic, Agile, Scrum, and "
        "CMMI. These system templates are READ-ONLY -- you cannot add custom work item "
        "types or custom fields to them directly. To unlock full customization, you must "
        "create an INHERITED process. Think of it as making a copy of the system template "
        "that you own and can modify freely."
    )

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*MS_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, safe("  Why You Need an Inherited Process"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(2)

    pdf.body(
        "An inherited process gives you the ability to:"
    )
    pdf.bullet("Add custom work item types (SecurityAlert, Vulnerability, etc.)")
    pdf.bullet("Add custom fields to any work item type (built-in or custom)")
    pdf.bullet("Customize the states/workflow for each work item type")
    pdf.bullet("Change the layout of the work item form (add groups, pages, etc.)")
    pdf.bullet("Hide built-in fields you do not need")
    pdf.bullet("Add custom rules (auto-set fields, make fields required, etc.)")

    pdf.body(
        "Your existing work items, queries, boards, and backlogs are NOT affected. "
        "The inherited process includes everything from the parent template plus your changes."
    )

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*MS_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, safe("  Step-by-Step: Create an Inherited Process"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(2)

    pdf.numbered_step(1,
        "Go to dev.azure.com/{your-org} (your organization home page)"
    )
    pdf.numbered_step(2,
        "Click the GEAR ICON (bottom-left corner) to open Organization Settings"
    )
    pdf.numbered_step(3,
        'In the left sidebar, under "Boards", click "Process"'
    )
    pdf.numbered_step(4,
        "You will see the four system templates listed:"
    )
    pdf.code_block([
        "  Basic    (System)  -- simplest: Issue, Epic, Task",
        "  Agile    (System)  -- User Story, Bug, Feature, Epic, Task",
        "  Scrum    (System)  -- Product Backlog Item, Bug, Feature, Epic, Task",
        "  CMMI     (System)  -- Requirement, Bug, Change Request, Feature, Epic, Task",
        "",
        "  NOTE: If you see (System) next to the name, it is read-only.",
        "  If you see (Inherited), someone already created a custom process.",
    ])

    pdf.numbered_step(5,
        'Choose which system template to inherit FROM. For most security teams, '
        '"Basic" is the simplest starting point. Click the "..." (three dots) menu '
        "next to your chosen template."
    )
    pdf.numbered_step(6,
        'Click "Create inherited process" from the dropdown menu'
    )
    pdf.numbered_step(7,
        "In the dialog that appears, fill in:"
    )
    pdf.code_block([
        'Name:         "Security-Process"  (or any name you prefer)',
        '              Examples: "MyCompany-Security", "DevSecOps-Process",',
        '              "BrandSafway-Security"',
        "",
        "Description:  Custom process template for GHAzDO security",
        "              alert tracking with custom work item types",
        "              and security-specific fields.",
    ])

    pdf.numbered_step(8,
        'Click "Create". Your new inherited process is now ready!'
    )

    pdf.body(
        "You will be taken to the process page showing all work item types inherited "
        "from the parent. You can now add custom types and fields."
    )

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*MS_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, safe("  Adding Custom Work Item Types to Your Process"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(2)

    pdf.body(
        "Now that you have an inherited process, let us add three security-specific "
        "work item types: SecurityAlert, Vulnerability, and ComplianceFinding."
    )

    pdf.ln(2)
    pdf.set_font("Helvetica", "BI", 10)
    pdf.cell(0, 6, safe("Type 1: SecurityAlert"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)

    pdf.numbered_step(1,
        'On your inherited process page, click "New work item type" (green + button)'
    )
    pdf.numbered_step(2, "Fill in the details:")
    pdf.code_block([
        "Name:         SecurityAlert",
        "Description:  Auto-created from GHAzDO security scanning alerts",
        "Icon:         Shield (or Warning triangle)",
        "Color:        Red (#E74C3C) -- high visibility on boards",
    ])
    pdf.numbered_step(3, 'Click "Create"')
    pdf.numbered_step(4,
        'You are now on the SecurityAlert layout page. Click "New field" to add fields:'
    )
    pdf.code_block([
        "Field 1:  AlertType",
        "  Type:   Text (single line)",
        "  Desc:   Type of security alert (secret, code, dependency)",
        "",
        "Field 2:  Severity",
        "  Type:   Picklist",
        "  Values: critical, high, medium, low",
        "  Desc:   GHAzDO severity level",
        "",
        "Field 3:  SourceRepository",
        "  Type:   Text (single line)",
        "  Desc:   Repository where the alert was detected",
        "",
        "Field 4:  FilePath",
        "  Type:   Text (single line)",
        "  Desc:   File path of the affected code or secret",
        "",
        "Field 5:  SecretType",
        "  Type:   Text (single line)",
        "  Desc:   Type of exposed secret (e.g., Azure Storage Key)",
        "",
        "Field 6:  DetectedDate",
        "  Type:   DateTime",
        "  Desc:   When GHAzDO first detected the issue",
        "",
        "Field 7:  RemediationOwner",
        "  Type:   Identity",
        "  Desc:   Person responsible for fixing the issue",
    ])
    pdf.numbered_step(5,
        "OPTIONAL: Click the 'States' tab to customize the workflow:"
    )
    pdf.code_block([
        "Recommended states for SecurityAlert:",
        "",
        "  New        (Proposed)    -- Alert just received",
        "  Triaging   (InProgress)  -- Team is evaluating the alert",
        "  Remediating (InProgress) -- Fix is being implemented",
        "  Verified   (Resolved)    -- Fix confirmed, alert resolved",
        "  Closed     (Completed)   -- Fully done",
        "",
        "To add: Click 'New state' -> Enter name -> Select category -> Save",
    ])

    pdf.ln(2)
    pdf.set_font("Helvetica", "BI", 10)
    pdf.cell(0, 6, safe("Type 2: Vulnerability"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)

    pdf.numbered_step(1, 'Click "New work item type" again')
    pdf.numbered_step(2, "Fill in:")
    pdf.code_block([
        "Name:         Vulnerability",
        "Description:  Tracks code and dependency vulnerabilities from GHAzDO",
        "Icon:         Bug (or broken shield)",
        "Color:        Orange (#E67E22) -- warning level visibility",
    ])
    pdf.numbered_step(3, 'Click "Create", then add these fields:')
    pdf.code_block([
        "Field 1:  CVEID",
        "  Type:   Text (single line)",
        "  Desc:   CVE identifier (e.g., CVE-2024-1234)",
        "",
        "Field 2:  CVSSScore",
        "  Type:   Decimal",
        "  Desc:   CVSS severity score (0.0 - 10.0)",
        "",
        "Field 3:  AttackVector",
        "  Type:   Picklist",
        "  Values: Network, Adjacent, Local, Physical",
        "",
        "Field 4:  AffectedPackage",
        "  Type:   Text (single line)",
        "  Desc:   Name and version of vulnerable package",
        "",
        "Field 5:  FixVersion",
        "  Type:   Text (single line)",
        "  Desc:   Version that fixes the vulnerability",
        "",
        "Field 6:  ExploitAvailable",
        "  Type:   Picklist",
        "  Values: Yes, No, Unknown",
        "",
        "Field 7:  PatchStatus",
        "  Type:   Picklist",
        "  Values: Not Started, In Progress, Patched, Will Not Fix",
    ])

    pdf.ln(2)
    pdf.set_font("Helvetica", "BI", 10)
    pdf.cell(0, 6, safe("Type 3: ComplianceFinding"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)

    pdf.numbered_step(1, 'Click "New work item type" one more time')
    pdf.numbered_step(2, "Fill in:")
    pdf.code_block([
        "Name:         ComplianceFinding",
        "Description:  Compliance and regulatory findings from security scans",
        "Icon:         Clipboard or Document",
        "Color:        Blue (#2980B9) -- informational visibility",
    ])
    pdf.numbered_step(3, 'Click "Create", then add these fields:')
    pdf.code_block([
        "Field 1:  ComplianceFramework",
        "  Type:   Picklist",
        "  Values: SOC2, HIPAA, PCI-DSS, FedRAMP, ISO27001, NIST, GDPR",
        "",
        "Field 2:  ControlID",
        "  Type:   Text (single line)",
        "  Desc:   The specific control (e.g., SOC2 CC6.1, PCI-DSS 6.5.3)",
        "",
        "Field 3:  RiskRating",
        "  Type:   Picklist",
        "  Values: Critical, High, Medium, Low, Informational",
        "",
        "Field 4:  DueDate",
        "  Type:   DateTime",
        "  Desc:   Compliance remediation deadline",
        "",
        "Field 5:  AuditorNotes",
        "  Type:   Text (multi-line / HTML)",
        "  Desc:   Notes from compliance auditor or reviewer",
        "",
        "Field 6:  EvidenceLink",
        "  Type:   Text (single line)",
        "  Desc:   URL to evidence or documentation",
    ])

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*MS_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, safe("  Assigning the Inherited Process to Your Project"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(2)

    pdf.body(
        "After creating your inherited process with custom types, you must assign it "
        "to your ADO project. This tells the project to use YOUR process instead of "
        "the default system one."
    )

    pdf.numbered_step(1,
        "Go back to Organization Settings -> Process"
    )
    pdf.numbered_step(2,
        "Click on your inherited process name (e.g., Security-Process)"
    )
    pdf.numbered_step(3,
        'Click the "Projects" tab at the top'
    )
    pdf.numbered_step(4,
        'You will see a list of projects using this process. Click "Change" or go to:'
    )
    pdf.code_block([
        "Project Settings -> General -> Overview",
        '-> Under "Process", you will see the current process template',
        '-> Click the process name link',
        '-> Click "Change process" (top-right)',
        '-> Select "Security-Process" from the dropdown',
        '-> Click "Save"',
    ])

    pdf.warning_box(
        "IMPORTANT: Changing the process is NON-DESTRUCTIVE. All existing work items, "
        "queries, boards, and backlogs keep working. Existing items will NOT lose data. "
        "The new custom types simply become AVAILABLE for new items. However, test on a "
        "non-production project first if you are concerned."
    )

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*MS_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, safe("  Using Custom Types with the Logic App"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(2)

    pdf.body(
        "Once your project uses the inherited process, update the Logic App JSON "
        "to create your custom work item type instead of Issue:"
    )

    pdf.code_block([
        '// In ghazdo-to-ado.json, change the workItemType parameter:',
        '"workItemType": {',
        '  "type": "String",',
        '  "defaultValue": "SecurityAlert"   <-- Use YOUR custom type name',
        '}',
        '',
        '// To use custom fields, add entries to HTTP_CreateWorkItem body:',
        '"body": [',
        '  ... existing fields ...',
        '  { "op": "add",',
        '    "path": "/fields/Custom.AlertType",',
        '    "value": "@{outputs(\'Compose_AlertType\')}" },',
        '  { "op": "add",',
        '    "path": "/fields/Custom.SourceRepository",',
        '    "value": "@{outputs(\'Compose_RepoName\')}" },',
        '  { "op": "add",',
        '    "path": "/fields/Custom.Severity",',
        '    "value": "@{outputs(\'Compose_Severity\')}" },',
        '  { "op": "add",',
        '    "path": "/fields/Custom.FilePath",',
        '    "value": "@{outputs(\'Compose_FilePath\')}" }',
        ']',
    ])

    pdf.body(
        "TIP: If you created custom states (e.g., Triaging -> Remediating -> Verified -> "
        "Closed), also update the auto-close action. Find HTTP_CloseWorkItem in the JSON "
        'and change "Done" to your completed state name (e.g., "Closed" or "Verified").'
    )

    pdf.code_block([
        '// In HTTP_CloseWorkItem, change the State value:',
        '{ "op": "add",',
        '  "path": "/fields/System.State",',
        '  "value": "Closed" }    <-- Match YOUR completed state name',
    ])

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*TIP_GREEN)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, safe("  Pro Tip: Multiple Logic Apps for Different Alert Types"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.set_fill_color(*TIP_BG)
    pdf.ln(2)

    pdf.body(
        "For advanced setups, you can deploy MULTIPLE Logic Apps -- each one creating a "
        "different custom work item type based on the alert type:"
    )

    pdf.code_block([
        "Logic App 1: ghas-ado-secrets",
        '  workItemType = "SecretExposure"',
        "  Service Hook: Advanced Security alert created (filter: secret alerts only)",
        "",
        "Logic App 2: ghas-ado-vulnerabilities",
        '  workItemType = "Vulnerability"',
        "  Service Hook: Advanced Security alert created (filter: dependency alerts)",
        "",
        "Logic App 3: ghas-ado-codescan",
        '  workItemType = "ComplianceFinding"',
        "  Service Hook: Advanced Security alert created (filter: code scan alerts)",
    ])

    pdf.body(
        "Each Logic App uses the SAME ghazdo-to-ado.json -- just with a different "
        "workItemType parameter. The Service Hooks can filter by alert type to route "
        "each category to the right Logic App."
    )

    # --- 10.12: Creating your own custom work item type (detailed) ---
    pdf.sub_heading("10.12  Creating Your OWN Custom Work Item Type")

    pdf.body(
        "What if Issue, Bug, Task, or User Story do not fit your needs? "
        "You can create a COMPLETELY CUSTOM work item type in ADO -- for example, "
        '"SecurityAlert", "Vulnerability", "ComplianceFinding", or "SecretExposure". '
        "This gives your security team a dedicated item type with its own fields, "
        "states, and workflow. Here is how:"
    )

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*MS_BLUE)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 7, safe("  Step-by-Step: Create a Custom Work Item Type in ADO"), fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(2)

    pdf.numbered_step(1,
        "Go to dev.azure.com/{your-org} -> Organization Settings (gear icon, bottom-left)"
    )
    pdf.numbered_step(2,
        'Under "Boards", click "Process"'
    )
    pdf.numbered_step(3,
        "IMPORTANT: You CANNOT modify system process templates (Basic, Agile, Scrum, CMMI) "
        "directly. You must create an INHERITED process first:"
    )
    pdf.code_block([
        "a) Click the '...' (three dots) next to your current process (e.g., Basic)",
        "b) Click 'Create inherited process'",
        "c) Name it (e.g., 'Basic-Security' or 'MyCompany-Agile')",
        "d) Click 'Create'",
        "",
        "NOTE: If you already have an inherited process, skip this step.",
    ])

    pdf.numbered_step(4,
        "Click on your inherited process name to open it"
    )
    pdf.numbered_step(5,
        'Click "New work item type" (the green + button at the top)'
    )
    pdf.numbered_step(6,
        "Fill in the details:"
    )
    pdf.code_block([
        "Name:         SecurityAlert",
        "Description:  Auto-created from GHAzDO security alerts",
        "Icon:         Choose a shield or warning icon",
        "Color:        Red (#E74C3C) for high visibility",
    ])

    pdf.numbered_step(7,
        'Click "Create". Your new work item type now exists!'
    )
    pdf.numbered_step(8,
        "Now ADD FIELDS to your custom type. On the Layout tab:"
    )
    pdf.code_block([
        'a) Click "New field" to add fields one by one, OR',
        'b) Click "New group" to create a field group (e.g., "Security Details")',
        "c) Recommended fields to add:",
        "   - AlertType (Text) -- secret, code, dependency",
        "   - Severity (Picklist) -- critical, high, medium, low",
        "   - SourceRepository (Text) -- which repo triggered the alert",
        "   - FilePath (Text) -- the affected file",
        "   - SecretType (Text) -- e.g., Azure Storage Key, AWS Key",
        "   - RemediationOwner (Identity) -- person responsible for fixing",
        "   - DetectedDate (DateTime) -- when GHAzDO found the issue",
        "   - ComplianceFramework (Picklist) -- SOC2, HIPAA, PCI-DSS",
    ])

    pdf.numbered_step(9,
        "CUSTOMIZE THE STATES (workflow). Click the 'States' tab:"
    )
    pdf.code_block([
        "Default states: New -> Active -> Resolved -> Closed",
        "",
        "You can customize to match your security workflow:",
        "  New       -> Triaging    -> Remediating  -> Verified  -> Closed",
        "",
        'To add a state: Click "New state", enter name, pick a category:',
        "  - Proposed  (maps to 'New' in queries)",
        "  - InProgress (maps to 'Active' in queries)",
        "  - Resolved  (maps to 'Resolved' in queries)",
        "  - Completed (maps to 'Closed' in queries)",
    ])

    pdf.warning_box(
        "IMPORTANT: If you add custom states, you MUST update the Logic App JSON! "
        'The auto-close action sets State to "Done" -- change this to match your '
        'completed state (e.g., "Closed" or "Verified"). Find HTTP_CloseWorkItem '
        "in the JSON and update the System.State value."
    )

    pdf.numbered_step(10,
        "ASSIGN THE PROCESS to your project. Go to your project:"
    )
    pdf.code_block([
        "a) Project Settings -> General -> Overview",
        'b) Under "Process", click "Change process"',
        "c) Select your inherited process (e.g., 'Basic-Security')",
        "d) Click Save",
        "",
        "NOTE: This is non-destructive. Existing work items keep their data.",
    ])

    pdf.numbered_step(11,
        "UPDATE THE LOGIC APP to use your custom type. "
        "In Code View, change the workItemType parameter:"
    )
    pdf.code_block([
        '"parameters": {',
        '  "adoOrganization": { "type": "String" },',
        '  "adoProject": { "type": "String" },',
        '  "adoPat": { "type": "SecureString" },',
        '  "workItemType": {',
        '    "type": "String",',
        '    "defaultValue": "SecurityAlert"   <-- YOUR CUSTOM TYPE NAME',
        '  }',
        '}',
    ])

    pdf.body(
        "That is it! The Logic App will now create SecurityAlert work items "
        "instead of Issues. All your custom fields and custom states will be available."
    )

    # --- 10.12: Example custom types for different teams ---
    pdf.sub_heading("10.12  Example Custom Work Item Types for Different Teams")

    pdf.body(
        "Here are some ideas for custom work item types that different teams might create:"
    )

    pdf.ln(2)
    w_ex = [45, 50, 95]
    pdf.table_row(["Type Name", "Best For", "Custom Fields to Add"], w_ex, bold=True, fill=True)
    pdf.table_row([
        "SecurityAlert",
        "AppSec / DevSecOps",
        "AlertType, Severity, CVSS Score, CWE ID, Affected Component"
    ], w_ex)
    pdf.table_row([
        "Vulnerability",
        "Security Operations",
        "CVE ID, CVSS Score, Attack Vector, Exploit Available, Patch Status"
    ], w_ex)
    pdf.table_row([
        "SecretExposure",
        "Secret Management",
        "SecretType, ExposedIn (file), RotationStatus, ExpiryDate"
    ], w_ex)
    pdf.table_row([
        "ComplianceFinding",
        "GRC / Compliance",
        "Framework (SOC2/HIPAA), Control ID, Risk Rating, Due Date"
    ], w_ex)
    pdf.table_row([
        "DependencyAlert",
        "SCA / Supply Chain",
        "Package Name, Version, Fix Version, License, Transitive (Y/N)"
    ], w_ex)
    pdf.table_row([
        "CodeScanFinding",
        "SAST / Code Review",
        "Rule ID, CWE, Language, False Positive (Y/N), Snippet"
    ], w_ex)

    pdf.body(
        "Each of these types can have its own icon, color, states, and fields in ADO. "
        "The Logic App JSON only needs the workItemType parameter changed -- everything "
        "else works the same. You can even run MULTIPLE Logic Apps, each creating a "
        "different work item type based on the alert type (secret vs code vs dependency)."
    )

    # --- 10.13: Quick reference - what changes where ---
    pdf.sub_heading("10.13  Quick Reference: What to Change Where")

    pdf.body(
        "Here is a summary of where to make each type of customization:"
    )

    pdf.ln(2)
    w_ref = [55, 50, 85]
    pdf.table_row(["What You Want", "Change In", "How"], w_ref, bold=True, fill=True)
    pdf.table_row([
        "Use a built-in type",
        "Logic App JSON",
        'Change workItemType param (e.g., "Bug")'
    ], w_ref)
    pdf.table_row([
        "Use a custom type",
        "ADO + Logic App JSON",
        "Create type in ADO Process, then update param"
    ], w_ref)
    pdf.table_row([
        "Add built-in fields",
        "Logic App JSON only",
        "Add JSON Patch entries (Section 10.2)"
    ], w_ref)
    pdf.table_row([
        "Add custom fields",
        "ADO + Logic App JSON",
        "Create field in ADO, then add JSON entry"
    ], w_ref)
    pdf.table_row([
        "Change states",
        "ADO + Logic App JSON",
        "Edit states in Process, update close action"
    ], w_ref)
    pdf.table_row([
        "Change priority map",
        "Logic App JSON only",
        "Edit @if() expression (Section 10.8)"
    ], w_ref)
    pdf.table_row([
        "Change tags",
        "Logic App JSON only",
        "Edit Compose_Tags action (Section 10.7)"
    ], w_ref)
    pdf.table_row([
        "Auto-assign owner",
        "Logic App JSON only",
        "Add AssignedTo field (Section 10.9)"
    ], w_ref)

    # ===== SECTION 11: TROUBLESHOOTING =====================================
    pdf.section_title("11", "Troubleshooting")

    pdf.body(
        "This section covers common issues and their solutions."
    )

    pdf.sub_heading("Issue 1: Work Item Not Created")
    pdf.bold_bullet("Symptom", "Logic App runs but no Work Item appears in ADO")
    pdf.bold_bullet("Cause", "PAT expired, wrong scopes, or incorrect org/project names")
    pdf.bold_bullet("Fix", "Check Logic App run history for error details. Verify PAT is valid and has Work Items (Read, Write & Manage) scope. Verify adoOrganization and adoProject are correct.")

    pdf.sub_heading("Issue 2: 401 Unauthorized Error")
    pdf.bold_bullet("Symptom", "HTTP action returns 401 Unauthorized")
    pdf.bold_bullet("Cause", "PAT is invalid, expired, or has wrong scopes")
    pdf.bold_bullet("Fix", "Create a new PAT with correct scopes. Update the adoPat parameter in Code View and Save.")

    pdf.sub_heading("Issue 3: 400 Bad Request Error")
    pdf.bold_bullet("Symptom", "HTTP action returns 400 Bad Request when creating Work Item")
    pdf.bold_bullet("Cause", "Work item type does not exist in your process template")
    pdf.bold_bullet("Fix", 'Verify your ADO process template (Basic, Agile, Scrum, CMMI) and use the correct workItemType. For Basic, use "Issue". For Agile, use "Bug" or "User Story".')

    pdf.sub_heading("Issue 4: Service Hook Test Fails")
    pdf.bold_bullet("Symptom", "Service Hook test returns an error (timeout, 404, etc.)")
    pdf.bold_bullet("Cause", "Webhook URL is incorrect or Logic App is disabled")
    pdf.bold_bullet("Fix", "Verify the webhook URL is correct and complete. Ensure the Logic App is enabled (not disabled). Try re-copying the URL from the Logic App Overview.")

    pdf.sub_heading("Issue 5: Push Protection Blocks Secret Push")
    pdf.bold_bullet("Symptom", "Git push is rejected by GHAzDO push protection")
    pdf.bold_bullet("Cause", "GHAzDO is configured in block mode for known secret patterns")
    pdf.bold_bullet("Fix", "Use the simulated webhook approach (Option B in Section 8) instead. Or configure push protection to 'report' mode temporarily for testing.")

    pdf.sub_heading("Issue 6: Duplicate Work Items")
    pdf.bold_bullet("Symptom", "Multiple Work Items created for the same alert")
    pdf.bold_bullet("Cause", "Service Hook fired multiple times or tag search failed")
    pdf.bold_bullet("Fix", "The workflow uses tags for deduplication. Ensure the tag format is consistent. Check if the WIQL query in the workflow correctly matches existing tags.")

    pdf.sub_heading("Issue 7: Auto-Close Not Working")
    pdf.bold_bullet("Symptom", "Alert is resolved in GHAzDO but Work Item stays open")
    pdf.bold_bullet("Cause", "Second Service Hook not configured, or tag mismatch")
    pdf.bold_bullet("Fix", 'Verify both Service Hooks exist. Check that the "alert state changed" hook is active. Ensure the Work Item tag matches the format: GHAzDO-{repoName}-{alertId}.')

    # ===== SECTION 12: ARCHITECTURE SUMMARY ================================
    pdf.section_title("12", "Architecture Summary")

    pdf.body(
        "The following diagram shows the end-to-end data flow of the integration."
    )

    pdf.sub_heading("Flow 1: Alert Created -> Work Item Created")
    pdf.code_block([
        "+--------------------+",
        "| ADO Repository     |",
        "| (push code/secret) |",
        "+--------+-----------+",
        "         |",
        "         v",
        "+--------------------+",
        "| GHAzDO Scanner     |",
        "| (detects secret)   |",
        "+--------+-----------+",
        "         |",
        "         v (alert created event)",
        "+----------------------------+",
        "| ADO Service Hook #1        |",
        "| (alert created)            |",
        "+--------+-------------------+",
        "         |",
        "         v (HTTP POST to webhook)",
        "+----------------------------+",
        "| Azure Logic App            |",
        "| (ghas-ado-sync-demo5)      |",
        "| - Parse alert payload      |",
        "| - Compute title, tags, pri |",
        "| - Create Work Item via API |",
        "+--------+-------------------+",
        "         |",
        "         v (REST API PATCH)",
        "+----------------------------+",
        "| ADO Work Item              |",
        "| - Title: [GHAzDO] alert    |",
        "| - Tags: GHAzDO-repo-id     |",
        "| - Priority: 1/2/3          |",
        "| - State: New               |",
        "+----------------------------+",
    ], font_size=7)

    pdf.sub_heading("Flow 2: Alert Resolved -> Work Item Closed")
    pdf.code_block([
        "+--------------------+",
        "| GHAzDO Scanner     |",
        "| (alert resolved)   |",
        "+--------+-----------+",
        "         |",
        "         v (alert state changed event)",
        "+----------------------------+",
        "| ADO Service Hook #2        |",
        "| (alert state changed)      |",
        "+--------+-------------------+",
        "         |",
        "         v (HTTP POST to webhook)",
        "+----------------------------+",
        "| Azure Logic App            |",
        "| - Parse state change       |",
        "| - Search Work Item by tag  |",
        "| - If found + resolved:     |",
        "|   Update state to Done     |",
        "+--------+-------------------+",
        "         |",
        "         v (REST API PATCH)",
        "+----------------------------+",
        "| ADO Work Item              |",
        "| - State: Done (closed)     |",
        "| - Comment: auto-closed     |",
        "+----------------------------+",
    ], font_size=7)

    pdf.sub_heading("Component Summary")
    widths4 = [55, 135]
    pdf.table_row(["Component", "Purpose"], widths4, bold=True, fill=True)
    pdf.table_row(["GHAzDO", "Scans repos for secrets, dependencies, code issues"], widths4)
    pdf.table_row(["ADO Service Hooks (x2)", "Send webhook events to Logic App"], widths4)
    pdf.table_row(["Azure Logic App", "Processes alerts, creates/updates Work Items"], widths4)
    pdf.table_row(["ADO Work Items", "Track security issues in the team's backlog"], widths4)
    pdf.table_row(["ADO PAT", "Authenticates Logic App to ADO REST API"], widths4)

    # ===== APPENDIX: JSON FILE REFERENCE ===================================
    pdf.section_title("A", "Appendix: JSON File Reference")

    pdf.body(
        "The workflow is defined in a single JSON file: ghazdo-to-ado.json. "
        "This appendix provides a quick reference to the file structure."
    )

    pdf.sub_heading("File Overview")
    widths5 = [55, 135]
    pdf.table_row(["Property", "Details"], widths5, bold=True, fill=True)
    pdf.table_row(["File name", "ghazdo-to-ado.json"], widths5)
    pdf.table_row(["Total lines", "~218"], widths5)
    pdf.table_row(["Parameters", "4 (adoOrganization, adoProject, adoPat, workItemType)"], widths5)
    pdf.table_row(["Trigger", "HTTP Request (When_a_GHAzDO_alert_is_received)"], widths5)
    pdf.table_row(["Compose actions", "~9 (field extractors and computers)"], widths5)
    pdf.table_row(["HTTP actions", "~4 (create WI, search WI, update WI, comment)"], widths5)
    pdf.table_row(["Condition actions", "~4 (event type, severity, state checks)"], widths5)
    pdf.table_row(["Auth method", "Base64-encoded PAT in Authorization header"], widths5)

    pdf.sub_heading("Key Actions in the Workflow")

    actions = [
        ("Extract_Alert_ID", "Pulls alertId from the webhook payload"),
        ("Extract_Alert_Type", "Pulls alertType (secret, dependency, code)"),
        ("Extract_Severity", "Pulls severity (critical, high, medium, low)"),
        ("Extract_Repo_Name", "Pulls repository name from the payload"),
        ("Extract_File_Path", "Pulls file path and line number from location"),
        ("Extract_Secret_Type", "Pulls secret type (e.g., Azure Storage Key)"),
        ("Compute_Title", "Builds the Work Item title string"),
        ("Compute_Tags", "Builds the unique tag for deduplication"),
        ("Compute_Priority", "Maps severity to ADO priority (1/2/3)"),
        ("Compute_Description", "Builds HTML description with alert details"),
        ("Create_ADO_Work_Item", "HTTP PATCH to create the Work Item"),
        ("Search_Work_Item_By_Tag", "WIQL query to find existing WI by tag"),
        ("Update_Work_Item_State", "HTTP PATCH to update WI state to Done"),
        ("Add_Comment", "HTTP POST to add auto-close comment"),
        ("Check_Event_Type", "Routes between create vs. state-change flows"),
        ("Check_If_Resolved", "Checks if new state is fixed/resolved"),
        ("Check_WI_Exists", "Checks if search returned a matching WI"),
    ]
    widths6 = [55, 135]
    pdf.table_row(["Action Name", "Purpose"], widths6, bold=True, fill=True)
    for name, purpose in actions:
        pdf.table_row([name, purpose], widths6)

    pdf.sub_heading("Deployment Methods")
    pdf.body("There are multiple ways to deploy this workflow to Azure:")

    pdf.numbered_step(1, "Code View (manual) -- Paste JSON directly into the Logic App editor (covered in Section 3)")
    pdf.numbered_step(2, "ARM Template -- Deploy via Azure Resource Manager template")
    pdf.numbered_step(3, "Azure CLI -- Use az logicapp deployment to deploy programmatically")
    pdf.numbered_step(4, "Bicep -- Use Infrastructure-as-Code for repeatable deployments")

    pdf.body(
        "For initial setup and demos, the Code View method (Section 3) is recommended. "
        "For production deployments, consider ARM templates or Bicep for repeatability."
    )

    # ===== FINAL PAGE ======================================================
    pdf.add_page()
    pdf.ln(40)
    pdf.set_fill_color(*MS_BLUE)
    pdf.rect(0, 60, 210, 80, "F")
    pdf.set_y(70)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 14, safe("Setup Complete!"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 10, safe("Your GHAzDO-to-ADO integration is ready."), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, safe("Security alerts will now auto-create and auto-close Work Items."),
             align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(155)
    pdf.set_text_color(*DARK_TEXT)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, safe("Quick Reference"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    ref_items = [
        ("Logic App", "Azure Portal -> Logic Apps -> ghas-ado-sync-demo5"),
        ("Service Hooks", "ADO -> Project Settings -> Service Hooks"),
        ("Run History", "Logic App -> Workflow -> Run History"),
        ("Work Items", "ADO -> Boards -> Work Items"),
        ("Alerts", "ADO -> Repos -> Advanced Security"),
    ]
    pdf.set_font("Helvetica", "", 10)
    for label, desc in ref_items:
        pdf.set_x(30)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(35, 7, safe(f"{label}:"), align="R")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(120, 7, safe(f"  {desc}"), align="L")
        pdf.ln(7)

    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 6, safe("GHAzDO-to-ADO Logic App Integration | Setup Guide | March 2026"),
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, safe("Confidential - Prepared for Customer"),
             align="C", new_x="LMARGIN", new_y="NEXT")

    # ===== SAVE ============================================================
    os.makedirs(DOCS_DIR, exist_ok=True)
    pdf.output(OUTPUT_PDF)
    return OUTPUT_PDF


if __name__ == "__main__":
    print("Generating Demo5 E2E Setup Guide PDF...")
    print(f"  Screenshots dir: {SCREENSHOTS_DIR}")
    print(f"  Output: {OUTPUT_PDF}")
    print()
    out = build_pdf()
    size_kb = os.path.getsize(out) / 1024
    size_mb = size_kb / 1024
    print(f"\nPDF generated successfully!")
    print(f"  File: {out}")
    if size_mb >= 1:
        print(f"  Size: {size_mb:.1f} MB")
    else:
        print(f"  Size: {size_kb:.0f} KB")
    print(f"  Pages: ~30+")
