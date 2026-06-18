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
function muslimColor(n) {
  return n >= 400 ? "#0b3d2e" : n >= 150 ? "#0f766e" : n >= 50 ? "#0d9488"
       : n >= 15 ? "#2dd4bf" : "#99f6e4";
}
function regionColor(n) {
  return n >= 2000 ? "#0b3d2e" : n >= 1000 ? "#0f766e" : n >= 500 ? "#0d9488"
       : n >= 200 ? "#2dd4bf" : n >= 1 ? "#99f6e4" : "#e5e7eb";
}

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
    color: (u) => muslimColor(u.total_muslim),
    value: (u) => u.total_muslim,
    subtitle: "2025 · students from Muslim-majority countries (>50% Muslim) · circle size & shade = count",
    legend: `<b>Students from Muslim-majority countries</b><br>Circle size = number of students.
      <div class="ramp"><span style="background:#99f6e4"></span><span style="background:#2dd4bf"></span>
      <span style="background:#0d9488"></span><span style="background:#0f766e"></span>
      <span style="background:#0b3d2e"></span></div><div class="ramp-lbl"><span>1</span><span>400+</span></div>
      Hover a campus to see each country.`,
    card: (u) => `<div class="uni-card"><h3>${u.name_en}</h3><p class="sub">${u.name_ko}</p>
      <p class="total">${u.total_muslim.toLocaleString()}<span> students from Muslim-majority countries</span></p>
      <h4>By country of origin</h4><table>${countryRows(u.by_country)}</table></div>`,
  },
};

const REGION_VIEW = {
  geo: "skorea_provinces.geojson",
  data: "muslim_by_region.json",
  subtitle: "2025 · Muslim-majority-country students aggregated by province/metropolitan city",
  legend: `<b>Muslim students by province</b><br>Shade = total students in the region.
    <div class="ramp"><span style="background:#99f6e4"></span><span style="background:#2dd4bf"></span>
    <span style="background:#0d9488"></span><span style="background:#0f766e"></span>
    <span style="background:#0b3d2e"></span></div><div class="ramp-lbl"><span>1</span><span>2000+</span></div>
    Hover a region for the country breakdown.`,
  card: (r) => `<div class="uni-card"><h3>${r.name_eng}</h3><p class="sub">${r.name}</p>
    <p class="total">${r.total_muslim.toLocaleString()}<span> students from Muslim-majority countries</span></p>
    <h4>By country of origin</h4><table>${countryRows(r.by_country)}</table></div>`,
};

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

function renderRegions(geojson, regions) {
  clearLayer();
  layer = L.geoJSON(geojson, {
    style: (f) => {
      const r = regions[f.properties.code];
      return { fillColor: regionColor(r ? r.total_muslim : 0), fillOpacity: 0.7,
               color: "#0b3d2e", weight: 1.2 };
    },
    onEachFeature: (f, lyr) => {
      const r = regions[f.properties.code] ||
        { name_eng: f.properties.name_eng, name: f.properties.name, total_muslim: 0, by_country: [] };
      lyr.bindPopup(REGION_VIEW.card(r), { maxHeight: 320 });
      lyr.on("mouseover", () => { lyr.setStyle({ weight: 3, fillOpacity: 0.85 }); lyr.openPopup(); });
      lyr.on("mouseout", () => layer.resetStyle(lyr));
      byName.set(`${(r.name_eng || "").toLowerCase()}${r.name || ""}`, { marker: lyr, u: null });
    },
  });
  map.addLayer(layer);
}

function loadView(name) {
  if (name === "region") {
    document.getElementById("subtitle").textContent = REGION_VIEW.subtitle;
    document.getElementById("legend").innerHTML = REGION_VIEW.legend;
    Promise.all([
      dataCache.geo || fetch(REGION_VIEW.geo).then((r) => r.json()),
      dataCache.region || fetch(REGION_VIEW.data).then((r) => r.json()),
    ]).then(([geojson, regions]) => {
      dataCache.geo = geojson; dataCache.region = regions;
      renderRegions(geojson, regions);
    });
    return;
  }
  const cfg = MARKER_VIEWS[name];
  document.getElementById("subtitle").textContent = cfg.subtitle;
  document.getElementById("legend").innerHTML = cfg.legend;
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
      if (u) { map.setView([u.lat, u.lon], 12); }
      else { map.fitBounds(marker.getBounds()); }
      marker.openPopup();
      break;
    }
  }
});

loadView("all");
