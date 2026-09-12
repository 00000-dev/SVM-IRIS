from fastapi import FastAPI
from pydantic import BaseModel
import joblib

# Load mô hình đã tạo ở Bước 1
model = joblib.load("svm_model.pkl")

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Iris Classification API",
    description="SVM model for the Iris dataset",
    version="1.0.0",
)

# Khai báo cấu trúc dữ liệu đầu vào
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

# Bảng ánh xạ nhãn dự đoán sang tên loài hoa
species = {
    0: "setosa",
    1: "versicolor",
    2: "virginica"
}

# Endpoint 1: Trang chủ
@app.get("/")
def home():
    return {"message": "Iris SVM API is running"}

# Endpoint 2: Kiểm tra trạng thái
@app.get("/health")
def health():
    return {"status": "healthy"}
@app.post("/predict")
def predict(data: IrisInput):
    features = [[
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width
    ]]

    # Mô hình trả về tên loài hoa
    raw_pred = model.predict(features)[0]
    pred_name = str(raw_pred)

    # Ánh xạ tên loài sang class_id
    class_mapping = {
        "Iris-setosa": 0,
        "Iris-versicolor": 1,
        "Iris-virginica": 2
    }

    class_id = class_mapping[pred_name]

    return {
        "class_id": class_id,
        "prediction": pred_name
    }