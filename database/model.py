from sqlalchemy import text
from database.connection import engine


def get_model_evaluations():
    sql = text("""
        SELECT
            m.ma_mo_hinh,
            m.ten_mo_hinh,
            m.loai_mo_hinh,
            m.mo_ta,
            m.trang_thai,
            k.accuracy,
            k.precision,
            k.recall,
            k.f1_score,
            k.thoi_gian_huan_luyen,
            k.thoi_gian_du_doan
        FROM mo_hinh AS m
        INNER JOIN ket_qua_mo_hinh AS k
            ON m.ma_mo_hinh = k.ma_mo_hinh
        WHERE m.trang_thai = TRUE
        ORDER BY m.ma_mo_hinh
    """)

    with engine.connect() as connection:
        result = connection.execute(sql)

        models = []

        for row in result:
            models.append({
                "ma_mo_hinh": row.ma_mo_hinh,
                "ten_mo_hinh": row.ten_mo_hinh,
                "loai_mo_hinh": row.loai_mo_hinh,
                "mo_ta": row.mo_ta,
                "trang_thai": row.trang_thai,
                "accuracy": row.accuracy,
                "precision": row.precision,
                "recall": row.recall,
                "f1_score": row.f1_score,
                "thoi_gian_huan_luyen": row.thoi_gian_huan_luyen,
                "thoi_gian_du_doan": row.thoi_gian_du_doan
            })

        return models