USE IrisBotanicaDB;
GO
CREATE TABLE nguoi_dung (
    ma_nguoi_dung INT IDENTITY(1,1) PRIMARY KEY,
    ten_dang_nhap VARCHAR(50) NOT NULL UNIQUE,
    mat_khau VARCHAR(255) NOT NULL,
    ngay_tao DATETIME NOT NULL DEFAULT GETDATE(),
    trang_thai BIT NOT NULL DEFAULT 1
);
GO
IF COL_LENGTH('dbo.nguoi_dung', 'vai_tro') IS NULL
BEGIN
    ALTER TABLE dbo.nguoi_dung
    ADD vai_tro NVARCHAR(20) NOT NULL
        CONSTRAINT DF_nguoi_dung_vai_tro
        DEFAULT N'user';
END;

UPDATE dbo.nguoi_dung
SET vai_tro = N'admin'
WHERE ten_dang_nhap = N'NguyenThiThanhThao';
SELECT ten_dang_nhap, vai_tro, trang_thai
FROM dbo.nguoi_dung;