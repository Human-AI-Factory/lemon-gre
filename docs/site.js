const siteData = JSON.parse(document.getElementById("site-data").textContent);
const spotlightTitle = document.getElementById("spotlight-title");
const spotlightCopy = document.getElementById("spotlight-copy");
const spotlightImage = document.getElementById("spotlight-image");
const spotlightVoices = document.getElementById("spotlight-voices");
const spotlightDownload = document.getElementById("spotlight-download");
const spotlightChip = document.getElementById("spotlight-chip");
const spotlightAudio = document.getElementById("spotlight-audio");
const spotlightPlayer = document.getElementById("spotlight-player");

function buildStats() {
  const statRow = document.getElementById("stat-row");
  statRow.innerHTML = siteData.stats.map((item) => `
    <article class="stat-card">
      <div class="stat-value">${item.value}</div>
      <div class="stat-label">${item.label}</div>
    </article>
  `).join("");
}

function buildFeatures() {
  const featureGrid = document.getElementById("feature-grid");
  featureGrid.innerHTML = siteData.features.map((item) => `
    <article class="feature-card">
      <div class="feature-icon ${item.icon}"></div>
      <h3>${item.title}</h3>
      <p>${item.copy}</p>
    </article>
  `).join("");
}

function updateSpotlight(theme) {
  document.documentElement.style.setProperty("--lime", theme.accent);
  document.documentElement.style.setProperty("--lemon", theme.accentSoft);
  spotlightTitle.textContent = theme.displayTitle;
  spotlightCopy.textContent = theme.copy;
  spotlightImage.src = theme.cover;
  spotlightImage.alt = `${theme.displayTitle} 封面`;
  spotlightDownload.href = theme.download;
  spotlightDownload.setAttribute("download", "");
  spotlightChip.textContent = theme.name;
  spotlightVoices.innerHTML = [
    ...theme.voicesEn.slice(0, 2).map((name) => `<span class="voice-tag">EN · ${name}</span>`),
    ...theme.voicesZh.slice(0, 2).map((name) => `<span class="voice-tag">ZH · ${name}</span>`)
  ].join("");

  spotlightAudio.onclick = () => {
    spotlightPlayer.src = theme.audio;
    spotlightPlayer.play().catch(() => {});
  };
}

function buildThemeOrbit() {
  const orbit = document.getElementById("theme-orbit");
  orbit.innerHTML = siteData.themes.map((theme, index) => `
    <button class="orbit-pill" type="button" data-theme-index="${index}">${theme.name}</button>
  `).join("");
}

function buildThemeGrid() {
  const themeGrid = document.getElementById("theme-grid");
  themeGrid.innerHTML = siteData.themes.map((theme, index) => `
    <article class="theme-card">
      <button class="theme-cover" type="button" data-theme-index="${index}">
        <img src="${theme.cover}" alt="${theme.displayTitle}">
      </button>
      <div class="theme-body">
        <div class="theme-meta">${theme.size} · 默认音色已配好</div>
        <h3>${theme.displayTitle}</h3>
        <p>${theme.copy}</p>
        <div class="voice-tags">
          <span class="voice-tag">EN · ${theme.voicesEn[0]}</span>
          <span class="voice-tag">ZH · ${theme.voicesZh[0]}</span>
        </div>
        <div class="theme-actions">
          <button class="tiny-btn" type="button" data-audio-index="${index}">试听</button>
          <button class="tiny-btn" type="button" data-theme-index="${index}">预览</button>
          <a class="tiny-btn strong" href="${theme.download}" download>下载 dmg</a>
        </div>
      </div>
    </article>
  `).join("");
}

function buildDownloads() {
  const downloadCards = document.getElementById("download-cards");
  downloadCards.innerHTML = siteData.themes.map((theme) => `
    <article class="download-card">
      <div class="download-label">${theme.name}</div>
      <h3>${theme.displayName}</h3>
      <p>${theme.copy}</p>
      <div class="download-size">macOS 安装包 · ${theme.size}</div>
      <div class="theme-actions">
        <a class="tiny-btn strong" href="${theme.download}" download>免费下载</a>
        <button class="tiny-btn" type="button" data-audio-src="${theme.audio}">试听音色</button>
      </div>
    </article>
  `).join("");
}

function bindActions() {
  document.querySelectorAll("[data-theme-index]").forEach((node) => {
    node.addEventListener("click", () => {
      const index = Number(node.getAttribute("data-theme-index"));
      updateSpotlight(siteData.themes[index]);
      document.getElementById("spotlight").scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  });

  document.querySelectorAll("[data-audio-index]").forEach((node) => {
    node.addEventListener("click", () => {
      const index = Number(node.getAttribute("data-audio-index"));
      spotlightPlayer.src = siteData.themes[index].audio;
      spotlightPlayer.play().catch(() => {});
    });
  });

  document.querySelectorAll("[data-audio-src]").forEach((node) => {
    node.addEventListener("click", () => {
      spotlightPlayer.src = node.getAttribute("data-audio-src");
      spotlightPlayer.play().catch(() => {});
    });
  });
}

buildStats();
buildFeatures();
buildThemeOrbit();
buildThemeGrid();
buildDownloads();
bindActions();
updateSpotlight(siteData.themes[0]);
