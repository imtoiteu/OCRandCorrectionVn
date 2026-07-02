"""Vietnamese OCR correction — routes (optional, user-triggered).

Adds a correction page and a small JSON API on top of the existing OCR results.
It never modifies the OCR engine or the raw OCR artifacts; corrected output is
stored under separate artifact kinds (`corrected_json`, `corrected_md`,
`corrected_meta`).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Blueprint, request, jsonify, send_from_directory
from flask_login import login_required, current_user

from config import cfg
from models import db, Document, DocumentArtifact, save_artifact, log_activity
from services import vi_correction as vc

BASE = Path(__file__).parent
correction_bp = Blueprint("correction", __name__)


def _defaults() -> dict:
    return {
        "enabled": cfg.VI_CORRECTION_ENABLED,
        "provider": cfg.VI_CORRECTION_PROVIDER,
        "model": cfg.VI_CORRECTION_MODEL,
        "model_path": cfg.VI_CORRECTION_MODEL_PATH,
        "device": cfg.VI_CORRECTION_DEVICE,
        "max_new_tokens": cfg.VI_CORRECTION_MAX_NEW_TOKENS,
        "num_beams": cfg.VI_CORRECTION_NUM_BEAMS,
    }


def _owned_or_403(doc):
    if doc.user_id != current_user.id and current_user.role != "admin":
        return False
    return True


# ── Page ────────────────────────────────────────────────────────────────────
@correction_bp.route("/correction")
@login_required
def correction_page():
    return send_from_directory(str(BASE / "static"), "correction.html")


# ── Config / provider catalogue ─────────────────────────────────────────────
@correction_bp.route("/api/correction/config")
@login_required
def correction_config():
    return jsonify({"success": True, "defaults": _defaults(),
                    "providers": vc.list_providers()})


# ── Documents that have structured OCR JSON (for the picker) ────────────────
@correction_bp.route("/api/correction/documents")
@login_required
def correction_documents():
    is_admin = current_user.role == "admin"
    q = Document.query if is_admin else Document.query.filter_by(user_id=current_user.id)
    docs = q.order_by(Document.upload_date.desc()).limit(200).all()
    ids = [d.id for d in docs]
    have = {}
    if ids:
        for did, kind in (db.session.query(DocumentArtifact.document_id, DocumentArtifact.kind)
                          .filter(DocumentArtifact.document_id.in_(ids)).all()):
            have.setdefault(did, set()).add(kind)
    out = []
    for d in docs:
        kinds = have.get(d.id, set())
        out.append({"id": d.id, "filename": d.filename,
                    "has_ocr_json": "ocr_json" in kinds,
                    "has_corrected": "corrected_json" in kinds})
    return jsonify({"success": True, "documents": out})


# ── Run correction ──────────────────────────────────────────────────────────
@correction_bp.route("/api/correction/run", methods=["POST"])
@login_required
def correction_run():
    if not cfg.VI_CORRECTION_ENABLED:
        return jsonify({"success": False, "error": "Vietnamese correction is disabled (VI_CORRECTION_ENABLED=false)."}), 403
    data = request.get_json(force=True, silent=True) or {}

    d = _defaults()
    provider  = (data.get("provider") or d["provider"]).strip()
    model     = (data.get("model") or d["model"]).strip()
    model_path = (data.get("model_path") or d["model_path"] or "").strip() or None
    device    = (data.get("device") or d["device"]).strip()
    max_new_tokens = data.get("max_new_tokens") or d["max_new_tokens"]
    num_beams = data.get("num_beams") or d["num_beams"]

    # ── resolve input document (canonical: list of pages of block dicts) ──
    doc_id = data.get("doc_id")
    try:
        if doc_id:
            doc = Document.query.get_or_404(int(doc_id))
            if not _owned_or_403(doc):
                return jsonify({"success": False, "error": "Permission denied"}), 403
            art = next((a for a in doc.artifacts if a.kind == "ocr_json"), None)
            if not art:
                return jsonify({"success": False, "error": "This document has no structured OCR JSON. Run OCR first, or paste JSON/text."}), 400
            doc_json = json.loads(art.content)
        elif data.get("ocr_json"):
            raw = data["ocr_json"]
            doc_json = json.loads(raw) if isinstance(raw, str) else raw
        elif data.get("markdown") or data.get("text"):
            doc_json = vc.normalize_input(markdown=data.get("markdown"), text=data.get("text"))
        else:
            return jsonify({"success": False, "error": "No input: provide doc_id, ocr_json, markdown, or text."}), 400
    except json.JSONDecodeError as e:
        return jsonify({"success": False, "error": f"Invalid JSON input: {e}"}), 400

    # ── build provider + check availability (no download here) ──
    try:
        prov = vc.build_provider(provider, model=model, model_path=model_path,
                                 device=device, max_new_tokens=max_new_tokens, num_beams=num_beams)
    except Exception as e:
        return jsonify({"success": False, "error": f"Could not construct provider '{provider}': {e}"}), 400
    ok, reason = prov.available()
    if not ok:
        return jsonify({"success": False, "error": f"Provider '{provider}' unavailable: {reason}"}), 400

    # ── run (model loads lazily; may be slow the first time) ──
    try:
        res = vc.run_correction(doc_json, prov)
    except Exception as e:
        return jsonify({"success": False, "error": f"Correction failed while loading/running the model: {e}"}), 500

    log_activity("vi_correct", f"provider={provider} model={model} device={device} "
                               f"changed={res['counts']['changed']} doc_id={doc_id}")
    return jsonify({"success": True, "provider": provider, "model": model,
                    "device": device, "doc_id": doc_id, "result": res})


# ── Save corrected result (separate from raw OCR; never overwrites content) ──
@correction_bp.route("/api/correction/save", methods=["POST"])
@login_required
def correction_save():
    data = request.get_json(force=True, silent=True) or {}
    doc_id = data.get("doc_id")
    if not doc_id:
        return jsonify({"success": False, "error": "doc_id is required to save."}), 400
    doc = Document.query.get_or_404(int(doc_id))
    if not _owned_or_403(doc):
        return jsonify({"success": False, "error": "Permission denied"}), 403

    saved = []
    cj = data.get("corrected_json")
    if cj is not None:
        content = cj if isinstance(cj, str) else json.dumps(cj, ensure_ascii=False)
        save_artifact(doc.id, "corrected_json", content)
        saved.append("corrected_json")
    md = data.get("corrected_markdown")
    if md is not None:
        save_artifact(doc.id, "corrected_md", md)
        saved.append("corrected_md")
    meta = data.get("meta")
    if meta is not None:
        save_artifact(doc.id, "corrected_meta",
                      meta if isinstance(meta, str) else json.dumps(meta, ensure_ascii=False))
        saved.append("corrected_meta")
    if not saved:
        return jsonify({"success": False, "error": "Nothing to save."}), 400
    log_activity("vi_correct_save", f"doc_id={doc_id} kinds={','.join(saved)}")
    return jsonify({"success": True, "saved": saved})


# ── Fetch a previously saved corrected result ───────────────────────────────
@correction_bp.route("/api/correction/result/<int:doc_id>")
@login_required
def correction_result(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if not _owned_or_403(doc):
        return jsonify({"success": False, "error": "Permission denied"}), 403
    arts = {a.kind: a.content for a in doc.artifacts
            if a.kind in ("corrected_json", "corrected_md", "corrected_meta")}
    return jsonify({"success": True, "doc_id": doc_id, "artifacts": arts})
