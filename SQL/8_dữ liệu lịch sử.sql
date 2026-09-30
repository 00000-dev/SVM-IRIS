USE IrisBotanicaDB;
GO

-- Thời gian thực hiện dự đoán
ALTER TABLE lich_su_du_doan
ADD thoi_gian_du_doan DATETIME NOT NULL
    CONSTRAINT DF_lich_su_du_doan_thoi_gian
    DEFAULT GETDATE();
GO

-- Đánh dấu lịch sử đã xóa
ALTER TABLE lich_su_du_doan
ADD da_xoa BIT NOT NULL
    CONSTRAINT DF_lich_su_du_doan_da_xoa
    DEFAULT 0;
GO

SELECT *
FROM lich_su_du_doan
ORDER BY ma_du_doan DESC;