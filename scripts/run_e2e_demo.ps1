Write-Host "=== MLOps E2E Demo ==="

Write-Host "`n[1/6] Starting stack..."
Set-Location -Path (Split-Path $PSScriptRoot)
Push-Location infra
docker compose up -d --build
Pop-Location

Write-Host "`n[2/6] Waiting for services..."
Start-Sleep -Seconds 30

Write-Host "`n[3/6] Running data pipeline..."
python -c "from src.ingestion.ingest import ingest; from src.preprocessing.preprocess import preprocess; from src.split.split import split_data; df=ingest(); df=preprocess(df); split_data(df)"

Write-Host "`n[4/6] Training model..."
python src/training/train.py

Write-Host "`n[5/6] Registering model..."
python scripts/register_best_model.py

Write-Host "`n[6/6] Testing API..."
Start-Sleep -Seconds 10
python scripts/sample_predict.py http://localhost:8000

Write-Host "`n=== Done! ==="
Write-Host "Grafana:    http://localhost:3000 (admin/admin)"
Write-Host "MLflow:     http://localhost:5000"
Write-Host "API:        http://localhost:8000/health"
Write-Host "Prometheus: http://localhost:9090"
Write-Host "MinIO:      http://localhost:9001 (minioadmin/minioadmin)"
