#!/usr/bin/env python3
"""
Generate the GHAzDO E2E Demo Complete Guide PDF.
Uses fpdf2 to produce a professional, screenshot-rich document.
"""

import os
import sys
from datetime import datetime
from fpdf import FPDF

# -- Paths ------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCREENSHOTS_DIR = os.path.join(REPO_ROOT, "screenshots")
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
OUTPUT_PDF = os.path.join(DOCS_DIR, "GHAzDO-E2E-Demo-Complete-Guide.pdf")

# -- Colors -----------------------------------------------------------------
MS_BLUE = (0, 120, 212)       # #0078D4
DARK_TEXT = (33, 33, 33)
WHITE = (255, 255, 255)
LIGHT_GRAY = (245, 245, 245)  # #F5F5F5
MED_GRAY = (200, 200, 200)
HEADER_BG = (0, 120, 212)
SECTION_BG = (230, 242, 255)
CODE_BG = (245, 245, 245)


class DemoPDF(FPDF):
    """Custom PDF with headers, footers, and helper methods."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=25)
        self.toc_entries = []
        self.current_section = ""

    # -- Header / Footer ----------------------------------------------------
    def header(self):
        if self.page_no() == 1:
            return  # title page has its own layout
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*MS_BLUE)
        self.cell(0, 8, "GHAzDO to ADO Work Items - E2E Demo Guide", align="L")
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
        """Major section heading (blue background bar)."""
        self.current_section = f"{number}. {title}"
        self.toc_entries.append((self.current_section, self.page_no()))
        self.ln(4)
        self.set_fill_color(*MS_BLUE)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, f"  {number}. {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(4)
        self.set_text_color(*DARK_TEXT)

    def sub_heading(self, text):
        """Sub-section heading."""
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

    def code_block(self, lines, font_size=8):
        """Render a code block with gray background."""
        self.ln(1)
        self.set_fill_color(*CODE_BG)
        self.set_font("Courier", "", font_size)
        self.set_text_color(*DARK_TEXT)
        for line in lines:
            safe = line.replace("\t", "    ")
            self.cell(0, 4.5, f"  {safe}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def add_screenshot(self, filename, caption="", width=190):
        """Embed a screenshot image with optional caption."""
        path = os.path.join(SCREENSHOTS_DIR, filename)
        if not os.path.exists(path):
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(200, 0, 0)
            self.cell(0, 6, f"[Screenshot not found: {filename}]", new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(*DARK_TEXT)
            return

        # Check remaining space; add page if needed
        if self.get_y() > 200:
            self.add_page()

        self.ln(2)
        try:
            self.image(path, x=10, w=width)
        except Exception as e:
            self.set_font("Helvetica", "I", 9)
            self.cell(0, 6, f"[Error loading {filename}: {e}]", new_x="LMARGIN", new_y="NEXT")
            return

        if caption:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, caption, align="C", new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(*DARK_TEXT)
        self.ln(3)

    def table_row(self, cells, widths, bold=False, fill=False):
        style = "B" if bold else ""
        if fill:
            self.set_fill_color(*SECTION_BG)
        self.set_font("Helvetica", style, 9)
        h = 6
        for i, (cell_text, w) in enumerate(zip(cells, widths)):
            self.cell(w, h, f" {cell_text}", border=1, fill=fill)
        self.ln(h)

    def check_space(self, needed_mm=60):
        """Add a page break if less than needed_mm remains."""
        if self.get_y() > (297 - 25 - needed_mm):
            self.add_page()


def build_pdf():
    pdf = DemoPDF()

    # ======================================================================
    # TITLE PAGE
    # ======================================================================
    pdf.add_page()

    # Blue banner at top
    pdf.set_fill_color(*MS_BLUE)
    pdf.rect(0, 0, 210, 100, "F")

    pdf.set_y(25)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 12, "GHAzDO to ADO Work Items", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Complete E2E Demo Guide", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(6)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "Designer-Only Logic App with Automated Work Item Lifecycle", align="C",
             new_x="LMARGIN", new_y="NEXT")

    # Metadata below banner
    pdf.set_y(115)
    pdf.set_text_color(*DARK_TEXT)
    pdf.set_font("Helvetica", "", 11)
    meta = [
        ("Date", datetime.now().strftime("%B %d, %Y")),
        ("Author", "Copilot CLI Demo Session"),
        ("Customer", "Learfield / BrandSafway"),
        ("Platform", "Azure Logic Apps (Consumption) + Azure DevOps"),
        ("Integration", "GHAzDO Advanced Security -> Service Hooks -> Logic App -> ADO Boards"),
    ]
    for label, value in meta:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(45, 8, f"{label}:", align="R")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, f"  {value}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)
    pdf.set_draw_color(*MS_BLUE)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())
    pdf.ln(8)

    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 6, (
        "This document captures the complete end-to-end walkthrough of building a "
        "GHAzDO-to-ADO integration using Azure Logic Apps, including every expression, "
        "screenshot, troubleshooting step, and test result from the live demo session."
    ), align="C")

    # ======================================================================
    # TABLE OF CONTENTS (placeholder - we'll rebuild after all pages)
    # ======================================================================
    pdf.add_page()
    toc_page = pdf.page_no()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*MS_BLUE)
    pdf.cell(0, 12, "Table of Contents", align="L", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_draw_color(*MS_BLUE)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    # We'll store the Y position and come back to fill TOC at the end
    toc_y_start = pdf.get_y()

    # Reserve space (we'll overwrite)
    toc_items_placeholder = [
        ("1. Executive Summary", "3"),
        ("2. Phase 1 - Create Logic App in Azure", "4"),
        ("3. Phase 2 - Build Workflow in Designer", "6"),
        ("4. Phase 3 - ADO Service Hooks", "11"),
        ("5. Phase 4 - E2E Test Results", "13"),
        ("6. Troubleshooting Summary", "15"),
        ("7. Workflow JSON Reference", "16"),
    ]

    for title, pg in toc_items_placeholder:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*DARK_TEXT)
        tw = pdf.get_string_width(title)
        pw = pdf.get_string_width(pg)
        dots_w = 190 - tw - pw - 4
        num_dots = int(dots_w / pdf.get_string_width("."))
        dots = "." * max(num_dots, 3)
        pdf.cell(tw + 2, 8, title)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(dots_w, 8, dots)
        pdf.set_text_color(*DARK_TEXT)
        pdf.cell(pw + 2, 8, pg, align="R", new_x="LMARGIN", new_y="NEXT")

    # ======================================================================
    # SECTION 1: EXECUTIVE SUMMARY
    # ======================================================================
    pdf.add_page()
    pdf.section_title("1", "Executive Summary")

    pdf.sub_heading("What This Demo Shows")
    pdf.body_text(
        "A complete, production-ready integration between GitHub Advanced Security for "
        "Azure DevOps (GHAzDO) and Azure DevOps Boards, built entirely in the Azure Logic "
        "App Designer -- no code deployment, no IDE required. The Logic App automatically "
        "creates work items when security alerts fire and closes them when alerts are resolved."
    )

    pdf.sub_heading("Architecture Flow")
    pdf.code_block([
        "ADO Repository (with GHAzDO enabled)",
        "    |",
        "    v",
        "GHAzDO Scanner (code, secrets, dependencies)",
        "    |",
        "    v",
        "ADO Service Hooks (alert.created + alert.stateChanged)",
        "    |   POST webhook",
        "    v",
        "Azure Logic App (Consumption plan)",
        "    |   - Parse 8 fields from payload",
        "    |   - Compute title, tags, description",
        "    |   - Deduplicate via WIQL query",
        "    |   - Create or Close work item via ADO REST API",
        "    v",
        "ADO Boards (Work Items with full metadata + auto-lifecycle)",
    ])

    pdf.sub_heading("Key Outcomes Demonstrated")
    pdf.bold_bullet("Auto-create", "New work item on every GHAzDO alert with title, description, tags, priority")
    pdf.bold_bullet("Auto-close", "Work item set to Done when alert is resolved/fixed")
    pdf.bold_bullet("Deduplication", "WIQL tag query prevents duplicate work items from webhook retries")
    pdf.bold_bullet("Priority mapping", "critical/high -> P1, medium -> P2, low -> P3")
    pdf.bold_bullet("Rich metadata", "HTML description table with alert type, severity, repo, file, line, link")
    pdf.bold_bullet("Tag strategy", "GHAzDO;{alertType};{severity};GHAzDO-{repo}-{alertId} for traceability")

    # ======================================================================
    # SECTION 2: PHASE 1 - CREATE LOGIC APP
    # ======================================================================
    pdf.add_page()
    pdf.section_title("2", "Phase 1 - Create Logic App in Azure")

    pdf.sub_heading("Step 1: Navigate to Azure Portal")
    pdf.body_text(
        "Open portal.azure.com and search for 'Logic App'. Click 'Create' to open the "
        "creation form."
    )

    pdf.sub_heading("Step 2: Configure Logic App Settings")
    pdf.body_text("Fill in the creation form with these values:")
    pdf.ln(1)

    widths = [55, 125]
    pdf.table_row(["Setting", "Value"], widths, bold=True, fill=True)
    settings = [
        ("Subscription", "Visual Studio Enterprise (or your sub)"),
        ("Resource Group", "rg-ghas-ado-learfield"),
        ("Logic App Name", "la-ghas-ado-learfield"),
        ("Region", "East US"),
        ("Plan Type", "Consumption"),
        ("Log Analytics", "Off (for demo)"),
    ]
    for s, v in settings:
        pdf.table_row([s, v], widths)

    pdf.ln(3)
    pdf.add_screenshot("01-create-logic-app-form.png",
                       "Figure 2.1: Logic App creation form in Azure Portal")

    pdf.check_space(80)
    pdf.sub_heading("Step 3: Deployment Completes")
    pdf.body_text(
        "After clicking 'Review + Create' then 'Create', Azure provisions the Logic App. "
        "Deployment typically completes in 30-60 seconds."
    )
    pdf.add_screenshot("02-deployment-complete.png",
                       "Figure 2.2: Deployment succeeded notification")

    # ======================================================================
    # SECTION 3: PHASE 2 - BUILD WORKFLOW IN DESIGNER
    # ======================================================================
    pdf.add_page()
    pdf.section_title("3", "Phase 2 - Build Workflow in Designer")

    pdf.body_text(
        "The entire workflow is built in the Logic App Designer using only Compose actions "
        "and HTTP actions -- no connectors, no custom code. The workflow has 21 total "
        "components organized into three layers:"
    )
    pdf.bullet("Layer 1: HTTP Trigger (1 component)")
    pdf.bullet("Layer 2: Field Extractors - 8 Compose actions to parse the incoming payload")
    pdf.bullet("Layer 3: Computed Fields - 5 Compose actions for title, tags, description, etc.")
    pdf.bullet("Layer 4: Condition + HTTP actions for create/close logic (7 components)")

    # -- Trigger --
    pdf.sub_heading("3.1 HTTP Request Trigger")
    pdf.body_text(
        "Start with a blank Logic App and add 'When a HTTP request is received' as the "
        "trigger. Leave the JSON schema empty -- we parse dynamically using expressions."
    )
    pdf.add_screenshot("03-trigger-added.png",
                       "Figure 3.1: HTTP trigger configured (no schema)")

    # -- 8 Extractors --
    pdf.check_space(40)
    pdf.sub_heading("3.2 Field Extractors (8 Compose Actions)")
    pdf.body_text(
        "Each Compose action extracts one field from the webhook payload using Logic App "
        "expressions. All 8 run in parallel after the trigger."
    )
    pdf.ln(1)

    widths_expr = [45, 145]
    pdf.table_row(["Compose Action", "Expression"], widths_expr, bold=True, fill=True)
    extractors = [
        ("Compose_EventType", "@triggerBody()?['eventType']"),
        ("Compose_AlertType", "@coalesce(triggerBody()?['resource']?['alertType'], 'unknown')"),
        ("Compose_AlertId", "@coalesce(triggerBody()?['resource']?['alertId'], ...?['id'], 0)"),
        ("Compose_RepoName", "@coalesce(triggerBody()?['resource']?['repository']?['name'], ...)"),
        ("Compose_AlertUrl", "@coalesce(triggerBody()?['resource']?['link'], ...?['url'], '')"),
        ("Compose_Severity", "@toLower(coalesce(triggerBody()?['resource']?['severity'], 'medium'))"),
        ("Compose_FilePath", "@coalesce(triggerBody()?['resource']?['location']?['file'], ...)"),
        ("Compose_LineNumber", "@coalesce(triggerBody()?['resource']?['location']?['line'], 'N/A')"),
    ]
    for name, expr in extractors:
        pdf.table_row([name, expr], widths_expr)

    pdf.ln(2)
    pdf.add_screenshot("04-eight-extractors-complete.png",
                       "Figure 3.2: All 8 field extractor Compose actions on the canvas")

    # -- Computed Fields --
    pdf.check_space(40)
    pdf.sub_heading("3.3 Computed Fields (5 Compose Actions)")
    pdf.body_text(
        "These Compose actions depend on the extractors above and compute derived values "
        "for the work item."
    )

    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Compose_GhasTag", new_x="LMARGIN", new_y="NEXT")
    pdf.code_block([
        "@concat('GHAzDO-', outputs('Compose_RepoName'),",
        "        '-', string(outputs('Compose_AlertId')))",
    ])

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Compose_Title (conditional per alert type)", new_x="LMARGIN", new_y="NEXT")
    pdf.code_block([
        "@if(equals(outputs('Compose_AlertType'), 'secret'),",
        "  concat('[GHAzDO-Secret] ', ...?['secretType']),",
        "  if(equals(..., 'code'),",
        "    concat('[GHAzDO-CodeScan] ', ...?['title']),",
        "    if(equals(..., 'dependency'),",
        "      concat('[GHAzDO-Dependency] ', ...?['advisoryTitle']),",
        "      concat('[GHAzDO-Alert] ', ...?['title']))))",
    ], font_size=7)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Compose_Tags", new_x="LMARGIN", new_y="NEXT")
    pdf.code_block([
        "@concat('GHAzDO;', outputs('Compose_AlertType'), ';',",
        "        outputs('Compose_Severity'), ';',",
        "        outputs('Compose_GhasTag'))",
    ])

    pdf.check_space(60)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Compose_Description (HTML table)", new_x="LMARGIN", new_y="NEXT")
    pdf.code_block([
        "@concat('<h3>GHAzDO Security Alert</h3>',",
        "  '<table border=1 cellpadding=5>',",
        "  '<tr><td><b>Alert Type</b></td><td>', outputs('Compose_AlertType'), '</td></tr>',",
        "  '<tr><td><b>Severity</b></td><td>', outputs('Compose_Severity'), '</td></tr>',",
        "  '<tr><td><b>Repository</b></td><td>', outputs('Compose_RepoName'), '</td></tr>',",
        "  '<tr><td><b>File</b></td><td>', outputs('Compose_FilePath'), '</td></tr>',",
        "  '<tr><td><b>Line</b></td><td>', outputs('Compose_LineNumber'), '</td></tr>',",
        "  '<tr><td><b>Alert ID</b></td><td>', outputs('Compose_AlertId'), '</td></tr>',",
        "  '<tr><td><b>Tag</b></td><td>', outputs('Compose_GhasTag'), '</td></tr>',",
        "  '</table>',",
        "  '<p><a href=...AlertUrl...>View Alert in Azure DevOps</a></p>')",
    ], font_size=7)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Compose_IsCreateEvent", new_x="LMARGIN", new_y="NEXT")
    pdf.code_block([
        "@or(equals(outputs('Compose_EventType'),",
        "           'advancedsecurity.alert.created'),",
        "    contains(string(outputs('Compose_EventType')), 'created'))",
    ])

    pdf.check_space(80)
    pdf.add_screenshot("05-all-compose-actions.png",
                       "Figure 3.3: All 13 Compose actions visible on the designer canvas")

    # -- Full Workflow --
    pdf.check_space(40)
    pdf.sub_heading("3.4 Condition and HTTP Actions (7 Components)")
    pdf.body_text(
        "The condition checks Compose_IsCreateEvent. The True branch queries for existing "
        "work items (deduplication) then creates a new one. The False branch finds and "
        "closes the matching work item."
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "True Branch (Alert Created):", new_x="LMARGIN", new_y="NEXT")
    pdf.bullet("HTTP_QueryExistingWorkItem - WIQL POST to check for duplicates")
    pdf.bullet("Condition_NoExistingWorkItem - length(workItems) == 0")
    pdf.bullet("HTTP_CreateWorkItem - PATCH to create work item with JSON-patch body")

    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "False Branch (Alert State Changed / Resolved):", new_x="LMARGIN", new_y="NEXT")
    pdf.bullet("HTTP_FindWorkItemToClose - WIQL POST to find open work items with tag")
    pdf.bullet("Condition_FoundWorkItemToClose - length(workItems) > 0")
    pdf.bullet("HTTP_CloseWorkItem - PATCH to set State=Done + History comment")

    pdf.ln(2)
    pdf.add_screenshot("06-all-21-components-complete.png",
                       "Figure 3.4: Complete workflow with all 21 components on the designer")

    # -- Save & Webhook URL --
    pdf.check_space(40)
    pdf.sub_heading("3.5 Save and Obtain Webhook URL")
    pdf.body_text(
        "Click Save in the designer toolbar. After saving, the HTTP trigger generates "
        "a webhook URL containing a SAS token. This URL is used in ADO Service Hooks."
    )

    pdf.add_screenshot("07-workflow-saved-success.png",
                       "Figure 3.5: Workflow saved successfully")

    pdf.check_space(80)
    pdf.add_screenshot("08-webhook-url-revealed.png",
                       "Figure 3.6: Webhook URL revealed after save (contains SAS token)")

    # ======================================================================
    # SECTION 4: PHASE 3 - ADO SERVICE HOOKS
    # ======================================================================
    pdf.add_page()
    pdf.section_title("4", "Phase 3 - ADO Service Hooks")

    pdf.body_text(
        "Azure DevOps Service Hooks send HTTP POST requests to the Logic App webhook URL "
        "whenever GHAzDO events occur. We configure 4 hooks total to cover all alert types "
        "and lifecycle events."
    )

    pdf.sub_heading("4.1 Service Hook 1: Code Scanning Alert Created")
    pdf.body_text(
        "Navigate to Project Settings -> Service Hooks -> Create Subscription. Select "
        "'Advanced Security: code scanning alert created' and paste the Logic App webhook URL."
    )
    pdf.add_screenshot("09-service-hook-1-url.png",
                       "Figure 4.1: Service Hook configuration with webhook URL")

    pdf.check_space(80)
    pdf.body_text(
        "Click 'Test' to send a sample payload. The Logic App should return HTTP 200."
    )
    pdf.add_screenshot("10-service-hook-1-test-success.png",
                       "Figure 4.2: Service Hook 1 test succeeded (HTTP 200)")

    # -- Hook 2 --
    pdf.check_space(40)
    pdf.sub_heading("4.2 Service Hook 2: Code Scanning Alert State Changed")
    pdf.body_text(
        "Create a second Service Hook for 'Advanced Security: code scanning alert state "
        "changed'. This fires when an alert is resolved/fixed, triggering the auto-close logic."
    )
    pdf.add_screenshot("11-service-hook-2-test-success.png",
                       "Figure 4.3: Service Hook 2 test succeeded")

    # -- All 4 hooks --
    pdf.check_space(40)
    pdf.sub_heading("4.3 Complete Service Hook Configuration")
    pdf.body_text(
        "Repeat for dependency and secret scanning events. The full set of 4 hooks:"
    )
    pdf.ln(1)

    widths_hooks = [10, 80, 80]
    pdf.table_row(["#", "Event Type", "Purpose"], widths_hooks, bold=True, fill=True)
    hooks = [
        ("1", "Code scanning alert created", "Create work item for code alerts"),
        ("2", "Code scanning alert state changed", "Close work item when code alert resolved"),
        ("3", "Dependency alert created", "Create work item for dependency alerts"),
        ("4", "Dependency alert state changed", "Close work item when dep alert resolved"),
    ]
    for num, evt, purpose in hooks:
        pdf.table_row([num, evt, purpose], widths_hooks)

    pdf.ln(3)
    pdf.add_screenshot("12-all-four-service-hooks.png",
                       "Figure 4.4: All 4 service hooks configured in ADO")

    # ======================================================================
    # SECTION 5: PHASE 4 - E2E TEST RESULTS
    # ======================================================================
    pdf.add_page()
    pdf.section_title("5", "Phase 4 - E2E Test Results")

    pdf.sub_heading("5.1 Alert Created -> Work Item Auto-Created")
    pdf.body_text(
        "When a GHAzDO alert fires (e.g., code scanning detects a vulnerability), the "
        "service hook sends the payload to the Logic App. The Logic App:"
    )
    pdf.bullet("Parses 8 fields from the webhook payload")
    pdf.bullet("Computes title with alert-type prefix (e.g., [GHAzDO-CodeScan])")
    pdf.bullet("Generates HTML description table with all metadata")
    pdf.bullet("Builds unique tag: GHAzDO-{repo}-{alertId}")
    pdf.bullet("Queries WIQL to check for existing work item with that tag")
    pdf.bullet("If none exists, creates a new work item via ADO REST API")
    pdf.bullet("Sets priority based on severity mapping")

    pdf.sub_heading("5.2 Alert Resolved -> Work Item Auto-Closed")
    pdf.body_text(
        "When the alert state changes to fixed/resolved, the service hook fires the "
        "state-changed event. The Logic App:"
    )
    pdf.bullet("Detects this is NOT a create event (IsCreateEvent = false)")
    pdf.bullet("Takes the False branch of the condition")
    pdf.bullet("Queries WIQL for open work items with matching GHAzDO tag")
    pdf.bullet("If found, PATCHes the work item: State -> Done")
    pdf.bullet("Adds history comment: 'Auto-closed: GHAzDO alert resolved/fixed.'")

    pdf.sub_heading("5.3 Run History")
    pdf.body_text(
        "The Logic App run history shows the complete execution trail. In our demo "
        "session, we see 2 succeeded runs and 5 failed runs (from troubleshooting). "
        "The final runs demonstrate both create and close paths working correctly."
    )
    pdf.add_screenshot("13-run-history-succeeded.png",
                       "Figure 5.1: Logic App run history - 2 succeeded, 5 failed (troubleshooting)")

    pdf.check_space(40)
    pdf.sub_heading("5.4 Work Item Created in ADO Boards")
    pdf.body_text(
        "The created work item appears in ADO Boards with full metadata, tags, priority, "
        "and HTML description. After the alert was resolved, the work item was automatically "
        "set to Done state."
    )
    pdf.add_screenshot("14-workitem-created-done.png",
                       "Figure 5.2: Work Item #14 in ADO Boards - State: Done (auto-closed)")

    # ======================================================================
    # SECTION 6: TROUBLESHOOTING SUMMARY
    # ======================================================================
    pdf.add_page()
    pdf.section_title("6", "Troubleshooting Summary")

    pdf.body_text(
        "During the live demo session, 4 issues were encountered and resolved. "
        "These are common pitfalls when building GHAzDO integrations."
    )
    pdf.ln(2)

    # Issue 1
    pdf.sub_heading("Issue 1: Push Protection Blocking Test Pushes")
    pdf.set_fill_color(*CODE_BG)
    widths_ts = [35, 155]
    pdf.table_row(["Symptom", "Git push rejected by GHAzDO push protection"], widths_ts, fill=True)
    pdf.table_row(["Root Cause", "GHAzDO blocks commits containing known secret patterns"], widths_ts)
    pdf.table_row(["Resolution", "Used simulated payloads via Service Hook 'Test' button instead"], widths_ts)

    pdf.ln(3)

    # Issue 2
    pdf.sub_heading("Issue 2: PAT Base64 Corruption")
    widths_ts = [35, 155]
    pdf.table_row(["Symptom", "ADO API returns 401 Unauthorized"], widths_ts, fill=True)
    pdf.table_row(["Root Cause", "PAT not properly base64-encoded in Authorization header"], widths_ts)
    pdf.table_row(["Resolution", "Used base64(concat(':', parameters('adoPat'))) expression"], widths_ts)

    pdf.ln(3)

    # Issue 3
    pdf.sub_heading("Issue 3: String Body vs JSON Body")
    widths_ts = [35, 155]
    pdf.table_row(["Symptom", "ADO API returns 400 Bad Request on WIQL query"], widths_ts, fill=True)
    pdf.table_row(["Root Cause", "HTTP action sent body as string instead of JSON object"], widths_ts)
    pdf.table_row(["Resolution", "Wrapped body with json() function or used proper JSON input mode"], widths_ts)

    pdf.ln(3)

    # Issue 4
    pdf.sub_heading("Issue 4: HTML Quotes Breaking JSON")
    widths_ts = [35, 155]
    pdf.table_row(["Symptom", "Workflow save fails or API returns malformed JSON error"], widths_ts, fill=True)
    pdf.table_row(["Root Cause", "Double quotes in HTML description broke JSON serialization"], widths_ts)
    pdf.table_row(["Resolution", "Removed double quotes from Description HTML; used single-quoted attrs"], widths_ts)

    # ======================================================================
    # SECTION 7: WORKFLOW JSON REFERENCE
    # ======================================================================
    pdf.add_page()
    pdf.section_title("7", "Workflow JSON Reference")

    pdf.sub_heading("7.1 All Expressions Quick Reference")
    pdf.ln(1)
    widths_ref = [50, 140]
    pdf.table_row(["Field", "Expression"], widths_ref, bold=True, fill=True)
    all_exprs = [
        ("EventType", "@triggerBody()?['eventType']"),
        ("AlertType", "@coalesce(...?['alertType'], 'unknown')"),
        ("AlertId", "@coalesce(...?['alertId'], ...?['id'], 0)"),
        ("RepoName", "@coalesce(...?['repository']?['name'], 'unknown-repo')"),
        ("AlertUrl", "@coalesce(...?['link'], ...?['url'], '')"),
        ("Severity", "@toLower(coalesce(...?['severity'], 'medium'))"),
        ("FilePath", "@coalesce(...?['location']?['file'], ...?['path'], 'N/A')"),
        ("LineNumber", "@coalesce(...?['location']?['line'], 'N/A')"),
        ("GhasTag", "@concat('GHAzDO-', RepoName, '-', string(AlertId))"),
        ("Tags", "@concat('GHAzDO;', AlertType, ';', Severity, ';', GhasTag)"),
        ("IsCreateEvent", "@or(equals(EventType, '...created'), contains(...))"),
    ]
    for field, expr in all_exprs:
        pdf.table_row([field, expr], widths_ref)

    pdf.ln(4)
    pdf.sub_heading("7.2 Tag Strategy")
    pdf.body_text("Each work item receives a multi-part tag string for filtering and deduplication:")
    pdf.code_block([
        "Format: GHAzDO;{alertType};{severity};GHAzDO-{repoName}-{alertId}",
        "",
        "Example: GHAzDO;code;high;GHAzDO-my-repo-42",
        "",
        "Components:",
        "  - 'GHAzDO'           : Global identifier for all GHAzDO work items",
        "  - alertType           : code | secret | dependency | unknown",
        "  - severity            : critical | high | medium | low",
        "  - GHAzDO-repo-id     : Unique tag for deduplication (WIQL queries)",
    ])

    pdf.check_space(60)
    pdf.sub_heading("7.3 Priority Mapping")
    pdf.ln(1)
    widths_pri = [50, 40, 80]
    pdf.table_row(["Severity", "Priority", "Logic"], widths_pri, bold=True, fill=True)
    pdf.table_row(["critical", "1 (Highest)", "severity == critical OR high"], widths_pri)
    pdf.table_row(["high", "1 (Highest)", "severity == critical OR high"], widths_pri)
    pdf.table_row(["medium", "2", "severity == medium"], widths_pri)
    pdf.table_row(["low", "3", "severity == low (default)"], widths_pri)

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, "Priority Expression:", new_x="LMARGIN", new_y="NEXT")
    pdf.code_block([
        "@if(or(equals(outputs('Compose_Severity'),'critical'),",
        "       equals(outputs('Compose_Severity'),'high')),",
        "   1,",
        "   if(equals(outputs('Compose_Severity'),'medium'), 2, 3))",
    ])

    pdf.check_space(60)
    pdf.sub_heading("7.4 ADO REST API Endpoints Used")
    pdf.ln(1)
    widths_api = [60, 25, 105]
    pdf.table_row(["Endpoint", "Method", "Purpose"], widths_api, bold=True, fill=True)
    apis = [
        ("/_apis/wit/wiql?api-version=7.1", "POST", "Query work items (deduplication + find-to-close)"),
        ("/_apis/wit/workitems/$Issue", "PATCH", "Create new work item (JSON-patch format)"),
        ("/_apis/wit/workitems/{id}", "PATCH", "Update work item state to Done"),
    ]
    for ep, method, purpose in apis:
        pdf.table_row([ep, method, purpose], widths_api)

    pdf.ln(4)
    pdf.sub_heading("7.5 Authentication")
    pdf.body_text("All ADO API calls use Basic auth with a Personal Access Token (PAT):")
    pdf.code_block([
        "Authorization: Basic @{base64(concat(':', parameters('adoPat')))}",
        "",
        "Required PAT Scope: Work Items (Read & Write)",
    ])

    pdf.ln(4)
    pdf.sub_heading("7.6 Component Summary")
    pdf.ln(1)
    widths_comp = [15, 60, 55, 60]
    pdf.table_row(["#", "Component", "Type", "Layer"], widths_comp, bold=True, fill=True)
    components = [
        ("1", "When_a_GHAzDO_alert_received", "Request Trigger", "Trigger"),
        ("2", "Compose_EventType", "Compose", "Field Extractor"),
        ("3", "Compose_AlertType", "Compose", "Field Extractor"),
        ("4", "Compose_AlertId", "Compose", "Field Extractor"),
        ("5", "Compose_RepoName", "Compose", "Field Extractor"),
        ("6", "Compose_AlertUrl", "Compose", "Field Extractor"),
        ("7", "Compose_Severity", "Compose", "Field Extractor"),
        ("8", "Compose_FilePath", "Compose", "Field Extractor"),
        ("9", "Compose_LineNumber", "Compose", "Field Extractor"),
        ("10", "Compose_GhasTag", "Compose", "Computed Field"),
        ("11", "Compose_Title", "Compose", "Computed Field"),
        ("12", "Compose_Tags", "Compose", "Computed Field"),
        ("13", "Compose_Description", "Compose", "Computed Field"),
        ("14", "Compose_IsCreateEvent", "Compose", "Computed Field"),
        ("15", "Condition_IsCreateAction", "If", "Router"),
        ("16", "HTTP_QueryExistingWorkItem", "HTTP", "True Branch"),
        ("17", "Condition_NoExistingWorkItem", "If", "True Branch"),
        ("18", "HTTP_CreateWorkItem", "HTTP", "True Branch"),
        ("19", "HTTP_FindWorkItemToClose", "HTTP", "False Branch"),
        ("20", "Condition_FoundWorkItemToClose", "If", "False Branch"),
        ("21", "HTTP_CloseWorkItem", "HTTP", "False Branch"),
    ]
    for num, name, ctype, layer in components:
        pdf.table_row([num, name, ctype, layer], widths_comp)

    # ======================================================================
    # OUTPUT
    # ======================================================================
    os.makedirs(DOCS_DIR, exist_ok=True)
    pdf.output(OUTPUT_PDF)
    print(f"PDF generated: {OUTPUT_PDF}")
    print(f"Total pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()
