# Model Card — House Price Prediction

## Thông tin chung

| Mục | Chi tiết |
|-----|----------|
| Tên model | GradientBoostingRegressor |
| Phiên bản | 0.1.0 |
| Mục tiêu | Dự đoán giá nhà dựa trên đặc trưng |
| Framework | Scikit-learn |
| Ngày tạo | 2024 |

## Mô tả

Model sử dụng thuật toán Gradient Boosting Regression để dự đoán giá nhà
dựa trên 6 đặc trưng đầu vào: diện tích, số phòng ngủ, số phòng tắm,
tuổi nhà, số chỗ đỗ xe và vị trí.

## Dữ liệu huấn luyện

- **Nguồn**: File houses.csv (1000 bản ghi)
- **Chia tập**: 70% train, 10% validation, 20% test
- **Tiền xử lý**: LabelEncoder cho location, StandardScaler cho biến số

## Đặc trưng đầu vào

| Đặc trưng | Kiểu | Mô tả |
|-----------|------|-------|
| area | float | Diện tích (m²) |
| bedrooms | int | Số phòng ngủ |
| bathrooms | int | Số phòng tắm |
| age | int | Tuổi nhà (năm) |
| garage | int | Số chỗ đỗ xe |
| location | str | Vị trí (mã hóa LabelEncoder) |

## Tham số huấn luyện

- n_estimators: 200
- max_depth: 5
- learning_rate: 0.1
- random_state: 42

## Tiêu chí chấp nhận

| Metric | Ngưỡng | Mô tả |
|--------|--------|-------|
| R² | >= 0.60 | Hệ số xác định |
| RMSE | <= 50000 | Sai số bình phương trung bình |
| MAE | <= 35000 | Sai số tuyệt đối trung bình |

## Giới hạn và rủi ro

- Model chỉ được huấn luyện trên dữ liệu mô phỏng, không phản ánh thị trường thực
- Hiệu năng có thể giảm khi phân phối dữ liệu thay đổi (data drift)
- Không xử lý được các vị trí ngoài danh sách District_1 đến District_20

## Quy trình cập nhật

1. Phát hiện data drift qua hệ thống monitoring
2. Thu thập dữ liệu mới
3. Huấn luyện lại model với pipeline DVC
4. Validate model theo tiêu chí chấp nhận
5. Promote model nếu đạt ngưỡng
