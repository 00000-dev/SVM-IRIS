

from pathlib import Path
import os
import time
import math
import traceback
import joblib

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sklearn import datasets
from sklearn.base import clone

from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
from zoneinfo import ZoneInfo

from database.user import (
    username_exists,
    create_user,
    check_login,
    get_user_by_id,
    get_all_users,
    update_user_status
)

from database.history import (
    create_login_history,
    get_login_history,
    get_all_login_history
)

from database.prediction import (
    create_prediction_history,
    get_prediction_history,
    get_deleted_prediction_history,
    get_prediction_by_id,
    soft_delete_prediction_history,
    restore_prediction_history,
    permanently_delete_prediction_history,
    permanently_delete_all_prediction_history,
    get_all_prediction_history,
    get_prediction_statistics
)

from database.model import get_model_evaluations

from database.model_history import (
    create_model_history,
    get_model_history
)


def get_vietnam_time():
    return datetime.now(
        ZoneInfo("Asia/Ho_Chi_Minh")
    ).strftime("%Y-%m-%d %H:%M:%S")
# =========================
# 1. ĐƯỜNG DẪN PROJECT
# =========================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "svm_model.pkl"
HTML_PATH = BASE_DIR / "index.html"
IMAGES_PATH = BASE_DIR / "images"


# 2. LOAD CÁC MÔ HÌNH
# =========================

model = joblib.load(BASE_DIR / "svm_model.pkl")  # SVM Linear

svm_rbf_model = joblib.load(BASE_DIR / "svm_rbf_model.pkl")
svm_poly_model = joblib.load(BASE_DIR / "svm_poly_model.pkl")
svm_sigmoid_model = joblib.load(BASE_DIR / "svm_sigmoid_model.pkl")

lda_model = joblib.load(BASE_DIR / "lda_model.pkl")
knn_model = joblib.load(BASE_DIR / "knn_model.pkl")
# =========================
# DỮ LIỆU HUẤN LUYỆN SVM TÙY CHỈNH
# =========================

iris_data = datasets.load_iris()

X_IRIS = iris_data.data
y_IRIS = iris_data.target

# =========================
# 3. FASTAPI APP
# =========================
app = FastAPI(
    title="IRIS BOTANICA TEST 123",
    description="SVM model for the Iris dataset",
    version="1.0.0",
)
print("ROUTE DELETE TRASH:", any(
    route.path == "/model-history/trash"
    and "DELETE" in route.methods
    for route in app.routes
))
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv(
        "SESSION_SECRET_KEY",
        "iris-botanica-secret-key-change-this"
    ),
    session_cookie="iris_session",
    same_site="lax",
    https_only=os.getenv("RENDER", "").lower() == "true"
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

    # Tham số tùy chỉnh cho SVM
    C: float = 1.0
    gamma: str = "scale"
    degree: int = 3

    
class SaveModelHistoryInput(BaseModel):
    model_name: str
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

    results = get_model_evaluations()

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


# =========================
@app.get("/model-history-page")
def model_history_page():
    return FileResponse(BASE_DIR / "model-history.html")

@app.post("/model-history")
def save_model_history(data: SaveModelHistoryInput):

    results = get_model_evaluations()

    selected_model = None

    for item in results:
        if item["ten_mo_hinh"] == data.model_name:
            selected_model = item
            break

    if selected_model is None:
        return {
            "success": False,
            "message": "Không tìm thấy mô hình cần lưu!"
        }

    success = create_model_history(
        ma_mo_hinh=selected_model["ma_mo_hinh"],
        accuracy=selected_model["accuracy"],
        precision=selected_model["precision"],
        recall=selected_model["recall"],
        f1_score=selected_model["f1_score"],
        thoi_gian_huan_luyen=selected_model["thoi_gian_huan_luyen"],
        thoi_gian_du_doan=selected_model["thoi_gian_du_doan"]
    )

    if not success:
        return {
            "success": False,
            "message": "Không thể lưu lịch sử mô hình!"
        }

    return {
        "success": True,
        "message": f"Đã lưu kết quả {data.model_name} vào lịch sử mô hình!",
        "ten_mo_hinh": data.model_name
    }
# =========================================================
# =========================================================
# LỊCH SỬ DỰ ĐOÁN
# =========================================================
@app.get("/prediction-history")
def prediction_history(request: Request):
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if not ma_nguoi_dung:
        return {
            "success": False,
            "message": "Bạn chưa đăng nhập!"
        }

    history = get_prediction_history(ma_nguoi_dung)

    return {
        "success": True,
        "history": history
    }


# =========================================================
# THÙNG RÁC
# =========================================================

@app.get("/prediction-history/trash")
def prediction_history_trash(request: Request):
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập!"
        }

    history = get_deleted_prediction_history(ma_nguoi_dung)

    return {
        "success": True,
        "history": history
    }


@app.delete("/prediction-history/trash")
async def permanently_delete_all_prediction_history_route(
    request: Request
):
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Bạn chưa đăng nhập!"
        }

    try:

        deleted_count = permanently_delete_all_prediction_history(
            ma_nguoi_dung
        )

        print(
            f"Đã xóa vĩnh viễn {deleted_count} bản ghi "
            f"của user {ma_nguoi_dung}"
        )

        return {
            "success": True,
            "message": f"Đã xóa vĩnh viễn {deleted_count} bản ghi.",
            "deleted_count": deleted_count
        }

    except Exception as e:

        print("LỖI XÓA TẤT CẢ:", repr(e))

        return {
            "success": False,
            "message": f"Lỗi: {str(e)}"
        }


# =========================================================
# LẤY 1 LỊCH SỬ
# =========================================================

@app.get("/prediction-history/{ma_du_doan}")
def get_one_prediction_history(
    ma_du_doan: int,
    request: Request
):
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập!"
        }

    history = get_prediction_by_id(
        ma_du_doan,
        ma_nguoi_dung
    )

    if history is None:
        return {
            "success": False,
            "message": "Không tìm thấy lịch sử dự đoán!"
        }

    return {
        "success": True,
        "history": history
    }


# =========================================================
# XÓA VÀO THÙNG RÁC
# =========================================================

@app.patch("/prediction-history/{ma_du_doan}/delete")
def delete_model_history(
    ma_du_doan: int,
    request: Request
):
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập!"
        }

    success = soft_delete_prediction_history(
        ma_du_doan,
        ma_nguoi_dung
    )

    return {
        "success": success,
        "message": (
            "Đã chuyển vào thùng rác!"
            if success
            else "Không tìm thấy lịch sử!"
        )
    }


# =========================================================
# KHÔI PHỤC
# =========================================================

@app.patch("/prediction-history/{ma_du_doan}/restore")
def restore_model_history(
    ma_du_doan: int,
    request: Request
):
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập!"
        }

    success = restore_prediction_history(
        ma_du_doan,
        ma_nguoi_dung
    )

    return {
        "success": success,
        "message": (
            "Đã khôi phục lịch sử!"
            if success
            else "Không tìm thấy lịch sử trong thùng rác!"
        )
    }


# =========================================================
# XÓA VĨNH VIỄN
# =========================================================

@app.delete("/prediction-history/{ma_du_doan}")
def permanently_delete_model_history(
    ma_du_doan: int,
    request: Request
):
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập!"
        }

    success = permanently_delete_prediction_history(
        ma_du_doan,
        ma_nguoi_dung
    )

    return {
        "success": success,
        "message": (
            "Đã xóa vĩnh viễn!"
            if success
            else "Không tìm thấy lịch sử!"
        )
    }
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

    # 1. Kiểm tra người dùng
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập trước khi dự đoán!"
        }

    # 2. Chuẩn bị dữ liệu
    features = [[
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width
    ]]

    # 3. Chạy mô hình + đo thời gian
    start_time = time.perf_counter()

    prediction = int(model.predict(features)[0])

    end_time = time.perf_counter()

    execution_time = end_time - start_time

    # 4. Lưu lịch sử dự đoán vào SQL Server
    create_prediction_history(
        ma_nguoi_dung=ma_nguoi_dung,
        sepal_length=data.sepal_length,
        sepal_width=data.sepal_width,
        petal_length=data.petal_length,
        petal_width=data.petal_width,
        ket_qua=prediction,
        ten_mo_hinh="SVM",
        thoi_gian_chay=execution_time
    )

    # 5. Trả kết quả về website
    return {
        "success": True,
        "class_id": prediction,
        "prediction": species[prediction],
        "model": "SVM",
        "execution_time": execution_time
    }
# =========================
# 12.1. API DỰ ĐOÁN THEO MÔ HÌNH
# =========================


# =========================================================
# API DỰ ĐOÁN THEO 6 MÔ HÌNH
# HỖ TRỢ TÙY CHỈNH THAM SỐ SVM
# =========================================================

@app.post("/predict-model")
def predict_model(
    data: PredictModelInput,
    request: Request
):

    # 1. KIỂM TRA ĐĂNG NHẬP
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập trước khi dự đoán!"
        }

    # 2. KIỂM TRA TÊN MÔ HÌNH
    models = {
        "SVM": model,
        "SVM_RBF": svm_rbf_model,
        "SVM_POLY": svm_poly_model,
        "SVM_SIGMOID": svm_sigmoid_model,
        "LDA": lda_model,
        "KNN": knn_model
    }

    if data.model_name not in models:
        return {
            "success": False,
            "message": "Mô hình không hợp lệ!"
        }

    selected_model = models[data.model_name]

    # 3. CHUẨN BỊ DỮ LIỆU ĐẦU VÀO
    features = [[
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width
    ]]

    # 4. XỬ LÝ THAM SỐ SVM
    parameters = {}

    if data.model_name.startswith("SVM"):

        C = data.C if data.C is not None else 1.0
        gamma = data.gamma or "scale"
        degree = data.degree if data.degree is not None else 3

        # Kiểm tra C
        if not math.isfinite(C) or C <= 0:
            return {
                "success": False,
                "message": "Tham số C phải là số lớn hơn 0!"
            }

        # Kiểm tra Gamma
        if gamma not in ["scale", "auto"]:
            return {
                "success": False,
                "message": "Gamma chỉ được chọn scale hoặc auto!"
            }

        # Kiểm tra Degree
        if not isinstance(degree, int) or not 1 <= degree <= 10:
            return {
                "success": False,
                "message": "Degree phải là số nguyên từ 1 đến 10!"
            }

        # Tạo bản sao Pipeline, không làm thay đổi model gốc
        selected_model = clone(selected_model)

        # Cấu hình tham số cho SVC bên trong Pipeline
        svm_params = {
            "classifier__C": C
        }

        if data.model_name in [
            "SVM_RBF",
            "SVM_POLY",
            "SVM_SIGMOID"
        ]:
            svm_params["classifier__gamma"] = gamma

        if data.model_name == "SVM_POLY":
            svm_params["classifier__degree"] = degree

        selected_model.set_params(**svm_params)

        parameters = {
            "C": C
        }

        if data.model_name in [
            "SVM_RBF",
            "SVM_POLY",
            "SVM_SIGMOID"
        ]:
            parameters["gamma"] = gamma

        if data.model_name == "SVM_POLY":
            parameters["degree"] = degree

   
    # 5. HUẤN LUYỆN VÀ DỰ ĐOÁN
    start_time = time.perf_counter()

    # Chỉ huấn luyện lại khi là SVM
    # LDA và KNN sử dụng mô hình đã lưu
    if data.model_name.startswith("SVM"):
        print("MODEL:", data.model_name)
        print("PARAMETERS:", parameters)

        selected_model.fit(X_IRIS, y_IRIS)

        print("SVM TRAINING SUCCESS")

    prediction = int(
        selected_model.predict(features)[0]
    )

    end_time = time.perf_counter()
    execution_time = end_time - start_time


    # 6. LƯU LỊCH SỬ DỰ ĐOÁN
    create_prediction_history(
        ma_nguoi_dung=ma_nguoi_dung,
        sepal_length=data.sepal_length,
        sepal_width=data.sepal_width,
        petal_length=data.petal_length,
        petal_width=data.petal_width,
        ket_qua=prediction,
        ten_mo_hinh=data.model_name,
        thoi_gian_chay=execution_time
    )

    # 7. TRẢ KẾT QUẢ
    return {
        "success": True,
        "class_id": prediction,
        "prediction": species[prediction],
        "model": data.model_name,
        "model_name": data.model_name,
        "execution_time": execution_time,
        "parameters": parameters
    }

# =========================
# 13. API ĐĂNG KÝ
# =========================
# =========================
# 13. API ĐĂNG KÝ
# =========================

@app.post("/register")
def register(data: RegisterInput):
    try:
        username = data.ten_dang_nhap.strip()
        password = data.mat_khau

        if not username or not password:
            return {
                "success": False,
                "message": "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu!"
            }

        if username_exists(username):
            return {
                "success": False,
                "message": "Tên đăng nhập đã tồn tại! Vui lòng đăng nhập."
            }

        create_user(username, password)

        return {
            "success": True,
            "message": "Đăng ký tài khoản thành công!"
        }

    except Exception as e:
        print("REGISTER ERROR:", repr(e))
        traceback.print_exc()

        return {
            "success": False,
            "message": "Không thể đăng ký tài khoản. Vui lòng thử lại!"
        }

# =========================
# 14. API ĐĂNG NHẬP
# =========================

@app.post("/login")
def login(data: LoginInput, request: Request):
    try:
        username = data.ten_dang_nhap.strip()

        user = check_login(username, data.mat_khau)

        if user is None:
            return {
                "success": False,
                "message": "Tên đăng nhập hoặc mật khẩu không đúng!"
            }

        request.session["ma_nguoi_dung"] = user["ma_nguoi_dung"]

        create_login_history(user["ma_nguoi_dung"])

        return {
            "success": True,
            "message": "Đăng nhập thành công!",
            "user": {
                "ma_nguoi_dung": user["ma_nguoi_dung"],
                "ten_dang_nhap": user["ten_dang_nhap"],
                "vai_tro": user["vai_tro"]
            }
        }

    except Exception as e:
        print("LOGIN ERROR:", repr(e))
        traceback.print_exc()

        return {
            "success": False,
            "message": "Không thể đăng nhập. Vui lòng thử lại!"
        }


# =========================
# 15. API KIỂM TRA SESSION
# =========================
@app.get("/me")
def get_current_user(request: Request):
    try:
        # Lấy mã người dùng từ session
        ma_nguoi_dung = request.session.get("ma_nguoi_dung")

        # Chưa đăng nhập
        if not ma_nguoi_dung:
            return {
                "success": False,
                "message": "Bạn chưa đăng nhập!",
                "logged_in": False
            }

        # Lấy thông tin mới nhất từ database
        user = get_user_by_id(ma_nguoi_dung)

        # Tài khoản không tồn tại hoặc đã bị khóa
        if user is None or not user["trang_thai"]:
            request.session.clear()

            return {
                "success": False,
                "message": "Tài khoản không tồn tại hoặc đã bị khóa!",
                "logged_in": False
            }

        return {
            "success": True,
            "logged_in": True,
            "ma_nguoi_dung": user["ma_nguoi_dung"],
            "ten_dang_nhap": user["ten_dang_nhap"],
            "ngay_tao": user["ngay_tao"],
            "vai_tro": user["vai_tro"]
        }

    except Exception as e:
        print("Lỗi kiểm tra session:", e)

        return {
            "success": False,
            "message": "Không thể kiểm tra thông tin đăng nhập!",
            "logged_in": False
        }



# =========================
# 15. API KIỂM TRA NGƯỜI DÙNG
# =========================

@app.get("/user/{ma_nguoi_dung}")
def get_user(ma_nguoi_dung: int, request: Request):

    current_id = request.session.get("ma_nguoi_dung")

    # Kiểm tra đăng nhập
    if current_id is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập!"
        }

    # Lấy thông tin người đang đăng nhập từ database
    current_user = get_user_by_id(current_id)

    if current_user is None or not current_user["trang_thai"]:
        request.session.clear()
        return {
            "success": False,
            "message": "Tài khoản không tồn tại hoặc đã bị khóa!"
        }

    # Kiểm tra quyền Admin từ database
    is_admin = (
        str(current_user["vai_tro"]).strip().lower() == "admin"
    )

    # USER chỉ được xem thông tin của chính mình
    if int(current_id) != ma_nguoi_dung and not is_admin:
        return {
            "success": False,
            "message": "Bạn không có quyền truy cập!"
        }

    # Lấy thông tin tài khoản cần xem
    user = get_user_by_id(ma_nguoi_dung)

    if user is None:
        return {
            "success": False,
            "message": "Không tìm thấy người dùng!"
        }

    return {
        "success": True,
        "ma_nguoi_dung": user["ma_nguoi_dung"],
        "ten_dang_nhap": user["ten_dang_nhap"],
        "ngay_tao": user["ngay_tao"],
        "vai_tro": user["vai_tro"]
    }

# =========================
# 16. API LỊCH SỬ ĐĂNG NHẬP
# =========================
@app.get("/login-history/{ma_nguoi_dung}")
def get_login_history_api(
    ma_nguoi_dung: int,
    request: Request
):
    current_id = request.session.get("ma_nguoi_dung")

    if current_id is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập!"
        }

    current_user = get_user_by_id(current_id)

    if current_user is None or not current_user["trang_thai"]:
        request.session.clear()
        return {
            "success": False,
            "message": "Tài khoản không tồn tại hoặc đã bị khóa!"
        }

    is_admin = (
        str(current_user["vai_tro"]).strip().lower() == "admin"
    )

    if int(current_id) != ma_nguoi_dung and not is_admin:
        return {
            "success": False,
            "message": "Bạn không có quyền xem lịch sử này!"
        }

    history = get_login_history(ma_nguoi_dung)

    return {
        "success": True,
        "history": [
            {
                "ma_dang_nhap": item["ma_dang_nhap"],
                "thoi_gian_dang_nhap": str(
                    item["thoi_gian_dang_nhap"]
                )
            }
            for item in history
        ]
    }
## =========================
# 17. API ĐĂNG XUẤT
# =========================

@app.post("/logout")
def logout(request: Request):

    request.session.clear()

    return {
        "success": True,
        "message": "Đăng xuất thành công!"
    }

# =========================================================
# 18. ADMIN - KIỂM TRA QUYỀN
# =========================================================

def get_admin_user(request: Request):
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return None

    # Luôn kiểm tra quyền mới nhất từ database
    user = get_user_by_id(ma_nguoi_dung)

    if user is None or not user["trang_thai"]:
        request.session.clear()
        return None

    if str(user["vai_tro"]).strip().lower() != "admin":
        return None

    return user

# =========================================================
# TRANG ADMIN
# =========================================================
@app.get("/admin")
def admin_page(request: Request):
    admin = get_admin_user(request)

    if admin is None:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền truy cập trang quản trị!"
        )

    return FileResponse(BASE_DIR / "admin.html")


# =========================================================
# API TỔNG QUAN ADMIN
# =========================================================

@app.get("/admin/dashboard")
def admin_dashboard(request: Request):

    admin = get_admin_user(request)

    if admin is None:
        return {
            "success": False,
            "message": "Bạn không có quyền quản trị!"
        }

    users = get_all_users()
    prediction_stats = get_prediction_statistics()

    total_users = len(users)

    active_users = sum(
        1 for user in users
        if user["trang_thai"]
    )

    locked_users = sum(
        1 for user in users
        if not user["trang_thai"]
    )

    admin_count = sum(
        1 for user in users
        if str(user["vai_tro"]).lower() == "admin"
    )

    return {
        "success": True,
        "total_users": total_users,
        "active_users": active_users,
        "locked_users": locked_users,
        "admin_count": admin_count,
        "total_predictions": prediction_stats["tong_luot_du_doan"],
"users_who_predicted": prediction_stats["so_nguoi_da_du_doan"]
    }

# =========================================================
# API DANH SÁCH TÀI KHOẢN
# =========================================================

@app.get("/admin/users")
def admin_users(request: Request):

    admin = get_admin_user(request)

    if admin is None:
        return {
            "success": False,
            "message": "Bạn không có quyền truy cập!"
        }

    users = get_all_users()

    return {
        "success": True,
        "users": [
            {
                "ma_nguoi_dung": user["ma_nguoi_dung"],
                "ten_dang_nhap": user["ten_dang_nhap"],
                "ngay_tao": (
                    str(user["ngay_tao"])
                    if user["ngay_tao"] else None
                ),
                "trang_thai": bool(user["trang_thai"]),
                "vai_tro": user["vai_tro"]
            }
            for user in users
        ]
    }


# =========================================================
# API KHÓA / MỞ KHÓA TÀI KHOẢN
# =========================================================

@app.patch("/admin/users/{ma_nguoi_dung}/status")
def admin_update_user_status(
    ma_nguoi_dung: int,
    request: Request
):

    admin = get_admin_user(request)

    if admin is None:
        return {
            "success": False,
            "message": "Bạn không có quyền thực hiện!"
        }

    target_user = get_user_by_id(ma_nguoi_dung)

    if target_user is None:
        return {
            "success": False,
            "message": "Không tìm thấy tài khoản!"
        }

    if str(target_user["vai_tro"]).lower() != "user":
        return {
            "success": False,
            "message": "Không thể khóa tài khoản quản trị!"
        }

    new_status = not bool(target_user["trang_thai"])

    success = update_user_status(
        ma_nguoi_dung,
        new_status
    )

    return {
        "success": success,
        "message": (
            "Đã mở khóa tài khoản!"
            if new_status
            else "Đã khóa tài khoản!"
        ) if success else "Không thể cập nhật tài khoản!"
    }
# =========================================================
# ADMIN - TOÀN BỘ LỊCH SỬ ĐĂNG NHẬP
# =========================================================

@app.get("/admin/login-history")
def admin_all_login_history(request: Request):

    admin = get_admin_user(request)

    if admin is None:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền truy cập!"
        )

    history = get_all_login_history()

    return {
        "success": True,
        "history": [
            {
                "ma_dang_nhap": item["ma_dang_nhap"],
                "ma_nguoi_dung": item["ma_nguoi_dung"],
                "ten_dang_nhap": item["ten_dang_nhap"],
                "vai_tro": item["vai_tro"],
                "thoi_gian_dang_nhap": str(
                    item["thoi_gian_dang_nhap"]
                )
            }
            for item in history
        ]
    }

# =========================================================
# ADMIN - TOÀN BỘ LỊCH SỬ DỰ ĐOÁN
# =========================================================

@app.get("/admin/prediction-history")
def admin_all_prediction_history(request: Request):

    admin = get_admin_user(request)

    if admin is None:
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền truy cập!"
        )

    history = get_all_prediction_history()

    return {
        "success": True,
        "history": [
            {
                **item,
                "thoi_gian_du_doan": str(
                    item["thoi_gian_du_doan"]
                ) if item.get("thoi_gian_du_doan") else None,
                "thoi_gian_chay": float(
                    item["thoi_gian_chay"]
                ) if item.get("thoi_gian_chay") is not None else None
            }
            for item in history
        ]
    }
# =========================
# KIỂM TRA ROUTE
# =========================

print("\n=== KIỂM TRA ROUTE ===")

for route in app.routes:
    if "history" in route.path:
        print(route.methods, route.path)