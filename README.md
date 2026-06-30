# OCROnlyFinal

Combined repository containing the full GLM-OCR stack:

| Folder | Description |
|--------|-------------|
| [`glm-ocr-server/`](./glm-ocr-server/) | GLM-OCR MLX model server (Apple Silicon) — serves `mlx-community/GLM-OCR-bf16` as an OpenAI-compatible HTTP API on `:8080` |
| [`glm-ocr-ui/`](./glm-ocr-ui/) | SmartDocs web UI — Flask app with OCR, document management, and GLM/Paddle/VietOCR engines on `:5001` |

## Quick Start

### Terminal 1 — GLM Model Server
```bash
GLM_ROOT=/path/to/glm-ocr-server \
GLM_MLX_PYTHON=/path/to/glm-ocr-server/.venv-mlx/bin/python \
glm-ocr-ui/tools/glm_serve.sh
```

### Terminal 2 — SmartDocs Web UI
```bash
# Copy and configure environment
cp glm-ocr-ui/.env.example glm-ocr-ui/.env

# Run with your Python venv
/path/to/.venv/bin/python glm-ocr-ui/app.py
```

Then open **http://localhost:5001** — login: `user / user123` or `admin / admin123`.

## Requirements
- Apple Silicon Mac (MLX for GLM server)
- Python 3.10+
- See `glm-ocr-ui/requirements.txt` for UI dependencies
