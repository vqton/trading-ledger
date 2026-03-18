from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from models.account import Account, AccountType
from repositories.financial_report_repository import FinancialReportRepository
from repositories.ledger_repository import LedgerRepository
from repositories.account_repository import AccountRepository


class BalanceSheetService:
    """Service for Balance Sheet (Bảng cân đối kế toán)."""

    @staticmethod
    def get_balance_sheet(end_date: date) -> Dict:
        """Generate Balance Sheet report.

        Formula: Assets = Liabilities + Equity + Retained Earnings
        """
        assets = FinancialReportRepository.get_account_balances_by_type(AccountType.ASSET, end_date)
        liabilities = FinancialReportRepository.get_account_balances_by_type(AccountType.LIABILITY, end_date)
        equity = FinancialReportRepository.get_account_balances_by_type(AccountType.EQUITY, end_date)

        total_assets = sum(a["balance"] for a in assets)
        total_liabilities = sum(l["balance"] for l in liabilities)
        total_equity = sum(e["balance"] for e in equity)

        retained_earnings = FinancialReportRepository.get_account_type_balance(AccountType.REVENUE, end_date) - \
                           FinancialReportRepository.get_account_type_balance(AccountType.EXPENSE, end_date)

        total_liab_equity = total_liabilities + total_equity + retained_earnings

        return {
            "end_date": end_date,
            "assets": assets,
            "liabilities": liabilities,
            "equity": equity,
            "total_assets": total_assets,
            "total_liabilities": total_liabilities,
            "total_equity": total_equity,
            "total_liab_equity": total_liab_equity,
            "retained_earnings": retained_earnings,
            "is_balanced": abs(total_assets - total_liab_equity) == Decimal("0"),
        }


class IncomeStatementService:
    """Service for Income Statement (Báo cáo kết quả kinh doanh)."""

    @staticmethod
    def get_income_statement(start_date: date, end_date: date) -> Dict:
        """Generate Income Statement report.

        Formula: Profit = Revenue - Expenses (for the period)
        """
        prior_revenue = FinancialReportRepository.get_account_type_balance(AccountType.REVENUE, start_date - timedelta(days=1))
        prior_expenses = FinancialReportRepository.get_account_type_balance(AccountType.EXPENSE, start_date - timedelta(days=1))

        revenue_end = FinancialReportRepository.get_account_type_balance(AccountType.REVENUE, end_date)
        expenses_end = FinancialReportRepository.get_account_type_balance(AccountType.EXPENSE, end_date)

        revenue_period = revenue_end - prior_revenue
        expenses_period = expenses_end - prior_expenses

        revenue = FinancialReportRepository.get_account_balances_by_type(AccountType.REVENUE, end_date)
        expenses = FinancialReportRepository.get_account_balances_by_type(AccountType.EXPENSE, end_date)

        total_revenue = revenue_period
        total_expenses = expenses_period

        gross_profit = total_revenue - total_expenses
        net_profit_before_tax = gross_profit
        net_profit_after_tax = net_profit_before_tax

        return {
            "start_date": start_date,
            "end_date": end_date,
            "revenue": revenue,
            "expenses": expenses,
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "gross_profit": gross_profit,
            "net_profit_before_tax": net_profit_before_tax,
            "net_profit_after_tax": net_profit_after_tax,
        }


class CashFlowService:
    """Service for Cash Flow Statement (Lưu chuyển tiền tệ) - Indirect Method."""

    @staticmethod
    def get_cash_flow(start_date: date, end_date: date) -> Dict:
        """Generate Cash Flow report using indirect method.

        Formula:
        Cash from Operating Activities
        + Cash from Investing Activities  
        + Cash from Financing Activities
        = Net Cash Flow
        
        Operating Activities = Net Profit + Depreciation + Changes in Working Capital
        """

        net_profit = IncomeStatementService.get_income_statement(start_date, end_date)["net_profit_after_tax"]

        from models.account import Account
        from core.database import db
        
        cash_accounts = Account.query.filter(Account.code.like("11%")).all()
        cash_change = sum(
            FinancialReportRepository.get_account_period_balance(acc.code, start_date, end_date) 
            for acc in cash_accounts
        )
        
        ar_accounts = Account.query.filter(Account.code.like("13%")).all()
        accounts_receivable_change = sum(
            FinancialReportRepository.get_account_period_balance(acc.code, start_date, end_date) 
            for acc in ar_accounts
        )
        
        inventory_accounts = Account.query.filter(Account.code.like("15%")).all()
        inventory_change = sum(
            FinancialReportRepository.get_account_period_balance(acc.code, start_date, end_date) 
            for acc in inventory_accounts
        )
        
        ap_accounts = Account.query.filter(Account.code.like("33%")).all()
        accounts_payable_change = sum(
            FinancialReportRepository.get_account_period_balance(acc.code, start_date, end_date) 
            for acc in ap_accounts
        )

        working_capital_change = -accounts_receivable_change - inventory_change + accounts_payable_change

        cash_from_operating = net_profit + working_capital_change

        cash_from_investing = Decimal("0")

        loan_accounts = Account.query.filter(Account.code.like("34%")).all()
        loans_change = sum(
            FinancialReportRepository.get_account_period_balance(acc.code, start_date, end_date) 
            for acc in loan_accounts
        )
        
        capital_accounts = Account.query.filter(Account.code.like("41%")).all()
        capital_change = sum(
            FinancialReportRepository.get_account_period_balance(acc.code, start_date, end_date) 
            for acc in capital_accounts
        )
        cash_from_financing = loans_change + capital_change

        net_cash_flow = cash_from_operating + cash_from_investing + cash_from_financing

        opening_cash = FinancialReportRepository.get_account_type_balance(AccountType.ASSET, start_date)
        opening_cash = Decimal("0")

        closing_cash = opening_cash + net_cash_flow

        return {
            "start_date": start_date,
            "end_date": end_date,
            "net_profit": net_profit,
            "working_capital_change": working_capital_change,
            "cash_from_operating": cash_from_operating,
            "cash_from_investing": cash_from_investing,
            "cash_from_financing": cash_from_financing,
            "net_cash_flow": net_cash_flow,
            "opening_cash": opening_cash,
            "closing_cash": closing_cash,
        }


class FinancialReportService:
    """Unified service for all financial reports."""

    @staticmethod
    def get_balance_sheet(end_date: date) -> Dict:
        """Get Balance Sheet."""
        return BalanceSheetService.get_balance_sheet(end_date)

    @staticmethod
    def get_income_statement(start_date: date, end_date: date) -> Dict:
        """Get Income Statement."""
        return IncomeStatementService.get_income_statement(start_date, end_date)

    @staticmethod
    def get_cash_flow(start_date: date, end_date: date) -> Dict:
        """Get Cash Flow Statement."""
        return CashFlowService.get_cash_flow(start_date, end_date)

    @staticmethod
    def validate_financial_statements(start_date: date, end_date: date) -> Dict:
        """Validate that all financial statements are consistent."""
        balance_sheet = BalanceSheetService.get_balance_sheet(end_date)
        income_stmt = IncomeStatementService.get_income_statement(start_date, end_date)

        return {
            "balance_sheet_balanced": balance_sheet["is_balanced"],
            "net_profit": income_stmt["net_profit_after_tax"],
            "retained_earnings_change": balance_sheet["retained_earnings"] - income_stmt["net_profit_after_tax"],
        }
