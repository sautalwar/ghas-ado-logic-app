#!/usr/bin/env python3
"""
Generate a comprehensive PDF guide for pushing secrets to ADO.
Uses fpdf2 library to create a professional step-by-step guide
with screenshots and detailed explanations.
"""

import os
import sys
from pathlib import Path
from fpdf import FPDF

# Configuration
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
SCREENSHOTS_DIR = REPO_ROOT / "screenshots" / "demo5"
OUTPUT_PDF = REPO_ROOT / "docs" / "ADO-Secret-Push-Step-By-Step.pdf"

# Ensure output directory exists
OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

class SecretPushGuide(FPDF):
    """Custom PDF class for the secret push guide."""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.page_num = 0
        self.title_text = "How Pushing a Secret to ADO Triggers Automatic Work Item Creation"
    
    def header(self):
        """Add header to each page."""
        if self.page_no() > 1:
            self.set_font("Arial", "", 9)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f"Page {self.page_no()}", align="R", border=0)
            self.ln(5)
    
    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, "Confidential - Prepared for Customer Demo", align="C", border=0)
    
    def add_heading(self, text, level=1):
        """Add a heading with proper formatting."""
        if level == 1:
            self.set_font("Arial", "B", 20)
            self.set_text_color(0, 120, 212)  # Microsoft blue
            self.ln(5)
            self.cell(0, 12, text, ln=True, align="L")
            self.set_text_color(0, 0, 0)
            self.ln(3)
        elif level == 2:
            self.set_font("Arial", "B", 14)
            self.set_text_color(0, 120, 212)
            self.ln(4)
            self.cell(0, 10, text, ln=True, align="L")
            self.set_text_color(0, 0, 0)
            self.ln(2)
        else:
            self.set_font("Arial", "B", 11)
            self.set_text_color(0, 120, 212)
            self.ln(3)
            self.cell(0, 8, text, ln=True, align="L")
            self.set_text_color(0, 0, 0)
    
    def add_paragraph(self, text):
        """Add a paragraph with word wrapping."""
        self.set_font("Arial", "", 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, text, align="L")
        self.ln(2)
    
    def add_bullet_list(self, items):
        """Add a bulleted list."""
        self.set_font("Arial", "", 10)
        for item in items:
            self.ln(2)
            self.cell(5, 5, "-")
            self.set_x(self.get_x() + 3)
            self.multi_cell(0, 5, item)
    
    def add_code_block(self, code):
        """Add a code block with monospace font."""
        self.set_font("Courier", "", 9)
        self.set_fill_color(240, 240, 240)
        self.ln(2)
        for line in code.split("\n"):
            if line.strip():
                self.cell(0, 5, line, border=1, fill=True, ln=True)
        self.ln(2)
        self.set_font("Arial", "", 10)
    
    def add_screenshot(self, filename, width=160):
        """Add a screenshot from the demo5 directory."""
        filepath = SCREENSHOTS_DIR / filename
        if filepath.exists():
            try:
                self.ln(3)
                self.image(str(filepath), w=width)
                self.ln(2)
                return True
            except Exception as e:
                print(f"Warning: Could not add screenshot {filename}: {e}")
                self.ln(2)
                self.set_font("Arial", "I", 9)
                self.set_text_color(128, 128, 128)
                self.cell(0, 5, f"[Screenshot: {filename} - not available]", ln=True)
                self.set_text_color(0, 0, 0)
                self.ln(1)
                return False
        else:
            self.ln(2)
            self.set_font("Arial", "I", 9)
            self.set_text_color(128, 128, 128)
            self.cell(0, 5, f"[Screenshot: {filename} - file not found]", ln=True)
            self.set_text_color(0, 0, 0)
            self.ln(1)
            return False
    
    def add_page_break(self):
        """Add a page break."""
        self.add_page()


def create_title_page(pdf):
    """Create the title page."""
    pdf.add_page()
    
    # Add some vertical space
    pdf.ln(40)
    
    # Main title
    pdf.set_font("Arial", "B", 28)
    pdf.set_text_color(0, 120, 212)
    pdf.multi_cell(0, 12, "How Pushing a Secret to ADO Triggers Automatic Work Item Creation", align="C")
    
    pdf.ln(10)
    
    # Subtitle
    pdf.set_font("Arial", "", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 8, "Step-by-Step Guide for Azure DevOps + GHAzDO + Logic App Integration", align="C")
    
    pdf.ln(20)
    
    # Footer info
    pdf.set_font("Arial", "I", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 8, "Prepared for: Learfield/BrandSafway Customer Demo", align="C")
    
    pdf.ln(30)
    
    # Add a separator line
    pdf.set_draw_color(0, 120, 212)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())


def create_section_1(pdf):
    """Section 1: Overview."""
    pdf.add_page_break()
    pdf.add_heading("Section 1: Overview - What Happens When You Push a Secret", level=1)
    
    pdf.add_paragraph(
        "When a developer pushes code containing a secret to an Azure DevOps repository, "
        "a powerful automated workflow is triggered. This workflow ensures that security "
        "vulnerabilities are detected, tracked, and resolved quickly. Here is the complete flow:"
    )
    
    items = [
        "Developer pushes code containing a secret (like an API key, password, or connection string) to an Azure DevOps repository",
        "GitHub Advanced Security for Azure DevOps (GHAzDO) automatically scans every push for 100+ secret patterns",
        "When GHAzDO detects a secret, it creates an 'Advanced Security alert'",
        "An ADO Service Hook catches this alert event and sends it as a webhook to the Logic App",
        "The Logic App processes the webhook and creates a Work Item in ADO Boards with all the details",
        "When the secret is removed/resolved, GHAzDO changes the alert state, triggering another webhook",
        "The Logic App automatically closes the Work Item and adds a comment"
    ]
    
    pdf.add_bullet_list(items)
    
    pdf.ln(5)
    pdf.add_paragraph(
        "This entire process is automated and requires no manual intervention. "
        "The security team is immediately notified through ADO Work Items, "
        "ensuring that secrets are remediated quickly."
    )


def create_section_2(pdf):
    """Section 2: Step 1 - Create the Secret File."""
    pdf.add_page_break()
    pdf.add_heading("Section 2: Step 1 - Create the Secret File", level=1)
    
    pdf.add_paragraph(
        "In this demonstration, we create a file called test-secrets/demo5-config.env "
        "containing sensitive configuration data like database URLs and storage keys:"
    )
    
    pdf.ln(2)
    code = """# Demo5 Configuration
DATABASE_URL=postgres://admin:SuperSecret123!@db.example.com:5432/production
AZURE_STORAGE_KEY=DefaultEndpointsProtocol=https;AccountName=demo5storage;AccountKey=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz==;EndpointSuffix=core.windows.net"""
    pdf.add_code_block(code)
    
    pdf.add_paragraph(
        "There are THREE ways to push this file to your repository. "
        "Choose the method that works best for your workflow:"
    )
    
    # Method A
    pdf.add_heading("Method A: Via ADO Web UI (Easiest for Demo)", level=3)
    items_a = [
        "Navigate to https://dev.azure.com/{org}/{project}/_git/{repo}",
        "Click on the folder where you want to add the file (e.g., test-secrets/)",
        "Click the '...' menu next to the folder name, then 'New' > 'File'",
        "Name the file demo5-config.env",
        "Paste the secret content into the editor",
        "Click 'Commit' with a message like 'Add demo5 test configuration'"
    ]
    pdf.add_bullet_list(items_a)
    
    # Method B
    pdf.add_heading("Method B: Via ADO REST API (What We Used)", level=3)
    pdf.add_paragraph(
        "The REST API method provides programmatic control and is useful for automation:"
    )
    items_b = [
        "First get the latest commit ID from refs/heads/main using GET /_apis/git/repositories/{repo}/refs?api-version=7.1",
        "Then POST to /_apis/git/repositories/{repo}/pushes?api-version=7.1 with the push payload",
        "The body includes: refUpdates (with branch name and old commit), commits (with comment and changes containing file path and base64-encoded content)",
        "Response includes the push ID and new commit ID"
    ]
    pdf.add_bullet_list(items_b)
    
    # Method C
    pdf.add_heading("Method C: Via Git Command Line", level=3)
    code_c = """git clone https://dev.azure.com/brandsafway1/_git/brandsafway_Engg
cd brandsafway_Engg
mkdir test-secrets
echo "DATABASE_URL=..." > test-secrets/demo5-config.env
git add test-secrets/demo5-config.env
git commit -m "Add demo5 configuration"
git push origin main"""
    pdf.add_code_block(code_c)
    
    pdf.add_paragraph(
        "Note: If Push Protection is enabled, GHAzDO may BLOCK the push entirely, "
        "preventing the secret from ever reaching the repo. In that case, you would need "
        "to remove the secret first or use the API simulation approach."
    )
    
    pdf.ln(3)
    pdf.add_paragraph("Screenshot showing the secret file in the ADO repository:")
    pdf.add_screenshot("19-secret-file-in-repo.png")


def create_section_3(pdf):
    """Section 3: Step 2 - GHAzDO Detects the Secret."""
    pdf.add_page_break()
    pdf.add_heading("Section 3: Step 2 - GHAzDO Detects the Secret", level=1)
    
    pdf.add_paragraph(
        "After the file is pushed to the repository, GitHub Advanced Security for Azure DevOps "
        "(GHAzDO) automatically scans the code for security vulnerabilities:"
    )
    
    items = [
        "GHAzDO runs automatically on every push - no pipeline or configuration needed",
        "It scans for 100+ secret patterns including AWS keys, Azure keys, database connection strings, API tokens, and more",
        "Detection typically happens within 1-5 minutes of the push",
        "The alert appears in the Repos > Advanced Security > Secrets tab",
        "Each alert includes: Alert ID, Alert Type (secret/code/dependency), Severity, File path, Line number, Secret type description"
    ]
    pdf.add_bullet_list(items)
    
    pdf.ln(3)
    pdf.add_paragraph("Screenshot showing the Advanced Security alerts dashboard:")
    pdf.add_screenshot("20-advanced-security-alerts.png")


def create_section_4(pdf):
    """Section 4: Step 3 - Service Hook Fires the Webhook."""
    pdf.add_page_break()
    pdf.add_heading("Section 4: Step 3 - Service Hook Fires the Webhook", level=1)
    
    pdf.add_paragraph(
        "ADO Service Hooks are configured to automatically send webhook notifications when "
        "GHAzDO detects or changes the status of security alerts:"
    )
    
    items = [
        "Service Hook 1: 'Advanced Security alert created' - fires when a NEW alert is detected",
        "Service Hook 2: 'Advanced Security alert state changed' - fires when an alert is resolved/dismissed",
        "Both hooks point to the Logic App webhook URL (prod-93.eastus.logic.azure.com)",
        "The hook sends a JSON payload containing all alert details to the Logic App",
        "Payload includes: eventType, resource (alertId, alertType, severity, repository, location, secretType, link), resourceContainers (project, account)"
    ]
    pdf.add_bullet_list(items)
    
    pdf.ln(3)
    pdf.add_paragraph("Screenshot showing all configured Service Hooks:")
    pdf.add_screenshot("17-all-service-hooks.png")
    
    pdf.ln(3)
    pdf.add_paragraph("Screenshots showing Service Hook trigger configuration and URL:")
    pdf.add_screenshot("11-service-hook-trigger.png", width=140)
    pdf.add_screenshot("12-service-hook-url.png", width=140)


def create_section_5(pdf):
    """Section 5: Step 4 - Logic App Processes the Webhook."""
    pdf.add_page_break()
    pdf.add_heading("Section 5: Step 4 - Logic App Processes the Webhook", level=1)
    
    pdf.add_paragraph(
        "The Logic App (ghazdo-to-ado.json) is the orchestration engine that receives the webhook "
        "and translates it into ADO Work Items. Here is how it works:"
    )
    
    items = [
        "HTTP Trigger receives the webhook payload from the Service Hook",
        "8 Compose actions extract fields: EventType, AlertType, AlertId, RepoName, AlertUrl, Severity, FilePath, LineNumber",
        "5 computed fields created: GhasTag (unique dedup tag), Title, Tags, Description (HTML table), IsCreateEvent",
        "Condition: Is this a 'created' event?",
        "  TRUE branch: Query ADO for existing work items with same tag, If none found, Create new Work Item with Title, Description, Tags, Priority",
        "  FALSE branch: Query ADO for open work items with same tag, If found, Close the work item (set State=Done) with auto-close comment"
    ]
    pdf.add_bullet_list(items)
    
    pdf.ln(3)
    pdf.add_paragraph("Screenshot showing the Logic App designer view:")
    pdf.add_screenshot("08-designer-view.png")
    
    pdf.ln(3)
    pdf.add_paragraph("Screenshot showing the JSON code view:")
    pdf.add_screenshot("06-code-view-deployed.png")


def create_section_6(pdf):
    """Section 6: Step 5 - Work Item Auto-Created."""
    pdf.add_page_break()
    pdf.add_heading("Section 6: Step 5 - Work Item Auto-Created", level=1)
    
    pdf.add_paragraph(
        "When the Logic App receives a 'created' event, it automatically creates a Work Item in ADO Boards "
        "with all the relevant details about the discovered secret:"
    )
    
    items = [
        "Title: '[GHAzDO-Secret] Azure Storage Account Key in demo5-config.env'",
        "State: 'To Do' (initial state - ready for the team to investigate)",
        "Tags: 'GHAzDO; secret; critical; GHAzDO-brandsafway_Engg-50'",
        "Priority: 1 (because severity is 'critical' - higher severity = higher priority)",
        "Description: HTML table with all alert details including secret type, file path, line number, and link to the alert",
        "The GhasTag (e.g., GHAzDO-brandsafway_Engg-50) prevents duplicate work items for the same alert"
    ]
    pdf.add_bullet_list(items)
    
    pdf.ln(3)
    pdf.add_paragraph("Screenshot showing the auto-created Work Item #15:")
    pdf.add_screenshot("21-workitem-created-and-closed.png")


def create_section_7(pdf):
    """Section 7: Step 6 - Auto-Close When Secret is Resolved."""
    pdf.add_page_break()
    pdf.add_heading("Section 7: Step 6 - Auto-Close When Secret is Resolved", level=1)
    
    pdf.add_paragraph(
        "When a developer removes the secret from the repository or dismisses the alert in GHAzDO, "
        "the automation continues to keep the Work Item in sync:"
    )
    
    items = [
        "GHAzDO detects that the secret has been removed and changes the alert state to 'resolved'",
        "The 'Advanced Security alert state changed' Service Hook fires with the state change event",
        "The Logic App receives the webhook and detects it is NOT a 'created' event",
        "It queries ADO for open work items with the matching GhasTag",
        "It PATCHES the work item: State = 'Done', adds comment 'Auto-closed: GHAzDO alert resolved/fixed.'",
        "In our demo, Work Item #15 transitioned from 'To Do' to 'Done' with the auto-close comment"
    ]
    pdf.add_bullet_list(items)


def create_section_8(pdf):
    """Section 8: Where to Add Custom Fields."""
    pdf.add_page_break()
    pdf.add_heading("Section 8: Where to Add Custom Fields", level=1)
    
    pdf.add_paragraph(
        "The Logic App template includes basic fields for all work items. However, customers can customize "
        "the work item by editing the JSON to add additional fields that match their organizational needs:"
    )
    
    pdf.add_heading("Current Fields (Included in Template):", level=3)
    items = [
        "System.Title - The alert title and secret type",
        "System.Description - HTML table with alert details",
        "System.Tags - Categorization tags",
        "Microsoft.VSTS.Common.Priority - Based on alert severity"
    ]
    pdf.add_bullet_list(items)
    
    pdf.add_heading("How to Add More Fields:", level=3)
    pdf.add_paragraph(
        "In the HTTP_CreateWorkItem action body, each field is a JSON Patch operation. "
        "Customers can ADD more fields by adding new patch operations like these examples:"
    )
    
    pdf.ln(2)
    code = """{ "op": "add", "path": "/fields/System.AssignedTo", "value": "user@company.com" }
{ "op": "add", "path": "/fields/System.AreaPath", "value": "Project\\\\Security" }
{ "op": "add", "path": "/fields/System.IterationPath", "value": "Project\\\\Sprint 1" }
{ "op": "add", "path": "/fields/Custom.SecurityCategory", "value": "Secret Exposure" }"""
    pdf.add_code_block(code)
    
    pdf.add_paragraph(
        "IMPORTANT: Custom fields must first be created in ADO Project Settings > Process > Work Item Types "
        "before you can use them in the Logic App JSON. Standard fields like System.AssignedTo are available "
        "on all work item types."
    )


def create_section_9(pdf):
    """Section 9: The JSON File to Give to Customers."""
    pdf.add_page_break()
    pdf.add_heading("Section 9: The JSON File to Give to Customers", level=1)
    
    pdf.add_paragraph(
        "The file ghazdo-to-ado.json (218 lines) contains the complete Logic App definition. "
        "Customers use this file to deploy the automation to their own environment."
    )
    
    pdf.add_heading("Key Parameters to Configure:", level=3)
    items = [
        "adoOrganization - The Azure DevOps organization name (e.g., 'brandsafway1')",
        "adoProject - The project name where work items will be created (e.g., 'brandsafway_Engg')",
        "adoPat - Personal Access Token with work item write permissions (stored as SecureString)",
        "workItemType - The type of work item to create (default: 'Issue', can be 'Bug', 'Task', etc.)"
    ]
    pdf.add_bullet_list(items)
    
    pdf.add_heading("Deployment Steps:", level=3)
    items_deploy = [
        "Copy the ghazdo-to-ado.json file",
        "Open Azure Logic Apps > Your Logic App > Code View",
        "Paste the entire JSON content",
        "Save and configure parameter values",
        "Configure Service Hooks in ADO Project Settings to point to the Logic App webhook URL"
    ]
    pdf.add_bullet_list(items_deploy)
    
    pdf.ln(3)
    pdf.add_paragraph("Screenshot showing the JSON code view with parameters:")
    pdf.add_screenshot("09-code-view-with-json.png")


def create_section_10(pdf):
    """Section 10: Troubleshooting Tips."""
    pdf.add_page_break()
    pdf.add_heading("Section 10: Troubleshooting Tips", level=1)
    
    pdf.add_paragraph(
        "This section provides solutions to common issues you might encounter when deploying "
        "or using the GHAzDO to ADO automation:"
    )
    
    pdf.add_heading("Issue 1: Push Protection Blocking Pushes", level=3)
    pdf.add_paragraph(
        "Problem: GHAzDO detects the secret before the push completes and blocks it entirely, "
        "preventing the secret from reaching the repository."
    )
    pdf.add_paragraph(
        "Solution: Use API simulation approach by pre-creating the alert in the demo, or dismiss "
        "the protection rule temporarily during the demonstration."
    )
    
    pdf.add_heading("Issue 2: PAT Corruption or Encoding Errors", level=3)
    pdf.add_paragraph(
        "Problem: The Personal Access Token causes authentication failures when creating work items."
    )
    pdf.add_paragraph(
        "Solution: Always decode and compare Base64-encoded values. Verify that the PAT has the correct "
        "scopes (Work Items read/write) and has not expired. Test the PAT with a simple REST API call first."
    )
    
    pdf.add_heading("Issue 3: 400 Invalid Patch Document Error", level=3)
    pdf.add_paragraph(
        "Problem: Work item creation fails with a '400 Invalid Patch Document' error."
    )
    pdf.add_paragraph(
        "Solution: Ensure the body is a valid JSON array (not a string). Verify all required fields "
        "are present. Check that field paths use correct ADO naming conventions."
    )
    
    pdf.add_heading("Issue 4: HTML Quotes Breaking JSON", level=3)
    pdf.add_paragraph(
        "Problem: HTML-formatted descriptions contain unescaped quotes that break the JSON structure."
    )
    pdf.add_paragraph(
        "Solution: Remove or escape <a href='...'>  tags with double quotes. Use HTML entities instead "
        "of raw quotes in the description field."
    )
    
    pdf.add_heading("Issue 5: Work Item Not Created", level=3)
    pdf.add_paragraph(
        "Problem: The webhook fires but no work item appears in ADO."
    )
    pdf.add_paragraph(
        "Solution: Check the Logic App run history for detailed error messages. Verify the Service Hook "
        "is sending data to the correct Logic App URL. Confirm the PAT has work item creation permissions."
    )


def main():
    """Generate the PDF guide."""
    print(f"Generating PDF guide at: {OUTPUT_PDF}")
    
    # Create PDF object
    pdf = SecretPushGuide()
    
    # Create title page
    print("Creating title page...")
    create_title_page(pdf)
    
    # Create sections
    print("Creating Section 1: Overview...")
    create_section_1(pdf)
    
    print("Creating Section 2: Create Secret File...")
    create_section_2(pdf)
    
    print("Creating Section 3: GHAzDO Detection...")
    create_section_3(pdf)
    
    print("Creating Section 4: Service Hook Webhook...")
    create_section_4(pdf)
    
    print("Creating Section 5: Logic App Processing...")
    create_section_5(pdf)
    
    print("Creating Section 6: Work Item Creation...")
    create_section_6(pdf)
    
    print("Creating Section 7: Auto-Close...")
    create_section_7(pdf)
    
    print("Creating Section 8: Custom Fields...")
    create_section_8(pdf)
    
    print("Creating Section 9: JSON File...")
    create_section_9(pdf)
    
    print("Creating Section 10: Troubleshooting...")
    create_section_10(pdf)
    
    # Save PDF
    try:
        pdf.output(str(OUTPUT_PDF))
        print(f"\nSuccess! PDF generated at: {OUTPUT_PDF}")
        print(f"File size: {OUTPUT_PDF.stat().st_size:,} bytes")
        return 0
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
