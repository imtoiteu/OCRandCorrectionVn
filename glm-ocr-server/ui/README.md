# GLM-OCR — Local Test UI

A minimal [Gradio](https://www.gradio.app/) UI for testing GLM-OCR. It is a
**thin wrapper** around the verified `glmocr` CLI — it does **not** modify or
re-implement the OCR pipeline. It simply runs the exact command that was
validated by hand and shows the files the CLI produces.

```
ui/
├── app.py            # the Gradio app (subprocess-calls `glmocr parse ...`)
├── requirements.txt  # gradio only
├── README.md         # this file
└── _runs/            # per-run input/output/zip artifacts (auto-created)
```

## Prerequisites

The UI reuses the environments from the main project test:

1. **SDK env** at `../.venv-sdk` with `glmocr` installed (`pip install -e ".[selfhosted]"`).
2. **MLX server** running and serving the model:

   ```bash
   cd ..            # repo root
   .venv-mlx/bin/python -m mlx_vlm.server \
     --model mlx-community/GLM-OCR-bf16 --port 8080 --trust-remote-code
   ```

   The UI shows a 🔴/🟢 indicator and refuses to run if the server is down.

## Install (one time)

```bash
cd /Users/imtoiteu/Desktop/GLM-OCR/GLM-OCR
uv venv .venv-ui --python 3.12 --seed
uv pip install --python .venv-ui/bin/python -r ui/requirements.txt
```

## Launch

```bash
cd /Users/imtoiteu/Desktop/GLM-OCR/GLM-OCR
.venv-ui/bin/python ui/app.py
# open http://127.0.0.1:7860
```

## Usage

1. Upload a **PDF / PNG / JPG / JPEG**.
2. Click **Run OCR** — progress/logs stream live.
3. View results: rendered Markdown, raw Markdown, extracted images, JSON.
4. Download the Markdown, the JSON, or **all outputs as a ZIP**.

## Configuration (env vars, all optional)

| Variable | Default | Meaning |
|---|---|---|
| `GLMOCR_REPO` | parent of `ui/` | repo root |
| `GLMOCR_BIN` | `$REPO/.venv-sdk/bin/glmocr` | CLI to call |
| `GLMOCR_CONFIG` | `$REPO/glmocr/config.yaml` | base config |
| `GLMOCR_OCR_HOST` / `GLMOCR_OCR_PORT` | `localhost` / `8080` | OCR server |
| `GLMOCR_OCR_MODEL` | `mlx-community/GLM-OCR-bf16` | model name |
| `GLMOCR_LAYOUT_DEVICE` | `cpu` | layout device |
| `GLMOCR_MAX_WORKERS` | `4` | parallel region workers |
| `GLMOCR_UI_HOST` / `GLMOCR_UI_PORT` | `127.0.0.1` / `7860` | UI bind |

The command the UI runs is exactly:

```bash
glmocr parse <upload> --config glmocr/config.yaml \
  --set pipeline.maas.enabled false \
  --set pipeline.ocr_api.api_host localhost \
  --set pipeline.ocr_api.api_port 8080 \
  --set pipeline.ocr_api.model mlx-community/GLM-OCR-bf16 \
  --set pipeline.ocr_api.api_path /chat/completions \
  --set pipeline.layout.device cpu \
  --set pipeline.max_workers 4 \
  --output ui/_runs/<id>/output
```
