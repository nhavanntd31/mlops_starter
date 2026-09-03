# Quy trình Kích hoạt Huấn luyện lại Model

## Tổng quan

Tài liệu này mô tả quy trình tự động phát hiện khi model cần được huấn luyện lại
và các bước thực hiện.

## Điều kiện kích hoạt

### 1. Data Drift
- PSI (Population Stability Index) > 0.2 cho bất kỳ đặc trưng nào
- Phát hiện qua báo cáo drift tự động chạy hàng ngày

### 2. Hiệu năng giảm
- R² giảm dưới ngưỡng 0.60
- RMSE tăng trên ngưỡng 50,000
- Phát hiện qua monitoring metrics

### 3. Dữ liệu mới
- Có thêm >= 20% dữ liệu mới so với tập huấn luyện gốc
- Scheduled retraining hàng tuần/tháng

## Quy trình thực hiện

`
Phát hiện trigger
       │
       ▼
Tạo báo cáo drift
       │
       ▼
Validate dữ liệu mới
       │
       ▼
Chạy pipeline DVC
       │
       ▼
Huấn luyện model mới
       │
       ▼
Validate model (thresholds)
       │
       ▼
So sánh với model hiện tại
       │
       ├── Model mới tốt hơn ──► Promote
       │
       └── Model mới không tốt hơn ──► Giữ model cũ, ghi log
`

## Cảnh báo

| Mức độ | Điều kiện | Hành động |
|--------|-----------|-----------|
| Warning | PSI > 0.1 | Ghi log, thông báo team |
| Critical | PSI > 0.2 | Kích hoạt retraining tự động |
| Emergency | Model không khả dụng | Rollback về model trước đó |

## Ghi chú

- Mọi lần retraining đều được log vào MLflow
- Model mới phải qua validation trước khi promote
- Giữ tối thiểu 3 phiên bản model trước đó để rollback
