"""
Biological Asset Routes - TK 215 biological asset endpoints.
Circular 99/2025/TT-BTC compliant biological asset management.
"""

from datetime import date
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user

from core.rbac import permission_required
from core.database import db
from services.biological_asset_service import BiologicalAssetService
from models.biological_asset import BiologicalAsset, BiologicalAssetType, BiologicalAssetStatus


biological_bp = Blueprint("biological", __name__, url_prefix="/biological")


@biological_bp.route("/")
@permission_required("report", "read")
def index():
    """Biological asset dashboard."""
    stats = BiologicalAssetService.get_asset_statistics()
    totals = BiologicalAssetService.get_total_value()
    return render_template(
        "accounting/biological/index.html",
        stats=stats,
        totals=totals,
    )


@biological_bp.route("/assets")
@permission_required("report", "read")
def assets():
    """List biological assets."""
    asset_type = request.args.get("asset_type")
    status = request.args.get("status")

    assets_list = BiologicalAssetService.get_assets(
        asset_type=asset_type,
        status=status,
        is_active=True,
    )

    asset_types = BiologicalAssetType.CHOICES
    statuses = BiologicalAssetStatus.CHOICES

    return render_template(
        "accounting/biological/assets.html",
        assets=assets_list,
        asset_types=asset_types,
        statuses=statuses,
    )


@biological_bp.route("/assets/new", methods=["GET", "POST"])
@permission_required("account", "create")
def asset_new():
    """Create new biological asset."""
    if request.method == "GET":
        asset_types = BiologicalAssetType.CHOICES
        return render_template(
            "accounting/biological/asset_form.html",
            asset=None,
            asset_types=asset_types,
        )

    acquisition_date_str = request.form.get("acquisition_date")
    acquisition_date = date.fromisoformat(acquisition_date_str) if acquisition_date_str else date.today()

    success, result = BiologicalAssetService.create_asset(
        code=request.form.get("code"),
        name=request.form.get("name"),
        asset_type=request.form.get("asset_type"),
        category=request.form.get("category"),
        quantity=Decimal(request.form.get("quantity", "0")),
        unit=request.form.get("unit"),
        initial_value=Decimal(request.form.get("initial_value", "0")),
        acquisition_date=acquisition_date,
        location=request.form.get("location"),
        description=request.form.get("description"),
        created_by=current_user.id if current_user.is_authenticated else 1,
    )

    if success:
        flash("Biological asset created successfully", "success")
        return redirect(url_for("biological.asset_detail", asset_id=result["id"]))
    else:
        flash(result.get("error", "Failed to create asset"), "danger")
        asset_types = BiologicalAssetType.CHOICES
        return render_template(
            "accounting/biological/asset_form.html",
            asset=request.form,
            asset_types=asset_types,
        )


@biological_bp.route("/assets/<int:asset_id>")
@permission_required("report", "read")
def asset_detail(asset_id: int):
    """Asset detail."""
    asset = BiologicalAssetService.get_asset_by_id(asset_id)
    if not asset:
        flash("Asset not found", "danger")
        return redirect(url_for("biological.assets"))

    return render_template(
        "accounting/biological/asset_detail.html",
        asset=asset,
    )


@biological_bp.route("/assets/<int:asset_id>/value", methods=["GET", "POST"])
@permission_required("account", "update")
def update_value(asset_id: int):
    """Update fair value."""
    if request.method == "GET":
        asset = BiologicalAssetService.get_asset_by_id(asset_id)
        return render_template(
            "accounting/biological/update_value.html",
            asset=asset,
        )

    fair_value = Decimal(request.form.get("fair_value", "0"))
    valuation_date_str = request.form.get("valuation_date")
    valuation_date = date.fromisoformat(valuation_date_str) if valuation_date_str else None

    success, result = BiologicalAssetService.update_fair_value(
        asset_id=asset_id,
        fair_value=fair_value,
        valuation_date=valuation_date,
    )

    if success:
        flash("Fair value updated successfully", "success")
    else:
        flash(result.get("error", "Failed to update value"), "danger")

    return redirect(url_for("biological.asset_detail", asset_id=asset_id))


@biological_bp.route("/assets/<int:asset_id>/growth", methods=["POST"])
@permission_required("account", "update")
def record_growth(asset_id: int):
    """Record growth/decline change."""
    quantity_change = Decimal(request.form.get("quantity_change", "0"))
    value_change = Decimal(request.form.get("value_change", "0"))
    change_date_str = request.form.get("change_date")
    change_date = date.fromisoformat(change_date_str) if change_date_str else None

    success, result = BiologicalAssetService.record_growth_change(
        asset_id=asset_id,
        quantity_change=quantity_change,
        value_change=value_change,
        description=request.form.get("description"),
        change_date=change_date,
    )

    if success:
        flash("Growth change recorded successfully", "success")
    else:
        flash(result.get("error", "Failed to record change"), "danger")

    return redirect(url_for("biological.asset_detail", asset_id=asset_id))


@biological_bp.route("/assets/<int:asset_id>/dispose", methods=["GET", "POST"])
@permission_required("account", "update")
def dispose_asset(asset_id: int):
    """Dispose biological asset."""
    if request.method == "GET":
        asset = BiologicalAssetService.get_asset_by_id(asset_id)
        return render_template(
            "accounting/biological/dispose_asset.html",
            asset=asset,
        )

    disposal_type = request.form.get("disposal_type")
    disposal_value = Decimal(request.form.get("disposal_value", "0"))
    disposal_date_str = request.form.get("disposal_date")
    disposal_date = date.fromisoformat(disposal_date_str) if disposal_date_str else None

    success, result = BiologicalAssetService.dispose_asset(
        asset_id=asset_id,
        disposal_type=disposal_type,
        disposal_value=disposal_value,
        disposal_date=disposal_date,
        buyer=request.form.get("buyer"),
        notes=request.form.get("notes"),
    )

    if success:
        flash("Asset disposed successfully", "success")
        return redirect(url_for("biological.assets"))
    else:
        flash(result.get("error", "Failed to dispose asset"), "danger")
        return redirect(url_for("biological.asset_detail", asset_id=asset_id))


@biological_bp.route("/api/assets")
@permission_required("report", "read")
def api_assets():
    """API: List biological assets."""
    assets_list = BiologicalAssetService.get_assets(is_active=True)
    return jsonify({
        "status": "success",
        "data": assets_list,
    })


@biological_bp.route("/api/stats")
@permission_required("report", "read")
def api_stats():
    """API: Get asset statistics."""
    stats = BiologicalAssetService.get_asset_statistics()
    totals = BiologicalAssetService.get_total_value()
    return jsonify({
        "status": "success",
        "stats": stats,
        "totals": totals,
    })
