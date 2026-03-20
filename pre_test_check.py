"""
pre_test_check.py - Pre-test verification for VAS Accounting App
=================================================================
Checks templates, routes, services, and dependencies before running tests.

Usage:
    python pre_test_check.py              # full check
    python pre_test_check.py --templates  # templates only
    python pre_test_check.py --routes     # routes only
    python pre_test_check.py --services   # services only

Exit codes:
    0 = all checks passed
    1 = one or more checks failed
"""

import os
import sys
import json
import importlib
import traceback
from datetime import datetime

# Path setup
APP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounting_app")
sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

# ========================================================================
# Result tracking
# ========================================================================

results = {
    "timestamp": datetime.now().isoformat(),
    "checks": [],
    "summary": {"total": 0, "passed": 0, "failed": 0, "warnings": 0},
}


def check(name, passed, message="", warning=False):
    """Record a check result."""
    icon = "✅" if passed else ("⚠️" if warning else "❌")
    status = "pass" if passed else ("warning" if warning else "fail")
    results["checks"].append({"name": name, "status": status, "message": message})
    results["summary"]["total"] += 1
    if passed:
        results["summary"]["passed"] += 1
    elif warning:
        results["summary"]["warnings"] += 1
    else:
        results["summary"]["failed"] += 1
    print(f"  {icon} {name}" + (f" — {message}" if message else ""))


# ========================================================================
# Check 1: Templates exist
# ========================================================================

def check_templates(app):
    """Verify all render_template() targets exist as files."""
    print("\n📁 Checking templates...")
    templates_dir = os.path.join(APP_DIR, "templates")
    missing = []

    # Collect all template references from routes by importing them
    # We do this by scanning source files for render_template calls
    import re
    route_dir = os.path.join(APP_DIR, "routes")
    template_refs = set()

    # Scan app.py
    with open(os.path.join(APP_DIR, "app.py"), "r") as f:
        for match in re.finditer(r'render_template\(\s*["\']([^"\']+)["\']', f.read()):
            template_refs.add(match.group(1))

    # Scan all route files
    for fname in os.listdir(route_dir):
        if fname.endswith(".py") and fname != "__init__.py":
            with open(os.path.join(route_dir, fname), "r") as f:
                for match in re.finditer(r'render_template\(\s*["\']([^"\']+)["\']', f.read()):
                    template_refs.add(match.group(1))

    # Check each template exists
    for tpl in sorted(template_refs):
        tpl_path = os.path.join(templates_dir, tpl)
        if os.path.isfile(tpl_path):
            check(f"template: {tpl}", True)
        else:
            check(f"template: {tpl}", False, f"File not found: templates/{tpl}")
            missing.append(tpl)

    check("All templates exist", len(missing) == 0,
          f"{len(missing)} missing" if missing else f"{len(template_refs)} templates OK")
    return missing


# ========================================================================
# Check 2: Routes registered
# ========================================================================

def check_routes(app):
    """Verify all blueprints are registered and no duplicate endpoints."""
    print("\n🔗 Checking routes...")

    with app.app_context():
        endpoints = {}
        duplicates = []

        for rule in app.url_map.iter_rules():
            if rule.endpoint == "static":
                continue
            ep = rule.endpoint
            if ep in endpoints:
                duplicates.append(ep)
                check(f"endpoint: {ep}", False, f"Duplicate! {endpoints[ep]} and {rule.rule}")
            else:
                endpoints[ep] = rule.rule
                check(f"route: {ep} → {rule.rule}", True)

        check("No duplicate endpoints", len(duplicates) == 0,
              f"{len(duplicates)} duplicates found" if duplicates else "")

        # Check blueprints registered
        expected_blueprints = [
            "auth", "accounting", "financial", "settings",
            "cost_center", "partner", "project", "tax",
            "tax_payment", "approval", "document", "notification",
            "backup", "biological", "dividend",
        ]
        registered = list(app.blueprints.keys())
        missing_bp = [bp for bp in expected_blueprints if bp not in registered]
        extra_bp = [bp for bp in registered if bp not in expected_blueprints]

        check("All expected blueprints registered", len(missing_bp) == 0,
              f"Missing: {missing_bp}" if missing_bp else f"{len(registered)} blueprints")
        if extra_bp:
            check("Extra blueprints", True, f"Extra: {extra_bp}", warning=True)

    return duplicates, missing_bp


# ========================================================================
# Check 3: Service dependencies
# ========================================================================

def check_services():
    """Verify all service modules can be imported (auto-discovered)."""
    print("\n🔧 Checking service imports...")
    import_errors = []
    services_dir = os.path.join(APP_DIR, "services")

    for fname in sorted(os.listdir(services_dir)):
        if fname.endswith("_service.py") or fname.endswith("_engine.py"):
            module_name = fname[:-3]
            module_path = f"services.{module_name}"
            try:
                importlib.import_module(module_path)
                check(f"service: {module_name}", True)
            except Exception as e:
                err_msg = f"{type(e).__name__}: {str(e)[:80]}"
                check(f"service: {module_name}", False, err_msg)
                import_errors.append((module_name, module_path, err_msg))

    check("All services importable", len(import_errors) == 0,
          f"{len(import_errors)} import errors" if import_errors else "")
    return import_errors


# ========================================================================
# Check 4: Core dependencies
# ========================================================================

CORE_DEPS = [
    "flask", "flask_login", "flask_wtf", "flask_sqlalchemy",
    "sqlalchemy", "alembic", "werkzeug", "wtforms",
    "pandas", "openpyxl",
]


def check_dependencies():
    """Verify core Python packages are installed."""
    print("\n📦 Checking dependencies...")
    missing = []

    for pkg in CORE_DEPS:
        try:
            importlib.import_module(pkg)
            check(f"dep: {pkg}", True)
        except ImportError:
            check(f"dep: {pkg}", False, "Not installed")
            missing.append(pkg)

    check("All dependencies installed", len(missing) == 0,
          f"Missing: {missing}" if missing else "")
    return missing


# ========================================================================
# Check 5: Models importable
# ========================================================================

def check_models():
    """Verify all model modules can be imported (auto-discovered)."""
    print("\n📊 Checking model imports...")
    errors = []
    models_dir = os.path.join(APP_DIR, "models")

    for fname in sorted(os.listdir(models_dir)):
        if fname.endswith(".py") and fname != "__init__.py":
            module_name = fname[:-3]
            module_path = f"models.{module_name}"
            try:
                importlib.import_module(module_path)
                check(f"model: {module_name}", True)
            except Exception as e:
                err_msg = f"{type(e).__name__}: {str(e)[:80]}"
                check(f"model: {module_name}", False, err_msg)
                errors.append((module_name, err_msg))

    check("All models importable", len(errors) == 0,
          f"{len(errors)} errors" if errors else "")
    return errors


# ========================================================================
# Check 6: Static files
# ========================================================================

def check_static_files():
    """Verify critical static files exist."""
    print("\n📄 Checking static files...")
    static_dir = os.path.join(APP_DIR, "static")
    required = [
        "css/app.css",
        "js/app.js",
    ]
    missing = []

    for f in required:
        path = os.path.join(static_dir, f)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            check(f"static: {f}", True, f"{size:,} bytes")
        else:
            check(f"static: {f}", False, "Not found")
            missing.append(f)

    check("All static files present", len(missing) == 0, "")
    return missing


# ========================================================================
# Main
# ========================================================================

def run_all():
    """Run all checks."""
    print("=" * 60)
    print("VAS Accounting — Pre-Test Verification")
    print("=" * 60)

    # Create app
    print("\n🚀 Initializing app...")
    try:
        from app import create_app
        app = create_app("testing")
        check("App creation", True)
    except Exception as e:
        check("App creation", False, str(e)[:120])
        _save_report()
        _print_summary()
        return 1

    # Run checks
    check_dependencies()
    check_models()
    check_templates(app)
    check_routes(app)
    check_services()
    check_static_files()

    # Save and report
    _save_report()
    _print_summary()

    return 0 if results["summary"]["failed"] == 0 else 1


def _save_report():
    """Save JSON report."""
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pre_test_report.json")
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Report saved: {report_path}")


def _print_summary():
    """Print summary."""
    s = results["summary"]
    print("\n" + "=" * 60)
    if s["failed"] == 0:
        print(f"✅ All checks passed ({s['passed']} passed, {s['warnings']} warnings)")
    else:
        print(f"❌ {s['failed']} check(s) FAILED ({s['passed']} passed, {s['warnings']} warnings)")
    print("=" * 60)


if __name__ == "__main__":
    # Parse simple args
    args = sys.argv[1:]

    if not args:
        sys.exit(run_all())

    # Partial checks
    print("=" * 60)
    print("VAS Accounting — Pre-Test Verification (partial)")
    print("=" * 60)

    from app import create_app
    app = create_app("testing")

    exit_code = 0
    if "--templates" in args:
        if check_templates(app):
            exit_code = 1
    if "--routes" in args:
        dups, missing = check_routes(app)
        if dups or missing:
            exit_code = 1
    if "--services" in args:
        if check_services():
            exit_code = 1

    _save_report()
    _print_summary()
    sys.exit(exit_code)
