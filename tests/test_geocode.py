import json
from pipeline.geocode import resolve_coords, clean_name, search_query


def test_search_query_appends_region_for_disambiguation():
    assert search_query("연세대학교", "서울") == "연세대학교, 서울, South Korea"
    assert search_query("국립부경대학교", None) == "부경대학교, South Korea"
    assert search_query("건국대학교(글로컬)_분교", "충북") == "건국대학교, 충북, South Korea"


def test_clean_name_strips_campus_branch_and_national_prefix():
    assert clean_name("가천대학교_제2캠퍼스") == "가천대학교"
    assert clean_name("가야대학교(김해)") == "가야대학교"
    assert clean_name("국립부경대학교") == "부경대학교"
    assert clean_name("건국대학교(글로컬)_분교") == "건국대학교"
    assert clean_name("고려대학교(세종)_분교") == "고려대학교"


def test_overrides_win_and_cache_is_written(tmp_path):
    cache = tmp_path / "cache.json"
    overrides = tmp_path / "ov.json"
    overrides.write_text(json.dumps({"override대학교": {"lat": 1.0, "lon": 2.0}}),
                         encoding="utf-8")

    calls = []

    def fake_geocoder(name):
        calls.append(name)
        return {"geo대학교": {"lat": 37.5, "lon": 127.0}}.get(name)

    located, unlocated = resolve_coords(
        ["override대학교", "geo대학교", "없는대학교"],
        str(cache), str(overrides), geocoder=fake_geocoder,
    )
    assert located["override대학교"] == {"lat": 1.0, "lon": 2.0}
    assert located["geo대학교"] == {"lat": 37.5, "lon": 127.0}
    assert unlocated == ["없는대학교"]
    assert "override대학교" not in calls            # override skips geocoder
    assert json.loads(cache.read_text(encoding="utf-8"))["geo대학교"]["lat"] == 37.5


def test_cache_prevents_second_geocoder_call(tmp_path):
    cache = tmp_path / "cache.json"
    cache.write_text(json.dumps({"x대학교": {"lat": 5.0, "lon": 6.0}}), encoding="utf-8")

    def boom(name):
        raise AssertionError("should not be called")

    located, unlocated = resolve_coords(
        ["x대학교"], str(cache), str(tmp_path / "ov.json"), geocoder=boom)
    assert located["x대학교"] == {"lat": 5.0, "lon": 6.0}
    assert unlocated == []
