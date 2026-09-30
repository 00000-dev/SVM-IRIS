USE IrisBotanicaDB;
GO

INSERT INTO mo_hinh (
    ten_mo_hinh,
    loai_mo_hinh,
    mo_ta,
    trang_thai
)
VALUES
(
    'SVM',
    'Supervised Learning',
    'Phan loai hoa Iris bang Support Vector Machine voi kernel tuyen tinh.',
    1
),
(
    'LDA',
    'Supervised Learning',
    'Phan loai hoa Iris bang Linear Discriminant Analysis.',
    1
),
(
    'KNN',
    'Supervised Learning',
    'Phan loai hoa Iris bang K-Nearest Neighbors.',
    1
);
GO

SELECT * FROM mo_hinh;