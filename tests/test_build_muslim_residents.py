from pipeline.build_muslim_residents import build_region_residents

GEO = {"features": [
    {"properties": {"code": "11", "name": "서울특별시", "name_eng": "Seoul"}},
    {"properties": {"code": "32", "name": "강원도", "name_eng": "Gangwon-do"}},
]}


def test_builds_region_records_with_mongolia_last_and_alias():
    province_counts = {
        "서울특별시": {"우즈베키스탄": 30, "파키스탄": 5, "몽골": 15, "베트남": 100},
        "강원특별자치도": {"이란": 7, "몽골": 3},          # renamed -> alias to 강원도 (code 32)
        "없는도": {"이란": 99},                            # no GeoJSON match -> skipped
    }
    out = build_region_residents(province_counts, GEO)
    assert set(out) == {"11", "32"}

    seoul = out["11"]
    assert seoul["name_eng"] == "Seoul"
    assert seoul["total_muslim"] == 35                    # Mongolia excluded from total
    assert seoul["by_country"] == [
        {"country": "Uzbekistan", "count": 30},
        {"country": "Pakistan", "count": 5},
        {"country": "Mongolia", "count": 15, "extra": True},   # pinned last
    ]
    assert out["32"]["total_muslim"] == 7
    assert out["32"]["by_country"][-1] == {"country": "Mongolia", "count": 3, "extra": True}
