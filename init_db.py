from database import get_connection


conn = get_connection()

cursor = conn.cursor()


# ==========================================
# 1. BẢNG NGƯỜI DÙNG
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS nguoi_dung (
    ma_nguoi_dung INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_dang_nhap TEXT NOT NULL UNIQUE,
    mat_khau TEXT NOT NULL,
    ngay_tao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


# ==========================================
# 2. BẢNG LỊCH SỬ ĐĂNG NHẬP
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS lich_su_dang_nhap (
    ma_dang_nhap INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nguoi_dung INTEGER NOT NULL,
    thoi_gian_dang_nhap TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ma_nguoi_dung)
    REFERENCES nguoi_dung(ma_nguoi_dung)
)
""")
# ==========================================
# 3. BẢNG LỊCH SỬ DỰ ĐOÁN
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS lich_su_du_doan (
    ma_du_doan INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_nguoi_dung INTEGER NOT NULL,

    sepal_length REAL NOT NULL,
    sepal_width REAL NOT NULL,
    petal_length REAL NOT NULL,
    petal_width REAL NOT NULL,

    ket_qua INTEGER NOT NULL,
    ten_mo_hinh TEXT NOT NULL,
    thoi_gian_chay REAL,

    thoi_gian_du_doan TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ma_nguoi_dung)
    REFERENCES nguoi_dung(ma_nguoi_dung)
)
""")


conn.commit()
conn.close()

print("Da tao CSDL va cac bang thanh cong!")