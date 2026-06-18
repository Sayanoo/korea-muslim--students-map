"""Aggregate per-university Muslim-student data into provinces via point-in-polygon."""
from __future__ import annotations


def point_in_polygon(lon: float, lat: float, rings: list) -> bool:
    """Ray-casting test against a polygon's outer ring (rings[0]); coords are [lon,lat]."""
    ring = rings[0]
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > lat) != (yj > lat)) and \
           (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _point_in_feature(lon: float, lat: float, geometry: dict) -> bool:
    t = geometry["type"]
    coords = geometry["coordinates"]
    if t == "Polygon":
        return point_in_polygon(lon, lat, coords)
    if t == "MultiPolygon":
        return any(point_in_polygon(lon, lat, poly) for poly in coords)
    return False


def region_for_point(lon: float, lat: float, features: list) -> dict | None:
    for f in features:
        if _point_in_feature(lon, lat, f["geometry"]):
            return f["properties"]
    return None


def _min_vertex_dist2(lon, lat, geometry):
    best = float("inf")
    coords = geometry["coordinates"]
    polys = coords if geometry["type"] == "MultiPolygon" else [coords]
    for poly in polys:
        for x, y in poly[0]:
            d = (x - lon) ** 2 + (y - lat) ** 2
            if d < best:
                best = d
    return best


def nearest_region_for_point(lon, lat, features, max_dist=0.2) -> dict | None:
    """PIP first; otherwise snap to the nearest province if within max_dist degrees
    (handles campuses on islands/coastline just outside simplified borders)."""
    hit = region_for_point(lon, lat, features)
    if hit:
        return hit
    best, best_f = max_dist ** 2, None
    for f in features:
        d = _min_vertex_dist2(lon, lat, f["geometry"])
        if d < best:
            best, best_f = d, f
    return best_f["properties"] if best_f else None


def aggregate_by_region(records: list[dict], geojson: dict) -> dict:
    """Group Muslim records into provinces, summing totals and merging country counts."""
    features = geojson["features"]
    regions: dict[str, dict] = {}
    for r in records:
        props = nearest_region_for_point(r["lon"], r["lat"], features)
        if not props:
            continue
        code = props["code"]
        reg = regions.setdefault(code, {
            "code": code, "name": props.get("name"), "name_eng": props.get("name_eng"),
            "total_muslim": 0, "_counts": {},
        })
        reg["total_muslim"] += r["total_muslim"]
        for c in r["by_country"]:
            reg["_counts"][c["country"]] = reg["_counts"].get(c["country"], 0) + c["count"]
    for reg in regions.values():
        reg["by_country"] = [{"country": c, "count": n} for c, n in
                             sorted(reg.pop("_counts").items(), key=lambda kv: kv[1], reverse=True)]
    return regions
