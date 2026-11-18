# ============================================================
# CONFUSION MATRIX - IRIS BOTANICA AI
# ============================================================
# Mục đích:
# - Huấn luyện 3 mô hình trên cùng tập dữ liệu
# - Đánh giá trên cùng tập kiểm thử
# - Tạo 3 ảnh ma trận nhầm lẫn
# - Lưu ảnh vào thư mục charts/
#
# Mô hình:
# 1. SVM Linear
# 2. Logistic Regression
# 3. KNN
# ============================================================

from pathlib import Path

import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# 1. THƯ MỤC LƯU ẢNH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. TẢI DỮ LIỆU IRIS
# ============================================================

iris = datasets.load_iris()

X = iris.data
y = iris.target

class_names = iris.target_names


# ============================================================
# 3. CHIA DỮ LIỆU TRAIN / TEST
# ============================================================
# 80% dùng để huấn luyện
# 20% dùng để kiểm thử
# random_state = 42 để kết quả có thể tái lập
# stratify = y để giữ tỷ lệ các lớp

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("=" * 60)
print("THÔNG TIN TẬP DỮ LIỆU")
print("=" * 60)

print(f"Tổng số mẫu      : {len(X)}")
print(f"Tập huấn luyện   : {len(X_train)}")
print(f"Tập kiểm thử     : {len(X_test)}")


# ============================================================
# 4. KHAI BÁO CÁC MÔ HÌNH
# ============================================================

models = {

    "SVM Linear": SVC(
        kernel="linear"
    ),

    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        random_state=42
    ),

    "KNN": KNeighborsClassifier(
        n_neighbors=5
    )
}


# ============================================================
# 5. HUẤN LUYỆN + ĐÁNH GIÁ + TẠO MA TRẬN
# ============================================================

print("\n")
print("=" * 60)
print("KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH")
print("=" * 60)


for model_name, model in models.items():

    # --------------------------------------------------------
    # Huấn luyện
    # --------------------------------------------------------

    model.fit(X_train, y_train)

    # --------------------------------------------------------
    # Dự đoán trên tập kiểm thử
    # --------------------------------------------------------

    y_pred = model.predict(X_test)

    # --------------------------------------------------------
    # Tính các chỉ số đánh giá
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # In kết quả
    # --------------------------------------------------------

    print(f"\nMô hình: {model_name}")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")

    # --------------------------------------------------------
    # Tạo confusion matrix
    # --------------------------------------------------------

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    print("Confusion Matrix:")
    print(cm)

    # --------------------------------------------------------
    # Vẽ confusion matrix
    # --------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(6, 5)
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=class_names
    )

    display.plot(
        ax=ax,
        cmap="Blues",
        values_format="d",
        colorbar=False
    )

    ax.set_title(
        f"Confusion Matrix - {model_name}"
    )

    ax.set_xlabel(
        "Predicted Label"
    )

    ax.set_ylabel(
        "True Label"
    )

    plt.tight_layout()

    # --------------------------------------------------------
    # Tạo tên file
    # --------------------------------------------------------

    safe_name = (
        model_name
        .lower()
        .replace(" ", "_")
    )

    output_path = (
        OUTPUT_DIR /
        f"confusion_matrix_{safe_name}.png"
    )

    # --------------------------------------------------------
    # Lưu ảnh
    # --------------------------------------------------------

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Đã lưu: {output_path}"
    )


# ============================================================
# 6. HOÀN TẤT
# ============================================================

print("\n")
print("=" * 60)
print("HOÀN TẤT")
print("=" * 60)

print(
    "Đã tạo 3 ảnh confusion matrix trong thư mục charts/"
)