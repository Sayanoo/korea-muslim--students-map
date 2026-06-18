// South Korea bounds — lock the viewport to the country.
const KOREA_BOUNDS = L.latLngBounds([32.8, 124.3], [39.0, 132.2]);
const map = L.map("map", {
  maxBounds: KOREA_BOUNDS,
  maxBoundsViscosity: 1.0,
  minZoom: 7,
}).setView([36.5, 127.8], 7);
map.setMaxBounds(KOREA_BOUNDS);
L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
  maxZoom: 19,
  minZoom: 7,
  attribution: "&copy; OpenStreetMap, &copy; CARTO",
}).addTo(map);

function radius(n) {
  return Math.max(5, Math.min(36, 4 + Math.sqrt(n) * 0.85));
}
function countryRows(list) {
  return list.map((c) =>
    `<tr class="${c.extra ? "extra" : ""}"><td>${c.country}${c.extra ? " <span class='tag'>non-Muslim</span>" : ""}</td>` +
    `<td class="n">${c.count.toLocaleString()}</td></tr>`).join("");
}
function plainRows(list) {
  return list.map((c) =>
    `<tr><td>${c.name}</td><td class="n">${c.count.toLocaleString()}</td></tr>`).join("");
}
function ramp(stops, lo, hi) {
  return `<div class="ramp">${stops.map((c) => `<span style="background:${c}"></span>`).join("")}</div>` +
         `<div class="ramp-lbl"><span>${lo}</span><span>${hi}</span></div>`;
}
const TEAL = ["#99f6e4", "#2dd4bf", "#0d9488", "#0f766e", "#0b3d2e"];
function bucket(n, t) {
  return n >= t[3] ? TEAL[4] : n >= t[2] ? TEAL[3] : n >= t[1] ? TEAL[2]
       : n >= t[0] ? TEAL[1] : n >= 1 ? TEAL[0] : "#e5e7eb";
}

// ---- Marker views --------------------------------------------------------
const MARKER_VIEWS = {
  all: {
    file: "universities.json",
    color: () => "#1a9e6e",
    value: (u) => u.total,
    subtitle: "2025 · KEDI / 대학알리미 · circle size = total foreign students",
    legend: `<b>All foreign students</b><br>Circle size = number of students.<br>Hover a campus for the program breakdown.`,
    card: (u) => {
      let h = `<div class="uni-card"><h3>${u.name_en}</h3>
        <p class="sub">${u.name_ko} · ${u.region_ko}</p>
        <p class="total">${u.total.toLocaleString()}<span> foreign students</span></p>`;
      if (u.by_field?.length)
        h += `<h4>Degree program · ${u.degree.toLocaleString()}</h4><table>${plainRows(u.by_field)}</table>`;
      if (u.by_program?.length)
        h += `<h4>Non-degree · ${u.non_degree.toLocaleString()}</h4><table>${plainRows(u.by_program)}</table>`;
      return h + `</div>`;
    },
  },
  muslim: {
    file: "muslim_universities.json",
    color: (u) => bucket(u.total_muslim, [15, 50, 150, 400]),
    value: (u) => u.total_muslim,
    subtitle: "2025 · university students from Muslim-majority countries (>50% Muslim)",
    legend: `<b>Muslim-country students (per university)</b><br>Circle size = number of students.
      ${ramp(TEAL, 1, "400+")}Hover a campus to see each country.`,
    card: (u) => `<div class="uni-card"><h3>${u.name_en}</h3><p class="sub">${u.name_ko}</p>
      <p class="total">${u.total_muslim.toLocaleString()}<span> students from Muslim-majority countries</span></p>
      <h4>By country of origin</h4><table>${countryRows(u.by_country)}</table></div>`,
  },
};

// ---- Province (choropleth) views -----------------------------------------
const REGION_VIEWS = {
  region: {
    geo: "skorea_provinces.geojson",
    data: "muslim_by_region.json",
    color: (r) => bucket(r ? r.total_muslim : 0, [200, 500, 1000, 2000]),
    subtitle: "2025 · university students from Muslim-majority countries, by province",
    legend: `<b>Muslim-country students by province</b><br>Shade = students in the region.
      ${ramp(TEAL, 1, "2000+")}Hover a region for the country breakdown.`,
    title: "students from Muslim-majority countries",
  },
  residents: {
    geo: "skorea_provinces.geojson",
    data: "muslim_residents_by_region.json",
    color: (r) => bucket(r ? r.total_muslim : 0, [2000, 5000, 15000, 40000]),
    subtitle: "2024 · registered residents from Muslim-majority countries (법무부 통계연보), by province",
    legend: `<b>Muslim-country residents by province</b><br>Shade = registered residents in the region.
      ${ramp(TEAL, 1, "40k+")}Hover a region for the country breakdown.`,
    title: "registered residents from Muslim-majority countries",
  },
};
function regionCard(cfg, r) {
  return `<div class="uni-card"><h3>${r.name_eng}</h3><p class="sub">${r.name}</p>
    <p class="total">${r.total_muslim.toLocaleString()}<span> ${cfg.title}</span></p>
    <h4>By country of origin</h4><table>${countryRows(r.by_country)}</table></div>`;
}

let layer = null;
let byName = new Map();
const dataCache = {};

function clearLayer() {
  if (layer) { map.removeLayer(layer); layer = null; }
  byName = new Map();
}

function renderMarkers(cfg, data) {
  clearLayer();
  layer = L.markerClusterGroup({ maxClusterRadius: 45 });
  data.forEach((u) => {
    const m = L.circleMarker([u.lat, u.lon], {
      radius: radius(cfg.value(u)), color: "#fff",
      fillColor: cfg.color(u), fillOpacity: 0.85, weight: 1.2,
    });
    m.bindPopup(cfg.card(u), { maxHeight: 320 });
    m.on("mouseover", () => m.openPopup());
    byName.set(`${u.name_en.toLowerCase()}${u.name_ko}`, { marker: m, u });
    layer.addLayer(m);
  });
  map.addLayer(layer);
}

function renderRegions(cfg, geojson, regions) {
  clearLayer();
  layer = L.geoJSON(geojson, {
    style: (f) => ({ fillColor: cfg.color(regions[f.properties.code]), fillOpacity: 0.72,
                     color: "#0b3d2e", weight: 1.2 }),
    onEachFeature: (f, lyr) => {
      const r = regions[f.properties.code] ||
        { name_eng: f.properties.name_eng, name: f.properties.name, total_muslim: 0, by_country: [] };
      lyr.bindPopup(regionCard(cfg, r), { maxHeight: 320 });
      lyr.on("mouseover", () => { lyr.setStyle({ weight: 3, fillOpacity: 0.9 }); lyr.openPopup(); });
      lyr.on("mouseout", () => layer.resetStyle(lyr));
      byName.set(`${(r.name_eng || "").toLowerCase()}${r.name || ""}`, { marker: lyr, u: null });
    },
  });
  map.addLayer(layer);
}

function loadView(name) {
  const cfg = REGION_VIEWS[name] || MARKER_VIEWS[name];
  document.getElementById("subtitle").textContent = cfg.subtitle;
  document.getElementById("legend").innerHTML = cfg.legend;
  if (REGION_VIEWS[name]) {
    Promise.all([
      dataCache.geo || fetch(cfg.geo).then((r) => r.json()),
      dataCache[name] || fetch(cfg.data).then((r) => r.json()),
    ]).then(([geojson, regions]) => {
      dataCache.geo = geojson; dataCache[name] = regions;
      renderRegions(cfg, geojson, regions);
    });
    return;
  }
  if (dataCache[name]) return renderMarkers(cfg, dataCache[name]);
  fetch(cfg.file).then((r) => r.json()).then((data) => {
    dataCache[name] = data;
    renderMarkers(cfg, data);
  });
}

document.querySelectorAll(".toggle button").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".toggle button").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    loadView(btn.dataset.view);
  });
});

document.getElementById("search").addEventListener("input", (e) => {
  const q = e.target.value.trim().toLowerCase();
  if (!q) return;
  for (const [key, { marker, u }] of byName) {
    if (key.includes(q)) {
      if (u) map.setView([u.lat, u.lon], 12);
      else map.fitBounds(marker.getBounds());
      marker.openPopup();
      break;
    }
  }
});

loadView("all");
