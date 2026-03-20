from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from models.account import Account, AccountType
from repositories.financial_report_repository import FinancialReportRepository
from repositories.ledger_repository import LedgerRepository
from repositories.account_repository import AccountRepository


def _line(ma_so: str, name: str, amount: Decimal) -> Dict:
    """Create a report line item with TT99 Mã số."""
    return {"ma_so": ma_so, "name": name, "amount": amount}


class BalanceSheetService:
    """Báo cáo tình hình tài chính - Mẫu B01-DN per TT99/2025/TT-BTC."""

    @staticmethod
    def _get_line_balance(
        debit_accounts: List[str],
        credit_accounts: List[str],
        end_date: date,
    ) -> Decimal:
        """Calculate balance = Σdebit_accounts - Σcredit_accounts (cumulative)."""
        debit_total = Decimal("0")
        credit_total = Decimal("0")

        if debit_accounts:
            debit_total = FinancialReportRepository.get_account_prefix_balance(
                debit_accounts, end_date, is_debit_normal=True
            )
        if credit_accounts:
            credit_total = FinancialReportRepository.get_account_prefix_balance(
                credit_accounts, end_date, is_debit_normal=False
            )

        return debit_total - credit_total

    @staticmethod
    def get_balance_sheet(end_date: date) -> Dict:
        """Generate B01-DN: Báo cáo tình hình tài chính.

        Structure per TT99:
        A. TÀI SẢN
          100 Tài sản ngắn hạn (110+120+130+140+160)
          200 Tài sản dài hạn (210+220+240+260+270)
        B. NỢ PHẢI TRẢ
          300 Nợ ngắn hạn (310+330+340+350)
          400 Nợ dài hạn (410+420)
        C. VỐN CHỦ SỞ HỮU
          500 Vốn chủ sở hữu (510+520)
        """
        get = BalanceSheetService._get_line_balance

        # --- A. TÀI SẢN (ASSETS) ---

        # Money and cash equivalents (110)
        tien_111 = get(["111", "112", "113"], [], end_date)
        tuong_duong_tien_112 = get(["1281"], [], end_date)
        tien_va_ttdt_110 = tien_111 + tuong_duong_tien_112

        # Short-term financial investments (120)
        dau_tu_tc_nn_120 = get(["121"], ["2291"], end_date)

        # Short-term receivables (130)
        phai_thu_nn_kh_131 = get(["131"], ["2293"], end_date)
        phai_thu_nn_khac_135 = get(["1388", "141"], [], end_date)
        phai_thu_nn_130 = phai_thu_nn_kh_131 + phai_thu_nn_khac_135

        # Inventories (140)
        hang_ton_kho_141 = get(["151", "152", "153", "154", "155", "156", "157", "158"], [], end_date)
        dp_giam_gia_htk_142 = get([], ["2294"], end_date)
        hang_ton_kho_140 = hang_ton_kho_141 + dp_giam_gia_htk_142

        # Other short-term assets (160)
        cp_tra_truoc_161 = get(["242"], [], end_date)
        thue_gtgt_162 = get(["133"], [], end_date)
        thue_phai_thu_163 = get(["333"], [], end_date)
        ts_nn_khac_160 = cp_tra_truoc_161 + thue_gtgt_162 + thue_phai_thu_163

        # SHORT-TERM ASSETS (100)
        tai_san_nn_100 = tien_va_ttdt_110 + dau_tu_tc_nn_120 + phai_thu_nn_130 + hang_ton_kho_140 + ts_nn_khac_160

        # --- LONG-TERM ASSETS (200) ---

        # Long-term receivables (210)
        phai_thu_dlh_210 = get(["136", "1388"], ["2293"], end_date)

        # Fixed assets (220)
        tsdh_nguyen_gia_221 = get(["211"], ["2141"], end_date)
        tsttc_nguyen_gia_224 = get(["212"], ["2142"], end_date)
        tsvh_nguyen_gia_227 = get(["213"], ["2143"], end_date)
        tai_san_co_dinh_220 = tsdh_nguyen_gia_221 + tsttc_nguyen_gia_224 + tsvh_nguyen_gia_227

        # Investment property (240)
        bds_dau_tu_240 = get(["217"], ["2147"], end_date)

        # Long-term financial investments (260)
        dau_tu_dlh_260 = get(["221", "222", "2282"], ["2292"], end_date)

        # Other long-term assets (270)
        cp_sxkd_dodang_271 = get(["154"], [], end_date)
        xdcb_dodang_272 = get(["241"], [], end_date)
        ts_dlh_khac_270 = cp_sxkd_dodang_271 + xdcb_dodang_272

        # LONG-TERM ASSETS (200)
        tai_san_dlh_200 = phai_thu_dlh_210 + tai_san_co_dinh_220 + bds_dau_tu_240 + dau_tu_dlh_260 + ts_dlh_khac_270

        # TOTAL ASSETS
        tong_tai_san = tai_san_nn_100 + tai_san_dlh_200

        # --- B. NỢ PHẢI TRẢ (LIABILITIES) ---

        # SHORT-TERM LIABILITIES (300)
        phai_tra_nguoi_ban_310 = get([], ["331"], end_date)
        thue_va_nop_ns_330 = get([], ["333"], end_date)
        phai_tra_nld_340 = get([], ["334"], end_date)
        no_nn_khac_350 = get([], ["336", "338", "341"], end_date)
        no_nn_300 = phai_tra_nguoi_ban_310 + thue_va_nop_ns_330 + phai_tra_nld_340 + no_nn_khac_350

        # LONG-TERM LIABILITIES (400)
        pt_nb_dlh_410 = get([], ["331"], end_date)
        vay_dlh_420 = get([], ["341"], end_date)
        no_dlh_400 = pt_nb_dlh_410 + vay_dlh_420

        # TOTAL LIABILITIES
        tong_no = no_nn_300 + no_dlh_400

        # --- C. VỐN CHỦ SỞ HỮU (EQUITY) ---

        # Owner's equity (510)
        von_gop_510 = get([], ["411"], end_date)

        # Retained earnings (520) - use account 421
        loi_nhuan_chua_pp_520 = get([], ["421"], end_date)

        # TOTAL EQUITY (500)
        tong_von_csh_500 = von_gop_510 + loi_nhuan_chua_pp_520

        # BALANCE CHECK
        tong_nguon_von = tong_no + tong_von_csh_500
        is_balanced = abs(tong_tai_san - tong_nguon_von) < Decimal("0.01")

        return {
            "report_name": "Báo cáo tình hình tài chính",
            "report_code": "B01-DN",
            "end_date": end_date,
            "is_balanced": is_balanced,
            "assets": {
                "short_term": {
                    "100": _line("100", "Tài sản ngắn hạn", tai_san_nn_100),
                    "110": _line("110", "Tiền và các khoản tương đương tiền", tien_va_ttdt_110),
                    "111": _line("111", "Tiền", tien_111),
                    "112": _line("112", "Các khoản tương đương tiền", tuong_duong_tien_112),
                    "120": _line("120", "Đầu tư tài chính ngắn hạn", dau_tu_tc_nn_120),
                    "130": _line("130", "Các khoản phải thu ngắn hạn", phai_thu_nn_130),
                    "131": _line("131", "Phải thu ngắn hạn của khách hàng", phai_thu_nn_kh_131),
                    "135": _line("135", "Phải thu ngắn hạn khác", phai_thu_nn_khac_135),
                    "140": _line("140", "Hàng tồn kho", hang_ton_kho_140),
                    "141": _line("141", "Hàng tồn kho", hang_ton_kho_141),
                    "142": _line("142", "Dự phòng giảm giá hàng tồn kho", dp_giam_gia_htk_142),
                    "160": _line("160", "Tài sản ngắn hạn khác", ts_nn_khac_160),
                    "161": _line("161", "Chi phí trả trước ngắn hạn", cp_tra_truoc_161),
                    "162": _line("162", "Thuế GTGT được khấu trừ", thue_gtgt_162),
                    "163": _line("163", "Thuế và các khoản khác phải thu Nhà nước", thue_phai_thu_163),
                },
                "long_term": {
                    "200": _line("200", "Tài sản dài hạn", tai_san_dlh_200),
                    "210": _line("210", "Các khoản phải thu dài hạn", phai_thu_dlh_210),
                    "220": _line("220", "Tài sản cố định", tai_san_co_dinh_220),
                    "221": _line("221", "TSCĐ hữu hình", tsdh_nguyen_gia_221),
                    "224": _line("224", "TSCĐ thuê tài chính", tsttc_nguyen_gia_224),
                    "227": _line("227", "TSCĐ vô hình", tsvh_nguyen_gia_227),
                    "240": _line("240", "Bất động sản đầu tư", bds_dau_tu_240),
                    "260": _line("260", "Đầu tư tài chính dài hạn", dau_tu_dlh_260),
                    "270": _line("270", "Tài sản dài hạn khác", ts_dlh_khac_270),
                    "271": _line("271", "Chi phí sản xuất kinh doanh dở dang dài hạn", cp_sxkd_dodang_271),
                    "272": _line("272", "Xây dựng cơ bản dở dang", xdcb_dodang_272),
                },
                "total": tong_tai_san,
            },
            "liabilities": {
                "short_term": {
                    "300": _line("300", "Nợ ngắn hạn", no_nn_300),
                    "310": _line("310", "Phải trả người bán ngắn hạn", phai_tra_nguoi_ban_310),
                    "330": _line("330", "Thuế và các khoản phải nộp Nhà nước", thue_va_nop_ns_330),
                    "340": _line("340", "Phải trả người lao động", phai_tra_nld_340),
                    "350": _line("350", "Nợ ngắn hạn khác", no_nn_khac_350),
                },
                "long_term": {
                    "400": _line("400", "Nợ dài hạn", no_dlh_400),
                    "410": _line("410", "Phải trả người bán dài hạn", pt_nb_dlh_410),
                    "420": _line("420", "Vay và nợ thuê tài chính dài hạn", vay_dlh_420),
                },
                "total": tong_no,
            },
            "equity": {
                "500": _line("500", "Vốn chủ sở hữu", tong_von_csh_500),
                "510": _line("510", "Vốn đầu tư của chủ sở hữu", von_gop_510),
                "520": _line("520", "Lợi nhuận sau thuế chưa phân phối", loi_nhuan_chua_pp_520),
                "total": tong_von_csh_500,
            },
            "total_liabilities_equity": tong_nguon_von,
        }


class IncomeStatementService:
    """Báo cáo kết quả hoạt động kinh doanh - Mẫu B02-DN per TT99/2025/TT-BTC."""

    @staticmethod
    def get_income_statement(start_date: date, end_date: date) -> Dict:
        """Generate B02-DN: Báo cáo kết quả hoạt động kinh doanh.

        Structure per TT99:
        10  Doanh thu bán hàng và CCDV
        20  Các khoản giảm trừ doanh thu (âm)
        30  Doanh thu thuần (= 10 - 20)
        40  Giá vốn hàng bán
        50  Lợi nhuận gộp (= 30 - 40)
        60  Doanh thu hoạt động tài chính
        70  Chi phí tài chính
        80  Chi phí bán hàng
        90  Chi phí quản lý doanh nghiệp
        100 Lợi nhuận khác, chi phí khác
        120 Lợi nhuận trước thuế TNDN (= 50+60-70-80-90+100)
        130 Chi phí thuế TNDN hiện hành
        140 Chi phí thuế TNDN hoãn lại
        150 Lợi nhuận sau thuế TNDN (= 120-130-140)
        """
        # Period credit sums (revenue type accounts)
        def period_credit(codes: List[str]) -> Decimal:
            if not codes:
                return Decimal("0")
            return FinancialReportRepository.get_period_credit_sum(codes, start_date, end_date)

        # Period debit sums (expense type accounts)
        def period_debit(codes: List[str]) -> Decimal:
            if not codes:
                return Decimal("0")
            return FinancialReportRepository.get_period_debit_sum(codes, start_date, end_date)

        # 10: Revenue
        doanh_thu_10 = period_credit(["511"])

        # 20: Sales deductions (negative)
        giam_tru_dt_20 = period_debit(["521"])

        # 30: Net revenue
        dt_thuan_30 = doanh_thu_10 - giam_tru_dt_20

        # 40: COGS
        gia_von_40 = period_debit(["632"])

        # 50: Gross profit
        loi_nhuan_gop_50 = dt_thuan_30 - gia_von_40

        # 60: Financial revenue
        dt_tai_chinh_60 = period_credit(["515"])

        # 70: Financial expenses
        cp_tai_chinh_70 = period_debit(["635"])

        # 80: Selling expenses
        cp_ban_hang_80 = period_debit(["641"])

        # 90: Administrative expenses
        cp_qldn_90 = period_debit(["642"])

        # 100: Other profit
        loi_nhuan_khac_711 = period_credit(["711"])
        chi_phi_khac_811 = period_debit(["811"])
        loi_nhuan_khac_100 = loi_nhuan_khac_711 - chi_phi_khac_811

        # 120: Profit before tax
        loi_nhuan_truoc_thue_120 = (
            loi_nhuan_gop_50 + dt_tai_chinh_60 - cp_tai_chinh_70
            - cp_ban_hang_80 - cp_qldn_90 + loi_nhuan_khac_100
        )

        # 130: Current CIT expense
        thue_tndn_hh_130 = period_debit(["8211"])

        # 140: Deferred CIT expense
        thue_tndn_dl_140 = period_debit(["8212"])

        # 150: Profit after tax
        loi_nhuan_sau_thue_150 = loi_nhuan_truoc_thue_120 - thue_tndn_hh_130 - thue_tndn_dl_140

        return {
            "report_name": "Báo cáo kết quả hoạt động kinh doanh",
            "report_code": "B02-DN",
            "start_date": start_date,
            "end_date": end_date,
            "lines": {
                "10": _line("10", "Doanh thu bán hàng và cung cấp dịch vụ", doanh_thu_10),
                "20": _line("20", "Các khoản giảm trừ doanh thu", giam_tru_dt_20),
                "30": _line("30", "Doanh thu thuần", dt_thuan_30),
                "40": _line("40", "Giá vốn hàng bán", gia_von_40),
                "50": _line("50", "Lợi nhuận gộp", loi_nhuan_gop_50),
                "60": _line("60", "Doanh thu hoạt động tài chính", dt_tai_chinh_60),
                "70": _line("70", "Chi phí tài chính", cp_tai_chinh_70),
                "80": _line("80", "Chi phí bán hàng", cp_ban_hang_80),
                "90": _line("90", "Chi phí quản lý doanh nghiệp", cp_qldn_90),
                "100": _line("100", "Lợi nhuận khác, chi phí khác", loi_nhuan_khac_100),
                "120": _line("120", "Lợi nhuận trước thuế TNDN", loi_nhuan_truoc_thue_120),
                "130": _line("130", "Chi phí thuế TNDN hiện hành", thue_tndn_hh_130),
                "140": _line("140", "Chi phí thuế TNDN hoãn lại", thue_tndn_dl_140),
                "150": _line("150", "Lợi nhuận sau thuế TNDN", loi_nhuan_sau_thue_150),
            },
            "net_profit_after_tax": loi_nhuan_sau_thue_150,
            "profit_before_tax": loi_nhuan_truoc_thue_120,
        }


class CashFlowService:
    """Báo cáo lưu chuyển tiền tệ - Mẫu B03-DN per TT99/2025/TT-BTC.
    
    Indirect method: starts from profit before tax, adjusts for non-cash items
    and working capital changes.
    """

    @staticmethod
    def get_cash_flow(start_date: date, end_date: date) -> Dict:
        """Generate B03-DN: Báo cáo lưu chuyển tiền tệ (Phương pháp gián tiếp).

        I.   LCTT từ hoạt động kinh doanh
        II.  LCTT từ hoạt động đầu tư
        III. LCTT từ hoạt động tài chính
        IV.  LCTT ròng trong kỳ
        V.   Tiền và TTT đầu kỳ
        VI.  Tiền và TTT cuối kỳ
        """
        # Helper functions
        def period_dr_minus_cr(codes: List[str]) -> Decimal:
            if not codes:
                return Decimal("0")
            return FinancialReportRepository.get_period_change_debit_minus_credit(
                codes, start_date, end_date
            )

        def period_cr_minus_dr(codes: List[str]) -> Decimal:
            if not codes:
                return Decimal("0")
            return FinancialReportRepository.get_period_change_credit_minus_debit(
                codes, start_date, end_date
            )

        def period_dr_sum(codes: List[str]) -> Decimal:
            if not codes:
                return Decimal("0")
            return FinancialReportRepository.get_period_debit_sum(codes, start_date, end_date)

        def cumulative_balance(codes: List[str], at_date: date, is_dr: bool) -> Decimal:
            if not codes:
                return Decimal("0")
            return FinancialReportRepository.get_account_prefix_balance(codes, at_date, is_dr)

        # --- Opening cash balance (from account 11x) ---
        opening_cash = cumulative_balance(["111", "112", "113"], start_date - timedelta(days=1), is_dr=True)

        # --- I. OPERATING ACTIVITIES ---
        # 01: Profit before tax (from B02 line 120)
        income = IncomeStatementService.get_income_statement(start_date, end_date)
        profit_before_tax = income["profit_before_tax"]

        # 02: Depreciation of fixed assets (debit to 214x accounts = depreciation expense)
        depreciation = period_dr_sum(["2141", "2142", "2143", "2147"])

        # 11: Increase/decrease in receivables (negative = cash outflow)
        ar_change = period_dr_minus_cr(["131", "136", "1388"])

        # 12: Increase/decrease in inventory (negative = cash outflow)
        inventory_change = period_dr_minus_cr(["151", "152", "153", "154", "155", "156", "157", "158"])

        # 13: Increase/decrease in payables (positive = cash inflow)
        payable_change = period_cr_minus_dr(["331", "333", "334", "338"])

        # Working capital changes: +payables -receivables -inventory
        working_capital = payable_change - ar_change - inventory_change

        # Cash from operations
        cash_from_operations = profit_before_tax + depreciation + working_capital

        # --- II. INVESTING ACTIVITIES ---
        # 21: Purchase of fixed assets (debit to 21x = asset additions, cash outflow)
        fixed_asset_purchases = period_dr_sum(["211", "212", "213", "217"])

        # 22: Sale of fixed assets (credit to 21x = asset disposals, cash inflow)
        fixed_asset_sales = FinancialReportRepository.get_period_credit_sum(
            ["211", "212", "213"], start_date, end_date
        )

        # Long-term investment changes
        lt_investment_change = period_dr_minus_cr(["221", "222", "2282"])

        cash_from_investing = -fixed_asset_purchases + fixed_asset_sales - lt_investment_change

        # --- III. FINANCING ACTIVITIES ---
        # 31: Borrowings / repayments
        loan_change = period_cr_minus_dr(["341"])

        # 32: Capital contributions
        capital_change = period_cr_minus_dr(["411"])

        # 33: Dividends paid (debit to 421 = distributions, cash outflow)
        dividends_paid = period_dr_sum(["421"])

        cash_from_financing = loan_change + capital_change - dividends_paid

        # --- IV. NET CASH FLOW ---
        net_cash_flow = cash_from_operations + cash_from_investing + cash_from_financing

        # --- V. Closing cash balance ---
        closing_cash = cumulative_balance(["111", "112", "113"], end_date, is_dr=True)

        # Validation: opening + net = closing
        calculated_closing = opening_cash + net_cash_flow
        is_reconciled = abs(calculated_closing - closing_cash) < Decimal("0.01")

        return {
            "report_name": "Báo cáo lưu chuyển tiền tệ",
            "report_code": "B03-DN",
            "start_date": start_date,
            "end_date": end_date,
            "is_reconciled": is_reconciled,
            "operating": {
                "01": _line("01", "Lợi nhuận trước thuế", profit_before_tax),
                "02": _line("02", "Khấu hao TSCĐ", depreciation),
                "11": _line("11", "Tăng/giảm các khoản phải thu", -ar_change),
                "12": _line("12", "Tăng/giảm hàng tồn kho", -inventory_change),
                "13": _line("13", "Tăng/giảm các khoản phải trả", payable_change),
                "total": _line("20", "LCTT ròng từ hoạt động KD", cash_from_operations),
            },
            "investing": {
                "21": _line("21", "Mua sắm TSCĐ, BĐSĐT", -fixed_asset_purchases),
                "22": _line("22", "Thu tiền từ bán TSCĐ", fixed_asset_sales),
                "total": _line("30", "LCTT ròng từ hoạt động đầu tư", cash_from_investing),
            },
            "financing": {
                "31": _line("31", "Vay thêm / trả nợ vay", loan_change),
                "32": _line("32", "Vốn góp thêm / mua lại cổ phiếu", capital_change),
                "33": _line("33", "Chi trả cổ tức và lợi nhuận", -dividends_paid),
                "total": _line("40", "LCTT ròng từ hoạt động tài chính", cash_from_financing),
            },
            "summary": {
                "net_cash_flow": _line("IV", "LCTT ròng trong kỳ", net_cash_flow),
                "opening_cash": _line("V", "Tiền và TTT đầu kỳ", opening_cash),
                "closing_cash": _line("VI", "Tiền và TTT cuối kỳ", closing_cash),
            },
        }


class FinancialReportService:
    """Unified service for all financial reports - TT99/2025/TT-BTC compliant."""

    @staticmethod
    def get_balance_sheet(end_date: date) -> Dict:
        """Get B01-DN: Báo cáo tình hình tài chính."""
        return BalanceSheetService.get_balance_sheet(end_date)

    @staticmethod
    def get_income_statement(start_date: date, end_date: date) -> Dict:
        """Get B02-DN: Báo cáo kết quả hoạt động kinh doanh."""
        return IncomeStatementService.get_income_statement(start_date, end_date)

    @staticmethod
    def get_cash_flow(start_date: date, end_date: date) -> Dict:
        """Get B03-DN: Báo cáo lưu chuyển tiền tệ."""
        return CashFlowService.get_cash_flow(start_date, end_date)

    @staticmethod
    def validate_financial_statements(start_date: date, end_date: date) -> Dict:
        """Validate that all financial statements are consistent."""
        balance_sheet = BalanceSheetService.get_balance_sheet(end_date)
        income_stmt = IncomeStatementService.get_income_statement(start_date, end_date)
        cash_flow = CashFlowService.get_cash_flow(start_date, end_date)

        bs_net_profit = income_stmt["net_profit_after_tax"]
        bs_retained = balance_sheet["equity"]["520"]["amount"]

        return {
            "balance_sheet_balanced": balance_sheet["is_balanced"],
            "cash_flow_reconciled": cash_flow["is_reconciled"],
            "net_profit_after_tax": bs_net_profit,
            "retained_earnings": bs_retained,
            "profit_to_retained_diff": abs(bs_retained - bs_net_profit),
            "all_valid": balance_sheet["is_balanced"] and cash_flow["is_reconciled"],
        }
