# Lộ trình Triển khai MLOps

## Tổng quan

Lộ trình triển khai MLOps cho doanh nghiệp, từ mức cơ bản đến nâng cao,
phù hợp cho các team bắt đầu áp dụng MLOps.

## Giai đoạn 1: Nền tảng (Tuần 1-2)

### Mục tiêu
- Thiết lập repository chuẩn
- Cấu hình môi trường phát triển
- Xây dựng data pipeline cơ bản

### Công việc
- [x] Tạo cấu trúc thư mục dự án
- [x] Viết requirements.txt và configs
- [x] Xây dựng pipeline: ingestion → validation → preprocessing → split
- [x] Thiết lập DVC cho quản lý dữ liệu
- [x] Viết unit tests cho data pipeline

### Sản phẩm
- Repository với cấu trúc chuẩn
- Data pipeline hoạt động end-to-end
- Test coverage cho data pipeline

## Giai đoạn 2: Training & Tracking (Tuần 3)

### Mục tiêu
- Huấn luyện model với theo dõi thí nghiệm
- Thiết lập MLflow tracking
- Đánh giá và so sánh model

### Công việc
- [x] Xây dựng training pipeline
- [x] Tích hợp MLflow logging
- [x] Tạo evaluation reports
- [x] Viết unit tests cho training

### Sản phẩm
- Training pipeline với MLflow tracking
- Model artifacts và evaluation metrics
- Model registry cơ bản

## Giai đoạn 3: Model Governance (Tuần 4)

### Mục tiêu
- Quy trình validate và promote model
- Tài liệu hóa model (model card)
- Tiêu chí chấp nhận model

### Công việc
- [x] Định nghĩa thresholds cho model validation
- [x] Script validate_model.py
- [x] Script promote_model.py
- [x] Viết model card

### Sản phẩm
- Quy trình governance tự động
- Model card documentation
- Validation thresholds

## Giai đoạn 4: Serving (Tuần 5)

### Mục tiêu
- API phục vụ dự đoán
- Đóng gói Docker
- Testing API

### Công việc
- [x] Xây dựng FastAPI application
- [x] Tạo Dockerfile
- [x] Viết API tests
- [x] Script sample prediction

### Sản phẩm
- REST API hoạt động
- Docker image
- API documentation (Swagger)

## Giai đoạn 5: CI/CD (Tuần 6)

### Mục tiêu
- Pipeline CI/CD tự động
- Quality gates
- Automated testing

### Công việc
- [x] Cấu hình GitLab CI
- [x] Lint, test, validate stages
- [x] Config validation script
- [x] Build và deploy stages

### Sản phẩm
- CI/CD pipeline hoạt động
- Quality gates tự động
- Automated deployment

## Giai đoạn 6: Monitoring (Tuần 7)

### Mục tiêu
- Giám sát hiệu năng API
- Phát hiện data drift
- Cảnh báo tự động

### Công việc
- [x] Prometheus metrics middleware
- [x] Alert rules
- [x] Drift detection script
- [x] Quy trình retraining trigger

### Sản phẩm
- Monitoring stack (Prometheus + Grafana)
- Drift detection reports
- Alert configuration

## Giai đoạn 7: Production (Tuần 8)

### Mục tiêu
- Triển khai full stack
- Demo end-to-end
- Documentation hoàn chỉnh

### Công việc
- [x] Docker Compose cho toàn bộ stack
- [x] E2E demo script
- [x] Model registry script
- [x] Documentation cuối cùng

### Sản phẩm
- Production-ready stack
- E2E demo
- Tài liệu đầy đủ

## Các bước tiếp theo

### Ngắn hạn
- Kubernetes deployment (Helm charts)
- A/B testing framework
- Feature store

### Trung hạn
- Automated retraining pipeline
- Multi-model serving
- Advanced monitoring (model performance tracking)

### Dài hạn
- ML Platform tự phục vụ
- AutoML integration
- Federated learning (nếu cần)
