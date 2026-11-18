
# =========================================================
# ĐÁNH GIÁ 4 KERNEL SVM, LDA VÀ KNN - IRIS BOTANICA AI
# =========================================================

from pathlib import Path
import time
import joblib

from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

from sqlalchemy import text
from database.connection import engine


# =========================================================
# 1. ĐƯỜNG DẪN LƯU MÔ HÌNH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent


# =========================================================
# 2. LẤY DỮ LIỆU IRIS
# =========================================================

iris = datasets.load_iris()

X = iris.data
y = iris.target


# =========================================================
# 3. CHIA DỮ LIỆU TRAIN VÀ TEST
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("Số mẫu huấn luyện:", len(X_train))
print("Số mẫu kiểm tra:", len(X_test))


# =========================================================
# 4. KHỞI TẠO 6 MÔ HÌNH
# =========================================================

models = {

    # 4 kernel SVM
    "SVM": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", SVC(kernel="linear"))
    ]),

    "SVM_RBF": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", SVC(kernel="rbf"))
    ]),

    "SVM_POLY": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", SVC(kernel="poly", degree=3))
    ]),

    "SVM_SIGMOID": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", SVC(kernel="sigmoid"))
    ]),

    # Giữ nguyên LDA và KNN
    "LDA": LinearDiscriminantAnalysis(),

    "KNN": KNeighborsClassifier(n_neighbors=15)
}


print("\nĐã khởi tạo 6 mô hình:")

for name in models:
    print("-", name)


# =========================================================
# 5. HUẤN LUYỆN VÀ ĐÁNH GIÁ
# =========================================================

results = {}

for model_name, model in models.items():

    print(f"\nĐang đánh giá: {model_name}")

    # Đo thời gian huấn luyện
    start_train = time.perf_counter()

    model.fit(X_train, y_train)

    training_time = time.perf_counter() - start_train

    # Đo thời gian dự đoán
    start_predict = time.perf_counter()

    y_pred = model.predict(X_test)

    prediction_time = time.perf_counter() - start_predict

    # Tính các chỉ số
    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    results[model_name] = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "training_time": float(training_time),
        "prediction_time": float(prediction_time)
    }

    print(f"Accuracy:  {accuracy * 100:.2f}%")
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall:    {recall * 100:.2f}%")
    print(f"F1-score:  {f1 * 100:.2f}%")
    print(f"Thời gian huấn luyện: {training_time:.6f} giây")
    print(f"Thời gian dự đoán: {prediction_time:.6f} giây")


# =========================================================
# 6. HUẤN LUYỆN LẠI TRÊN TOÀN BỘ 150 MẪU
# =========================================================

print("\n========================================")
print("HUẤN LUYỆN MÔ HÌNH CUỐI CÙNG")
print("========================================")

final_models = {}

for model_name, model in models.items():

    print(f"Đang huấn luyện toàn bộ dữ liệu: {model_name}")

    model.fit(X, y)

    final_models[model_name] = model


# =========================================================
# 7. LƯU 6 FILE MÔ HÌNH
# =========================================================

model_files = {
    "SVM": "svm_model.pkl",
    "SVM_RBF": "svm_rbf_model.pkl",
    "SVM_POLY": "svm_poly_model.pkl",
    "SVM_SIGMOID": "svm_sigmoid_model.pkl",
    "LDA": "lda_model.pkl",
    "KNN": "knn_model.pkl"
}

for model_name, filename in model_files.items():

    file_path = BASE_DIR / filename

    joblib.dump(final_models[model_name], file_path)

    print("Đã lưu:", filename)


# =========================================================
# 8. LƯU THÔNG TIN VÀ KẾT QUẢ VÀO POSTGRESQL
# =========================================================

model_descriptions = {

    "SVM": (
        "SVM",
        "Phân loại hoa Iris bằng SVM với kernel tuyến tính."
    ),

    "SVM_RBF": (
        "SVM",
        "Phân loại hoa Iris bằng SVM với kernel RBF."
    ),

    "SVM_POLY": (
        "SVM",
        "Phân loại hoa Iris bằng SVM với kernel Polynomial bậc 3."
    ),

    "SVM_SIGMOID": (
        "SVM",
        "Phân loại hoa Iris bằng SVM với kernel Sigmoid."
    ),

    "LDA": (
        "LDA",
        "Phân loại hoa Iris bằng Linear Discriminant Analysis."
    ),

    "KNN": (
        "KNN",
        "Phân loại hoa Iris bằng K-Nearest Neighbors với k=15."
    )
}


with engine.begin() as connection:

    for model_name, result in results.items():

        loai_mo_hinh, mo_ta = model_descriptions[model_name]

        # Tạo mô hình nếu chưa tồn tại.
        # Nếu đã có thì giữ nguyên mã mô hình.
        model_id = connection.execute(
            text("""
                INSERT INTO mo_hinh (
                    ten_mo_hinh,
                    loai_mo_hinh,
                    mo_ta,
                    trang_thai
                )
                VALUES (
                    :ten_mo_hinh,
                    :loai_mo_hinh,
                    :mo_ta,
                    TRUE
                )
                ON CONFLICT (ten_mo_hinh)
                DO UPDATE SET
                    loai_mo_hinh = EXCLUDED.loai_mo_hinh,
                    mo_ta = EXCLUDED.mo_ta,
                    trang_thai = TRUE
                RETURNING ma_mo_hinh
            """),
            {
                "ten_mo_hinh": model_name,
                "loai_mo_hinh": loai_mo_hinh,
                "mo_ta": mo_ta
            }
        ).scalar_one()

               # Thêm kết quả đánh giá mới vào lịch sử
        connection.execute(
            text("""
                INSERT INTO ket_qua_mo_hinh (
                    ma_mo_hinh,
                    accuracy,
                    precision,
                    recall,
                    f1_score,
                    thoi_gian_huan_luyen,
                    thoi_gian_du_doan
                )
                VALUES (
                    :ma_mo_hinh,
                    :accuracy,
                    :precision,
                    :recall,
                    :f1_score,
                    :thoi_gian_huan_luyen,
                    :thoi_gian_du_doan
                )
            """),
            {
                "ma_mo_hinh": model_id,
                "accuracy": result["accuracy"],
                "precision": result["precision"],
                "recall": result["recall"],
                "f1_score": result["f1"],
                "thoi_gian_huan_luyen": result["training_time"],
                "thoi_gian_du_doan": result["prediction_time"]
            }
        )

        print(f"Đã lưu kết quả đánh giá: {model_name}")


print("\n========================================")
print("HOÀN TẤT HUẤN LUYỆN VÀ ĐÁNH GIÁ")
print("========================================")
print("Tổng số mô hình:", len(results))
print("Đã lưu 6 file PKL.")
print("Đã cập nhật kết quả vào PostgreSQL.")
