# Architecture

## Overview

```
data/raw/kc_house_data.csv (Kaggle King County)
    |
    v
data/raw/houses.csv (mapped features)
    |
    v
[Data Pipeline] -- src/ingestion, validation, preprocessing, split
    |
    v
data/processed/
    |
    v
[Training] -- src/training/train.py + MLflow tracking
    |
    v
[Model Registry] -- MLflow registry, validate, promote
    |
    v
[Serving] -- app/ FastAPI + Docker
    |
    v
[Monitoring] -- Prometheus, Loki, Grafana
    |
    v
[E2E Stack] -- infra/docker-compose.yml
```

## Components

- **Data Pipeline**: Ingest CSV, validate schema/ranges, preprocess (encode, scale), split train/val/test
- **Training**: GradientBoostingRegressor, log params/metrics/artifacts to MLflow
- **Registry**: Version models, automated validation against thresholds, promote/rollback
- **Serving**: FastAPI endpoints /health, /predict, /model-info; Docker image
- **CI/CD**: GitLab CI lint, test, validate config, build image
- **Monitoring**: Prometheus metrics, Loki logs, Grafana dashboards, drift detection
- **E2E**: Docker Compose orchestrates all services
