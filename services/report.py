import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect, String, Line

def generate_pdf_report(report_data):
    """
    Generates an in-memory PDF file containing the full ATS optimization and interview prep report.
    """
    buffer = io.BytesIO()
    
    # Page setup
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=40, leftMargin=40,
        topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom color palette
    primary_color = colors.HexColor("#0f172a")    # Premium Dark Slate (Navy-Black)
    secondary_color = colors.HexColor("#0f766e")  # Dark Emerald/Teal
    accent_color = colors.HexColor("#0ea5e9")     # Vibrant Cyan
    dark_text = colors.HexColor("#334155")        # Gray-Slate
    light_bg = colors.HexColor("#f8fafc")         # Slate 50
    border_color = colors.HexColor("#e2e8f0")     # Slate 200
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=5
    )
    
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=20
    )
    
    h1_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=secondary_color,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=dark_text,
        spaceAfter=6
    )
    
    bold_body_style = ParagraphStyle(
        'BoldBodyCustom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    header_style = ParagraphStyle(
        'TableHeaderCustom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.white
    )

    elements = []
    
    # --- HEADER / BRAND BANNER ---
    # Decorative horizontal color bar at the very top
    top_bar = Drawing(530, 4)
    top_bar.add(Rect(0, 0, 530, 4, fillColor=secondary_color, strokeColor=None))
    elements.append(top_bar)
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("PRO-ALIGN: TALENT MATCH & OPTIMIZATION REPORT", title_style))
    elements.append(Paragraph(f"Resume context: {report_data.get('filename')} | Profile score: {report_data.get('overall_score')}%", subtitle_style))
    elements.append(Spacer(1, 5))
    
    # --- MATCH SCORE CARD ---
    elements.append(Paragraph("1. ATS Performance Score Card", h1_style))
    
    # Draw simple progress bar
    score = report_data.get('overall_score', 0)
    d = Drawing(530, 24)
    # Background bar
    d.add(Rect(0, 2, 530, 16, fillColor=colors.HexColor("#f1f5f9"), strokeColor=None, rx=4, ry=4))
    # Filled progress bar
    bar_color = secondary_color if score >= 80 else (colors.HexColor("#b45309") if score >= 60 else colors.HexColor("#be123c"))
    d.add(Rect(0, 2, int(score * 5.3), 16, fillColor=bar_color, strokeColor=None, rx=4, ry=4))
    # Score label
    d.add(String(220, 6, f"Overall ATS Score: {score}%", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.white if score > 50 else dark_text))
    elements.append(d)
    elements.append(Spacer(1, 12))
    
    # Score Breakdown Table
    breakdown = report_data.get('breakdown', {})
    scores = breakdown.get('scores', {})
    table_data = [
        [
            Paragraph("Metric Category", header_style), 
            Paragraph("Score (%)", header_style), 
            Paragraph("Target Weight", header_style)
        ]
    ]
    
    # Map breakdown scores from correct nested scores keys
    categories = [
        ("Skills Compatibility", scores.get("skills", 0), "40%"),
        ("Experience Alignment", scores.get("experience", 0), "20%"),
        ("Projects Fit", scores.get("projects", 0), "15%"),
        ("Education Match", scores.get("education", 0), "10%"),
        ("Formatting & Structure", scores.get("formatting", 0), "5%"),
        ("NLP Semantic Similarity", scores.get("semantic", 0), "10%"),
    ]
    
    for label, val, weight in categories:
        table_data.append([
            Paragraph(label, body_style), 
            Paragraph(f"{val}%", body_style), 
            Paragraph(weight, body_style)
        ])
        
    t = Table(table_data, colWidths=[270, 130, 130])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 7),
        ('TOPPADDING', (0,0), (-1,0), 7),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
        ('TOPPADDING', (0,1), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg])
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 15))
    
    # --- KEYWORD MATCH & MISSING SKILLS ---
    elements.append(Paragraph("2. Skill Match Analysis", h1_style))
    
    matched = report_data.get('matched_skills', [])
    missing = report_data.get('missing_skills', [])
    
    matched_text = ", ".join(matched) if matched else "None identified"
    missing_text = ", ".join(missing) if missing else "None identified"
    
    matched_p = Paragraph(f"<font color='#065f46'><b>{matched_text}</b></font>", body_style)
    missing_p = Paragraph(f"<font color='#991b1b'><b>{missing_text}</b></font>", body_style)
    
    skills_header_style = ParagraphStyle(
        'SkillsHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=primary_color
    )

    skills_table_data = [
        [
            Paragraph("Matched Keywords", skills_header_style), 
            Paragraph("Missing Gaps in JD", skills_header_style)
        ],
        [matched_p, missing_p]
    ]
    
    st = Table(skills_table_data, colWidths=[265, 265])
    st.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#e2f0d9")), # Soft green background
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#fce4d6")), # Soft rose background
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
    ]))
    
    elements.append(st)
    elements.append(Spacer(1, 15))
    
    # --- SUGGESTIONS ---
    elements.append(Paragraph("3. Optimization Suggestions", h1_style))
    suggestions = report_data.get('suggestions', [])
    for sug in suggestions:
        if isinstance(sug, dict):
            title = sug.get('type', 'Recommendation')
            msg = sug.get('message', '')
        else:
            title = 'Recommendation'
            msg = str(sug)
            if msg.startswith('✓ '):
                msg = msg[2:]
            elif msg.startswith('✓'):
                msg = msg[1:]
        elements.append(Paragraph(f"• <b>{title}:</b> {msg}", bullet_style))
        
    elements.append(Spacer(1, 15))
    
    # Page Break for Interview Prep
    elements.append(PageBreak())
    
    # --- INTERVIEW QUESTIONS & COACHING ---
    elements.append(Paragraph("4. AI Mock Interview Prep Simulator", h1_style))
    elements.append(Paragraph("Prepare for potential screening and panel questions using these optimized answers.", subtitle_style))
    
    questions = report_data.get('interview_questions', [])
    for idx, q in enumerate(questions, 1):
        q_elements = []
        
        # Heading: Question index and difficulty
        q_elements.append(Paragraph(
            f"<font color='#0f766e'><b>Q{idx}. [{q.get('type', 'Technical')}]</b></font> &nbsp;|&nbsp; <b>Difficulty: {q.get('difficulty', 'Medium')}</b>", 
            body_style
        ))
        
        # Question text
        q_elements.append(Paragraph(
            f"<b>Question:</b> {q.get('question', '')}", 
            body_style
        ))
        
        # Ideal Answer
        q_elements.append(Paragraph(
            f"<b>Ideal AI Answer:</b> {q.get('ideal_answer', '')}", 
            body_style
        ))
        
        # STAR Method Response
        star = q.get('star_answer', {})
        if star and isinstance(star, dict):
            star_text = (
                f"<b>Situation:</b> {star.get('situation', '')}<br/>"
                f"<b>Task:</b> {star.get('task', '')}<br/>"
                f"<b>Action:</b> {star.get('action', '')}<br/>"
                f"<b>Result:</b> {star.get('result', '')}"
            )
            q_elements.append(Paragraph(f"<b>STAR Method Response:</b><br/>{star_text}", body_style))
            
        # Common Mistakes
        common = q.get('common_mistakes', [])
        if common:
            q_elements.append(Paragraph(f"<b>Common Mistakes:</b> {', '.join(common)}", body_style))
            
        # Confidence Tips
        tips = q.get('confidence_tips', '')
        if tips:
            q_elements.append(Paragraph(f"<b>Confidence Tips:</b> {tips}", body_style))
            
        # Wrap everything in a nice left-accented table card
        card_table_data = [
            [
                "", # Left border spacer
                q_elements
            ]
        ]
        
        # Column 0 is the accent bar, Column 1 is the details
        card_table = Table(card_table_data, colWidths=[4, 510])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), secondary_color), # Left accent color (Teal)
            ('BACKGROUND', (1,0), (1,0), colors.HexColor("#f8fafc")), # Card background (Slate 50)
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (1,0), (1,0), 10),
            ('TOPPADDING', (1,0), (1,0), 10),
            ('LEFTPADDING', (1,0), (1,0), 12),
            ('RIGHTPADDING', (1,0), (1,0), 12),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ]))
        
        elements.append(card_table)
        elements.append(Spacer(1, 12))
        
    # Build Document
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
