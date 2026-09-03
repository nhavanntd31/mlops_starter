# Script demo End-to-End cho du an House Price Prediction
# Chay toan bo pipeline tu data den prediction

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " DEMO END-TO-END: House Price Prediction" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "[Buoc 1] Kiem tra du lieu tho..." -ForegroundColor Yellow
python -c "import pandas as pd; df = pd.read_csv('data/raw/houses.csv'); print(f'  Du lieu: {len(df)} dong, {len(df.columns)} cot')"

Write-Host ""
Write-Host "[Buoc 2] Chay validation du lieu..." -ForegroundColor Yellow
python src/validation/validate.py

Write-Host ""
Write-Host "[Buoc 3] Tien xu ly du lieu..." -ForegroundColor Yellow
python src/preprocessing/preprocess.py

Write-Host ""
Write-Host "[Buoc 4] Chia du lieu train/val/test..." -ForegroundColor Yellow
python src/split/split.py

Write-Host ""
Write-Host "[Buoc 5] Huan luyen model..." -ForegroundColor Yellow
python src/training/train.py

Write-Host ""
Write-Host "[Buoc 6] Validate model..." -ForegroundColor Yellow
python scripts/validate_model.py

Write-Host ""
Write-Host "[Buoc 7] Dang ky model..." -ForegroundColor Yellow
python scripts/register_best_model.py

Write-Host ""
Write-Host "[Buoc 8] Kiem tra drift..." -ForegroundColor Yellow
python monitoring/generate_drift_report.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " DEMO HOAN TAT!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Cac buoc tiep theo:" -ForegroundColor Cyan
Write-Host "  1. Khoi dong stack: docker compose -f infra/docker-compose.yml up -d"
Write-Host "  2. Mo MLflow UI: http://localhost:5000"
Write-Host "  3. Mo API docs: http://localhost:8000/docs"
Write-Host "  4. Mo Grafana: http://localhost:3000"
Write-Host "  5. Thu predict: python scripts/sample_predict.py"
