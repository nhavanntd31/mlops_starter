# Buổi 05 — Docker và FastAPI Model Serving

> **Dataset:** [House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) (`data/raw/kc_house_data.csv`), raw `data/raw/kc_house_data.csv` (~21510 rows; `sqft_living→area`, `yr_built→age`, `zipcode→location`, `floors`).
> Chuẩn bị lại: `# column mapping in src/ingestion/ingest.py`


## Mục tiêu buổi học

- Xây dựng API serving với FastAPI: `/health`, `/predict`, `/model-info`
- Hiểu 3 loại inference: batch, online, streaming
- Đóng gói ứng dụng với Docker
- Viết integration test cho API

---

## Kiến thức lý thuyết

### 3 loại Inference

| Loại | Mô tả | Ví dụ | Đặc điểm |
|------|--------|-------|-----------|
| **Batch** | Xử lý hàng loạt dữ liệu theo lịch | Cron job chạy dự đoán mỗi đêm | Throughput cao, latency không quan trọng |
| **Online** | Real-time REST API, trả kết quả ngay | Người dùng gửi request, nhận prediction | Low latency (< 200ms), đồng bộ |
| **Streaming** | Event-driven, xử lý liên tục | Kafka consumer nhận event và dự đoán | Bất đồng bộ, throughput cao, near real-time |

### FastAPI

- Framework Python hiện đại, hỗ trợ **async/await**
- Tự động sinh tài liệu API (Swagger UI tại `/docs`, ReDoc tại `/redoc`)
- Validation dữ liệu đầu vào với **Pydantic**
- Hiệu năng cao nhờ Starlette và Uvicorn (ASGI)
- Type hints giúp code rõ ràng, dễ bảo trì

### Docker

| Khái niệm | Giải thích |
|------------|------------|
| **Image** | Bản thiết kế bất biến chứa code, dependencies, runtime |
| **Container** | Thực thể đang chạy từ image, cô lập với hệ thống host |
| **Dockerfile** | File kịch bản định nghĩa cách build image |
| **Layer caching** | Mỗi lệnh trong Dockerfile tạo một layer; Docker cache layer không đổi để build nhanh hơn |

### API Contract

**Input** — `POST /predict`:
```json
{
  "features": {
    "area": 120.5,
    "bedrooms": 3,
    "location": "quan_7"
  }
}
```

**Output**:
```json
{
  "prediction": 3250000000,
  "latency_ms": 12.5,
  "model_version": "1.0.0"
}
```

---

## Cấu trúc file mới thêm

```
session-05-docker-fastapi/
├── app/
│   ├── main.py              # FastAPI app, endpoints, lifespan
│   ├── schemas.py           # Pydantic models cho request/response
│   ├── model_loader.py      # ModelHolder class, load từ MLflow
│   └── predictors/
│       └── tabular.py       # Logic dự đoán cho tabular data
├── Dockerfile               # Đóng gói ứng dụng
├── .dockerignore             # Loại trừ file không cần thiết
├── tests/
│   └── test_api.py          # Integration tests cho API
└── scripts/
    └── sample_predict.py    # Script gửi request mẫu
```

---

## Hướng dẫn thực hành

### Bước 1: Checkout branch

```bash
git checkout session-05-docker-fastapi
```

### Bước 2: Cài thêm dependencies

```bash
pip install fastapi uvicorn httpx python-multipart
```

### Bước 3: Chạy API local

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> **Lưu ý:** Model sẽ không load được nếu chưa có MLflow server đang chạy, nhưng endpoint `/health` vẫn hoạt động bình thường.

### Bước 4: Test thủ công bằng trình duyệt hoặc curl

Mở trình duyệt và truy cập **Swagger UI**:

```
http://localhost:8000/docs
```

Hoặc dùng curl:

```bash
curl http://localhost:8000/health
```

### Bước 5: Test endpoint `/health`

```bash
curl -X GET http://localhost:8000/health
```

Kết quả mong đợi:
```json
{
  "status": "healthy",
  "model_loaded": false
}
```

### Bước 6: Build Docker image

```bash
docker build -t house-price-api .
```

### Bước 7: Chạy Docker container

```bash
docker run -p 8000:8000 house-price-api
```

Kiểm tra container đang chạy:
```bash
docker ps
```

### Bước 8: Chạy integration tests

```bash
pytest tests/test_api.py -v
```

### Bước 9: Dùng script gửi request mẫu

```bash
python scripts/sample_predict.py
```

Script sẽ gửi request đến `/predict` và in kết quả ra terminal.

---

## Chi tiết code

### `app/schemas.py`

```python
from pydantic import BaseModel
from typing import Any, Optional

class PredictRequest(BaseModel):
    features: dict[str, Any]

class PredictResponse(BaseModel):
    prediction: float
    latency_ms: float
    model_version: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

class ModelInfoResponse(BaseModel):
    model_name: Optional[str]
    model_version: Optional[str]
    model_uri: Optional[str]
    features_expected: Optional[list[str]]
```

### `app/model_loader.py`

```python
import mlflow
import time

class ModelHolder:
    def __init__(self):
        self.model = None
        self.model_name = None
        self.model_version = None
        self.model_uri = None

    def load(self, model_uri: str):
        self.model_uri = model_uri
        self.model = mlflow.pyfunc.load_model(model_uri)
        self.model_name = model_uri.split("/")[-1]

    def predict(self, features: dict) -> tuple[float, float]:
        import pandas as pd
        start = time.perf_counter()
        df = pd.DataFrame([features])
        prediction = self.model.predict(df)[0]
        latency_ms = (time.perf_counter() - start) * 1000
        return float(prediction), latency_ms
```

### `app/main.py`

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.schemas import PredictRequest, PredictResponse, HealthResponse, ModelInfoResponse
from app.model_loader import ModelHolder
import os

model_holder = ModelHolder()

@asynccontextmanager
async def lifespan(app: FastAPI):
    model_uri = os.getenv("MODEL_URI", "")
    if model_uri:
        model_holder.load(model_uri)
    yield

app = FastAPI(title="House Price Prediction API", lifespan=lifespan)

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="healthy", model_loaded=model_holder.model is not None)

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    prediction, latency_ms = model_holder.predict(request.features)
    return PredictResponse(
        prediction=prediction,
        latency_ms=latency_ms,
        model_version=model_holder.model_version or "unknown",
    )

@app.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    return ModelInfoResponse(
        model_name=model_holder.model_name,
        model_version=model_holder.model_version,
        model_uri=model_holder.model_uri,
        features_expected=None,
    )
```

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- Dùng `python:3.11-slim` để giảm kích thước image
- Copy `requirements.txt` trước để tận dụng **layer caching** (chỉ cài lại khi file thay đổi)
- `EXPOSE 8000` khai báo cổng cho container
- `CMD` chạy Uvicorn khi container khởi động

---

## Bài tập sau buổi học

1. **Thêm endpoint `/predict/batch`** — nhận danh sách nhiều mẫu dữ liệu, trả về danh sách prediction. Sử dụng `list[PredictRequest]` làm input.

2. **Thêm input validation** — trong `schemas.py`, thêm validator kiểm tra `features` không rỗng và các giá trị số phải dương. Dùng `@field_validator` của Pydantic v2.

3. **Viết thêm test cases** — trong `tests/test_api.py`, thêm test cho trường hợp: request thiếu field, request có giá trị âm, request body rỗng. Kiểm tra API trả về đúng mã lỗi (422).

4. **Tối ưu Dockerfile** — thêm `.dockerignore` để loại trừ `__pycache__`, `.git`, `*.pyc`, `data/`. So sánh kích thước image trước và sau khi tối ưu.

---

## Buổi tiếp theo

**Buổi 06 — CI/CD và Quality Gate**: Xây dựng pipeline CI/CD tự động với GitLab CI, thiết lập quality gates (lint, test, validate config, build Docker), và viết script kiểm tra cấu hình dự án.
