"""
GLM-OCR — minimal local test UI (Gradio).

This UI is a THIN WRAPPER around the verified `glmocr` CLI. It does NOT touch
the OCR pipeline: it builds the exact command that was validated by hand and
runs it as a subprocess, then collects the files the CLI writes to --output.

Verified command it reproduces:

    .venv-sdk/bin/glmocr parse <input> --config glmocr/config.yaml \
        --set pipeline.maas.enabled false \
        --set pipeline.ocr_api.api_host localhost \
        --set pipeline.ocr_api.api_port 8080 \
        --set pipeline.ocr_api.model mlx-community/GLM-OCR-bf16 \
        --set pipeline.ocr_api.api_path /chat/completions \
        --set pipeline.layout.device cpu \
        --set pipeline.max_workers 4 \
        --output <run_dir>

Everything is configurable via environment variables (see CONFIG below) so no
paths are hard-coded into the core project.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import time
import uuid
from pathlib import Path

import gradio as gr

# --------------------------------------------------------------------------- #
# Config (override with env vars; sensible defaults for this repo layout)      #
# --------------------------------------------------------------------------- #
UI_DIR = Path(__file__).resolve().parent
REPO = Path(os.environ.get("GLMOCR_REPO", UI_DIR.parent)).resolve()

GLMOCR_BIN = os.environ.get("GLMOCR_BIN", str(REPO / ".venv-sdk" / "bin" / "glmocr"))
GLMOCR_CONFIG = os.environ.get("GLMOCR_CONFIG", str(REPO / "glmocr" / "config.yaml"))

OCR_HOST = os.environ.get("GLMOCR_OCR_HOST", "localhost")
OCR_PORT = int(os.environ.get("GLMOCR_OCR_PORT", "8080"))
OCR_MODEL = os.environ.get("GLMOCR_OCR_MODEL", "mlx-community/GLM-OCR-bf16")
OCR_API_PATH = os.environ.get("GLMOCR_OCR_API_PATH", "/chat/completions")
LAYOUT_DEVICE = os.environ.get("GLMOCR_LAYOUT_DEVICE", "cpu")
MAX_WORKERS = os.environ.get("GLMOCR_MAX_WORKERS", "4")

RUNS_DIR = Path(os.environ.get("GLMOCR_UI_RUNS", str(UI_DIR / "_runs"))).resolve()
RUNS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXT = {".pdf", ".png", ".jpg", ".jpeg"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif"}

# KaTeX delimiters for gr.Markdown. Gradio's default is None (no math), which is
# why raw LaTeX was shown. List $$ before $ so block math is matched first, and
# include the \(...\) / \[...\] forms for completeness.
LATEX_DELIMITERS = [
    {"left": "$$", "right": "$$", "display": True},
    {"left": "$", "right": "$", "display": False},
    {"left": "\\[", "right": "\\]", "display": True},
    {"left": "\\(", "right": "\\)", "display": False},
]


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #
def build_command(input_path: str, out_dir: str) -> list[str]:
    """Build the exact verified glmocr CLI invocation."""
    return [
        GLMOCR_BIN, "parse", input_path,
        "--config", GLMOCR_CONFIG,
        "--set", "pipeline.maas.enabled", "false",
        "--set", "pipeline.ocr_api.api_host", OCR_HOST,
        "--set", "pipeline.ocr_api.api_port", str(OCR_PORT),
        "--set", "pipeline.ocr_api.model", OCR_MODEL,
        "--set", "pipeline.ocr_api.api_path", OCR_API_PATH,
        "--set", "pipeline.layout.device", LAYOUT_DEVICE,
        "--set", "pipeline.max_workers", str(MAX_WORKERS),
        "--output", out_dir,
    ]


def server_reachable(timeout: float = 2.0) -> bool:
    """Quick TCP check that the MLX/OCR server port is open."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((OCR_HOST, OCR_PORT)) == 0
    except OSError:
        return False


def server_status_md() -> str:
    if server_reachable():
        return (
            f"🟢 **OCR server reachable** at `{OCR_HOST}:{OCR_PORT}` "
            f"(model `{OCR_MODEL}`)."
        )
    return (
        f"🔴 **OCR server NOT reachable** at `{OCR_HOST}:{OCR_PORT}`.\n\n"
        "Start it first (separate terminal):\n\n"
        f"```bash\ncd {REPO}\n.venv-mlx/bin/python -m mlx_vlm.server "
        f"--model {OCR_MODEL} --port {OCR_PORT} --trust-remote-code\n```"
    )


def _read_tail(path: Path, max_chars: int = 6000, max_lines: int = 30) -> str:
    """Read a tail of the log, normalising tqdm carriage returns."""
    try:
        data = path.read_text(errors="replace")
    except OSError:
        return ""
    # tqdm uses '\r' to repaint the same line; keep only the final repaint.
    data = data.replace("\r", "\n")
    lines = [ln for ln in data.splitlines() if ln.strip()]
    return "\n".join(lines[-max_lines:])[-max_chars:]


def find_outputs(out_root: Path):
    """Collect the files the CLI produced."""
    md_files, json_files, images = [], [], []
    for p in sorted(out_root.rglob("*")):
        if not p.is_file():
            continue
        suf = p.suffix.lower()
        if suf == ".md":
            md_files.append(p)
        elif suf == ".json":
            json_files.append(p)
        elif suf in IMAGE_EXT:
            images.append(p)
    # primary markdown = largest .md (the main content)
    primary_md = max(md_files, key=lambda p: p.stat().st_size, default=None)
    # primary json = prefer the structured result over *_model.json
    non_model = [p for p in json_files if not p.stem.endswith("_model")]
    primary_json = (non_model or json_files or [None])[0]
    return primary_md, primary_json, images, md_files, json_files


def make_zip(out_root: Path, dest_base: Path) -> str:
    """Zip the entire output directory; return the zip path."""
    archive = shutil.make_archive(str(dest_base), "zip", root_dir=str(out_root))
    return archive


def normalize_display_math(md: str) -> str:
    """Display-layer only: repair a known upstream artifact so KaTeX can pair
    `$$` fences.

    GLM-OCR's result_formatter occasionally emits an *extra* bare `$$` line
    immediately before a real display formula, e.g.::

        $$
        $$
        \\sum ... = dR.
        $$

    The doubled opening fence mis-pairs the delimiters, pushing the formula body
    outside math (shown raw). We collapse two *adjacent* `$$`-only lines into one,
    which restores correct pairing. A legitimately empty formula (`$$` / blank /
    `$$`, with a blank line between) is left untouched. This does NOT modify the
    OCR pipeline, the saved `.md`, or the downloads — only what is rendered.
    """
    if not md or "$$" not in md:
        return md
    out, prev_fence = [], False
    for line in md.split("\n"):
        is_fence = line.strip() == "$$"
        if is_fence and prev_fence:
            continue  # drop the duplicate adjacent opening fence
        out.append(line)
        prev_fence = is_fence
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Main callback (generator -> streamed progress)                              #
# --------------------------------------------------------------------------- #
N_OUTPUTS = 8  # status, md_render, md_raw, gallery, json, dl_md, dl_json, dl_zip


def _emit(status, md=gr.update(), raw=gr.update(), gallery=gr.update(),
          js=gr.update(), dlmd=gr.update(), dljson=gr.update(), dlzip=gr.update()):
    return status, md, raw, gallery, js, dlmd, dljson, dlzip


def run_ocr_stream(file_path):
    # ---- validate input -------------------------------------------------- #
    if not file_path:
        yield _emit("⚠️ Please upload a PDF / PNG / JPG / JPEG file first.")
        return

    src = Path(file_path)
    ext = src.suffix.lower()
    if ext not in ALLOWED_EXT:
        yield _emit(f"❌ Unsupported file type `{ext}`. "
                    f"Allowed: {', '.join(sorted(ALLOWED_EXT))}")
        return

    if not Path(GLMOCR_BIN).exists():
        yield _emit(f"❌ glmocr binary not found at `{GLMOCR_BIN}`. "
                    "Set GLMOCR_BIN env var.")
        return

    if not server_reachable():
        yield _emit("❌ OCR server not reachable.\n\n" + server_status_md())
        return

    # ---- set up run dir; copy upload with its real name ------------------ #
    run_id = uuid.uuid4().hex[:8]
    run_dir = RUNS_DIR / run_id
    in_dir = run_dir / "input"
    out_dir = run_dir / "output"
    in_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    input_path = in_dir / src.name
    shutil.copy2(src, input_path)

    cmd = build_command(str(input_path), str(out_dir))
    log_path = run_dir / "glmocr.log"

    header = (
        f"▶️ Running GLM-OCR on `{src.name}`\n"
        f"$ {' '.join(cmd)}\n"
        f"{'-' * 60}\n"
    )
    yield _emit(header + "starting…")

    # ---- launch subprocess; stream progress ------------------------------ #
    t0 = time.time()
    with open(log_path, "w") as logf:
        proc = subprocess.Popen(
            cmd, stdout=logf, stderr=subprocess.STDOUT,
            text=True, cwd=str(REPO),
        )
        while proc.poll() is None:
            tail = _read_tail(log_path)
            yield _emit(f"{header}{tail}\n\n⏳ running… {time.time() - t0:0.0f}s")
            time.sleep(0.5)

    rc = proc.returncode
    elapsed = time.time() - t0
    tail = _read_tail(log_path)

    if rc != 0:
        yield _emit(
            f"{header}{tail}\n\n❌ glmocr exited with code {rc} "
            f"after {elapsed:0.1f}s. See log above."
        )
        return

    # ---- collect results ------------------------------------------------- #
    primary_md, primary_json, images, md_files, json_files = find_outputs(out_dir)

    if primary_md is None and primary_json is None:
        yield _emit(f"{header}{tail}\n\n⚠️ Command succeeded but no output files "
                    f"were found in {out_dir}.")
        return

    md_text = primary_md.read_text(errors="replace") if primary_md else "*(no markdown)*"

    json_value = None
    if primary_json:
        try:
            json_value = json.loads(primary_json.read_text(errors="replace"))
        except json.JSONDecodeError:
            json_value = {"_raw": primary_json.read_text(errors="replace")[:5000]}

    gallery_items = [(str(p), p.relative_to(out_dir).as_posix()) for p in images]

    zip_path = make_zip(out_dir, run_dir / f"{src.stem}_glmocr_{run_id}")

    summary = (
        f"{header}{tail}\n\n"
        f"✅ Done in {elapsed:0.1f}s.\n"
        f"   markdown files: {len(md_files)} | json files: {len(json_files)} "
        f"| images: {len(images)}\n"
        f"   output dir: {out_dir}"
    )

    yield _emit(
        summary,
        md=normalize_display_math(md_text),  # rendered view (KaTeX)
        raw=md_text,                         # faithful raw OCR output
        gallery=gallery_items,
        js=json_value,
        dlmd=str(primary_md) if primary_md else None,
        dljson=str(primary_json) if primary_json else None,
        dlzip=zip_path,
    )


# --------------------------------------------------------------------------- #
# UI                                                                           #
# --------------------------------------------------------------------------- #
def build_ui() -> gr.Blocks:
    with gr.Blocks(title="GLM-OCR — Local Test UI", fill_height=True) as demo:
        gr.Markdown("# 🧾 GLM-OCR — Local Test UI")
        gr.Markdown(
            "Thin wrapper around the verified `glmocr` CLI. Upload a document, "
            "run OCR through the existing MLX pipeline, and view / download the "
            "results. _The OCR pipeline itself is unchanged._"
        )

        status_box = gr.Markdown(server_status_md())
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh server status", scale=0)

        with gr.Row(equal_height=False):
            with gr.Column(scale=1):
                file_in = gr.File(
                    label="Upload  (PDF / PNG / JPG / JPEG)",
                    file_count="single",
                    file_types=[".pdf", ".png", ".jpg", ".jpeg"],
                    type="filepath",
                )
                run_btn = gr.Button("▶️ Run OCR", variant="primary")
                progress = gr.Textbox(
                    label="Progress / logs", lines=14, max_lines=14,
                    autoscroll=True, show_copy_button=True,
                )
            with gr.Column(scale=2):
                with gr.Tabs():
                    with gr.Tab("Markdown (rendered)"):
                        md_render = gr.Markdown(latex_delimiters=LATEX_DELIMITERS)
                    with gr.Tab("Markdown (raw)"):
                        md_raw = gr.Textbox(
                            lines=22, show_copy_button=True, label="raw .md"
                        )
                    with gr.Tab("Extracted images"):
                        gallery = gr.Gallery(
                            label="imgs/ and layout_vis/", columns=3,
                            height="auto", object_fit="contain",
                        )
                    with gr.Tab("JSON"):
                        json_out = gr.JSON()

        gr.Markdown("### ⬇️ Downloads")
        with gr.Row():
            dl_md = gr.File(label="Markdown (.md)", interactive=False)
            dl_json = gr.File(label="JSON (.json)", interactive=False)
            dl_zip = gr.File(label="All outputs (.zip)", interactive=False)

        outputs = [progress, md_render, md_raw, gallery, json_out,
                   dl_md, dl_json, dl_zip]

        run_btn.click(run_ocr_stream, inputs=[file_in], outputs=outputs)
        refresh_btn.click(lambda: server_status_md(), outputs=[status_box])

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.queue()  # required for streamed/generator outputs
    demo.launch(
        server_name=os.environ.get("GLMOCR_UI_HOST", "127.0.0.1"),
        server_port=int(os.environ.get("GLMOCR_UI_PORT", "7860")),
        allowed_paths=[str(RUNS_DIR)],
        show_error=True,
    )
