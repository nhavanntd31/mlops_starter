import subprocess
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent


def run(cmd, check=True):
    print(">", cmd)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO)
    if r.stdout.strip():
        print(r.stdout.strip()[:400])
    if r.returncode != 0 and check:
        print(r.stderr)
        raise SystemExit(r.returncode)
    return r


REPLACEMENTS = [
    ("| garage     | int            | Số chỗ đỗ xe                                 | 1                |",
     "| floors     | float          | Số tầng                                      | 1.0              |"),
    ("| location   | str            | Vị trí (quận/huyện)                          | District_1       |",
     "| location   | str            | Zipcode (King County)                        | 98178            |"),
    ("| area       | float          | Diện tích nhà (m²)                           | 120.5            |",
     "| area       | float          | Diện tích sống (sqft)                        | 2000             |"),
    ("| bathrooms  | int            | Số phòng tắm                                 | 2                |",
     "| bathrooms  | float          | Số phòng tắm                                 | 2.25             |"),
    ("| price      | float          | Giá nhà (đơn vị tiền tệ) — biến mục tiêu    | 350000.0         |",
     "| price      | float          | Giá nhà (USD) — biến mục tiêu                | 450000.0         |"),
    ("- Dữ liệu: file houses.csv (1000 bản ghi)",
     "- Dữ liệu: King County house sales → houses.csv (~21510 bản ghi)"),
    ("- **Số lượng:** 1000 bản ghi",
     "- **Số lượng:** ~21510 bản ghi (King County)"),
    ("- **Nguồn**: File houses.csv (1000 bản ghi)",
     "- **Nguồn**: King County house sales → houses.csv (~21510 bản ghi)"),
    ("- **Nguồn:** data/raw/houses.csv",
     "- **Nguồn:** Kaggle King County (`kc_house_data.csv` → `houses.csv`)"),
    ("Kết quả mong đợi (với 1000 bản ghi):",
     "Kết quả mong đợi (với ~21510 bản ghi King County):"),
    ("| train.csv    | 70%    | ~700             |",
     "| train.csv    | 70%    | ~15057           |"),
    ("| val.csv      | 10%    | ~100             |",
     "| val.csv      | 10%    | ~2151            |"),
    ("| test.csv     | 20%    | ~200             |",
     "| test.csv     | 20%    | ~4302            |"),
    ("`area`, `bedrooms`, `bathrooms`, `age`, `garage`, `price`",
     "`area`, `bedrooms`, `bathrooms`, `age`, `floors`, `price`"),
    ("bathrooms, age, garage, location.",
     "bathrooms, age, floors, location."),
    ("    - garage",
     "    - floors"),
    ("- garage",
     "- floors"),
    ("RMSE < 30.000",
     "RMSE < 250.000"),
    ("RMSE | <= 50000",
     "RMSE | <= 250000"),
    ("MAE | <= 35000",
     "MAE | <= 150000"),
    ("| R² | >= 0.60 | Hệ số xác định |\n| RMSE | <= 50000 | Sai số bình phương trung bình |\n| MAE | <= 35000 | Sai số tuyệt đối trung bình |",
     "| R² | >= 0.60 | Hệ số xác định |\n| RMSE | <= 250000 | Sai số bình phương trung bình (USD) |\n| MAE | <= 150000 | Sai số tuyệt đối trung bình (USD) |"),
    ("Model chỉ được huấn luyện trên dữ liệu mô phỏng, không phản ánh thị trường thực",
     "Model dùng dữ liệu King County 2014–2015 (Kaggle), không phản ánh thị trường hiện tại"),
    ("Không xử lý được các vị trí ngoài danh sách District_1 đến District_20",
     "Không xử lý tốt zipcode ngoài phân phối huấn luyện"),
    ("các vị trí ngoài danh sách District_1 đến District_20",
     "zipcode ngoài phân phối huấn luyện"),
    ("District_1 đến District_20",
     "các zipcode King County"),
    ("District_1",
     "98178"),
    ("số chỗ đỗ xe và vị trí",
     "số tầng và zipcode"),
    ("Số chỗ đỗ xe",
     "Số tầng"),
    ("Diện tích (m²)",
     "Diện tích (sqft)"),
    ("| floors | int | Số chỗ đỗ xe |",
     "| floors | float | Số tầng |"),
    ("| floors | int | Số tầng |",
     "| floors | float | Số tầng |"),
    ("Vị trí hợp lệ** — Cột `location` chỉ chứa các giá trị trong danh sách cho phép",
     "Vị trí hợp lệ** — Cột `location` (zipcode) không được rỗng"),
    ("`area` ∈ (0, 10000], `bedrooms` ∈ [0, 20], `price` > 0",
     "`area` ∈ [300, 10000], `bedrooms` ∈ [1, 10], `floors` ∈ [1, 4], `price` ∈ [50000, 3000000]"),
    ("dữ liệu mô phỏng",
     "dữ liệu King County (Kaggle)"),
    ("`garage`",
     "`floors`"),
    (" garage",
     " floors"),
]

DATASET_BLURB = (
    "\n\n> **Dataset:** [House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) "
    "(`data/raw/kc_house_data.csv`), đã map sang `data/raw/houses.csv` "
    "(~21510 rows; `sqft_living→area`, `yr_built→age`, `zipcode→location`, `floors`).\n"
    "> Chuẩn bị lại: `python scripts/prepare_king_county.py`\n"
)


def patch_text(text: str) -> str:
    for a, b in REPLACEMENTS:
        text = text.replace(a, b)
    # leftover bare garage token in md tables/lists
    text = re.sub(r"\bgarage\b", "floors", text)
    return text


def maybe_insert_dataset_blurb(text: str, path: str) -> str:
    name = pathlib.Path(path).name
    if name not in {"README.md"} and not name.startswith("session"):
        return text
    if "King County" in text[:800] or "kc_house_data" in text[:1200]:
        return text
    # insert after first H1
    m = re.search(r"^# .+$", text, flags=re.M)
    if not m:
        return text
    end = m.end()
    return text[:end] + DATASET_BLURB + text[end:]


branches = ["session/01", "session/02", "session/03", "session/04",
            "session/05", "session/06", "session/07", "session/08"]

for b in branches:
    print("====", b, "====")
    run(f"git checkout {b}")
    md_files = list(REPO.glob("*.md")) + list(REPO.glob("docs/*.md"))
    # also sessionXX-README.md in root
    md_files = sorted({p.resolve() for p in md_files if p.is_file()})
    changed_any = False
    for p in md_files:
        rel = str(p.relative_to(REPO)).replace("\\", "/")
        if rel.startswith(".") or "_update" in rel:
            continue
        orig = p.read_text(encoding="utf-8")
        text = patch_text(orig)
        text = maybe_insert_dataset_blurb(text, rel)
        if text != orig:
            p.write_text(text, encoding="utf-8")
            print("  patched", rel)
            changed_any = True
    if not changed_any:
        print("  no md changes")
        continue
    run("git add -A")
    r = run("git status --porcelain", check=False)
    if r.stdout.strip():
        run('git commit -m "docs: update session READMEs for King County dataset"')

run("git checkout master")
print("DONE")
