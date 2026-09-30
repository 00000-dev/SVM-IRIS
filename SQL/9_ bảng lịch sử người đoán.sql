USE IrisBotanicaDB;
GO

ALTER TABLE lich_su_du_doan
ADD thoi_gian_du_doan DATETIME NOT NULL
    CONSTRAINT DF_lich_su_du_doan_thoi_gian
    DEFAULT GETDATE();
GO

ALTER TABLE lich_su_du_doan
ADD da_xoa BIT NOT NULL
    CONSTRAINT DF_lich_su_du_doan_da_xoa
    DEFAULT 0;
GO

SELECT
    ma_du_doan,
    ma_nguoi_dung,
    ket_qua,
    ten_mo_hinh,
    thoi_gian_chay,
    thoi_gian_du_doan,
    da_xoa
FROM lich_su_du_doan;