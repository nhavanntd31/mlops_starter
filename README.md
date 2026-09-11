# Buổi 03 — Training và Experiment Tracking với MLflow

> **Dataset:** [House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) (`data/raw/kc_house_data.csv`), raw `data/raw/kc_house_data.csv` (~21510 rows; `sqft_living→area`, `yr_built→age`, `zipcode→location`, `floors`).
> Chuẩn bị lại: `# column mapping in src/ingestion/ingest.py`


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
│   ├── data/
│   │   └── ensure_data.py       # Kiểm tra data; thiếu thì pull/rebuild
│   └── training/
│       ├── train.py             # Huấn luyện model và log MLflow
│       └── features.py          # Extract feature theo configs/params.yaml
├── tests/
│   └── test_training.py         # Unit test cho training pipeline
├── configs/
│   └── params.yaml              # Cập nhật thêm phần training
├── models/
│   └── model.pkl                # Model đã huấn luyện (đầu ra)
└── reports/
    ├── evaluation.json          # Báo cáo đánh giá (đầu ra)
    └── features.json            # Danh sách feature đã log
```

---

## Hướng dẫn thực hành

### Bước 1: Chuẩn bị dữ liệu từ buổi 2

Cần có `train.csv`, `val.csv`, `test.csv` trong `data/processed/` trước khi train. Dùng **đúng `dvc.lock` buổi 2 của máy bạn** (hash khớp data đã `dvc push` vào `../../dvc-storage`). Không dùng lock của người khác.

**Cách nhanh — kiểm tra và tự bổ sung data**

```powershell
python src/data/ensure_data.py
```

Script kiểm tra raw + train/val/test (file tồn tại, có cột bắt buộc, không rỗng). Nếu thiếu: thử `dvc pull` (khi có `dvc.lock` + `.dvc/config`), rồi nếu vẫn thiếu thì chạy `ingest → validate → preprocess → split`. `train.py` cũng gọi sẵn bước này trước khi huấn luyện.

**Cách 1 — Pull data version buổi 2 (mặc định)**

```powershell
git checkout session/03
git checkout session/02 -- dvc.lock .dvc/config
dvc pull
```

Nếu cùng máy đã làm buổi 2 và cache local còn:

```powershell
dvc checkout
```

**Cách 2 — Mất `dvc.lock`: sinh lại data bằng DVC**

```powershell
dvc repro
```

`dvc repro` đọc `dvc.yaml` và chạy lại `ingest → validate → preprocess → split`. Cần sẵn `data/raw/kc_house_data.csv` (trên `session/03` file này đang trong Git).

Không có DVC thì chạy từng bước:

```powershell
python src/ingestion/ingest.py
python src/validation/validate.py
python src/preprocessing/preprocess.py
python src/split/split.py
```

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

### Bước 3: Bật MLflow UI rồi huấn luyện

`train.py` log thí nghiệm tới `http://localhost:5000`. **Phải bật UI trước**, để nguyên terminal đó, rồi mới train ở terminal khác. Nếu quên, lệnh train sẽ đứng im vì retry kết nối bị từ chối.

**Terminal 1** — giữ chạy, không Ctrl+C:

```powershell
mlflow ui --port 5000
```

Đợi log `Uvicorn running on http://127.0.0.1:5000`, rồi mở http://localhost:5000.

**Terminal 2** — train:

```powershell
$env:PYTHONUTF8="1"
python src/training/train.py
```

`$env:PYTHONUTF8="1"` tránh lỗi encoding emoji MLflow trên Windows.

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

UI đã chạy từ Bước 3. Mở trình duyệt tại `http://localhost:5000`. Bạn sẽ thấy:

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

### Bước 6: Feature engineering rồi train lần 2

Lần 1 (Bước 3) là **baseline**: `feature_engineering.enabled: false`, chỉ 6 cột gốc. Giữ nguyên hyperparams, bật extract rồi train lần 2 để MLflow so sánh đúng phần feature, không lẫn thay đổi cây.

Mở `configs/params.yaml`:

```yaml
feature_engineering:
  enabled: true
  run_name: with-extracted-features
  eps: 0.000001
  extract:
    - total_rooms
    - bath_bed_ratio
    - area_per_floor
    - area_per_room
    - age_squared
```

Có thể bớt/thêm tên trong `extract` (các extractor có sẵn: `total_rooms`, `bath_bed_ratio`, `area_per_floor`, `area_per_room`, `age_squared`). `eps` tránh chia cho 0.

Chạy lại training (Terminal 1 vẫn giữ `mlflow ui`):

```powershell
$env:PYTHONUTF8="1"
python src/training/train.py
```

Kỳ vọng log:

```
[Training] run_name=with-extracted-features fe_enabled=True
[Training] n_features=11
[Training] extracted=['total_rooms', 'bath_bed_ratio', 'area_per_floor', 'area_per_room', 'age_squared']
```

MLflow run lần 2 có:

- tag `run_type=feature_engineering`
- params `fe_enabled`, `n_features`, `feature_names`, `extracted_features`
- artifact `features.json` (danh sách feature + feature importance)

Mở UI, chọn run `baseline` và `with-extracted-features`, nhấn **Compare**.

File local: `reports/features.json`.

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
2. Gọi `extract_features()` nếu `feature_engineering.enabled: true`
3. Khởi tạo `GradientBoostingRegressor` với tham số từ config
4. Gọi `model.fit(X_train, y_train)` để huấn luyện
5. Đánh giá trên tập validation và test
6. Bắt đầu MLflow run:
   - `mlflow.log_params()` — hyperparams + `fe_enabled`, `n_features`, `feature_names`
   - `mlflow.log_metrics()` — RMSE, MAE, R²
   - `mlflow.log_dict()` — artifact `features.json`
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
