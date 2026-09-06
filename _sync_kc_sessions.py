import subprocess
import re
import pathlib

REPO = pathlib.Path(__file__).resolve().parent


def run(cmd, check=True):
    print(">", cmd)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO)
    if r.stdout.strip():
        print(r.stdout.strip()[:800])
    if r.returncode != 0 and check:
        print(r.stderr)
        raise SystemExit(r.returncode)
    return r


VALIDATE_OLD_REQUIRED = 'REQUIRED_COLUMNS = ["area", "bedrooms", "bathrooms", "age", "garage", "location", "price"]'
VALIDATE_NEW_REQUIRED = 'REQUIRED_COLUMNS = ["area", "bedrooms", "bathrooms", "age", "floors", "location", "price"]'
VALIDATE_OLD_NUM = 'NUMERIC_COLUMNS = ["area", "bedrooms", "bathrooms", "age", "garage", "price"]'
VALIDATE_NEW_NUM = 'NUMERIC_COLUMNS = ["area", "bedrooms", "bathrooms", "age", "floors", "price"]'

RANGE_OLD = '''RANGE_CHECKS = {
    "area": (10, 10000),
    "bedrooms": (0, 20),
    "bathrooms": (0, 10),
    "age": (0, 200),
    "garage": (0, 10),
    "price": (1000, 100000000),
}'''

RANGE_NEW = '''RANGE_CHECKS = {
    "area": (300, 10000),
    "bedrooms": (1, 10),
    "bathrooms": (0.5, 8),
    "age": (0, 120),
    "floors": (1, 4),
    "price": (50000, 3000000),
}'''

LOC_OLD = 'VALID_LOCATIONS = [f"District_{i}" for i in range(1, 21)]'
LOC_NEW = "VALID_LOCATIONS = None  # zipcodes from King County"

LOC_FN_OLD = '''def validate_location(df):
    invalid = df[~df["location"].isin(VALID_LOCATIONS)]
    assert invalid.empty, f"{len(invalid)} rows with invalid location"
    print("[Validation] Location check passed")'''

LOC_FN_NEW = '''def validate_location(df):
    empty = df["location"].astype(str).str.strip().eq("") | df["location"].isna()
    assert not empty.any(), f"{int(empty.sum())} rows with empty location"
    print("[Validation] Location check passed")'''

PREPROCESS_OLD = 'numeric_cols = ["area", "bedrooms", "bathrooms", "age", "garage"]'
PREPROCESS_NEW = 'numeric_cols = ["area", "bedrooms", "bathrooms", "age", "floors"]'

DVC_MAP = '''stages:
  map_raw:
    cmd: python scripts/prepare_king_county.py
    deps:
      - data/raw/kc_house_data.csv
      - scripts/prepare_king_county.py
    outs:
      - data/raw/houses.csv
'''

branches = [f"session/0{i}" for i in range(2, 9)]

for b in branches:
    print("====", b, "====")
    run(f"git checkout {b}")
    run("git checkout master -- data/raw/houses.csv data/raw/kc_house_data.csv scripts/prepare_king_county.py")

    vp = REPO / "src/validation/validate.py"
    if vp.exists():
        t = vp.read_text(encoding="utf-8")
        t = t.replace(VALIDATE_OLD_REQUIRED, VALIDATE_NEW_REQUIRED)
        t = t.replace(VALIDATE_OLD_NUM, VALIDATE_NEW_NUM)
        t = t.replace(RANGE_OLD, RANGE_NEW)
        t = t.replace('"garage": (0, 10),', '"floors": (1, 4),')
        t = t.replace('"garage": (0, 5),', '"floors": (1, 4),')
        if LOC_OLD in t:
            t = t.replace(LOC_OLD, LOC_NEW)
        if LOC_FN_OLD in t:
            t = t.replace(LOC_FN_OLD, LOC_FN_NEW)
        else:
            t = re.sub(
                r'def validate_location\(df\):.*?print\("\[Validation\] Location check passed"\)',
                LOC_FN_NEW,
                t,
                count=1,
                flags=re.S,
            )
        vp.write_text(t, encoding="utf-8")
        print("  patched validate.py")

    pp = REPO / "src/preprocessing/preprocess.py"
    if pp.exists():
        t = pp.read_text(encoding="utf-8")
        t = t.replace(PREPROCESS_OLD, PREPROCESS_NEW)
        t = t.replace('"garage"', '"floors"')
        pp.write_text(t, encoding="utf-8")
        print("  patched preprocess.py")

    ip = REPO / "src/ingestion/ingest.py"
    if ip.exists():
        t = ip.read_text(encoding="utf-8")
        if 'dtype={"location": str}' not in t:
            t = t.replace("pd.read_csv(raw_path)", 'pd.read_csv(raw_path, dtype={"location": str})')
            if 'if "location" in df.columns:' not in t:
                t = t.replace(
                    'print(f"[Ingestion] Loaded {len(df)} rows, {len(df.columns)} columns")',
                    'if "location" in df.columns:\n        df["location"] = df["location"].astype(str)\n    print(f"[Ingestion] Loaded {len(df)} rows, {len(df.columns)} columns")',
                )
            ip.write_text(t, encoding="utf-8")
            print("  patched ingest.py")

    dp = REPO / "dvc.yaml"
    if dp.exists():
        t = dp.read_text(encoding="utf-8")
        if "map_raw:" not in t:
            if t.startswith("stages:"):
                t = t.replace("stages:\n", DVC_MAP, 1)
            else:
                t = DVC_MAP + t
            dp.write_text(t, encoding="utf-8")
            print("  patched dvc.yaml")

    if b in [f"session/0{i}" for i in range(4, 9)]:
        tp = REPO / "configs/thresholds.yaml"
        if tp.exists():
            t = tp.read_text(encoding="utf-8")
            t = t.replace("max_rmse: 50000", "max_rmse: 250000")
            t = t.replace("max_mae: 35000", "max_mae: 150000")
            t = t.replace("rmse_max: 30000", "rmse_max: 250000")
            t = t.replace("mae_max: 20000", "mae_max: 150000")
            tp.write_text(t, encoding="utf-8")
            print("  patched thresholds.yaml")

    if b in [f"session/0{i}" for i in range(5, 9)]:
        patches = {
            "scripts/sample_predict.py": [
                ('"garage": 1', '"floors": 1.0'),
                ("garage=1", "floors=1.0"),
                ('"location": "District_1"', '"location": "98178"'),
                ('location="District_1"', 'location="98178"'),
                ('"area": 150.0', '"area": 2000.0'),
            ],
            "tests/test_api.py": [
                ("garage=1", "floors=1.0"),
                ('location="District_1"', 'location="98178"'),
                ("area=120", "area=2000"),
            ],
            "app/schemas.py": [
                ("garage: int = Field(..., ge=0)", "floors: float = Field(..., gt=0)"),
                (
                    'location: str = Field(..., description="District name")',
                    'location: str = Field(..., description="Zipcode")',
                ),
                ('description="Area in sqm"', 'description="Living area in sqft"'),
                ("bathrooms: int = Field(..., ge=0)", "bathrooms: float = Field(..., ge=0)"),
            ],
            "docs/model-card.md": [
                ("garage", "floors"),
                ("File houses.csv (1000 bản ghi)", "King County house sales (~21510 bản ghi)"),
                ("dữ liệu mô phỏng", "dữ liệu King County (Kaggle)"),
                ("District_1 đến District_20", "các zipcode King County"),
                ("RMSE | <= 50000", "RMSE | <= 250000"),
                ("MAE | <= 35000", "MAE | <= 150000"),
                ("Số chỗ đỗ xe", "Số tầng"),
                ("Diện tích (m²)", "Diện tích (sqft)"),
            ],
        }
        for rel, reps in patches.items():
            p = REPO / rel
            if not p.exists():
                continue
            t = p.read_text(encoding="utf-8")
            for a, b_ in reps:
                t = t.replace(a, b_)
            p.write_text(t, encoding="utf-8")
            print(f"  patched {rel}")

    run("git add -A")
    r = run("git status --porcelain", check=False)
    if not r.stdout.strip():
        print("  nothing to commit")
        continue
    run('git commit -m "data: switch training data to King County house sales"')

run("git checkout master")
print("DONE")
