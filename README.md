# IRIS BOTANICA AI

## Bảng hướng dẫn các mục code

| File / Thư mục | Chức năng |
|---|---|
| `app.py` | File chính của hệ thống FastAPI, xử lý API, dự đoán và kết nối các chức năng |
| `TRAIN_SVM.py` | Huấn luyện mô hình SVM và lưu mô hình |
| `evaluate_models.py` | Huấn luyện và đánh giá các mô hình SVM, LDA và KNN |
| `index.html` | Giao diện chính, nhập thông số hoa và thực hiện dự đoán |
| `model-evaluation.html` | Hiển thị kết quả đánh giá và so sánh các mô hình |
| `model-history.html` | Hiển thị lịch sử dự đoán và thùng rác |
| `species.html` | Hiển thị thông tin các loài hoa Iris |
| `Iris.csv` | Bộ dữ liệu Iris sử dụng cho quá trình huấn luyện |
| `svm_model.pkl` | Mô hình SVM đã được huấn luyện |
| `lda_model.pkl` | Mô hình LDA đã được huấn luyện |
| `knn_model.pkl` | Mô hình KNN đã được huấn luyện |
| `database/connection.py` | Thiết lập kết nối với SQL Server |
| `database/user.py` | Xử lý đăng ký, đăng nhập và thông tin người dùng |
| `database/history.py` | Xử lý lịch sử đăng nhập |
| `database/prediction.py` | Lưu, lấy, xóa, khôi phục và quản lý lịch sử dự đoán |
| `database/model.py` | Xử lý thông tin các mô hình |
| `database/model_history.py` | Xử lý lịch sử hoạt động của mô hình |
| `SQL/` | Chứa các câu lệnh SQL tạo và quản lý cơ sở dữ liệu |
| `images/` | Chứa hình ảnh sử dụng trong giao diện |
| `report/` | Chứa báo cáo của đề tài |
| `requirements.txt` | Danh sách các thư viện Python cần thiết |
| `Procfile` | Cấu hình lệnh chạy ứng dụng khi triển khai |
| `render.yaml` | Cấu hình triển khai hệ thống trên Render |

---

## Quy trình hoạt động

```text
Iris Dataset
     ↓
TRAIN_SVM.py
     ↓
Huấn luyện mô hình SVM
     ↓
svm_model.pkl
     ↓
app.py
     ↓
FastAPI API
     ↓
index.html
     ↓
Nhập thông số hoa Iris
     ↓
Dự đoán kết quả
     ↓
SQL Server
     ↓
Lưu lịch sử dự đoán
```

---

## Chạy hệ thống

### 1. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### 2. Chạy FastAPI

```bash
python -m uvicorn app:app --reload
```

### 3. Mở giao diện

Truy cập:

http://127.0.0.1:8000

### Nếu chạy bằng port 8010

```bash
python -m uvicorn app:app --port 8010
```

Truy cập:

http://127.0.0.1:8010