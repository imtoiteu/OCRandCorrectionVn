from __future__ import annotations

import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)

from config import cfg

from .base import OCREngine

# ---------------------------------------------------------------------------
# VietOCR vgg_transformer defaults (merged base.yml + vgg-transformer.yml)
# These are embedded here so the adapter works OFFLINE with no local config.yml.
# Values match https://vocr.vn/data/vietocr/config/{base.yml,vgg-transformer.yml}
# ---------------------------------------------------------------------------
_VGG_TRANSFORMER_DEFAULTS: dict = {
    # Vietnamese character vocabulary
    "vocab": (
        "aAàÀảẢãÃáÁạẠăĂằẰẳẲẵẴắẮặẶâÂầẦẩẨẫẪấẤậẬbBcCdDđĐeEèÈẻẺẽẼéÉẹẸêÊề"
        "ỀểỂễỄếẾệỆfFgGhHiIìÌỉỈĩĨíÍịỊjJkKlLmMnNoOòÒỏỎõÕóÓọỌôÔồỒổỔỗỖố"
        "ỐộỘơƠờỜởỞỡỠớỚợỢpPqQrRsStTuUùÙủỦũŨúÚụỤưƯừỪửỬữỮứỨựỰvVwWxXyYỳỲỷ"
        'ỶỹỸýÝỵỴzZ0123456789!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '
    ),
    "device": "cpu",
    "seq_modeling": "transformer",
    "transformer": {
        "d_model": 256,
        "nhead": 8,
        "num_encoder_layers": 6,
        "num_decoder_layers": 6,
        "dim_feedforward": 2048,
        "max_seq_length": 1024,
        "pos_dropout": 0.1,
        "trans_dropout": 0.1,
    },
    "optimizer": {"max_lr": 0.0003, "pct_start": 0.1},
    "trainer": {
        "batch_size": 32,
        "print_every": 200,
        "valid_every": 4000,
        "iters": 100000,
        "export": "./weights/transformerocr.pth",
        "checkpoint": "./checkpoint/transformerocr_checkpoint.pth",
        "log": "./train.log",
        "metrics": None,
    },
    "dataset": {
        "name": "data",
        "data_root": "./img/",
        "train_annotation": "annotation_train.txt",
        "valid_annotation": "annotation_val_small.txt",
        # These three are REQUIRED by predictor.process_input() — missing them
        # causes KeyError: 'image_height' which is silently caught as empty text.
        "image_height": 32,
        "image_min_width": 32,
        "image_max_width": 512,
    },
    "dataloader": {"num_workers": 3, "pin_memory": True},
    "aug": {"image_aug": True, "masked_language_model": True},
    # Official weights URL — used only if no local weights file is found
    "weights": "https://vocr.vn/data/vietocr/vgg_transformer.pth",
    "backbone": "vgg19_bn",
    "cnn": {
        "pretrained": False,   # disable pretrained CNN backbone download
        "ss": [[2, 2], [2, 2], [2, 1], [2, 1], [1, 1]],
        "ks": [[2, 2], [2, 2], [2, 1], [2, 1], [1, 1]],
        "hidden": 256,
    },
    "predictor": {"beamsearch": False},
    "quiet": True,
}


def _resolve_vietocr_config():
    """Return a vietocr Cfg object.

    Resolution order:
      1. VIETOCR_CONFIG_PATH env var → load that yml file
      2. Local file at MODEL_DIR/vietocr/config.yml
      3. Embedded defaults (vgg_transformer) — no internet, no file required
    """
    from vietocr.tool.config import Cfg

    # ── 1. Explicit env override ───────────────────────────────────────────
    env_path = os.environ.get("VIETOCR_CONFIG_PATH", "").strip()
    if env_path:
        p = Path(env_path)
        if p.exists():
            return Cfg.load_config_from_file(str(p))
        raise RuntimeError(
            f"VIETOCR_CONFIG_PATH set but file not found: {p}"
        )

    # ── 2. Local file next to model weights ───────────────────────────────
    local_yml = cfg.MODEL_DIR / "vietocr" / "config.yml"
    if local_yml.exists():
        return Cfg.load_config_from_file(str(local_yml))

    # ── 3. Programmatic defaults — no file required ───────────────────────
    return Cfg(dict(_VGG_TRANSFORMER_DEFAULTS))


def _resolve_vietocr_weights() -> str:
    """Return the local weights path (or the official HTTP URL as fallback).

    Resolution order:
      1. VIETOCR_WEIGHTS_PATH env var
      2. cfg.VIETOCR_WEIGHTS  (from VIETOCR_WEIGHTS in .env)
      3. MODEL_DIR/vietocr/vgg_transformer.pth
      4. Official vocr.vn URL (VietOCR downloads it to /tmp on first use)
    """
    # 1. Explicit env override
    env_wts = os.environ.get("VIETOCR_WEIGHTS_PATH", "").strip()
    if env_wts and Path(env_wts).exists():
        return env_wts

    # 2. VIETOCR_WEIGHTS from cfg / .env
    if cfg.VIETOCR_WEIGHTS and Path(cfg.VIETOCR_WEIGHTS).exists():
        return cfg.VIETOCR_WEIGHTS

    # 3. Default local path
    local_pth = cfg.MODEL_DIR / "vietocr" / "vgg_transformer.pth"
    if local_pth.exists():
        return str(local_pth)

    # 4. Official URL — VietOCR's download_weights() caches it in /tmp
    return "https://vocr.vn/data/vietocr/vgg_transformer.pth"


class VietOCREngine(OCREngine):
    """Image-first VietOCR integration.

    Phase 2 uses PaddleOCR detection boxes plus VietOCR recognition for image
    files. PDF requests continue using PaddleOCR via the caller.

    Config resolution (no local config.yml required):
      VIETOCR_CONFIG_PATH env → MODEL_DIR/vietocr/config.yml → embedded defaults

    Weights resolution:
      VIETOCR_WEIGHTS_PATH env → VIETOCR_WEIGHTS env → MODEL_DIR/vietocr/*.pth
      → official URL (downloaded to /tmp on first run)
    """

    engine_name = "vietocr"

    def __init__(self):
        self._detector = None
        self._predictor = None

    def _get_detector(self):
        if self._detector is None:
            from paddleocr import PaddleOCR

            # Pin detection to PP-OCRv5 so VietOCR's detection boxes stay
            # unchanged after the 3.7 upgrade (whose default is PP-OCRv6).
            self._detector = PaddleOCR(
                ocr_version="PP-OCRv5",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
            )
        return self._detector

    def _get_predictor(self):
        if self._predictor is None:
            from vietocr.tool.predictor import Predictor

            config = _resolve_vietocr_config()

            # Apply runtime overrides
            config["cnn"]["pretrained"] = False
            config["device"] = cfg.VIETOCR_DEVICE or "cpu"
            config["predictor"]["beamsearch"] = False
            config["weights"] = _resolve_vietocr_weights()

            self._predictor = Predictor(config)
        return self._predictor

    @staticmethod
    def _crop_polygon(image, polygon):
        xs = [int(pt[0]) for pt in polygon]
        ys = [int(pt[1]) for pt in polygon]
        left, top = max(0, min(xs)), max(0, min(ys))
        right, bottom = max(xs), max(ys)
        if right <= left or bottom <= top:
            return None
        return image.crop((left, top, right, bottom))

    def run(self, image_path: str) -> dict:
        from PIL import Image

        suffix = Path(image_path).suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise ValueError(
                "VietOCR currently supports image OCR only in this phase."
            )

        image = Image.open(image_path).convert("RGB")
        w, h = image.size
        t0 = time.time()

        detector = self._get_detector()
        predictor = self._get_predictor()
        detected = detector.predict(image_path)

        items = []
        for res in detected:
            boxes = res.get("det_polys", res.get("dt_polys", []))
            for poly in boxes:
                polygon = poly.tolist() if hasattr(poly, "tolist") else poly
                crop = self._crop_polygon(image, polygon)
                if crop is None:
                    continue
                _n_err = 0
                try:
                    text = predictor.predict(crop)
                    # VietOCR never returns None, but guard anyway
                    text = text or ""
                except Exception as exc:
                    _n_err += 1
                    if _n_err == 1:
                        logger.error(
                            "VietOCR predictor.predict() failed on crop %d: %s",
                            len(items), exc, exc_info=True,
                        )
                    # Reset cached predictor so next call reloads cleanly
                    self._predictor = None
                    raise RuntimeError(
                        f"VietOCR predictor failed: {exc}"
                    ) from exc
                items.append(
                    {
                        "text": text,
                        "confidence": None,
                        "box": polygon,
                    }
                )

        ms = round((time.time() - t0) * 1000)
        return {
            "success": True,
            "results": items,
            "img_width": w,
            "img_height": h,
            "elapsed_ms": ms,
            "ocr_engine": self.engine_name,
            "inference_status": "ok",
        }
