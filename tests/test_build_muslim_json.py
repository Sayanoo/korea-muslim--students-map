from pipeline.build_muslim_json import build_muslim_records


def test_filters_muslim_sorts_and_attaches_coords():
    scraped = {
        "001": {"rep_name": "가대학교",
                "countries": {"우즈베키스탄": 10, "중국": 300, "파키스탄": 5, "베트남": 50}},
        "002": {"rep_name": "나대학교", "countries": {"중국": 100, "일본": 20}},   # no Muslim
        "003": {"rep_name": "위치없음", "countries": {"이란": 7}},                 # no coords
    }
    located = {"가대학교": {"lat": 37.5, "lon": 127.0},
               "나대학교": {"lat": 35.1, "lon": 129.0}}
    out = build_muslim_records(scraped, located)

    assert [r["name_ko"] for r in out] == ["가대학교"]   # only one with Muslim students + coords
    u = out[0]
    assert "name_en" in u
    assert u["total_muslim"] == 15
    assert u["by_country"] == [
        {"country": "Uzbekistan", "count": 10},
        {"country": "Pakistan", "count": 5},
    ]
    assert u["lat"] == 37.5 and u["lon"] == 127.0


def test_mongolia_appended_last_and_not_counted_in_total():
    scraped = {
        "001": {"rep_name": "가대학교",
                "countries": {"우즈베키스탄": 10, "파키스탄": 5, "몽골": 40, "중국": 3}},
        "002": {"rep_name": "나대학교", "countries": {"몽골": 50, "중국": 10}},  # only Mongolia -> excluded
    }
    located = {"가대학교": {"lat": 37.5, "lon": 127.0}, "나대학교": {"lat": 35.1, "lon": 129.0}}
    out = build_muslim_records(scraped, located)

    assert [r["name_ko"] for r in out] == ["가대학교"]   # Mongolia-only school not on the map
    u = out[0]
    assert u["total_muslim"] == 15                       # Mongolia NOT counted
    assert u["by_country"] == [                           # Mongolia pinned LAST, after sorted Muslim
        {"country": "Uzbekistan", "count": 10},
        {"country": "Pakistan", "count": 5},
        {"country": "Mongolia", "count": 40, "extra": True},
    ]


def test_merges_country_aliases():
    scraped = {"001": {"rep_name": "다대학교", "countries": {"터키": 3, "튀르키예": 4}}}
    located = {"다대학교": {"lat": 1.0, "lon": 2.0}}
    out = build_muslim_records(scraped, located)
    assert out[0]["by_country"] == [{"country": "Turkey", "count": 7}]
    assert out[0]["total_muslim"] == 7
