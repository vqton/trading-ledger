from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import date, datetime
from sqlalchemy import or_, func

from core.database import db
from models.journal import JournalVoucher, JournalEntry, VoucherStatus
from models.account import Account
from models.partner import Partner
from models.notification import Notification

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


@api_bp.route('/kpi/summary', methods=['GET'])
@login_required
def kpi_summary():
    today = date.today()
    current_month = today.month
    current_year = today.year

    entries = db.session.query(
        func.sum(JournalEntry.debit).label('total_debit'),
        func.sum(JournalEntry.credit).label('total_credit')
    ).join(
        JournalVoucher, JournalVoucher.id == JournalEntry.voucher_id
    ).filter(
        JournalVoucher.status == VoucherStatus.APPROVED,
        func.extract('month', JournalVoucher.voucher_date) == current_month,
        func.extract('year', JournalVoucher.voucher_date) == current_year
    ).first()

    total_debit = float(entries.total_debit or 0)
    total_credit = float(entries.total_credit or 0)

    return jsonify({
        'total_debit': total_debit,
        'total_credit': total_credit,
        'difference': total_debit - total_credit,
        'period': f'{current_month:02d}/{current_year}'
    })


@api_bp.route('/notifications/count', methods=['GET'])
@login_required
def notification_count():
    count = Notification.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).count()
    return jsonify({'count': count})


@api_bp.route('/search', methods=['GET'])
@login_required
def global_search():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'results': []})

    results = []
    query_lower = query.lower()

    vouchers = JournalVoucher.query.filter(
        or_(
            JournalVoucher.voucher_no.ilike(f'%{query}%'),
            JournalVoucher.description.ilike(f'%{query}%')
        )
    ).limit(5).all()
    for v in vouchers:
        results.append({
            'type': 'CT',
            'title': f'{v.voucher_no} - {v.description[:50]}',
            'meta': v.voucher_date.strftime('%d/%m/%Y'),
            'url': f'/accounting/voucher/{v.id}',
            'icon': 'fa-file-invoice'
        })

    accounts = Account.query.filter(
        or_(
            Account.account_code.ilike(f'%{query}%'),
            Account.account_name.ilike(f'%{query}%')
        )
    ).limit(5).all()
    for a in accounts:
        results.append({
            'type': 'TK',
            'title': f'{a.account_code} - {a.account_name}',
            'meta': a.account_type,
            'url': f'/accounting/ledger/{a.id}',
            'icon': 'fa-sitemap'
        })

    partners = Partner.query.filter(
        or_(
            Partner.code.ilike(f'%{query}%'),
            Partner.name.ilike(f'%{query}%')
        )
    ).limit(5).all()
    for p in partners:
        partner_type = 'Khách hàng' if p.partner_type.value == 'customer' else 'Nhà cung cấp'
        results.append({
            'type': partner_type[:2],
            'title': f'{p.code} - {p.name}',
            'meta': partner_type,
            'url': f'/partner/{p.id}',
            'icon': 'fa-address-book'
        })

    return jsonify({'results': results})
