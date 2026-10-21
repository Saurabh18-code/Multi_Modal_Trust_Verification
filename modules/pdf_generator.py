import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def generate_pdf_report(result_data, user_id="Unknown"):
    """
    Generates a clean, non-overlapping 1-page Identity Verification Summary.
    
    Args:
        result_data (dict): Verification results containing scores & explanations.
        user_id (str): User identifier associated with the verification attempt.
        
    Returns:
        io.BytesIO: In-memory binary stream of the generated PDF document.
    """
    buffer = io.BytesIO()
    
    # 612 x 792 pt page size (Letter). Margins 40pt left/right -> Printable width = 532pt
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # -------------------------------------------------------------
    # CUSTOM TYPOGRAPHY WITH EXPLICIT LEADING (PREVENTS TEXT MERGING)
    # -------------------------------------------------------------
    brand_title = ParagraphStyle(
        'BrandTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#111827')
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#315efb')
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475467')
    )
    
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#111827')
    )

    card_label = ParagraphStyle(
        'CardLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#64748b')
    )

    card_score = ParagraphStyle(
        'CardScore',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#111827')
    )

    table_header_style = ParagraphStyle(
        'THeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    elements = []

    # -------------------------------------------------------------
    # 1. HEADER SECTION
    # -------------------------------------------------------------
    elements.append(Paragraph("TRUSTNET AI · DIGITAL IDENTITY SYSTEM", subtitle_style))
    elements.append(Spacer(1, 2))
    elements.append(Paragraph("Verification Summary Report", brand_title))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#315efb'), spaceAfter=14))

    # -------------------------------------------------------------
    # 2. METADATA BLOCK
    # -------------------------------------------------------------
    now_str = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
    meta_data = [
        [
            Paragraph(f"<b>User Identifier:</b> {user_id}", body_style),
            Paragraph(f"<b>Date & Time:</b> {now_str}", body_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[266, 266])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e3e7ef')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # 3. OVERALL RESULT CARD (NO OVERLAPPING TEXT)
    # -------------------------------------------------------------
    decision = str(result_data.get('decision', 'N/A')).upper()
    trust_score = result_data.get('trust_score', 0.0)

    if "VERIFIED" in decision:
        status_bg = colors.HexColor('#edf9f5')
        status_color = colors.HexColor('#16a46f')
    elif "FLAGGED" in decision:
        status_bg = colors.HexColor('#fffbeb')
        status_color = colors.HexColor('#d98a19')
    else:
        status_bg = colors.HexColor('#fff2f2')
        status_color = colors.HexColor('#dc4c4c')

    card_verdict = ParagraphStyle(
        'CardVerdict',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        textColor=status_color
    )

    cell_score = [
        Paragraph("OVERALL TRUST SCORE", card_label),
        Spacer(1, 4),
        Paragraph(f"<b>{trust_score}%</b>", card_score)
    ]
    
    cell_verdict = [
        Paragraph("VERDICT", card_label),
        Spacer(1, 6),
        Paragraph(f"<b>● {decision}</b>", card_verdict)
    ]

    summary_card = Table([[cell_score, cell_verdict]], colWidths=[266, 266])
    summary_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), status_bg),
        ('BOX', (0, 0), (-1, -1), 1, status_color),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(summary_card)
    elements.append(Spacer(1, 18))

    # -------------------------------------------------------------
    # 4. SIGNALS BREAKDOWN TABLE
    # -------------------------------------------------------------
    elements.append(Paragraph("Verification Signals Breakdown", body_bold))
    elements.append(Spacer(1, 8))

    table_data = [
        [
            Paragraph("Modality", table_header_style),
            Paragraph("Score", table_header_style),
            Paragraph("Status Summary", table_header_style)
        ]
    ]

    modalities = [
        ("Facial Verification", result_data.get('face_score', 0.0), result_data.get('face_explanation', 'N/A')),
        ("Document Verification", result_data.get('document_score', 0.0), result_data.get('document_explanation', 'N/A')),
        ("Behavioral Analysis", result_data.get('behavioral_score', 0.0), result_data.get('behavioral_explanation', 'N/A'))
    ]

    for mod_name, score, exp in modalities:
        short_exp = str(exp)
        if len(short_exp) > 110:
            short_exp = short_exp[:107] + "..."

        table_data.append([
            Paragraph(f"<b>{mod_name}</b>", body_style),
            Paragraph(f"<b>{score}%</b>", body_bold),
            Paragraph(short_exp, body_style)
        ])

    breakdown_table = Table(table_data, colWidths=[140, 70, 322])
    breakdown_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111827')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e3e7ef')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    elements.append(breakdown_table)

    # -------------------------------------------------------------
    # 5. FOOTER SECTION
    # -------------------------------------------------------------
    elements.append(Spacer(1, 35))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=10))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#98a2b3')
    )
    
    footer = Paragraph(
        "This document is an official automated verification summary generated by TrustNet AI.<br/>"
        "Confidential · Digital Identity Verification Record",
        footer_style
    )
    elements.append(footer)

    doc.build(elements)
    buffer.seek(0)
    return buffer