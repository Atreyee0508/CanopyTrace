"""ReportLab PDF dossier generator for CanopyTrace customs triage reports."""

import os
from pathlib import Path
from typing import Any, Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from canopytrace.schemas.forensic_output import MANDATORY_LEGAL_DISCLAIMER


def generate_pdf_dossier(case_data: Dict[str, Any], output_pdf_path: Path, sha256_hash: str) -> Path:
    """
    Generates a printable, customs-grade forensic triage PDF report.
    """
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e293b"),
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748b"),
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    disclaimer_style = ParagraphStyle(
        "DisclaimerText",
        parent=styles["Italic"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#991b1b"),
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("CANOPYTRACE // FORENSIC TRIAGE REPORT", title_style))
    elements.append(Paragraph(
        "Border Customs & Wildlife Law Enforcement Investigative Decision-Support",
        subtitle_style
    ))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=8, spaceBefore=4))

    manifest = case_data.get("manifest", {})
    inspection = case_data.get("inspection", {})
    forensic = case_data.get("forensic_output", {})

    case_id = case_data.get("case_id", "CASE-UNKNOWN")
    discrepancy = forensic.get("discrepancy_score", 0.0)

    # Status Banner
    status_color = colors.HexColor("#dc2626") if discrepancy >= 0.70 else (
        colors.HexColor("#d97706") if discrepancy >= 0.30 else colors.HexColor("#16a34a")
    )
    status_text = "🚨 CRITICAL CONTRABAND SUSPECTED - SEIZURE RECOMMENDED" if discrepancy >= 0.70 else (
        "⚠️ ELEVATED UNCERTAINTY - SECONDARY INSPECTION" if discrepancy >= 0.30 else "✅ LOW DISCREPANCY - CLEARANCE PERMITTED"
    )

    banner_data = [
        [Paragraph(f"<b>CASE FILE:</b> {case_id}", body_style),
         Paragraph(f"<b>STATUS:</b> <font color='{status_color.hexval()}'><b>{status_text}</b></font>", body_style)],
        [Paragraph(f"<b>DISCREPANCY SCORE:</b> <b>{discrepancy:.2f} / 1.00</b>", body_style),
         Paragraph(f"<b>CITES APPENDIX:</b> <b>{forensic.get('cites_appendix', 'None')}</b>", body_style)],
    ]
    banner_table = Table(banner_data, colWidths=[270, 270])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(banner_table)
    elements.append(Spacer(1, 8))

    # Manifest vs Inspection Summary Table
    elements.append(Paragraph("1. CARGO DECLARATION VS. PHYSICAL FINDINGS", section_heading))
    table_data = [
        [Paragraph("<b>Attribute</b>", body_style), Paragraph("<b>Manifest Paperwork</b>", body_style), Paragraph("<b>Physical Examination</b>", body_style)],
        [Paragraph("Declared / Suspected Taxon", body_style),
         Paragraph(f"{manifest.get('declared_item_name', 'N/A')}<br/><i>{manifest.get('declared_scientific_name', '')}</i>", body_style),
         Paragraph(f"<b>{forensic.get('suspected_actual_species', 'N/A')}</b>", body_style)],
        [Paragraph("Origin / Native Range", body_style),
         Paragraph(f"{manifest.get('country_of_origin', 'N/A')}", body_style),
         Paragraph(f"Category: {inspection.get('observed_specimen_category', 'N/A')}", body_style)],
        [Paragraph("Permit Claims", body_style),
         Paragraph(f"{', '.join(manifest.get('permit_numbers', [])) or 'None Provided'}", body_style),
         Paragraph(f"Appendix Breach: <b>{forensic.get('cites_appendix', 'None')}</b>", body_style)],
    ]
    meta_table = Table(table_data, colWidths=[140, 200, 200])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8))

    # Optional Photographic Evidence Embedding
    photos = inspection.get("photos", [])
    if photos and isinstance(photos, list) and os.path.exists(str(photos[0])):
        try:
            from PIL import Image as PILImage
            from reportlab.platypus import Image as RLImage
            # Verify image is valid readable image format
            with PILImage.open(str(photos[0])) as p_img:
                p_img.verify()
            elements.append(Paragraph("<b>ON-SITE PHOTOGRAPHIC EVIDENCE:</b>", section_heading))
            elements.append(RLImage(str(photos[0]), width=220, height=140))
            elements.append(Spacer(1, 8))
        except Exception:
            pass

    # Flagged Contradictions & Modus Operandi
    elements.append(Paragraph("2. FORENSIC CONTRADICTIONS & SMUGGLING MODUS OPERANDI", section_heading))
    flagged = forensic.get("flagged_indicators", [])
    if flagged:
        for ind in flagged:
            elements.append(Paragraph(f"• <b>CONTRADICTION:</b> {ind}", body_style))
    else:
        elements.append(Paragraph("• No empirical contradictions detected between declaration and physical metrics.", body_style))

    mos = forensic.get("smuggling_mo_detected", [])
    if mos:
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"<b>MATCHED SMUGGLING MODUS OPERANDI:</b> {', '.join(mos)}", body_style))

    elements.append(Spacer(1, 8))

    # Forensic Rationale
    elements.append(Paragraph("3. AI INVESTIGATIVE RATIONALE (GEMMA 2 DECODING)", section_heading))
    rationale = forensic.get("forensic_rationale", "No rationale generated.")
    elements.append(Paragraph(rationale, body_style))
    elements.append(Spacer(1, 8))

    # Recommended Laboratory Protocol
    elements.append(Paragraph("4. RECOMMENDED CONFIRMATORY LABORATORY PROTOCOL", section_heading))
    lab_actions = forensic.get("suggested_lab_action", [])
    lab_data = [
        [Paragraph("<b>Assay / Test Type</b>", body_style), Paragraph("<b>Priority</b>", body_style), Paragraph("<b>Target Discriminator</b>", body_style)]
    ]
    if lab_actions:
        for action in lab_actions:
            lab_data.append([
                Paragraph(action.get("test_type", ""), body_style),
                Paragraph(f"<b>{action.get('priority', '').upper()}</b>", body_style),
                Paragraph(action.get("expected_discriminator", ""), body_style),
            ])
    else:
        lab_data.append([Paragraph("Standard visual audit", body_style), Paragraph("OPTIONAL", body_style), Paragraph("Baseline documentation", body_style)])

    lab_table = Table(lab_data, colWidths=[160, 90, 290])
    lab_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(lab_table)
    elements.append(Spacer(1, 10))

    # Mandatory Legal Disclaimer Box
    elements.append(KeepTogether([
        Table(
            [[Paragraph(f"<b>MANDATORY LEGAL DISCLAIMER:</b><br/>{MANDATORY_LEGAL_DISCLAIMER}", disclaimer_style)]],
            colWidths=[540],
            style=TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#f87171")),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ])
        ),
        Spacer(1, 6),
        Paragraph(f"<b>CHAIN-OF-CUSTODY SHA-256 INTEGRITY DIGEST:</b> <code>{sha256_hash}</code>", subtitle_style),
    ]))

    doc.build(elements)
    return output_pdf_path
