#!/usr/bin/env python3
"""
Generate the demo2 vs demo3 Logic App Comparison PDF.
Uses fpdf2 to produce a professional document explaining why both Logic Apps
work despite being built completely differently.
"""

import os
import sys
from datetime import datetime
from fpdf import FPDF

# -- Paths ------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
OUTPUT_PDF = os.path.join(DOCS_DIR, "Demo2-vs-Demo3-Comparison.pdf")

# -- Colors -----------------------------------------------------------------
MS_BLUE = (0, 120, 212)
DARK_TEXT = (33, 33, 33)
WHITE = (255, 255, 255)
LIGHT_GRAY = (240, 240, 240)
CODE_BG = (240, 240, 240)
SECTION_BG = (230, 242, 255)
TABLE_HDR = (0, 120, 212)
MED_GRAY = (200, 200, 200)


class ComparisonPDF(FPDF):
    """Custom PDF with headers, footers, and helper methods."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=25)
        self.current_section = ""

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*MS_BLUE)
        self.cell(0, 8, "Why Both Logic Apps Work: demo2 vs demo3", align="L")
        self.set_draw_color(*MS_BLUE)
        self.line(10, 14, 200, 14)
        self.ln(8)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    # -- Helpers ------------------------------------------------------------
    def section_title(self, number, title):
        self.current_section = f"{number}. {title}"
        self.ln(4)
        self.set_fill_color(*MS_BLUE)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 14)
        self.cell(
            0, 10, f"  {number}. {title}",
            fill=True, new_x="LMARGIN", new_y="NEXT",
        )
        self.ln(4)
        self.set_text_color(*DARK_TEXT)

    def sub_heading(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*MS_BLUE)
        self.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*DARK_TEXT)
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK_TEXT)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, text, indent=10):
        self.set_x(self.l_margin + indent)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK_TEXT)
        w = self.w - self.r_margin - self.get_x()
        self.multi_cell(w, 5.5, f"- {text}")
        self.ln(0.5)

    def bold_bullet(self, label, desc, indent=10):
        self.set_font("Helvetica", "B", 10)
        prefix = f"- {label}: "
        self.set_x(self.l_margin + indent)
        self.cell(self.get_string_width(prefix) + 1, 5.5, prefix)
        self.set_font("Helvetica", "", 10)
        remaining_w = self.w - self.r_margin - self.get_x()
        if remaining_w < 20:
            self.ln(5.5)
            self.set_x(self.l_margin + indent + 4)
            self.multi_cell(self.w - self.r_margin - self.get_x(), 5.5, desc)
        else:
            self.multi_cell(remaining_w, 5.5, desc)
        self.ln(0.5)

    def numbered_item(self, number, text, indent=10):
        self.set_x(self.l_margin + indent)
        self.set_font("Helvetica", "B", 10)
        prefix = f"{number}. "
        self.cell(self.get_string_width(prefix) + 1, 5.5, prefix)
        self.set_font("Helvetica", "", 10)
        remaining_w = self.w - self.r_margin - self.get_x()
        if remaining_w < 20:
            self.ln(5.5)
            self.set_x(self.l_margin + indent + 4)
            self.multi_cell(self.w - self.r_margin - self.get_x(), 5.5, text)
        else:
            self.multi_cell(remaining_w, 5.5, text)
        self.ln(0.5)

    def code_block(self, lines, font_size=7.5):
        self.ln(1)
        self.set_fill_color(*CODE_BG)
        self.set_font("Courier", "", font_size)
        self.set_text_color(*DARK_TEXT)
        for line in lines:
            safe = line.replace("\t", "    ")
            # Truncate very long lines to avoid overflow
            max_chars = 105
            if len(safe) > max_chars:
                safe = safe[: max_chars - 3] + "..."
            self.cell(
                0, 4.2, f"  {safe}",
                fill=True, new_x="LMARGIN", new_y="NEXT",
            )
        self.ln(2)

    def info_box(self, title, text):
        """Blue-tinted info box."""
        self.ln(2)
        self.set_fill_color(*SECTION_BG)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*MS_BLUE)
        self.cell(
            0, 7, f"  {title}",
            fill=True, new_x="LMARGIN", new_y="NEXT",
        )
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*DARK_TEXT)
        self.multi_cell(0, 5.5, text, fill=True)
        self.ln(2)

    def table_header(self, cells, widths):
        self.set_fill_color(*TABLE_HDR)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9)
        h = 7
        for cell_text, w in zip(cells, widths):
            self.cell(w, h, f" {cell_text}", border=1, fill=True)
        self.ln(h)
        self.set_text_color(*DARK_TEXT)

    def table_row(self, cells, widths, fill=False):
        if fill:
            self.set_fill_color(*SECTION_BG)
        else:
            self.set_fill_color(*WHITE)
        self.set_font("Helvetica", "", 8)
        # Calculate max height needed
        line_h = 4.5
        max_lines = 1
        for cell_text, w in zip(cells, widths):
            text_w = w - 2
            n_lines = max(1, len(self.multi_cell(text_w, line_h, cell_text, dry_run=True, output="LINES")))
            max_lines = max(max_lines, n_lines)
        row_h = max_lines * line_h

        x_start = self.get_x()
        y_start = self.get_y()

        for cell_text, w in zip(cells, widths):
            x = self.get_x()
            # Draw cell border and fill
            self.rect(x, y_start, w, row_h, "DF" if fill else "D")
            self.set_xy(x + 1, y_start + 0.5)
            self.multi_cell(w - 2, line_h, cell_text)
            self.set_xy(x + w, y_start)

        self.set_xy(x_start, y_start + row_h)

    def check_space(self, needed_mm=60):
        if self.get_y() > (297 - 25 - needed_mm):
            self.add_page()


def build_pdf():
    pdf = ComparisonPDF()

    # ======================================================================
    # TITLE PAGE
    # ======================================================================
    pdf.add_page()
    pdf.ln(40)

    # Blue accent bar
    pdf.set_fill_color(*MS_BLUE)
    pdf.rect(10, 45, 190, 3, "F")

    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(*MS_BLUE)
    pdf.cell(0, 12, "Why Both Logic Apps Work:", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 10, "demo2 vs demo3 Comparison", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(
        0, 7,
        "Code View vs Designer - Two Roads to the Same Destination",
        align="C",
    )

    pdf.ln(20)
    pdf.set_draw_color(*MS_BLUE)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*DARK_TEXT)
    pdf.cell(0, 8, "Prepared for: Learfield / BrandSafway GHAzDO Demo", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(
        0, 8,
        f"Date: {datetime.now().strftime('%B %d, %Y')}",
        align="C", new_x="LMARGIN", new_y="NEXT",
    )

    pdf.ln(20)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(
        0, 6,
        "This document explains why two Logic Apps built with completely "
        "different methods produce identical results. Written for beginners "
        "with no prior Logic App experience.",
        align="C",
    )

    # ======================================================================
    # SECTION 1: THE BIG PICTURE
    # ======================================================================
    pdf.add_page()
    pdf.section_title("1", "The Big Picture")

    pdf.body_text(
        "Both ghas-ado-sync-demo2 and ghas-ado-sync-demo3 do the EXACT SAME JOB. "
        "They are two Logic Apps running in Azure that automate the same workflow:"
    )

    pdf.numbered_item("1", "Receive a GHAzDO alert webhook from ADO Service Hooks")
    pdf.numbered_item("2", "Extract alert details (type, severity, repo, file, line number)")
    pdf.numbered_item("3", "Check if a work item already exists (deduplication)")
    pdf.numbered_item("4", "If new alert -> Create a work item with tags and priority")
    pdf.numbered_item("5", "If alert resolved -> Close the matching work item with a comment")

    pdf.ln(3)
    pdf.body_text(
        "But they were BUILT differently and their internal JSON looks very different. "
        "demo2 was built by writing JSON by hand in Code View. demo3 was built by "
        "clicking buttons in the Logic App Designer UI."
    )

    pdf.info_box(
        "Analogy: Two Chefs, Same Dish",
        "Think of it like two chefs making the same dish. One writes the recipe by hand "
        "(Code View), the other uses a recipe builder app (Designer). The food tastes "
        "the same, but the recipe cards look different. The oven does not care how the "
        "recipe was written -- it just follows the instructions and produces the same result.",
    )

    pdf.body_text(
        "This document walks through exactly HOW each Logic App was built, what the "
        "JSON differences look like, and WHY those differences do not matter at runtime."
    )

    # ======================================================================
    # SECTION 2: HOW demo2 WAS BUILT -- CODE VIEW
    # ======================================================================
    pdf.add_page()
    pdf.section_title("2", "How demo2 Was Built -- Code View Approach")

    pdf.sub_heading("Method")
    pdf.body_text(
        "We wrote the complete workflow JSON by hand and pasted it into the Logic App's "
        "Code View editor. The source file is ghazdo-to-ado.json (218 lines)."
    )

    pdf.sub_heading("What is Code View?")
    pdf.body_text(
        "In the Azure portal, every Logic App has a 'Code View' button that shows the "
        "raw JSON definition of the workflow. You can edit this JSON directly -- add "
        "actions, change expressions, configure triggers -- all by typing JSON. This is "
        "powerful but requires you to know the Logic App JSON schema."
    )

    pdf.sub_heading("Key Characteristic #1: HTTP Bodies are Native JSON")
    pdf.body_text(
        "When you write JSON by hand, you can put a real JSON object as the HTTP body. "
        "Logic Apps sees this and sends it as-is with the correct Content-Type header."
    )
    pdf.body_text("For the WIQL query (searching for existing work items):")
    pdf.code_block([
        '"body": {',
        '  "query": "SELECT [System.Id] FROM WorkItems',
        '    WHERE [System.Tags] CONTAINS',
        '    \'@{outputs(\'Compose_GhasTag\')}\'',
        '  "',
        '}',
    ])
    pdf.body_text(
        "The body is a REAL JSON object -- curly braces, proper structure. The "
        "@{...} expressions get replaced with actual values at runtime."
    )

    pdf.body_text("For work item creation, the body is a proper JSON array:")
    pdf.code_block([
        '"body": [',
        '  {"op":"add", "path":"/fields/System.Title",',
        '   "value":"@{outputs(\'Compose_Title\')}"},',
        '  {"op":"add", "path":"/fields/System.Description",',
        '   "value":"@{outputs(\'Compose_Description\')}"}',
        ']',
    ])

    pdf.check_space(80)
    pdf.sub_heading("Key Characteristic #2: Parameters for Secrets and Config")
    pdf.body_text(
        "The workflow defines parameters at the top of the JSON. This means "
        "sensitive values and environment-specific settings are not hardcoded:"
    )
    pdf.code_block([
        '"parameters": {',
        '  "adoOrganization": { "type": "String" },',
        '  "adoProject":      { "type": "String" },',
        '  "adoPat":          { "type": "SecureString" },',
        '  "workItemType":    { "type": "String",',
        '                       "defaultValue": "Issue" }',
        '}',
    ])
    pdf.body_text(
        "The PAT (Personal Access Token) is stored as a SecureString parameter. "
        "The org and project are parameterized so you can change them without editing "
        "the workflow. URLs reference these with @{parameters('adoOrganization')} "
        "and @{parameters('adoProject')}."
    )

    pdf.check_space(70)
    pdf.sub_heading("Key Characteristic #3: Dynamic Authorization")
    pdf.body_text(
        "The PAT is Base64-encoded AT RUNTIME using built-in functions:"
    )
    pdf.code_block([
        '"Authorization": "Basic @{base64(concat(\':\',',
        '                   parameters(\'adoPat\')))}"',
    ])
    pdf.body_text(
        "The base64() and concat() functions run when the workflow executes. "
        "This is more secure because the raw PAT is never visible in the JSON -- "
        "it is stored in the SecureString parameter and only encoded when needed."
    )

    pdf.check_space(50)
    pdf.sub_heading("Key Characteristic #4: Inline String Interpolation")
    pdf.body_text(
        "Throughout the JSON, dynamic values are inserted using @{expression} syntax "
        "directly inside string values. This is natural when writing JSON by hand -- "
        "you just put the expression where you want the value to appear. For example:"
    )
    pdf.code_block([
        '"value": "@{outputs(\'Compose_Title\')}"',
        '"uri": "https://dev.azure.com/@{parameters(\'adoOrganization\')}/"',
    ])

    pdf.check_space(40)
    pdf.sub_heading("Action Count and File Size")
    pdf.bold_bullet("Total actions", "17 (9 Compose + 4 HTTP + 4 Conditions)")
    pdf.bold_bullet("File size", "218 lines -- compact and hand-optimized")
    pdf.body_text(
        "Slightly fewer actions because some Compose actions were combined "
        "when writing by hand."
    )

    # ======================================================================
    # SECTION 3: HOW demo3 WAS BUILT -- DESIGNER
    # ======================================================================
    pdf.add_page()
    pdf.section_title("3", "How demo3 Was Built -- Designer Approach")

    pdf.sub_heading("Method")
    pdf.body_text(
        "Every single action was added through the Logic App Designer UI -- clicking "
        "buttons, searching for actions, filling in fields, and typing expressions in "
        "the Expression editor dialog."
    )

    pdf.sub_heading("What is the Designer?")
    pdf.body_text(
        "The Logic App Designer is a visual, drag-and-drop editor in the Azure portal. "
        "You see your workflow as a flowchart. To add an action, you click '+ New step', "
        "search for the action type (like 'HTTP' or 'Compose'), and fill in the fields. "
        "For dynamic values, you click into a field and open the 'Expression' tab to type "
        "a function like outputs('Compose_Title')."
    )

    pdf.sub_heading("Key Characteristic #1: HTTP Bodies Use String Building")
    pdf.body_text(
        "The Designer does not have a 'type raw JSON' option for the HTTP body field. "
        "Instead, you open the Expression editor and build the entire body as a string "
        "using concat(), then wrap it in json() to convert it to a proper JSON object:"
    )
    pdf.code_block([
        "@json(concat(",
        "  '{\"query\": \"SELECT [System.Id]',",
        "  ' FROM WorkItems WHERE [System.Tags]',",
        "  ' CONTAINS ',",
        "  '''', outputs('Compose_GhasTag'), '''',",
        "  '\"}'",
        "))",
    ])
    pdf.body_text(
        "This is MORE VERBOSE but it is the only way when using the Designer's "
        "expression editor. You cannot just type a JSON object directly -- you have to "
        "construct it as a string. The json() function then converts the assembled string "
        "into a proper JSON object before sending."
    )

    pdf.check_space(80)
    pdf.sub_heading("Key Characteristic #2: No Parameters -- Values Hardcoded")
    pdf.body_text(
        "The Designer does not easily expose the Parameters editor. When building via "
        "UI clicks, it is natural to type values directly:"
    )
    pdf.bullet(
        "URLs have the org and project name hardcoded: "
        "concat('https://dev.azure.com/brandsafway1/brandsafway_Engg/_apis/...')"
    )
    pdf.bullet(
        "The PAT is hardcoded as a pre-computed Base64 string"
    )
    pdf.ln(1)
    pdf.body_text(
        "This means if you want to use this workflow in a different project, you would "
        "need to edit every HTTP action. Not ideal for reuse, but fine for a demo."
    )

    pdf.check_space(60)
    pdf.sub_heading("Key Characteristic #3: Static Authorization String")
    pdf.body_text(
        "The Base64 encoding was done BEFORE entering it in the Designer. The full "
        "encoded string is pasted in as a literal value:"
    )
    pdf.code_block([
        '"Authorization": "Basic OkRiYzVOaVND..."',
        "",
        "(The full Base64 string is visible in the workflow JSON)",
    ])
    pdf.body_text(
        "This is less secure (the encoded PAT is visible in the workflow JSON) "
        "but it works. Anyone who can view the workflow can decode the PAT."
    )

    pdf.check_space(60)
    pdf.sub_heading("Key Characteristic #4: Everything Wrapped in concat()")
    pdf.body_text(
        "Even static URIs are wrapped in a concat() call:"
    )
    pdf.code_block([
        "@concat('https://dev.azure.com/brandsafway1/',",
        "  'brandsafway_Engg/_apis/wit/wiql?api-version=7.0')",
    ])
    pdf.body_text(
        "This happens because in the Designer, you enter the URI through the Expression "
        "editor, which always wraps values in a function call. A hand-written JSON would "
        "just have the plain string. The concat() on a single string is unnecessary but "
        "harmless -- it evaluates to the same string."
    )

    pdf.check_space(60)
    pdf.sub_heading("Key Characteristic #5: More Compose Actions")
    pdf.bold_bullet("Total actions", "20 (13 Compose + 4 HTTP + 3 Conditions)")
    pdf.body_text(
        "More Compose actions because each field is extracted individually. The "
        "Designer encourages a 'one action per field' pattern, which actually makes "
        "it easier to debug -- you can click each action and see its output value."
    )

    pdf.check_space(40)
    pdf.sub_heading("Key Characteristic #6: Auto-Generated Metadata")
    pdf.body_text(
        "The Designer adds extra metadata that you would not add by hand:"
    )
    pdf.code_block([
        '"runtimeConfiguration": {',
        '  "contentTransfer": {',
        '    "transferMode": "Chunked"',
        '  }',
        '}',
    ])
    pdf.body_text(
        "These do not change behavior but make the JSON larger. They are just "
        "default values the Designer inserts automatically."
    )

    # ======================================================================
    # SECTION 4: SIDE-BY-SIDE COMPARISON TABLE
    # ======================================================================
    pdf.add_page()
    pdf.section_title("4", "Side-by-Side Comparison Table")

    pdf.body_text(
        "The following table summarizes every major difference between the two "
        "Logic Apps. Despite all these differences, the end result is identical."
    )
    pdf.ln(2)

    col_widths = [38, 62, 62]
    # Use a simpler approach: draw the table with multi_cell rows

    rows = [
        ("How it was built",
         "Wrote JSON by hand, pasted into Code View",
         "Clicked buttons in Logic App Designer UI"),
        ("Total actions",
         "17",
         "20"),
        ("Compose actions",
         "9",
         "13"),
        ("HTTP body format",
         "Native JSON objects/arrays with @{...} interpolation",
         "String concat() wrapped in json()"),
        ("Parameters",
         "4 (adoOrg, adoProject, adoPat, workItemType)",
         "None (all hardcoded)"),
        ("PAT handling",
         "SecureString param, Base64 encoded at runtime",
         "Pre-computed Base64 string, hardcoded"),
        ("URI format",
         "Plain string with @{parameters(...)}",
         "Wrapped in @concat() even for static values"),
        ("Portability",
         "High -- change params for any org/project",
         "Low -- must edit every HTTP action"),
        ("Security",
         "Better -- PAT in SecureString parameter",
         "Weaker -- PAT visible in workflow JSON"),
        ("Readability",
         "Requires JSON knowledge",
         "Visual -- can see flow in Designer canvas"),
        ("Debugging",
         "Need to read JSON to find issues",
         "Click actions in Designer to inspect"),
        ("File size",
         "218 lines (compact)",
         "~350+ lines (verbose with metadata)"),
        ("Extra metadata",
         "Minimal",
         "runtimeConfiguration, contentTransfer, etc."),
        ("Webhook host",
         "prod-33.eastus.logic.azure.com",
         "prod-74.eastus.logic.azure.com"),
        ("Service Hooks",
         "Hooks 1-2 (prod-33)",
         "Hooks 3-4 (prod-74)"),
    ]

    # Table header
    pdf.table_header(["Aspect", "demo2 (Code View)", "demo3 (Designer)"], col_widths)

    for i, (aspect, demo2, demo3) in enumerate(rows):
        pdf.check_space(20)
        pdf.table_row([aspect, demo2, demo3], col_widths, fill=(i % 2 == 0))

    # ======================================================================
    # SECTION 5: WHY BOTH WORK
    # ======================================================================
    pdf.add_page()
    pdf.section_title("5", "Why Both Work Despite the Differences")

    pdf.info_box(
        "Key Insight",
        "The Logic App runtime does not care HOW you built the workflow. It reads "
        "the JSON definition, evaluates all expressions, and executes the actions. "
        "The result is identical regardless of whether you typed JSON by hand or "
        "clicked buttons in the Designer.",
    )

    pdf.sub_heading("Reason 1: Same Trigger, Same Input")
    pdf.body_text(
        "Both Logic Apps receive the exact same JSON payload from ADO Service Hooks. "
        "The webhook URL is different (prod-33 vs prod-74) but the payload format is "
        "identical. ADO sends the same alert data to both."
    )

    pdf.sub_heading("Reason 2: String concat + json() = Native JSON Object")
    pdf.body_text("When demo3 does this:")
    pdf.code_block([
        '@json(concat(\'{"key":"value"}\'))',
    ])
    pdf.body_text(
        "The json() function parses the string into a proper JSON object. The result "
        "is IDENTICAL to demo2's native JSON:"
    )
    pdf.code_block([
        '{"key": "value"}',
    ])
    pdf.body_text(
        "The ADO API receives the exact same HTTP request body from both Logic Apps. "
        "The json() function is like a translator -- it converts a text string into "
        "a structured JSON object, which is what the API expects."
    )

    pdf.sub_heading("Reason 3: Hardcoded PAT = Parameterized PAT (at Runtime)")
    pdf.body_text(
        "In demo2, the expression @{base64(concat(':', parameters('adoPat')))} evaluates "
        "to a Base64 string like 'OkRiYzVOaVNC...' at runtime."
    )
    pdf.body_text(
        "In demo3, 'Basic OkRiYzVOaVNC...' is already that exact value."
    )
    pdf.body_text(
        "Both send the exact same Authorization header to ADO. The API does not know "
        "or care whether the value was computed at runtime or pasted in ahead of time."
    )

    pdf.check_space(60)
    pdf.sub_heading("Reason 4: @concat() on a Static String = The String Itself")
    pdf.code_block([
        "@concat('https://dev.azure.com/...')",
        "  evaluates to -->",
        "'https://dev.azure.com/...'",
    ])
    pdf.body_text(
        "Wrapping a single string in concat() is a no-op -- it does nothing. It is just "
        "unnecessary verbosity from the Designer. The final URL is identical."
    )

    pdf.sub_heading("Reason 5: More Compose Actions Do Not Change the Result")
    pdf.body_text(
        "demo3 has 13 Compose actions vs demo2's 9, but the final computed values "
        "(Title, Tags, Description, GhasTag) are the same. demo3 just does more "
        "granular extraction -- extracting each field into its own step."
    )
    pdf.body_text(
        "This actually makes demo3 EASIER to debug because you can click each Compose "
        "action in the Designer and see its output. In demo2, some values are computed "
        "inline and you cannot inspect intermediate results as easily."
    )

    pdf.check_space(40)
    pdf.sub_heading("Reason 6: Extra Metadata is Ignored")
    pdf.body_text(
        "Things like runtimeConfiguration.contentTransfer.transferMode: 'Chunked' are "
        "defaults that do not affect behavior. The Designer adds them automatically, "
        "but they are just informational. The Logic App runtime uses the same defaults "
        "whether or not these properties are present in the JSON."
    )

    # ======================================================================
    # SECTION 6: WHEN TO USE WHICH APPROACH
    # ======================================================================
    pdf.add_page()
    pdf.section_title("6", "When to Use Which Approach")

    pdf.sub_heading("Use Code View (like demo2) when:")
    pdf.bullet("You need maximum portability (parameters for org, project, PAT)")
    pdf.bullet("You are deploying via Infrastructure-as-Code (ARM/Bicep templates)")
    pdf.bullet("You want the most compact, readable JSON")
    pdf.bullet("Security is a priority (SecureString parameters)")
    pdf.bullet("You are comfortable writing JSON")
    pdf.bullet("You want to version-control the workflow and diff changes")

    pdf.ln(3)
    pdf.sub_heading("Use Designer (like demo3) when:")
    pdf.bullet("You are showing a customer how to build it themselves")
    pdf.bullet("The audience is non-technical or new to Logic Apps")
    pdf.bullet("You want a visual, clickable representation")
    pdf.bullet("You need to debug by clicking through each action")
    pdf.bullet("You are prototyping and iterating quickly")
    pdf.bullet("You do not need to deploy to multiple environments")

    pdf.ln(3)
    pdf.sub_heading("Best Practice for Production")
    pdf.body_text(
        "Start with the Designer to prototype, then export the JSON and clean it up. "
        "Here is the recommended workflow:"
    )
    pdf.numbered_item("1", "Build in Designer (like demo3) to get the logic right")
    pdf.numbered_item("2", "Export to Code View")
    pdf.numbered_item("3", "Replace hardcoded values with parameters")
    pdf.numbered_item("4", "Replace concat() wrappers on static strings with plain strings")
    pdf.numbered_item("5", "Replace json(concat(...)) body patterns with native JSON objects")
    pdf.numbered_item("6", "Store PAT as SecureString parameter")
    pdf.numbered_item("7", "Version control the cleaned-up JSON (like demo2)")

    pdf.info_box(
        "Bottom Line",
        "demo3 (Designer) is the starting point for rapid development. "
        "demo2 (Code View) is the end goal for production-ready, secure, "
        "portable workflows. Both are valid -- they are just different stages "
        "of the same development lifecycle.",
    )

    # ======================================================================
    # SECTION 7: ARCHITECTURE DIAGRAM
    # ======================================================================
    pdf.add_page()
    pdf.section_title("7", "Quick Reference -- Architecture Diagram")

    pdf.body_text(
        "The following diagram shows how both Logic Apps fit into the overall "
        "GHAzDO-to-ADO-Work-Items architecture:"
    )
    pdf.ln(2)

    pdf.code_block([
        "ADO Repo (brandsafway_Engg)",
        "    |",
        "    v",
        "GHAzDO Scanner",
        "  (detects secrets, code vulnerabilities,",
        "   dependency issues)",
        "    |",
        "    v",
        "ADO Service Hooks (4 total)",
        "    |",
        "    +---> Hook 1,2 (alert created + state changed)",
        "    |         |",
        "    |         v",
        "    |     ghas-ado-sync-demo2 (prod-33)",
        "    |     [Code View built]",
        "    |         |",
        "    |         v",
        "    |     ADO Work Items API",
        "    |       --> Creates/Closes Work Items",
        "    |",
        "    +---> Hook 3,4 (alert created + state changed)",
        "              |",
        "              v",
        "          ghas-ado-sync-demo3 (prod-74)",
        "          [Designer built]",
        "              |",
        "              v",
        "          ADO Work Items API",
        "            --> Creates/Closes Work Items",
    ])

    pdf.ln(2)
    pdf.body_text(
        "Both Logic Apps hit the SAME ADO Work Items API, creating items in the SAME "
        "project board. If both hooks fire for the same alert, the deduplication check "
        "(WIQL query by GhasTag) prevents duplicate work items."
    )

    pdf.info_box(
        "Deduplication Explained",
        "Before creating a new work item, both Logic Apps run a WIQL query that "
        "searches for existing work items with a matching GhasTag. The GhasTag is a "
        "unique identifier for each alert (e.g., 'GHAzDO-secret-123'). If a match is "
        "found, the Logic App skips creation. This is why you can safely have both "
        "demo2 and demo3 running -- they will not create duplicate work items for the "
        "same alert.",
    )

    pdf.ln(5)
    pdf.set_draw_color(*MS_BLUE)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(
        0, 6,
        "End of document. For questions or updates, refer to the Logic App "
        "workflow JSON files: ghazdo-to-ado.json (demo2) and the demo3 workflow "
        "definition in the Azure portal.",
        align="C",
    )

    # -- Save ---------------------------------------------------------------
    os.makedirs(os.path.dirname(OUTPUT_PDF), exist_ok=True)
    pdf.output(OUTPUT_PDF)
    print(f"[OK] PDF saved to: {OUTPUT_PDF}")
    print(f"     Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()
