USE IrisBotanicaDB;
GO

CREATE TABLE lich_su_mo_hinh (
    ma_lich_su INT IDENTITY(1,1) PRIMARY KEY,
    ma_mo_hinh INT NOT NULL,
    accuracy FLOAT NOT NULL,
    precision FLOAT NOT NULL,
    recall FLOAT NOT NULL,
    f1_score FLOAT NOT NULL,
    thoi_gian_huan_luyen FLOAT,
    thoi_gian_du_doan FLOAT,
    thoi_gian_chay DATETIME NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_lich_su_mo_hinh_mo_hinh
        FOREIGN KEY (ma_mo_hinh)
        REFERENCES mo_hinh(ma_mo_hinh)
);
GO