"""
Document Routes - Document management endpoints.
Handles documents, attachments, and templates.
"""

from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify, send_file
from flask_login import current_user

from core.rbac import permission_required
from core.database import db
from services.document_service import DocumentService
from models.document import Document, DocumentTemplate, DocumentType, DocumentStatus


document_bp = Blueprint("document", __name__, url_prefix="/documents")


@document_bp.route("/")
@permission_required("report", "read")
def index():
    """Document dashboard."""
    stats = DocumentService.get_document_statistics()
    return render_template(
        "accounting/documents/index.html",
        stats=stats,
    )


@document_bp.route("/documents")
@permission_required("report", "read")
def documents():
    """List documents."""
    document_type = request.args.get("document_type")
    status = request.args.get("status")

    query = Document.query
    if document_type:
        query = query.filter_by(document_type=document_type)
    if status:
        query = query.filter_by(status=status)

    documents_list = query.order_by(Document.document_date.desc()).all()
    document_types = DocumentType.CHOICES
    statuses = DocumentStatus.CHOICES

    return render_template(
        "accounting/documents/documents.html",
        documents=documents_list,
        document_types=document_types,
        statuses=statuses,
    )


@document_bp.route("/documents/new", methods=["GET", "POST"])
@permission_required("account", "create")
def document_new():
    """Create new document."""
    if request.method == "GET":
        document_types = DocumentType.CHOICES
        return render_template(
            "accounting/documents/document_form.html",
            document=None,
            document_types=document_types,
        )

    document_date_str = request.form.get("document_date")
    document_date = datetime.strptime(document_date_str, "%Y-%m-%d").date() if document_date_str else date.today()

    success, result = DocumentService.create_document(
        document_type=request.form.get("document_type"),
        document_date=document_date,
        entity_type=request.form.get("entity_type"),
        entity_id=request.form.get("entity_id", type=int),
        voucher_id=request.form.get("voucher_id", type=int),
        reference_no=request.form.get("reference_no"),
        amount=request.form.get("amount"),
        currency=request.form.get("currency", "VND"),
        description=request.form.get("description"),
        created_by=current_user.id if current_user.is_authenticated else 1,
    )

    if success:
        flash("Document created successfully", "success")
        return redirect(url_for("document.document_detail", document_id=result["id"]))
    else:
        flash(result.get("error", "Failed to create document"), "danger")
        document_types = DocumentType.CHOICES
        return render_template(
            "accounting/documents/document_form.html",
            document=request.form,
            document_types=document_types,
        )


@document_bp.route("/documents/<int:document_id>")
@permission_required("report", "read")
def document_detail(document_id: int):
    """Document detail."""
    document = db.session.get(Document, document_id)
    if not document:
        flash("Document not found", "danger")
        return redirect(url_for("document.documents"))

    return render_template(
        "accounting/documents/document_detail.html",
        document=document,
    )


@document_bp.route("/documents/<int:document_id>/approve", methods=["POST"])
@permission_required("account", "update")
def document_approve(document_id: int):
    """Approve document."""
    success, result = DocumentService.approve_document(
        document_id=document_id,
        approver_id=current_user.id if current_user.is_authenticated else 1,
    )

    if success:
        flash("Document approved", "success")
    else:
        flash(result.get("error", "Failed to approve"), "danger")

    return redirect(url_for("document.document_detail", document_id=document_id))


@document_bp.route("/documents/<int:document_id>/sign", methods=["POST"])
@permission_required("account", "update")
def document_sign(document_id: int):
    """Sign document."""
    success, result = DocumentService.sign_document(
        document_id=document_id,
        signer_id=current_user.id if current_user.is_authenticated else 1,
    )

    if success:
        flash("Document signed", "success")
    else:
        flash(result.get("error", "Failed to sign"), "danger")

    return redirect(url_for("document.document_detail", document_id=document_id))


@document_bp.route("/templates")
@permission_required("report", "read")
def templates():
    """List document templates."""
    templates_list = DocumentTemplate.query.filter_by(is_active=True).order_by(
        DocumentTemplate.code
    ).all()
    return render_template(
        "accounting/documents/templates.html",
        templates=templates_list,
    )


@document_bp.route("/templates/new", methods=["GET", "POST"])
@permission_required("account", "create")
def template_new():
    """Create new template."""
    if request.method == "GET":
        document_types = DocumentType.CHOICES
        return render_template(
            "accounting/documents/template_form.html",
            template=None,
            document_types=document_types,
        )

    success, result = DocumentService.create_template(
        code=request.form.get("code"),
        name=request.form.get("name"),
        document_type=request.form.get("document_type"),
        description=request.form.get("description"),
        template_content=request.form.get("template_content"),
        created_by=current_user.id if current_user.is_authenticated else 1,
    )

    if success:
        flash("Template created successfully", "success")
        return redirect(url_for("document.templates"))
    else:
        flash(result.get("error", "Failed to create template"), "danger")
        document_types = DocumentType.CHOICES
        return render_template(
            "accounting/documents/template_form.html",
            template=request.form,
            document_types=document_types,
        )


@document_bp.route("/api/documents")
@permission_required("report", "read")
def api_documents():
    """API: List documents."""
    documents_list = Document.query.order_by(
        Document.document_date.desc()
    ).limit(100).all()
    return jsonify({
        "status": "success",
        "data": [d.to_dict() for d in documents_list],
    })


@document_bp.route("/api/templates")
@permission_required("report", "read")
def api_templates():
    """API: List templates."""
    templates_list = DocumentTemplate.query.filter_by(is_active=True).all()
    return jsonify({
        "status": "success",
        "data": [t.to_dict() for t in templates_list],
    })
