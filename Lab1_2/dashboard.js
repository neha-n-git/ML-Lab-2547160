const data = {
  kpis: [
    { label: "Air rows", value: "29,531", note: "Readings collected across 26 cities" },
    { label: "Crop rows", value: "246,091", note: "A broad national crop dataset" },
    { label: "AQI buckets", value: "6", note: "From good air to severe pollution" },
    { label: "Shared year", value: "2015", note: "The only overlap between both datasets" },
  ],
  seasonalMonths: [
    { month: "Jan", level: 4, tone: "high" },
    { month: "Feb", level: 4, tone: "high" },
    { month: "Mar", level: 3, tone: "" },
    { month: "Apr", level: 3, tone: "" },
    { month: "May", level: 3, tone: "" },
    { month: "Jun", level: 2, tone: "" },
    { month: "Jul", level: 1, tone: "" },
    { month: "Aug", level: 1, tone: "" },
    { month: "Sep", level: 1, tone: "" },
    { month: "Oct", level: 4, tone: "high" },
    { month: "Nov", level: 5, tone: "peak" },
    { month: "Dec", level: 4, tone: "high" },
  ],
  correlations: [
    { label: "PM2.5", value: 0.8, note: "Tiny particles" },
    { label: "NO", value: 0.8, note: "Traffic and combustion" },
    { label: "NO2", value: 0.8, note: "Traffic and combustion" },
    { label: "SO2", value: 0.7, note: "Industrial smoke" },
    { label: "O3", value: 0.7, note: "Photochemical smog" },
    { label: "CO", value: 0.5, note: "Incomplete burning" },
    { label: "PM10", value: 0.4, note: "Larger dust particles" },
    { label: "NOx", value: 0.4, note: "Nitrogen oxides" },
  ],
  missing: [
    { label: "Xylene", value: 61.32 },
    { label: "PM10", value: 37.72 },
    { label: "NH3", value: 34.97 },
    { label: "Toluene", value: 27.23 },
    { label: "Benzene", value: 19.04 },
    { label: "AQI", value: 15.85 },
  ],
  cropMetrics: [
    { label: "States", value: "33", note: "State-level crop coverage" },
    { label: "Districts", value: "646", note: "Local geography covered" },
    { label: "Crops", value: "124", note: "Different crop types" },
  ],
};

function renderKpis() {
  const grid = document.getElementById("kpi-grid");
  grid.innerHTML = data.kpis
    .map(
      (item) => `
        <article class="kpi-card">
          <p class="label">${item.label}</p>
          <strong class="value">${item.value}</strong>
          <p class="note">${item.note}</p>
        </article>
      `,
    )
    .join("");
}

function renderSeasonStrip() {
  const strip = document.getElementById("season-strip");
  strip.innerHTML = data.seasonalMonths
    .map(
      (item) => `
        <div class="month-tile ${item.tone}" style="--level:${item.level}">
          <span>${item.month}</span>
          <strong>${item.level === 5 ? "Worst" : item.level === 1 ? "Best" : "Higher risk"}</strong>
        </div>
      `,
    )
    .join("");
}

function renderBars(targetId, rows, fillClass = "") {
  const target = document.getElementById(targetId);
  const max = Math.max(...rows.map((row) => row.value));
  target.innerHTML = rows
    .map((row) => {
      const width = Math.max(8, (row.value / max) * 100);
      return `
        <div class="bar-item">
          <div class="bar-label">${row.label}</div>
          <div class="bar-track">
            <div class="bar-fill ${fillClass}" style="width:${width}%"></div>
          </div>
          <div class="bar-value">${row.value.toFixed(2)}%</div>
        </div>
      `;
    })
    .join("");
}

function renderCorrelations() {
  const target = document.getElementById("correlation-bars");
  const max = 1;
  target.innerHTML = data.correlations
    .map((row) => {
      const width = Math.max(12, (row.value / max) * 100);
      return `
        <div class="bar-item">
          <div class="bar-label">${row.label}</div>
          <div class="bar-track">
            <div class="bar-fill" style="width:${width}%"></div>
          </div>
          <div class="bar-value">${row.value.toFixed(1)}</div>
        </div>
      `;
    })
    .join("");
}

function renderCropMetrics() {
  const target = document.getElementById("crop-metrics");
  target.innerHTML = data.cropMetrics
    .map(
      (item) => `
        <div class="mini-card">
          <strong>${item.value}</strong>
          <span>${item.label}<br />${item.note}</span>
        </div>
      `,
    )
    .join("");
}

renderKpis();
renderSeasonStrip();
renderCorrelations();
renderBars("missing-bars", data.missing, "missing");
renderCropMetrics();
