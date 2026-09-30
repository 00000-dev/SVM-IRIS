# ==========================================
# ĐÁNH GIÁ CÁC MÔ HÌNH PHÂN LOẠI HOA IRIS
# ==========================================

from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

import time
import joblib


# ==========================================
# 1. LẤY DỮ LIỆU IRIS
# ==========================================

iris = datasets.load_iris()

X = iris.data
y = iris.target


# ==========================================
# 2. CHIA DỮ LIỆU TRAIN VÀ TEST
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


print("Số mẫu dùng để huấn luyện:", len(X_train))
print("Số mẫu dùng để kiểm tra:", len(X_test))
# ==========================================
# 3. KHỞI TẠO 3 MÔ HÌNH
# ==========================================

# Mô hình 1: SVM với đường phân chia tuyến tính
svm_model = SVC(kernel="linear")

# Mô hình 2: LDA
lda_model = LinearDiscriminantAnalysis()

# Mô hình 3: KNN
# Sử dụng 15 láng giềng để thử nghiệm khả năng phân loại
knn_model = KNeighborsClassifier(n_neighbors=15)


models = {
    "SVM": svm_model,
    "LDA": lda_model,
    "KNN": knn_model
}


print("\nĐã khởi tạo 3 mô hình:")
for model_name in models:
    print("-", model_name)
# ==========================================
# 4. HUẤN LUYỆN VÀ ĐÁNH GIÁ 3 MÔ HÌNH
# ==========================================

results = {}

for model_name, model in models.items():

    print(f"\nĐang huấn luyện mô hình: {model_name}")

    # --------------------------------------
    # Đo thời gian huấn luyện
    # --------------------------------------
    start_train = time.perf_counter()

    model.fit(X_train, y_train)

    end_train = time.perf_counter()

    training_time = end_train - start_train

    # --------------------------------------
    # Đo thời gian dự đoán
    # --------------------------------------
    start_predict = time.perf_counter()

    y_pred = model.predict(X_test)

    end_predict = time.perf_counter()

    prediction_time = end_predict - start_predict

    # --------------------------------------
    # Tính các chỉ số đánh giá
    # --------------------------------------
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

    # --------------------------------------
    # Lưu kết quả
    # --------------------------------------
    results[model_name] = {
        "model": model,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "training_time": training_time,
        "prediction_time": prediction_time
    }

    print(f"Accuracy:  {accuracy * 100:.2f}%")
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall:    {recall * 100:.2f}%")
    print(f"F1-score:  {f1 * 100:.2f}%")
    print(f"Thời gian huấn luyện: {training_time:.6f} giây")
    print(f"Thời gian dự đoán:    {prediction_time:.6f} giây")
    
# 5. HUẤN LUYỆN LẠI TRÊN TOÀN BỘ DỮ LIỆU
# ==========================================

print("\n==========================================")
print("HUẤN LUYỆN LẠI TRÊN TOÀN BỘ 150 MẪU")
print("==========================================")

# Huấn luyện lại SVM trên toàn bộ dữ liệu Iris
final_svm = SVC(kernel="linear")
final_svm.fit(X, y)

# Huấn luyện lại LDA trên toàn bộ dữ liệu Iris
final_lda = LinearDiscriminantAnalysis()
final_lda.fit(X, y)

# Huấn luyện lại KNN trên toàn bộ dữ liệu Iris
final_knn = KNeighborsClassifier(n_neighbors=15)
final_knn.fit(X, y)

# ==========================================
# 6. LƯU CÁC MÔ HÌNH ĐỂ SỬ DỤNG TRÊN WEB
# ==========================================

joblib.dump(final_svm, "svm_model.pkl")
joblib.dump(final_lda, "lda_model.pkl")
joblib.dump(final_knn, "knn_model.pkl")


print("\nĐã lưu các mô hình:")
print("- svm_model.pkl")
print("- lda_model.pkl")
print("- knn_model.pkl")
