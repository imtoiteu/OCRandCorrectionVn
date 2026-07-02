import base64
import copy
from io import BytesIO
from pathlib import Path

from services.ocr_engines import router
from services import layout_service


DEFAULT_ENGINE = router.default_engine_name()


def pil_to_b64(pil_img, fmt="JPEG"):
    buf = BytesIO()
    pil_img.convert("RGB").save(buf, format=fmt, quality=92)
    return base64.b64encode(buf.getvalue()).decode()


def pdf_page_to_pil(pdf_path, page_num, scale=2.0):
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(pdf_path)
    bm = doc[page_num - 1].render(scale=scale)
    pil = bm.to_pil()
    doc.close()
    return pil


def pdf_page_count(pdf_path):
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(pdf_path)
    n = len(doc)
    doc.close()
    return n


def get_default_engine_name() -> str:
    return router.default_engine_name()


def get_available_engines() -> list[str]:
    return router.available_engines()


def normalize_engine_name(engine_name: str | None = None) -> str:
    return router.normalize_engine_name(engine_name)


def _normalize_block(item: dict) -> dict:
    """Ensure every block has a canonical ``text`` field and valid bbox.

    Different engines use different keys:
    - VietOCR / PaddleOCR:   {"text": "...", "box": [[x,y],...], ...}
    - GLM-OCR:                {"text": "...", "box": [...], ...}
    - PaddleOCR Modern:       may use "content" or "text"

    After this normalisation every block is guaranteed to have:
    - ``text``       str  (possibly empty)
    - ``box``        list[list[float]] | None
    - ``confidence`` float | None
    """
    out = dict(item)

    # --- text / content unification -------------------------------------------
    text = out.get("text")
    content = out.get("content")
    if not text and content:
        out["text"] = str(content)
    elif text is None:
        out["text"] = ""
    else:
        out["text"] = str(text)

    # Ensure content mirrors text for downstream consumers that prefer content
    if not out.get("content"):
        out["content"] = out["text"]

    # --- bbox normalisation ---------------------------------------------------
    box = out.get("box")
    # Some engines return an empty list instead of None
    if isinstance(box, list) and len(box) == 0:
        out["box"] = None

    return out


def _render_overlay_image(image_path: str, results: list[dict]) -> str | None:
    """Draw OCR bounding-box polygons onto the source image and return a
    base-64 PNG data-URI.  Used by non-GLM engines so the Images tab
    shows an annotated view consistent with the GLM-OCR layout visualisation.

    Returns ``None`` if the image cannot be opened or if no blocks have
    valid geometry (nothing to draw).
    """
    # Only import Pillow/ImageDraw here — keeps the top-level import fast
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None

    # Filter to blocks with valid polygon boxes
    boxed = [r for r in results if r.get("box") is not None]
    if not boxed:
        return None

    try:
        img = Image.open(image_path).convert("RGB")
    except Exception:
        return None

    draw = ImageDraw.Draw(img, "RGBA")

    # Confidence-based colour palette (matches the frontend canvas colours)
    def _col(conf):
        if conf is None:
            return (59, 130, 246, 60), (59, 130, 246)       # blue (no conf info)
        if conf >= 0.9:
            return (16, 185, 129, 50), (16, 185, 129)        # green
        if conf >= 0.7:
            return (245, 158, 11, 50), (245, 158, 11)         # amber
        return (239, 68, 68, 50), (239, 68, 68)               # red

    for block in boxed:
        poly = block["box"]
        # poly is [[x,y], [x,y], ...]
        try:
            pts = [tuple(map(float, pt)) for pt in poly]
        except Exception:
            continue
        if len(pts) < 3:
            continue

        conf = block.get("confidence")
        fill, stroke = _col(conf)

        # Draw filled polygon + border
        draw.polygon(pts, fill=fill)
        # Close the polygon by drawing each edge
        for j in range(len(pts)):
            p1 = pts[j]
            p2 = pts[(j + 1) % len(pts)]
            draw.line([p1, p2], fill=stroke, width=2)

    # Encode as PNG into a data-URI
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def run_ocr(image_path: str, engine_name: str | None = None) -> dict:
    """Public OCR entry point used by the app.

    Returns a normalised result dict where every item in ``results`` is
    guaranteed to have ``text``, ``content``, ``box``, and ``confidence`` keys.

    Items that have no geometry (box=None) are preserved in reading order
    *after* the geometrically-reordered blocks so they are never silently
    dropped by the layout reconstructor.

    For engines that don't produce their own image artifacts (VietOCR,
    PaddleOCR Legacy), this function generates an annotated overlay image
    and injects it as ``res["images"]`` so the Images tab activates in the
    frontend the same way it does for GLM-OCR.
    """
    from services import activity_registry
    with activity_registry.track("ocr"):  # DIAGNOSTIC: in-flight CPU-heavy op
        res = router.run_ocr(
            image_path, engine_name or router.default_engine_name()
        )

    if not (res and res.get("success") and "results" in res):
        return res

    # ── 1. Normalise all blocks ────────────────────────────────────────────
    raw_items: list[dict] = [_normalize_block(it) for it in res["results"]]

    # ── 2. Stash a copy of the original (pre-layout) order ────────────────
    res["raw_results"] = copy.deepcopy(raw_items)

    # ── 3. Split: items with valid geometry vs items with no box ──────────
    # The geometry service filters out box=None items, which silently drops
    # text from engines like VietOCR when a crop produced no usable polygon.
    geo_items   = [it for it in raw_items if it.get("box") is not None]
    nobox_items = [it for it in raw_items if it.get("box") is None]

    # ── 4. Reconstruct layout for boxed items only ─────────────────────────
    if not res.get("layout_native"):
        ordered = layout_service.reconstruct_layout(
            geo_items,
            res.get("img_width", 0),
            res.get("img_height", 0),
            image=image_path,
        ) if geo_items else []
    else:
        ordered = geo_items

    # ── 5. Merge back: geometry-ordered first, then geometry-less items ────
    merged = ordered + nobox_items

    # ── 6. Re-normalise after merge (merge_blocks may add text concatenation
    #       but skip content sync); also add sequential index if missing ────
    final: list[dict] = []
    for idx, it in enumerate(merged):
        block = _normalize_block(it)
        if "index" not in block:
            block["index"] = idx
        final.append(block)

    res["results"] = final

    # ── 7. Generate annotated overlay image for engines that don't produce
    #       their own visual artifacts (VietOCR, PaddleOCR Legacy).
    #       GLM-OCR already sets res["images"] from its layout_vis/ output, so
    #       we only inject when that key is absent or empty.
    if not res.get("images"):
        engine = res.get("ocr_engine", engine_name or "")
        overlay_uri = _render_overlay_image(image_path, final)
        if overlay_uri:
            res["images"] = [{
                "label": f"OCR overlay ({engine})",
                "kind":  "overlay",
                "page":  1,
                "src":   overlay_uri,
            }]

    return res
