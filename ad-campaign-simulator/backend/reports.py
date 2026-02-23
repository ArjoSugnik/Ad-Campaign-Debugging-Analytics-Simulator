"""
=============================================================
  reports.py - PDF Report Generator
=============================================================
  Generates a downloadable PDF report for a campaign.
  Uses the 'reportlab' library to create professional PDFs.
  
  Install: pip install reportlab
"""

import os
from datetime import datetime

# We'll use reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️  reportlab not installed. PDF export will use text format.")
    print("   Run: pip install reportlab")


# Where to save generated reports
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_pdf_report(campaign, diagnostics):
    """
    Generates a PDF report and saves it to the reports folder.
    Returns the file path.
    """
    filename = f"campaign_{campaign['id']}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)

    if REPORTLAB_AVAILABLE:
        _generate_with_reportlab(filepath, campaign, diagnostics)
    else:
        # Fallback to plain text if reportlab not installed
        filepath = filepath.replace(".pdf", ".txt")
        _generate_text_report(filepath, campaign, diagnostics)

    return filepath


def _generate_with_reportlab(filepath, campaign, diagnostics):
    """Creates a formatted PDF using reportlab."""
    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=1*inch, bottomMargin=1*inch)

    styles = getSampleStyleSheet()
    elements = []

    # Define custom styles
    title_style = ParagraphStyle('Title', parent=styles['Title'],
                                  fontSize=24, textColor=colors.HexColor("#1a1a2e"),
                                  spaceAfter=6)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'],
                                    fontSize=14, textColor=colors.HexColor("#16213e"),
                                    spaceBefore=12, spaceAfter=6)
    body_style = styles['BodyText']
    body_style.fontSize = 10

    # ---- HEADER ----
    elements.append(Paragraph("📊 Ad Campaign Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", body_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0f3460")))
    elements.append(Spacer(1, 12))

    # ---- CAMPAIGN OVERVIEW ----
    elements.append(Paragraph("Campaign Overview", heading_style))

    # Health score color
    score = diagnostics.get("health_score", 0)
    if score >= 80:
        score_color = colors.green
    elif score >= 50:
        score_color = colors.orange
    else:
        score_color = colors.red

    overview_data = [
        ["Field", "Value"],
        ["Campaign Name", campaign.get("name", "")],
        ["Health Score", f"{score}/100"],
        ["Status", diagnostics.get("status", "").upper()],
        ["Budget", f"${campaign.get('budget', 0):,.2f}"],
        ["Impressions", f"{campaign.get('impressions', 0):,}"],
        ["Clicks", f"{campaign.get('clicks', 0):,}"],
        ["Conversions", f"{campaign.get('conversions', 0):,}"],
    ]

    overview_table = Table(overview_data, colWidths=[2.5*inch, 4*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f3460")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 16))

    # ---- KEY METRICS ----
    elements.append(Paragraph("Key Metrics", heading_style))

    metrics = diagnostics.get("metrics_analyzed", {})
    metrics_data = [
        ["Metric", "Value", "Benchmark"],
        ["CTR (Click-Through Rate)", f"{metrics.get('ctr', 0)}%", "≥ 2.0% is good"],
        ["CPC (Cost Per Click)", f"${metrics.get('cpc', 0)}", "≤ $5.00 is good"],
        ["Conversion Rate", f"{metrics.get('conversion_rate', 0)}%", "≥ 2.0% is good"],
        ["Budget Remaining", f"{metrics.get('budget_remaining_pct', 0)}%", "≥ 20% is safe"],
    ]

    metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#533483")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0eeff")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 16))

    # ---- DETECTED ISSUES ----
    issues = diagnostics.get("issues", [])
    elements.append(Paragraph(f"Detected Issues ({len(issues)} found)", heading_style))

    if not issues:
        elements.append(Paragraph("✅ No issues detected. Campaign is healthy!", body_style))
    else:
        for i, issue in enumerate(issues, 1):
            sev = issue.get("severity", "info")
            sev_color = {"critical": "#ff4444", "warning": "#ff9900", "info": "#0066cc"}.get(sev, "#333")

            elements.append(Paragraph(f"{i}. {issue.get('title', 'Unknown Issue')}", heading_style))
            elements.append(Paragraph(issue.get("description", ""), body_style))

            causes = issue.get("root_causes", [])
            if causes:
                elements.append(Paragraph("Possible Root Causes:", ParagraphStyle(
                    'BoldBody', parent=body_style, fontName='Helvetica-Bold')))
                for cause in causes[:3]:  # Limit to top 3
                    elements.append(Paragraph(f"  • {cause}", body_style))

            elements.append(Spacer(1, 6))

    elements.append(Spacer(1, 12))

    # ---- RECOMMENDATIONS ----
    recommendations = diagnostics.get("recommendations", [])
    elements.append(Paragraph(f"Top Recommendations ({len(recommendations)} actions)", heading_style))

    for j, rec in enumerate(recommendations[:8], 1):  # Top 8 recs
        elements.append(Paragraph(f"{j}. {rec}", body_style))
        elements.append(Spacer(1, 3))

    # ---- FOOTER ----
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elements.append(Paragraph("Generated by Ad Campaign Debugging & Analytics Simulator",
                               ParagraphStyle('Footer', parent=body_style, fontSize=8,
                                              textColor=colors.grey, alignment=1)))

    doc.build(elements)
    print(f"✅ PDF report saved: {filepath}")


def _generate_text_report(filepath, campaign, diagnostics):
    """Fallback plain-text report if reportlab isn't installed."""
    lines = [
        "=" * 60,
        "  AD CAMPAIGN REPORT",
        f"  Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        "=" * 60,
        "",
        f"Campaign: {campaign.get('name')}",
        f"Health Score: {diagnostics.get('health_score')}/100",
        f"Status: {diagnostics.get('status', '').upper()}",
        "",
        "--- KEY METRICS ---",
        f"CTR: {campaign.get('ctr')}%",
        f"CPC: ${campaign.get('cpc')}",
        f"Conversion Rate: {campaign.get('conversion_rate')}%",
        "",
        "--- ISSUES DETECTED ---",
    ]

    for issue in diagnostics.get("issues", []):
        lines.append(f"[{issue.get('severity', '').upper()}] {issue.get('title')}")
        lines.append(f"  {issue.get('description')}")

    lines.append("")
    lines.append("--- RECOMMENDATIONS ---")
    for i, rec in enumerate(diagnostics.get("recommendations", []), 1):
        lines.append(f"{i}. {rec}")

    with open(filepath, "w") as f:
        f.write("\n".join(lines))
    print(f"✅ Text report saved: {filepath}")
