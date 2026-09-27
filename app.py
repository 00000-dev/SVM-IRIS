from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import joblib
import time

from database import get_connection
from starlette.middleware.sessions import SessionMiddleware 

# =========================
# 1. ĐƯỜNG DẪN PROJECT
# =========================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "svm_model.pkl"
HTML_PATH = BASE_DIR / "index.html"
IMAGES_PATH = BASE_DIR / "images"


# =========================
# 2. LOAD MODEL SVM
# =========================

model = joblib.load(MODEL_PATH)
LDA_MODEL_PATH = BASE_DIR / "lda_model.pkl"
KNN_MODEL_PATH = BASE_DIR / "knn_model.pkl"

lda_model = joblib.load(LDA_MODEL_PATH)
knn_model = joblib.load(KNN_MODEL_PATH)

# =========================
# 3. FASTAPI APP
# =========================

app = FastAPI(
    title="Iris Classification API",
    description="SVM model for the Iris dataset",
    version="1.0.0",
)

app.add_middleware(
    SessionMiddleware,
    secret_key="iris-botanica-secret-key"
)
# =========================
# 4. THƯ MỤC HÌNH ẢNH
# =========================

app.mount(
    "/images",
    StaticFiles(directory=IMAGES_PATH),
    name="images"
)


# =========================
# 5. INPUT DATA
# =========================

class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

class PredictModelInput(BaseModel):
    model_name: str
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
# =========================
# =========================
# 6. INPUT ĐĂNG KÝ
# =========================

class RegisterInput(BaseModel):
    ten_dang_nhap: str
    mat_khau: str
    # =========================
# 6. INPUT ĐĂNG NHẬP
# =========================

class LoginInput(BaseModel):
    ten_dang_nhap: str
    mat_khau: str
# 6. MAPPING LOÀI HOA
# =========================

species = {
    0: "setosa",
    1: "versicolor",
    2: "virginica",
}


# =========================
# 7. TRANG CHỦ
# =========================

@app.get("/")
def home():
    return FileResponse(HTML_PATH)


# =========================
# 8. TRANG BỘ SƯU TẬP
# =========================

@app.get("/species")
def species_page():
    return FileResponse(BASE_DIR / "species.html")


# =========================
# 9. TRANG ĐIỂM NGHIÊN CỨU
# =========================

@app.get("/locations")
def locations_page():
    return FileResponse(BASE_DIR / "locations.html")

# =========================

@app.get("/about")
def about_page():
    return FileResponse(BASE_DIR / "about.html")
# =========================
@app.get("/model-evaluation")
def get_model_evaluation():

    conn = get_connection()
    cursor = conn.cursor()

    results = cursor.execute("""
        SELECT
            ten_mo_hinh,
            accuracy,
            precision,
            recall,
            f1_score,
            thoi_gian_huan_luyen,
            thoi_gian_du_doan
        FROM ket_qua_mo_hinh
        ORDER BY ma_mo_hinh
    """).fetchall()

    conn.close()

    return {
        "success": True,
        "models": [
            {
                "ten_mo_hinh": row["ten_mo_hinh"],
                "accuracy": row["accuracy"],
                "precision": row["precision"],
                "recall": row["recall"],
                "f1_score": row["f1_score"],
                "thoi_gian_huan_luyen": row["thoi_gian_huan_luyen"],
                "thoi_gian_du_doan": row["thoi_gian_du_doan"]
            }
            for row in results
        ]
    }
# =========================
# TRANG ĐÁNH GIÁ MÔ HÌNH
# =========================

@app.get("/model-evaluation-page")
def model_evaluation_page():
    return FileResponse(BASE_DIR / "model-evaluation.html")
# 11. HEALTH CHECK
# =========================

@app.get("/health")
def health():
    return {"status": "healthy"}


# =========================
# 12. DỰ ĐOÁN
# =========================
@app.post("/predict")
def predict(data: IrisInput, request: Request):

    # =========================
    # 1. Kiểm tra người dùng
    # =========================
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập trước khi dự đoán!"
        }

    # =========================
    # 2. Chuẩn bị dữ liệu
    # =========================
    features = [[
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width,
    ]]

    # =========================
    # 3. Chạy mô hình + đo thời gian
    # =========================
    start_time = time.perf_counter()

    prediction = int(model.predict(features)[0])

    end_time = time.perf_counter()

    execution_time = end_time - start_time

    # =========================
    # 4. Lưu lịch sử dự đoán
    # =========================
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO lich_su_du_doan (
            ma_nguoi_dung,
            sepal_length,
            sepal_width,
            petal_length,
            petal_width,
            ket_qua,
            ten_mo_hinh,
            thoi_gian_chay
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ma_nguoi_dung,
            data.sepal_length,
            data.sepal_width,
            data.petal_length,
            data.petal_width,
            prediction,
            "SVM",
            execution_time
        )
    )

    conn.commit()
    conn.close()

    # =========================
    # 5. Trả kết quả về website
    # =========================
    return {
        "success": True,
        "class_id": prediction,
        "prediction": species[prediction],
        "model": "SVM",
        "execution_time": execution_time
    }
@app.post("/predict-model")
def predict_model(data: PredictModelInput, request: Request):

    # 1. Kiểm tra đăng nhập
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập trước khi dự đoán!"
        }

    # 2. Chọn mô hình
    models = {
        "SVM": model,
        "LDA": lda_model,
        "KNN": knn_model
    }

    if data.model_name not in models:
        return {
            "success": False,
            "message": "Mô hình không hợp lệ!"
        }

    selected_model = models[data.model_name]

    # 3. Chuẩn bị dữ liệu đầu vào
    features = [[
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width
    ]]

    # 4. Đo thời gian dự đoán
    start_time = time.perf_counter()

    prediction = int(selected_model.predict(features)[0])

    end_time = time.perf_counter()

    execution_time = end_time - start_time

    # 5. Lưu lịch sử dự đoán vào database
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO lich_su_du_doan (
            ma_nguoi_dung,
            sepal_length,
            sepal_width,
            petal_length,
            petal_width,
            ket_qua,
            ten_mo_hinh,
            thoi_gian_chay
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ma_nguoi_dung,
            data.sepal_length,
            data.sepal_width,
            data.petal_length,
            data.petal_width,
            prediction,
            data.model_name,
            execution_time
        )
    )

    conn.commit()
    conn.close()

    # 6. Trả kết quả về giao diện
    return {
        "success": True,
        "class_id": prediction,
        "prediction": species[prediction],
        "model": data.model_name,
        "execution_time": execution_time
    }
# 13. API ĐĂNG KÝ
# =========================

@app.post("/register")
def register(data: RegisterInput):

    conn = get_connection()
    cursor = conn.cursor()

    # Kiểm tra tên đăng nhập đã tồn tại chưa
    user = cursor.execute(
        """
        SELECT ma_nguoi_dung
        FROM nguoi_dung
        WHERE ten_dang_nhap = ?
        """,
        (data.ten_dang_nhap,)
    ).fetchone()

    if user:
        conn.close()

        return {
            "success": False,
            "message": "Tên đăng nhập đã tồn tại!"
        }

    # Thêm người dùng mới
    cursor.execute(
        """
        INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau)
        VALUES (?, ?)
        """,
        (data.ten_dang_nhap, data.mat_khau)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Đăng ký tài khoản thành công!"
    }
# =========================
# 14. API ĐĂNG NHẬP
# =========================


@app.post("/login")
def login(data: LoginInput, request: Request):

    conn = get_connection()
    cursor = conn.cursor()

    # Tìm người dùng theo tên đăng nhập
    user = cursor.execute(
        """
        SELECT ma_nguoi_dung, ten_dang_nhap, mat_khau
        FROM nguoi_dung
        WHERE ten_dang_nhap = ?
        """,
        (data.ten_dang_nhap,)
    ).fetchone()

    # Không tìm thấy tài khoản
    if user is None:
        conn.close()
        return {
            "success": False,
            "message": "Tên đăng nhập không tồn tại!"
        }

    # Kiểm tra mật khẩu
    if user["mat_khau"] != data.mat_khau:
        conn.close()
        return {
            "success": False,
            "message": "Mật khẩu không đúng!"
        }

    # Lưu người dùng vào Session
    request.session["ma_nguoi_dung"] = user["ma_nguoi_dung"]

    # Lưu lịch sử đăng nhập
    cursor.execute(
        """
        INSERT INTO lich_su_dang_nhap (ma_nguoi_dung)
        VALUES (?)
        """,
        (user["ma_nguoi_dung"],)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Đăng nhập thành công!",
        "ma_nguoi_dung": user["ma_nguoi_dung"],
        "ten_dang_nhap": user["ten_dang_nhap"]
    }

# =========================
# 15. API KIỂM TRA NGƯỜI DÙNG
# =========================

@app.get("/user/{ma_nguoi_dung}")
def get_user(ma_nguoi_dung: int):

    conn = get_connection()
    cursor = conn.cursor()

    user = cursor.execute(
        """
        SELECT ma_nguoi_dung, ten_dang_nhap, ngay_tao
        FROM nguoi_dung
        WHERE ma_nguoi_dung = ?
        """,
        (ma_nguoi_dung,)
    ).fetchone()
    
    conn.close()

    if user is None:
        return {
            "success": False,
            "message": "Không tìm thấy người dùng!"
        }

    return {
        "success": True,
        "ma_nguoi_dung": user["ma_nguoi_dung"],
        "ten_dang_nhap": user["ten_dang_nhap"],
        "ngay_tao": user["ngay_tao"]
    }
# =========================
# 16. API LỊCH SỬ ĐĂNG NHẬP
# =========================

@app.get("/login-history/{ma_nguoi_dung}")
def get_login_history(ma_nguoi_dung: int):

    conn = get_connection()
    cursor = conn.cursor()

    history = cursor.execute(
        """
        SELECT ma_dang_nhap, thoi_gian_dang_nhap
        FROM lich_su_dang_nhap
        WHERE ma_nguoi_dung = ?
        ORDER BY thoi_gian_dang_nhap DESC
        """,
        (ma_nguoi_dung,)
    ).fetchall()

    conn.close()

    return {
        "success": True,
        "history": [
            {
                "ma_dang_nhap": row["ma_dang_nhap"],
                "thoi_gian_dang_nhap": row["thoi_gian_dang_nhap"]
            }
            for row in history
        ]
    }
# =========================
# 17. API ĐĂNG XUẤT
# =========================

@app.post("/logout")
def logout(request: Request):

    request.session.clear()

    return {
        "success": True,
        "message": "Đăng xuất thành công!"
    }