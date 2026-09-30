USE IrisBotanicaDB;
GO
CREATE TABLE lich_su_dang_nhap (
    ma_dang_nhap INT IDENTITY(1,1) PRIMARY KEY,
    ma_nguoi_dung INT NOT NULL,
    thoi_gian_dang_nhap DATETIME NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_lich_su_dang_nhap_nguoi_dung
        FOREIGN KEY (ma_nguoi_dung)
        REFERENCES nguoi_dung(ma_nguoi_dung)
);
GO