# Buổi 07 — Monitoring, Metrics và Drift Detection

> **Dataset:** [House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) (`data/raw/kc_house_data.csv`), raw `data/raw/kc_house_data.csv` (~21510 rows; `sqft_living→area`, `yr_built→age`, `zipcode→location`, `floors`).
> Chuẩn bị lại: `# column mapping in src/ingestion/ingest.py`


## Mục tiêu buổi học

- Instrument FastAPI với Prometheus metrics
- Thu thập logs có cấu trúc (JSON logging)
- Cấu hình Prometheus scrape metrics
- Cấu hình Loki + Promtail thu thập logs
- Viết script phát hiện data drift
- Thiết lập alert rules

---

## Kiến thức lý thuyết

### 3 tầng Monitoring

| Tầng | Mô tả | Ví dụ metrics |
|------|--------|---------------|
| **Service metrics** | Giám sát hiệu năng hệ thống | Latency (p50, p95, p99), error rate, throughput (req/s) |
| **ML metrics** | Giám sát chất lượng mô hình | Accuracy, R², drift score, prediction distribution |
| **Business metrics** | Giám sát tác động kinh doanh | Conversion rate, revenue, số lượng dự đoán sai ảnh hưởng nghiệp vụ |

### Prometheus

- **Pull-based**: Prometheus chủ động kéo (scrape) metrics từ các endpoint `/metrics`
- **Time-series DB**: Lưu trữ dữ liệu dạng chuỗi thời gian
- **PromQL**: Ngôn ngữ truy vấn mạnh mẽ (ví dụ: `rate(request_count[5m])`)
- **Alerting**: Định nghĩa rules, khi điều kiện thỏa mãn → gửi cảnh báo qua Alertmanager

### Loki

- **Log aggregation**: Thu thập và lưu trữ logs tập trung
- **LogQL**: Ngôn ngữ truy vấn logs (tương tự PromQL)
- Kết hợp với **Grafana** để hiển thị logs trực quan
- Không index nội dung log (chỉ index labels) → tiết kiệm tài nguyên

### Promtail

- Agent chạy trên mỗi máy, đọc file log và đẩy vào Loki
- Cấu hình đường dẫn log, labels, và parsing rules
- Hỗ trợ pipeline stages: regex, json, labels, timestamp

### Grafana

- Nền tảng visualization dashboards
- Hỗ trợ nhiều data sources: Prometheus, Loki, PostgreSQL, ...
- Tạo dashboard với nhiều panel: graph, stat, table, logs

### Các loại Drift

| Loại Drift | Mô tả | Phương pháp phát hiện |
|------------|--------|----------------------|
| **Data Drift** | Phân phối input thay đổi theo thời gian | So sánh thống kê: z-score, KS test, PSI |
| **Model Drift** | Performance mô hình giảm dần | Theo dõi metrics: R², MAE, RMSE theo thời gian |
| **Concept Drift** | Mối quan hệ giữa input và output thay đổi | So sánh prediction distribution, cần ground truth |

### Delayed Evaluation

Trong nhiều bài toán, **ground truth đến muộn** so với thời điểm dự đoán:

- **Ví dụ**: Dự đoán giá nhà hôm nay, nhưng giá bán thực tế chỉ biết sau 3 tháng
- **Hệ quả**: Không thể tính accuracy ngay → phải dùng proxy metrics hoặc data drift để giám sát tạm thời
- **Chiến lược**: Khi có ground truth → tính metrics thực tế → quyết định retrain

---

## Cấu trúc file mới thêm

```
session-07-monitoring/
├── app/
│   └── metrics.py                        # PrometheusMiddleware, Counter, Histogram
├── infra/
│   ├── prometheus.yml                    # Cấu hình Prometheus scrape
│   └── promtail.yml                      # Cấu hình Promtail đọc logs
├── monitoring/
│   ├── prometheus/
│   │   └── alerts.yml                    # Alert rules
│   └── generate_drift_report.py          # Script phát hiện data drift
└── docs/
    └── retraining-trigger.md             # Tài liệu chiến lược retrain
```

---

## Hướng dẫn thực hành

### Bước 1: Checkout branch

```bash
git checkout session-07-monitoring
```

### Bước 2: Xem `app/metrics.py`

Hiểu cách tích hợp Prometheus với FastAPI:
- `PrometheusMiddleware`: middleware tự động đo latency và đếm request
- `Counter`: đếm số lần xảy ra sự kiện (ví dụ: tổng request, tổng prediction)
- `Histogram`: đo phân phối giá trị (ví dụ: latency theo percentile)

### Bước 3: Chạy API local và kiểm tra metrics

```bash
uvicorn app.main:app --reload --port 8000
```

Gửi vài request rồi truy cập endpoint metrics:
```bash
curl http://localhost:8000/metrics
```

Kết quả sẽ hiển thị dạng Prometheus exposition format:
```
# HELP request_count_total Tổng số request
# TYPE request_count_total counter
request_count_total{method="GET",endpoint="/health",status="200"} 3.0
...
```

### Bước 4: Xem cấu hình Prometheus

Mở file `infra/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "model-api"
    static_configs:
      - targets: ["model-api:8000"]

rule_files:
  - "/etc/prometheus/alerts.yml"
```

### Bước 5: Xem alert rules

Mở file `monitoring/prometheus/alerts.yml` — có 2 rules:

| Alert | Điều kiện | Thời gian chờ |
|-------|-----------|--------------|
| **HighErrorRate** | Tỷ lệ lỗi > 1% | Liên tục trong 2 phút |
| **HighLatency** | p95 latency > 200ms | Liên tục trong 2 phút |

### Bước 6: Chạy drift report

```bash
python monitoring/generate_drift_report.py
```

Xem kết quả:
```bash
type monitoring\reports\drift_report.json
```

Kết quả mẫu:
```json
{
  "generated_at": "2025-01-15T10:30:00",
  "features_analyzed": 5,
  "drifted_features": ["area", "location_encoded"],
  "details": {
    "area": {"z_score": 3.2, "drifted": true},
    "bedrooms": {"z_score": 0.5, "drifted": false}
  }
}
```

### Bước 7: Đọc tài liệu chiến lược retrain

Mở `docs/retraining-trigger.md` — mô tả:
- Khi nào cần retrain (drift phát hiện, performance giảm, dữ liệu mới đủ lớn)
- Quy trình retrain tự động (CT pipeline)
- Rollback strategy nếu model mới kém hơn

---

## Chi tiết code

### `app/metrics.py`

```python
from prometheus_client import Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time

REQUEST_COUNT = Counter(
    "request_count",
    "Tổng số HTTP request",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "request_latency_seconds",
    "Latency của HTTP request (giây)",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.2, 0.5, 1.0],
)

PREDICTION_COUNT = Counter(
    "prediction_count",
    "Tổng số lần gọi prediction",
)

PREDICTION_LATENCY = Histogram(
    "prediction_latency_seconds",
    "Latency của prediction (giây)",
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25],
)

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        latency = time.perf_counter() - start

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path,
        ).observe(latency)

        return response

async def metrics_endpoint(request: Request) -> Response:
    return Response(
        content=generate_latest(),
        media_type="text/plain",
    )
```

### `app/main.py` — cập nhật

Thêm middleware và JSON logging:

```python
import logging
import json

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(message)s",
)

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics_endpoint)

@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    prediction, latency_ms = model_holder.predict(request.features)

    logging.info(json.dumps({
        "event": "prediction",
        "features": request.features,
        "prediction": prediction,
        "latency_ms": latency_ms,
        "model_version": model_holder.model_version,
    }))

    PREDICTION_COUNT.inc()
    PREDICTION_LATENCY.observe(latency_ms / 1000)

    return PredictResponse(
        prediction=prediction,
        latency_ms=latency_ms,
        model_version=model_holder.model_version or "unknown",
    )
```

### `monitoring/generate_drift_report.py`

```python
import json
import numpy as np
from datetime import datetime
from pathlib import Path

def compute_stats(values: list[float]) -> dict:
    return {
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
    }

def detect_drift(
    baseline_mean: float,
    baseline_std: float,
    current_mean: float,
    threshold: float = 2.0,
) -> tuple[float, bool]:
    if baseline_std == 0:
        return 0.0, False
    z_score = abs(current_mean - baseline_mean) / baseline_std
    return z_score, z_score > threshold

def generate_report(
    baseline_data: dict[str, list[float]],
    current_data: dict[str, list[float]],
    output_path: str = "monitoring/reports/drift_report.json",
):
    details = {}
    drifted_features = []

    for feature in baseline_data:
        baseline_stats = compute_stats(baseline_data[feature])
        current_stats = compute_stats(current_data[feature])

        z_score, drifted = detect_drift(
            baseline_stats["mean"],
            baseline_stats["std"],
            current_stats["mean"],
        )

        details[feature] = {
            "baseline": baseline_stats,
            "current": current_stats,
            "z_score": round(z_score, 4),
            "drifted": drifted,
        }

        if drifted:
            drifted_features.append(feature)

    report = {
        "generated_at": datetime.now().isoformat(),
        "features_analyzed": len(baseline_data),
        "drifted_features": drifted_features,
        "details": details,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"📊 Báo cáo drift đã được tạo: {output_path}")
    print(f"   Tổng features phân tích: {len(baseline_data)}")
    print(f"   Features bị drift: {drifted_features or 'Không có'}")

    return report
```

### `monitoring/prometheus/alerts.yml`

```yaml
groups:
  - name: model-api-alerts
    rules:
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(request_count{status=~"5.."}[2m]))
            /
            sum(rate(request_count[2m]))
          ) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Tỷ lệ lỗi API cao"
          description: "Tỷ lệ lỗi 5xx vượt quá 1% trong 2 phút qua"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95, rate(request_latency_seconds_bucket[2m])) > 0.2
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Latency API cao"
          description: "P95 latency vượt quá 200ms trong 2 phút qua"
```

---

## Bài tập sau buổi học

1. **Thêm metric cho model confidence** — tạo thêm Histogram `prediction_confidence` để theo dõi phân phối độ tin cậy của mô hình. Cập nhật endpoint `/predict` để trả về và ghi nhận confidence score.

2. **Cấu hình Grafana dashboard** — tạo file JSON cho Grafana dashboard hiển thị: request rate, latency p95, error rate, prediction distribution. Import vào Grafana và chụp ảnh kết quả.

3. **Mở rộng drift detection** — thêm phương pháp KS test (Kolmogorov-Smirnov) bên cạnh z-score trong `generate_drift_report.py`. So sánh kết quả hai phương pháp.

4. **Viết alert cho model drift** — thêm rule trong `alerts.yml` cảnh báo khi `prediction_latency` tăng đột biến (> 500ms) hoặc khi tỷ lệ prediction có giá trị bất thường (ngoài khoảng mong đợi).

---

## Buổi tiếp theo

**Buổi 08 — Tích hợp End-to-End với Docker Compose**: Tích hợp tất cả thành phần (PostgreSQL, MinIO, MLflow, FastAPI, Prometheus, Loki, Promtail, Grafana) vào một stack duy nhất bằng Docker Compose. Khởi động toàn bộ hệ thống bằng một lệnh và chạy full flow: train → register → predict → monitor.
