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
├── scripts/
│   └── prepare_data.py          # Giải nén dataset seed ra data/raw/ (bước 0c)
├── data/
│   ├── seed/
│   │   └── kc_house_data.csv.gz # Dataset nén, track bằng Git để ai clone cũng có data
│   └── raw/
│       ├── kc_house_data.csv    # File raw thật — DVC quản, KHÔNG nằm trong Git
│       └── kc_house_data.csv.dvc# Meta file Git track thay cho CSV lớn
├── tests/
│   └── test_data.py             # Unit test cho data pipeline
├── dvc.yaml                     # Định nghĩa pipeline DVC
└── params.yaml                  # Tham số pipeline (symlink hoặc copy từ configs/)
```

---

## Hướng dẫn thực hành

> Lệnh viết theo PowerShell. Trên Linux/macOS đổi 3 chỗ:
> `venv\Scripts\activate` → `source venv/bin/activate` · `mkdir ..\dvc-storage` → `mkdir -p ../dvc-storage` · `dir` → `ls`

### Bước 0: Chuẩn bị sau khi clone repo

Repo không chứa file CSV thô và không chứa thư mục DVC remote — phải tự dựng 2 thứ này trước.

**0a — Môi trường Python**

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
dvc --version
```

Kết quả: in ra phiên bản DVC, ví dụ `3.67.1`.

**0b — Tạo thư mục DVC remote**

```powershell
mkdir ..\dvc-storage
dvc remote list
```

Kết quả:

```
localremote     C:\...\dvc-storage  (default)
```

Đường dẫn phải nằm **cạnh** repo, không nằm trong repo:

```
Documents/
├── mlops_starter/     ← repo
└── dvc-storage/       ← remote (đóng vai S3/MinIO)
```

**0c — Giải nén dữ liệu thô**

```powershell
python scripts/prepare_data.py
```

Kết quả:

```
[PrepareData] Đã giải nén data/seed/kc_house_data.csv.gz -> data/raw/kc_house_data.csv
[PrepareData] 2515206 bytes, md5 b1e7bdf4f3e61792c0979a5697dc7145
```

**0d — Chạy pipeline lần đầu**

```powershell
dvc repro
dvc push
```

Kết quả:

```
Stage 'ingest' didn't change, skipping
Stage 'validate' didn't change, skipping
Running stage 'preprocess':
Running stage 'split':
[Split] Train: 11830, Val: 3227, Test: 6453
```

rồi `7 files pushed`.

> `ingest` và `validate` bị skip vì 2 stage này không tạo file output nào (`outs` trống trong `dvc.yaml`) —
> chúng chỉ đọc và in ra màn hình. Muốn xem output của chúng thì chạy tay ở Bước 2.

### Bước 1: Tạo branch làm việc

```powershell
git checkout -b session02-data-pipeline
```

### Bước 2: Chạy từng bước pipeline bằng tay

Mục đích: xem rõ từng bước làm gì trước khi để DVC tự động hóa.

**2a — Ingest (đọc dữ liệu thô)**

```powershell
python src/ingestion/ingest.py
```

Kết quả: `Loaded 21613 raw rows -> 21510 mapped rows, 7 columns` + in 5 dòng đầu.

**2b — Validate (kiểm tra chất lượng)**

```powershell
python src/validation/validate.py
```

Kết quả: 6 dòng PASS + `[Validation] All checks passed!`

**2c — Preprocess (tiền xử lý)**

```powershell
python src/preprocessing/preprocess.py
```

Kết quả: `Processed 21510 rows`, lưu `data/processed/processed.csv` và 2 file `.pkl` vào `models/`.

**2d — Split (chia dữ liệu)**

```powershell
python src/split/split.py
```

Kết quả: `[Split] Train: 11830, Val: 3227, Test: 6453`

### Bước 3: Chạy pipeline bằng DVC

**3a — Khởi tạo DVC (repo này đã làm rồi, bỏ qua)**

```powershell
dvc init
git add .dvc .dvcignore
git commit -m "chore: initialize DVC"
```

**3b — Đưa dataset vào DVC (repo này đã làm rồi, bỏ qua)**

```powershell
git rm --cached data/raw/kc_house_data.csv   # gỡ khỏi Git, giữ file trên đĩa
dvc add data/raw/kc_house_data.csv           # giao cho DVC quản
git add data/raw/kc_house_data.csv.dvc data/raw/.gitignore
git commit -m "data: track kc_house_data.csv with DVC"
```

Kiểm tra kết quả của bước này:

```powershell
git ls-files data/raw/
```

```
data/raw/.gitignore
data/raw/kc_house_data.csv.dvc     ← Git chỉ giữ file meta 100 byte
                                    ← CSV 2.4MB do DVC quản, không nằm trong Git
```

> Một file **không được** vừa nằm trong Git vừa có file `.dvc`. Nếu bị vậy, `dvc repro` sẽ báo
> `output ... is already tracked by SCM (e.g. Git)` — sửa bằng đúng 2 lệnh đầu ở trên.

**3c — Xem đồ thị pipeline**

```powershell
dvc dag
```

Kết quả: `ingest → validate` và `ingest → preprocess → split`.

**3d — Chạy toàn bộ pipeline**

```powershell
dvc repro
```

DVC đọc `dvc.yaml`, chỉ chạy các stage có thay đổi.

**3e — Kiểm tra trạng thái**

```powershell
dvc status
```

Kết quả: `Data and pipelines are up to date.`

**3f — Đổi params và xem DVC bắt thay đổi**

Baseline của nhánh `session/02`: `test_size: 0.3`, `val_size: 0.15` → **11830 / 3227 / 6453**

Sửa `configs/params.yaml`:

```yaml
data:
  test_size: 0.25
  val_size: 0.15
```

Xem DVC phát hiện thay đổi:

```powershell
dvc status
dvc params diff
```

Kết quả:

```
split:
        changed deps:
                configs/params.yaml:
                        modified:           data.test_size

Path                 Param           HEAD    workspace
configs/params.yaml  data.test_size  0.3     0.25
```

Chạy lại:

```powershell
dvc repro
```

Kết quả: 3 stage đầu skip, `split` cho ra kết quả mới. Dòng cuối là một trong hai:

| Log | Nghĩa |
|---|---|
| `Running stage 'split':` → `[Split] Train: 12905, Val: 3227, Test: 5378` | Lần đầu chạy tỷ lệ này, tính mới |
| `Stage 'split' is cached - skipping run` | Đã từng chạy tỷ lệ này, lấy lại từ run-cache |

Cả hai đều đúng và cho cùng kết quả. Kiểm tra số dòng:

```powershell
python -c "import pandas as pd; print({f: len(pd.read_csv(f'data/processed/{f}')) for f in ['train.csv','val.csv','test.csv']})"
```

```
{'train.csv': 12905, 'val.csv': 3227, 'test.csv': 5378}
```

Trả lại baseline:

```powershell
git checkout -- configs/params.yaml
dvc repro
```

Cả 2 lệnh này chạy **im lặng** (git thành công thì không in gì; `dvc repro` lấy từ cache nên không chạy
`split.py`, không có dòng `[Split] ...`). Kiểm chứng bằng:

```powershell
grep -E "test_size|val_size" configs/params.yaml
python -c "import pandas as pd; print({f: len(pd.read_csv(f'data/processed/{f}')) for f in ['train.csv','val.csv','test.csv']})"
```

```
  test_size: 0.3
  val_size: 0.15
{'train.csv': 11830, 'val.csv': 3227, 'test.csv': 6453}
```

> **Run-cache**: DVC nhớ kết quả của mọi tổ hợp (code + data + params) đã từng chạy. Đổi qua đổi lại
> giữa các tỷ lệ đã dùng sẽ lấy từ cache thay vì tính lại — quay về version cũ không tốn thời gian.

**3g — Chạy lại 1 stage**

```powershell
dvc repro preprocess
dvc repro split
```

**3h — Đẩy và kéo data với remote**

```powershell
dvc push
```

Giả lập mất file local rồi kéo lại — chạy **cả 3 lệnh**, đừng dừng giữa chừng:

```powershell
Remove-Item data\raw\kc_house_data.csv
dvc pull
dir data\raw\kc_house_data.csv
```

Kết quả: `dvc pull` báo `1 file added`, `dir` thấy lại file 2.4MB.

> Nếu chỉ chạy `Remove-Item` rồi bỏ đó, mọi lệnh `dvc repro` sau đó sẽ báo
> `missing data 'source': data/raw/kc_house_data.csv`. Chạy `dvc pull` là xong.

| Lệnh | Tác dụng |
|---|---|
| `dvc push` | Upload data từ cache local lên remote |
| `dvc pull` | Download data từ remote theo `.dvc` / `dvc.lock` đang có trên Git |

> Remote của lab là thư mục trên **máy bạn**. Người khác clone repo về máy họ sẽ không truy cập được —
> họ dùng Bước 0c để lấy data. Muốn nhiều người cùng `dvc pull` thì cần remote dùng chung (MinIO/S3), xem buổi 08.

**3i — Khôi phục version dữ liệu cũ**

Trước khi bắt đầu, working tree phải sạch:

```powershell
git status
```

Nếu còn file đang sửa dở thì commit hoặc `git stash` trước — không thì `git checkout <tag>` sẽ báo
`Your local changes to the following files would be overwritten by checkout`.

Repo có sẵn 2 tag:

| Tag | Params | train / val / test |
|---|---|---|
| `data-v1` | `test_size: 0.2`, `val_size: 0.1` | 15057 / 2151 / 4302 |
| `data-v2` | `test_size: 0.3`, `val_size: 0.15` | 11830 / 3227 / 6453 |

Về version 1:

```powershell
git checkout data-v1
dvc repro
python -c "import pandas as pd; print({f: len(pd.read_csv(f'data/processed/{f}')) for f in ['train.csv','val.csv','test.csv']})"
```

Kết quả: `{'train.csv': 15057, 'val.csv': 2151, 'test.csv': 4302}`

Quay lại nhánh làm việc:

```powershell
git checkout -- dvc.lock data/raw/kc_house_data.csv.dvc
git switch session/02
dvc repro
```

> Dùng `dvc repro` chứ không dùng `dvc pull`: file CSV thô không do Git quản nên `git checkout` không đụng
> tới nó, `dvc repro` chỉ cần sinh lại các file processed theo params của version đó. Pipeline dùng
> `random_state=42` nên kết quả tái tạo luôn giống hệt bản gốc.
>
> Phải `git checkout -- dvc.lock ...` trước khi `git switch`, vì `dvc repro` vừa ghi hash mới vào `dvc.lock`.

**Tạo version mới của riêng bạn:**

```powershell
# sửa configs/params.yaml theo ý muốn
dvc repro
dvc push
git add dvc.lock configs/params.yaml
git commit -m "data: v3 change split ratios"
git tag data-v3
```

### Bước 4: Kiểm tra kết quả

```powershell
dir data\processed\

python -c "import pandas as pd; [print(f'{f}: {len(pd.read_csv(f\"data/processed/{f}\"))} dòng') for f in ['train.csv', 'val.csv', 'test.csv']]"
```

Kết quả mong đợi trên nhánh `session/02` (`test_size=0.3`, `val_size=0.15`):

| Tập dữ liệu | Tỷ lệ | Số dòng |
| ------------ | ------ | ------- |
| train.csv    | 55%    | 11830   |
| val.csv      | 15%    | 3227    |
| test.csv     | 30%    | 6453    |

Tổng luôn bằng 21510 dòng sau khi ingest.

### Bước 5: Chạy tests

```powershell
pytest tests/test_data.py -v
```

Kết quả: `5 passed`

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `missing data 'source': data/raw/kc_house_data.csv` | Chưa có file CSV thô | `python scripts/prepare_data.py` (Bước 0c) |
| `Missing cache files` khi `dvc pull` | Remote trống hoặc chưa tạo | `mkdir ..\dvc-storage` (0b), rồi `dvc repro` + `dvc push` |
| `output ... is already tracked by SCM (e.g. Git)` | File vừa trong Git vừa có `.dvc` | `git rm --cached <file>` rồi `dvc add <file>` |
| `Your local changes ... would be overwritten by checkout: dvc.lock` | `dvc repro` vừa ghi hash mới | `git checkout -- dvc.lock` rồi checkout lại |
| `fatal: pathspec ... did not match any files` khi `git rm --cached` | File đã không còn trong Git | Không cần làm gì, đây là trạng thái đúng |
| `Data and pipelines are up to date.` khi mong đợi chạy lại | Không có gì thay đổi | Đúng như thiết kế. Muốn ép chạy lại: `dvc repro --force` |


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

Module chia dữ liệu thành 3 tập, tỷ lệ đọc từ `configs/params.yaml`:

- Lần 1: `train_test_split` với `test_size` → tách test set
- Lần 2: `train_test_split` trên phần còn lại với tỷ lệ `val_size / (1 - test_size)` → tách val set
- Lưu `train.csv`, `val.csv`, `test.csv` vào `data/processed/`
- Dùng `random_state` từ `project.random_seed` (= 42) để kết quả tái tạo được

Với `test_size=0.3`, `val_size=0.15` trên 21510 dòng: test = 6453, val = 3227, train = 11830.

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
3. **Version dữ liệu bằng DVC** — Đổi `test_size` trong `configs/params.yaml`, `dvc repro` + `dvc push`, commit và tạo tag `data-v3`. Sau đó `git checkout data-v1` + `dvc repro` để khôi phục bản cũ. Giải thích stage nào re-run và vì sao.
4. **Viết thêm test** — Bổ sung test case: kiểm tra tổng số dòng train + val + test = tổng dữ liệu sau ingest, kiểm tra không có rò rỉ dữ liệu giữa các tập.

---

## Buổi tiếp theo

**Buổi 03 — Training và Experiment Tracking với MLflow**: Huấn luyện model GradientBoostingRegressor, sử dụng MLflow để ghi lại tham số, metrics và artifacts. So sánh nhiều lần chạy thí nghiệm để chọn model tốt nhất.
