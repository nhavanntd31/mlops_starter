import subprocess
import pathlib

REPO = pathlib.Path(__file__).resolve().parent


def run(cmd, check=True):
    print(">", cmd)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=REPO)
    if r.stdout.strip():
        print(r.stdout.strip()[:500])
    if r.returncode != 0 and check:
        print(r.stderr)
        raise SystemExit(r.returncode)
    return r


REPLACEMENTS = [
    ('features=["area", "bedrooms", "bathrooms", "age", "garage", "location"]',
     'features=["area", "bedrooms", "bathrooms", "age", "floors", "location"]'),
    ("garage=request.garage,", "floors=request.floors,"),
    ("def predict_price(area, bedrooms, bathrooms, age, garage, location):",
     "def predict_price(area, bedrooms, bathrooms, age, floors, location):"),
    ("numeric_features = np.array([[area, bedrooms, bathrooms, age, garage]])",
     "numeric_features = np.array([[area, bedrooms, bathrooms, age, floors]])"),
    ("    - garage", "    - floors"),
    ('"garage"', '"floors"'),
    ("'garage'", "'floors'"),
    ("garage", "floors"),
]

# Only touch runtime/config files; avoid rewriting long READMEs wholesale via blind garage->floors
TARGETS = [
    "app/main.py",
    "app/predictors/tabular.py",
    "configs/params.yaml",
    "docs/model-card.md",
    "build_repo.py",
]

for b in [f"session/0{i}" for i in range(2, 9)]:
    print("====", b, "====")
    run(f"git checkout {b}")
    changed = False
    for rel in TARGETS:
        p = REPO / rel
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        orig = t
        # ordered specific then generic for code files
        if rel.endswith(".py") or rel.endswith(".yaml") or rel == "docs/model-card.md":
            for a, b_ in REPLACEMENTS:
                t = t.replace(a, b_)
        if t != orig:
            p.write_text(t, encoding="utf-8")
            print("  patched", rel)
            changed = True
    if not changed:
        print("  nothing")
        continue
    run("git add -A")
    r = run("git status --porcelain", check=False)
    if r.stdout.strip():
        run('git commit -m "fix: rename garage feature to floors for King County"')

run("git checkout master")
print("DONE")
