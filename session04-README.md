# Buổi 04 — Model Registry và Governance

> **Dataset:** [House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) (`data/raw/kc_house_data.csv`), đã map sang `data/raw/kc_house_data.csv` (~21510 rows; `sqft_living→area`, `yr_built→age`, `zipcode→location`, `floors`).
> Chuẩn bị lại: `# column mapping in src/ingestion/ingest.py`


## Mục tiêu buổi học

- Đăng ký model vào MLflow Model Registry
- Hiểu vòng đời model: Candidate → Staging → Production
- Viết automated validation pipeline (kiểm tra metrics so với ngưỡng)
- Thực hiện promote và rollback phiên bản model
- Viết Model Card cho model

---

## Kiến thức lý thuyết

### Model Registry là gì?

Model Registry là trung tâm quản lý tất cả phiên bản model. Nó giúp:

- Lưu trữ và đánh số phiên bản cho mỗi model
- Theo dõi model nào đang chạy trên production
- Quản lý quy trình duyệt trước khi triển khai
- Hỗ trợ rollback nhanh khi model mới gặp vấn đề

### Vòng đời Model (Model Lifecycle)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MODEL LIFECYCLE                                  │
│                                                                      │
│  Train                                                               │
│    │                                                                 │
│    ▼                                                                 │
│  Register (đăng ký vào Model Registry)                               │
│    │                                                                 │
│    ▼                                                                 │
│  Automated Validation                                                │
│    │                                                                 │
│    ├── FAIL ──► Từ chối, không triển khai                            │
│    │                                                                 │
│    └── PASS                                                          │
│         │                                                            │
│         ▼                                                            │
│       Staging (kiểm thử trên môi trường giả lập)                    │
│         │                                                            │
│         ▼                                                            │
│       Human Approve (người duyệt xác nhận)                          │
│         │                                                            │
│         ▼                                                            │
│       Production (phục vụ dự đoán thực tế)                           │
│         │                                                            │
│         ▼                                                            │
│       Monitoring (giám sát liên tục)                                 │
│         │                                                            │
│         ├── Bình thường ──► Tiếp tục phục vụ                         │
│         │                                                            │
│         └── Phát hiện vấn đề ──► Rollback (quay về phiên bản cũ)    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Model Governance

Model Governance đảm bảo mỗi model đưa lên production đều có thể truy vết và kiểm soát:

| Khía cạnh         | Mô tả                                                                | Ví dụ                                      |
| ------------------ | --------------------------------------------------------------------- | ------------------------------------------- |
| Traceability       | Truy vết nguồn gốc model: run nào, dữ liệu nào, code version nào    | `run_id`, `dataset_version`, `git_commit`   |
| Audit Trail        | Nhật ký mọi thay đổi trạng thái của model                            | Ai duyệt, khi nào promote, lý do rollback  |
| Approval Workflow  | Quy trình phê duyệt trước khi model lên production                   | Validation tự động + duyệt thủ công         |

### Model Card

Model Card là tài liệu mô tả model, bao gồm:

- Mục đích sử dụng và giới hạn của model
- Dữ liệu huấn luyện (nguồn, kích thước, thời gian)
- Hiệu năng trên các tập dữ liệu khác nhau
- Các rủi ro đã biết và hướng giảm thiểu
- Hướng dẫn sử dụng và liên hệ người phụ trách

---

## Cấu trúc file mới thêm

```
mlops-starter-repo/
├── scripts/
│   ├── validate_model.py        # Kiểm tra metrics so với ngưỡng
│   └── promote_model.py         # Promote hoặc rollback model version
├── configs/
│   └── thresholds.yaml          # Ngưỡng chấp nhận cho metrics
└── docs/
    └── model-card.md            # Tài liệu mô tả model
```

---

## Hướng dẫn thực hành

### Bước 1: Checkout, chạy data pipeline và training

```powershell
git checkout -b session04-registry

python src/ingestion/ingest.py
python src/validation/validate.py
python src/preprocessing/preprocess.py
python src/split/split.py
python src/training/train.py
```

Hoặc sử dụng lại kết quả từ buổi 03 nếu đã có `reports/evaluation.json` và `models/model.pkl`.

### Bước 2: Xem ngưỡng chấp nhận

Nội dung file `configs/thresholds.yaml`:

```yaml
model_quality:
  rmse_max: 30000
  mae_max: 20000
  r2_min: 0.60
  mape_max: 25.0

serving:
  latency_p95_ms: 200
  error_rate_max: 0.01
```

| Metric      | Ngưỡng              | Ý nghĩa                                        |
| ----------- | -------------------- | ----------------------------------------------- |
| rmse_max    | 30.000               | RMSE phải nhỏ hơn 30.000                       |
| mae_max     | 20.000               | MAE phải nhỏ hơn 20.000                        |
| r2_min      | 0.60                 | R² phải lớn hơn hoặc bằng 0.60                 |
| mape_max    | 25.0                 | MAPE phải nhỏ hơn 25%                          |
| latency_p95 | 200ms                | Thời gian phản hồi p95 của API phải dưới 200ms |
| error_rate  | 1%                   | Tỷ lệ lỗi API phải dưới 1%                     |

### Bước 3: Chạy validate_model.py

```powershell
python scripts/validate_model.py
```

Kết quả mong đợi:

```
╔══════════════════════════════════════════════════════╗
║             KẾT QUẢ VALIDATION MODEL                ║
╠══════════════════════════════════════════════════════╣
║  RMSE:  25431.12 < 30000.00  ──► PASS ✓            ║
║  MAE:   18234.56 < 20000.00  ──► PASS ✓            ║
║  R²:    0.72     > 0.60      ──► PASS ✓            ║
║  MAPE:  15.3%    < 25.0%     ──► PASS ✓            ║
╠══════════════════════════════════════════════════════╣
║  KẾT QUẢ TỔNG: PASS — Model đủ điều kiện triển khai║
╚══════════════════════════════════════════════════════╝
```

### Bước 4: Đăng ký model vào MLflow Model Registry

**Cách 1 — Dùng MLflow CLI:**

```powershell
mlflow models register -m "runs:/<run_id>/model" -n "house-price-model"
```

**Cách 2 — Dùng Python:**

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")

result = mlflow.register_model(
    model_uri="runs:/<run_id>/model",
    name="house-price-model"
)
print(f"Đã đăng ký phiên bản: {result.version}")
```

### Bước 5: Promote model

```powershell
python scripts/promote_model.py champion
```

Kết quả mong đợi:

```
Model 'house-price-model' phiên bản 1 đã được gán alias 'champion'.
Phiên bản này sẽ được sử dụng khi serving.
```

Các alias phổ biến:

| Alias      | Ý nghĩa                                          |
| ---------- | ------------------------------------------------- |
| candidate  | Model mới được đăng ký, chờ validation            |
| staging    | Model đã qua validation, đang kiểm thử            |
| champion   | Model đang phục vụ trên production                 |

### Bước 6: Đọc và chỉnh sửa Model Card

```powershell
type docs\model-card.md
```

Mẫu Model Card:

```markdown
# Model Card — House Price Prediction

## Tổng quan
- **Tên model:** house-price-model
- **Phiên bản:** 1
- **Thuật toán:** GradientBoostingRegressor
- **Ngày huấn luyện:** 2026-09-03
- **Người phụ trách:** MLOps Team

## Mục đích sử dụng
Dự đoán giá nhà dựa trên các đặc trưng: diện tích, số phòng, tuổi nhà, vị trí.

## Dữ liệu huấn luyện
- **Nguồn:** Kaggle King County (`kc_house_data.csv` → `kc_house_data.csv`)
- **Số lượng:** ~21510 bản ghi (King County)
- **Thời gian thu thập:** 2026
- **Chia tập:** train 70%, validation 10%, test 20%

## Hiệu năng
| Tập dữ liệu | RMSE     | MAE      | R²   | MAPE  |
| ------------ | -------- | -------- | ---- | ----- |
| Validation   | 25431.12 | 18234.56 | 0.72 | 15.3% |
| Test         | 26102.45 | 19012.33 | 0.70 | 16.1% |

## Giới hạn và rủi ro
- Chỉ áp dụng cho thị trường bất động sản trong phạm vi dữ liệu huấn luyện
- Không xử lý tốt khi giá nhà biến động đột biến (data drift)
- Dữ liệu huấn luyện có thể không đại diện cho mọi khu vực

## Hướng dẫn sử dụng
Gọi API prediction endpoint với JSON chứa các trường: area, bedrooms,
bathrooms, age, floors, location.
```

Chỉnh sửa Model Card phù hợp với kết quả thực tế của bạn.

### Bước 7: Thử rollback scenario

Giả sử model mới (phiên bản 2) có kết quả kém hơn, bạn muốn quay về phiên bản 1:

```powershell
python scripts/promote_model.py champion --version 1
```

Kết quả:

```
Rollback thành công. Model 'house-price-model' phiên bản 1 đã được gán lại alias 'champion'.
```

---

## Chi tiết code

### `scripts/validate_model.py`

Chức năng:

1. Đọc file `reports/evaluation.json` để lấy metrics thực tế
2. Đọc file `configs/thresholds.yaml` để lấy ngưỡng chấp nhận
3. So sánh từng metric với ngưỡng tương ứng:
   - `rmse` ≤ `rmse_max` → PASS
   - `mae` ≤ `mae_max` → PASS
   - `r2` ≥ `r2_min` → PASS
   - `mape` ≤ `mape_max` → PASS
4. In kết quả PASS/FAIL cho từng metric
5. Kết luận tổng: PASS nếu tất cả metrics đạt, FAIL nếu bất kỳ metric nào không đạt
6. Trả về exit code 0 (thành công) hoặc 1 (thất bại) — hữu ích cho CI/CD

### `scripts/promote_model.py`

Chức năng:

1. Nhận đối số dòng lệnh: alias (candidate/staging/champion) và tùy chọn version
2. Kết nối đến MLflow Tracking Server
3. Lấy phiên bản model mới nhất (hoặc phiên bản chỉ định)
4. Gán alias cho phiên bản đó bằng `client.set_registered_model_alias()`
5. In xác nhận thành công

Sử dụng:

```powershell
python scripts/promote_model.py candidate
python scripts/promote_model.py staging
python scripts/promote_model.py champion
python scripts/promote_model.py champion --version 1
```

### `configs/thresholds.yaml`

```yaml
model_quality:
  rmse_max: 30000
  mae_max: 20000
  r2_min: 0.60
  mape_max: 25.0

serving:
  latency_p95_ms: 200
  error_rate_max: 0.01
```

Hai nhóm ngưỡng:

- **model_quality** — Dùng trong `validate_model.py` để kiểm tra chất lượng model trước khi triển khai
- **serving** — Dùng trong monitoring để kiểm tra hiệu năng API sau khi triển khai

---

## Bài tập sau buổi học

1. **Tự động hóa quy trình** — Viết script kết hợp: train → validate → register → promote tự động nếu tất cả metrics đạt ngưỡng.
2. **Thêm ngưỡng nghiêm ngặt hơn** — Điều chỉnh `thresholds.yaml` (ví dụ: r2_min = 0.75) và quan sát model nào PASS/FAIL.
3. **Viết Model Card chi tiết** — Bổ sung phần: phân tích công bằng (fairness) theo location, so sánh hiệu năng giữa các nhóm dữ liệu.
4. **Rollback có kiểm tra** — Viết script rollback có ghi nhật ký: ai rollback, khi nào, lý do, phiên bản trước và sau.

---

## Buổi tiếp theo

**Buổi 05 — Đóng gói Model và Triển khai API**: Đóng gói model bằng Docker, xây dựng REST API với FastAPI, viết health check và test endpoint dự đoán.
