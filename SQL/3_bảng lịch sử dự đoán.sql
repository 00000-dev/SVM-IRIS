USE IrisBotanicaDB;
GO

CREATE TABLE lich_su_du_doan (
    ma_du_doan INT IDENTITY(1,1) PRIMARY KEY,
    ma_nguoi_dung INT NOT NULL,

    sepal_length FLOAT NOT NULL,
    sepal_width FLOAT NOT NULL,
    petal_length FLOAT NOT NULL,
    petal_width FLOAT NOT NULL,

    ket_qua INT NOT NULL,
    ten_mo_hinh VARCHAR(20) NOT NULL,
    thoi_gian_chay FLOAT NOT NULL,

    CONSTRAINT FK_lich_su_du_doan_nguoi_dung
        FOREIGN KEY (ma_nguoi_dung)
        REFERENCES nguoi_dung(ma_nguoi_dung)
);
GO