USE IrisBotanicaDB;
GO

CREATE TABLE mo_hinh (
    ma_mo_hinh INT IDENTITY(1,1) PRIMARY KEY,
    ten_mo_hinh VARCHAR(50) NOT NULL UNIQUE,
    loai_mo_hinh VARCHAR(50),
    mo_ta VARCHAR(255),
    trang_thai BIT NOT NULL DEFAULT 1
);
GO