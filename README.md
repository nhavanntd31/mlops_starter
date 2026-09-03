# Buổi 03 — Training và Experiment Tracking với MLflow

## Mục tiêu buổi học

- Huấn luyện model GradientBoostingRegressor trên dữ liệu đã xử lý
- Hiểu và sử dụng MLflow để theo dõi thí nghiệm: params, metrics, artifacts
- So sánh nhiều lần chạy (run) để chọn model tốt nhất
- Viết báo cáo đánh giá (evaluation report) tự động
- Viết unit test cho training pipeline

---

## Kiến thức lý thuyết

### Tại sao cần Experiment Tracking?

Khi huấn luyện model, bạn thường thử nhiều tổ hợp tham số khác nhau. Nếu không ghi lại, bạn sẽ:

- Không nhớ tham số nào cho kết quả tốt nhất
- Không tái tạo được kết quả trước đó
- Không so sánh được các phiên bản model
- Không biết model nào đang chạy trên production

Experiment tracking giải quyết bằng cách ghi lại:

- **Parameters** — Tham số huấn luyện (n_estimators, learning_rate, ...)
- **Metrics** — Chỉ số đánh giá (RMSE, MAE, R², MAPE)
- **Artifacts** — File đầu ra (model.pkl, evaluation.json, biểu đồ)
- **Tags** — Nhãn phân loại (dataset_version, git_commit, author)

### Các thành phần của MLflow

| Thành phần  | Mô tả                                                        |
| ----------- | ------------------------------------------------------------- |
| Experiment  | Nhóm các lần chạy thí nghiệm theo cùng một bài toán         |
| Run         | Một lần chạy huấn luyện cụ thể với bộ tham số riêng          |
| Parameters  | Tham số đầu vào được ghi lại cho mỗi run                     |
| Metrics     | Chỉ số đánh giá được tính toán và ghi lại                    |
| Artifacts   | File đầu ra: model đã huấn luyện, báo cáo, biểu đồ          |
| Tags        | Metadata bổ sung: phiên bản dữ liệu, commit hash, tác giả   |

### Metrics cho Tabular Regression

| Metric | Công thức                              | Ý nghĩa                                                    | Giá trị tốt     |
| ------ | -------------------------------------- | ----------------------------------------------------------- | ---------------- |
| RMSE   | √(Σ(yᵢ - ŷᵢ)² / n)                   | Sai số trung bình bình phương gốc, cùng đơn vị với y       | Càng thấp càng tốt |
| MAE    | Σ\|yᵢ - ŷᵢ\| / n                      | Sai số tuyệt đối trung bình, ít nhạy với outlier hơn RMSE  | Càng thấp càng tốt |
| R²     | 1 - Σ(yᵢ - ŷᵢ)² / Σ(yᵢ - ȳ)²        | Tỷ lệ phương sai được giải thích bởi model                 | Càng gần 1 càng tốt |
| MAPE   | (Σ\|yᵢ - ŷᵢ\| / \|yᵢ\|) × 100 / n    | Phần trăm sai số tuyệt đối trung bình                      | < 10% là rất tốt  |

### Training Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                      TRAINING PIPELINE                               │
│                                                                      │
│  data/processed/          configs/params.yaml                        │
│  ├── train.csv                    │                                  │
│  ├── val.csv                      │                                  │
│  └── test.csv                     │                                  │
│       │                           │                                  │
│       ▼                           ▼                                  │
│  ┌─────────────────────────────────────┐                             │
│  │         src/training/train.py       │                             │
│  │                                     │                             │
│  │  1. Đọc cấu hình (params.yaml)     │                             │
│  │  2. Tải dữ liệu train/val/test     │                             │
│  │  3. Huấn luyện model               │                             │
│  │  4. Đánh giá trên val và test       │                             │
│  │  5. Log vào MLflow                  │                             │
│  │  6. Lưu model và báo cáo           │                             │
│  └─────────────────────────────────────┘                             │
│       │                    │                    │                     │
│       ▼                    ▼                    ▼                     │
│  models/model.pkl   reports/evaluation.json   MLflow Tracking        │
│                                               (params, metrics,      │
│                                                artifacts)            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Cấu trúc file mới thêm

```
mlops-starter-repo/
├── src/
│   └── training/
│       └── train.py             # Huấn luyện model và log MLflow
├── tests/
│   └── test_training.py         # Unit test cho training pipeline
├── configs/
│   └── params.yaml              # Cập nhật thêm phần training
├── models/
│   └── model.pkl                # Model đã huấn luyện (đầu ra)
└── reports/
    └── evaluation.json          # Báo cáo đánh giá (đầu ra)
```

---

## Hướng dẫn thực hành

### Bước 1: Checkout và chạy data pipeline trước

```powershell
git checkout -b session03-training

python src/ingestion/ingest.py
python src/validation/validate.py
python src/preprocessing/preprocess.py
python src/split/split.py
```

Đảm bảo thư mục `data/processed/` đã có `train.csv`, `val.csv`, `test.csv`.

### Bước 2: Xem cấu hình training

```yaml
training:
  model: GradientBoostingRegressor
  params:
    n_estimators: 200
    max_depth: 5
    learning_rate: 0.1
    random_state: 42
  experiment_name: house-price-prediction
```

### Bước 3: Huấn luyện model

```powershell
python src/training/train.py
```

Kết quả mong đợi:

```
Đang tải dữ liệu...
Đang huấn luyện GradientBoostingRegressor...
Đánh giá trên tập validation:
  RMSE: 25431.12
  MAE:  18234.56
  R²:   0.72
  MAPE: 15.3%
Đánh giá trên tập test:
  RMSE: 26102.45
  MAE:  19012.33
  R²:   0.70
  MAPE: 16.1%
Model đã lưu tại: models/model.pkl
Báo cáo đã lưu tại: reports/evaluation.json
MLflow run ID: abc123def456
```

### Bước 4: Xem MLflow UI

```powershell
mlflow ui --port 5000
```

Mở trình duyệt tại `http://localhost:5000`. Bạn sẽ thấy:

- Danh sách experiments bên trái
- Bảng các runs với cột params và metrics
- Nhấp vào một run để xem chi tiết: parameters, metrics, artifacts

### Bước 5: Xem evaluation report

```powershell
python -c "import json; print(json.dumps(json.load(open('reports/evaluation.json')), indent=2))"
```

Cấu trúc file `evaluation.json`:

```json
{
  "model": "GradientBoostingRegressor",
  "timestamp": "2026-09-03T22:00:00",
  "validation": {
    "rmse": 25431.12,
    "mae": 18234.56,
    "r2": 0.72,
    "mape": 15.3
  },
  "test": {
    "rmse": 26102.45,
    "mae": 19012.33,
    "r2": 0.70,
    "mape": 16.1
  },
  "params": {
    "n_estimators": 200,
    "max_depth": 5,
    "learning_rate": 0.1,
    "random_state": 42
  },
  "mlflow_run_id": "abc123def456"
}
```

### Bước 6: Thử thay đổi hyperparams và so sánh

Mở `configs/params.yaml`, thay đổi tham số:

```yaml
training:
  params:
    n_estimators: 300
    max_depth: 7
    learning_rate: 0.05
```

Chạy lại training:

```powershell
python src/training/train.py
```

Mở MLflow UI, chọn 2 runs và nhấn **Compare** để so sánh metrics giữa các lần chạy.

### Bước 7: Chạy tests

```powershell
pytest tests/test_training.py -v
```

---

## Chi tiết code — `src/training/train.py`

### Hàm `load_config()`

- Đọc file `configs/params.yaml` bằng thư viện `yaml`
- Trả về dictionary chứa toàn bộ cấu hình

### Hàm `load_data(config)`

- Đọc `train.csv`, `val.csv`, `test.csv` từ `data/processed/`
- Tách features (X) và target (y) dựa trên cấu hình
- Trả về 6 biến: `X_train, y_train, X_val, y_val, X_test, y_test`

### Hàm `evaluate(model, X, y)`

- Tính 4 metrics: RMSE, MAE, R², MAPE
- Sử dụng `sklearn.metrics`: `mean_squared_error`, `mean_absolute_error`, `r2_score`
- MAPE tính thủ công: `np.mean(np.abs((y - y_pred) / y)) * 100`
- Trả về dictionary `{"rmse": ..., "mae": ..., "r2": ..., "mape": ...}`

### Hàm `train()`

Luồng chính:

1. Gọi `load_config()` để đọc tham số
2. Gọi `load_data()` để tải dữ liệu
3. Khởi tạo `GradientBoostingRegressor` với tham số từ config
4. Gọi `model.fit(X_train, y_train)` để huấn luyện
5. Đánh giá trên tập validation và test bằng `evaluate()`
6. Bắt đầu MLflow run:
   - `mlflow.log_params()` — ghi tham số
   - `mlflow.log_metrics()` — ghi metrics
   - `mlflow.sklearn.log_model()` — lưu model artifact
7. Lưu model vào `models/model.pkl` bằng `joblib.dump()`
8. Lưu báo cáo vào `reports/evaluation.json`

### Định dạng `evaluation.json`

File JSON chứa:

- `model` — Tên thuật toán
- `timestamp` — Thời gian huấn luyện
- `validation` — Metrics trên tập validation
- `test` — Metrics trên tập test
- `params` — Tham số huấn luyện
- `mlflow_run_id` — ID của MLflow run để truy vết

---

## Bài tập sau buổi học

1. **Thử thuật toán khác** — Thay GradientBoostingRegressor bằng RandomForestRegressor hoặc XGBRegressor, so sánh kết quả trên MLflow.
2. **Grid search** — Viết script tự động thử nhiều tổ hợp hyperparams (n_estimators ∈ [100, 200, 300], max_depth ∈ [3, 5, 7]) và log tất cả vào MLflow.
3. **Feature importance** — Thêm code xuất biểu đồ feature importance và log vào MLflow artifacts.
4. **Viết thêm test** — Bổ sung test: kiểm tra model có thể predict được, kiểm tra output shape đúng, kiểm tra metrics nằm trong phạm vi hợp lý.

---

## Buổi tiếp theo

**Buổi 04 — Model Registry và Governance**: Đăng ký model vào MLflow Model Registry, thiết lập quy trình duyệt model (Candidate → Staging → Production), viết validation pipeline tự động và Model Card.
