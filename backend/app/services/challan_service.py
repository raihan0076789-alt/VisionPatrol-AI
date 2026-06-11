import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from app.core.config import settings


async def generate_challan_pdf(challan, violation) -> str:
    """Generate a professional challan PDF and return file path"""
    try:
        os.makedirs(f"{settings.UPLOAD_DIR}/challans", exist_ok=True)
        pdf_path = f"{settings.UPLOAD_DIR}/challans/{challan.challan_number}.pdf"

        doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)

        styles = getSampleStyleSheet()
        elements = []

        # Header
        header_style = ParagraphStyle('header', fontSize=20, fontName='Helvetica-Bold',
                                      textColor=colors.HexColor('#1a1a2e'), alignment=1)
        sub_style = ParagraphStyle('sub', fontSize=11, fontName='Helvetica',
                                   textColor=colors.grey, alignment=1)
        elements.append(Paragraph("VisionPatrol AI", header_style))
        elements.append(Paragraph("AI-Powered Traffic Enforcement System", sub_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#e63946')))
        elements.append(Spacer(1, 10))

        # Challan Title
        title_style = ParagraphStyle('title', fontSize=16, fontName='Helvetica-Bold',
                                     textColor=colors.HexColor('#e63946'), alignment=1)
        elements.append(Paragraph("TRAFFIC VIOLATION CHALLAN", title_style))
        elements.append(Spacer(1, 20))

        # Challan Info Table
        challan_data = [
            ["Challan Number", challan.challan_number, "Issue Date", datetime.utcnow().strftime("%d-%m-%Y")],
            ["Due Date", challan.due_date.strftime("%d-%m-%Y") if challan.due_date else "N/A",
             "Status", challan.status.value.upper()],
        ]
        table = Table(challan_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # Violation Details
        elements.append(Paragraph("Violation Details", styles['Heading2']))
        violation_data = [
            ["Violation Type", violation.violation_type.value.replace("_", " ").title()],
            ["Detection Confidence", f"{violation.confidence_score * 100:.1f}%"],
            ["Vehicle Plate", violation.plate_number or "Not Detected"],
            ["Location", violation.location or "N/A"],
            ["Detected At", violation.detected_at.strftime("%d-%m-%Y %H:%M:%S")],
            ["Fine Amount", f"₹ {challan.fine_amount:,.0f}"],
        ]
        v_table = Table(violation_data, colWidths=[2.5*inch, 4.5*inch])
        v_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        elements.append(v_table)
        elements.append(Spacer(1, 20))

        # Fine Amount Highlight
        fine_style = ParagraphStyle('fine', fontSize=14, fontName='Helvetica-Bold',
                                    textColor=colors.white, alignment=1)
        fine_data = [[Paragraph(f"TOTAL FINE AMOUNT: ₹ {challan.fine_amount:,.0f}", fine_style)]]
        fine_table = Table(fine_data, colWidths=[7*inch])
        fine_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e63946')),
            ('PADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(fine_table)
        elements.append(Spacer(1, 20))

        # Footer
        footer_style = ParagraphStyle('footer', fontSize=8, textColor=colors.grey, alignment=1)
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(
            "This is a computer-generated challan by VisionPatrol AI Traffic Enforcement System. "
            "Pay within due date to avoid additional penalties.",
            footer_style
        ))

        doc.build(elements)
        return pdf_path

    except Exception as e:
        print(f"PDF generation error: {e}")
        return None