from pipeline.build_json import build_records


def test_attaches_coords_sorts_by_total_and_drops_unlocated():
    universities = [
        {"name_ko": "가대학교", "total": 50, "by_field": [], "by_program": []},
        {"name_ko": "나대학교", "total": 900, "by_field": [], "by_program": []},
        {"name_ko": "위치없음", "total": 999, "by_field": [], "by_program": []},
    ]
    located = {
        "가대학교": {"lat": 37.5, "lon": 127.0},
        "나대학교": {"lat": 35.1, "lon": 129.0},
    }
    out = build_records(universities, located)

    assert [u["name_ko"] for u in out] == ["나대학교", "가대학교"]  # 900 > 50, unlocated dropped
    assert all("name_en" in u for u in out)
    assert out[0]["lat"] == 35.1 and out[0]["lon"] == 129.0
    assert out[1]["total"] == 50


def test_keeps_breakdown_fields():
    universities = [{"name_ko": "다대학교", "total": 10,
                     "by_field": [{"name": "Engineering", "count": 10}],
                     "by_program": []}]
    out = build_records(universities, {"다대학교": {"lat": 1.0, "lon": 2.0}})
    assert out[0]["by_field"] == [{"name": "Engineering", "count": 10}]
