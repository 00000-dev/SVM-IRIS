from sqlalchemy import text
from database.connection import engine


def create_model_history(
    ma_mo_hinh,
    accuracy,
    precision,
    recall,
    f1_score,
    thoi_gian_huan_luyen,
    thoi_gian_du_doan
):
    sql = text("""
        INSERT INTO lich_su_mo_hinh (
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
    """)

    with engine.begin() as connection:
        result = connection.execute(
            sql,
            {
                "ma_mo_hinh": ma_mo_hinh,
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "thoi_gian_huan_luyen": thoi_gian_huan_luyen,
                "thoi_gian_du_doan": thoi_gian_du_doan
            }
        )

        return result.rowcount > 0


def get_model_history():
    sql = text("""
        SELECT
            l.ma_lich_su,
            m.ten_mo_hinh,
            m.loai_mo_hinh,
            l.accuracy,
            l.precision,
            l.recall,
            l.f1_score,
            l.thoi_gian_huan_luyen,
            l.thoi_gian_du_doan,
            l.thoi_gian_chay
        FROM lich_su_mo_hinh AS l
        INNER JOIN mo_hinh AS m
            ON l.ma_mo_hinh = m.ma_mo_hinh
        ORDER BY l.thoi_gian_chay DESC
    """)

    with engine.connect() as connection:
        result = connection.execute(sql)

        history = []

        for row in result:
            history.append({
                "ma_lich_su": row.ma_lich_su,
                "ten_mo_hinh": row.ten_mo_hinh,
                "loai_mo_hinh": row.loai_mo_hinh,
                "accuracy": row.accuracy,
                "precision": row.precision,
                "recall": row.recall,
                "f1_score": row.f1_score,
                "thoi_gian_huan_luyen": row.thoi_gian_huan_luyen,
                "thoi_gian_du_doan": row.thoi_gian_du_doan,
                "thoi_gian_chay": row.thoi_gian_chay
            })

        return history