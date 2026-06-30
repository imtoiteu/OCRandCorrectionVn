# Terminal 1 — GLM Model Server:
GLM_ROOT=/Users/imtoiteu/Desktop/OCRSoftware/GLM-OCR/GLM-OCR \
GLM_MLX_PYTHON=/Users/imtoiteu/Desktop/OCRSoftware/GLM-OCR/GLM-OCR/.venv-mlx/bin/python \
/Users/imtoiteu/Desktop/ocr-local/GLMOCRUI/tools/glm_serve.sh

# Terminal 2 — SmartDocs Web UI:
/Users/imtoiteu/Desktop/OCRSoftware/.venv/bin/python \
/Users/imtoiteu/Desktop/ocr-local/GLMOCRUI/app.py

# Then open http://localhost:5001 — login: user / user123 or admin / admin123.