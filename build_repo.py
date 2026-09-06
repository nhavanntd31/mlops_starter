import os, shutil

def w(path, content):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def run(cmd):
    os.system(cmd)

# ===== SESSION 01 =====
shutil.copy('session01-README.md', 'README.md')
w('requirements.txt', 'pandas>=2.0\nscikit-learn>=1.3\nmlflow>=2.10\ndvc>=3.0\npyyaml>=6.0\n')
w('configs/params.yaml', 'project:\n  name: house-price-prediction\n  version: "0.1.0"\n  random_seed: 42\n\ndata:\n  raw_path: data/raw/houses.csv\n  processed_dir: data/processed\n  test_size: 0.2\n  val_size: 0.1\n')
w('docs/architecture.md', '# Ki\u1ebfn tr\u00fac h\u1ec7 th\u1ed1ng\n\nData Pipeline -> Training -> Registry -> Serving -> Monitoring -> E2E\n\nXem README.md \u0111\u1ec3 bi\u1ebft chi ti\u1ebft.\n')
for d in ['data/interim','data/processed','models','reports','logs','src/ingestion','src/validation','src/preprocessing','src/split','src/training','app','app/predictors','tests','scripts','infra','infra/ansible','monitoring','monitoring/grafana/dashboards','monitoring/prometheus']:
    os.makedirs(d, exist_ok=True)
    gk = os.path.join(d, '.gitkeep')
    if not os.path.exists(gk):
        open(gk, 'w').close()

run('git add -A')
run('git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>" -m "session/01: c\u1ea5u tr\u00fac repo, README, requirements, configs"')

# ===== SESSION 02 =====
run('git checkout -b session/02')
shutil.copy('session02-README.md', 'README.md')

w('src/ingestion/ingest.py', '''import pandas as pd
import yaml

def load_config(config_path="configs/params.yaml"):
    with open(config_path) as f:
        return yaml.safe_load(f)

def ingest(config=None):
    if config is None:
        config = load_config()
    raw_path = config["data"]["raw_path"]
    df = pd.read_csv(raw_path)
    print(f"Ingested {len(df)} rows from {raw_path}")
    return df

if __name__ == "__main__":
    df = ingest()
    print(df.head())
    print(df.dtypes)
''')

w('src/validation/validate.py', '''import pandas as pd

REQUIRED_COLUMNS = ["area", "bedrooms", "bathrooms", "age", "floors", "location", "price"]
NUMERIC_COLUMNS = ["area", "bedrooms", "bathrooms", "age", "floors", "price"]
VALID_LOCATIONS = ["downtown", "suburban", "rural", "urban", "waterfront"]
RANGES = {
    "area": (10, 1000), "bedrooms": (1, 10), "bathrooms": (1, 5),
    "age": (0, 100), "floors": (0, 5), "price": (1, 10_000_000),
}

def validate(df):
    report = {"total_rows": len(df), "errors": []}
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        report["errors"].append(f"Missing columns: {missing}")
        return report
    for col in NUMERIC_COLUMNS:
        non_numeric = pd.to_numeric(df[col], errors="coerce").isna().sum() - df[col].isna().sum()
        if non_numeric > 0:
            report["errors"].append(f"{col}: {non_numeric} non-numeric values")
    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    for col, cnt in null_counts.items():
        if cnt > 0:
            report["errors"].append(f"{col}: {cnt} null values")
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        report["errors"].append(f"{dup_count} duplicate rows")
    for col, (lo, hi) in RANGES.items():
        out = ((df[col] < lo) | (df[col] > hi)).sum()
        if out > 0:
            report["errors"].append(f"{col}: {out} values out of range [{lo}, {hi}]")
    invalid_loc = ~df["location"].isin(VALID_LOCATIONS)
    if invalid_loc.sum() > 0:
        report["errors"].append(f"location: {invalid_loc.sum()} invalid values")
    report["valid"] = len(report["errors"]) == 0
    report["valid_rows"] = len(df) - df.duplicated().sum()
    print(f"Validation: {len(report['errors'])} issues found")
    return report
''')

w('src/preprocessing/preprocess.py', '''import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
from pathlib import Path

def preprocess(df, output_dir="data/interim"):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    df = df.copy()
    df = df.drop_duplicates()
    df = df.dropna()
    le = LabelEncoder()
    df["location_encoded"] = le.fit_transform(df["location"])
    joblib.dump(le, Path(output_dir) / "label_encoder.pkl")
    feature_cols = ["area", "bedrooms", "bathrooms", "age", "floors", "location_encoded"]
    scaler = StandardScaler()
    df[feature_cols] = scaler.fit_transform(df[feature_cols])
    joblib.dump(scaler, Path(output_dir) / "scaler.pkl")
    df = df.drop(columns=["location"])
    print(f"Preprocessed: {len(df)} rows, saved encoders to {output_dir}")
    return df
''')

w('src/split/split.py', '''import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path
import yaml

def load_config(config_path="configs/params.yaml"):
    with open(config_path) as f:
        return yaml.safe_load(f)

def split_data(df, config=None):
    if config is None:
        config = load_config()
    test_size = config["data"]["test_size"]
    val_size = config["data"]["val_size"]
    seed = config["project"]["random_seed"]
    output_dir = Path(config["data"]["processed_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    train_val, test = train_test_split(df, test_size=test_size, random_state=seed)
    relative_val = val_size / (1 - test_size)
    train, val = train_test_split(train_val, test_size=relative_val, random_state=seed)
    train.to_csv(output_dir / "train.csv", index=False)
    val.to_csv(output_dir / "val.csv", index=False)
    test.to_csv(output_dir / "test.csv", index=False)
    result = {"train": len(train), "val": len(val), "test": len(test)}
    print(f"Split: train={result['train']}, val={result['val']}, test={result['test']}")
    return result
''')

w('params.yaml', 'prepare:\n  raw_path: data/raw/houses.csv\n  processed_dir: data/processed\n  test_size: 0.2\n  val_size: 0.1\n  seed: 42\n')

w('dvc.yaml', '''stages:
  prepare:
    cmd: python -c "from src.ingestion.ingest import ingest; from src.preprocessing.preprocess import preprocess; from src.split.split import split_data; df=ingest(); df=preprocess(df); split_data(df)"
    deps:
      - data/raw/houses.csv
      - src/ingestion/ingest.py
      - src/validation/validate.py
      - src/preprocessing/preprocess.py
      - src/split/split.py
      - configs/params.yaml
    params:
      - params.yaml:
          - prepare
    outs:
      - data/processed/train.csv
      - data/processed/val.csv
      - data/processed/test.csv
      - data/interim/label_encoder.pkl
      - data/interim/scaler.pkl
''')

w('tests/test_data.py', '''import pandas as pd
import pytest
from src.ingestion.ingest import ingest
from src.validation.validate import validate, REQUIRED_COLUMNS

def test_ingest_returns_dataframe():
    df = ingest()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

def test_ingest_has_required_columns():
    df = ingest()
    for col in REQUIRED_COLUMNS:
        assert col in df.columns

def test_validate_clean_data():
    df = ingest()
    report = validate(df)
    assert report["valid"] is True

def test_validate_detects_missing_column():
    df = pd.DataFrame({"area": [100], "bedrooms": [2]})
    report = validate(df)
    assert report["valid"] is False

def test_validate_detects_out_of_range():
    df = ingest()
    df.loc[0, "price"] = -100
    report = validate(df)
    assert any("price" in e for e in report["errors"])
''')

run('git add -A')
run('git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>" -m "session/02: data pipeline, DVC, validation tests"')

# ===== SESSION 03 =====
run('git checkout -b session/03')
shutil.copy('session03-README.md', 'README.md')

# Update configs/params.yaml with training section
w('configs/params.yaml', 'project:\n  name: house-price-prediction\n  version: "0.1.0"\n  random_seed: 42\n\ndata:\n  raw_path: data/raw/houses.csv\n  processed_dir: data/processed\n  test_size: 0.2\n  val_size: 0.1\n\ntraining:\n  n_estimators: 200\n  max_depth: 5\n  learning_rate: 0.1\n  subsample: 0.8\n')

w('src/training/train.py', '''import pandas as pd
import numpy as np
import yaml, json
import mlflow, mlflow.sklearn
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pathlib import Path

def load_config(config_path="configs/params.yaml"):
    with open(config_path) as f:
        return yaml.safe_load(f)

def load_data(processed_dir):
    train = pd.read_csv(f"{processed_dir}/train.csv")
    val = pd.read_csv(f"{processed_dir}/val.csv")
    test = pd.read_csv(f"{processed_dir}/test.csv")
    target = "price"
    features = [c for c in train.columns if c != target]
    return train[features], train[target], val[features], val[target], test[features], test[target], features

def evaluate(model, X, y, prefix=""):
    preds = model.predict(X)
    rmse = float(np.sqrt(mean_squared_error(y, preds)))
    mae = float(mean_absolute_error(y, preds))
    r2 = float(r2_score(y, preds))
    mape = float(np.mean(np.abs((y - preds) / np.where(y == 0, 1, y))) * 100)
    return {f"{prefix}rmse": rmse, f"{prefix}mae": mae, f"{prefix}r2": r2, f"{prefix}mape": mape}

def train(config=None):
    if config is None:
        config = load_config()
    processed_dir = config["data"]["processed_dir"]
    seed = config["project"]["random_seed"]
    tc = config.get("training", {})
    n_est = tc.get("n_estimators", 200)
    md = tc.get("max_depth", 5)
    lr = tc.get("learning_rate", 0.1)
    ss = tc.get("subsample", 0.8)
    X_tr, y_tr, X_v, y_v, X_te, y_te, feats = load_data(processed_dir)
    mlflow.set_experiment("house-price-prediction")
    with mlflow.start_run() as run:
        mlflow.log_param("model_type", "GradientBoostingRegressor")
        mlflow.log_param("n_estimators", n_est)
        mlflow.log_param("max_depth", md)
        mlflow.log_param("learning_rate", lr)
        mlflow.log_param("subsample", ss)
        mlflow.log_param("random_seed", seed)
        mlflow.log_param("n_features", len(feats))
        mlflow.log_param("n_train_samples", len(X_tr))
        mlflow.set_tag("dataset_version", config["project"]["version"])
        model = GradientBoostingRegressor(n_estimators=n_est, max_depth=md, learning_rate=lr, subsample=ss, random_state=seed)
        model.fit(X_tr, y_tr)
        tr_m = evaluate(model, X_tr, y_tr, "train_")
        v_m = evaluate(model, X_v, y_v, "val_")
        te_m = evaluate(model, X_te, y_te, "test_")
        all_m = {**tr_m, **v_m, **te_m}
        mlflow.log_metrics(all_m)
        mlflow.sklearn.log_model(model, artifact_path="model", input_example=X_tr.iloc[:1])
        Path("reports").mkdir(exist_ok=True)
        report = {"run_id": run.info.run_id, "metrics": all_m, "params": {"n_estimators": n_est, "max_depth": md, "learning_rate": lr, "subsample": ss}, "features": feats}
        with open("reports/evaluation.json", "w") as f:
            json.dump(report, f, indent=2)
        print(f"Run ID: {run.info.run_id}")
        print(f"Val RMSE: {v_m['val_rmse']:.2f}, Val R2: {v_m['val_r2']:.4f}")
        print(f"Test RMSE: {te_m['test_rmse']:.2f}, Test R2: {te_m['test_r2']:.4f}")
    return run.info.run_id

if __name__ == "__main__":
    train()
''')

w('tests/test_training.py', '''import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

def test_model_can_fit_and_predict():
    rng = np.random.RandomState(42)
    X = rng.rand(50, 3)
    y = X[:, 0] * 100 + X[:, 1] * 50 + rng.randn(50) * 5
    model = GradientBoostingRegressor(n_estimators=10, random_state=42)
    model.fit(X, y)
    preds = model.predict(X[:5])
    assert preds.shape == (5,)
    assert all(np.isfinite(preds))

def test_model_improves_over_mean():
    rng = np.random.RandomState(42)
    X = rng.rand(100, 4)
    y = X[:, 0] * 200 + X[:, 1] * 80 + rng.randn(100) * 10
    model = GradientBoostingRegressor(n_estimators=50, random_state=42)
    model.fit(X[:80], y[:80])
    preds = model.predict(X[80:])
    mse_model = np.mean((y[80:] - preds) ** 2)
    mse_mean = np.mean((y[80:] - np.mean(y[:80])) ** 2)
    assert mse_model < mse_mean
''')

run('git add -A')
run('git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>" -m "session/03: training v\u1edbi MLflow, evaluation, tests"')

# ===== SESSION 04 =====
run('git checkout -b session/04')
shutil.copy('session04-README.md', 'README.md')

w('configs/thresholds.yaml', 'tabular:\n  rmse_max: 30000\n  mae_max: 20000\n  r2_min: 0.60\n  mape_max: 25.0\n\nserving:\n  latency_p95_ms: 200\n  error_rate_max: 0.01\n')

w('scripts/validate_model.py', '''import json, yaml, sys

def load_thresholds(path="configs/thresholds.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def validate_model(report_path="reports/evaluation.json"):
    with open(report_path) as f:
        report = json.load(f)
    thresholds = load_thresholds()["tabular"]
    metrics = report["metrics"]
    checks = []
    for name, key, tkey, op in [("RMSE","test_rmse","rmse_max","<="),("MAE","test_mae","mae_max","<="),("R2","test_r2","r2_min",">="),("MAPE","test_mape","mape_max","<=")]:
        val = metrics.get(key, float("inf") if op == "<=" else -1)
        thr = thresholds[tkey]
        passed = val <= thr if op == "<=" else val >= thr
        checks.append((name, val, thr, op, passed))
    all_passed = True
    for name, value, threshold, op, passed in checks:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}: {value:.4f} {op} {threshold}")
        if not passed:
            all_passed = False
    return all_passed

if __name__ == "__main__":
    ok = validate_model()
    print(f"\\nOverall: {'PASSED' if ok else 'FAILED'}")
    sys.exit(0 if ok else 1)
''')

w('scripts/promote_model.py', '''import mlflow
from mlflow.tracking import MlflowClient
import json, sys, os

def promote(model_name=None, version=None, alias="champion", report_path="reports/evaluation.json"):
    model_name = model_name or os.getenv("MODEL_NAME", "house-price-model")
    client = MlflowClient()
    if version is None:
        with open(report_path) as f:
            report = json.load(f)
        run_id = report["run_id"]
        versions = client.search_model_versions(f"run_id='{run_id}'")
        if not versions:
            print(f"No registered version found for run {run_id}")
            sys.exit(1)
        version = versions[0].version
    client.set_registered_model_alias(model_name, alias, version)
    print(f"Promoted {model_name} v{version} -> alias '{alias}'")

if __name__ == "__main__":
    alias = sys.argv[1] if len(sys.argv) > 1 else "champion"
    promote(alias=alias)
''')

w('docs/model-card.md', '''# Model Card \u2014 D\u1ef1 \u0111o\u00e1n Gi\u00e1 Nh\u00e0

## Th\u00f4ng tin Model
- **Lo\u1ea1i**: GradientBoostingRegressor (scikit-learn)
- **B\u00e0i to\u00e1n**: H\u1ed3i quy b\u1ea3ng \u2014 d\u1ef1 \u0111o\u00e1n gi\u00e1 nh\u00e0 t\u1eeb c\u00e1c \u0111\u1eb7c tr\u01b0ng
- **\u0110\u1eb7c tr\u01b0ng**: area, bedrooms, bathrooms, age, floors, location_encoded
- **M\u1ee5c ti\u00eau**: price

## D\u1eef li\u1ec7u hu\u1ea5n luy\u1ec7n
- Ngu\u1ed3n: data/raw/houses.csv (200 d\u00f2ng)
- Chia t\u1eadp: 70% train, 10% val, 20% test
- Ti\u1ec1n x\u1eed l\u00fd: LabelEncoder + StandardScaler

## Ng\u01b0\u1ee1ng ch\u1ea5t l\u01b0\u1ee3ng
| Metric | Ng\u01b0\u1ee1ng | M\u00f4 t\u1ea3 |
|--------|--------|-------|
| RMSE | <= 30000 | Sai s\u1ed1 b\u00ecnh ph\u01b0\u01a1ng trung b\u00ecnh |
| MAE | <= 20000 | Sai s\u1ed1 tuy\u1ec7t \u0111\u1ed1i trung b\u00ecnh |
| R\u00b2 | >= 0.60 | H\u1ec7 s\u1ed1 x\u00e1c \u0111\u1ecbnh |
| MAPE | <= 25% | Sai s\u1ed1 ph\u1ea7n tr\u0103m trung b\u00ecnh |

## H\u1ea1n ch\u1ebf
- Dataset t\u1ed5ng h\u1ee3p, kh\u00f4ng \u0111\u1ea1i di\u1ec7n cho th\u1ecb tr\u01b0\u1eddng th\u1ef1c
- K\u00edch th\u01b0\u1edbc m\u1eabu nh\u1ecf (200 d\u00f2ng)
''')

run('git add -A')
run('git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>" -m "session/04: model registry, validation, governance"')

# ===== SESSION 05 =====
run('git checkout -b session/05')
shutil.copy('session05-README.md', 'README.md')

w('app/schemas.py', '''from pydantic import BaseModel

class PredictRequest(BaseModel):
    features: dict

class PredictResponse(BaseModel):
    prediction: float
    latency_ms: float
    model_version: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    features: list
''')

w('app/model_loader.py', '''import os
import mlflow.pyfunc

class ModelHolder:
    def __init__(self):
        self.model = None
        self.model_name = os.getenv("MODEL_NAME", "house-price-model")
        self.model_version = os.getenv("MODEL_VERSION", "1")
        self.features = []

    def load(self):
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        mlflow.set_tracking_uri(tracking_uri)
        model_uri = f"models:/{self.model_name}/{self.model_version}"
        self.model = mlflow.pyfunc.load_model(model_uri)
        if hasattr(self.model, "metadata") and self.model.metadata.signature:
            sig = self.model.metadata.signature
            if sig.inputs:
                self.features = [inp.name for inp in sig.inputs.inputs]
        print(f"Loaded {model_uri}")

    def predict(self, features):
        import pandas as pd
        df = pd.DataFrame([features])
        prediction = self.model.predict(df)
        return float(prediction[0])

model_holder = ModelHolder()
''')

w('app/predictors/tabular.py', '''from app.model_loader import model_holder

def predict_tabular(features):
    return model_holder.predict(features)
''')

w('app/main.py', '''import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from app.schemas import PredictRequest, PredictResponse, HealthResponse, ModelInfoResponse
from app.model_loader import model_holder
from app.predictors.tabular import predict_tabular

@asynccontextmanager
async def lifespan(app):
    try:
        model_holder.load()
    except Exception as e:
        print(f"WARNING: Model not loaded: {e}")
    yield

app = FastAPI(title="House Price Prediction API", lifespan=lifespan)

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", model_loaded=model_holder.model is not None)

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if model_holder.model is None:
        raise HTTPException(503, "Model not loaded")
    start = time.perf_counter()
    prediction = predict_tabular(req.features)
    latency = (time.perf_counter() - start) * 1000
    return PredictResponse(prediction=prediction, latency_ms=round(latency, 2), model_version=model_holder.model_version)

@app.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    return ModelInfoResponse(model_name=model_holder.model_name, model_version=model_holder.model_version, features=model_holder.features)
''')

w('Dockerfile', 'FROM python:3.11-slim\n\nWORKDIR /app\n\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt \\\\\n    && pip install --no-cache-dir fastapi uvicorn python-multipart httpx prometheus-client\n\nCOPY app/ ./app/\n\nEXPOSE 8000\n\nCMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]\n')

w('.dockerignore', '.git\n.venv\nvenv\n__pycache__\n*.pyc\ndata/\nmodels/\nreports/\nlogs/\nmlruns/\nmlartifacts/\n.dvc/cache\n.dvc/tmp\ninfra/\nmonitoring/\ndocs/\ntests/\nscripts/\n*.md\n')

w('tests/test_api.py', '''import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    with patch("app.model_loader.model_holder") as mock_holder:
        mock_holder.model = MagicMock()
        mock_holder.model_name = "house-price-model"
        mock_holder.model_version = "1"
        mock_holder.features = ["area", "bedrooms", "bathrooms", "age", "floors", "location_encoded"]
        mock_holder.predict.return_value = 150000.0
        from app.main import app
        yield TestClient(app)

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_predict(client):
    payload = {"features": {"area": 120, "bedrooms": 3, "bathrooms": 2, "age": 10, "floors": 1, "location_encoded": 0}}
    resp = client.post("/predict", json=payload)
    assert resp.status_code == 200
    assert "prediction" in resp.json()

def test_model_info(client):
    resp = client.get("/model-info")
    assert resp.status_code == 200
    assert resp.json()["model_name"] == "house-price-model"
''')

w('scripts/sample_predict.py', '''import httpx, sys

def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    print(f"Health: {httpx.get(f'{base_url}/health').json()}")
    payload = {"features": {"area": 150, "bedrooms": 3, "bathrooms": 2, "age": 5, "floors": 1, "location_encoded": 2}}
    print(f"Predict: {httpx.post(f'{base_url}/predict', json=payload).json()}")
    print(f"Model Info: {httpx.get(f'{base_url}/model-info').json()}")

if __name__ == "__main__":
    main()
''')

run('git add -A')
run('git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>" -m "session/05: FastAPI serving, Docker, tests"')

# ===== SESSION 06 =====
run('git checkout -b session/06')
shutil.copy('session06-README.md', 'README.md')

w('.gitlab-ci.yml', '''stages:
  - lint
  - test
  - validate
  - build

variables:
  PIP_CACHE_DIR: "/.cache/pip"

cache:
  paths:
    - .cache/pip

lint:
  stage: lint
  image: python:3.11
  script:
    - pip install ruff
    - ruff check app/ src/ tests/ scripts/

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install fastapi uvicorn httpx pytest
    - pytest tests/ -v --ignore=tests/test_api.py

test-api:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install fastapi uvicorn httpx pytest
    - pytest tests/test_api.py -v

validate-config:
  stage: validate
  image: python:3.11
  script:
    - pip install pyyaml
    - python scripts/validate_config.py

docker-build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker build -t model-api:ci .
    - docker run --rm model-api:ci python -c "import app.main"

workflow:
  rules:
    - if: 
    - if:  == "main"
''')

w('scripts/validate_config.py', '''import yaml, sys
from pathlib import Path

REQUIRED_SECTIONS = {
    "configs/params.yaml": ["project", "data", "training"],
    "configs/thresholds.yaml": ["tabular", "serving"],
}

def validate_config():
    errors = []
    for config_path, sections in REQUIRED_SECTIONS.items():
        path = Path(config_path)
        if not path.exists():
            errors.append(f"Missing config file: {config_path}")
            continue
        with open(path) as f:
            data = yaml.safe_load(f)
        if data is None:
            errors.append(f"Empty config file: {config_path}")
            continue
        for section in sections:
            if section not in data:
                errors.append(f"{config_path}: missing section '{section}'")
    params_path = Path("configs/params.yaml")
    if params_path.exists():
        with open(params_path) as f:
            params = yaml.safe_load(f)
        raw = params.get("data", {}).get("raw_path")
        if raw and not Path(raw).exists():
            errors.append(f"Raw data path does not exist: {raw}")
        training = params.get("training", {})
        if training.get("n_estimators", 0) < 1:
            errors.append("training.n_estimators must be >= 1")
        if not (0 < training.get("learning_rate", 0) <= 1):
            errors.append("training.learning_rate must be in (0, 1]")
    if errors:
        print("Config validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return False
    print("Config validation PASSED")
    return True

if __name__ == "__main__":
    sys.exit(0 if validate_config() else 1)
''')

run('git add -A')
run('git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>" -m "session/06: CI/CD pipeline, quality gates"')

# ===== SESSION 07 =====
run('git checkout -b session/07')
shutil.copy('session07-README.md', 'README.md')

w('app/metrics.py', '''import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"])
PREDICTION_COUNT = Counter("predictions_total", "Total predictions served", ["model_version"])
PREDICTION_LATENCY = Histogram("prediction_duration_seconds", "Model prediction latency", ["model_version"])

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        method = request.method
        path = request.url.path
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        REQUEST_COUNT.labels(method=method, endpoint=path, status=response.status_code).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)
        return response

async def metrics_endpoint(request):
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
''')

# Update app/main.py with metrics + logging
w('app/main.py', '''import time, json, logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from app.schemas import PredictRequest, PredictResponse, HealthResponse, ModelInfoResponse
from app.model_loader import model_holder
from app.predictors.tabular import predict_tabular
from app.metrics import PrometheusMiddleware, metrics_endpoint, PREDICTION_COUNT, PREDICTION_LATENCY

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logger = logging.getLogger("model-api")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(log_dir / "app.log")
handler.setFormatter(logging.Formatter(json.dumps({"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"})))
logger.addHandler(handler)

@asynccontextmanager
async def lifespan(app):
    try:
        model_holder.load()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.warning(f"Model not loaded: {e}")
    yield

app = FastAPI(title="House Price Prediction API", lifespan=lifespan)
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics_endpoint)

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", model_loaded=model_holder.model is not None)

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if model_holder.model is None:
        raise HTTPException(503, "Model not loaded")
    start = time.perf_counter()
    prediction = predict_tabular(req.features)
    latency = (time.perf_counter() - start) * 1000
    PREDICTION_COUNT.labels(model_version=model_holder.model_version).inc()
    PREDICTION_LATENCY.labels(model_version=model_holder.model_version).observe(latency / 1000)
    logger.info(json.dumps({"event": "prediction", "model_version": model_holder.model_version, "latency_ms": round(latency, 2), "prediction": prediction}))
    return PredictResponse(prediction=prediction, latency_ms=round(latency, 2), model_version=model_holder.model_version)

@app.get("/model-info", response_model=ModelInfoResponse)
def model_info():
    return ModelInfoResponse(model_name=model_holder.model_name, model_version=model_holder.model_version, features=model_holder.features)
''')

w('infra/prometheus.yml', 'global:\n  scrape_interval: 15s\n  evaluation_interval: 15s\n\nscrape_configs:\n  - job_name: "model-api"\n    static_configs:\n      - targets: ["model-api:8000"]\n')

w('infra/promtail.yml', 'server:\n  http_listen_port: 9080\n\npositions:\n  filename: /tmp/positions.yaml\n\nclients:\n  - url: http://loki:3100/loki/api/v1/push\n\nscrape_configs:\n  - job_name: model-api-logs\n    static_configs:\n      - targets:\n          - localhost\n        labels:\n          job: model-api\n          __path__: /var/log/app/*.log\n')

w('monitoring/prometheus/alerts.yml', '''groups:
  - name: model-api-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate on model-api"
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.2
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High p95 latency on model-api"
''')

w('monitoring/generate_drift_report.py', '''import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

def compute_stats(df, numeric_cols):
    stats = {}
    for col in numeric_cols:
        stats[col] = {"mean": float(df[col].mean()), "std": float(df[col].std()), "min": float(df[col].min()), "max": float(df[col].max()), "median": float(df[col].median())}
    return stats

def detect_drift(ref_stats, cur_stats, threshold=2.0):
    drift = {}
    for col in ref_stats:
        if col not in cur_stats:
            continue
        ref_mean, ref_std, cur_mean = ref_stats[col]["mean"], ref_stats[col]["std"], cur_stats[col]["mean"]
        z_score = abs(cur_mean - ref_mean) / ref_std if ref_std > 0 else 0.0
        drift[col] = {"z_score": round(z_score, 4), "drifted": z_score > threshold, "ref_mean": ref_mean, "cur_mean": cur_mean}
    return drift

def generate_report(reference_path="data/processed/train.csv", current_path=None, output_dir="monitoring/reports"):
    ref_df = pd.read_csv(reference_path)
    numeric_cols = ref_df.select_dtypes(include=[np.number]).columns.tolist()
    if "price" in numeric_cols:
        numeric_cols.remove("price")
    ref_stats = compute_stats(ref_df, numeric_cols)
    if current_path:
        cur_df = pd.read_csv(current_path)
    else:
        cur_df = ref_df.copy()
        for col in numeric_cols:
            cur_df[col] = cur_df[col] + np.random.normal(0, 0.1, len(cur_df))
    cur_stats = compute_stats(cur_df, numeric_cols)
    drift = detect_drift(ref_stats, cur_stats)
    report = {"generated_at": datetime.now().isoformat(), "reference_path": reference_path, "current_path": current_path or "simulated", "n_features": len(numeric_cols), "features_drifted": sum(1 for v in drift.values() if v["drifted"]), "details": drift}
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(Path(output_dir) / "drift_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print(f"Drift report saved. Features drifted: {report['features_drifted']}/{report['n_features']}")
    return report

if __name__ == "__main__":
    generate_report()
''')

w('docs/retraining-trigger.md', '''# Chi\u1ebfn l\u01b0\u1ee3c K\u00edch ho\u1ea1t Hu\u1ea5n luy\u1ec7n l\u1ea1i

## Khi n\u00e0o c\u1ea7n hu\u1ea5n luy\u1ec7n l\u1ea1i?
1. Ph\u00e1t hi\u1ec7n Data Drift
2. Hi\u1ec7u su\u1ea5t Model gi\u1ea3m
3. Theo l\u1ecbch (h\u00e0ng tu\u1ea7n/h\u00e0ng th\u00e1ng)
4. C\u00f3 d\u1eef li\u1ec7u m\u1edbi \u0111\u00e1ng k\u1ec3

## Pipeline
K\u00edch ho\u1ea1t -> K\u00e9o d\u1eef li\u1ec7u (DVC) -> Data pipeline -> Train -> Validate -> Register -> Promote -> Tri\u1ec3n khai l\u1ea1i

## Rollback
1. \u0110\u1eb7t alias v\u1ec1 phi\u00ean b\u1ea3n tr\u01b0\u1edbc
2. Restart container
3. \u0110i\u1ec1u tra nguy\u00ean nh\u00e2n
''')

run('git add -A')
run('git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>" -m "session/07: monitoring, metrics, drift detection"')

# ===== SESSION 08 =====
run('git checkout -b session/08')
shutil.copy('session08-README.md', 'README.md')

w('infra/docker-compose.yml', '''services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: mlflow
      POSTGRES_PASSWORD: mlflow
      POSTGRES_DB: mlflow
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mlflow"]
      interval: 10s
      retries: 5
    networks:
      - mlops-net

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio-data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      retries: 5
    networks:
      - mlops-net

  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    command: >
      mlflow server
      --backend-store-uri postgresql://mlflow:mlflow@postgres:5432/mlflow
      --default-artifact-root s3://mlflow/
      --host 0.0.0.0
      --port 5000
    environment:
      MLFLOW_S3_ENDPOINT_URL: http://minio:9000
      AWS_ACCESS_KEY_ID: minioadmin
      AWS_SECRET_ACCESS_KEY: minioadmin
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
      minio:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 15s
      retries: 5
    networks:
      - mlops-net

  model-api:
    build:
      context: ..
      dockerfile: Dockerfile
    environment:
      MLFLOW_TRACKING_URI: http://mlflow:5000
      MODEL_NAME: house-price-model
      MODEL_VERSION: "1"
    ports:
      - "8000:8000"
    volumes:
      - app-logs:/app/logs
    depends_on:
      mlflow:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      retries: 5
    networks:
      - mlops-net

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ../monitoring/prometheus/alerts.yml:/etc/prometheus/alerts.yml
    ports:
      - "9090:9090"
    depends_on:
      - model-api
    networks:
      - mlops-net

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    networks:
      - mlops-net

  promtail:
    image: grafana/promtail:latest
    volumes:
      - ./promtail.yml:/etc/promtail/config.yml
      - app-logs:/var/log/app:ro
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki
    networks:
      - mlops-net

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus
      - loki
    networks:
      - mlops-net

networks:
  mlops-net:
    driver: bridge

volumes:
  postgres-data:
  minio-data:
  grafana-data:
  app-logs:
''')

w('.env.example', 'MLFLOW_TRACKING_URI=http://localhost:5000\nMODEL_NAME=house-price-model\nMODEL_VERSION=1\n\nPOSTGRES_USER=mlflow\nPOSTGRES_PASSWORD=mlflow\nPOSTGRES_DB=mlflow\n\nMINIO_ROOT_USER=minioadmin\nMINIO_ROOT_PASSWORD=minioadmin\n\nAWS_ACCESS_KEY_ID=minioadmin\nAWS_SECRET_ACCESS_KEY=minioadmin\nMLFLOW_S3_ENDPOINT_URL=http://localhost:9000\n\nGF_SECURITY_ADMIN_PASSWORD=admin\n')

w('scripts/register_best_model.py', '''import json, mlflow, os, sys

def register_best(report_path="reports/evaluation.json", model_name=None):
    model_name = model_name or os.getenv("MODEL_NAME", "house-price-model")
    with open(report_path) as f:
        report = json.load(f)
    run_id = report["run_id"]
    result = mlflow.register_model(model_uri=f"runs:/{run_id}/model", name=model_name)
    print(f"Registered {model_name} version {result.version} from run {run_id}")
    return result

if __name__ == "__main__":
    register_best(model_name=sys.argv[1] if len(sys.argv) > 1 else None)
''')

w('scripts/run_e2e_demo.ps1', '''Write-Host "=== MLOps E2E Demo ==="
Write-Host "
[1/6] Kh\u1edfi \u0111\u1ed9ng stack..."
Set-Location -Path (Split-Path C:\Users\datth\AppData\Local\Temp)
Push-Location infra
docker compose up -d --build
Pop-Location
Write-Host "
[2/6] Ch\u1edd services..."
Start-Sleep -Seconds 30
Write-Host "
[3/6] Ch\u1ea1y data pipeline..."
python -c "from src.ingestion.ingest import ingest; from src.preprocessing.preprocess import preprocess; from src.split.split import split_data; df=ingest(); df=preprocess(df); split_data(df)"
Write-Host "
[4/6] Training model..."
python src/training/train.py
Write-Host "
[5/6] \u0110\u0103ng k\u00fd model..."
python scripts/register_best_model.py
Write-Host "
[6/6] Test API..."
Start-Sleep -Seconds 10
python scripts/sample_predict.py http://localhost:8000
Write-Host "
=== Ho\u00e0n t\u1ea5t! ==="
Write-Host "Grafana:    http://localhost:3000 (admin/admin)"
Write-Host "MLflow:     http://localhost:5000"
Write-Host "API:        http://localhost:8000/health"
Write-Host "Prometheus: http://localhost:9090"
Write-Host "MinIO:      http://localhost:9001 (minioadmin/minioadmin)"
''')

# Clean up temp README files
for i in range(1, 9):
    f = f'session0{i}-README.md'
    if os.path.exists(f):
        os.remove(f)

run('git add -A')
run('git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>" -m "session/08: Docker Compose E2E, demo script"')

# ===== MERGE TO MASTER =====
run('git checkout master')
run('git merge session/08 --no-ff -m "merge session/08 into main"')

# Session 9-10 docs
w('docs/ai-proposal.md', '''# M\u1eabu \u0110\u1ec1 xu\u1ea5t Gi\u1ea3i ph\u00e1p AI

## 1. B\u00e0i to\u00e1n kinh doanh
- C\u00f4ng ty/L\u0129nh v\u1ef1c: _____
- M\u00f4 t\u1ea3 v\u1ea5n \u0111\u1ec1: _____
- K\u1ebft qu\u1ea3 mong \u0111\u1ee3i: _____

## 2. M\u1ee9c \u0111\u1ed9 s\u1eb5n s\u00e0ng d\u1eef li\u1ec7u
| Ti\u00eau ch\u00ed | Tr\u1ea1ng th\u00e1i |
|----------|-----------|
| D\u1eef li\u1ec7u t\u1ed3n t\u1ea1i | C\u00f3/Kh\u00f4ng |
| Ch\u1ea5t l\u01b0\u1ee3ng ch\u1ea5p nh\u1eadn | C\u00f3/Kh\u00f4ng |
| \u0110\u1ee7 kh\u1ed1i l\u01b0\u1ee3ng | C\u00f3/Kh\u00f4ng |

## 3. \u0110\u00e1nh gi\u00e1 ROI
- Chi ph\u00ed ph\u00e1t tri\u1ec3n: _____
- Ti\u1ebft ki\u1ec7m k\u1ef3 v\u1ecdng: _____
- Th\u1eddi gian ho\u00e0n v\u1ed1n: _____

## 4. L\u1ed9 tr\u00ecnh tri\u1ec3n khai
| Giai \u0111o\u1ea1n | Th\u1eddi gian | S\u1ea3n ph\u1ea9m |
|-----------|-----------|----------|
| PoC | 2-4 tu\u1ea7n | Model baseline |
| MVP | 4-8 tu\u1ea7n | API + monitoring |
| Production | 4-8 tu\u1ea7n | MLOps \u0111\u1ea7y \u0111\u1ee7 |
''')

w('docs/roadmap.md', '''# L\u1ed9 tr\u00ecnh Tri\u1ec3n khai MLOps

## K\u1ebf ho\u1ea1ch 3 th\u00e1ng
| Th\u00e1ng | Tr\u1ecdng t\u00e2m |
|-------|-----------|
| 1 | D\u1eef li\u1ec7u + Training |
| 2 | Serving + CI/CD |
| 3 | Monitoring + Governance |

## S\u1ed5 \u0111\u0103ng k\u00fd R\u1ee7i ro
| R\u1ee7i ro | Kh\u1ea3 n\u0103ng | T\u00e1c \u0111\u1ed9ng | Gi\u1ea3m thi\u1ec3u |
|--------|----------|----------|-----------|
| Suy gi\u1ea3m ch\u1ea5t l\u01b0\u1ee3ng d\u1eef li\u1ec7u | Trung b\u00ecnh | Cao | Validation t\u1ef1 \u0111\u1ed9ng |
| Hi\u1ec7u su\u1ea5t model gi\u1ea3m | Trung b\u00ecnh | Cao | Quality gates, rollback |

## Ch\u1ec9 s\u1ed1 th\u00e0nh c\u00f4ng
- R\u00b2 >= 0.60
- \u0110\u1ed9 tr\u1ec5 API p95 < 200ms
- Ph\u00e1t hi\u1ec7n drift trong 24 gi\u1edd
''')

run('git add -A')
run('git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>" -m "docs: \u0111\u1ec1 xu\u1ea5t AI v\u00e0 l\u1ed9 tr\u00ecnh tri\u1ec3n khai (bu\u1ed5i 9-10)"')

run('git log --oneline --all --graph')
print('\n=== DONE ===')