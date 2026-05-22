#!/usr/bin/env python3
"""
Generate the GHAzDO-to-ADO Customization Guide PDF.
Covers: custom fields, custom work item types, inherited process templates,
custom states, priority mapping, tags, team assignment, and more.
"""

import os
import sys
from fpdf import FPDF

# -- Paths ------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
OUTPUT_PDF = os.path.join(DOCS_DIR, "GHAzDO-Customization-Guide.pdf")

# -- Colors -----------------------------------------------------------------
MS_BLUE = (0, 120, 212)
DARK_TEXT = (33, 33, 33)
WHITE = (255, 255, 255)
LIGHT_GRAY = (245, 245, 245)
MED_GRAY = (200, 200, 200)
SECTION_BG = (230, 242, 255)
CODE_BG = (240, 240, 240)
WARN_RED = (200, 0, 0)
WARN_BG = (255, 243, 224)
WARN_BORDER = (230, 126, 34)
TIP_GREEN = (0, 128, 64)
TIP_BG = (232, 245, 233)
PURPLE = (102, 51, 153)


def safe(text):
    """Replace common Unicode characters with ASCII equivalents."""
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


class CustomizationPDF(FPDF):
    """PDF class for the Customization Guide."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() <= 1:
            return
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*MS_BLUE)
        self.cell(95, 8, safe("GHAzDO-to-ADO | Customization Guide"), align="L")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(95, 8, safe("Confidential - Customer Guide"), align="R")
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
        self.cell(95, 10, safe("GHAzDO-to-ADO | Customization Guide"), align="L")
        self.cell(95, 10, safe(f"Page {self.page_no()}"), align="R")

    # -- Helpers ------------------------------------------------------------
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

    def table_row(self, cells, widths, bold=False, fill=False, highlight=False):
        style = "B" if bold else ""
        if highlight:
            self.set_fill_color(255, 255, 200)  # bright yellow highlight
        elif fill:
            self.set_fill_color(*SECTION_BG)
        do_fill = fill or highlight
        self.set_font("Helvetica", style, 9)
        h = 7
        for i, (cell_text, w) in enumerate(zip(cells, widths)):
            if highlight and i == 0:
                # Prepend NEW tag to first cell
                self.set_font("Helvetica", "B", 8)
                self.set_text_color(200, 0, 0)
                tag_w = self.get_string_width(" NEW ") + 2
                self.cell(tag_w, h, safe(" NEW"), border="LTB", fill=do_fill)
                self.set_font("Helvetica", style, 9)
                self.set_text_color(*DARK_TEXT)
                self.cell(w - tag_w, h, safe(f" {cell_text}"), border="RTB", fill=do_fill)
            else:
                self.set_text_color(*DARK_TEXT)
                self.cell(w, h, safe(f" {cell_text}"), border=1, fill=do_fill)
        self.ln(h)
        if highlight:
            self.set_fill_color(*SECTION_BG)

    def code_line_highlight(self, line, font_size=8):
        """Render a single highlighted code line (yellow bg, bold)."""
        self.set_fill_color(255, 255, 180)
        self.set_font("Courier", "B", font_size)
        self.set_text_color(0, 90, 180)
        s = safe(line.replace("\t", "    "))
        self.cell(0, 4.5, f">> {s}", fill=True,
                  new_x="LMARGIN", new_y="NEXT")
        self.set_fill_color(*CODE_BG)
        self.set_font("Courier", "", font_size)
        self.set_text_color(*DARK_TEXT)

    def code_block_mixed(self, lines, highlights=None, font_size=8):
        """Code block where specific line indices are highlighted."""
        if highlights is None:
            highlights = set()
        self.ln(1)
        for i, line in enumerate(lines):
            if i in highlights:
                self.code_line_highlight(line, font_size)
            else:
                self.set_fill_color(*CODE_BG)
                self.set_font("Courier", "", font_size)
                self.set_text_color(*DARK_TEXT)
                s = safe(line.replace("\t", "    "))
                self.cell(0, 4.5, f"  {s}", fill=True,
                          new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def new_tag(self):
        """Inline NEW tag in red."""
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(255, 255, 255)
        self.set_fill_color(200, 0, 0)
        self.cell(12, 5, " NEW", fill=True)
        self.set_text_color(*DARK_TEXT)
        self.set_fill_color(*SECTION_BG)
        self.cell(3, 5, " ")

    def blue_banner(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(*MS_BLUE)
        self.set_text_color(*WHITE)
        self.cell(0, 7, safe(f"  {text}"), fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*DARK_TEXT)
        self.ln(2)

    def green_banner(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(*TIP_GREEN)
        self.set_text_color(*WHITE)
        self.cell(0, 7, safe(f"  {text}"), fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*DARK_TEXT)
        self.set_fill_color(*TIP_BG)
        self.ln(2)

    def purple_banner(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(*PURPLE)
        self.set_text_color(*WHITE)
        self.cell(0, 7, safe(f"  {text}"), fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*DARK_TEXT)
        self.ln(2)

    def flow_diagram(self, title, boxes, arrow_label=""):
        """Draw a horizontal flow diagram with boxes connected by arrows.

        boxes: list of (header, body_lines) tuples.
        Each box is drawn as a rounded-ish rectangle with a colored header.
        """
        self.ln(4)
        if self.get_y() > 200:
            self.add_page()
        # Title
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*MS_BLUE)
        self.cell(0, 7, safe(title), new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*DARK_TEXT)
        self.ln(2)

        num = len(boxes)
        page_w = self.w - self.l_margin - self.r_margin
        gap = 8  # space between boxes for arrow
        box_w = (page_w - gap * (num - 1)) / num
        box_h = 40
        start_x = self.l_margin
        start_y = self.get_y()

        colors = [
            (0, 120, 212),    # blue
            (0, 128, 64),     # green
            (200, 100, 0),    # orange
            (102, 51, 153),   # purple
        ]

        for i, (header, body_lines) in enumerate(boxes):
            x = start_x + i * (box_w + gap)
            y = start_y
            c = colors[i % len(colors)]

            # Box outline
            self.set_draw_color(*c)
            self.set_line_width(0.8)
            self.rect(x, y, box_w, box_h, "D")

            # Header bar
            self.set_fill_color(*c)
            self.rect(x, y, box_w, 8, "F")
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*WHITE)
            self.set_xy(x + 1, y + 1)
            self.cell(box_w - 2, 6, safe(header), align="C")

            # Body lines
            self.set_font("Helvetica", "", 7)
            self.set_text_color(*DARK_TEXT)
            line_y = y + 10
            for line in body_lines:
                self.set_xy(x + 2, line_y)
                self.cell(box_w - 4, 4, safe(line), align="L")
                line_y += 4

            # Arrow to next box
            if i < num - 1:
                arrow_x = x + box_w + 1
                arrow_y = start_y + box_h / 2
                self.set_draw_color(*MED_GRAY)
                self.set_line_width(0.6)
                self.line(arrow_x, arrow_y, arrow_x + gap - 2, arrow_y)
                # arrowhead
                self.line(arrow_x + gap - 4, arrow_y - 2,
                          arrow_x + gap - 2, arrow_y)
                self.line(arrow_x + gap - 4, arrow_y + 2,
                          arrow_x + gap - 2, arrow_y)

        self.set_draw_color(*MED_GRAY)
        self.set_line_width(0.2)
        self.set_y(start_y + box_h + 4)
        self.ln(2)


# ===========================================================================
# BUILD THE PDF
# ===========================================================================
def build_pdf():
    pdf = CustomizationPDF()

    # ===== TITLE PAGE ======================================================
    pdf.add_page()
    pdf.set_fill_color(*MS_BLUE)
    pdf.rect(0, 0, 210, 110, "F")

    pdf.set_y(20)
    pdf.set_font("Helvetica", "B", 30)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 14, safe("GHAzDO-to-ADO"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 12, safe("Customization Guide"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 8, safe("Custom Fields, Work Item Types,"), align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, safe("Inherited Processes & Advanced Configuration"), align="C",
             new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(120)
    pdf.set_text_color(*DARK_TEXT)
    pdf.set_font("Helvetica", "", 11)

    info = [
        ("Document Type", "Customer Customization Guide"),
        ("Audience", "DevSecOps Engineers, ADO Administrators, Security Teams"),
        ("JSON File", "ghazdo-to-ado.json (218 lines, 4 parameters)"),
        ("Prerequisites", "E2E Setup Guide completed, Logic App deployed"),
        ("Date", "March 2026"),
        ("Classification", "Customer-Facing"),
    ]
    for label, val in info:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(50, 8, safe(f"  {label}:"))
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, safe(val), new_x="LMARGIN", new_y="NEXT")

    # ===== TABLE OF CONTENTS ===============================================
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*MS_BLUE)
    pdf.cell(0, 12, safe("Table of Contents"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(5)

    toc = [
        ("1", "Where to Customize in the JSON", "3"),
        ("2", "Built-in ADO Fields Catalog", "4"),
        ("3", "Creating Custom Fields in ADO (Step-by-Step)", "7"),
        ("4", "Recommended Custom Fields for Security Teams", "9"),
        ("5", "Complete JSON Example with Custom Fields", "10"),
        ("6", "Why the Work Item Has So Many Fields", "12"),
        ("7", "Understanding the Tags System", "13"),
        ("8", "Creating an Inherited Process Template", "15"),
        ("9", "Adding Custom Work Item Types", "19"),
        ("  9a", "  Type: SecurityAlert (with fields & states)", "19"),
        ("  9b", "  Type: Vulnerability", "21"),
        ("  9c", "  Type: ComplianceFinding", "22"),
        ("10", "Assigning the Process to Your Project", "24"),
        ("11", "Using Custom Types with the Logic App", "25"),
        ("12", "Multiple Logic Apps for Different Alert Types", "26"),
        ("13", "Changing Priority Mapping", "27"),
        ("14", "Auto-Assigning to Team Members", "28"),
        ("15", "Changing Work Item Type", "29"),
        ("16", "Quick Reference: What to Change Where", "30"),
    ]
    w_toc = [15, 140, 20]
    pdf.table_row(["Section", "Topic", "Page"], w_toc, bold=True, fill=True)
    for num, topic, pg in toc:
        pdf.table_row([num, topic, pg], w_toc)

    # ===== SECTION 1: WHERE TO CUSTOMIZE ===================================
    pdf.section_title("1", "Where to Customize in the JSON")

    pdf.body(
        'Open ghazdo-to-ado.json in any text editor (VS Code, Notepad++, etc). '
        'The section you need to modify is the "HTTP_CreateWorkItem" action '
        '(around line 144-161).'
    )

    pdf.blue_banner("What is this JSON doing?")

    pdf.body(
        "When a GHAzDO alert fires, the Logic App creates a Work Item in ADO. "
        "To create the Work Item, the Logic App sends a list of fields and values "
        "to the ADO REST API. This list is called the BODY array."
    )

    pdf.body(
        'The body is a JSON array (starts with [ and ends with ]). '
        'Inside the array, each { ... } block sets ONE field on the Work Item. '
        'Think of it like a form: each block fills in one form field.'
    )

    pdf.blue_banner("The DEFAULT body (already in the JSON -- DO NOT REMOVE)")

    pdf.body(
        "The JSON file you received (ghazdo-to-ado.json) already has 4 fields "
        "pre-configured. These are the MINIMUM required fields. "
        "DO NOT delete or change these unless you know what you are doing."
    )

    pdf.code_block_mixed([
        '"body": [                               <-- Array starts here',
        '',
        '  {                                     <-- FIELD 1: Work Item Title',
        '    "op": "add",                            (always "add")',
        '    "path": "/fields/System.Title",          (which field to fill)',
        '    "value": "@{outputs(\'Compose_Title\')}"   (auto-filled from alert)',
        '  },                                    <-- comma separates entries',
        '',
        '  {                                     <-- FIELD 2: Description',
        '    "op": "add",',
        '    "path": "/fields/System.Description",',
        '    "value": "@{outputs(\'Compose_Description\')}"',
        '  },',
        '',
        '  {                                     <-- FIELD 3: Tags',
        '    "op": "add",',
        '    "path": "/fields/System.Tags",',
        '    "value": "@{outputs(\'Compose_Tags\')}"',
        '  },',
        '',
        '  {                                     <-- FIELD 4: Priority',
        '    "op": "add",',
        '    "path": "/fields/Microsoft.VSTS.Common.Priority",',
        '    "value": "@if(...severity mapping...)"',
        '  }                                     <-- last item: NO comma',
        '',
        ']                                       <-- Array ends here',
    ], highlights={0, 3, 4, 5, 26})

    pdf.warning_box(
        "DO NOT REMOVE these 4 existing entries! They are required for the Logic App "
        "to create valid Work Items. You are only ADDING new entries to this array."
    )

    pdf.blue_banner("How to ADD a new field (step by step)")

    pdf.body(
        "To add a new field, you insert a new { ... } block into the body array. "
        "Here is exactly what to do:"
    )

    pdf.numbered_step(1,
        "Open ghazdo-to-ado.json in a text editor"
    )
    pdf.numbered_step(2,
        'Find the body array (search for "body": [). It is inside the '
        "HTTP_CreateWorkItem action, around line 144."
    )
    pdf.numbered_step(3,
        "Go to the LAST entry in the array (the Priority field). "
        "Add a COMMA after its closing brace }."
    )
    pdf.numbered_step(4,
        "Paste your new field block after the comma. "
        "Each block has exactly 3 parts (see below)."
    )
    pdf.numbered_step(5,
        "Save the file. Paste the updated JSON into the Logic App Code View."
    )

    pdf.blue_banner("The 3 parts of every field entry")

    pdf.body("Every { ... } block you add has exactly 3 lines:")

    pdf.code_block_mixed([
        '{',
        '  "op": "add",                  <-- ALWAYS "add" (never change this)',
        '  "path": "/fields/FIELD.NAME", <-- The ADO field (from Section 2 or 3)',
        '  "value": "YOUR VALUE"         <-- What to put in that field',
        '}',
    ], highlights={1, 2, 3})

    pdf.numbered_step(1,
        '"op": "add" -- This is ALWAYS "add". It tells ADO to set a field value. '
        "You never change this line."
    )
    pdf.numbered_step(2,
        '"path": "/fields/FIELD.NAME" -- Replace FIELD.NAME with the ADO field '
        "reference name. Section 2 lists all built-in fields. Section 3 shows how "
        "to create custom fields (Custom.YourFieldName)."
    )
    pdf.numbered_step(3,
        '"value": "..." -- The value to put in the field. This can be:\n'
        '   - STATIC text you write (e.g. "GHAzDO", "High", "Security Team")\n'
        "   - DYNAMIC expression that auto-fills from the alert (e.g. @{outputs('Compose_Title')})\n"
        "   - A MIX of both (e.g. \"Found by GHAzDO on @{utcNow()}\")"
    )

    pdf.blue_banner("BEFORE and AFTER Example")

    pdf.body(
        "Here is a real example. Say you want to add an AssignedTo field "
        "so all security alerts go to 'security-team@company.com'."
    )

    pdf.sub_heading("BEFORE (original -- 4 fields, DO NOT TOUCH these):")
    pdf.code_block_mixed([
        '"body": [',
        '  { "op": "add", "path": "/fields/System.Title",',
        '    "value": "@{outputs(\'Compose_Title\')}" },',
        '  { "op": "add", "path": "/fields/System.Description",',
        '    "value": "@{outputs(\'Compose_Description\')}" },',
        '  { "op": "add", "path": "/fields/System.Tags",',
        '    "value": "@{outputs(\'Compose_Tags\')}" },',
        '  { "op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority",',
        '    "value": "@if(...severity mapping...)" }  <-- you will add comma HERE',
        ']',
    ], highlights={8})

    pdf.sub_heading("AFTER (you added 1 new field -- now 5 fields):")
    pdf.code_block_mixed([
        '"body": [',
        '  { "op": "add", "path": "/fields/System.Title",',
        '    "value": "@{outputs(\'Compose_Title\')}" },',
        '  { "op": "add", "path": "/fields/System.Description",',
        '    "value": "@{outputs(\'Compose_Description\')}" },',
        '  { "op": "add", "path": "/fields/System.Tags",',
        '    "value": "@{outputs(\'Compose_Tags\')}" },',
        '  { "op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority",',
        '    "value": "@if(...severity mapping...)" },  <-- ADDED comma here!',
        '',
        '  { "op": "add",                               <-- NEW ENTRY',
        '    "path": "/fields/System.AssignedTo",        <-- field name',
        '    "value": "security-team@company.com" }      <-- your value',
        ']',
    ], highlights={8, 10, 11, 12})

    pdf.warning_box(
        "IMPORTANT: Notice the comma on line 9! The entry BEFORE your new one "
        "must end with },  (brace + comma). The LAST entry in the array must NOT "
        "have a comma. If you forget the comma, you will get a JSON parse error."
    )

    pdf.tip_box(
        "You can add as many new fields as you want. Just keep adding { ... } blocks "
        "to the array. Each new block = one more field on the Work Item. "
        "See Section 2 for all available built-in field names."
    )

    # ===== SECTION 2: BUILT-IN FIELDS CATALOG ==============================
    pdf.section_title("2", "Built-in ADO Fields Catalog")

    pdf.body(
        "These fields already exist in every ADO project -- you do NOT need to create "
        "them. Just add the JSON Patch entry and they will work immediately."
    )

    pdf.body(
        "LEGEND: Rows highlighted in YELLOW with a NEW tag are fields you can ADD "
        "to the JSON. Non-highlighted rows are either already in the default JSON "
        "or are auto-managed by ADO."
    )

    pdf.blue_banner("Assignment & Ownership Fields")

    w_field = [80, 110]
    pdf.table_row(["Field Path", "What It Does"], w_field, bold=True, fill=True)
    pdf.table_row(["/fields/System.AssignedTo", "Assign to a person (email or display name)"], w_field, highlight=True)
    pdf.table_row(["/fields/System.AreaPath", "Route to a team area (e.g., Project\\Security)"], w_field, highlight=True)
    pdf.table_row(["/fields/System.IterationPath", "Assign to a sprint (e.g., Project\\Sprint 5)"], w_field, highlight=True)
    pdf.table_row(["/fields/System.CreatedBy", "Override creator (usually auto-set by ADO)"], w_field)
    pdf.table_row(["/fields/System.ChangedBy", "Override last changed by (usually auto-set)"], w_field)

    pdf.blue_banner("Classification & Tracking Fields")

    pdf.table_row(["Field Path", "What It Does"], w_field, bold=True, fill=True)
    pdf.table_row(["/fields/System.State", "Set initial state (To Do, Active, etc.)"], w_field, highlight=True)
    pdf.table_row(["/fields/System.Reason", "Reason for the current state"], w_field, highlight=True)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.Priority", "Priority: 1-Critical to 4-Low (ALREADY IN JSON)"], w_field)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.Severity", "Severity: 1-Critical to 4-Low"], w_field, highlight=True)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.ValueArea", "Business or Architectural"], w_field, highlight=True)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.Risk", "Risk level: 1-High, 2-Medium, 3-Low"], w_field, highlight=True)
    pdf.table_row(["/fields/System.Tags", "Semicolon-separated tags (ALREADY IN JSON)"], w_field)
    pdf.table_row(["/fields/System.BoardColumn", "Kanban board column name"], w_field, highlight=True)

    pdf.blue_banner("Planning & Effort Fields")

    pdf.table_row(["Field Path", "What It Does"], w_field, bold=True, fill=True)
    pdf.table_row(["/fields/Microsoft.VSTS.Scheduling.Effort", "Story points or effort estimate"], w_field, highlight=True)
    pdf.table_row(["/fields/Microsoft.VSTS.Scheduling.StoryPoints", "Story points (Agile template)"], w_field, highlight=True)
    pdf.table_row(["/fields/Microsoft.VSTS.Scheduling.OriginalEstimate", "Original time estimate (hours)"], w_field, highlight=True)
    pdf.table_row(["/fields/Microsoft.VSTS.Scheduling.RemainingWork", "Remaining work (hours)"], w_field, highlight=True)
    pdf.table_row(["/fields/Microsoft.VSTS.Scheduling.CompletedWork", "Completed work (hours)"], w_field, highlight=True)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.Activity", "Activity type (Development, Testing)"], w_field, highlight=True)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.StackRank", "Stack rank for backlog ordering"], w_field, highlight=True)

    pdf.blue_banner("Description & History Fields")

    pdf.table_row(["Field Path", "What It Does"], w_field, bold=True, fill=True)
    pdf.table_row(["/fields/System.Description", "Rich text description (ALREADY IN JSON)"], w_field)
    pdf.table_row(["/fields/System.History", "Add a discussion comment entry"], w_field, highlight=True)
    pdf.table_row(["/fields/Microsoft.VSTS.TCM.ReproSteps", "Repro steps (Bug work items only)"], w_field, highlight=True)
    pdf.table_row(["/fields/Microsoft.VSTS.Common.AcceptanceCriteria", "Acceptance criteria text"], w_field, highlight=True)

    # --- HOW TO ADD the NEW fields (bridge the gap) ---
    pdf.blue_banner("How to Add These NEW Fields to the JSON")

    pdf.body(
        "Each NEW field above needs a JSON Patch entry in the Logic App workflow. "
        "Below are copy-paste examples for each one. Add these entries to the BODY array "
        "of the HTTP_CreateWorkItem action in your Logic App JSON."
    )

    pdf.warning_box(
        'UNDERSTANDING THE "value" FIELD: Each entry below has a "value" that can contain '
        "two types of content:\n"
        "1) STATIC TEXT -- text you type yourself (e.g. 'GHAzDO'). Same every time.\n"
        "2) DYNAMIC EXPRESSIONS -- text inside @{...} curly braces. These are "
        "AUTOMATICALLY PULLED from the data ADO sends in the webhook. "
        "You do NOT hardcode these values. The Logic App reads the incoming "
        "webhook payload and extracts the real values at runtime."
    )

    pdf.blue_banner("How Dynamic Values Work (You Do NOT Hardcode Them)")

    pdf.body(
        "When ADO detects a security alert, it sends a webhook payload containing "
        "all the alert details (alert type, severity, repo name, file path, etc). "
        "The Logic App receives this payload and extracts each piece of data using "
        "Compose actions. The @{...} expressions reference those extracted values."
    )

    pdf.body(
        "In other words: you do NOT type 'secret' or 'critical' or 'my-repo' into "
        "the JSON. Instead, the @{...} expression tells the Logic App: "
        "'Go get the REAL value from whatever ADO just sent me.' Each time a "
        "different alert fires, the values are different -- automatically."
    )

    pdf.body("Here is how the data flows:")
    pdf.code_block_mixed([
        "ADO sends webhook  -->  Logic App receives payload  -->  Compose actions extract fields",
        "",
        "Example: ADO sends:   { 'alertType': 'secret', 'severity': 'critical' }",
        "  Compose_AlertType extracts 'secret'",
        "  Compose_Severity extracts 'critical'",
        "",
        "In your JSON, @{body('Compose_AlertType')} becomes 'secret'",
        "In your JSON, @{body('Compose_Severity')} becomes 'critical'",
        "",
        "Next time, ADO sends: { 'alertType': 'dependency', 'severity': 'high' }",
        "  Same expressions now become 'dependency' and 'high' -- automatically!",
    ], highlights={2, 6, 7, 9, 10})

    pdf.body("Available dynamic expressions (each one pulls a REAL value from ADO):")
    w_dyn = [75, 115]
    pdf.table_row(["Expression", "What ADO Sends (auto-filled, NOT hardcoded)"],
                  w_dyn, bold=True, fill=True)
    pdf.table_row(
        ["@{body('Compose_AlertType')}",
         "The alert category: 'secret', 'code', or 'dependency' -- from ADO payload"],
        w_dyn)
    pdf.table_row(
        ["@{body('Compose_Severity')}",
         "The severity: 'critical', 'high', 'medium', 'low' -- from ADO payload"],
        w_dyn)
    pdf.table_row(
        ["@{body('Compose_File')}",
         "The file path where issue was found (e.g. 'src/config.env') -- from ADO"],
        w_dyn)
    pdf.table_row(
        ["@{body('Compose_RepoName')}",
         "The repository name -- pulled from what ADO sends"],
        w_dyn)
    pdf.table_row(
        ["@{body('Compose_AlertId')}",
         "The unique alert ID number -- from ADO payload"],
        w_dyn)
    pdf.table_row(
        ["@{utcNow()}",
         "Current date/time when Logic App runs -- auto-generated, not from ADO"],
        w_dyn)

    pdf.tip_box(
        "KEY TAKEAWAY: You never hardcode alert data. The @{...} expressions pull "
        "the real values from whatever ADO sends. If ADO sends 'critical', that is "
        "what goes into the Work Item. If ADO sends 'low', that is what goes in. "
        "You only hardcode LABELS (like 'Alert Type:') and FIXED values (like 'GHAzDO')."
    )

    pdf.sub_heading("Adding System.History (Discussion Comment)")
    pdf.body(
        "This adds a comment in the Work Item's Discussion tab when it is created."
    )

    pdf.body("YOUR RESPONSIBILITY:")
    pdf.bullet(
        "You can CHANGE the static text part to say anything you want. For example, "
        'change "Auto-created by GHAzDO Logic App" to "Security alert detected by scanner".'
    )
    pdf.bullet(
        "The @{utcNow()} part is a DYNAMIC expression -- the Logic App automatically "
        "fills in the current date/time when it runs. You do NOT type a date here. "
        "Leave @{utcNow()} as-is and it will always show the real timestamp."
    )
    pdf.bullet(
        "ACTION: Copy-paste the block below. Edit the quoted text if you want a different "
        "message. Leave @{utcNow()} untouched -- it is auto-generated."
    )

    pdf.code_block_mixed([
        '// Add this entry to the body array in HTTP_CreateWorkItem:',
        '{',
        '  "op": "add",',
        '  "path": "/fields/System.History",',
        '  "value": "Auto-created by GHAzDO Logic App on @{utcNow()}"',
        '}',
        '',
        '// BREAKDOWN:',
        '//   "Auto-created by GHAzDO Logic App on "  <-- YOUR text (change freely)',
        '//   @{utcNow()}                             <-- AUTO-GENERATED timestamp',
        '//                                              (not hardcoded, not from ADO)',
    ], highlights={3, 4})

    pdf.sub_heading("Adding ReproSteps (Bug Work Items)")
    pdf.body(
        "If you use Bug as your work item type, this populates the Repro Steps tab. "
        "This field supports HTML formatting (bold, line breaks, etc)."
    )

    pdf.body("YOUR RESPONSIBILITY:")
    pdf.bullet(
        'You can CHANGE the HTML labels (the <b>...</b> parts). These are just '
        'display labels like "Alert Type:" or "File:" -- rename them to whatever you want.'
    )
    pdf.bullet(
        "You do NOT hardcode the actual alert data! The @{body('Compose_AlertType')} "
        "expression automatically pulls the REAL alert type from whatever ADO sent "
        "(e.g. 'secret', 'code', 'dependency'). Same for @{body('Compose_File')} -- "
        "it pulls the real file path from the ADO webhook payload."
    )
    pdf.bullet(
        "ACTION: Copy-paste the block below. Customize the labels if you want. "
        "Leave the @{body(...)} expressions as-is -- they pull live data from ADO."
    )

    pdf.code_block_mixed([
        '{',
        '  "op": "add",',
        '  "path": "/fields/Microsoft.VSTS.TCM.ReproSteps",',
        '  "value": "<b>Alert Type:</b> @{body(\'Compose_AlertType\')}<br>',
        '            <b>File:</b> @{body(\'Compose_File\')}<br>',
        '            <b>Severity:</b> @{body(\'Compose_Severity\')}"',
        '}',
        '',
        '// BREAKDOWN:',
        '//   <b>Alert Type:</b>            <-- YOUR label (change freely)',
        '//   @{body(\'Compose_AlertType\')}  <-- PULLED FROM ADO (not hardcoded!)',
        '//                                    ADO sends "secret" or "code" etc.',
        '//   <b>File:</b>                   <-- YOUR label (change freely)',
        '//   @{body(\'Compose_File\')}       <-- PULLED FROM ADO (not hardcoded!)',
        '//                                    ADO sends the real file path',
    ], highlights={2, 3, 4, 5})

    pdf.sub_heading("Adding AcceptanceCriteria")
    pdf.body(
        "This defines what 'done' looks like for resolving this security alert. "
        "Unlike the others, this is 100% STATIC text -- no dynamic expressions."
    )

    pdf.body("YOUR RESPONSIBILITY:")
    pdf.bullet(
        "This is entirely YOUR text. Write whatever acceptance criteria make sense "
        "for your team. The example below is a starting point -- change it completely "
        "to match your team's definition of done."
    )
    pdf.bullet(
        "The \\n creates a new line in the text. You can add or remove lines as needed."
    )
    pdf.bullet(
        "ACTION: Copy-paste the block below. Replace the criteria text with YOUR team's "
        "requirements. Everything here is editable."
    )

    pdf.code_block_mixed([
        '{',
        '  "op": "add",',
        '  "path": "/fields/Microsoft.VSTS.Common.AcceptanceCriteria",',
        '  "value": "1. Root cause identified\\n2. Fix merged to main\\n3. No new alerts"',
        '}',
        '',
        '// BREAKDOWN:',
        '//   EVERYTHING in "value" is YOUR text (no dynamic parts)',
        '//   Change it to whatever your team uses, for example:',
        '//   "1. Reviewed by security team\\n2. PR approved\\n3. Deployed to prod"',
    ], highlights={2, 3})

    # Summary table: what's yours vs what's auto
    pdf.blue_banner("Quick Reference: What You Control vs What Is Automatic")

    w_ref = [50, 70, 70]
    pdf.table_row(["Field", "YOUR Responsibility", "Pulled from ADO (not hardcoded)"],
                  w_ref, bold=True, fill=True)
    pdf.table_row(
        ["System.History",
         "Change the message text only",
         "@{utcNow()} = auto timestamp"],
        w_ref)
    pdf.table_row(
        ["ReproSteps",
         "Change HTML labels only",
         "@{body('Compose_...')} = real ADO data"],
        w_ref)
    pdf.table_row(
        ["AcceptanceCriteria",
         "Write ALL the text (100% yours)",
         "Nothing -- all static text you write"],
        w_ref)
    pdf.table_row(
        ["Custom fields",
         "Pick field name + reference name",
         "Use @{outputs('Compose_...')} to pull from ADO"],
        w_ref)

    pdf.tip_box(
        "WHERE TO PASTE: In the Logic App Code View, find the HTTP_CreateWorkItem action. "
        "Its 'body' is a JSON array of patch operations. Add each new entry as a new object "
        "in that array, separated by a comma."
    )

    pdf.blue_banner("Links & Relations (Advanced)")

    pdf.body(
        "You can also add hyperlinks and related work item links using the JSON Patch format:"
    )
    pdf.code_block_mixed([
        '// Add a hyperlink to the GHAzDO alert:',
        '{ "op": "add",',
        '  "path": "/relations/-",',
        '  "value": {',
        '    "rel": "Hyperlink",',
        '    "url": "https://dev.azure.com/org/project/_git/repo/alerts/42",',
        '    "attributes": { "comment": "GHAzDO Alert Link" }',
        '  }',
        '}',
    ], highlights={1, 2, 5})

    # ===== SECTION 3: CREATING CUSTOM FIELDS ===============================
    pdf.section_title("3", "Creating Custom Fields in ADO (Step-by-Step)")

    pdf.body(
        "If the built-in fields above are not enough, you can create completely custom "
        "fields in ADO. For example: SecurityTool, VulnerabilityCategory, ComplianceTag, "
        "RemediationOwner, etc."
    )

    pdf.blue_banner("Prerequisites")
    pdf.bullet("You must be a Project Collection Administrator or Organization Owner")
    pdf.bullet("Your project must use an INHERITED process (not a system process)")
    pdf.bullet("If using a system process, see Section 8 to create an inherited process first")

    pdf.blue_banner("Step-by-Step: Add a Custom Field")

    pdf.numbered_step(1,
        "Go to dev.azure.com/{your-org} and click the gear icon (bottom-left) "
        "to open Organization Settings"
    )
    pdf.numbered_step(2,
        'Under "Boards", click "Process"'
    )
    pdf.numbered_step(3,
        "Click on your inherited process name (e.g., Security-Process). "
        "If you only see system processes (Basic, Agile, Scrum, CMMI), you need to "
        "create an inherited process first -- see Section 8."
    )
    pdf.numbered_step(4,
        "Click on the Work Item type you are using (e.g., Issue, Bug, SecurityAlert)"
    )
    pdf.numbered_step(5,
        'Click "New field" at the top of the Layout tab'
    )
    pdf.numbered_step(6,
        "In the dialog, fill in the field details:"
    )

    pdf.code_block_mixed([
        "Create a field:",
        "  Name:        SecurityTool             <-- YOUR field name",
        "  Type:        Text (single line)        <-- pick a type",
        "               Other types: Integer, Decimal, DateTime, Boolean,",
        "               Picklist, Identity (person), Text (multi-line/HTML)",
        "  Description: The security scanning tool that detected this issue",
        "",
        "Add to layout:",
        "  Page:        Details (or create a new group)",
        "  Group:       You can create a new group called 'Security Details'",
    ], highlights={1, 2, 5})

    pdf.numbered_step(7,
        "For PICKLIST fields, click 'Options' to define the allowed values:"
    )
    pdf.code_block_mixed([
        "Example picklist for 'AlertCategory':",
        "  - secret",
        "  - code-scanning",
        "  - dependency",
        "  - infrastructure",
        "",
        "Example picklist for 'ComplianceFramework':",
        "  - SOC2",
        "  - HIPAA",
        "  - PCI-DSS",
        "  - FedRAMP",
        "  - ISO27001",
        "  - NIST",
        "  - GDPR",
    ], highlights={1, 2, 3, 4, 7, 8, 9, 10, 11, 12, 13})

    pdf.numbered_step(8,
        'Click "Add field" to save. The field is now available on all Work Items of that type.'
    )

    pdf.warning_box(
        "The field REFERENCE NAME is auto-generated as 'Custom.FieldName' "
        "(e.g., Custom.SecurityTool). You MUST use this exact reference name in the JSON. "
        "Once created, the reference name CANNOT be changed. The display name CAN be changed later."
    )

    pdf.tip_box(
        "You can also add RULES to custom fields. For example: make a field required, "
        "set a default value, or make it read-only when the state is 'Closed'. "
        "Go to the field settings and click 'Add a rule'."
    )

    # --- Visual flow diagram: ADO field -> JSON -> Logic App ---
    pdf.flow_diagram(
        "How Custom Fields Flow from ADO to the Logic App",
        [
            ("1. Create in ADO", [
                "Org Settings > Process",
                "Pick inherited process",
                "Pick Work Item type",
                'Click "New field"',
                "Set Name & Type",
            ]),
            ("2. Note Ref Name", [
                "ADO auto-generates:",
                "Custom.FieldName",
                "(e.g. Custom.SecurityTool)",
                "This is the KEY you",
                "use in the JSON!",
            ]),
            ("3. Add to JSON", [
                'In Logic App JSON:',
                '{ "op": "add",',
                '  "path": "/fields/',
                '    Custom.SecurityTool",',
                '  "value": "GHAzDO" }',
            ]),
            ("4. Deploy & Test", [
                "Save Logic App",
                "Send test webhook",
                "Check Work Item:",
                "new field should",
                "appear with value!",
            ]),
        ],
    )

    # ===== SECTION 4: RECOMMENDED CUSTOM FIELDS ===========================
    pdf.section_title("4", "Recommended Custom Fields for Security Teams")

    pdf.body(
        "Here are custom fields we recommend creating for security alert tracking. "
        "Create each one in ADO (Section 3), then add the corresponding JSON Patch entry."
    )

    w_rec = [40, 28, 50, 72]
    pdf.table_row(["Field Name", "Type", "Reference Name", "Example Value / Purpose"], w_rec, bold=True, fill=True)
    pdf.table_row(["SecurityTool", "Text", "Custom.SecurityTool", "GHAzDO -- identifies the source tool"], w_rec, highlight=True)
    pdf.table_row(["AlertCategory", "Picklist", "Custom.AlertCategory", "secret / code / dependency"], w_rec, highlight=True)
    pdf.table_row(["SourceRepo", "Text", "Custom.SourceRepo", "The repo where alert was found"], w_rec, highlight=True)
    pdf.table_row(["AlertSeverity", "Picklist", "Custom.AlertSeverity", "critical / high / medium / low"], w_rec, highlight=True)
    pdf.table_row(["FilePath", "Text", "Custom.FilePath", "src/config.env -- affected file"], w_rec, highlight=True)
    pdf.table_row(["SecretType", "Text", "Custom.SecretType", "Azure Storage Account Key"], w_rec, highlight=True)
    pdf.table_row(["RemediationOwner", "Identity", "Custom.RemediationOwner", "Person responsible for fix"], w_rec, highlight=True)
    pdf.table_row(["ComplianceTag", "Picklist", "Custom.ComplianceTag", "SOC2 / HIPAA / PCI-DSS"], w_rec, highlight=True)
    pdf.table_row(["SLADueDate", "DateTime", "Custom.SLADueDate", "Remediation deadline date"], w_rec, highlight=True)
    pdf.table_row(["AutoDetected", "Boolean", "Custom.AutoDetected", "true -- flag for automated finds"], w_rec, highlight=True)
    pdf.table_row(["CVEID", "Text", "Custom.CVEID", "CVE-2024-1234 (for dependencies)"], w_rec, highlight=True)
    pdf.table_row(["CVSSScore", "Decimal", "Custom.CVSSScore", "9.8 (severity score 0-10)"], w_rec, highlight=True)

    # ===== SECTION 5: COMPLETE JSON EXAMPLE ================================
    pdf.section_title("5", "Complete JSON Example with Custom Fields")

    pdf.body(
        "Here is what the HTTP_CreateWorkItem body looks like after adding all the "
        "recommended custom fields. Copy this and replace the existing body array "
        "in ghazdo-to-ado.json (lines 153-158)."
    )

    pdf.body(
        "LEGEND: Lines highlighted in YELLOW with >> are NEW fields you are adding. "
        "Non-highlighted lines are the original fields already in the default JSON."
    )

    # Lines 12-19 are Assignment (highlight), 20-35 are Custom (highlight)
    pdf.code_block_mixed([
        '"body": [',                                                        # 0
        '  // --- Standard fields (already in default JSON) ---',           # 1
        '  { "op": "add", "path": "/fields/System.Title",',                # 2
        '    "value": "@{outputs(\'Compose_Title\')}" },',                  # 3
        '  { "op": "add", "path": "/fields/System.Description",',          # 4
        '    "value": "@{outputs(\'Compose_Description\')}" },',            # 5
        '  { "op": "add", "path": "/fields/System.Tags",',                 # 6
        '    "value": "@{outputs(\'Compose_Tags\')}" },',                   # 7
        '  { "op": "add",',                                                # 8
        '    "path": "/fields/Microsoft.VSTS.Common.Priority",',           # 9
        '    "value": "@if(or(equals(...severity...)),1,',                  # 10
        '              if(equals(...,\'medium\'),2,3))" },',                # 11
        '',                                                                # 12
        '  // --- NEW: Assignment fields (built-in, no ADO setup) ---',    # 13
        '  { "op": "add", "path": "/fields/System.AssignedTo",',           # 14
        '    "value": "security-team@company.com" },',                     # 15
        '  { "op": "add", "path": "/fields/System.AreaPath",',             # 16
        '    "value": "MyProject\\\\Security" },',                          # 17
        '  { "op": "add", "path": "/fields/System.IterationPath",',        # 18
        '    "value": "MyProject\\\\Sprint 5" },',                          # 19
        '',                                                                # 20
        '  // --- NEW: Custom fields (create in ADO first! Sec 3) ---',    # 21
        '  { "op": "add", "path": "/fields/Custom.SecurityTool",',         # 22
        '    "value": "GHAzDO" },',                                        # 23
        '  { "op": "add", "path": "/fields/Custom.AlertCategory",',        # 24
        '    "value": "@{outputs(\'Compose_AlertType\')}" },',              # 25
        '  { "op": "add", "path": "/fields/Custom.SourceRepo",',           # 26
        '    "value": "@{outputs(\'Compose_RepoName\')}" },',               # 27
        '  { "op": "add", "path": "/fields/Custom.AlertSeverity",',        # 28
        '    "value": "@{outputs(\'Compose_Severity\')}" },',               # 29
        '  { "op": "add", "path": "/fields/Custom.FilePath",',             # 30
        '    "value": "@{outputs(\'Compose_FilePath\')}" },',               # 31
        '  { "op": "add", "path": "/fields/Custom.AutoDetected",',         # 32
        '    "value": true },',                                            # 33
        '  { "op": "add", "path": "/fields/Custom.ComplianceTag",',        # 34
        '    "value": "SOC2" }',                                           # 35
        ']',                                                               # 36
    ], highlights={13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35})

    pdf.body(
        "NOTE: The @{outputs('Compose_...')} values are DYNAMIC -- they pull data "
        "from the GHAzDO webhook payload automatically. Static values like "
        '"GHAzDO" or "SOC2" stay the same for every work item.'
    )

    pdf.warning_box(
        "If you reference a Custom.* field that does NOT exist in ADO, the API will "
        "return a 400 Bad Request error. Always create the field in ADO first (Section 3), "
        "then add the JSON entry."
    )

    # --- NEW: Connecting the dots - ADO field creation to JSON ---
    pdf.sub_heading("Connecting the Dots: From ADO Field to JSON Entry")

    pdf.body(
        "Here is the exact connection between creating a field in ADO and adding it "
        "to the JSON. We will walk through ONE complete example end-to-end."
    )

    pdf.blue_banner("Example: Adding a 'SecurityTool' Field (Complete Walkthrough)")

    pdf.body("PART A -- Create the field in ADO:")
    pdf.numbered_step(1, "Go to dev.azure.com/{org} -> Organization Settings -> Process")
    pdf.numbered_step(2, "Click your inherited process (e.g., Security-Process)")
    pdf.numbered_step(3, "Click the work item type (e.g., Issue)")
    pdf.numbered_step(4, 'Click "New field"')
    pdf.numbered_step(5, 'Enter Name: SecurityTool, Type: Text (single line)')
    pdf.numbered_step(6, 'Click "Add field"')
    pdf.numbered_step(7, "ADO auto-generates the reference name: Custom.SecurityTool")

    pdf.body("PART B -- Add the JSON entry in ghazdo-to-ado.json:")
    pdf.numbered_step(8, "Open ghazdo-to-ado.json in any text editor")
    pdf.numbered_step(9, 'Find the "body" array in the HTTP_CreateWorkItem action (line ~153)')
    pdf.numbered_step(10, "Add a comma after the LAST entry in the array")
    pdf.numbered_step(11, "Add this new entry:")

    pdf.code_block_mixed([
        '  // ... existing entries above ...',
        '  { "op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority",',
        '    "value": "..." }          <-- add comma here!',
        '',
        '  // NEW ENTRY: (add this)',
        '  { "op": "add",',
        '    "path": "/fields/Custom.SecurityTool",',
        '    "value": "GHAzDO" }',
    ], highlights={4, 5, 6, 7})

    pdf.numbered_step(12, "Save the file")
    pdf.numbered_step(13, "Go to Logic App -> Code View -> paste the updated JSON -> Save")

    pdf.body(
        "That is the COMPLETE flow: Create in ADO -> get reference name -> add JSON "
        "entry -> paste into Code View -> Save. Repeat for each custom field."
    )

    pdf.blue_banner("Example: Adding a Dynamic Field (SourceRepo)")

    pdf.body(
        "Some fields should be filled DYNAMICALLY from the webhook payload instead of "
        "using a hardcoded value. Here is how:"
    )

    pdf.body("PART A -- Create the field in ADO (same as above):")
    pdf.numbered_step(1, 'Create field: Name=SourceRepo, Type=Text. ADO gives you: Custom.SourceRepo')

    pdf.body("PART B -- Add the JSON entry with a DYNAMIC value:")
    pdf.code_block_mixed([
        '  // Static value (same every time):',
        '  { "op": "add", "path": "/fields/Custom.SecurityTool",',
        '    "value": "GHAzDO" },',
        '',
        '  // Dynamic value (different per alert):',
        '  { "op": "add", "path": "/fields/Custom.SourceRepo",',
        '    "value": "@{outputs(\'Compose_RepoName\')}" },',
    ], highlights={4, 5, 6})

    pdf.body("Available dynamic values you can use:")
    w_dyn = [70, 120]
    pdf.table_row(["Dynamic Expression", "What It Contains"], w_dyn, bold=True, fill=True)
    pdf.table_row(["@{outputs('Compose_AlertType')}", "Alert category: secret, code, or dependency"], w_dyn)
    pdf.table_row(["@{outputs('Compose_Severity')}", "Severity: critical, high, medium, low"], w_dyn)
    pdf.table_row(["@{outputs('Compose_RepoName')}", "Repository name where alert was found"], w_dyn)
    pdf.table_row(["@{outputs('Compose_FilePath')}", "File path of the affected code/secret"], w_dyn)
    pdf.table_row(["@{outputs('Compose_AlertId')}", "Unique alert ID number"], w_dyn)
    pdf.table_row(["@{outputs('Compose_AlertUrl')}", "URL link back to the GHAzDO alert"], w_dyn)
    pdf.table_row(["@{outputs('Compose_LineNumber')}", "Line number in the file"], w_dyn)
    pdf.table_row(["@{outputs('Compose_GhasTag')}", "Unique tag: GHAzDO-repoName-alertId"], w_dyn)

    # ===== SECTION 6: WHY SO MANY FIELDS ===================================
    pdf.section_title("6", "Why Does the Work Item Have So Many Fields?")

    pdf.body(
        "You may notice the auto-created Work Item has many fields populated. "
        "Here is WHY each default field matters and what value it provides:"
    )

    w_why = [45, 55, 90]
    pdf.table_row(["Field", "Value Example", "Why It Matters"], w_why, bold=True, fill=True)
    pdf.table_row(["Title", "[GHAzDO-Secret] Azure Key", "Instantly tells you WHAT was found"], w_why)
    pdf.table_row(["Description", "HTML table with details", "Full context without opening GHAzDO portal"], w_why)
    pdf.table_row(["Tags (GHAzDO)", "GHAzDO", "Filter ALL security items across the board"], w_why)
    pdf.table_row(["Tags (type)", "secret", "Filter by alert category (secret/code/dep)"], w_why)
    pdf.table_row(["Tags (severity)", "critical", "Filter by urgency level"], w_why)
    pdf.table_row(["Tags (unique)", "GHAzDO-repo-42", "Prevents duplicates + enables auto-close"], w_why)
    pdf.table_row(["Priority", "1 (Critical)", "Drives board ordering and SLA tracking"], w_why)
    pdf.table_row(["State", "To Do -> Done", "Tracks lifecycle: auto-closes when resolved"], w_why)

    pdf.body(
        "The goal is to give the security team EVERYTHING they need to triage and "
        "respond to the alert directly from the ADO Work Item -- without having to "
        "switch to the GHAzDO portal. The description includes an HTML table with "
        "alert type, severity, repository, file path, line number, and a direct link "
        "back to the alert for detailed investigation."
    )

    # ===== SECTION 7: UNDERSTANDING TAGS ===================================
    pdf.section_title("7", "Understanding the Tags System")

    pdf.body(
        "The workflow creates FOUR tags on every Work Item, separated by semicolons. "
        "Each tag serves a specific purpose:"
    )

    pdf.code_block_mixed([
        "Tags = GHAzDO;secret;critical;GHAzDO-my-repo-42",
        "",
        "  Tag 1: GHAzDO           -> Master filter: find ALL GHAzDO items",
        "  Tag 2: secret            -> Alert type (secret / code / dependency)",
        "  Tag 3: critical          -> Severity (critical / high / medium / low)",
        "  Tag 4: GHAzDO-my-repo-42 -> Unique ID for dedup + auto-close",
    ], highlights={0, 5})

    pdf.sub_heading("Why Tag 4 is Critical")

    pdf.body(
        "Tag 4 is the most important -- it is a unique identifier combining the repo "
        "name and alert ID. This is how the auto-close flow finds the right Work Item "
        "to close when the alert is resolved. Without this tag, the Logic App would not "
        "know which Work Item corresponds to which alert."
    )

    pdf.body(
        "It also prevents DUPLICATE work items. When a new alert webhook arrives, the "
        "Logic App first queries ADO: 'Is there already a Work Item tagged with "
        "GHAzDO-reponame-42?' If yes, it skips creating a new one."
    )

    pdf.sub_heading("Adding Your Own Tags")

    pdf.body(
        "You can ADD more tags by modifying the Compose_Tags action in the JSON. "
        "For example, to add a team tag and a compliance tag:"
    )

    pdf.code_block_mixed([
        '// In ghazdo-to-ado.json, find Compose_Tags (line ~73-80):',
        '"Compose_Tags": {',
        '  "type": "Compose",',
        '  "inputs": "@concat(',
        "    'GHAzDO;',",
        "    outputs('Compose_AlertType'), ';',",
        "    outputs('Compose_Severity'), ';',",
        "    outputs('Compose_GhasTag'),",
        "    ';SecurityTeam;SOC2'            <-- ADD your custom tags here",
        '  )"',
        '}',
        '',
        '// Result: GHAzDO;secret;critical;GHAzDO-repo-42;SecurityTeam;SOC2',
    ], highlights={8, 12})

    pdf.warning_box(
        "Do NOT remove or change the format of Tag 4 (GHAzDO-reponame-alertId). "
        "This tag is used by the auto-close logic to find matching work items. "
        "You can safely ADD tags after it."
    )

    # ===== SECTION 8: INHERITED PROCESS TEMPLATE ===========================
    pdf.section_title("8", "Creating an Inherited Process Template in ADO")

    pdf.body(
        "Azure DevOps ships with four SYSTEM process templates: Basic, Agile, Scrum, and "
        "CMMI. These system templates are READ-ONLY -- you cannot add custom work item "
        "types or custom fields to them directly. To unlock full customization, you must "
        "create an INHERITED process. Think of it as making a copy of the system template "
        "that you own and can modify freely."
    )

    pdf.blue_banner("Why You Need an Inherited Process")

    pdf.body("An inherited process gives you the ability to:")
    pdf.bullet("Add custom work item types (SecurityAlert, Vulnerability, etc.)")
    pdf.bullet("Add custom fields to any work item type (built-in or custom)")
    pdf.bullet("Customize the states/workflow for each work item type")
    pdf.bullet("Change the layout of the work item form (add groups, pages)")
    pdf.bullet("Hide built-in fields you do not need")
    pdf.bullet("Add custom rules (auto-set fields, make fields required, etc.)")

    pdf.body(
        "Your existing work items, queries, boards, and backlogs are NOT affected. "
        "The inherited process includes everything from the parent template plus your changes."
    )

    pdf.blue_banner("Which System Template Should You Inherit From?")

    w_tmpl = [30, 55, 105]
    pdf.table_row(["Template", "Built-in Types", "Best For"], w_tmpl, bold=True, fill=True)
    pdf.table_row(["Basic", "Issue, Epic, Task", "Simplest starting point, small teams"], w_tmpl)
    pdf.table_row(["Agile", "User Story, Bug, Feature, Epic, Task", "Most teams, flexible workflow"], w_tmpl)
    pdf.table_row(["Scrum", "PBI, Bug, Feature, Epic, Task", "Scrum methodology teams"], w_tmpl)
    pdf.table_row(["CMMI", "Requirement, Bug, Change Req, etc.", "Regulated/compliance-heavy orgs"], w_tmpl)

    pdf.tip_box(
        "For security teams, we recommend inheriting from 'Basic' (simplest) or 'Agile' "
        "(most flexible). If your org already uses Scrum or CMMI, inherit from that to "
        "maintain consistency."
    )

    pdf.blue_banner("Step-by-Step: Create an Inherited Process")

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
    pdf.code_block_mixed([
        "  Basic    (System)  -- simplest: Issue, Epic, Task",
        "  Agile    (System)  -- User Story, Bug, Feature, Epic, Task",
        "  Scrum    (System)  -- Product Backlog Item, Bug, Feature, Epic, Task",
        "  CMMI     (System)  -- Requirement, Bug, Change Request, Feature, Epic, Task",
        "",
        "  If you see (System) next to the name, it is READ-ONLY.",
        "  If you see (Inherited), someone already created a custom process.",
    ], highlights={0, 5})

    pdf.numbered_step(5,
        'Choose which template to inherit FROM. Click the "..." (three dots) menu '
        "next to your chosen template."
    )
    pdf.numbered_step(6,
        'Click "Create inherited process" from the dropdown menu'
    )
    pdf.numbered_step(7,
        "In the dialog that appears, fill in:"
    )
    pdf.code_block_mixed([
        'Name:         "Security-Process"          <-- YOUR process name',
        '              (or: "MyCompany-Security", "DevSecOps-Process",',
        '               "BrandSafway-Security")',
        "",
        "Description:  Custom process template for GHAzDO security",
        "              alert tracking with custom work item types",
        "              and security-specific fields.",
    ], highlights={0, 4})

    pdf.numbered_step(8,
        'Click "Create". Your new inherited process is now ready!'
    )

    pdf.body(
        "You will be taken to the process page showing all work item types inherited "
        "from the parent. Everything from the parent is included -- you can now add "
        "custom types and fields on top."
    )

    # ===== SECTION 9: ADDING CUSTOM WORK ITEM TYPES ========================
    pdf.section_title("9", "Adding Custom Work Item Types")

    pdf.body(
        "Now that you have an inherited process, let us add three security-specific "
        "work item types. Each one gets its own icon, color, fields, and states."
    )

    # --- SecurityAlert ---
    pdf.sub_heading("9a. Type: SecurityAlert")

    pdf.purple_banner("Create the Type")

    pdf.numbered_step(1,
        'On your inherited process page, click "New work item type" (green + button)'
    )
    pdf.numbered_step(2, "Fill in the details:")
    pdf.code_block_mixed([
        "Name:         SecurityAlert              <-- YOUR type name",
        "Description:  Auto-created from GHAzDO security scanning alerts",
        "Icon:         Shield (or Warning triangle)",
        "Color:        Red (#E74C3C) -- high visibility on boards",
    ], highlights={0, 3})
    pdf.numbered_step(3, 'Click "Create"')

    pdf.purple_banner("Add Custom Fields")

    pdf.numbered_step(4,
        'You are now on the SecurityAlert layout page. Click "New field" for each:'
    )
    pdf.code_block_mixed([
        "Field 1:  AlertType",
        "  Type:   Text (single line)",
        "  Desc:   Type of alert (secret, code, dependency)",
        "",
        "Field 2:  Severity",
        "  Type:   Picklist -> Values: critical, high, medium, low",
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
    ], highlights={0, 4, 8, 12, 16, 20, 24})

    pdf.purple_banner("Customize the States (Workflow)")

    pdf.numbered_step(5,
        "Click the 'States' tab to customize the workflow for security alerts:"
    )
    pdf.code_block_mixed([
        "Recommended states for SecurityAlert:",
        "",
        "  New         (Proposed)     -- Alert just received from GHAzDO",
        "  Triaging    (InProgress)   -- Team is evaluating the alert",
        "  Remediating (InProgress)   -- Fix is being implemented",
        "  Verified    (Resolved)     -- Fix confirmed, alert resolved",
        "  Closed      (Completed)    -- Fully done",
        "",
        "How to add a state:",
        "  a) Click 'New state'",
        "  b) Enter the state name (e.g., 'Triaging')",
        "  c) Select the STATE CATEGORY:",
        "     - Proposed   = maps to 'New' in queries and reports",
        "     - InProgress = maps to 'Active' in queries and reports",
        "     - Resolved   = maps to 'Resolved' in queries and reports",
        "     - Completed  = maps to 'Closed' in queries and reports",
        "  d) Set the order (drag to reorder)",
        "  e) Click 'Save'",
    ], highlights={2, 3, 4, 5, 6})

    pdf.warning_box(
        "If you add custom states, you MUST update the Logic App JSON! "
        'The auto-close action sets State to "Done". Change this to match your '
        'completed state (e.g., "Closed" or "Verified"). Find HTTP_CloseWorkItem '
        "in the JSON and update the System.State value."
    )

    # --- Vulnerability ---
    pdf.sub_heading("9b. Type: Vulnerability")

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
        "Field 1:  CVEID           (Text)     -- CVE-2024-1234",
        "Field 2:  CVSSScore       (Decimal)  -- 9.8 (0.0 to 10.0)",
        "Field 3:  AttackVector    (Picklist)  -- Network, Adjacent, Local, Physical",
        "Field 4:  AffectedPackage (Text)     -- e.g., lodash@4.17.20",
        "Field 5:  FixVersion      (Text)     -- e.g., lodash@4.17.21",
        "Field 6:  ExploitAvailable (Picklist) -- Yes, No, Unknown",
        "Field 7:  PatchStatus     (Picklist)  -- Not Started, In Progress, Patched, Wont Fix",
    ])

    # --- ComplianceFinding ---
    pdf.sub_heading("9c. Type: ComplianceFinding")

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
        "Field 1:  ComplianceFramework (Picklist) -- SOC2, HIPAA, PCI-DSS,",
        "                                            FedRAMP, ISO27001, NIST, GDPR",
        "Field 2:  ControlID           (Text)     -- SOC2 CC6.1, PCI-DSS 6.5.3",
        "Field 3:  RiskRating          (Picklist) -- Critical, High, Medium, Low, Info",
        "Field 4:  DueDate             (DateTime) -- Compliance remediation deadline",
        "Field 5:  AuditorNotes        (HTML)     -- Notes from compliance reviewer",
        "Field 6:  EvidenceLink        (Text)     -- URL to evidence documentation",
    ])

    # ===== SECTION 10: ASSIGNING PROCESS TO PROJECT ========================
    pdf.section_title("10", "Assigning the Inherited Process to Your Project")

    pdf.body(
        "After creating your inherited process with custom types, you must assign it "
        "to your ADO project. This tells the project to use YOUR process instead of "
        "the default system one."
    )

    pdf.numbered_step(1, "Go to Organization Settings -> Process")
    pdf.numbered_step(2, "Click on your inherited process name (e.g., Security-Process)")
    pdf.numbered_step(3, 'Click the "Projects" tab at the top')
    pdf.numbered_step(4, "If your project is not listed, assign it:")
    pdf.code_block([
        "Option A -- From the Process page:",
        "  a) On the Projects tab, you may not see your project yet",
        "  b) Navigate to your project settings instead (see Option B)",
        "",
        "Option B -- From Project Settings (recommended):",
        "  a) Go to dev.azure.com/{org}/{project}",
        "  b) Click Project Settings (gear icon, bottom-left)",
        "  c) Under 'General', click 'Overview'",
        "  d) Find 'Process' -- it shows the current template (e.g., Basic)",
        "  e) Click the process name link",
        "  f) Click 'Change process' (top-right of the process page)",
        "  g) Select your inherited process (e.g., 'Security-Process')",
        "  h) Click 'Save'",
    ])

    pdf.warning_box(
        "Changing the process is NON-DESTRUCTIVE. All existing work items, "
        "queries, boards, and backlogs keep working. Existing items will NOT lose data. "
        "The new custom types simply become AVAILABLE for new items. However, test on a "
        "non-production project first if you are concerned."
    )

    # ===== SECTION 11: USING CUSTOM TYPES WITH LOGIC APP ===================
    pdf.section_title("11", "Using Custom Types with the Logic App")

    pdf.body(
        "Once your project uses the inherited process, update the Logic App JSON "
        "to create your custom work item type instead of Issue."
    )

    pdf.blue_banner("Step 1: Change the workItemType Parameter")

    pdf.code_block([
        '// In ghazdo-to-ado.json, change the workItemType parameter:',
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

    pdf.blue_banner("Step 2: Add Custom Fields to the Body")

    pdf.code_block([
        '// Add entries for your custom fields in HTTP_CreateWorkItem body:',
        '"body": [',
        '  ... existing standard fields ...',
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

    pdf.blue_banner("Step 3: Update the Auto-Close State (If Using Custom States)")

    pdf.code_block([
        '// In HTTP_CloseWorkItem, change the State value to match',
        '// your custom completed state:',
        '{ "op": "add",',
        '  "path": "/fields/System.State",',
        '  "value": "Closed" }    <-- or "Verified" -- match YOUR state',
    ])

    pdf.body(
        "Save the JSON in Code View. The Logic App will now create your custom "
        "work item type with all your custom fields populated automatically."
    )

    # ===== SECTION 12: MULTIPLE LOGIC APPS =================================
    pdf.section_title("12", "Advanced: Multiple Logic Apps for Different Alert Types")

    pdf.body(
        "For organizations that want maximum control, you can deploy MULTIPLE Logic Apps "
        "-- each one creating a different custom work item type based on the alert category."
    )

    pdf.code_block([
        "Logic App 1: ghas-ado-secrets",
        '  workItemType = "SecretExposure"',
        "  Service Hook filter: secret alerts only",
        "  Custom fields: SecretType, RotationStatus, ExpiryDate",
        "",
        "Logic App 2: ghas-ado-vulnerabilities",
        '  workItemType = "Vulnerability"',
        "  Service Hook filter: dependency alerts only",
        "  Custom fields: CVEID, CVSSScore, AffectedPackage, FixVersion",
        "",
        "Logic App 3: ghas-ado-codescan",
        '  workItemType = "ComplianceFinding"',
        "  Service Hook filter: code scanning alerts only",
        "  Custom fields: ControlID, RiskRating, ComplianceFramework",
    ])

    pdf.body(
        "Each Logic App uses the SAME ghazdo-to-ado.json -- just with a different "
        "workItemType parameter and additional custom field entries. The Service Hooks "
        "can filter by alert type in ADO to route each category to the right Logic App."
    )

    pdf.tip_box(
        "Alternatively, you can use a SINGLE Logic App with conditional branching "
        "to create different work item types based on the alert type. Add a condition "
        "that checks outputs('Compose_AlertType') and routes to different HTTP actions."
    )

    # ===== SECTION 13: PRIORITY MAPPING ====================================
    pdf.section_title("13", "Changing Priority Mapping")

    pdf.body(
        "The workflow maps GHAzDO severity to ADO priority. The default mapping is:"
    )

    w_p = [60, 60, 70]
    pdf.table_row(["GHAzDO Severity", "ADO Priority", "Meaning"], w_p, bold=True, fill=True)
    pdf.table_row(["critical", "1 - Critical", "Immediate action needed"], w_p)
    pdf.table_row(["high", "1 - Critical", "Immediate action needed"], w_p)
    pdf.table_row(["medium", "2 - High", "Address soon"], w_p)
    pdf.table_row(["low", "3 - Medium", "Plan to address"], w_p)
    pdf.table_row(["(other)", "3 - Medium", "Default fallback"], w_p)

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
        '// Example: Make each severity its own priority:',
        '@if(equals(severity,"critical"), 1,',
        '  if(equals(severity,"high"), 2,',
        '    if(equals(severity,"medium"), 3, 4)))',
    ])

    # ===== SECTION 14: AUTO-ASSIGNING ======================================
    pdf.section_title("14", "Auto-Assigning to Team Members")

    pdf.body(
        "Add an AssignedTo field to automatically route security alerts to the right "
        "person or team:"
    )

    pdf.sub_heading("Option A: Assign to a Fixed Person/Team")
    pdf.code_block([
        '{ "op": "add",',
        '  "path": "/fields/System.AssignedTo",',
        '  "value": "security-team@company.com" }',
    ])

    pdf.sub_heading("Option B: Dynamic Assignment Based on Alert Type")
    pdf.body(
        "Add a new Compose action before HTTP_CreateWorkItem that picks the right owner:"
    )
    pdf.code_block([
        '// Add this action to the JSON:',
        '"Compose_AssignTo": {',
        '  "type": "Compose",',
        '  "inputs": "@if(',
        "    equals(outputs('Compose_AlertType'),'secret'),",
        "    'secrets-team@company.com',",
        "    if(equals(outputs('Compose_AlertType'),'dependency'),",
        "      'sca-team@company.com',",
        "      'appsec-team@company.com'))",
        '",',
        '  "runAfter": { "Compose_AlertType": ["Succeeded"] }',
        '}',
        '',
        '// Then in the HTTP_CreateWorkItem body, reference it:',
        '{ "op": "add",',
        '  "path": "/fields/System.AssignedTo",',
        "  \"value\": \"@{outputs('Compose_AssignTo')}\" }",
    ])

    # ===== SECTION 15: WORK ITEM TYPE ======================================
    pdf.section_title("15", "Changing the Work Item Type")

    pdf.body(
        'The default workItemType parameter is "Issue" (for the Basic process template). '
        "Here are all the options by process template:"
    )

    w_wit = [40, 45, 105]
    pdf.table_row(["Process", "Recommended", "All Available Types"], w_wit, bold=True, fill=True)
    pdf.table_row(["Basic", "Issue", "Issue, Epic, Task"], w_wit)
    pdf.table_row(["Agile", "Bug", "Bug, User Story, Feature, Epic, Task"], w_wit)
    pdf.table_row(["Scrum", "Bug", "Bug, Product Backlog Item, Feature, Epic, Task"], w_wit)
    pdf.table_row(["CMMI", "Bug", "Bug, Requirement, Change Request, Feature, Epic, Task"], w_wit)
    pdf.table_row(["Inherited", "YOUR TYPE", "SecurityAlert, Vulnerability, ComplianceFinding, etc."], w_wit)

    pdf.body(
        "To change: In Code View, find the parameters section at the top of the JSON "
        'and change the defaultValue of workItemType.'
    )

    # ===== SECTION 16: QUICK REFERENCE =====================================
    pdf.section_title("16", "Quick Reference: What to Change Where")

    pdf.body("Summary of where to make each type of customization:")

    w_ref = [55, 50, 85]
    pdf.table_row(["What You Want", "Change In", "How"], w_ref, bold=True, fill=True)
    pdf.table_row([
        "Use a built-in type",
        "Logic App JSON only",
        'Change workItemType param (e.g., "Bug")'
    ], w_ref)
    pdf.table_row([
        "Create a custom type",
        "ADO Process first",
        "Inherited process -> New work item type (Sec. 8-9)"
    ], w_ref)
    pdf.table_row([
        "Use a custom type",
        "ADO + JSON",
        "Create type, then update workItemType param (Sec. 11)"
    ], w_ref)
    pdf.table_row([
        "Add built-in fields",
        "JSON only",
        "Add JSON Patch entries (Section 2)"
    ], w_ref)
    pdf.table_row([
        "Add custom fields",
        "ADO + JSON",
        "Create field in ADO (Sec. 3), add JSON entry (Sec. 5)"
    ], w_ref)
    pdf.table_row([
        "Change states",
        "ADO + JSON",
        "Edit states in Process (Sec. 9a), update close action"
    ], w_ref)
    pdf.table_row([
        "Change priority map",
        "JSON only",
        "Edit @if() expression (Section 13)"
    ], w_ref)
    pdf.table_row([
        "Change/add tags",
        "JSON only",
        "Edit Compose_Tags action (Section 7)"
    ], w_ref)
    pdf.table_row([
        "Auto-assign owner",
        "JSON only",
        "Add AssignedTo field (Section 14)"
    ], w_ref)
    pdf.table_row([
        "Multiple alert routing",
        "Azure + ADO",
        "Deploy multiple Logic Apps (Section 12)"
    ], w_ref)

    # ===== FINAL PAGE ======================================================
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*MS_BLUE)
    pdf.cell(0, 12, safe("You're All Set!"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*DARK_TEXT)
    pdf.multi_cell(0, 7, safe(
        "This guide covered everything you need to customize the GHAzDO-to-ADO "
        "Logic App integration for your organization. From simple field additions "
        "to fully custom work item types with their own states and workflows -- "
        "the system is designed to adapt to YOUR security operations process."
    ), align="C")

    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*MS_BLUE)
    pdf.cell(0, 8, safe("Key Files"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*DARK_TEXT)
    pdf.ln(3)
    pdf.cell(0, 7, safe("ghazdo-to-ado.json -- The workflow JSON (paste into Code View)"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, safe("Demo5-E2E-Setup-Guide.pdf -- Full deployment walkthrough"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, safe("This PDF -- Customization reference"), align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(15)
    pdf.set_draw_color(*MED_GRAY)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 6, safe("Confidential - Prepared for Customer"), align="C",
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
    print("Generating GHAzDO Customization Guide PDF...")
    build_pdf()
    print("Done!")
