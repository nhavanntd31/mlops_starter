# Buổi 02 — Quản lý Dữ liệu và Data Pipeline

> **Dataset:** [House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) (`data/raw/kc_house_data.csv`), raw `data/raw/kc_house_data.csv` (~21510 rows; `sqft_living→area`, `yr_built→age`, `zipcode→location`, `floors`).
> Chuẩn bị lại: `# column mapping in src/ingestion/ingest.py`


## Mục tiêu buổi học

- Xây dựng data pipeline từ đầu đến cuối: ingest → validate → preprocess → split
- Hiểu data quality là gì và cách kiểm tra chất lượng dữ liệu
- Sử dụng DVC để quản lý phiên bản dataset
- Viết unit test cho data pipeline

---

## Kiến thức lý thuyết

### Data Pipeline là gì?

Data pipeline là chuỗi các bước xử lý dữ liệu có thứ tự, tự động hóa, và có thể tái tạo được. Mỗi bước nhận đầu vào từ bước trước và tạo đầu ra cho bước sau.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        DATA PIPELINE                                 │
│                                                                      │
│  data/raw/kc_house_data.csv                                                 │
│       │                                                              │
│       ▼                                                              │
│  ┌──────────┐    ┌──────────┐    ┌─────────────┐    ┌──────────┐    │
│  │  Ingest   │──►│ Validate  │──►│ Preprocess   │──►│  Split    │    │
│  │          │    │          │    │             │    │          │    │
│  │ Đọc CSV  │    │ Kiểm tra │    │ Encode      │    │ Train    │    │
│  │ chuẩn hóa│    │ chất lượng│    │ Scale       │    │ Val      │    │
│  │ schema   │    │ dữ liệu  │    │ Lưu encoder │    │ Test     │    │
│  └──────────┘    └──────────┘    └─────────────┘    └──────────┘    │
│                                                          │           │
│                                                          ▼           │
│                                              data/processed/         │
│                                              ├── train.csv           │
│                                              ├── val.csv             │
│                                              └── test.csv            │
└──────────────────────────────────────────────────────────────────────┘
```

### Data Quality — 6 chiều chất lượng dữ liệu

| Chiều           | Mô tả                                              | Ví dụ kiểm tra                                     |
| --------------- | --------------------------------------------------- | --------------------------------------------------- |
| Completeness    | Dữ liệu không bị thiếu                             | Kiểm tra tỷ lệ null < 5%                           |
| Consistency     | Dữ liệu nhất quán giữa các nguồn                   | Cùng đơn vị đo lường (m², VND)                      |
| Accuracy        | Dữ liệu phản ánh đúng thực tế                      | Diện tích > 0, giá > 0                              |
| Validity        | Dữ liệu nằm trong phạm vi hợp lệ                   | Số phòng ngủ ∈ [0, 20], tuổi nhà ∈ [0, 200]        |
| Uniqueness      | Không có bản ghi trùng lặp                          | Không có dòng giống hệt nhau                        |
| Timeliness      | Dữ liệu được cập nhật đúng thời điểm               | Dataset không quá 6 tháng tuổi                      |

### DVC (Data Version Control)

DVC là công cụ quản lý phiên bản dữ liệu và pipeline cho dự án ML, hoạt động tương tự Git nhưng dành cho file lớn và pipeline.

Các file quan trọng:

- **dvc.yaml** — Định nghĩa các bước trong pipeline, đầu vào và đầu ra
- **params.yaml** — Tham số cấu hình được pipeline sử dụng
- **dvc repro** — Lệnh chạy lại toàn bộ pipeline (chỉ chạy lại bước có thay đổi)

---

## Cấu trúc file mới thêm

```
mlops-starter-repo/
├── src/
│   ├── ingestion/
│   │   └── ingest.py            # Đọc và chuẩn hóa dữ liệu thô
│   ├── validation/
│   │   └── validate.py          # Kiểm tra chất lượng dữ liệu
│   ├── preprocessing/
│   │   └── preprocess.py        # Mã hóa biến phân loại, chuẩn hóa biến số
│   └── split/
│       └── split.py             # Chia dữ liệu train/val/test
├── tests/
│   └── test_data.py             # Unit test cho data pipeline
├── dvc.yaml                     # Định nghĩa pipeline DVC
└── params.yaml                  # Tham số pipeline (symlink hoặc copy từ configs/)
```

---

## Hướng dẫn thực hành

### Bước 1: Checkout branch

```powershell
git checkout -b session02-data-pipeline
```

### Bước 2: Chạy từng bước pipeline

**Bước 2a — Ingest (đọc dữ liệu thô)**

```powershell
python src/ingestion/ingest.py
```

Kết quả: đọc `data/raw/kc_house_data.csv`, kiểm tra schema, lưu dữ liệu đã chuẩn hóa.

**Bước 2b — Validate (kiểm tra chất lượng)**

```powershell
python src/validation/validate.py
```

Kết quả: kiểm tra 6 quy tắc chất lượng, in báo cáo PASS/FAIL cho từng quy tắc.

**Bước 2c — Preprocess (tiền xử lý)**

```powershell
python src/preprocessing/preprocess.py
```

Kết quả: mã hóa cột `location` bằng LabelEncoder, chuẩn hóa biến số bằng StandardScaler, lưu encoder và scaler vào `models/`.

**Bước 2d — Split (chia dữ liệu)**

```powershell
python src/split/split.py
```

Kết quả: chia thành train (70%), val (10%), test (20%) và lưu vào `data/processed/`.

### Bước 3: Chạy toàn bộ pipeline một lệnh

**Cách 1 — Python one-liner:**

```powershell
python -c "import subprocess; [subprocess.run(['python', f'src/{m}/{m.split('/')[-1]}.py'], check=True) for m in ['ingestion/ingest', 'validation/validate', 'preprocessing/preprocess', 'split/split']]"
```

**Cách 2 — DVC:**

```powershell
dvc repro
```

### Bước 4: Kiểm tra kết quả

```powershell
dir data\processed\

python -c "import pandas as pd; [print(f'{f}: {len(pd.read_csv(f\"data/processed/{f}\"))} dòng') for f in ['train.csv', 'val.csv', 'test.csv']]"
```

Kết quả mong đợi (với ~21510 bản ghi King County):

| Tập dữ liệu | Tỷ lệ | Số dòng ước tính |
| ------------ | ------ | ---------------- |
| train.csv    | 70%    | ~15057           |
| val.csv      | 10%    | ~2151            |
| test.csv     | 20%    | ~4302            |

### Bước 5: Chạy tests

```powershell
pytest tests/test_data.py -v
```

Kết quả mong đợi: tất cả test case đều PASSED.

---

## Chi tiết code

### `src/ingestion/ingest.py`

Module này chịu trách nhiệm đọc dữ liệu thô từ file CSV. Các chức năng:

- Đọc file `data/raw/kc_house_data.csv` bằng `pandas.read_csv()`
- Kiểm tra sự tồn tại của file
- Xác nhận schema (danh sách cột) khớp với cấu hình
- Chuyển đổi kiểu dữ liệu nếu cần
- Trả về DataFrame đã chuẩn hóa

### `src/validation/validate.py`

Module kiểm tra chất lượng dữ liệu theo 6 quy tắc:

1. **Cột bắt buộc** — Kiểm tra tất cả cột cần thiết đều tồn tại
2. **Kiểu số** — Các cột `area`, `bedrooms`, `bathrooms`, `age`, `floors`, `price` phải là kiểu số
3. **Giá trị null** — Tỷ lệ null mỗi cột phải < 5%
4. **Bản ghi trùng lặp** — Tỷ lệ trùng lặp phải < 1%
5. **Phạm vi giá trị** — `area` ∈ [300, 10000], `bedrooms` ∈ [1, 10], `floors` ∈ [1, 4], `price` ∈ [50000, 3000000]
6. **Vị trí hợp lệ** — Cột `location` (zipcode) không được rỗng

### `src/preprocessing/preprocess.py`

Module tiền xử lý dữ liệu:

- **LabelEncoder** — Mã hóa cột `location` từ chuỗi sang số nguyên
- **StandardScaler** — Chuẩn hóa các biến số về mean=0, std=1
- Lưu encoder vào `models/label_encoder.pkl`
- Lưu scaler vào `models/scaler.pkl`
- Lưu dữ liệu đã xử lý với cột đã được mã hóa và chuẩn hóa

### `src/split/split.py`

Module chia dữ liệu thành 3 tập:

- Lần 1: `train_test_split` với `test_size=0.2` → tách test set
- Lần 2: `train_test_split` trên phần còn lại với `test_size=0.125` (= 10% tổng) → tách val set
- Lưu `train.csv`, `val.csv`, `test.csv` vào `data/processed/`
- Sử dụng `random_state=42` để kết quả tái tạo được

---

## Quy tắc Validation

| #  | Quy tắc                  | Điều kiện                                                        | Kết quả nếu vi phạm      |
| -- | ------------------------ | ---------------------------------------------------------------- | ------------------------- |
| 1  | Cột bắt buộc             | Tất cả cột trong config phải tồn tại                            | FAIL — liệt kê cột thiếu |
| 2  | Kiểu dữ liệu số         | Cột số phải có dtype là int hoặc float                           | FAIL — liệt kê cột sai   |
| 3  | Giá trị null             | Tỷ lệ null mỗi cột < 5%                                        | FAIL — in tỷ lệ null     |
| 4  | Bản ghi trùng lặp        | Tỷ lệ dòng trùng < 1%                                          | FAIL — in số dòng trùng  |
| 5  | Phạm vi giá trị          | `area` > 0, `bedrooms` ≥ 0, `price` > 0                         | FAIL — in bản ghi sai    |
| 6  | Vị trí hợp lệ            | `location` ∈ danh sách cho phép trong config                    | FAIL — in giá trị lạ     |

---

## Bài tập sau buổi học

1. **Thêm quy tắc validation** — Viết thêm kiểm tra: `bathrooms` ≤ `bedrooms`, `age` ≥ 0, phát hiện outlier bằng IQR.
2. **Xử lý giá trị thiếu** — Thay vì chỉ kiểm tra null, hãy viết logic xử lý: điền median cho biến số, điền mode cho biến phân loại.
3. **Version dữ liệu bằng DVC** — Khởi tạo DVC (`dvc init`), thêm `data/raw/kc_house_data.csv` vào DVC tracking, push lên remote storage.
4. **Viết thêm test** — Bổ sung test case: kiểm tra tổng số dòng train + val + test = tổng dữ liệu gốc, kiểm tra không có rò rỉ dữ liệu giữa các tập.

---

## Buổi tiếp theo

**Buổi 03 — Training và Experiment Tracking với MLflow**: Huấn luyện model GradientBoostingRegressor, sử dụng MLflow để ghi lại tham số, metrics và artifacts. So sánh nhiều lần chạy thí nghiệm để chọn model tốt nhất.
