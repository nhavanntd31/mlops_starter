# Buổi 06 — CI/CD và Quality Gate

> **Dataset:** [House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) (`data/raw/kc_house_data.csv`), raw `data/raw/kc_house_data.csv` (~21510 rows; `sqft_living→area`, `yr_built→age`, `zipcode→location`, `floors`).
> Chuẩn bị lại: `# column mapping in src/ingestion/ingest.py`


## Mục tiêu buổi học

- Hiểu CI/CD/CT trong MLOps
- Xây dựng GitLab CI pipeline: lint, test, validate config, build Docker image
- Thiết lập quality gates tự động
- Viết script validate config

---

## Kiến thức lý thuyết

### CI / CD / CT trong MLOps

| Khái niệm | Giải thích | Ví dụ |
|------------|------------|-------|
| **CI** (Continuous Integration) | Mỗi commit tự động trigger lint + test | Push code → GitLab chạy `ruff check` + `pytest` |
| **CD** (Continuous Delivery) | Tự động build Docker image, deploy lên staging | Merge vào `main` → build image → deploy staging |
| **CT** (Continuous Training) | Tự động retrain khi dữ liệu thay đổi hoặc phát hiện drift | Data mới → trigger pipeline train → đánh giá → register model |

### Quality Gate

Quality Gate là tập hợp các điều kiện **bắt buộc phải đạt** trước khi code được merge hoặc deploy:

| Gate | Mô tả | Công cụ |
|------|--------|---------|
| Lint pass | Code tuân thủ coding style | `ruff` |
| Tests pass | Tất cả unit/integration tests đều pass | `pytest` |
| Config valid | File cấu hình đúng format, giá trị hợp lệ | `validate_config.py` |
| Docker build OK | Image build thành công, app import được | `docker build` + smoke test |

### GitLab CI — Các khái niệm chính

| Khái niệm | Giải thích |
|------------|------------|
| `.gitlab-ci.yml` | File cấu hình pipeline, đặt ở thư mục gốc |
| **Stages** | Các giai đoạn chạy tuần tự: lint → test → validate → build |
| **Jobs** | Các tác vụ trong mỗi stage, chạy song song nếu cùng stage |
| **image** | Docker image dùng để chạy job (ví dụ: `python:3.11-slim`) |
| **script** | Danh sách lệnh thực thi trong job |
| **artifacts** | File kết quả lưu lại sau khi job chạy xong |
| **rules** | Điều kiện để job được kích hoạt (ví dụ: chỉ chạy khi có MR) |

---

## Cấu trúc file mới thêm

```
session-06-ci-cd/
├── .gitlab-ci.yml            # Pipeline CI/CD với 4 stages
└── scripts/
    └── validate_config.py    # Script kiểm tra file cấu hình
```

---

## Hướng dẫn thực hành

### Bước 1: Checkout branch

```bash
git checkout session-06-ci-cd
```

### Bước 2: Đọc `.gitlab-ci.yml`

Mở file và hiểu cấu trúc 4 stages:

```
stages:
  - lint        # Kiểm tra coding style
  - test        # Chạy unit tests
  - validate    # Kiểm tra cấu hình
  - build       # Build Docker image
```

### Bước 3: Chạy lint local

```bash
pip install ruff
ruff check app/ src/ tests/ scripts/
```

Nếu có lỗi, sửa theo gợi ý hoặc chạy tự động:
```bash
ruff check --fix app/ src/ tests/ scripts/
```

### Bước 4: Chạy tests local

```bash
pytest tests/ -v --ignore=tests/test_api.py
```

> **Lưu ý:** Bỏ qua `test_api.py` vì cần API server đang chạy.

### Bước 5: Chạy validate config

```bash
python scripts/validate_config.py
```

Kết quả mong đợi nếu tất cả hợp lệ:
```
[OK] configs/params.yaml — tất cả sections hợp lệ
[OK] configs/thresholds.yaml — tất cả sections hợp lệ
[OK] Đường dẫn dữ liệu raw tồn tại
[OK] Tất cả tham số training hợp lệ
✅ Tất cả kiểm tra đều PASS
```

### Bước 6: Build Docker image local

```bash
docker build -t model-api:ci .
```

Smoke test — kiểm tra app import được:
```bash
docker run --rm model-api:ci python -c "import app.main"
```

### Bước 7: Push lên GitLab (nếu có)

```bash
git add .
git commit -m "feat: thêm CI/CD pipeline"
git push origin session-06-ci-cd
```

Sau khi push, mở GitLab → **CI/CD → Pipelines** để xem pipeline chạy.

---

## Chi tiết code

### `.gitlab-ci.yml`

```yaml
stages:
  - lint
  - test
  - validate
  - build

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/

lint:
  stage: lint
  image: python:3.11-slim
  script:
    - pip install ruff
    - ruff check app/ src/ tests/ scripts/
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

test:
  stage: test
  image: python:3.11-slim
  script:
    - pip install -r requirements.txt
    - pip install pytest
    - pytest tests/ -v --ignore=tests/test_api.py
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

validate-config:
  stage: validate
  image: python:3.11-slim
  script:
    - pip install pyyaml
    - python scripts/validate_config.py
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

docker-build:
  stage: build
  image: docker:24.0
  services:
    - docker:24.0-dind
  script:
    - docker build -t model-api:ci .
    - docker run --rm model-api:ci python -c "import app.main"
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'
```

**Giải thích:**
- **lint**: Dùng `ruff` kiểm tra coding style cho tất cả thư mục code
- **test**: Cài dependencies, chạy `pytest` (bỏ qua integration test)
- **validate-config**: Chạy script kiểm tra file cấu hình
- **docker-build**: Build image và chạy smoke test kiểm tra import thành công
- **rules**: Pipeline chỉ chạy khi có Merge Request hoặc push vào `main`

### `scripts/validate_config.py`

```python
import yaml
import sys
from pathlib import Path

def load_yaml(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)

def validate_params(config: dict):
    required_sections = ["project", "data", "training"]
    for section in required_sections:
        assert section in config, f"Thiếu section '{section}' trong params.yaml"

    training = config["training"]
    assert training.get("n_estimators", 0) >= 1, \
        f"n_estimators phải >= 1, nhận được {training.get('n_estimators')}"
    lr = training.get("learning_rate", 0)
    assert 0 < lr <= 1, \
        f"learning_rate phải trong khoảng (0, 1], nhận được {lr}"

def validate_thresholds(config: dict):
    required_sections = ["tabular", "serving"]
    for section in required_sections:
        assert section in config, f"Thiếu section '{section}' trong thresholds.yaml"

def validate_data_path(config: dict):
    raw_path = config.get("data", {}).get("raw_path", "")
    assert Path(raw_path).exists(), \
        f"Đường dẫn dữ liệu raw không tồn tại: {raw_path}"

def main():
    errors = []

    try:
        params = load_yaml("configs/params.yaml")
        validate_params(params)
        print("[OK] configs/params.yaml — tất cả sections hợp lệ")
    except Exception as e:
        errors.append(f"[FAIL] params.yaml: {e}")

    try:
        thresholds = load_yaml("configs/thresholds.yaml")
        validate_thresholds(thresholds)
        print("[OK] configs/thresholds.yaml — tất cả sections hợp lệ")
    except Exception as e:
        errors.append(f"[FAIL] thresholds.yaml: {e}")

    try:
        validate_data_path(params)
        print("[OK] Đường dẫn dữ liệu raw tồn tại")
    except Exception as e:
        errors.append(f"[FAIL] data path: {e}")

    print("[OK] Tất cả tham số training hợp lệ")

    if errors:
        print("\n❌ Có lỗi:")
        for err in errors:
            print(f"  {err}")
        sys.exit(1)
    else:
        print("\n✅ Tất cả kiểm tra đều PASS")

if __name__ == "__main__":
    main()
```

**Kiểm tra bao gồm:**
- `configs/params.yaml` có đủ sections: `project`, `data`, `training`
- `configs/thresholds.yaml` có đủ sections: `tabular`, `serving`
- Đường dẫn raw data tồn tại trên hệ thống
- `n_estimators >= 1`
- `0 < learning_rate <= 1`

---

## Bài tập sau buổi học

1. **Thêm stage `security-scan`** — thêm một job mới dùng `pip-audit` hoặc `safety` để quét lỗ hổng bảo mật trong dependencies. Đặt ở stage riêng giữa `test` và `validate`.

2. **Thêm kiểm tra thresholds chi tiết** — trong `validate_config.py`, kiểm tra thêm: `min_r2_score` phải nằm trong khoảng `[0, 1]`, `max_latency_ms` phải dương.

3. **Cấu hình artifacts** — chỉnh `.gitlab-ci.yml` để lưu kết quả test dưới dạng JUnit XML (`pytest --junitxml=report.xml`), sau đó dùng `artifacts:reports:junit` để GitLab hiển thị kết quả test trên giao diện MR.

4. **Viết script `pre-commit` hook** — tạo script chạy `ruff check` và `validate_config.py` tự động mỗi khi developer commit. Đặt trong `.githooks/pre-commit`.

---

## Buổi tiếp theo

**Buổi 07 — Monitoring, Metrics và Drift Detection**: Tích hợp Prometheus metrics vào FastAPI, thu thập logs với Loki + Promtail, viết script phát hiện data drift, và thiết lập alert rules.
