# Buổi 02 — Quản lý Dữ liệu và Data Pipeline

> **Dataset:** [House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction)
> File raw: `data/raw/kc_house_data.csv` (~21613 rows). Mapping cột trong `src/ingestion/ingest.py`.

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

Các file / lệnh quan trọng:

| Thành phần | Vai trò |
|---|---|
| `dvc.yaml` | Định nghĩa các stage pipeline (deps → cmd → outs) |
| `params.yaml` / `configs/params.yaml` | Tham số pipeline (`test_size`, `val_size`, …) |
| `*.dvc` | Meta file Git track thay cho file data lớn |
| `dvc repro` | Chạy lại pipeline; chỉ re-run stage bị ảnh hưởng |
| `dvc dag` | Xem đồ thị phụ thuộc các stage |
| `dvc status` | Xem stage/data nào đã đổi so với lần chạy trước |
| `dvc add` | Đưa file data vào DVC tracking |
| `dvc push` / `dvc pull` | Upload / download data với remote |
| `dvc checkout` | Khôi phục data khớp meta `.dvc` hiện tại |

Pipeline trong `dvc.yaml` của buổi này:

```
kc_house_data.csv
       │
       ▼
   [ingest] ──► [validate]
       │
       ▼
  [preprocess] ── outs: processed.csv, label_encoder.pkl, scaler.pkl
       │
       ▼
    [split] ── outs: train.csv, val.csv, test.csv
```

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

### Bước 3: Chạy pipeline bằng DVC

> Trên Windows: luôn `venv\Scripts\activate` trước khi chạy `dvc` / `python`.

**Bước 3a — Cài và khởi tạo DVC (một lần)**

```powershell
pip install -r requirements.txt
dvc --version
```

Nếu chưa có thư mục `.dvc/`:

```powershell
dvc init
git add .dvc .dvcignore
git commit -m "chore: initialize DVC"
```

Nếu repo đã có `.dvc/` thì bỏ qua `dvc init`.

**Bước 3b — Version dataset bằng DVC**

CSV lớn không nên track bằng Git. Nếu `kc_house_data.csv` đang nằm trong Git:

```powershell
git rm --cached data/raw/kc_house_data.csv
```

Rồi thêm vào DVC (giữ file local):

```powershell
dvc add data/raw/kc_house_data.csv
git add data/raw/kc_house_data.csv.dvc data/raw/.gitignore
git commit -m "data: track kc_house_data.csv with DVC"
```

Sau lệnh này Git chỉ lưu file nhỏ `kc_house_data.csv.dvc` (checksum + path), còn CSV lớn do DVC quản lý.

**Bước 3c — Xem đồ thị pipeline**

```powershell
dvc dag
```

Kỳ vọng thấy chuỗi: `ingest → validate` và `ingest → preprocess → split` (đúng như `dvc.yaml`).

**Bước 3d — Chạy toàn bộ pipeline**

```powershell
dvc repro
```

DVC đọc `dvc.yaml`, chạy lần lượt các stage còn stale. Lần đầu sẽ chạy đủ `ingest`, `validate`, `preprocess`, `split`.

**Bước 3e — Kiểm tra trạng thái**

```powershell
dvc status
```

Nếu không đổi code/data/params → `Data and pipelines are up to date.`

**Bước 3f — Chạy lại có chọn lọc**

Sửa `configs/params.yaml` (ví dụ `test_size: 0.25`), rồi:

```powershell
dvc repro
dvc status
```

Chỉ các stage phụ thuộc param/`split` cần chạy lại; stage không đổi sẽ được skip.

**Bước 3g — Chạy lại 1 stage**

```powershell
dvc repro preprocess
dvc repro split
```

**Bước 3h — Cấu hình remote và `dvc push` / `dvc pull`**

Lab dùng remote **local folder** (không cần cloud). Tạo thư mục cạnh repo:

```powershell
mkdir ..\dvc-storage
dvc remote add -d localremote ..\dvc-storage
dvc remote list
git add .dvc/config
git commit -m "chore: add local DVC remote"
```

Đẩy data đã track lên remote:

```powershell
dvc push
```

Giả lập máy mới / mất file local, rồi kéo lại:

```powershell
Remove-Item data\raw\kc_house_data.csv
dvc pull
dir data\raw\kc_house_data.csv
```

`dvc push` = upload cache/data lên remote.  
`dvc pull` = download theo `.dvc` meta đang có trên Git.

> Buổi 08 có thể đổi remote sang MinIO (`s3://...`) — cùng lệnh `push`/`pull`.

**Bước 3i — Versioning data (Git tag + DVC)**

1. Mỗi lần đổi dataset: `dvc add data/raw/kc_house_data.csv` → commit file `.dvc` → `dvc push`
2. Gắn version:

```powershell
git tag data-v1
```

3. Sau này lấy lại đúng version:

```powershell
git checkout data-v1
dvc checkout
dvc pull
```

Git giữ meta (`.dvc`), DVC giữ file nặng (remote/cache).

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
3. **Version dữ liệu bằng DVC** — `dvc add` → commit `.dvc` → `dvc push`. Tag `data-v1`, rồi `git checkout` + `dvc pull` để khôi phục. Đổi `test_size` và `dvc repro`, giải thích stage nào re-run.
4. **Viết thêm test** — Bổ sung test case: kiểm tra tổng số dòng train + val + test = tổng dữ liệu sau ingest, kiểm tra không có rò rỉ dữ liệu giữa các tập.

---

## Buổi tiếp theo

**Buổi 03 — Training và Experiment Tracking với MLflow**: Huấn luyện model GradientBoostingRegressor, sử dụng MLflow để ghi lại tham số, metrics và artifacts. So sánh nhiều lần chạy thí nghiệm để chọn model tốt nhất.
