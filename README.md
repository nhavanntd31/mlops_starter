# MLOps Starter — House Price Prediction

End-to-end MLOps project: data pipeline, training, serving, monitoring.

Dataset: [House Sales in King County, USA](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction) (`data/raw/kc_house_data.csv`), mapped to `data/raw/houses.csv`.

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

## Prepare Raw Data

```bash
kaggle datasets download harlfoxem/housesalesprediction -p data/raw --unzip
python scripts/prepare_king_county.py
```

## Run Data Pipeline

```bash
python -c "from src.ingestion.ingest import ingest; from src.preprocessing.preprocess import preprocess; from src.split.split import split_data; df=ingest(); df=preprocess(df); split_data(df)"
```

## Train Model

```bash
python src/training/train.py
```

## Serve API (local)

```bash
pip install fastapi uvicorn httpx prometheus-client
uvicorn app.main:app --reload
```

## Run Full Stack (Docker Compose)

```bash
cd infra
docker compose up -d --build
```

Services:
- API: http://localhost:8000
- MLflow: http://localhost:5000
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090
- MinIO: http://localhost:9001 (minioadmin/minioadmin)

## E2E Demo (PowerShell)

```powershell
.\scripts\run_e2e_demo.ps1
```

## Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

## Project Structure

```
configs/        # params, thresholds
data/           # raw / interim / processed
src/            # data & training pipelines
app/            # FastAPI serving + Prometheus metrics
tests/          # unit & integration tests
scripts/        # utility & automation scripts
infra/          # docker-compose, prometheus, promtail
monitoring/     # grafana dashboards, alerts, drift
docs/           # architecture, model card, proposals
models/         # trained model artifacts (git-ignored)
reports/        # evaluation reports (git-ignored)
logs/           # application logs (git-ignored)
```

## Branch Map

| Branch | Session | Focus |
|---|---|---|
| session/01 | 1 | Repo structure, baseline |
| session/02 | 2 | Data pipeline, DVC |
| session/03 | 3 | Training, MLflow tracking |
| session/04 | 4 | Model registry, validation |
| session/05 | 5 | FastAPI, Docker |
| session/06 | 6 | CI/CD, quality gates |
| session/07 | 7 | Monitoring, drift |
| session/08 | 8 | Docker Compose E2E |
