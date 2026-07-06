# Hướng dẫn cài đặt và chạy OCRandCorrectionVn trên macOS

Tài liệu này hướng dẫn clone, cài đặt và chạy dự án **OCRandCorrectionVn / SmartDocs-Agent** trên macOS, đặc biệt là macOS Apple Silicon khi dùng **GLM-OCR MLX**.

> Đã kiểm tra các lỗi thường gặp:
>
> - Sai path mặc định `/Users/imtoiteu/Desktop/GLM-OCR/GLM-OCR/...`
> - Thiếu `.venv-sdk`
> - Lỗi lệch phiên bản `transformers`
> - Lỗi không tải được `PaddlePaddle/PP-DocLayoutV3_safetensors`
> - Lỗi port `8080` hoặc `5001` đang bị chiếm

---

## 1. Yêu cầu hệ thống

Khuyến nghị:

- macOS Apple Silicon: M1 / M2 / M3 / M4
- Python 3.10
- Git
- Homebrew
- Internet trong lần chạy đầu tiên để tải model

Cài Python 3.10 và Git nếu chưa có:

```bash
brew install python@3.10 git
```

Kiểm tra:

```bash
python3.10 --version
git --version
```

---

## 2. Clone source code

Ví dụ clone về Desktop:

```bash
cd ~/Desktop
git clone https://github.com/imtoiteu/OCRandCorrectionVn.git
cd OCRandCorrectionVn
```

Cấu trúc chính:

```text
OCRandCorrectionVn/
├── glm-ocr-ui/        # Web UI SmartDocs-Agent
└── glm-ocr-server/    # GLM-OCR SDK + MLX server
```

---

## 3. Cài và chạy Web UI

Vào thư mục UI:

```bash
cd ~/Desktop/OCRandCorrectionVn/glm-ocr-ui
```

Tạo virtual environment:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

Cài dependencies:

```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Tạo file `.env`:

```bash
cp .env.example .env
```

Chạy Web UI:

```bash
python app.py
```

Mở trình duyệt:

```text
http://localhost:5001
```

Tài khoản mặc định:

```text
user / user123
admin / admin123
```

---

## 4. Cấu hình `.env` cho lần chạy đầu tiên

Mở file:

```bash
nano ~/Desktop/OCRandCorrectionVn/glm-ocr-ui/.env
```

Trong lần chạy đầu tiên, nên để:

```env
OFFLINE=0
```

Lý do: GLM-OCR và một số engine cần tải model từ Hugging Face / Paddle trong lần đầu. Nếu để `OFFLINE=1`, có thể gặp lỗi không tải được model, ví dụ:

```text
Can't load image processor for 'PaddlePaddle/PP-DocLayoutV3_safetensors'
```

Sau khi các model đã tải xong và cache ổn định, có thể cân nhắc đổi lại:

```env
OFFLINE=1
```

---

## 5. Cấu hình GLM-OCR path trong `.env`

Trong file `.env`, các dòng GLM mặc định thường đang bị comment bằng dấu `#`, ví dụ:

```env
# GLM_ROOT=/path/to/GLM-OCR/GLM-OCR
# GLM_SDK_PYTHON=/path/to/GLM-OCR/GLM-OCR/.venv/bin/python
# GLM_MLX_PYTHON=/path/to/GLM-OCR/GLM-OCR/.venv-mlx/bin/python
# GLM_CONFIG_YAML=
# GLM_OCR_API_URL=http://localhost:8080
# GLM_TIMEOUT=300
```

Các dòng có dấu `#` ở đầu sẽ không được app đọc.

Thêm các dòng sau vào cuối file `.env`:

```env
GLM_ROOT=/Users/imtoiteu/Desktop/OCRandCorrectionVn/glm-ocr-server
GLM_SDK_PYTHON=/Users/imtoiteu/Desktop/OCRandCorrectionVn/glm-ocr-server/.venv-sdk/bin/python
GLM_MLX_PYTHON=/Users/imtoiteu/Desktop/OCRandCorrectionVn/glm-ocr-server/.venv-mlx/bin/python
GLM_CONFIG_YAML=/Users/imtoiteu/Desktop/OCRandCorrectionVn/glm-ocr-server/mlx_config.yaml
GLM_OCR_API_URL=http://localhost:8080
GLM_TIMEOUT=300
```

Hoặc chạy lệnh tự động thêm vào cuối file:

```bash
cat >> ~/Desktop/OCRandCorrectionVn/glm-ocr-ui/.env <<'EOF'

# GLM-OCR local config
GLM_ROOT=/Users/imtoiteu/Desktop/OCRandCorrectionVn/glm-ocr-server
GLM_SDK_PYTHON=/Users/imtoiteu/Desktop/OCRandCorrectionVn/glm-ocr-server/.venv-sdk/bin/python
GLM_MLX_PYTHON=/Users/imtoiteu/Desktop/OCRandCorrectionVn/glm-ocr-server/.venv-mlx/bin/python
GLM_CONFIG_YAML=/Users/imtoiteu/Desktop/OCRandCorrectionVn/glm-ocr-server/mlx_config.yaml
GLM_OCR_API_URL=http://localhost:8080
GLM_TIMEOUT=300
EOF
```

Kiểm tra:

```bash
grep -n "GLM_" ~/Desktop/OCRandCorrectionVn/glm-ocr-ui/.env
```

Lưu ý: nếu bạn clone repo ở thư mục khác, hãy sửa lại `/Users/imtoiteu/Desktop/OCRandCorrectionVn` theo đúng đường dẫn thật.

---

## 6. Cài GLM-OCR SDK virtual environment

GLM-OCR cần `.venv-sdk` để UI gọi OCR qua CLI.

Chạy:

```bash
cd ~/Desktop/OCRandCorrectionVn/glm-ocr-server

python3.10 -m venv .venv-sdk
source .venv-sdk/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[selfhosted]"
```

Kiểm tra SDK:

```bash
~/Desktop/OCRandCorrectionVn/glm-ocr-server/.venv-sdk/bin/python -m glmocr.cli --help
```

Nếu hiện help của CLI là OK.

---

## 7. Cài GLM-OCR MLX server virtual environment

GLM-OCR MLX server cần `.venv-mlx`.

Chạy:

```bash
cd ~/Desktop/OCRandCorrectionVn/glm-ocr-server

python3.10 -m venv .venv-mlx
source .venv-mlx/bin/activate

python -m pip install --upgrade pip setuptools wheel
pip install -U mlx-vlm
```

---

## 8. Fix lỗi `transformers` nếu gặp lỗi import

Nếu chạy GLM server mà gặp lỗi dạng:

```text
AttributeError: 'str' object has no attribute '__module__'
```

hoặc lỗi liên quan:

```text
AutoTokenizer.register("NewlineTokenizer", ...)
```

thì nguyên nhân thường là phiên bản `transformers` không tương thích với `mlx-lm` / `mlx-vlm`.

Cài lại `transformers` bản ổn định cho cả hai môi trường:

```bash
cd ~/Desktop/OCRandCorrectionVn/glm-ocr-server

source .venv-sdk/bin/activate
python -m pip install --force-reinstall "transformers>=5.12,<5.13"
deactivate

source .venv-mlx/bin/activate
python -m pip install --force-reinstall "transformers>=5.12,<5.13"
deactivate
```

Kiểm tra import:

```bash
cd ~/Desktop/OCRandCorrectionVn/glm-ocr-server
source .venv-mlx/bin/activate

python - <<'PY'
import transformers
import mlx_lm
import mlx_vlm

print("transformers:", transformers.__version__)
print("mlx_lm import: OK")
print("mlx_vlm import: OK")
PY
```

---

## 9. Chạy đầy đủ hệ thống

Cần mở **2 Terminal**.

### Terminal 1: chạy GLM-OCR MLX server

```bash
cd ~/Desktop/OCRandCorrectionVn

GLM_ROOT="$PWD/glm-ocr-server" \
GLM_MLX_PYTHON="$PWD/glm-ocr-server/.venv-mlx/bin/python" \
bash glm-ocr-ui/tools/glm_serve.sh
```

Nếu chạy thành công, sẽ thấy server chạy ở:

```text
http://localhost:8080
```

Giữ Terminal này đang chạy.

---

### Terminal 2: chạy Web UI

```bash
cd ~/Desktop/OCRandCorrectionVn/glm-ocr-ui
source .venv/bin/activate
python app.py
```

Mở trình duyệt:

```text
http://localhost:5001
```

Trong UI, chọn engine **GLM OCR** nếu muốn dùng GLM.

---

## 10. Chạy nhanh bằng script `run_mac.sh`

Sau khi đã cài `.venv`, có thể chạy UI bằng script:

```bash
cd ~/Desktop/OCRandCorrectionVn/glm-ocr-ui
bash run_mac.sh
```

Lưu ý: GLM server vẫn cần chạy riêng ở Terminal khác nếu muốn dùng engine GLM OCR.

---

## 11. Xử lý lỗi thường gặp

### Lỗi 1: Port 8080 đang bị chiếm

Lỗi:

```text
error while attempting to bind on address ('0.0.0.0', 8080): address already in use
```

Xử lý:

```bash
lsof -ti :8080 | xargs kill -9
```

Sau đó chạy lại GLM server.

---

### Lỗi 2: Port 5001 đang bị chiếm

Xử lý:

```bash
lsof -ti :5001 | xargs kill -9
```

Sau đó chạy lại Web UI.

---

### Lỗi 3: Sai path GLM SDK

Lỗi:

```text
GLM OCR SDK not found at /Users/imtoiteu/Desktop/GLM-OCR/GLM-OCR/.venv-sdk/bin/python
```

Nguyên nhân: app đang dùng default path trong `config.py` vì `.env` chưa cấu hình GLM path thật.

Kiểm tra `.env`:

```bash
grep -n "GLM_" ~/Desktop/OCRandCorrectionVn/glm-ocr-ui/.env
```

Phải có các dòng không bị comment:

```env
GLM_ROOT=/Users/imtoiteu/Desktop/OCRandCorrectionVn/glm-ocr-server
GLM_SDK_PYTHON=/Users/imtoiteu/Desktop/OCRandCorrectionVn/glm-ocr-server/.venv-sdk/bin/python
GLM_MLX_PYTHON=/Users/imtoiteu/Desktop/OCRandCorrectionVn/glm-ocr-server/.venv-mlx/bin/python
GLM_CONFIG_YAML=/Users/imtoiteu/Desktop/OCRandCorrectionVn/glm-ocr-server/mlx_config.yaml
GLM_OCR_API_URL=http://localhost:8080
GLM_TIMEOUT=300
```

Sau khi sửa `.env`, phải restart lại Web UI.

---

### Lỗi 4: Không load được `PaddlePaddle/PP-DocLayoutV3_safetensors`

Lỗi:

```text
Can't load image processor for 'PaddlePaddle/PP-DocLayoutV3_safetensors'
```

Nguyên nhân thường gặp: `.env` đang để:

```env
OFFLINE=1
```

Trong lần chạy đầu tiên, đổi thành:

```env
OFFLINE=0
```

Chạy lệnh:

```bash
cd ~/Desktop/OCRandCorrectionVn/glm-ocr-ui
perl -pi -e 's/^OFFLINE=1/OFFLINE=0/' .env
```

Sau đó restart Web UI.

Có thể kiểm tra trực tiếp bằng `.venv-sdk`:

```bash
cd ~/Desktop/OCRandCorrectionVn/glm-ocr-server
source .venv-sdk/bin/activate

unset HF_HUB_OFFLINE
unset TRANSFORMERS_OFFLINE

python - <<'PY'
from transformers import AutoImageProcessor, AutoModelForObjectDetection

model_id = "PaddlePaddle/PP-DocLayoutV3_safetensors"
processor = AutoImageProcessor.from_pretrained(model_id)
model = AutoModelForObjectDetection.from_pretrained(model_id)

print("PP-DocLayoutV3 load: OK")
PY
```

---

### Lỗi 5: `.env` đã sửa nhưng app vẫn dùng cấu hình cũ

Nguyên nhân: Web UI đang chạy từ trước, chưa restart.

Cách xử lý:

1. Dừng Web UI bằng `Ctrl-C`
2. Chạy lại:

```bash
cd ~/Desktop/OCRandCorrectionVn/glm-ocr-ui
source .venv/bin/activate
python app.py
```

---

## 12. Checklist chạy lại từ đầu

Khi cần chạy lại toàn bộ hệ thống:

### Terminal 1

```bash
cd ~/Desktop/OCRandCorrectionVn

GLM_ROOT="$PWD/glm-ocr-server" \
GLM_MLX_PYTHON="$PWD/glm-ocr-server/.venv-mlx/bin/python" \
bash glm-ocr-ui/tools/glm_serve.sh
```

### Terminal 2

```bash
cd ~/Desktop/OCRandCorrectionVn/glm-ocr-ui
source .venv/bin/activate
python app.py
```

Mở:

```text
http://localhost:5001
```

---

## 13. Gợi ý trước khi push code

Không nên push các thư mục virtual environment và cache model:

```text
.venv/
.venv-sdk/
.venv-mlx/
models/
__pycache__/
*.pyc
```

Nên kiểm tra `.gitignore` có các dòng này chưa.

Kiểm tra trạng thái git:

```bash
cd ~/Desktop/OCRandCorrectionVn
git status
```

Nếu chỉ muốn thêm file hướng dẫn:

```bash
git add RUN_MACOS.md
git commit -m "docs: add macOS setup and run guide"
git push
```
