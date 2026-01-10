"""
PDF Generator Service
Creates formatted PDF reports from CV analysis feedback
"""

import io
import os
from datetime import datetime
from typing import Optional


class PDFGenerator:
    """Generate PDF reports from CV feedback analysis"""

    _font_registered = False
    _font_name = 'Helvetica'  # Fallback

    @classmethod
    def _register_unicode_font(cls):
        """Register a Unicode-compatible font for PDF generation"""
        if cls._font_registered:
            return cls._font_name

        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        # Try to find and register a Unicode font
        font_paths = [
            # Linux (Streamlit Cloud)
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/freefont/FreeSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            # Windows
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/segoeui.ttf',
            # macOS
            '/System/Library/Fonts/Helvetica.ttc',
            '/Library/Fonts/Arial.ttf',
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('UnicodeFont', font_path))
                    cls._font_name = 'UnicodeFont'
                    cls._font_registered = True
                    return cls._font_name
                except Exception:
                    continue

        # Fallback to Helvetica if no Unicode font found
        cls._font_registered = True
        return cls._font_name

    @staticmethod
    def generate_feedback_pdf(
        feedback: str,
        match_score: float,
        job_title: str = "Position",
        provider: str = "AI",
        model: str = "",
        cv_preview: str = "",
        job_preview: str = ""
    ) -> bytes:
        """
        Generate a formatted PDF report

        Args:
            feedback: The AI-generated feedback text
            match_score: CV-to-job match percentage
            job_title: Title/name for the position
            provider: LLM provider used
            model: Model name used
            cv_preview: First part of CV (for reference)
            job_preview: First part of job description

        Returns:
            PDF file as bytes
        """
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, ListFlowable, ListItem
        )

        # Register Unicode font
        font_name = PDFGenerator._register_unicode_font()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )

        # Get base styles
        styles = getSampleStyleSheet()

        # Custom styles with Unicode font
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name,
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor('#06b6d4'),
            alignment=1  # Center
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=12,
            textColor=colors.HexColor('#64748b'),
            alignment=1,
            spaceAfter=30
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontName=font_name,
            fontSize=14,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=20,
            spaceAfter=10,
            borderPadding=5
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor('#334155'),
            spaceBefore=5,
            spaceAfter=5,
            leading=14
        )

        elements = []

        # Title
        elements.append(Paragraph("CV Feedback Analysis Report", title_style))
        elements.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            subtitle_style
        ))

        # Divider
        elements.append(HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor('#06b6d4'),
            spaceAfter=20
        ))

        # Metadata table
        score_color = '#10b981' if match_score >= 70 else '#f59e0b' if match_score >= 50 else '#ef4444'
        meta_data = [
            ['Position:', job_title, 'Match Score:', f'{match_score}%'],
            ['AI Provider:', provider, 'Model:', model],
        ]

        meta_table = Table(meta_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#64748b')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (3, 0), (3, 0), colors.HexColor(score_color)),
            ('FONTNAME', (3, 0), (3, 0), font_name),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 20))

        # Divider
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#e2e8f0'),
            spaceAfter=20
        ))

        # Feedback content
        elements.append(Paragraph("Detailed Analysis", heading_style))

        import re

        def escape_xml(text):
            """Escape special XML characters"""
            text = text.replace('&', '&amp;')
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;')
            return text

        def process_line(line):
            """Process a line of text for PDF formatting"""
            # Escape special characters first
            line = escape_xml(line)
            # Handle bold markdown
            line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
            line = re.sub(r'__(.+?)__', r'<b>\1</b>', line)
            # Handle inline code
            line = re.sub(r'`([^`]+)`', r'<font face="Courier">\1</font>', line)
            return line

        # Process feedback text - split by markdown headers and format
        sections = feedback.split('\n')
        current_section = []
        in_table = False
        table_rows = []

        for line in sections:
            line = line.strip()

            # Skip empty lines but output accumulated content
            if not line:
                if current_section:
                    elements.append(Paragraph('<br/>'.join(current_section), body_style))
                    current_section = []
                continue

            # Skip table separator lines (|---|---|)
            if re.match(r'^\|[-:\s|]+\|$', line):
                continue

            # Handle markdown tables
            if line.startswith('|') and line.endswith('|'):
                if not in_table:
                    # Output any pending content before table
                    if current_section:
                        elements.append(Paragraph('<br/>'.join(current_section), body_style))
                        current_section = []
                    in_table = True
                    table_rows = []

                # Parse table row
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                table_rows.append([process_line(cell) for cell in cells])
                continue
            elif in_table and table_rows:
                # End of table - create table element
                try:
                    if len(table_rows) > 0:
                        # Calculate column widths
                        num_cols = len(table_rows[0])
                        col_width = 6.5 * inch / num_cols

                        # Create table with data wrapped in Paragraphs
                        table_data = []
                        for row in table_rows:
                            table_data.append([Paragraph(cell, body_style) for cell in row])

                        t = Table(table_data, colWidths=[col_width] * num_cols)
                        t.setStyle(TableStyle([
                            ('FONTNAME', (0, 0), (-1, -1), font_name),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#334155')),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('TOPPADDING', (0, 0), (-1, -1), 6),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                            ('LEFTPADDING', (0, 0), (-1, -1), 6),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                        ]))
                        elements.append(Spacer(1, 10))
                        elements.append(t)
                        elements.append(Spacer(1, 10))
                except Exception as e:
                    # If table fails, add as text
                    for row in table_rows:
                        elements.append(Paragraph(' | '.join(row), body_style))

                in_table = False
                table_rows = []

            # Handle markdown headers
            if line.startswith('### '):
                if current_section:
                    elements.append(Paragraph('<br/>'.join(current_section), body_style))
                    current_section = []
                elements.append(Paragraph(escape_xml(line[4:]), heading_style))
            elif line.startswith('## '):
                if current_section:
                    elements.append(Paragraph('<br/>'.join(current_section), body_style))
                    current_section = []
                elements.append(Paragraph(escape_xml(line[3:]), heading_style))
            elif line.startswith('# '):
                if current_section:
                    elements.append(Paragraph('<br/>'.join(current_section), body_style))
                    current_section = []
                elements.append(Paragraph(escape_xml(line[2:]), heading_style))
            elif line.startswith('- ') or line.startswith('* '):
                # Bullet point
                current_section.append(f"&bull; {process_line(line[2:])}")
            elif re.match(r'^\d+\.', line):
                # Numbered item
                current_section.append(process_line(line))
            else:
                # Regular text
                current_section.append(process_line(line))

        # Output remaining content
        if current_section:
            elements.append(Paragraph('<br/>'.join(current_section), body_style))

        # Handle any remaining table
        if in_table and table_rows:
            try:
                num_cols = len(table_rows[0])
                col_width = 6.5 * inch / num_cols
                table_data = [[Paragraph(cell, body_style) for cell in row] for row in table_rows]
                t = Table(table_data, colWidths=[col_width] * num_cols)
                t.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(t)
            except:
                pass

        # Footer
        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#e2e8f0'),
            spaceBefore=20,
            spaceAfter=10
        ))

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=8,
            textColor=colors.HexColor('#94a3b8'),
            alignment=1
        )
        elements.append(Paragraph(
            "Generated by CV Feedback Assistant | Powered by AI",
            footer_style
        ))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def get_download_filename(job_title: str = "analysis") -> str:
        """Generate a filename for the PDF download"""
        # Clean job title for filename
        import re
        clean_title = re.sub(r'[^\w\s-]', '', job_title)
        clean_title = re.sub(r'[-\s]+', '_', clean_title).strip('_')
        if not clean_title:
            clean_title = "cv_feedback"

        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        return f"{clean_title}_feedback_{timestamp}.pdf"
