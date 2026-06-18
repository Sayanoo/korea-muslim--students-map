from pipeline.aggregate_regions import (
    point_in_polygon, aggregate_by_region, nearest_region_for_point)

SQUARE = [[[0, 0], [0, 10], [10, 10], [10, 0], [0, 0]]]  # one ring, [lon,lat]


def test_point_in_polygon():
    assert point_in_polygon(5, 5, SQUARE) is True
    assert point_in_polygon(15, 5, SQUARE) is False
    assert point_in_polygon(-1, 5, SQUARE) is False


def test_nearest_snaps_only_within_threshold():
    feats = [{"properties": {"code": "11", "name_eng": "Ga-do"},
              "geometry": {"type": "Polygon", "coordinates": SQUARE}}]
    # just outside a corner vertex -> snaps to the province
    assert nearest_region_for_point(10.1, 10.1, feats)["code"] == "11"
    # far away -> not snapped
    assert nearest_region_for_point(50, 50, feats) is None


def test_aggregate_sums_and_merges_countries_by_region():
    geojson = {"features": [
        {"properties": {"code": "11", "name": "가도", "name_eng": "Ga-do"},
         "geometry": {"type": "Polygon", "coordinates": SQUARE}},
    ]}
    records = [
        {"lat": 5, "lon": 5, "total_muslim": 10,
         "by_country": [{"country": "Iran", "count": 6}, {"country": "Iraq", "count": 4}]},
        {"lat": 6, "lon": 5, "total_muslim": 5,
         "by_country": [{"country": "Iran", "count": 5}]},
        {"lat": 50, "lon": 50, "total_muslim": 99,             # outside -> ignored
         "by_country": [{"country": "Egypt", "count": 99}]},
    ]
    out = aggregate_by_region(records, geojson)
    assert "11" in out and len(out) == 1
    reg = out["11"]
    assert reg["name_eng"] == "Ga-do"
    assert reg["total_muslim"] == 15
    assert reg["by_country"] == [
        {"country": "Iran", "count": 11},
        {"country": "Iraq", "count": 4},
    ]
