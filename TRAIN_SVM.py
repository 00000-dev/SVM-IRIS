from sklearn import datasets
from sklearn.model_selection import train_test_split # <-- Import hàm chia tập dữ liệu
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import joblib

# 1. Lấy dữ liệu
iris = datasets.load_iris()
X = iris.data
y = iris.target

# 2. CHIA DỮ LIỆU: 80% để học (X_train, y_train), 20% để thi thử (X_test, y_test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. Cho mô hình HỌC trên 80% dữ liệu
model = SVC(kernel="linear")
model.fit(X_train, y_train)

# 4. Cho mô hình "THI THỬ" trên 20% dữ liệu chưa từng thấy
y_pred = model.predict(X_test)

# 5. Tính xem máy đoán đúng bao nhiêu %
acc = accuracy_score(y_test, y_pred)
print(f"Độ chính xác thực tế của mô hình trên tập Test: {acc * 100:.2f}%")

# 6. Sau khi biết điểm OK rồi, em train lại trên toàn bộ 150 mẫu để lưu file pkl mang đi làm Web
final_model = SVC(kernel="linear")
final_model.fit(X, y)
joblib.dump(final_model, "svm_model.pkl")
print("Đã lưu mô hình hoàn chỉnh vào file svm_model.pkl!")
