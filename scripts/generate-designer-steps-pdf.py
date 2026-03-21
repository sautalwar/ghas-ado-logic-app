"""
Generates a detailed step-by-step PDF for building the GHAzDO Logic App
entirely in the Logic App Designer (no Code View).
Every click, menu selection, and text entry is documented.
"""

from fpdf import FPDF
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS = REPO_ROOT / "screenshots"
PDF_FILE = REPO_ROOT / "docs" / "Logic-App-Designer-Step-By-Step.pdf"

# Color palette
BLUE = (0, 120, 212)
GREEN = (16, 124, 16)
ORANGE = (255, 140, 0)
DARK = (30, 30, 30)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)
LIGHT_BG = (240, 240, 240)
CODE_BG = (245, 245, 245)
TIP_BG = (255, 249, 235)
TIP_BORDER = (255, 183, 0)
GREEN_BG = (232, 255, 232)
TABLE_HEADER_BG = (0, 120, 212)
TABLE_ALT_BG = (248, 249, 250)
SECTION_LINE = (208, 208, 208)


class DesignerPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(20, 20, 20)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*GRAY)
            self.cell(0, 5,
                      "GHAzDO Logic App - Designer Step-by-Step Guide",
                      align="R")
            self.ln(2)
            self.set_draw_color(*SECTION_LINE)
            self.line(20, self.get_y(), 190, self.get_y())
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    # ---- helper methods ----

    def section_title(self, num, title):
        self.add_page()
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*BLUE)
        self.cell(0, 12, f"Section {num}: {title}",
                  new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*BLUE)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(6)

    def sub_title(self, title):
        self.ln(3)
        if self.get_y() > 250:
            self.add_page()
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*BLUE)
        self.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)

    def sub_sub_title(self, title):
        self.ln(2)
        if self.get_y() > 255:
            self.add_page()
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(60, 60, 60)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bold_text(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def step(self, num, text):
        """Numbered step with green number."""
        if self.get_y() > 268:
            self.add_page()
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*GREEN)
        x = self.get_x()
        self.cell(8, 6, f"{num}.", align="R")
        self.set_x(x + 10)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        self.multi_cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.8)

    def bullet(self, text, indent=5):
        if self.get_y() > 268:
            self.add_page()
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK)
        self.cell(5, 5.5, "-")
        self.set_x(x + indent + 5)
        self.multi_cell(0, 5.5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.5)

    def code_block(self, text):
        self.ln(1)
        if self.get_y() > 240:
            self.add_page()
        y_start = self.get_y()
        self.set_fill_color(*CODE_BG)
        self.set_font("Courier", "", 7.5)
        lines = text.split('\n')
        h = len(lines) * 4.2 + 6
        if y_start + h > 275:
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
        self.set_y(max(self.get_y(), y_start + h) + 2)

    def tip_box(self, text):
        self._callout_box("TIP", text, TIP_BG, TIP_BORDER, (180, 130, 0),
                          (80, 60, 0))

    def warn_box(self, text):
        self._callout_box("WARNING", text, (255, 235, 230), (220, 50, 30),
                          (200, 30, 30), (120, 20, 20))

    def info_box(self, title, text):
        self._callout_box(title, text, (235, 245, 255), BLUE, BLUE,
                          (40, 40, 40))

    def success_box(self, text):
        self._callout_box("OK", text, GREEN_BG, GREEN, GREEN, (20, 80, 20))

    def _callout_box(self, label, text, bg, border_c, label_c, text_c):
        self.ln(2)
        if self.get_y() > 240:
            self.add_page()
        y_start = self.get_y()
        self.set_fill_color(*bg)
        self.set_font("Helvetica", "", 9.5)
        est_lines = len(text) / 75 + text.count('\n') + 2
        h = max(est_lines * 5 + 10, 14)
        self.rect(20, y_start, 170, h, "F")
        self.set_fill_color(*border_c)
        self.rect(20, y_start, 1.5, h, "F")
        self.set_xy(24, y_start + 2)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*label_c)
        self.cell(0, 5, label)
        self.set_xy(24, y_start + 8)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*text_c)
        self.multi_cell(162, 5, text)
        self.set_y(max(self.get_y(), y_start + h) + 2)

    def table(self, headers, rows, col_widths=None):
        self.ln(1)
        if self.get_y() > 240:
            self.add_page()
        if col_widths is None:
            w = 170 / len(headers)
            col_widths = [w] * len(headers)

        def _draw_header():
            self.set_fill_color(*TABLE_HEADER_BG)
            self.set_text_color(*WHITE)
            self.set_font("Helvetica", "B", 9)
            for i, h in enumerate(headers):
                self.cell(col_widths[i], 7, h, border=1, fill=True)
            self.ln()

        _draw_header()
        self.set_font("Helvetica", "", 8.5)
        for ri, row in enumerate(rows):
            if self.get_y() > 265:
                self.add_page()
                _draw_header()
                self.set_font("Helvetica", "", 8.5)
            if ri % 2 == 1:
                self.set_fill_color(*TABLE_ALT_BG)
            else:
                self.set_fill_color(*WHITE)
            self.set_text_color(*DARK)
            x_start = self.get_x()
            y_start = self.get_y()
            max_y = y_start
            for i, cell_text in enumerate(row):
                self.set_xy(x_start + sum(col_widths[:i]), y_start)
                self.multi_cell(col_widths[i], 5, str(cell_text),
                                border=1, fill=True)
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
        self.image(str(img_path), x=15, w=180)
        self.ln(4)


# ============================================================
# PDF CONTENT
# ============================================================

def build_pdf():
    pdf = DesignerPDF()
    pdf.alias_nb_pages()

    # ==================== COVER PAGE ====================
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*BLUE)
    pdf.cell(0, 14, "Building a GHAzDO Logic App",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 12, "Designer Step-by-Step Guide",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 8,
             "21 Components Built Entirely in the Visual Designer",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "(Zero Code View)",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_draw_color(*BLUE)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*DARK)
    details = [
        ("Audience", "Beginners / First-time Logic App users"),
        ("Total Components", "1 HTTP Trigger + 20 Actions = 21 total"),
        ("Method", "100% visual Designer - no JSON, no Code View"),
        ("Estimated Time", "30-45 minutes for first build"),
    ]
    for label, val in details:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(45, 7, f"  {label}:", align="R")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, f"  {val}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 7,
             "Every click, every menu selection, every text entry - documented.",
             align="C", new_x="LMARGIN", new_y="NEXT")

    # ==================== SECTION 1 ====================
    pdf.section_title(1, "What We're Building")

    pdf.body(
        "This guide walks you through building an Azure Logic App that "
        "connects GitHub Advanced Security for Azure DevOps (GHAzDO) to "
        "Azure DevOps Boards. When a security alert is created, the Logic "
        "App automatically creates a work item. When the alert is resolved "
        "or dismissed, it automatically closes the matching work item."
    )

    pdf.sub_title("The Logic App will:")
    pdf.bullet("Receive GHAzDO alert webhooks via an HTTP trigger")
    pdf.bullet("Extract alert details: type, severity, repo, file, line number, URL")
    pdf.bullet("Compute derived fields: unique tag, title, description, tags")
    pdf.bullet("Check if the alert is a 'created' or 'state changed' event")
    pdf.bullet("CREATE a new ADO work item when a new alert arrives (if one does not already exist)")
    pdf.bullet("CLOSE an existing ADO work item when an alert is resolved/dismissed")

    pdf.sub_title("Component Summary")
    pdf.table(
        ["Category", "Count", "Components"],
        [
            ["HTTP Trigger", "1", "When_a_GHAzDO_alert_is_received"],
            ["Field Extractors", "8", "Compose_EventType through Compose_AlertUrl"],
            ["Computed Fields", "5", "Compose_GhasTag through Compose_IsCreateEvent"],
            ["Conditions", "3", "Main condition + 2 nested conditions"],
            ["HTTP Actions", "4", "Query, Create, Find, Close work items"],
        ],
        col_widths=[35, 15, 120]
    )

    pdf.bold_text("Total: 1 trigger + 20 actions = 21 components")
    pdf.body(
        "Every single one of these components is built using ONLY the "
        "visual Designer canvas. No JSON editing. No switching to Code View. "
        "No copy-pasting workflow definitions."
    )

    # ==================== SECTION 2 ====================
    pdf.section_title(2, "Create the Logic App Resource")

    pdf.body(
        "First, we create the Logic App resource in the Azure Portal. "
        "This is the container that will host our workflow."
    )

    pdf.sub_title("Step-by-Step: Create the Resource")
    pdf.step(1, 'Open your browser and navigate to portal.azure.com')
    pdf.step(2, 'Click the "+ Create a resource" button in the top-left corner of the portal')
    pdf.step(3, 'In the search bar that appears, type "Logic App" and press Enter')
    pdf.step(4, 'In the search results, click "Logic App" (the one published by Microsoft)')
    pdf.step(5, 'Click the "Create" button on the Logic App product page')

    pdf.sub_title("Fill in the Creation Form")
    pdf.add_screenshot("01-create-logic-app-form.png",
                       "Figure 2.1 - Logic App creation form in Azure Portal")

    pdf.step(6, 'Subscription: Select your Azure subscription from the dropdown')
    pdf.step(7,
             'Resource Group: Click "Create new" and type '
             '"rg-ghas-ado-learfield", or select an existing resource group')
    pdf.step(8, 'Logic App name: Type "ghas-ado-sync-demo3"')
    pdf.step(9, 'Region: Select "East US" from the dropdown')
    pdf.step(10,
             'Plan type: Make sure "Consumption" is selected. '
             'This is the pay-per-execution plan (cheapest for demos).')
    pdf.step(11, 'Zone redundancy: Leave as "Disabled"')
    pdf.step(12, 'Click "Review + create" at the bottom of the form')
    pdf.step(13,
             'Review the summary. Verify the name, region, and plan type. '
             'Then click "Create".')
    pdf.step(14,
             'Wait for the deployment to complete. You will see '
             '"Your deployment is complete" with a green checkmark.')

    pdf.add_screenshot("02-deployment-complete.png",
                       "Figure 2.2 - Deployment complete confirmation")

    pdf.step(15, 'Click "Go to resource" to open the newly created Logic App')

    pdf.success_box(
        "Your Logic App resource is now created. You should see the "
        "Logic App Overview page with the name 'ghas-ado-sync-demo3'."
    )

    # ==================== SECTION 3 ====================
    pdf.section_title(3, "Open the Designer")

    pdf.body(
        "Now we need to open the Logic App Designer, which is the visual "
        "canvas where we build our workflow by adding and connecting components."
    )

    pdf.step(1,
             'In the Logic App overview page, look at the left sidebar menu')
    pdf.step(2,
             'Under "Development Tools", click "Logic app designer"')
    pdf.step(3,
             'The Designer canvas loads. You will see a blank canvas with '
             'a section titled "Start with a common trigger".')
    pdf.step(4,
             'You will see several trigger options like "When a HTTP request '
             'is received", "Recurrence", etc.')
    pdf.step(5,
             'Click "When a HTTP request is received" to add it as our trigger')

    pdf.tip_box(
        "If you do not see the common trigger list, click 'Add a trigger' "
        "at the top of the canvas, then search for 'HTTP' and select "
        "'When a HTTP request is received'."
    )

    # ==================== SECTION 4 ====================
    pdf.section_title(4, "Configure the HTTP Trigger")

    pdf.body(
        "The HTTP trigger is the entry point for our Logic App. It creates "
        "a webhook URL that Azure DevOps will call when a GHAzDO alert fires."
    )

    pdf.step(1,
             'The trigger card "When a HTTP request is received" appears on '
             'the canvas')
    pdf.step(2,
             'Click on the card title text "When a HTTP request is received" - '
             'triple-click to select all the text')
    pdf.step(3,
             'Type the new name: When_a_GHAzDO_alert_is_received')
    pdf.step(4,
             'You will see a field labeled "Request Body JSON Schema". '
             'Leave this field EMPTY. We will parse the body using Compose '
             'actions instead.')
    pdf.step(5,
             'The trigger is now configured. After we save later, it will '
             'generate a webhook URL automatically.')

    pdf.add_screenshot("03-trigger-added.png",
                       "Figure 4.1 - HTTP trigger configured and renamed")

    pdf.info_box("Why leave the schema empty?",
                 "GHAzDO sends different JSON structures for different alert "
                 "types (code scanning, dependency, secret). Instead of "
                 "defining a rigid schema, we use Compose actions with "
                 "coalesce() to safely extract fields regardless of structure.")

    # ==================== SECTION 5 ====================
    pdf.section_title(5, "Add the 8 Field Extractor Compose Actions")

    pdf.body(
        "Now we add 8 Compose actions that extract individual fields from "
        "the incoming webhook payload. Each one uses an expression to pull "
        "a specific piece of data."
    )

    pdf.sub_title("The Click Pattern (Repeat for Every Compose Action)")
    pdf.body(
        "For EACH of these 8 Compose actions, you will follow the exact "
        "same click sequence. Memorize this pattern - you will use it 13 "
        "times total (8 extractors + 5 computed fields)."
    )

    pdf.info_box("DESIGNER PATTERN: Adding a Compose Action",
                 "This 13-step pattern is the core Designer skill. "
                 "Every Compose action uses exactly these clicks.")

    pdf.step(1,
             'Click the "+" button below the last action on the canvas. '
             '(For the very first Compose, this is below the trigger.) '
             'The button tooltip says "Insert a new step".')
    pdf.step(2,
             'A small popup menu appears with two options: "Add an action" '
             'and "Add an agent". Click "Add an action".')
    pdf.step(3,
             'A search panel opens on the right side of the screen. '
             'Type "Compose" in the search box.')
    pdf.step(4,
             'In the search results, find the "Compose" action with the blue '
             'Data Operations icon. Click it.')
    pdf.step(5,
             'A new Compose card appears on the canvas with the default name '
             '"Compose".')
    pdf.step(6,
             'Click the card title text "Compose" - triple-click to select it.')
    pdf.step(7,
             'Type the new name (e.g., "Compose_EventType"). The name changes '
             'immediately.')
    pdf.step(8,
             'Click the "Inputs" field on the Compose card. A typeahead menu '
             'appears below the field.')
    pdf.step(9,
             'At the bottom of the typeahead menu, you will see two small '
             'icon buttons. The first icon (lightning bolt) is for dynamic '
             'content. The SECOND icon (function/fx) is for expressions.')
    pdf.step(10,
             'Click the SECOND icon button (the function/expression icon). '
             'This opens the Expression editor.')
    pdf.step(11,
             'A text input box appears with the label "Expression". '
             'Type your expression in this box (see the table below).')
    pdf.step(12,
             'Click the "Add" button below the expression text box. '
             'This inserts the expression.')
    pdf.step(13,
             'The expression appears as a green token/pill in the Inputs '
             'field. This confirms the expression was accepted.')

    pdf.tip_box(
        "If you make a typo: Click the green token in the Inputs field to "
        "re-open the Expression editor. Fix the expression, then click "
        "\"Update\" (not \"Add\") to replace it."
    )

    pdf.sub_title("Extractor #1: Compose_EventType")
    pdf.bold_text("Action Name: Compose_EventType")
    pdf.body("This extracts the event type (e.g., 'created' or 'stateChanged').")
    pdf.body("Expression to type in the Expression editor:")
    pdf.code_block("triggerBody()?['eventType']")
    pdf.step(1, 'Follow the 13-step pattern above')
    pdf.step(2, 'In step 7, type the name: Compose_EventType')
    pdf.step(3, "In step 11, type: triggerBody()?['eventType']")
    pdf.step(4, 'Click "Add". You should see a green token in the Inputs field.')

    pdf.sub_title("Extractor #2: Compose_AlertType")
    pdf.bold_text("Action Name: Compose_AlertType")
    pdf.body(
        "Extracts the alert type (code, dependency, secret). Uses coalesce() "
        "to default to 'unknown' if the field is missing."
    )
    pdf.body("Expression:")
    pdf.code_block("coalesce(triggerBody()?['resource']?['alertType'], 'unknown')")
    pdf.step(1, 'Click "+" below Compose_EventType -> "Add an action"')
    pdf.step(2, 'Search "Compose" -> click the Compose action')
    pdf.step(3, 'Rename to: Compose_AlertType')
    pdf.step(4, 'Click Inputs -> click the expression (fx) icon')
    pdf.step(5,
             "Type: coalesce(triggerBody()?['resource']?['alertType'], 'unknown')")
    pdf.step(6, 'Click "Add"')

    pdf.sub_title("Extractor #3: Compose_Severity")
    pdf.bold_text("Action Name: Compose_Severity")
    pdf.body(
        "Extracts severity and converts to lowercase. Defaults to 'medium'."
    )
    pdf.body("Expression:")
    pdf.code_block(
        "toLower(coalesce(triggerBody()?['resource']?['severity'], 'medium'))"
    )
    pdf.step(1, 'Click "+" below Compose_AlertType -> "Add an action"')
    pdf.step(2, 'Search "Compose" -> click the Compose action')
    pdf.step(3, 'Rename to: Compose_Severity')
    pdf.step(4, 'Click Inputs -> expression (fx) icon')
    pdf.step(5,
             "Type: toLower(coalesce(triggerBody()?['resource']?['severity'], "
             "'medium'))")
    pdf.step(6, 'Click "Add"')

    pdf.sub_title("Extractor #4: Compose_AlertId")
    pdf.bold_text("Action Name: Compose_AlertId")
    pdf.body(
        "Extracts the alert ID number. Tries 'alertId' first, falls back "
        "to 'id', then defaults to 0."
    )
    pdf.body("Expression:")
    pdf.code_block(
        "coalesce(triggerBody()?['resource']?['alertId'], "
        "triggerBody()?['resource']?['id'], 0)"
    )
    pdf.step(1, 'Click "+" below Compose_Severity -> "Add an action"')
    pdf.step(2, 'Search "Compose" -> click the Compose action')
    pdf.step(3, 'Rename to: Compose_AlertId')
    pdf.step(4, 'Click Inputs -> expression (fx) icon')
    pdf.step(5,
             "Type: coalesce(triggerBody()?['resource']?['alertId'], "
             "triggerBody()?['resource']?['id'], 0)")
    pdf.step(6, 'Click "Add"')

    pdf.sub_title("Extractor #5: Compose_RepoName")
    pdf.bold_text("Action Name: Compose_RepoName")
    pdf.body("Extracts the repository name. Defaults to 'unknown-repo'.")
    pdf.body("Expression:")
    pdf.code_block(
        "coalesce(triggerBody()?['resource']?['repository']?['name'], "
        "'unknown-repo')"
    )
    pdf.step(1, 'Click "+" below Compose_AlertId -> "Add an action"')
    pdf.step(2, 'Search "Compose" -> click the Compose action')
    pdf.step(3, 'Rename to: Compose_RepoName')
    pdf.step(4, 'Click Inputs -> expression (fx) icon')
    pdf.step(5,
             "Type: coalesce(triggerBody()?['resource']?['repository']"
             "?['name'], 'unknown-repo')")
    pdf.step(6, 'Click "Add"')

    pdf.sub_title("Extractor #6: Compose_FilePath")
    pdf.bold_text("Action Name: Compose_FilePath")
    pdf.body(
        "Extracts the file path from the alert location. Tries 'file' "
        "first, falls back to 'path', then 'N/A'."
    )
    pdf.body("Expression:")
    pdf.code_block(
        "coalesce(triggerBody()?['resource']?['location']?['file'], "
        "triggerBody()?['resource']?['location']?['path'], 'N/A')"
    )
    pdf.step(1, 'Click "+" below Compose_RepoName -> "Add an action"')
    pdf.step(2, 'Search "Compose" -> click the Compose action')
    pdf.step(3, 'Rename to: Compose_FilePath')
    pdf.step(4, 'Click Inputs -> expression (fx) icon')
    pdf.step(5,
             "Type: coalesce(triggerBody()?['resource']?['location']"
             "?['file'], triggerBody()?['resource']?['location']?['path'], "
             "'N/A')")
    pdf.step(6, 'Click "Add"')

    pdf.sub_title("Extractor #7: Compose_LineNumber")
    pdf.bold_text("Action Name: Compose_LineNumber")
    pdf.body("Extracts the line number. Defaults to 'N/A'.")
    pdf.body("Expression:")
    pdf.code_block(
        "coalesce(triggerBody()?['resource']?['location']?['line'], 'N/A')"
    )
    pdf.step(1, 'Click "+" below Compose_FilePath -> "Add an action"')
    pdf.step(2, 'Search "Compose" -> click the Compose action')
    pdf.step(3, 'Rename to: Compose_LineNumber')
    pdf.step(4, 'Click Inputs -> expression (fx) icon')
    pdf.step(5,
             "Type: coalesce(triggerBody()?['resource']?['location']"
             "?['line'], 'N/A')")
    pdf.step(6, 'Click "Add"')

    pdf.sub_title("Extractor #8: Compose_AlertUrl")
    pdf.bold_text("Action Name: Compose_AlertUrl")
    pdf.body(
        "Extracts the alert URL/link. Tries 'link' first, "
        "falls back to 'url', then empty string."
    )
    pdf.body("Expression:")
    pdf.code_block(
        "coalesce(triggerBody()?['resource']?['link'], "
        "triggerBody()?['resource']?['url'], '')"
    )
    pdf.step(1, 'Click "+" below Compose_LineNumber -> "Add an action"')
    pdf.step(2, 'Search "Compose" -> click the Compose action')
    pdf.step(3, 'Rename to: Compose_AlertUrl')
    pdf.step(4, 'Click Inputs -> expression (fx) icon')
    pdf.step(5,
             "Type: coalesce(triggerBody()?['resource']?['link'], "
             "triggerBody()?['resource']?['url'], '')")
    pdf.step(6, 'Click "Add"')

    pdf.add_screenshot("04-eight-extractors-complete.png",
                       "Figure 5.1 - All 8 field extractor Compose actions "
                       "on the canvas")

    pdf.success_box(
        "You now have 9 components on the canvas: 1 trigger + 8 Compose "
        "extractors. Each Compose card should show a green expression token "
        "in its Inputs field."
    )

    # ==================== SECTION 6 ====================
    pdf.section_title(6, "Add the 5 Computed Field Compose Actions")

    pdf.body(
        "Now we add 5 more Compose actions that compute derived values from "
        "the extracted fields. These use the outputs of the previous Compose "
        "actions as building blocks."
    )

    pdf.info_box("Same Click Pattern",
                 "Use the exact same 13-step pattern from Section 5. "
                 "The only difference is the name and expression for each one.")

    pdf.sub_title("Computed #9: Compose_GhasTag")
    pdf.bold_text("Action Name: Compose_GhasTag")
    pdf.body(
        "Creates a unique tag like 'GHAzDO-myrepo-42' to identify the "
        "alert in ADO work items. Used to prevent duplicate work items."
    )
    pdf.body("Expression:")
    pdf.code_block(
        "concat('GHAzDO-', outputs('Compose_RepoName'), '-', "
        "string(outputs('Compose_AlertId')))"
    )
    pdf.step(1, 'Click "+" below Compose_AlertUrl -> "Add an action"')
    pdf.step(2, 'Search "Compose" -> click the Compose action')
    pdf.step(3, 'Rename to: Compose_GhasTag')
    pdf.step(4, 'Click Inputs -> expression (fx) icon')
    pdf.step(5,
             "Type: concat('GHAzDO-', outputs('Compose_RepoName'), '-', "
             "string(outputs('Compose_AlertId')))")
    pdf.step(6, 'Click "Add"')

    pdf.sub_title("Computed #10: Compose_Title")
    pdf.bold_text("Action Name: Compose_Title")
    pdf.body(
        "Generates a descriptive work item title based on the alert type. "
        "Secret alerts get '[GHAzDO Secret]', code scanning gets "
        "'[GHAzDO-CodeScan]', and dependency alerts get '[GHAzDO-Dependency]'."
    )
    pdf.warn_box(
        "This is the LONGEST expression in the entire workflow. "
        "Type it very carefully, or copy-paste from a text editor. "
        "A single misplaced quote or parenthesis will cause an error."
    )
    pdf.body("Expression (type this entire thing in one line):")
    pdf.code_block(
        "if(equals(outputs('Compose_AlertType'),'secret'),\n"
        "  concat('[GHAzDO Secret] ',outputs('Compose_RepoName'),\n"
        "    ': Exposed credential in ',outputs('Compose_FilePath')),\n"
        "  if(equals(outputs('Compose_AlertType'),'code'),\n"
        "    concat('[GHAzDO-CodeScan] ',outputs('Compose_RepoName'),\n"
        "      ': ',outputs('Compose_FilePath'),' L',\n"
        "      outputs('Compose_LineNumber')),\n"
        "    concat('[GHAzDO-Dependency] ',\n"
        "      outputs('Compose_RepoName'),\n"
        "      ': Vulnerable component')))"
    )
    pdf.tip_box(
        "In the Expression editor, type it as ONE continuous line with NO "
        "line breaks. The multi-line format above is just for readability."
    )
    pdf.step(1, 'Click "+" below Compose_GhasTag -> "Add an action"')
    pdf.step(2, 'Search "Compose" -> click the Compose action')
    pdf.step(3, 'Rename to: Compose_Title')
    pdf.step(4, 'Click Inputs -> expression (fx) icon')
    pdf.step(5, 'Type the full expression (one continuous line, no breaks)')
    pdf.step(6, 'Click "Add" - verify the green token appears')

    pdf.sub_title("Computed #11: Compose_Tags")
    pdf.bold_text("Action Name: Compose_Tags")
    pdf.body(
        "Creates a semicolon-separated tag string like "
        "'GHAzDO;secret;high;GHAzDO-myrepo-42' for the ADO work item."
    )
    pdf.body("Expression:")
    pdf.code_block(
        "concat('GHAzDO;', outputs('Compose_AlertType'), ';', "
        "outputs('Compose_Severity'), ';', outputs('Compose_GhasTag'))"
    )
    pdf.step(1, 'Click "+" below Compose_Title -> "Add an action"')
    pdf.step(2, 'Search "Compose" -> click the Compose action')
    pdf.step(3, 'Rename to: Compose_Tags')
    pdf.step(4, 'Click Inputs -> expression (fx) icon')
    pdf.step(5,
             "Type: concat('GHAzDO;', outputs('Compose_AlertType'), ';', "
             "outputs('Compose_Severity'), ';', outputs('Compose_GhasTag'))")
    pdf.step(6, 'Click "Add"')

    pdf.sub_title("Computed #12: Compose_Description")
    pdf.bold_text("Action Name: Compose_Description")
    pdf.body(
        "Generates an HTML table for the work item description with all "
        "alert details."
    )
    pdf.warn_box(
        "This expression contains HTML tags. Use border=1 (no quotes around "
        "the 1). Do NOT use double quotes inside the HTML - the expression "
        "already uses single quotes for string boundaries."
    )
    pdf.body("Expression:")
    pdf.code_block(
        "concat('<h3>GHAzDO Security Alert</h3>',\n"
        "  '<table border=1>',\n"
        "  '<tr><td><b>Alert Type</b></td><td>',\n"
        "    outputs('Compose_AlertType'),'</td></tr>',\n"
        "  '<tr><td><b>Severity</b></td><td>',\n"
        "    outputs('Compose_Severity'),'</td></tr>',\n"
        "  '<tr><td><b>Repository</b></td><td>',\n"
        "    outputs('Compose_RepoName'),'</td></tr>',\n"
        "  '<tr><td><b>File</b></td><td>',\n"
        "    outputs('Compose_FilePath'),'</td></tr>',\n"
        "  '<tr><td><b>Line</b></td><td>',\n"
        "    outputs('Compose_LineNumber'),'</td></tr>',\n"
        "  '<tr><td><b>Alert Link</b></td><td>',\n"
        "    outputs('Compose_AlertUrl'),'</td></tr>',\n"
        "  '</table>',\n"
        "  '<p>Auto-created by GHAzDO Logic App.</p>')"
    )
    pdf.step(1, 'Click "+" below Compose_Tags -> "Add an action"')
    pdf.step(2, 'Search "Compose" -> click the Compose action')
    pdf.step(3, 'Rename to: Compose_Description')
    pdf.step(4, 'Click Inputs -> expression (fx) icon')
    pdf.step(5, 'Type the full concat(...) expression as one continuous line')
    pdf.step(6, 'Click "Add"')

    pdf.sub_title("Computed #13: Compose_IsCreateEvent")
    pdf.bold_text("Action Name: Compose_IsCreateEvent")
    pdf.body(
        "Returns true if this is a new alert (created event) or false if "
        "it is a state change (resolved/dismissed). This drives the main "
        "condition branch."
    )
    pdf.body("Expression:")
    pdf.code_block(
        "or(equals(outputs('Compose_EventType'),\n"
        "  'ms.vss-code.advancedsecurity.alert.created'),\n"
        "  contains(string(outputs('Compose_EventType')),'created'))"
    )
    pdf.step(1, 'Click "+" below Compose_Description -> "Add an action"')
    pdf.step(2, 'Search "Compose" -> click the Compose action')
    pdf.step(3, 'Rename to: Compose_IsCreateEvent')
    pdf.step(4, 'Click Inputs -> expression (fx) icon')
    pdf.step(5,
             "Type: or(equals(outputs('Compose_EventType'),"
             "'ms.vss-code.advancedsecurity.alert.created'),"
             "contains(string(outputs('Compose_EventType')),'created'))")
    pdf.step(6, 'Click "Add"')

    pdf.add_screenshot("05-all-compose-actions.png",
                       "Figure 6.1 - All 13 Compose actions visible on canvas")

    pdf.success_box(
        "You now have 14 components on the canvas: 1 trigger + 13 Compose "
        "actions. The extractors pull raw fields; the computed actions "
        "derive values from them."
    )

    # ==================== SECTION 7 ====================
    pdf.section_title(7, "Add the Main Condition Branch")

    pdf.body(
        "Now we add the main Condition that splits the workflow into two "
        "branches: one for new alerts (True) and one for state changes (False)."
    )

    pdf.sub_title("Add the Condition Control")
    pdf.step(1,
             'Click the "+" button below Compose_IsCreateEvent')
    pdf.step(2, 'Click "Add an action" in the popup menu')
    pdf.step(3,
             'In the search panel, type "Condition" in the search box')
    pdf.step(4,
             'Click "Condition" - the one in the "Control" category '
             '(it has a diamond/rhombus icon)')
    pdf.step(5,
             'A Condition card appears on the canvas with two branches: '
             '"True" on the left and "False" on the right')
    pdf.step(6,
             'Click the card title "Condition" - triple-click to select it')
    pdf.step(7, 'Type the new name: Condition_IsCreateAction')

    pdf.sub_title("Configure the Condition Expression")
    pdf.step(8,
             'In the condition row, you see three fields: left value, '
             'operator, right value')
    pdf.step(9,
             'Click "Choose a value" on the LEFT side of the condition row')
    pdf.step(10,
             'The typeahead menu appears. Click the expression (fx) icon '
             'button (the second icon at the bottom)')
    pdf.step(11,
             "In the Expression editor, type: outputs('Compose_IsCreateEvent')")
    pdf.step(12, 'Click "Add"')
    pdf.step(13,
             'The operator dropdown shows "is equal to" by default. '
             'Leave it as "is equal to".')
    pdf.step(14,
             'Click "Choose a value" on the RIGHT side of the condition row')
    pdf.step(15,
             'Type: true  (just the word true, not in quotes, not as an '
             'expression - type it directly in the field)')

    pdf.info_box("What this does",
                 "When Compose_IsCreateEvent returns true (new alert), the "
                 "workflow follows the True branch and creates a work item. "
                 "When it returns false (alert resolved/dismissed), the "
                 "workflow follows the False branch and closes the work item.")

    pdf.tip_box(
        "The True and False branches each have their own '+' button for "
        "adding actions. Make sure you click the correct branch's '+' "
        "button in the next sections."
    )

    # ==================== SECTION 8 ====================
    pdf.section_title(8, "Build the True Branch - Create Work Item")

    pdf.body(
        "The True branch handles NEW alerts. It queries ADO to check if "
        "a work item already exists for this alert, and if not, creates one."
    )

    # 8a
    pdf.sub_title("Step 8a: Add HTTP_QueryExistingWorkItem")
    pdf.body(
        "This HTTP action sends a WIQL query to Azure DevOps to check if "
        "a work item with our unique GhasTag already exists."
    )
    pdf.step(1,
             'Inside the TRUE branch, click the "+" button (it says '
             '"Insert a new step in True" or similar)')
    pdf.step(2, 'Click "Add an action"')
    pdf.step(3,
             'In the search panel, type "HTTP" in the search box')
    pdf.step(4,
             'Click "HTTP" - the plain HTTP action (NOT "HTTP + Swagger", '
             'NOT "HTTP Webhook", just "HTTP")')
    pdf.step(5,
             'A new HTTP card appears. Click the title "HTTP" -> '
             'triple-click -> type: HTTP_QueryExistingWorkItem')

    pdf.sub_sub_title("Configure the HTTP Action")
    pdf.step(6,
             'Method: Click the "Method" dropdown -> Select "POST" from '
             'the list')
    pdf.step(7,
             'URI: Click the URI field -> click the expression (fx) icon')
    pdf.step(8,
             "Type this expression in the Expression editor:\n"
             "concat('https://dev.azure.com/{YOUR_ORG}/{YOUR_PROJECT}"
             "/_apis/wit/wiql?api-version=7.0')")
    pdf.step(9, 'Click "Add"')

    pdf.warn_box(
        "Replace {YOUR_ORG} with your Azure DevOps organization name and "
        "{YOUR_PROJECT} with your project name. For example: "
        "'https://dev.azure.com/mycompany/myproject/...'")

    pdf.step(10,
             'Headers: Click "Show advanced options" if headers are not '
             'visible. You need to add two headers.')
    pdf.step(11,
             'First header row - Key: Content-Type  Value: application/json')
    pdf.step(12,
             'Click "+ Add new parameter" or the "+" next to headers to add '
             'a second row')
    pdf.step(13,
             'Second header row - Key: Authorization  Value: Basic {YOUR_BASE64_PAT}')

    pdf.warn_box(
        "Replace {YOUR_BASE64_PAT} with your Base64-encoded Personal Access "
        "Token. Generate it in ADO -> User Settings -> Personal Access Tokens "
        "with Work Items Read/Write scope. Then Base64-encode as :PAT "
        "(colon + PAT).")

    pdf.step(14,
             'Body: Click the Body field -> click the expression (fx) icon')
    pdf.step(15,
             "Type the WIQL query expression:")
    pdf.code_block(
        "json(concat('{\"query\": \"SELECT [System.Id] FROM WorkItems "
        "WHERE [System.Tags] CONTAINS ', '''', "
        "outputs('Compose_GhasTag'), '''', "
        "' AND [System.State] <> ', '''', 'Removed', '''', '\"}'))"
    )
    pdf.step(16, 'Click "Add"')

    # 8b
    pdf.sub_title("Step 8b: Add Condition_NoExistingWorkItem")
    pdf.body(
        "This nested condition checks if the WIQL query returned zero "
        "results (meaning no existing work item was found)."
    )
    pdf.step(1,
             'Click "+" below HTTP_QueryExistingWorkItem (still inside the '
             'True branch) -> "Add an action"')
    pdf.step(2, 'Search "Condition" -> click it')
    pdf.step(3, 'Rename to: Condition_NoExistingWorkItem')
    pdf.step(4,
             'Left value: Click "Choose a value" -> click expression (fx) icon')
    pdf.step(5,
             "Type: length(body('HTTP_QueryExistingWorkItem')?['workItems'])")
    pdf.step(6, 'Click "Add"')
    pdf.step(7, 'Operator: Leave as "is equal to"')
    pdf.step(8, 'Right value: Click "Choose a value" -> type: 0')

    pdf.info_box("What this does",
                 "If length(...) equals 0, it means no work item exists for "
                 "this alert yet, so we create one. If a work item already "
                 "exists, we skip creation to prevent duplicates.")

    # 8c
    pdf.sub_title("Step 8c: Add HTTP_CreateWorkItem")
    pdf.body(
        "Inside the True branch of the nested condition, we add the HTTP "
        "action that creates a new ADO work item."
    )
    pdf.step(1,
             'Inside Condition_NoExistingWorkItem -> TRUE branch, '
             'click "+" -> "Add an action"')
    pdf.step(2, 'Search "HTTP" -> click the HTTP action')
    pdf.step(3, 'Rename to: HTTP_CreateWorkItem')
    pdf.step(4,
             'Method: Click the dropdown -> Select "PATCH"')

    pdf.tip_box(
        "Yes, PATCH is correct! The ADO REST API uses PATCH with "
        "JSON Patch format for creating work items, not POST."
    )

    pdf.step(5, 'URI: Click the URI field -> expression (fx) icon')
    pdf.step(6,
             "Type: concat('https://dev.azure.com/{YOUR_ORG}/{YOUR_PROJECT}"
             "/_apis/wit/workitems/$Issue?api-version=7.0')")
    pdf.step(7, 'Click "Add"')
    pdf.step(8,
             'Headers - First row: Key: Content-Type  '
             'Value: application/json-patch+json')
    pdf.step(9,
             'Headers - Second row: Key: Authorization  '
             'Value: Basic {YOUR_BASE64_PAT}')
    pdf.step(10,
             'Body: Click the Body field -> expression (fx) icon')
    pdf.step(11, 'Type the JSON Patch body expression:')
    pdf.code_block(
        "json(concat('[{\"op\":\"add\",\"path\":\"/fields/System.Title\",\n"
        "  \"value\":\"', outputs('Compose_Title'), '\"},\n"
        " {\"op\":\"add\",\"path\":\"/fields/System.Description\",\n"
        "  \"value\":\"', outputs('Compose_Description'), '\"},\n"
        " {\"op\":\"add\",\"path\":\"/fields/System.Tags\",\n"
        "  \"value\":\"', outputs('Compose_Tags'), '\"},\n"
        " {\"op\":\"add\",\n"
        "  \"path\":\"/fields/Microsoft.VSTS.Common.Priority\",\n"
        "  \"value\":', string(if(\n"
        "    or(equals(outputs('Compose_Severity'),'critical'),\n"
        "       equals(outputs('Compose_Severity'),'high')),1,\n"
        "    if(equals(outputs('Compose_Severity'),'medium'),2,3))\n"
        "  ), '}]'))"
    )
    pdf.step(12, 'Click "Add"')

    pdf.info_box("Priority Mapping",
                 "The expression maps severity to ADO priority:\n"
                 "  critical/high -> Priority 1\n"
                 "  medium -> Priority 2\n"
                 "  low/other -> Priority 3")

    pdf.add_screenshot("06-all-21-components-complete.png",
                       "Figure 8.1 - Full workflow with all 21 components "
                       "visible on canvas")

    # ==================== SECTION 9 ====================
    pdf.section_title(9, "Build the False Branch - Close Work Item")

    pdf.body(
        "The False branch handles RESOLVED or DISMISSED alerts. It finds "
        "the matching work item in ADO and closes it."
    )

    # 9a
    pdf.sub_title("Step 9a: Add HTTP_FindWorkItemToClose")
    pdf.body(
        "This HTTP action queries ADO for the work item that matches our "
        "alert's unique GhasTag."
    )
    pdf.step(1,
             'Inside the FALSE branch of Condition_IsCreateAction, '
             'click the "+" button')
    pdf.step(2, 'Click "Add an action"')
    pdf.step(3, 'Search "HTTP" -> click the HTTP action')
    pdf.step(4, 'Rename to: HTTP_FindWorkItemToClose')

    pdf.sub_sub_title("Configure the HTTP Action")
    pdf.step(5, 'Method: Select "POST"')
    pdf.step(6, 'URI: Click -> expression (fx) icon -> type:')
    pdf.code_block(
        "concat('https://dev.azure.com/{YOUR_ORG}/{YOUR_PROJECT}"
        "/_apis/wit/wiql?api-version=7.0')"
    )
    pdf.step(7, 'Click "Add"')
    pdf.step(8,
             'Headers: Same two headers as before:\n'
             '  Content-Type: application/json\n'
             '  Authorization: Basic {YOUR_BASE64_PAT}')
    pdf.step(9, 'Body: Click -> expression (fx) icon -> type:')
    pdf.code_block(
        "json(concat('{\"query\": \"SELECT [System.Id] FROM WorkItems "
        "WHERE [System.Tags] CONTAINS ', '''', "
        "outputs('Compose_GhasTag'), '''', "
        "' AND [System.State] <> ', '''', 'Done', '''', "
        "' AND [System.State] <> ', '''', 'Removed', '''', '\"}'))"
    )
    pdf.step(10, 'Click "Add"')

    pdf.info_box("Why a different query?",
                 "The Create branch searches for any non-Removed work item "
                 "(to avoid duplicates). The Close branch searches for work "
                 "items NOT in Done or Removed state (to find active ones "
                 "to close).")

    # 9b
    pdf.sub_title("Step 9b: Add Condition_FoundWorkItemToClose")
    pdf.body(
        "This condition checks if we actually found a work item to close."
    )
    pdf.step(1,
             'Click "+" below HTTP_FindWorkItemToClose (still in False '
             'branch) -> "Add an action"')
    pdf.step(2, 'Search "Condition" -> click it')
    pdf.step(3, 'Rename to: Condition_FoundWorkItemToClose')
    pdf.step(4,
             'Left value: Click "Choose a value" -> expression (fx) icon')
    pdf.step(5,
             "Type: length(body('HTTP_FindWorkItemToClose')?['workItems'])")
    pdf.step(6, 'Click "Add"')
    pdf.step(7,
             'Operator: Click the operator dropdown. It defaults to '
             '"is equal to". Click to expand the dropdown and select '
             '"is greater than".')
    pdf.step(8, 'Right value: Click "Choose a value" -> type: 0')

    # 9c
    pdf.sub_title("Step 9c: Add HTTP_CloseWorkItem")
    pdf.body(
        "Inside the True branch of this nested condition, add the HTTP "
        "action that updates the work item state to 'Done'."
    )
    pdf.step(1,
             'Inside Condition_FoundWorkItemToClose -> TRUE branch, '
             'click "+" -> "Add an action"')
    pdf.step(2, 'Search "HTTP" -> click the HTTP action')
    pdf.step(3, 'Rename to: HTTP_CloseWorkItem')
    pdf.step(4, 'Method: Select "PATCH"')
    pdf.step(5, 'URI: Click -> expression (fx) icon -> type:')
    pdf.code_block(
        "concat('https://dev.azure.com/{YOUR_ORG}/{YOUR_PROJECT}"
        "/_apis/wit/workitems/',\n"
        "  string(first(body('HTTP_FindWorkItemToClose')\n"
        "    ?['workItems'])?['id']),\n"
        "  '?api-version=7.0')"
    )
    pdf.step(6, 'Click "Add"')

    pdf.info_box("Dynamic Work Item ID",
                 "The URI expression dynamically inserts the work item ID "
                 "from the query results using first(...)?['id']. This gets "
                 "the ID of the first matching work item.")

    pdf.step(7,
             'Headers:\n'
             '  Content-Type: application/json-patch+json\n'
             '  Authorization: Basic {YOUR_BASE64_PAT}')
    pdf.step(8, 'Body: Click -> expression (fx) icon -> type:')
    pdf.code_block(
        "json(concat('[{\"op\":\"replace\",\n"
        "  \"path\":\"/fields/System.State\",\n"
        "  \"value\":\"Done\"},\n"
        " {\"op\":\"add\",\n"
        "  \"path\":\"/fields/System.History\",\n"
        "  \"value\":\"Auto-closed: GHAzDO alert resolved/dismissed. "
        "Event: ', outputs('Compose_EventType'), '\"}]'))"
    )
    pdf.step(9, 'Click "Add"')

    pdf.success_box(
        "The workflow is now complete! You have 21 components on the canvas:\n"
        "1 trigger + 13 Compose + 3 Conditions + 4 HTTP actions = 21 total."
    )

    # ==================== SECTION 10 ====================
    pdf.section_title(10, "Save and Get the Webhook URL")

    pdf.body(
        "With all 21 components built, it is time to save the workflow "
        "and retrieve the webhook URL for ADO Service Hooks."
    )

    pdf.step(1,
             'Click the "Save" button in the top toolbar of the Designer')
    pdf.step(2,
             'Wait for the notification banner: "Successfully saved logic '
             'app workflow". This may take a few seconds.')

    pdf.add_screenshot("07-workflow-saved-success.png",
                       "Figure 10.1 - Save success notification")

    pdf.step(3,
             'Click the trigger card ("When_a_GHAzDO_alert_is_received") '
             'to expand it')
    pdf.step(4,
             'The "HTTP POST URL" field now shows a long URL starting with '
             'https://prod-XX.eastus.logic.azure.com:443/workflows/...')
    pdf.step(5,
             'Click the copy icon next to the URL to copy it to your '
             'clipboard')
    pdf.step(6,
             'Save this URL somewhere safe - you will paste it into the '
             'ADO Service Hook configuration')

    pdf.add_screenshot("08-webhook-url-revealed.png",
                       "Figure 10.2 - Webhook URL revealed after saving")

    pdf.warn_box(
        "This URL contains a secret signature (sig=...). Anyone with this "
        "URL can trigger your Logic App. Do NOT commit it to source control "
        "or share it publicly."
    )

    pdf.success_box(
        "Your Logic App is now live and ready to receive webhooks! "
        "The next step is to create ADO Service Hooks that point to this URL."
    )

    # ==================== SECTION 11 ====================
    pdf.section_title(11, "Designer Tips and Tricks")

    pdf.body(
        "Here are practical tips for working with the Logic App Designer "
        "that will save you time and frustration."
    )

    pdf.sub_title("Expression Editor")
    pdf.bullet(
        'Always click the SECOND icon button (function/fx icon) at the '
        'bottom of the typeahead popup to open the Expression editor. '
        'The first icon (lightning bolt) opens Dynamic Content, which '
        'is not what we need.',
        indent=0)
    pdf.bullet(
        'After typing an expression, always click "Add" (for new) or '
        '"Update" (for editing existing). Pressing Enter does NOT submit '
        'the expression.',
        indent=0)
    pdf.bullet(
        'If you see a red error message below the expression box, check '
        'for mismatched parentheses, missing quotes, or typos in function '
        'names.',
        indent=0)

    pdf.sub_title("Renaming Actions")
    pdf.bullet(
        'Triple-click the card title to select all the text, then type '
        'the new name. Single-clicking places the cursor but does not '
        'select.',
        indent=0)
    pdf.bullet(
        'Rename HTTP actions IMMEDIATELY after adding them. The Designer '
        'auto-names them HTTP, HTTP 1, HTTP 2, etc., which is very confusing.',
        indent=0)
    pdf.bullet(
        'Action names cannot contain spaces in references. Use underscores '
        '(e.g., Compose_EventType, not Compose EventType).',
        indent=0)

    pdf.sub_title("Working with Conditions")
    pdf.bullet(
        'The True branch is always on the LEFT, False on the RIGHT.',
        indent=0)
    pdf.bullet(
        'The "+" button inside a branch is labeled differently than the '
        'main "+" button. It may say "Insert a new step in True" or '
        '"Insert a new step in Condition-actions".',
        indent=0)
    pdf.bullet(
        'Nested conditions (a condition inside a condition branch) work '
        'the same way - click "+" inside the inner branch.',
        indent=0)

    pdf.sub_title("Common Pitfalls")
    pdf.bullet(
        'If a tooltip or popup blocks a button, click elsewhere on the '
        'canvas first to dismiss it, then try again.',
        indent=0)
    pdf.bullet(
        'Long expressions: Consider typing them in Notepad first, then '
        'copy-pasting into the Expression editor.',
        indent=0)
    pdf.bullet(
        'Save frequently! The Designer does not auto-save. If your browser '
        'crashes or you navigate away, unsaved changes are lost.',
        indent=0)
    pdf.bullet(
        'If the canvas feels cluttered, use the zoom controls (bottom-right '
        'of the Designer) to zoom out and see the full workflow.',
        indent=0)

    pdf.sub_title("Quick Reference: All 21 Components")
    pdf.table(
        ["#", "Name", "Type"],
        [
            ["1", "When_a_GHAzDO_alert_is_received", "HTTP Trigger"],
            ["2", "Compose_EventType", "Compose"],
            ["3", "Compose_AlertType", "Compose"],
            ["4", "Compose_Severity", "Compose"],
            ["5", "Compose_AlertId", "Compose"],
            ["6", "Compose_RepoName", "Compose"],
            ["7", "Compose_FilePath", "Compose"],
            ["8", "Compose_LineNumber", "Compose"],
            ["9", "Compose_AlertUrl", "Compose"],
            ["10", "Compose_GhasTag", "Compose"],
            ["11", "Compose_Title", "Compose"],
            ["12", "Compose_Tags", "Compose"],
            ["13", "Compose_Description", "Compose"],
            ["14", "Compose_IsCreateEvent", "Compose"],
            ["15", "Condition_IsCreateAction", "Condition"],
            ["16", "HTTP_QueryExistingWorkItem", "HTTP"],
            ["17", "Condition_NoExistingWorkItem", "Condition"],
            ["18", "HTTP_CreateWorkItem", "HTTP"],
            ["19", "HTTP_FindWorkItemToClose", "HTTP"],
            ["20", "Condition_FoundWorkItemToClose", "Condition"],
            ["21", "HTTP_CloseWorkItem", "HTTP"],
        ],
        col_widths=[12, 118, 40]
    )

    # ---- Output ----
    PDF_FILE.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(PDF_FILE))
    print(f"[OK] PDF generated: {PDF_FILE}")
    print(f"     Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()
