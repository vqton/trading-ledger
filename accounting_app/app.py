import os

from flask import Flask
from flask_login import LoginManager

from config import config
from core.database import db, init_db
from core.logging import setup_logging
from core.security import User


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: int) -> User:
    """Load user by ID for Flask-Login."""
    return db.session.get(User, int(user_id))


def create_app(config_name: str = None) -> Flask:
    """Application factory."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    setup_logging(app)

    # Request/Response logging for development
    if app.config.get("DEBUG"):
        import logging
        import time
        
        request_logger = logging.getLogger("requests")
        
        @app.before_request
        def log_request():
            from flask import request, g
            g.start_time = time.time()
            request_logger.debug(f"→ {request.method} {request.path} | Args: {request.args} | Form: {request.form}")
        
        @app.after_request
        def log_response(response):
            from flask import request, g
            duration = time.time() - g.get("start_time", time.time())
            request_logger.debug(f"← {request.method} {request.path} | Status: {response.status_code} | Duration: {duration:.3f}s")
            return response

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    with app.app_context():
        from models.account import Account
        from models.journal import JournalVoucher, JournalEntry
        from models.inventory import InventoryItem, Warehouse, StockTransaction
        from models.audit_log import AuditLog
        
        init_db(app)
        from core.security import create_default_roles, create_admin_user
        create_default_roles()
        create_admin_user()
        
        from models.seed_data import create_chart_of_accounts
        create_chart_of_accounts()

    from routes.auth_routes import auth_bp
    from routes.accounting_routes import accounting_bp
    from routes.tax_routes import tax_bp
    from routes.partner_routes import partner_bp
    from routes.financial_routes import financial_bp
    from routes.cost_center_routes import cost_center_bp
    from routes.project_routes import project_bp
    from routes.tax_payment_routes import tax_payment_bp
    from routes.approval_routes import approval_bp
    from routes.document_routes import document_bp
    from routes.notification_routes import notification_bp
    from routes.settings_routes import settings_bp
    from routes.backup_routes import backup_bp
    from routes.biological_routes import biological_bp
    from routes.dividend_routes import dividend_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(accounting_bp)
    app.register_blueprint(tax_bp)
    app.register_blueprint(partner_bp)
    app.register_blueprint(financial_bp)
    app.register_blueprint(cost_center_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(tax_payment_bp)
    app.register_blueprint(approval_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(biological_bp)
    app.register_blueprint(dividend_bp)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        from core.database import db
        db.session.remove()

    @app.route("/")
    def index():
        from flask import render_template, redirect, url_for
        from flask_login import current_user
        from datetime import date
        
        if current_user.is_authenticated:
            from services.account_service import AccountService
            kpis = AccountService.get_dashboard_kpis(date.today())
            
            from models.journal import JournalVoucher, VoucherStatus
            recent_vouchers = JournalVoucher.query.filter(
                JournalVoucher.status == VoucherStatus.DRAFT
            ).order_by(JournalVoucher.created_at.desc()).limit(5).all()
            
            return render_template(
                "index.html",
                kpis=kpis,
                recent_vouchers=recent_vouchers
            )
        
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
