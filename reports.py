from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
import io
import os

def generate_student_report_card(university_name, student_data, grades_data, attendance_summary, remarks_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    elements = []

    # Title / Header
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#4F46E5"), # Brand Primary
        alignment=1, # Center
        spaceAfter=20
    )
    elements.append(Paragraph(university_name, title_style))
    elements.append(Paragraph("Official Academic Report Card", styles['Heading2']))
    elements.append(Spacer(1, 0.25 * inch))

    # Student Info Table
    data = [
        ["Student Name:", student_data['username'], "Role:", student_data['role'].capitalize()],
        ["Report Term:", remarks_data.get('term', 'Annual'), "Date Generated:", "Jan 2026"]
    ]
    t = Table(data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
        ('TEXTCOLOR', (2,0), (2,-1), colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.5 * inch))

    # Academic Performance Header
    elements.append(Paragraph("Academic Performance", styles['Heading3']))
    elements.append(Spacer(1, 0.1 * inch))

    # Grades Table
    grade_table_data = [["Course Name", "Subject Mastery", "Status"]]
    for g in grades_data:
        grade_table_data.append([g['name'], f"{g['avg_score']}%", "Pass" if g['avg_score'] >= 50 else "Fail"])

    gt = Table(grade_table_data, colWidths=[3*inch, 2*inch, 1*inch])
    gt.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
    ]))
    elements.append(gt)
    elements.append(Spacer(1, 0.4 * inch))

    # Attendance & Stats
    elements.append(Paragraph("Operational Metrics", styles['Heading3']))
    elements.append(Spacer(1, 0.1 * inch))
    
    total_logs = sum([row['count'] for row in attendance_summary])
    present_logs = next((row['count'] for row in attendance_summary if row['status'] == 'Present'), 0)
    attendance_rate = f"{int((present_logs/total_logs)*100)}%" if total_logs > 0 else "N/A"

    att_data = [
        ["Attendance Rate:", attendance_rate, "Total Sessions:", str(total_logs)]
    ]
    at = Table(att_data, colWidths=[1.5*inch, 1*inch, 1.5*inch, 1*inch])
    at.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ]))
    elements.append(at)
    elements.append(Spacer(1, 0.5 * inch))

    # Teacher Remarks Section
    elements.append(Paragraph("Teacher Evaluation & Remarks", styles['Heading3']))
    elements.append(Spacer(1, 0.1 * inch))
    
    remarks_box = [
        [Paragraph(f"<b>General Remarks:</b><br/>{remarks_data.get('remarks', 'No remarks provided.')}", styles['Normal'])],
        [Spacer(1, 0.1 * inch)],
        [Paragraph(f"<b>Areas for Improvement:</b><br/>{remarks_data.get('improvement_areas', 'Continue pushing for excellence.')}", styles['Normal'])]
    ]
    rt = Table(remarks_box, colWidths=[6*inch])
    rt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F9FAFB")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E5E7EB")),
        ('PADDING', (0,0), (-1,-1), 20),
    ]))
    elements.append(rt)

    # Footer
    elements.append(Spacer(1, 1 * inch))
    elements.append(Paragraph("__________________________", styles['Normal']))
    elements.append(Paragraph("Dean of Academics Signature", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer
