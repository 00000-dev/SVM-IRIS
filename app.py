from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import joblib
import time

from database.user import (
    username_exists,
    create_user,
    check_login,
    get_user_by_id
)

from database.history import (
    create_login_history,
    get_login_history
)

from database.prediction import (
    create_prediction_history,
    get_prediction_history,
    get_deleted_prediction_history,
    get_prediction_by_id,
    soft_delete_prediction_history,
    restore_prediction_history,
    permanently_delete_prediction_history,
    permanently_delete_all_prediction_history
)
from database.model import (
    get_model_evaluations
)

from database.model_history import (
    create_model_history,
    get_model_history
)
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
from zoneinfo import ZoneInfo

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
print("ROUTE DELETE TRASH:", any(
    route.path == "/model-history/trash"
    and "DELETE" in route.methods
    for route in app.routes
))
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
# LỊCH SỬ DỰ ĐOÁN
# =========================================================

@app.get("/model-history")
def model_history(request: Request):
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập để xem lịch sử dự đoán!"
        }

    history = get_prediction_history(ma_nguoi_dung)

    return {
        "success": True,
        "history": history
    }


# =========================================================
# THÙNG RÁC
# =========================================================

@app.get("/model-history/trash")
def model_history_trash(request: Request):
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

@app.delete("/model-history/trash")
async def permanently_delete_all_history(request: Request):

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

@app.get("/model-history/{ma_du_doan}")
def get_one_model_history(
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

@app.patch("/model-history/{ma_du_doan}/delete")
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

@app.patch("/model-history/{ma_du_doan}/restore")
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

@app.delete("/model-history/{ma_du_doan}")
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

@app.post("/predict-model")
def predict_model(
    data: PredictModelInput,
    request: Request
):

    # =========================
    # 1. KIỂM TRA ĐĂNG NHẬP
    # =========================

    ma_nguoi_dung = request.session.get(
        "ma_nguoi_dung"
    )

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập trước khi dự đoán!"
        }

    # =========================
    # 2. CHỌN MÔ HÌNH
    # =========================

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

    # =========================
    # 3. CHUẨN BỊ DỮ LIỆU
    # =========================

    features = [[
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width
    ]]

    # =========================
    # 4. CHẠY MÔ HÌNH
    # =========================

    start_time = time.perf_counter()

    prediction = int(
        selected_model.predict(features)[0]
    )

    end_time = time.perf_counter()

    execution_time = (
        end_time - start_time
    )

    # =========================
    # 5. LƯU LỊCH SỬ DỰ ĐOÁN
    # =========================

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

    # =========================
    # 6. TRẢ KẾT QUẢ
    # =========================

    return {
        "success": True,
        "class_id": prediction,
        "prediction": species[prediction],
        "model": data.model_name,
        "execution_time": execution_time
    }
# =========================
# 13. API ĐĂNG KÝ
# =========================

@app.post("/register")
def register(data: RegisterInput):

    # Kiểm tra tên đăng nhập
    if username_exists(data.ten_dang_nhap):
        return {
            "success": False,
            "message": "Tên đăng nhập đã tồn tại!"
        }

    # Tạo tài khoản
    create_user(
        data.ten_dang_nhap,
        data.mat_khau
    )

    return {
        "success": True,
        "message": "Đăng ký tài khoản thành công!"
    }
# =========================
# 14. API ĐĂNG NHẬP
# =========================

@app.post("/login")
def login(data: LoginInput, request: Request):

    user = check_login(
        data.ten_dang_nhap,
        data.mat_khau
    )

    if user is None:

        # Phân biệt tài khoản không tồn tại
        if not username_exists(data.ten_dang_nhap):
            return {
                "success": False,
                "message": "Tên đăng nhập không tồn tại!"
            }

        return {
            "success": False,
            "message": "Mật khẩu không đúng!"
        }

    # Lưu người dùng vào Session
    request.session["ma_nguoi_dung"] = user["ma_nguoi_dung"]

    # Ghi lịch sử đăng nhập
    create_login_history(
        user["ma_nguoi_dung"]
    )

    return {
        "success": True,
        "message": "Đăng nhập thành công!",
        "ma_nguoi_dung": user["ma_nguoi_dung"],
        "ten_dang_nhap": user["ten_dang_nhap"]
    }
# =========================
@app.get("/me")
def get_current_user(request: Request):

    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Chưa đăng nhập!"
        }

    user = get_user_by_id(ma_nguoi_dung)

    if user is None:
        request.session.clear()

        return {
            "success": False,
            "message": "Phiên đăng nhập không hợp lệ!"
        }

    return {
        "success": True,
        "ma_nguoi_dung": user["ma_nguoi_dung"],
        "ten_dang_nhap": user["ten_dang_nhap"],
        "ngay_tao": user["ngay_tao"]
    }
# 15. API KIỂM TRA NGƯỜI DÙNG
# =========================

@app.get("/user/{ma_nguoi_dung}")
def get_user(ma_nguoi_dung: int):

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
        "ngay_tao": user["ngay_tao"]
    }
# =========================
# 16. API LỊCH SỬ ĐĂNG NHẬP
# =========================

@app.get("/login-history/{ma_nguoi_dung}")
def get_login_history_api(ma_nguoi_dung: int):

    history = get_login_history(ma_nguoi_dung)

    return {
        "success": True,
        "history": [
            {
                "ma_dang_nhap": item["ma_dang_nhap"],
                "thoi_gian_dang_nhap": item["thoi_gian_dang_nhap"]
            }
            for item in history
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


@app.get("/prediction-history")
def prediction_history(request: Request):
    ma_nguoi_dung = request.session.get("ma_nguoi_dung")

    if ma_nguoi_dung is None:
        return {
            "success": False,
            "message": "Vui lòng đăng nhập để xem lịch sử dự đoán!"
        }

    history = get_prediction_history(ma_nguoi_dung)

    return {
        "success": True,
        "history": history
    }