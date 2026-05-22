"""Generate PDF from customer reply to Michael Hubicka."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

OUTPUT = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                      "Customer_Reply_Michael_Hubicka.pdf")

BLUE = HexColor("#0078D4")
DARK = HexColor("#1B1B1B")
GRAY = HexColor("#505050")
LIGHT_GRAY = HexColor("#F5F5F5")
GREEN = HexColor("#107C10")
RED = HexColor("#D83B01")
WHITE = HexColor("#FFFFFF")

styles = getSampleStyleSheet()

title_style = ParagraphStyle("Title2", parent=styles["Title"],
    fontSize=18, textColor=BLUE, spaceAfter=6, alignment=TA_LEFT)
subtitle_style = ParagraphStyle("Sub", parent=styles["Normal"],
    fontSize=10, textColor=GRAY, spaceAfter=4)
heading_style = ParagraphStyle("H1", parent=styles["Heading1"],
    fontSize=14, textColor=BLUE, spaceBefore=16, spaceAfter=8)
subheading_style = ParagraphStyle("H2", parent=styles["Heading2"],
    fontSize=12, textColor=DARK, spaceBefore=12, spaceAfter=6)
body_style = ParagraphStyle("Body", parent=styles["Normal"],
    fontSize=10, textColor=DARK, leading=14, spaceAfter=4)
bold_body = ParagraphStyle("BoldBody", parent=body_style, fontName="Helvetica-Bold")
bullet_style = ParagraphStyle("Bullet", parent=body_style,
    leftIndent=20, bulletIndent=8, spaceBefore=2, spaceAfter=2)
numbered_style = ParagraphStyle("Numbered", parent=body_style,
    leftIndent=20, bulletIndent=8, spaceBefore=2, spaceAfter=2)
quote_style = ParagraphStyle("Quote", parent=body_style,
    leftIndent=20, rightIndent=20, fontName="Helvetica-Oblique",
    textColor=GRAY, borderColor=BLUE, borderWidth=0, borderPadding=4)

def hr():
    return HRFlowable(width="100%", thickness=1, color=HexColor("#DDDDDD"),
                      spaceBefore=8, spaceAfter=8)

def table_block(headers, rows, col_widths=None):
    data = [headers] + rows
    if not col_widths:
        col_widths = [3.2 * inch, 3.2 * inch]
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CCCCCC")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ])
    t = Table(data, colWidths=col_widths)
    t.setStyle(style)
    return t

def build():
    doc = SimpleDocTemplate(OUTPUT, pagesize=letter,
        topMargin=0.75*inch, bottomMargin=0.75*inch,
        leftMargin=0.75*inch, rightMargin=0.75*inch)
    story = []

    # Header
    story.append(Paragraph("Re: GHAzDO Testing Feedback", title_style))
    story.append(Paragraph("Here's What We Built, What We Learned, and What's Next", 
        ParagraphStyle("SubTitle", parent=body_style, fontSize=12, textColor=GRAY)))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>To:</b> michael.holder@learfield.com", subtitle_style))
    story.append(Paragraph("<b>CC:</b> Pupun Das, Saurabh Talwar", subtitle_style))
    story.append(Paragraph("<b>Subject:</b> Re: The GHAS testing feedback — you're right, and here's the simpler path", subtitle_style))
    story.append(hr())

    # Greeting
    story.append(Paragraph("Hi Michael,", body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Thank you for that clear feedback on the GHAS testing. You're absolutely right — and your "
        "message helped us realize we should give you two better paths forward instead of just one. "
        "Let me walk you through where we started, what we learned from you, and what we're suggesting now.",
        body_style))
    story.append(hr())

    # Section 1
    story.append(Paragraph("Section 1: What We Originally Built For You", heading_style))
    story.append(Paragraph(
        "We created that Logic App automation (<b>ghazdo-to-ado.json</b>) to solve the exact problem "
        "you described — the multi-step manual workflow that adds friction to your security response "
        "process. Here's what it does:", body_style))
    story.append(Spacer(1, 4))
    for b in [
        "<b>Automatically creates a work item</b> the moment a GHAzDO alert appears in your ADO project",
        "<b>Automatically closes the work item</b> when the alert is resolved",
        "<b>Bidirectionally links</b> everything, so your team sees the full context without extra clicks",
    ]:
        story.append(Paragraph(b, bullet_style, bulletText="•"))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        'We built it because that\'s the "lights-out" automation story — one thing happens upstream '
        "(an alert), and everything downstream flows automatically. No manual steps. Complete hands-off.",
        body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        'But you gave us crucial feedback: <b>"I do believe that simplifying the work item creation '
        'process would be most beneficial"</b> — and then you said the quiet part out loud: '
        '"Logic Apps add complexity your team shouldn\'t need to worry about." You\'re absolutely right. '
        "Maintaining another piece of infrastructure (Logic App, service hooks, error handling) is "
        "overhead you don't need if there's a simpler way.",
        body_style))
    story.append(hr())

    # Section 2
    story.append(Paragraph("Section 2: What We're Now Suggesting — Two Paths", heading_style))
    story.append(Paragraph(
        "Based on your feedback, we're proposing two options that both eliminate manual toil, "
        "but in different ways.", body_style))
    story.append(Spacer(1, 8))

    # Option A
    story.append(Paragraph("Option A: Native ADO Button (Instant Win, Zero Setup)", subheading_style))
    story.append(Paragraph(
        'Azure DevOps now ships with a native <b>"Add" / "Related Work" button</b> directly in the '
        "GHAzDO alerts page. This is exactly what you asked for: click a button to create a work item "
        "from the alert.", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>How it works:</b>", bold_body))
    for i, step in enumerate([
        "Open a GHAzDO alert in your ADO project",
        'Click <b>"Add"</b> in the alert details (Related Work section)',
        "Select your work item type (Bug, Issue, Task — your choice)",
        "ADO creates a new work item with alert details pre-populated and auto-links it bidirectionally",
    ], 1):
        story.append(Paragraph(f"{i}. {step}", numbered_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>What you get:</b>", bold_body))
    for b in [
        "<b>Zero setup</b> (it's already there)",
        "<b>Zero cost</b> (built into ADO)",
        "<b>Zero ongoing maintenance</b> (Microsoft manages it)",
        "<b>Instant availability</b> (use it today)",
    ]:
        story.append(Paragraph(b, bullet_style, bulletText="•"))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>How Option A eliminates your manual steps:</b>", bold_body))
    story.append(Spacer(1, 4))
    story.append(table_block(
        ["Your Current Manual Process", "With Native ADO Button"],
        [
            ["Scan to receive an alert", "✅ Same — alerts appear in GHAzDO"],
            ["Create a work item", "❌ Eliminated — click \"Add\" right from the alert"],
            ["Attach it to the alert", "❌ Eliminated — auto-linked bidirectionally"],
        ]
    ))
    story.append(Spacer(1, 12))

    # Option B
    story.append(Paragraph("Option B: Full Hands-Free Automation (Optional Upgrade)", subheading_style))
    story.append(Paragraph(
        "If your team decides you want <b>zero clicks</b> — fully automatic creation and closure "
        "without any manual intervention — we've simplified the Logic App deployment into a genuine "
        "one-click experience:", body_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>How it works:</b>", bold_body))
    for i, step in enumerate([
        'Click a single <b>"Deploy to Azure" button</b> (in our repo)',
        "Enter just <b>3 fields</b>: your ADO org name, project name, and a Personal Access Token",
        "<b>Done.</b> The Logic App deploys in ~5 minutes. From then on alerts automatically create "
        "work items, and resolved alerts automatically close them.",
    ], 1):
        story.append(Paragraph(f"{i}. {step}", numbered_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>What it costs:</b>", bold_body))
    for b in [
        "Setup time: ~5 minutes",
        "Monthly cost: ~$50–100 (Logic App hosting)",
        "Ongoing maintenance: Zero — Microsoft handles all updates",
    ]:
        story.append(Paragraph(b, bullet_style, bulletText="•"))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>How Option B eliminates your manual steps:</b>", bold_body))
    story.append(Spacer(1, 4))
    story.append(table_block(
        ["Your Current Manual Process", "With Full Automation"],
        [
            ["Scan to receive an alert", "❌ Eliminated — automatic"],
            ["Create a work item", "❌ Eliminated — automatic"],
            ["Attach it to the alert", "❌ Eliminated — auto-tagged and linked"],
            ["Bonus: Close work item when fixed", "❌ Eliminated — auto-closed when alert resolves"],
        ]
    ))
    story.append(hr())

    # Section 3
    story.append(Paragraph("Section 3: A Few Quick Environment Questions", heading_style))
    story.append(Paragraph(
        "To make sure everything works smoothly in your environment, could you help me confirm a few things?",
        body_style))
    story.append(Spacer(1, 4))
    questions = [
        "<b>What ADO process template are you using?</b> (Agile, Scrum, Basic, or CMMI?) — "
        "This affects how work items behave and what types are available.",
        '<b>Is "brandsafway1" still the correct ADO organization name?</b> '
        "I want to make sure we have the right details on file.",
        "<b>When you create work items from alerts, what type do you prefer?</b> "
        "(Bug, Issue, Task?) — This becomes your default.",
        "<b>Do you have an Azure subscription available?</b> "
        "(Just in case you decide to explore the full automation path later.)",
    ]
    for i, q in enumerate(questions, 1):
        story.append(Paragraph(f"{i}. {q}", numbered_style))
    story.append(hr())

    # Section 4
    story.append(Paragraph("Section 4: Next Steps", heading_style))
    story.append(Paragraph(
        '<b>Immediate:</b> I\'d like to walk you through the native "Add" button on a '
        "<b>15-minute call</b> — we can click through it together in your actual ADO environment "
        "so you can see it works exactly as described. No setup required; it's already there.",
        body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Optional:</b> While we're talking, we can also discuss whether the full automation "
        "option (Option B) makes sense for your workflow down the road. But no pressure — many "
        "teams find the native button strikes the perfect balance between simplicity and automation.",
        body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "I'm attaching <b>Dallas_Automation_Strategy.pdf</b> for reference if you want to dig "
        "deeper into the full automation approach.", body_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Are you available for a quick call this week?</b> I'm flexible — just let me know "
        "what works for your schedule.", body_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Thanks again for the thoughtful feedback. It really does make a difference in shaping "
        "how we build and explain this.", body_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Best,", body_style))
    story.append(Paragraph("<b>Saurabh</b>", body_style))
    story.append(Paragraph("GitHub/Microsoft Advanced Security Team", 
        ParagraphStyle("Sig", parent=body_style, textColor=GRAY, fontSize=9)))
    story.append(hr())
    story.append(Paragraph("<b>Attachments:</b>", bold_body))
    story.append(Paragraph("• Dallas_Automation_Strategy.pdf (Full automation approach reference)",
        bullet_style))

    doc.build(story)
    print(f"✅ PDF generated: {OUTPUT}")

if __name__ == "__main__":
    build()
