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
