from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import matplotlib.pyplot as plt
import numpy as np


# =========================================================
# 1. LOAD DATASET IRIS
# =========================================================

iris = datasets.load_iris()

X = iris.data
y = iris.target

feature_names = iris.feature_names
target_names = iris.target_names


# =========================================================
# 2. CHỌN 2 ĐẶC TRƯNG ĐỂ MINH HỌA
#    Petal Length + Petal Width
# =========================================================

X_visual = X[:, [2, 3]]


# =========================================================
# 3. CHIA TRAIN / TEST
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X_visual,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# =========================================================
# 4. HUẤN LUYỆN SVM KERNEL TUYẾN TÍNH
# =========================================================

model = SVC(
    kernel="linear",
    C=1.0
)

model.fit(X_train, y_train)


# =========================================================
# 5. TẠO LƯỚI ĐIỂM ĐỂ VẼ VÙNG PHÂN LOẠI
# =========================================================

x_min = X_visual[:, 0].min() - 0.5
x_max = X_visual[:, 0].max() + 0.5

y_min = X_visual[:, 1].min() - 0.5
y_max = X_visual[:, 1].max() + 0.5

xx, yy = np.meshgrid(
    np.linspace(x_min, x_max, 500),
    np.linspace(y_min, y_max, 500)
)


# =========================================================
# 6. DỰ ĐOÁN TRÊN TOÀN BỘ LƯỚI
# =========================================================

grid = np.c_[xx.ravel(), yy.ravel()]

Z = model.predict(grid)

Z = Z.reshape(xx.shape)


# =========================================================
# 7. VẼ ĐƯỜNG PHÂN CHIA TUYẾN TÍNH
# =========================================================

plt.figure(figsize=(10, 7))

plt.contourf(
    xx,
    yy,
    Z,
    alpha=0.15
)


# =========================================================
# 8. VẼ DỮ LIỆU IRIS
# =========================================================

colors = ["red", "green", "blue"]

for class_id, class_name in enumerate(target_names):

    plt.scatter(
        X_visual[y == class_id, 0],
        X_visual[y == class_id, 1],
        label=class_name,
        alpha=0.8
    )


# =========================================================
# 9. VẼ SUPPORT VECTORS
# =========================================================

plt.scatter(
    model.support_vectors_[:, 0],
    model.support_vectors_[:, 1],
    s=120,
    facecolors="none",
    edgecolors="black",
    linewidths=1.5,
    label="Support Vectors"
)


# =========================================================
# 10. TIÊU ĐỀ VÀ NHÃN
# =========================================================

plt.xlabel("Petal Length (cm)")
plt.ylabel("Petal Width (cm)")

plt.title(
    "Linear SVM Decision Boundary trên tập dữ liệu Iris"
)

plt.legend()
plt.grid(alpha=0.25)


# =========================================================
# 11. LƯU HÌNH
# =========================================================

plt.tight_layout()

plt.savefig(
    "linear_decision_boundary.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()