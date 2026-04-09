from __future__ import annotations

import json
import math
import shutil
import subprocess
import textwrap
from pathlib import Path

from build_theme_apps import THEMES


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
APPS = ROOT / "apps"


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    units = ["B", "KB", "MB", "GB"]
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{num_bytes} B"


def convert_audio(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["afconvert", "-f", "WAVE", "-d", "LEI16", str(source), str(target)],
        check=True,
    )


def copy_online_demo() -> None:
    source = APPS / "清爽柠檬" / "web"
    target = DOCS / "app"
    shutil.copytree(source, target, dirs_exist_ok=True)


def collect_themes() -> list[dict]:
    results = []
    for theme in THEMES:
        theme_dir = APPS / theme["dir_name"]
        mac_dir = theme_dir / "macOS"
        dmg_path = mac_dir / f"{theme['display_name']}.dmg"
        cover_path = theme_dir / "cover.png"
        voice_path = theme_dir / "voice-preview.aiff"
        icon_path = theme_dir / "web" / "icons" / "app-icon.png"

        if not dmg_path.exists():
            raise FileNotFoundError(dmg_path)
        if not cover_path.exists():
            raise FileNotFoundError(cover_path)
        if not voice_path.exists():
            raise FileNotFoundError(voice_path)
        if not icon_path.exists():
            raise FileNotFoundError(icon_path)

        cover_target = DOCS / "assets" / "themes" / f"{theme['slug']}-cover.png"
        audio_target = DOCS / "assets" / "audio" / f"{theme['slug']}.wav"
        dmg_target = DOCS / "downloads" / f"{theme['slug']}.dmg"

        cover_target.parent.mkdir(parents=True, exist_ok=True)
        audio_target.parent.mkdir(parents=True, exist_ok=True)
        dmg_target.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(cover_path, cover_target)
        shutil.copy2(dmg_path, dmg_target)
        convert_audio(voice_path, audio_target)

        if theme["dir_name"] == "清爽柠檬":
            shutil.copy2(icon_path, DOCS / "assets" / "favicon.png")
            shutil.copy2(cover_path, DOCS / "assets" / "og-cover.png")

        results.append({
            "name": theme["dir_name"],
            "slug": theme["slug"],
            "displayName": theme["display_name"],
            "displayTitle": theme["display_title"],
            "copy": theme["brand_copy"],
            "cover": f"./assets/themes/{theme['slug']}-cover.png",
            "audio": f"./assets/audio/{theme['slug']}.wav",
            "download": f"./downloads/{theme['slug']}.dmg",
            "size": human_size(dmg_path.stat().st_size),
            "voicesEn": theme["voices"]["en"],
            "voicesZh": theme["voices"]["zh"],
            "accent": theme["colors"]["lime"],
            "accentSoft": theme["colors"]["lemon"],
            "background": theme["colors"]["bgCream"],
        })
    return results


def build_site_data(themes: list[dict]) -> str:
    payload = {
        "repoName": "Lemon GRE",
        "heroTitle": "背 GRE 单词，不要再像罚抄。",
        "heroCopy": "Lemon GRE 把背词拆成一页一词的顺序流：到页即发音、点击滑动翻页、熟词低频召回、Excel 拖进来就能学，还能导出今日音频。现在它不止能用，还做成了 6 款主题版本，直接从 GitHub 免费下载。",
        "stats": [
            {"value": "3041", "label": "内置 GRE 词"},
            {"value": "1 页 1 词", "label": "顺序翻页背"},
            {"value": "Excel", "label": "拖拽导入"},
            {"value": "6 款", "label": "主题版本"},
        ],
        "features": [
            {
                "title": "顺序刷词，不乱跳",
                "copy": "每个单词都是单独一页，点击或滑动就往下走。你能明显感受到一轮一轮往前推，而不是被算法随便打散。",
                "icon": "stack",
            },
            {
                "title": "熟悉度调频",
                "copy": "不熟悉就多出现，熟悉就稍后出现，太熟了就低频召回。不是简单删掉，而是按记忆状态调整出现频率。",
                "icon": "dial",
            },
            {
                "title": "随时加词表",
                "copy": "支持手动粘贴、拖拽 Excel / CSV / TXT、拆分词库、合并词库。新词会直接进当前学习队列，不需要重开。",
                "icon": "spark",
            },
            {
                "title": "今日音频",
                "copy": "整轮单词和中文释义可以连续朗读，还能导出脚本或录制成音频，适合通勤和睡前复习。",
                "icon": "wave",
            },
        ],
        "themes": themes,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_index_html(site_data: str) -> str:
    return textwrap.dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <meta name="theme-color" content="#a5cf5b">
          <meta name="description" content="Lemon GRE：图文并茂的 GRE 背词神器宣传站，支持在线体验、主题试听和 GitHub 免费下载。">
          <meta property="og:title" content="Lemon GRE 背词神器">
          <meta property="og:description" content="六款主题、顺序刷词、熟词低频召回、今日音频、Excel 直接导入。">
          <meta property="og:image" content="./assets/og-cover.png">
          <title>Lemon GRE | GRE 背词神器</title>
          <link rel="icon" href="./assets/favicon.png" type="image/png">
          <link rel="preconnect" href="https://fonts.googleapis.com">
          <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
          <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">
          <link rel="stylesheet" href="./styles.css">
        </head>
        <body>
          <div class="page-shell">
            <header class="topbar">
              <a class="brand" href="#hero">
                <span class="brand-mark">L</span>
                <span class="brand-text">Lemon GRE</span>
              </a>
              <nav class="nav">
                <a href="#features">玩法亮点</a>
                <a href="#themes">主题版本</a>
                <a href="#downloads">免费下载</a>
                <a href="./app/index.html">在线体验</a>
              </nav>
            </header>

            <main>
              <section class="hero" id="hero">
                <div class="hero-copy">
                  <div class="eyebrow">GRE Vocab, But Finally Fun</div>
                  <h1 class="hero-title">背 GRE 单词，不要再像罚抄。</h1>
                  <p class="hero-text">Lemon GRE 把背词拆成一页一词的顺序流：到页即发音、点击滑动翻页、熟词低频召回、Excel 拖进来就能学，还能导出今日音频。现在它不止能用，还做成了 6 款主题版本，直接从 GitHub 免费下载。</p>
                  <div class="hero-actions">
                    <a class="primary-cta" href="#downloads">免费下载 App</a>
                    <a class="secondary-cta" href="./app/index.html">在线体验网页版</a>
                  </div>
                  <div class="stat-row" id="stat-row"></div>
                </div>

                <aside class="spotlight" id="spotlight">
                  <div class="spotlight-media">
                    <img id="spotlight-image" alt="Lemon GRE 主题封面">
                    <div class="floating-chip" id="spotlight-chip">Theme Pack</div>
                  </div>
                  <div class="spotlight-body">
                    <div class="spotlight-label">主题主打</div>
                    <h2 id="spotlight-title"></h2>
                    <p id="spotlight-copy"></p>
                    <div class="voice-tags" id="spotlight-voices"></div>
                    <div class="spotlight-actions">
                      <button id="spotlight-audio" class="mini-cta" type="button">试听主题音色</button>
                      <a id="spotlight-download" class="mini-cta strong" href="">下载 macOS 版</a>
                    </div>
                    <audio id="spotlight-player" preload="none" controls></audio>
                  </div>
                </aside>
              </section>

              <section class="feature-section" id="features">
                <div class="section-heading">
                  <p class="eyebrow">Why It Hits</p>
                  <h2>不是“又一个背单词工具”，而是一套更顺手的复习节奏。</h2>
                </div>
                <div class="feature-grid" id="feature-grid"></div>
              </section>

              <section class="showcase">
                <div class="showcase-card live-demo">
                  <div>
                    <p class="eyebrow">Live Demo</p>
                    <h3>GitHub Pages 上直接打开就能背</h3>
                    <p>站点里内置了在线体验版。手机上直接打开网页，Safari / Chrome 都可以继续走添加到主屏幕这条路。</p>
                  </div>
                  <div class="showcase-actions">
                    <a class="primary-cta small" href="./app/index.html">立刻试玩</a>
                    <a class="secondary-cta small" href="#downloads">看下载版本</a>
                  </div>
                </div>
                <div class="showcase-card mood-board">
                  <p class="eyebrow">Theme Mixer</p>
                  <h3>六种风格，不止换皮，连默认音色都换了。</h3>
                  <div class="theme-orbit" id="theme-orbit"></div>
                </div>
              </section>

              <section class="themes-section" id="themes">
                <div class="section-heading">
                  <p class="eyebrow">Theme Gallery</p>
                  <h2>选你最愿意每天打开的那一版。</h2>
                </div>
                <div class="theme-grid" id="theme-grid"></div>
              </section>

              <section class="download-section" id="downloads">
                <div class="section-heading">
                  <p class="eyebrow">Free Downloads</p>
                  <h2>安装包就托管在这个 GitHub 站点里，点下去直接拿。</h2>
                </div>
                <div class="download-layout">
                  <div class="download-copy">
                    <p>当前最完整的是 macOS 版，每个主题都有独立 <code>dmg</code>。如果你想先在手机上试，直接点“在线体验网页版”就行，再按浏览器提示加入主屏幕。</p>
                    <ul class="download-notes">
                      <li>Mac：直接下载 <code>dmg</code>，拖进应用程序就能用。</li>
                      <li>iPhone / Android：打开网页体验版，安装到主屏幕。</li>
                      <li>GitHub 托管：网站、试听和安装包都可以随仓库一起发布。</li>
                    </ul>
                  </div>
                  <div class="download-cards" id="download-cards"></div>
                </div>
              </section>

              <section class="faq-section">
                <div class="section-heading">
                  <p class="eyebrow">FAQ</p>
                  <h2>几个你大概率会被问到的问题。</h2>
                </div>
                <div class="faq-list">
                  <article>
                    <h3>它和普通抽认卡最大区别是什么？</h3>
                    <p>不是随机乱飞的卡片流，而是顺序推进的一页一词。你会明显感觉自己在完整地刷完一轮，再靠熟悉度把节奏调顺。</p>
                  </article>
                  <article>
                    <h3>熟词会不会直接消失？</h3>
                    <p>不会。它只会进入“低频召回”，你太熟的词以后还是会回来，只是间隔更长，避免浪费注意力。</p>
                  </article>
                  <article>
                    <h3>能不能自己加词表？</h3>
                    <p>可以。Excel、CSV、TXT 都支持，拖进去就能扩充；还可以新建词库、合并词库和拆分词库。</p>
                  </article>
                </div>
              </section>
            </main>

            <footer class="footer">
              <p>Lemon GRE · GitHub Pages 宣传站</p>
              <p>推到 GitHub 后，把 Pages 的发布目录指向 <code>/docs</code> 即可上线。</p>
            </footer>
          </div>

          <script id="site-data" type="application/json">{site_data}</script>
          <script src="./site.js"></script>
        </body>
        </html>
        """
    )


def build_styles() -> str:
    return textwrap.dedent(
        """
        :root {
          --bg: #fbf7e8;
          --bg-soft: #f2f9e8;
          --ink: #102b1d;
          --ink-soft: #54695b;
          --line: rgba(16, 43, 29, 0.08);
          --card: rgba(255, 255, 255, 0.74);
          --lime: #a5cf5b;
          --lemon: #ffd95a;
          --mint: #dff1d2;
          --shadow: 0 30px 70px rgba(79, 120, 34, 0.16);
        }

        * {
          box-sizing: border-box;
        }

        html {
          scroll-behavior: smooth;
        }

        body {
          margin: 0;
          min-height: 100%;
          font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
          color: var(--ink);
          background:
            radial-gradient(circle at top left, rgba(255, 217, 90, 0.56), transparent 26%),
            radial-gradient(circle at top right, rgba(165, 207, 91, 0.22), transparent 25%),
            linear-gradient(180deg, var(--bg), var(--bg-soft));
          overflow-x: hidden;
        }

        a {
          color: inherit;
          text-decoration: none;
        }

        button {
          font: inherit;
          border: 0;
          cursor: pointer;
        }

        .page-shell {
          max-width: 1220px;
          margin: 0 auto;
          padding: 24px 20px 64px;
        }

        .topbar {
          position: sticky;
          top: 16px;
          z-index: 20;
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 16px;
          margin-bottom: 32px;
          padding: 16px 18px;
          border-radius: 22px;
          background: rgba(255, 255, 255, 0.78);
          backdrop-filter: blur(18px);
          box-shadow: 0 18px 38px rgba(78, 108, 44, 0.12);
          border: 1px solid rgba(255, 255, 255, 0.64);
        }

        .brand {
          display: inline-flex;
          align-items: center;
          gap: 12px;
          font-weight: 700;
          letter-spacing: -0.03em;
        }

        .brand-mark {
          width: 44px;
          height: 44px;
          display: grid;
          place-items: center;
          border-radius: 14px;
          background: linear-gradient(135deg, var(--lemon), var(--lime));
          box-shadow: 0 14px 28px rgba(255, 217, 90, 0.32);
        }

        .brand-text {
          font-size: 18px;
        }

        .nav {
          display: flex;
          flex-wrap: wrap;
          gap: 18px;
          color: var(--ink-soft);
          font-size: 14px;
        }

        .hero {
          display: grid;
          grid-template-columns: minmax(0, 1.1fr) minmax(360px, 0.9fr);
          gap: 28px;
          align-items: center;
          padding: 18px 0 28px;
        }

        .eyebrow {
          margin: 0 0 12px;
          color: #6c8d2f;
          letter-spacing: 0.14em;
          font-size: 12px;
          text-transform: uppercase;
          font-weight: 700;
        }

        .hero-title,
        .section-heading h2 {
          margin: 0;
          font-family: "Noto Sans SC", sans-serif;
          font-size: clamp(36px, 6vw, 72px);
          line-height: 0.98;
          letter-spacing: -0.06em;
        }

        .hero-text {
          margin: 18px 0 0;
          max-width: 700px;
          font-size: 18px;
          line-height: 1.72;
          color: var(--ink-soft);
        }

        .hero-actions,
        .showcase-actions,
        .spotlight-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          margin-top: 24px;
        }

        .primary-cta,
        .secondary-cta,
        .mini-cta {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-height: 52px;
          padding: 0 18px;
          border-radius: 999px;
          transition: transform 0.22s ease, box-shadow 0.22s ease, background 0.22s ease;
        }

        .primary-cta,
        .mini-cta.strong {
          color: #213117;
          background: linear-gradient(135deg, var(--lemon), var(--lime));
          box-shadow: 0 16px 28px rgba(165, 207, 91, 0.28);
        }

        .secondary-cta,
        .mini-cta {
          color: var(--ink);
          background: rgba(255, 255, 255, 0.84);
          border: 1px solid rgba(16, 43, 29, 0.08);
        }

        .primary-cta:hover,
        .secondary-cta:hover,
        .mini-cta:hover {
          transform: translateY(-2px);
        }

        .primary-cta.small,
        .secondary-cta.small {
          min-height: 46px;
          padding: 0 16px;
        }

        .stat-row {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 12px;
          margin-top: 28px;
        }

        .stat-card,
        .feature-card,
        .showcase-card,
        .theme-card,
        .download-card,
        .faq-list article,
        .spotlight {
          background: var(--card);
          border: 1px solid rgba(255, 255, 255, 0.54);
          box-shadow: var(--shadow);
          backdrop-filter: blur(18px);
        }

        .stat-card {
          padding: 18px;
          border-radius: 24px;
        }

        .stat-value {
          font-size: 28px;
          font-weight: 700;
          letter-spacing: -0.05em;
        }

        .stat-label {
          margin-top: 8px;
          color: var(--ink-soft);
          font-size: 13px;
          line-height: 1.5;
        }

        .spotlight {
          position: relative;
          overflow: hidden;
          border-radius: 34px;
          padding: 20px;
        }

        .spotlight::before {
          content: "";
          position: absolute;
          width: 240px;
          height: 240px;
          border-radius: 50%;
          background: rgba(255, 217, 90, 0.28);
          right: -60px;
          top: -60px;
          filter: blur(8px);
        }

        .spotlight-media {
          position: relative;
          aspect-ratio: 1.1 / 1;
          overflow: hidden;
          border-radius: 26px;
        }

        .spotlight-media img {
          width: 100%;
          height: 100%;
          object-fit: cover;
          display: block;
        }

        .floating-chip {
          position: absolute;
          left: 18px;
          bottom: 18px;
          padding: 10px 14px;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.9);
          font-size: 12px;
          font-weight: 700;
          letter-spacing: 0.06em;
          text-transform: uppercase;
        }

        .spotlight-body {
          position: relative;
          z-index: 1;
          margin-top: 18px;
        }

        .spotlight-label {
          color: var(--ink-soft);
          font-size: 12px;
          text-transform: uppercase;
          letter-spacing: 0.08em;
        }

        .spotlight-body h2 {
          margin: 8px 0 0;
          font-size: 34px;
          line-height: 1.05;
          letter-spacing: -0.05em;
        }

        .spotlight-body p {
          margin: 12px 0 0;
          color: var(--ink-soft);
          line-height: 1.7;
        }

        .voice-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 16px;
        }

        .voice-tag {
          padding: 10px 12px;
          border-radius: 14px;
          background: rgba(255, 255, 255, 0.72);
          font-size: 12px;
          color: var(--ink-soft);
        }

        audio {
          width: 100%;
          margin-top: 16px;
        }

        .feature-section,
        .themes-section,
        .download-section,
        .faq-section {
          margin-top: 84px;
        }

        .section-heading {
          max-width: 760px;
          margin-bottom: 28px;
        }

        .section-heading h2 {
          font-size: clamp(28px, 4vw, 52px);
        }

        .feature-grid {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 16px;
        }

        .feature-card {
          padding: 22px;
          border-radius: 28px;
        }

        .feature-icon {
          width: 54px;
          height: 54px;
          border-radius: 16px;
          display: grid;
          place-items: center;
          background: linear-gradient(135deg, rgba(255, 217, 90, 0.9), rgba(165, 207, 91, 0.9));
          margin-bottom: 18px;
          position: relative;
        }

        .feature-icon::before,
        .feature-icon::after {
          content: "";
          position: absolute;
          background: #163021;
          opacity: 0.88;
        }

        .feature-icon.stack::before {
          width: 24px;
          height: 18px;
          top: 14px;
          left: 15px;
          border-radius: 8px;
          box-shadow: 0 8px 0 rgba(22, 48, 33, 0.4), 0 16px 0 rgba(22, 48, 33, 0.24);
        }

        .feature-icon.dial::before {
          inset: 11px;
          border: 4px solid #163021;
          border-radius: 50%;
          background: transparent;
        }

        .feature-icon.dial::after {
          width: 4px;
          height: 16px;
          top: 12px;
          left: 25px;
          transform: rotate(32deg);
          transform-origin: bottom center;
          border-radius: 999px;
        }

        .feature-icon.spark::before {
          width: 6px;
          height: 28px;
          top: 13px;
          left: 24px;
          border-radius: 999px;
        }

        .feature-icon.spark::after {
          width: 28px;
          height: 6px;
          top: 24px;
          left: 13px;
          border-radius: 999px;
        }

        .feature-icon.wave::before {
          width: 30px;
          height: 18px;
          left: 12px;
          top: 18px;
          border-bottom: 4px solid #163021;
          border-top: 0;
          background: transparent;
          border-radius: 0 0 24px 24px;
        }

        .feature-icon.wave::after {
          width: 18px;
          height: 18px;
          left: 18px;
          top: 10px;
          border: 4px solid #163021;
          border-color: #163021 transparent transparent transparent;
          border-radius: 50%;
          background: transparent;
        }

        .feature-card h3,
        .showcase-card h3,
        .download-card h3,
        .faq-list h3 {
          margin: 0;
          font-size: 22px;
          line-height: 1.25;
          letter-spacing: -0.03em;
        }

        .feature-card p,
        .showcase-card p,
        .download-card p,
        .faq-list p {
          margin: 10px 0 0;
          color: var(--ink-soft);
          line-height: 1.7;
        }

        .showcase {
          margin-top: 84px;
          display: grid;
          grid-template-columns: 1.1fr 0.9fr;
          gap: 16px;
        }

        .showcase-card {
          padding: 28px;
          border-radius: 32px;
        }

        .theme-orbit {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          margin-top: 18px;
        }

        .orbit-pill {
          padding: 11px 14px;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.8);
          font-size: 13px;
          font-weight: 600;
        }

        .theme-grid {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 18px;
        }

        .theme-card {
          overflow: hidden;
          border-radius: 30px;
        }

        .theme-cover {
          aspect-ratio: 1.25 / 1;
          overflow: hidden;
        }

        .theme-cover img {
          display: block;
          width: 100%;
          height: 100%;
          object-fit: cover;
          transition: transform 0.35s ease;
        }

        .theme-card:hover .theme-cover img {
          transform: scale(1.04);
        }

        .theme-body {
          padding: 22px;
        }

        .theme-meta {
          color: var(--ink-soft);
          font-size: 13px;
          margin-bottom: 8px;
        }

        .theme-actions {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          margin-top: 18px;
        }

        .tiny-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          min-height: 42px;
          padding: 0 14px;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.88);
          border: 1px solid rgba(16, 43, 29, 0.08);
          color: var(--ink);
        }

        .tiny-btn.strong {
          background: linear-gradient(135deg, var(--lemon), var(--lime));
          color: #213117;
          font-weight: 700;
        }

        .download-layout {
          display: grid;
          grid-template-columns: 0.9fr 1.1fr;
          gap: 18px;
          align-items: start;
        }

        .download-copy {
          padding: 26px;
          border-radius: 30px;
          background: rgba(255, 255, 255, 0.78);
          border: 1px solid rgba(255, 255, 255, 0.54);
          box-shadow: var(--shadow);
        }

        .download-notes {
          margin: 18px 0 0;
          padding-left: 18px;
          color: var(--ink-soft);
          line-height: 1.8;
        }

        .download-cards {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 16px;
        }

        .download-card {
          padding: 22px;
          border-radius: 28px;
        }

        .download-label {
          display: inline-flex;
          padding: 8px 12px;
          border-radius: 999px;
          background: rgba(255, 255, 255, 0.8);
          font-size: 12px;
          color: var(--ink-soft);
          margin-bottom: 14px;
        }

        .download-size {
          margin-top: 12px;
          color: var(--ink-soft);
          font-size: 13px;
        }

        .faq-list {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 16px;
        }

        .faq-list article {
          padding: 24px;
          border-radius: 28px;
        }

        .footer {
          margin-top: 84px;
          padding: 28px 0 12px;
          display: flex;
          justify-content: space-between;
          gap: 18px;
          flex-wrap: wrap;
          color: var(--ink-soft);
          border-top: 1px solid var(--line);
        }

        code {
          padding: 4px 8px;
          border-radius: 10px;
          background: rgba(255, 255, 255, 0.7);
        }

        @media (max-width: 1080px) {
          .hero,
          .showcase,
          .download-layout,
          .feature-grid,
          .theme-grid,
          .faq-list {
            grid-template-columns: 1fr;
          }

          .download-cards {
            grid-template-columns: 1fr 1fr;
          }
        }

        @media (max-width: 720px) {
          .page-shell {
            padding: 18px 14px 40px;
          }

          .topbar {
            position: static;
            align-items: flex-start;
            flex-direction: column;
          }

          .nav {
            gap: 12px;
          }

          .stat-row,
          .download-cards {
            grid-template-columns: 1fr;
          }

          .hero-title,
          .section-heading h2 {
            font-size: 38px;
          }

          .spotlight {
            padding: 16px;
          }
        }
        """
    ).strip() + "\n"


def build_site_js() -> str:
    return textwrap.dedent(
        """
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
        """
    ).strip() + "\n"


def build_docs_readme() -> str:
    return textwrap.dedent(
        """
        # GitHub Pages 发布

        这个目录已经是可直接发布的静态站点。

        ## 打开方式

        1. 把整个仓库推到 GitHub。
        2. 进入仓库 `Settings -> Pages`。
        3. `Source` 选择 `Deploy from a branch`。
        4. Branch 选择 `main`，Folder 选择 `/docs`。
        5. 保存后等待 GitHub Pages 完成部署。

        ## 站点内容

        - 首页宣传站：`/docs/index.html`
        - 在线体验版：`/docs/app/index.html`
        - Mac 下载包：`/docs/downloads/*.dmg`
        - 主题封面：`/docs/assets/themes`
        - 主题试听：`/docs/assets/audio`

        ## 重新生成

        ```bash
        python3 scripts/build_marketing_site.py
        ```
        """
    ).strip() + "\n"


def main() -> None:
    reset_dir(DOCS)
    copy_online_demo()
    themes = collect_themes()
    site_data = build_site_data(themes)

    write_text(DOCS / "index.html", build_index_html(site_data))
    write_text(DOCS / "styles.css", build_styles())
    write_text(DOCS / "site.js", build_site_js())
    write_text(DOCS / "README.md", build_docs_readme())

    print(f"Marketing site built at: {DOCS}")


if __name__ == "__main__":
    main()
