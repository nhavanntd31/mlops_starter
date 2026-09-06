# Retraining Trigger Strategy

## When to Retrain

1. **Data Drift Detected**: drift_report.json shows features_drifted > 0
2. **Model Performance Degradation**: delayed evaluation metrics drop below thresholds
3. **Scheduled**: weekly/monthly retraining cadence
4. **New Data Volume**: significant new labeled data available

## Retraining Pipeline

```
Trigger (drift alert / schedule / manual)
    |
    v
Pull latest data (DVC)
    |
    v
Run data pipeline (ingest -> validate -> preprocess -> split)
    |
    v
Train new model (src/training/train.py)
    |
    v
Validate against thresholds (scripts/validate_model.py)
    |
    v
Register in MLflow (if passed)
    |
    v
Promote to champion (scripts/promote_model.py)
    |
    v
Redeploy (restart model-api container)
```

## Rollback

If the new model underperforms in production:
1. Set alias back to previous version
2. Restart model-api container
3. Investigate root cause
