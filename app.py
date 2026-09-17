from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import joblib


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


# =========================
# 3. FASTAPI APP
# =========================

app = FastAPI(
    title="Iris Classification API",
    description="SVM model for the Iris dataset",
    version="1.0.0",
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


# =========================
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
# 10. HEALTH CHECK
# =========================

@app.get("/health")
def health():
    return {"status": "healthy"}


# =========================
# 11. DỰ ĐOÁN
# =========================

@app.post("/predict")
def predict(data: IrisInput):

    features = [[
        data.sepal_length,
        data.sepal_width,
        data.petal_length,
        data.petal_width,
    ]]

    prediction = int(model.predict(features)[0])

    return {
        "class_id": prediction,
        "prediction": species[prediction],
    }