"""Generates CSV and PDF exports of transaction data."""
import csv
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def export_transactions_csv(transactions):
    """Return an in-memory CSV file (BytesIO) of the given transactions."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Type", "Category", "Amount", "Payment Method", "Notes"])
    for tx in transactions:
        writer.writerow(
            [
                tx.date.strftime("%Y-%m-%d"),
                tx.type.capitalize(),
                tx.category.name if tx.category else "",
                f"{tx.amount:.2f}",
                tx.payment_method,
                (tx.notes or "").replace("\n", " "),
            ]
        )
    # Convert to bytes for send_file
    byte_output = io.BytesIO(output.getvalue().encode("utf-8"))
    byte_output.seek(0)
    return byte_output


def export_transactions_pdf(transactions, user, title="Transaction Report", summary=None):
    """Return an in-memory PDF file (BytesIO) of the given transactions."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=18, spaceAfter=6)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=10, textColor=colors.grey)

    elements = [
        Paragraph(title, title_style),
        Paragraph(f"Account holder: {user.full_name} ({user.email})", subtitle_style),
        Paragraph(f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", subtitle_style),
        Spacer(1, 12),
    ]

    if summary:
        summary_data = [
            ["Total Income", f"{summary['income']:.2f}"],
            ["Total Expense", f"{summary['expense']:.2f}"],
            ["Balance", f"{summary['balance']:.2f}"],
        ]
        summary_table = Table(summary_data, colWidths=[2 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 16))

    table_data = [["Date", "Type", "Category", "Amount", "Payment Method", "Notes"]]
    for tx in transactions:
        table_data.append(
            [
                tx.date.strftime("%Y-%m-%d"),
                tx.type.capitalize(),
                tx.category.name if tx.category else "",
                f"{tx.amount:.2f}",
                tx.payment_method,
                (tx.notes or "")[:40],
            ]
        )

    table = Table(table_data, repeatRows=1, colWidths=[0.85 * inch, 0.7 * inch, 1.1 * inch, 0.8 * inch, 1.15 * inch, 1.9 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
