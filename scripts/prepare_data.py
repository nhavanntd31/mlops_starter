"""Giải nén dataset seed trong Git ra data/raw/ để chạy pipeline.

Repo không track file raw bằng Git (DVC quản lý), nên máy mới clone về sẽ không có
data/raw/kc_house_data.csv. Script này lấy bản seed nén sẵn trong Git ra đúng chỗ,
để người dùng mới không cần tải lại từ Kaggle.

    python scripts/prepare_data.py
    python scripts/prepare_data.py --force    # ghi đè file đã có
"""

import argparse
import gzip
import hashlib
import shutil
from pathlib import Path

SEED_PATH = Path("data/seed/kc_house_data.csv.gz")
RAW_PATH = Path("data/raw/kc_house_data.csv")


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="Ghi đè data/raw/kc_house_data.csv nếu đã tồn tại"
    )
    args = parser.parse_args()

    if not SEED_PATH.exists():
        raise SystemExit(f"[PrepareData] Không tìm thấy seed: {SEED_PATH}")

    if RAW_PATH.exists() and not args.force:
        print(f"[PrepareData] {RAW_PATH} đã tồn tại (md5 {md5_of(RAW_PATH)}), bỏ qua.")
        print("[PrepareData] Dùng --force nếu muốn ghi đè.")
        return

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(SEED_PATH, "rb") as src, open(RAW_PATH, "wb") as dst:
        shutil.copyfileobj(src, dst)

    print(f"[PrepareData] Đã giải nén {SEED_PATH} -> {RAW_PATH}")
    print(f"[PrepareData] {RAW_PATH.stat().st_size} bytes, md5 {md5_of(RAW_PATH)}")
    print("[PrepareData] Tiếp theo: dvc repro")


if __name__ == "__main__":
    main()
