from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from services.ledger_service import LedgerService
from services.financial_report_service import FinancialReportService


class PDFExporter:
    """PDF export utility for financial reports."""

    @staticmethod
    def _format_currency(value) -> str:
        """Format number as Vietnamese currency."""
        if value is None or value == 0:
            return ""
        return f"{value:,.0f}"

    @staticmethod
    def _create_style():
        """Create custom styles."""
        styles = getSampleStyleSheet()
        
        styles.add(ParagraphStyle(
            name='TitleCenter',
            parent=styles['Heading1'],
            alignment=TA_CENTER,
            fontSize=14,
            spaceAfter=10,
        ))
        
        styles.add(ParagraphStyle(
            name='SubTitle',
            parent=styles['Normal'],
            alignment=TA_CENTER,
            fontSize=11,
            spaceAfter=20,
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading3'],
            fontSize=11,
            spaceBefore=10,
            spaceAfter=5,
        ))
        
        return styles

    @staticmethod
    def export_trial_balance(end_date: date) -> bytes:
        """Export Trial Balance to PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
        
        styles = PDFExporter._create_style()
        elements = []
        
        elements.append(Paragraph("BẢNG CÂN ĐỐI TÀI KHOẢN", styles['TitleCenter']))
        elements.append(Paragraph(f"Ngày lập: {end_date.strftime('%d/%m/%Y')}", styles['SubTitle']))
        
        data = LedgerService.get_trial_balance(end_date)
        
        table_data = [["Mã TK", "Tên tài khoản", "Loại", "Số dư Nợ", "Số dư Có"]]
        
        for acc in data["accounts"]:
            table_data.append([
                acc["account_code"],
                acc["account_name"],
                acc["account_type"],
                PDFExporter._format_currency(acc["debit_balance"]),
                PDFExporter._format_currency(acc["credit_balance"]),
            ])
        
        table_data.append(["", "Tổng cộng:", "", 
                          PDFExporter._format_currency(data["total_debit"]),
                          PDFExporter._format_currency(data["total_credit"])])
        
        table = Table(table_data, colWidths=[2*cm, 8*cm, 3*cm, 3.5*cm, 3.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
        ]))
        
        elements.append(table)
        
        if not data["is_balanced"]:
            elements.append(Spacer(1, 0.5*cm))
            elements.append(Paragraph(f"<b>Cảnh báo:</b> Bảng cân đối không cân bằng. Chênh lệch: {PDFExporter._format_currency(data['total_debit'] - data['total_credit'])}", 
                                   styles['Normal']))
        
        doc.build(elements)
        return buffer.getvalue()

    @staticmethod
    def export_balance_sheet(end_date: date) -> bytes:
        """Export Balance Sheet to PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        
        styles = PDFExporter._create_style()
        elements = []
        
        elements.append(Paragraph("BẢNG CÂN ĐỐI KẾ TOÁN", styles['TitleCenter']))
        elements.append(Paragraph(f"Tại ngày {end_date.strftime('%d/%m/%Y')}", styles['SubTitle']))
        
        data = FinancialReportService.get_balance_sheet(end_date)
        
        table_data = [["Mã số", "Thuyết minh", "Số cuối kỳ"]]
        
        elements.append(Paragraph("A. TÀI SẢN", styles['SectionHeader']))
        
        for acc in data["assets"]:
            if acc["balance"] != 0:
                table_data.append([
                    acc["account_code"],
                    acc["account_name"],
                    PDFExporter._format_currency(acc["balance"]),
                ])
        
        table_data.append(["", "Tổng cộng Tài sản (A)", PDFExporter._format_currency(data["total_assets"])])
        
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph("B. NỢ PHẢI TRẢ", styles['SectionHeader']))
        
        for acc in data["liabilities"]:
            if acc["balance"] != 0:
                table_data.append([
                    acc["account_code"],
                    acc["account_name"],
                    PDFExporter._format_currency(acc["balance"]),
                ])
        
        table_data.append(["", "Tổng Nợ phải trả (B)", PDFExporter._format_currency(data["total_liabilities"])])
        
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph("C. VỐN CHỦ SỞ HỮU", styles['SectionHeader']))
        
        for acc in data["equity"]:
            if acc["balance"] != 0:
                table_data.append([
                    acc["account_code"],
                    acc["account_name"],
                    PDFExporter._format_currency(acc["balance"]),
                ])
        
        table_data.append(["", "Lợi nhuận sau thuế", PDFExporter._format_currency(data["retained_earnings"])])
        table_data.append(["", "Tổng Vốn chủ sở hữu (C)", 
                          PDFExporter._format_currency(data["total_equity"] + data["retained_earnings"])])
        
        table = Table(table_data, colWidths=[2*cm, 10*cm, 4*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (1, -1), (-1, -1), colors.lightgrey),
        ]))
        
        elements.append(table)
        
        doc.build(elements)
        return buffer.getvalue()

    @staticmethod
    def export_income_statement(start_date: date, end_date: date) -> bytes:
        """Export Income Statement to PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        
        styles = PDFExporter._create_style()
        elements = []
        
        elements.append(Paragraph("BÁO CÁO KẾT QUẢ KINH DOANH", styles['TitleCenter']))
        elements.append(Paragraph(f"Từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}", styles['SubTitle']))
        
        data = FinancialReportService.get_income_statement(start_date, end_date)
        
        table_data = [["Mã số", "Chỉ tiêu", "Số kỳ này"]]
        
        elements.append(Paragraph("1. DOANH THU", styles['SectionHeader']))
        
        for acc in data["revenue"]:
            if acc["balance"] != 0:
                table_data.append([
                    acc["account_code"],
                    acc["account_name"],
                    PDFExporter._format_currency(acc["balance"]),
                ])
        
        table_data.append(["", "Tổng doanh thu", PDFExporter._format_currency(data["total_revenue"])])
        
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph("2. GIÁ VỐN HÀNG BÁN", styles['SectionHeader']))
        
        for acc in data["expenses"]:
            if acc["balance"] != 0:
                table_data.append([
                    acc["account_code"],
                    acc["account_name"],
                    PDFExporter._format_currency(acc["balance"]),
                ])
        
        table_data.append(["", "Tổng giá vốn", PDFExporter._format_currency(data["total_expenses"])])
        
        table_data.append(["", "Lợi nhuận gộp", PDFExporter._format_currency(data["gross_profit"])])
        table_data.append(["", "Lợi nhuận sau thuế", PDFExporter._format_currency(data["net_profit_after_tax"])])
        
        table = Table(table_data, colWidths=[2*cm, 10*cm, 4*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (1, -1), (-1, -1), colors.lightgrey),
        ]))
        
        elements.append(table)
        
        doc.build(elements)
        return buffer.getvalue()

    @staticmethod
    def export_journal_voucher(voucher_id: int) -> bytes:
        """Export Journal Voucher to PDF."""
        from services.journal_service import JournalService
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        
        styles = PDFExporter._create_style()
        elements = []
        
        voucher = JournalService.get_voucher(voucher_id)
        if not voucher:
            raise ValueError("Chứng từ không tồn tại")
        
        elements.append(Paragraph("CHỨNG TỪ KẾ TOÁN", styles['TitleCenter']))
        elements.append(Spacer(1, 0.5*cm))
        
        info_data = [
            ["Số chứng từ:", voucher.voucher_no],
            ["Ngày:", voucher.voucher_date.strftime("%d/%m/%Y")],
            ["Loại:", voucher.voucher_type],
            ["Diễn giải:", voucher.description or ""],
        ]
        
        info_table = Table(info_data, colWidths=[3*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0, colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        elements.append(info_table)
        
        elements.append(Spacer(1, 0.5*cm))
        
        table_data = [["STT", "Tài khoản", "Nợ", "Có", "Diễn giải"]]
        
        for idx, entry in enumerate(voucher.entries, 1):
            table_data.append([
                str(idx),
                f"{entry.account.account_code} - {entry.account.account_name}",
                PDFExporter._format_currency(entry.debit),
                PDFExporter._format_currency(entry.credit),
                entry.description or "",
            ])
        
        table_data.append(["", "Tổng cộng:", 
                          PDFExporter._format_currency(voucher.total_debit),
                          PDFExporter._format_currency(voucher.total_credit),
                          ""])
        
        table = Table(table_data, colWidths=[1*cm, 6*cm, 2.5*cm, 2.5*cm, 5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (1, -1), (3, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (1, -1), (3, -1), colors.lightgrey),
        ]))
        
        elements.append(table)
        
        doc.build(elements)
        return buffer.getvalue()
