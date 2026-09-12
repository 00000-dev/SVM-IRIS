import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

# 1. Đọc dữ liệu từ file Iris.csv
df = pd.read_csv('Iris.csv')

# 2. Bỏ cột Id (nếu có) và tách cột nhãn Species
if 'Id' in df.columns:
    X = df.drop(columns=['Id', 'Species'])
else:
    X = df.drop(columns=['Species'])

y = df['Species']

# 3. Chia tập train / test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Huấn luyện mô hình SVM
model = SVC(kernel='linear')
model.fit(X_train, y_train)

# 5. Lưu thành file svm_model.pkl
joblib.dump(model, 'svm_model.pkl')
print('Model saved!')