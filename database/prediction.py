from sqlalchemy import text
from database.connection import engine


# =========================================================
# 1. LƯU LỊCH SỬ DỰ ĐOÁN
# =========================================================

def create_prediction_history(
    ma_nguoi_dung,
    sepal_length,
    sepal_width,
    petal_length,
    petal_width,
    ket_qua,
    ten_mo_hinh,
    thoi_gian_chay
):
    sql = text("""
        INSERT INTO lich_su_du_doan (
            ma_nguoi_dung,
            sepal_length,
            sepal_width,
            petal_length,
            petal_width,
            ket_qua,
            ten_mo_hinh,
            thoi_gian_chay
        )
        VALUES (
            :ma_nguoi_dung,
            :sepal_length,
            :sepal_width,
            :petal_length,
            :petal_width,
            :ket_qua,
            :ten_mo_hinh,
            :thoi_gian_chay
        )
    """)

    with engine.begin() as connection:
        result = connection.execute(
            sql,
            {
                "ma_nguoi_dung": ma_nguoi_dung,
                "sepal_length": sepal_length,
                "sepal_width": sepal_width,
                "petal_length": petal_length,
                "petal_width": petal_width,
                "ket_qua": ket_qua,
                "ten_mo_hinh": ten_mo_hinh,
                "thoi_gian_chay": thoi_gian_chay
            }
        )

        return result.rowcount > 0


# =========================================================
# 2. LẤY LỊCH SỬ ĐANG HOẠT ĐỘNG
# =========================================================

def get_prediction_history(ma_nguoi_dung):
    sql = text("""
        SELECT
            l.ma_du_doan,
            l.ma_nguoi_dung,
            n.ten_dang_nhap,
            l.sepal_length,
            l.sepal_width,
            l.petal_length,
            l.petal_width,
            l.ket_qua,
            l.ten_mo_hinh,
            l.thoi_gian_chay,
            l.thoi_gian_du_doan,
            l.da_xoa
        FROM lich_su_du_doan AS l
        INNER JOIN nguoi_dung AS n
            ON l.ma_nguoi_dung = n.ma_nguoi_dung
        WHERE l.ma_nguoi_dung = :ma_nguoi_dung
          AND l.da_xoa = :da_xoa
        ORDER BY l.thoi_gian_du_doan DESC
    """)

    with engine.connect() as connection:
        result = connection.execute(
            sql,
            {
                "ma_nguoi_dung": ma_nguoi_dung,
                "da_xoa": False
            }
        )

        history = []

        for row in result:
            history.append({
                "ma_du_doan": row.ma_du_doan,
                "ma_nguoi_dung": row.ma_nguoi_dung,
                "ten_dang_nhap": row.ten_dang_nhap,
                "sepal_length": row.sepal_length,
                "sepal_width": row.sepal_width,
                "petal_length": row.petal_length,
                "petal_width": row.petal_width,
                "ket_qua": row.ket_qua,
                "ten_mo_hinh": row.ten_mo_hinh,
                "thoi_gian_chay": row.thoi_gian_chay,
                "thoi_gian_du_doan": row.thoi_gian_du_doan,
                "da_xoa": row.da_xoa
            })

        return history


# =========================================================
# 3. LẤY THÙNG RÁC
# =========================================================

def get_deleted_prediction_history(ma_nguoi_dung):
    sql = text("""
        SELECT
            l.ma_du_doan,
            l.ma_nguoi_dung,
            n.ten_dang_nhap,
            l.sepal_length,
            l.sepal_width,
            l.petal_length,
            l.petal_width,
            l.ket_qua,
            l.ten_mo_hinh,
            l.thoi_gian_chay,
            l.thoi_gian_du_doan,
            l.da_xoa
        FROM lich_su_du_doan AS l
        INNER JOIN nguoi_dung AS n
            ON l.ma_nguoi_dung = n.ma_nguoi_dung
        WHERE l.ma_nguoi_dung = :ma_nguoi_dung
          AND l.da_xoa = :da_xoa
        ORDER BY l.thoi_gian_du_doan DESC
    """)

    with engine.connect() as connection:
        result = connection.execute(
            sql,
            {
                "ma_nguoi_dung": ma_nguoi_dung,
                "da_xoa": True
            }
        )

        history = []

        for row in result:
            history.append({
                "ma_du_doan": row.ma_du_doan,
                "ma_nguoi_dung": row.ma_nguoi_dung,
                "ten_dang_nhap": row.ten_dang_nhap,
                "sepal_length": row.sepal_length,
                "sepal_width": row.sepal_width,
                "petal_length": row.petal_length,
                "petal_width": row.petal_width,
                "ket_qua": row.ket_qua,
                "ten_mo_hinh": row.ten_mo_hinh,
                "thoi_gian_chay": row.thoi_gian_chay,
                "thoi_gian_du_doan": row.thoi_gian_du_doan,
                "da_xoa": row.da_xoa
            })

        return history


# =========================================================
# 4. LẤY 1 LỊCH SỬ ĐỂ MỞ LẠI
# =========================================================

def get_prediction_by_id(ma_du_doan, ma_nguoi_dung):
    sql = text("""
        SELECT
            ma_du_doan,
            ma_nguoi_dung,
            sepal_length,
            sepal_width,
            petal_length,
            petal_width,
            ket_qua,
            ten_mo_hinh,
            thoi_gian_chay,
            thoi_gian_du_doan
        FROM lich_su_du_doan
        WHERE ma_du_doan = :ma_du_doan
          AND ma_nguoi_dung = :ma_nguoi_dung
          AND da_xoa = :da_xoa
    """)

    with engine.connect() as connection:
        row = connection.execute(
            sql,
            {
                "ma_du_doan": ma_du_doan,
                "ma_nguoi_dung": ma_nguoi_dung,
                "da_xoa": False
            }
        ).fetchone()

        if row is None:
            return None

        return {
            "ma_du_doan": row.ma_du_doan,
            "ma_nguoi_dung": row.ma_nguoi_dung,
            "sepal_length": row.sepal_length,
            "sepal_width": row.sepal_width,
            "petal_length": row.petal_length,
            "petal_width": row.petal_width,
            "ket_qua": row.ket_qua,
            "ten_mo_hinh": row.ten_mo_hinh,
            "thoi_gian_chay": row.thoi_gian_chay,
            "thoi_gian_du_doan": row.thoi_gian_du_doan
        }


# =========================================================
# 5. ĐƯA VÀO THÙNG RÁC
# =========================================================

def soft_delete_prediction_history(ma_du_doan, ma_nguoi_dung):
    sql = text("""
        UPDATE lich_su_du_doan
        SET da_xoa = :da_xoa
        WHERE ma_du_doan = :ma_du_doan
          AND ma_nguoi_dung = :ma_nguoi_dung
          AND da_xoa = :da_xoa_hien_tai
    """)

    with engine.begin() as connection:
        result = connection.execute(
            sql,
            {
                "ma_du_doan": ma_du_doan,
                "ma_nguoi_dung": ma_nguoi_dung,
                "da_xoa": True,
                "da_xoa_hien_tai": False
            }
        )

        return result.rowcount > 0


# =========================================================
# 6. KHÔI PHỤC
# =========================================================

def restore_prediction_history(ma_du_doan, ma_nguoi_dung):
    sql = text("""
        UPDATE lich_su_du_doan
        SET da_xoa = :da_xoa
        WHERE ma_du_doan = :ma_du_doan
          AND ma_nguoi_dung = :ma_nguoi_dung
          AND da_xoa = :da_xoa_hien_tai
    """)

    with engine.begin() as connection:
        result = connection.execute(
            sql,
            {
                "ma_du_doan": ma_du_doan,
                "ma_nguoi_dung": ma_nguoi_dung,
                "da_xoa": False,
                "da_xoa_hien_tai": True
            }
        )

        return result.rowcount > 0


# =========================================================
# 7. XÓA VĨNH VIỄN 1 LỊCH SỬ
# =========================================================

def permanently_delete_prediction_history(ma_du_doan, ma_nguoi_dung):
    sql = text("""
        DELETE FROM lich_su_du_doan
        WHERE ma_du_doan = :ma_du_doan
          AND ma_nguoi_dung = :ma_nguoi_dung
          AND da_xoa = :da_xoa
    """)

    with engine.begin() as connection:
        result = connection.execute(
            sql,
            {
                "ma_du_doan": ma_du_doan,
                "ma_nguoi_dung": ma_nguoi_dung,
                "da_xoa": True
            }
        )

        return result.rowcount > 0


# =========================================================
# 8. XÓA VĨNH VIỄN TOÀN BỘ THÙNG RÁC
# =========================================================

def permanently_delete_all_prediction_history(ma_nguoi_dung):
    sql = text("""
        DELETE FROM lich_su_du_doan
        WHERE ma_nguoi_dung = :ma_nguoi_dung
          AND da_xoa = :da_xoa
    """)

    with engine.begin() as connection:
        result = connection.execute(
            sql,
            {
                "ma_nguoi_dung": ma_nguoi_dung,
                "da_xoa": True
            }
        )

        return result.rowcount
