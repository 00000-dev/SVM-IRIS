USE IrisBotanicaDB;
GO

INSERT INTO ket_qua_mo_hinh (
    ma_mo_hinh,
    accuracy,
    precision,
    recall,
    f1_score,
    thoi_gian_huan_luyen,
    thoi_gian_du_doan
)
VALUES
(
    1,
    1.0000,
    1.0000,
    1.0000,
    1.0000,
    0.008273,
    0.002062
),
(
    2,
    1.0000,
    1.0000,
    1.0000,
    1.0000,
    0.017877,
    0.000727
),
(
    3,
    0.9667,
    0.9697,
    0.9667,
    0.9666,
    0.005230,
    0.009872
);
GO
SELECT * FROM ket_qua_mo_hinh;