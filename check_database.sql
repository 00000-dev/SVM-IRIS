USE IrisBotanicaDB;
GO

-- Chỉ tạo bảng nếu bảng chưa tồn tại
IF OBJECT_ID(N'dbo.nguoi_dung', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.nguoi_dung (
        ma_nguoi_dung INT IDENTITY(1,1) PRIMARY KEY,
        ten_dang_nhap VARCHAR(50) NOT NULL UNIQUE,
        mat_khau VARCHAR(255) NOT NULL,
        ngay_tao DATETIME NOT NULL DEFAULT GETDATE(),
        trang_thai BIT NOT NULL DEFAULT 1
    );
END;
GO

-- Thêm cột vai_tro nếu chưa có
IF COL_LENGTH(N'dbo.nguoi_dung', N'vai_tro') IS NULL
BEGIN
    ALTER TABLE dbo.nguoi_dung
    ADD vai_tro NVARCHAR(20) NOT NULL
        CONSTRAINT DF_nguoi_dung_vai_tro DEFAULT N'user';
END;
GO

-- Kiểm tra các cột hiện có
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = N'nguoi_dung'
ORDER BY ORDINAL_POSITION;

-- Kiểm tra dữ liệu tài khoản
SELECT ma_nguoi_dung, ten_dang_nhap, vai_tro
FROM dbo.nguoi_dung;