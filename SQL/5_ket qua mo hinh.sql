USE IrisBotanicaDB;
GO

CREATE TABLE ket_qua_mo_hinh (
    ma_ket_qua INT IDENTITY(1,1) PRIMARY KEY,
    ma_mo_hinh INT NOT NULL,
    accuracy FLOAT NOT NULL,
    precision FLOAT NOT NULL,
    recall FLOAT NOT NULL,
    f1_score FLOAT NOT NULL,
    thoi_gian_huan_luyen FLOAT,
    thoi_gian_du_doan FLOAT,

    CONSTRAINT FK_ket_qua_mo_hinh_mo_hinh
        FOREIGN KEY (ma_mo_hinh)
        REFERENCES mo_hinh(ma_mo_hinh)
);
GO