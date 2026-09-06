# Buổi 01 — Tổng quan MLOps và Kiến trúc Production

> **Dataset:** [House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) (`data/raw/kc_house_data.csv`), đã map sang `data/raw/houses.csv` (~21510 rows; `sqft_living→area`, `yr_built→age`, `zipcode→location`, `floors`).
> Chuẩn bị lại: `python scripts/prepare_king_county.py`


## Mục tiêu buổi học

- Hiểu MLOps là gì, tại sao cần MLOps trong môi trường production
- Nhận biết các giai đoạn của AI/ML lifecycle
- Thiết lập repository chuẩn cho dự án ML
- Vẽ được architecture diagram cơ bản
- Viết project charter cho dự án House Price Prediction

---

## Kiến thức lý thuyết

### MLOps = ML + DevOps

MLOps (Machine Learning Operations) là tập hợp các phương pháp, quy trình và công cụ giúp triển khai, vận hành và bảo trì hệ thống Machine Learning trong môi trường production một cách đáng tin cậy và hiệu quả.

Trong thực tế, phần lớn thời gian của một dự án ML **không phải** là viết model mà là:

| Hoạt động                  | Tỷ lệ thời gian ước tính |
| -------------------------- | ------------------------- |
| Thu thập & làm sạch dữ liệu | ~40%                      |
| Xây dựng pipeline          | ~20%                      |
| Triển khai & giám sát       | ~25%                      |
| Huấn luyện & tinh chỉnh model | ~15%                   |

MLOps giải quyết các vấn đề phổ biến:

- **Không tái tạo được kết quả** — thiếu quản lý phiên bản dữ liệu và tham số
- **Triển khai thủ công** — dễ sai sót, mất thời gian
- **Không phát hiện model xuống cấp** — thiếu hệ thống giám sát
- **Không có quy trình kiểm duyệt** — model đưa lên production mà không qua validation

### ML Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ML LIFECYCLE                                │
│                                                                     │
│  Business Problem                                                   │
│       │                                                             │
│       ▼                                                             │
│  Data Collection ──► Data Validation ──► Feature Engineering        │
│                                                │                    │
│                                                ▼                    │
│                                          Model Training             │
│                                                │                    │
│                                                ▼                    │
│                                        Model Evaluation             │
│                                                │                    │
│                                                ▼                    │
│                                         Model Registry              │
│                                                │                    │
│                                                ▼                    │
│                                          Model Serving              │
│                                                │                    │
│                                                ▼                    │
│                                           Monitoring                │
│                                                │                    │
│                                                ▼                    │
│                                           Retraining ──────┐       │
│                                                            │       │
│                              ◄─────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

### Các vai trò trong team MLOps

| Vai trò           | Trách nhiệm chính                                                   | Công cụ thường dùng                |
| ----------------- | -------------------------------------------------------------------- | ---------------------------------- |
| Data Engineer     | Xây dựng pipeline dữ liệu, đảm bảo chất lượng dữ liệu              | Airflow, Spark, SQL, dbt           |
| ML Engineer       | Huấn luyện model, tinh chỉnh hyperparams, đánh giá hiệu năng       | Scikit-learn, PyTorch, MLflow      |
| MLOps Engineer    | Triển khai model, CI/CD, giám sát, quản lý hạ tầng                  | Docker, Kubernetes, GitHub Actions |
| Product Owner     | Định nghĩa bài toán kinh doanh, đặt tiêu chí chấp nhận             | Jira, Confluence                   |

### 4 trụ cột của MLOps

1. **Data Management** — Quản lý phiên bản dữ liệu, kiểm tra chất lượng, lưu trữ metadata
2. **Model Management** — Theo dõi thí nghiệm, đăng ký model, quản lý vòng đời model
3. **Deployment** — Đóng gói model, triển khai API, CI/CD pipeline
4. **Monitoring** — Giám sát hiệu năng model, phát hiện data drift, cảnh báo

---

## Cấu trúc thư mục dự án

```
mlops-starter-repo/
├── configs/
│   └── params.yaml              # Tham số cấu hình cho toàn bộ pipeline
├── data/
│   ├── raw/
│   │   └── houses.csv           # Dữ liệu thô ban đầu
│   └── processed/               # Dữ liệu đã xử lý (train/val/test)
├── docs/
│   ├── architecture.md          # Sơ đồ kiến trúc hệ thống
│   └── model-card.md            # Tài liệu mô tả model
├── models/                      # Model đã huấn luyện (.pkl)
├── notebooks/                   # Jupyter notebooks phân tích, thử nghiệm
├── reports/
│   └── evaluation.json          # Kết quả đánh giá model
├── scripts/                     # Các script hỗ trợ (validate, promote, ...)
├── src/
│   ├── ingestion/
│   │   └── ingest.py            # Đọc dữ liệu thô
│   ├── validation/
│   │   └── validate.py          # Kiểm tra chất lượng dữ liệu
│   ├── preprocessing/
│   │   └── preprocess.py        # Tiền xử lý: encode, scale
│   ├── split/
│   │   └── split.py             # Chia train/val/test
│   ├── training/
│   │   └── train.py             # Huấn luyện model và log MLflow
│   └── serving/
│       └── app.py               # API phục vụ dự đoán
├── tests/                       # Unit tests
├── dvc.yaml                     # Pipeline DVC
├── requirements.txt             # Thư viện Python cần thiết
├── Dockerfile                   # Đóng gói ứng dụng
└── README.md                    # Tài liệu tổng quan
```

---

## Hướng dẫn thực hành

### Bước 1: Clone repository và cài đặt môi trường

```powershell
git clone <repository-url> mlops-starter-repo
cd mlops-starter-repo

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

### Bước 2: Kiểm tra dataset

```python
python -c "import pandas as pd; df = pd.read_csv('data/raw/houses.csv'); print(df.shape); print(df.head())"
```

Mô tả các cột trong dataset:

| Cột        | Kiểu dữ liệu | Mô tả                                      | Ví dụ           |
| ---------- | -------------- | -------------------------------------------- | ---------------- |
| area       | float          | Diện tích sống (sqft)                        | 2000             |
| bedrooms   | int            | Số phòng ngủ                                 | 3                |
| bathrooms  | float          | Số phòng tắm                                 | 2.25             |
| age        | int            | Tuổi nhà (năm)                               | 10               |
| floors     | float          | Số tầng                                      | 1.0              |
| location   | str            | Zipcode (King County)                        | 98178            |
| price      | float          | Giá nhà (USD) — biến mục tiêu                | 450000.0         |

### Bước 3: Đọc architecture diagram

```powershell
type docs\architecture.md
```

Sơ đồ kiến trúc mô tả luồng dữ liệu từ nguồn thô đến API phục vụ, bao gồm các thành phần: Data Pipeline, Training Pipeline, Model Registry, Serving API, và Monitoring.

### Bước 4: Viết project charter

Tạo file `docs/project-charter.md` theo mẫu sau:

```markdown
# Project Charter — House Price Prediction

## Tên dự án
House Price Prediction

## Mục tiêu kinh doanh
Dự đoán giá nhà dựa trên các đặc trưng (diện tích, vị trí, ...) để hỗ trợ quyết định mua bán bất động sản.

## Chỉ số thành công
- RMSE < 250.000
- R² > 0.60
- Thời gian phản hồi API < 200ms (p95)

## Phạm vi
- Dữ liệu: King County house sales → houses.csv (~21510 bản ghi)
- Model: GradientBoostingRegressor
- Triển khai: REST API trên Docker

## Rủi ro
- Dữ liệu không đại diện cho thị trường thực tế
- Data drift khi giá nhà biến động mạnh

## Đội ngũ
- ML Engineer: huấn luyện và đánh giá model
- MLOps Engineer: triển khai và giám sát

## Thời gian dự kiến
8 buổi (4 tuần)
```

### Bước 5: Verify công cụ

```powershell
python --version
git --version
docker --version
```

Đảm bảo kết quả trả về phiên bản hợp lệ cho cả 3 công cụ.

---

## Cấu hình dự án

Nội dung file `configs/params.yaml`:

```yaml
data:
  raw_path: data/raw/houses.csv
  processed_dir: data/processed
  test_size: 0.2
  val_size: 0.1
  random_state: 42

features:
  numeric:
    - area
    - bedrooms
    - bathrooms
    - age
    - floors
  categorical:
    - location
  target: price

preprocessing:
  scaler: StandardScaler
  encoder: LabelEncoder

training:
  model: GradientBoostingRegressor
  params:
    n_estimators: 200
    max_depth: 5
    learning_rate: 0.1
    random_state: 42
  experiment_name: house-price-prediction

mlflow:
  tracking_uri: http://localhost:5000
  experiment_name: house-price-prediction
```

---

## Bài tập sau buổi học

1. **Hoàn thiện project charter** — Bổ sung thêm phần "Giả định" và "Ràng buộc kỹ thuật" vào project charter.
2. **Vẽ architecture diagram** — Sử dụng draw.io hoặc Mermaid vẽ lại kiến trúc hệ thống với đầy đủ các thành phần.
3. **Khám phá dataset** — Viết một notebook phân tích thăm dò dữ liệu (EDA): thống kê mô tả, phân phối giá, tương quan giữa các biến.
4. **So sánh MLOps tools** — Tìm hiểu và so sánh 3 nền tảng MLOps phổ biến (MLflow, Kubeflow, Vertex AI) theo bảng tiêu chí.

---

## Buổi tiếp theo

**Buổi 02 — Quản lý Dữ liệu và Data Pipeline**: Xây dựng pipeline hoàn chỉnh từ ingestion → validation → preprocessing → split. Sử dụng DVC để quản lý phiên bản dữ liệu và viết unit test cho từng bước trong pipeline.
