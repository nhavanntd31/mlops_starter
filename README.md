# Buổi 08 — Tích hợp End-to-End với Docker Compose

## Mục tiêu buổi học

- Tích hợp tất cả thành phần vào một stack duy nhất bằng Docker Compose
- Khởi động toàn bộ hệ thống bằng một lệnh
- Chạy full flow: train → register → predict → monitor
- Hiểu Ansible (optional) cho Infrastructure as Code

---

## Kiến thức lý thuyết

### Docker Compose

- Công cụ **orchestrate** ứng dụng đa container
- Định nghĩa tất cả services trong một file `docker-compose.yml`
- Quản lý networks, volumes, dependencies giữa các services
- Khởi động/dừng toàn bộ stack bằng một lệnh duy nhất

### Các service trong stack

| Service | Vai trò |
|---------|---------|
| **PostgreSQL** | Backend store cho MLflow (lưu metadata experiments, runs, metrics) |
| **MinIO** | S3-compatible object storage (lưu artifacts: model files, plots) |
| **MLflow Server** | Tracking server kết nối PostgreSQL + MinIO |
| **Model API** | FastAPI serving predictions, expose `/health`, `/predict`, `/metrics` |
| **Prometheus** | Thu thập và lưu trữ metrics từ Model API |
| **Loki** | Thu thập và lưu trữ logs tập trung |
| **Promtail** | Agent đọc log files và đẩy vào Loki |
| **Grafana** | Dashboard hiển thị metrics và logs |

### Service Dependencies và Health Checks

```
PostgreSQL ──┐
             ├── MLflow Server ── Model API ── Prometheus
MinIO ───────┘                                     │
                                    Loki ── Promtail
                                     │
                                   Grafana
```

- MLflow phụ thuộc PostgreSQL + MinIO (phải healthy trước)
- Model API phụ thuộc MLflow (để load model)
- Grafana kết nối Prometheus + Loki làm data sources

### Infrastructure as Code (IaC) — Ansible (optional)

- **Ansible**: công cụ tự động hóa cấu hình server
- Dùng YAML playbooks để mô tả trạng thái mong muốn
- Không cần agent trên máy đích (agentless, dùng SSH)
- Ứng dụng: cài Docker, deploy stack lên server remote

---

## Cấu trúc file mới thêm

```
session-08-docker-compose/
├── infra/
│   └── docker-compose.yml        # Định nghĩa toàn bộ stack
├── .env.example                   # Biến môi trường mẫu
└── scripts/
    ├── run_e2e_demo.ps1           # Script chạy demo end-to-end (PowerShell)
    └── register_best_model.py     # Đăng ký model tốt nhất vào MLflow Registry
```

---

## Hướng dẫn thực hành

### Bước 1: Checkout branch

```bash
git checkout session-08-docker-compose
```

### Bước 2: Chuẩn bị file `.env`

```powershell
Copy-Item .env.example .env
```

Mở `.env` và điều chỉnh nếu cần:
```env
POSTGRES_USER=mlflow
POSTGRES_PASSWORD=mlflow123
POSTGRES_DB=mlflow_db
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MLFLOW_TRACKING_URI=http://mlflow:5000
MLFLOW_S3_ENDPOINT_URL=http://minio:9000
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
```

### Bước 3: Đọc `docker-compose.yml`

Hiểu từng service và cách chúng kết nối:

| Service | Image | Port | Mô tả | Health check |
|---------|-------|------|--------|-------------|
| `postgres` | `postgres:15` | `5432` | Backend store MLflow | `pg_isready` |
| `minio` | `minio/minio` | `9000`, `9001` | Artifact storage (API + Console) | `curl /minio/health/live` |
| `mlflow` | `ghcr.io/mlflow/mlflow` | `5000` | Tracking server | `curl /health` |
| `model-api` | build từ `Dockerfile` | `8000` | FastAPI prediction API | `curl /health` |
| `prometheus` | `prom/prometheus` | `9090` | Metrics collection | `curl /-/healthy` |
| `loki` | `grafana/loki` | `3100` | Log aggregation | `curl /ready` |
| `promtail` | `grafana/promtail` | — | Đẩy logs vào Loki | — |
| `grafana` | `grafana/grafana` | `3000` | Dashboards | `curl /api/health` |

### Bước 4: Khởi động stack

```powershell
cd infra
docker compose up -d --build
```

Theo dõi logs:
```powershell
docker compose logs -f
```

### Bước 5: Kiểm tra services

```powershell
docker compose ps
```

Kiểm tra từng endpoint:
```powershell
curl http://localhost:8000/health
curl http://localhost:5000/health
curl http://localhost:9090/-/healthy
curl http://localhost:3100/ready
```

### Bước 6: Chạy data pipeline + train

```powershell
python src/data/make_dataset.py
python src/features/build_features.py
python src/models/train_model.py
```

### Bước 7: Register model

```powershell
python scripts/register_best_model.py
```

Script sẽ:
- Tìm run có R² cao nhất trong MLflow
- Đăng ký model vào MLflow Model Registry
- Chuyển model sang stage "Production"

### Bước 8: Test API

```powershell
python scripts/sample_predict.py http://localhost:8000
```

Hoặc dùng curl:
```powershell
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"features\": {\"area\": 120.5, \"bedrooms\": 3}}"
```

### Bước 9: Mở Grafana

1. Truy cập: **http://localhost:3000**
2. Đăng nhập: `admin` / `admin`
3. Thêm data source **Prometheus**: URL = `http://prometheus:9090`
4. Thêm data source **Loki**: URL = `http://loki:3100`
5. Tạo dashboard mới hoặc import từ template

### Bước 10: Chạy E2E demo tự động

```powershell
.\scripts\run_e2e_demo.ps1
```

Script thực hiện toàn bộ flow tự động:
1. Khởi động stack
2. Chờ services healthy
3. Chạy data pipeline
4. Train model
5. Register model
6. Gửi prediction requests
7. Kiểm tra metrics endpoint
8. In kết quả tổng hợp

---

## Bảng service và port

| Service | Image | Port(s) | Mô tả | URL kiểm tra |
|---------|-------|---------|--------|--------------|
| PostgreSQL | `postgres:15` | `5432` | MLflow backend store | — |
| MinIO | `minio/minio` | `9000` (API), `9001` (Console) | S3-compatible storage | `http://localhost:9001` |
| MLflow | `ghcr.io/mlflow/mlflow` | `5000` | Experiment tracking | `http://localhost:5000` |
| Model API | build local | `8000` | Prediction serving | `http://localhost:8000/docs` |
| Prometheus | `prom/prometheus` | `9090` | Metrics DB | `http://localhost:9090` |
| Loki | `grafana/loki` | `3100` | Log aggregation | — |
| Promtail | `grafana/promtail` | — | Log shipping agent | — |
| Grafana | `grafana/grafana` | `3000` | Visualization | `http://localhost:3000` |

---

## Chi tiết `docker-compose.yml`

### PostgreSQL

```yaml
postgres:
  image: postgres:15
  environment:
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: ${POSTGRES_DB}
  volumes:
    - postgres_data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
    interval: 10s
    timeout: 5s
    retries: 5
```

Lưu trữ metadata của MLflow: experiments, runs, params, metrics.

### MinIO

```yaml
minio:
  image: minio/minio
  command: server /data --console-address ":9001"
  environment:
    MINIO_ROOT_USER: ${MINIO_ROOT_USER}
    MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
  ports:
    - "9000:9000"
    - "9001:9001"
  volumes:
    - minio_data:/data
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
    interval: 10s
    timeout: 5s
    retries: 5
```

S3-compatible storage cho MLflow artifacts (model files, plots, ...).

### MLflow Server

```yaml
mlflow:
  image: ghcr.io/mlflow/mlflow
  command: >
    mlflow server
    --backend-store-uri postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
    --default-artifact-root s3://mlflow-artifacts/
    --host 0.0.0.0
    --port 5000
  environment:
    MLFLOW_S3_ENDPOINT_URL: http://minio:9000
    AWS_ACCESS_KEY_ID: ${MINIO_ROOT_USER}
    AWS_SECRET_ACCESS_KEY: ${MINIO_ROOT_PASSWORD}
  ports:
    - "5000:5000"
  depends_on:
    postgres:
      condition: service_healthy
    minio:
      condition: service_healthy
```

Kết nối PostgreSQL (backend) + MinIO (artifacts). Chỉ khởi động sau khi cả hai healthy.

### Model API

```yaml
model-api:
  build:
    context: ..
    dockerfile: Dockerfile
  environment:
    MODEL_URI: ${MODEL_URI:-}
    MLFLOW_TRACKING_URI: ${MLFLOW_TRACKING_URI}
  ports:
    - "8000:8000"
  volumes:
    - api_logs:/app/logs
  depends_on:
    mlflow:
      condition: service_healthy
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 10s
    timeout: 5s
    retries: 5
```

FastAPI app serving predictions. Mount volume `api_logs` để Promtail đọc logs.

### Prometheus

```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
    - ../monitoring/prometheus/alerts.yml:/etc/prometheus/alerts.yml
    - prometheus_data:/prometheus
  ports:
    - "9090:9090"
  depends_on:
    model-api:
      condition: service_healthy
```

Scrape metrics từ Model API mỗi 15 giây, lưu time-series data.

### Loki

```yaml
loki:
  image: grafana/loki:2.9.0
  ports:
    - "3100:3100"
  volumes:
    - loki_data:/loki
```

Nhận và lưu trữ logs từ Promtail.

### Promtail

```yaml
promtail:
  image: grafana/promtail:2.9.0
  volumes:
    - ./promtail.yml:/etc/promtail/config.yml
    - api_logs:/var/log/app:ro
  depends_on:
    - loki
```

Đọc log files từ volume `api_logs` và đẩy vào Loki.

### Grafana

```yaml
grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  environment:
    GF_SECURITY_ADMIN_USER: admin
    GF_SECURITY_ADMIN_PASSWORD: admin
  volumes:
    - grafana_data:/var/lib/grafana
  depends_on:
    - prometheus
    - loki
```

Dashboard hiển thị metrics (Prometheus) và logs (Loki).

### Networks và Volumes

```yaml
networks:
  default:
    name: mlops-network

volumes:
  postgres_data:
  minio_data:
  prometheus_data:
  loki_data:
  grafana_data:
  api_logs:
```

Tất cả services cùng network `mlops-network`, giao tiếp qua tên service. Volumes persist dữ liệu giữa các lần restart.

---

## Bài tập sau buổi học

1. **Thêm service Alertmanager** — thêm `alertmanager` vào `docker-compose.yml`, cấu hình nhận alerts từ Prometheus và gửi thông báo (email hoặc Slack webhook). Test bằng cách tạo tình huống HighErrorRate.

2. **Tạo Grafana dashboard tự động** — viết file JSON provisioning cho Grafana dashboard, mount vào container. Dashboard hiển thị: request rate, latency p95, error rate, prediction count. Khi Grafana khởi động sẽ tự động có dashboard.

3. **Viết script health check toàn bộ stack** — tạo `scripts/check_stack_health.py` kiểm tra tất cả services (curl health endpoint), in bảng trạng thái, exit code = 1 nếu có service nào fail.

4. **Thêm auto-scaling cho Model API** — nghiên cứu và cấu hình `deploy.replicas` trong Docker Compose hoặc dùng `docker compose up --scale model-api=3`. Test load balancing bằng cách gửi nhiều request đồng thời.

---

## Buổi tiếp theo

**Buổi 09 — Phân tích Bài toán AI Doanh nghiệp**: Chuyển từ kỹ thuật sang tư duy sản phẩm — phân tích bài toán kinh doanh, xác định bài toán ML phù hợp, thiết kế hệ thống AI cho doanh nghiệp, và trình bày kế hoạch triển khai.
