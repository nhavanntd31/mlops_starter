# Kiến trúc Hệ thống MLOps — House Price Prediction

## Tổng quan

Hệ thống MLOps cho dự án dự đoán giá nhà được thiết kế theo kiến trúc modular,
bao gồm các thành phần chính: Data Pipeline, Training Pipeline, Model Registry,
Serving API và Monitoring.

## Sơ đồ kiến trúc

`
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│  Data Source  │───>│  Ingestion   │───>│   Validation     │
│ (kc_house_data.csv) │    │  (ingest.py) │    │  (validate.py)   │
└──────────────┘    └──────────────┘    └──────────────────┘
                                                │
                                                ▼
                                        ┌──────────────────┐
                                        │  Preprocessing   │
                                        │ (preprocess.py)  │
                                        └──────────────────┘
                                                │
                                                ▼
                                        ┌──────────────────┐
                                        │   Train/Val/Test │
                                        │   (split.py)     │
                                        └──────────────────┘
                                                │
                                                ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────────┐
│   MLflow     │<───│   Training   │<───│   Params/Config  │
│  Tracking    │    │  (train.py)  │    │  (params.yaml)   │
└──────────────┘    └──────────────┘    └──────────────────┘
       │                    │
       ▼                    ▼
┌──────────────┐    ┌──────────────────┐
│   Model      │───>│   Serving API    │
│  Registry    │    │   (FastAPI)      │
└──────────────┘    └──────────────────┘
                            │
                            ▼
                    ┌──────────────────┐
                    │   Monitoring     │
                    │ (Prometheus,     │
                    │  Grafana, Loki)  │
                    └──────────────────┘
`

## Các thành phần chính

### 1. Data Pipeline
- **Ingestion**: Đọc dữ liệu thô từ CSV
- **Validation**: Kiểm tra chất lượng dữ liệu (null, duplicate, range)
- **Preprocessing**: Mã hóa biến phân loại, chuẩn hóa biến số
- **Split**: Chia dữ liệu thành tập train/val/test

### 2. Training Pipeline
- Huấn luyện GradientBoostingRegressor
- Log tham số và metrics vào MLflow
- Lưu model artifact (.pkl)

### 3. Model Registry
- Quản lý phiên bản model qua MLflow
- Quy trình validate và promote model
- Model card ghi lại thông tin model

### 4. Serving API
- FastAPI cung cấp endpoint dự đoán
- Đóng gói bằng Docker
- Health check và model info endpoints

### 5. Monitoring
- Prometheus thu thập metrics (latency, request count)
- Grafana hiển thị dashboard
- Loki + Promtail thu thập logs
- Phát hiện data drift

## Công nghệ sử dụng

| Thành phần       | Công nghệ            |
| ---------------- | --------------------- |
| Ngôn ngữ         | Python 3.11           |
| ML Framework     | Scikit-learn          |
| Experiment Track | MLflow                |
| Data Versioning  | DVC                   |
| API Framework    | FastAPI               |
| Container        | Docker                |
| Monitoring       | Prometheus + Grafana  |
| Logging          | Loki + Promtail       |
| CI/CD            | GitLab CI             |
