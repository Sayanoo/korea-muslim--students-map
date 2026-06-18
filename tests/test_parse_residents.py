import pandas as pd
from pipeline.parse_residents import parse_province_counts


def test_extracts_province_total_rows_only():
    df = pd.DataFrame([
        {"시도": "총합계", "시군구": None, "성별": "총계", "총합계": 100,
         "우즈베키스탄": 60, "몽골": 30, "베트남": 10},                       # national row -> excluded
        {"시도": "서울특별시", "시군구": "총계", "성별": "총계", "총합계": 50,
         "우즈베키스탄": 30, "몽골": 15, "베트남": 5},                        # province total
        {"시도": None, "시군구": "종로구", "성별": "총계", "총합계": 20,
         "우즈베키스탄": 10, "몽골": 5, "베트남": 5},                         # district -> excluded
        {"시도": "서울특별시", "시군구": "총계", "성별": "남성", "총합계": 30,
         "우즈베키스탄": 20, "몽골": 8, "베트남": 2},                         # gender split -> excluded
        {"시도": "경기도", "시군구": "총계", "성별": "총계", "총합계": 40,
         "우즈베키스탄": 25, "몽골": 10, "베트남": 5},
    ])
    out = parse_province_counts(df)
    assert set(out) == {"서울특별시", "경기도"}
    assert out["서울특별시"] == {"우즈베키스탄": 30, "몽골": 15, "베트남": 5}
    assert out["경기도"]["우즈베키스탄"] == 25
