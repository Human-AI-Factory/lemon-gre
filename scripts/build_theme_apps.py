from __future__ import annotations

import argparse
import json
import math
import plistlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
APPS_ROOT = ROOT / "apps"
VOICE_ROOT = ROOT / "voice-samples"
VENDOR_ROOT = ROOT / "vendor"


THEMES = [
    {
        "dir_name": "清爽柠檬",
        "slug": "qing-shuang-ning-meng",
        "display_name": "Lemon GRE - 清爽柠檬",
        "display_title": "Lemon GRE · 清爽柠檬",
        "brand_copy": "像咬开一片冰镇柠檬一样清醒，单词按顺序回来，熟词只做低频召回。",
        "icon_kind": "lemon",
        "colors": {
            "bgCream": "#f7f4de",
            "bgMint": "#edf7e4",
            "ink": "#143a2b",
            "inkSoft": "#4b6556",
            "lemon": "#ffd75d",
            "lime": "#9fca57",
            "limeDeep": "#6f9d2d",
            "mint": "#dff1d2",
            "warning": "#ffb347",
            "danger": "#e67452",
        },
        "voices": {
            "en": ["Samantha", "Eddy (英语（美国）)", "Reed (英语（美国）)"],
            "zh": ["Tingting", "Eddy (中文（中国大陆）)", "Reed (中文（中国大陆）)"],
        },
    },
    {
        "dir_name": "烟熏玫瑰",
        "slug": "yan-xun-mei-gui",
        "display_name": "Lemon GRE - 烟熏玫瑰",
        "display_title": "Lemon GRE · 烟熏玫瑰",
        "brand_copy": "暗红、烟紫和一点夜色，把单词背成一张带香气的复古卡片。",
        "icon_kind": "rose",
        "colors": {
            "bgCream": "#2c1825",
            "bgMint": "#60324a",
            "ink": "#fff1f5",
            "inkSoft": "#e0becd",
            "lemon": "#f2a2bc",
            "lime": "#b56f86",
            "limeDeep": "#8d445c",
            "mint": "#6a3b54",
            "warning": "#f5b46a",
            "danger": "#ff8b8b",
        },
        "voices": {
            "en": ["Moira", "Karen", "Eddy (英语（英国）)"],
            "zh": ["Meijia", "Sandy (中文（台湾）)", "Flo (中文（台湾）)"],
        },
    },
    {
        "dir_name": "魅力樱桃",
        "slug": "mei-li-ying-tao",
        "display_name": "Lemon GRE - 魅力樱桃",
        "display_title": "Lemon GRE · 魅力樱桃",
        "brand_copy": "高饱和樱桃红配一点俏皮感，让单词像糖渍果子一样更容易记住。",
        "icon_kind": "cherry",
        "colors": {
            "bgCream": "#fff1f4",
            "bgMint": "#ffe1ea",
            "ink": "#531a2c",
            "inkSoft": "#8a445f",
            "lemon": "#ff94b5",
            "lime": "#ff4f7d",
            "limeDeep": "#c5255e",
            "mint": "#ffd3df",
            "warning": "#ffca80",
            "danger": "#ff5b5b",
        },
        "voices": {
            "en": ["Karen", "Samantha", "Flo (英语（美国）)"],
            "zh": ["Flo (中文（中国大陆）)", "Tingting", "Eddy (中文（中国大陆）)"],
        },
    },
    {
        "dir_name": "阳光海盐",
        "slug": "yang-guang-hai-yan",
        "display_name": "Lemon GRE - 阳光海盐",
        "display_title": "Lemon GRE · 阳光海盐",
        "brand_copy": "海风、阳光和盐粒感的配色，会把这套背词页面拉得更明亮也更松弛。",
        "icon_kind": "sea",
        "colors": {
            "bgCream": "#fff7dd",
            "bgMint": "#dff6ff",
            "ink": "#173a52",
            "inkSoft": "#5e7b92",
            "lemon": "#ffd36b",
            "lime": "#55c2df",
            "limeDeep": "#258ca8",
            "mint": "#c8eef9",
            "warning": "#ffbf67",
            "danger": "#ff7b7b",
        },
        "voices": {
            "en": ["Daniel", "Eddy (英语（英国）)", "Reed (英语（英国）)"],
            "zh": ["Reed (中文（中国大陆）)", "Eddy (中文（中国大陆）)", "Tingting"],
        },
    },
    {
        "dir_name": "柴柴老头",
        "slug": "chai-chai-lao-tou",
        "display_name": "Lemon GRE - 柴柴老头",
        "display_title": "Lemon GRE · 柴柴老头",
        "brand_copy": "暖木色、柴犬脸和一点老派气质，让这版更像一位会碎碎念的背词搭子。",
        "icon_kind": "shiba",
        "colors": {
            "bgCream": "#fff4e6",
            "bgMint": "#f6e6d2",
            "ink": "#4a2d16",
            "inkSoft": "#866044",
            "lemon": "#ffcf88",
            "lime": "#d88f4d",
            "limeDeep": "#9a6233",
            "mint": "#f2dcc4",
            "warning": "#f0b264",
            "danger": "#db7650",
        },
        "voices": {
            "en": ["Grandpa (英语（美国）)", "Grandma (英语（美国）)", "Ralph"],
            "zh": ["Grandpa (中文（中国大陆）)", "Grandma (中文（中国大陆）)", "Tingting"],
        },
    },
    {
        "dir_name": "机械小子",
        "slug": "ji-xie-xiao-zi",
        "display_name": "Lemon GRE - 机械小子",
        "display_title": "Lemon GRE · 机械小子",
        "brand_copy": "硬朗的金属蓝和发光面板，把背词做成一台会说话的小型学习机器。",
        "icon_kind": "robot",
        "colors": {
            "bgCream": "#0e1624",
            "bgMint": "#18253a",
            "ink": "#f3fbff",
            "inkSoft": "#8fb3c6",
            "lemon": "#61e3ff",
            "lime": "#34c9eb",
            "limeDeep": "#0f83b5",
            "mint": "#183147",
            "warning": "#ffc66d",
            "danger": "#ff7c7c",
        },
        "voices": {
            "en": ["Zarvox", "Eddy (英语（美国）)", "Reed (英语（美国）)"],
            "zh": ["Rocko (中文（中国大陆）)", "Eddy (中文（中国大陆）)", "Reed (中文（中国大陆）)"],
        },
    },
]


SERVE_SCRIPT = textwrap.dedent(
    """
    from __future__ import annotations

    import argparse
    import os
    import socket
    import webbrowser
    from functools import partial
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    from pathlib import Path


    SCRIPT_PATH = Path(__file__).resolve()
    RELEASE_ROOT = SCRIPT_PATH.parents[1]
    WEB_ROOT = RELEASE_ROOT / "web"


    class ThemeHandler(SimpleHTTPRequestHandler):
        extensions_map = {
            **SimpleHTTPRequestHandler.extensions_map,
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".svg": "image/svg+xml",
            ".webmanifest": "application/manifest+json; charset=utf-8",
        }

        def end_headers(self) -> None:
            self.send_header("Cache-Control", "no-store")
            super().end_headers()


    def get_local_ips() -> list[str]:
        ips: set[str] = set()
        try:
            for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
                ip = info[4][0]
                if not ip.startswith("127."):
                    ips.add(ip)
        except OSError:
            pass

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("8.8.8.8", 80))
                ip = sock.getsockname()[0]
                if not ip.startswith("127."):
                    ips.add(ip)
        except OSError:
            pass

        return sorted(ips)


    def main() -> None:
        parser = argparse.ArgumentParser(description="Serve release assets.")
        parser.add_argument("--host", default="127.0.0.1")
        parser.add_argument("--port", type=int, default=43123)
        parser.add_argument("--open", action="store_true")
        args = parser.parse_args()

        handler = partial(ThemeHandler, directory=os.fspath(WEB_ROOT))
        server = ThreadingHTTPServer((args.host, args.port), handler)
        local_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
        local_url = f"http://{local_host}:{args.port}/index.html"

        print(f"Serving {WEB_ROOT}")
        print(f"Local: {local_url}")
        if args.host == "0.0.0.0":
            for ip in get_local_ips():
                print(f"LAN:   http://{ip}:{args.port}/index.html")

        if args.open:
            webbrowser.open(local_url)

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()


    if __name__ == "__main__":
        main()
    """
).strip() + "\n"


WINDOWS_PS1 = textwrap.dedent(
    """
    param(
        [switch]$Share,
        [int]$Port = 43123
    )

    $ErrorActionPreference = "Stop"
    $releaseRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
    $webRoot = Resolve-Path (Join-Path $releaseRoot "web")
    $prefix = if ($Share) { "http://*:$Port/" } else { "http://127.0.0.1:$Port/" }
    $openUrl = "http://127.0.0.1:$Port/index.html"

    $mimeTypes = @{
        ".html" = "text/html; charset=utf-8"
        ".js" = "application/javascript; charset=utf-8"
        ".json" = "application/json; charset=utf-8"
        ".png" = "image/png"
        ".svg" = "image/svg+xml"
        ".webmanifest" = "application/manifest+json; charset=utf-8"
    }

    function Get-LanAddresses {
        try {
            return [System.Net.Dns]::GetHostAddresses([System.Net.Dns]::GetHostName()) |
                Where-Object { $_.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork -and -not $_.ToString().StartsWith("127.") } |
                ForEach-Object { $_.ToString() } |
                Select-Object -Unique
        } catch {
            return @()
        }
    }

    $listener = [System.Net.HttpListener]::new()
    $listener.Prefixes.Add($prefix)
    $listener.Start()

    Write-Host "Serving $webRoot"
    Write-Host "Local: $openUrl"
    if ($Share) {
        Get-LanAddresses | ForEach-Object {
            Write-Host ("LAN:   http://{0}:{1}/index.html" -f $_, $Port)
        }
    }

    Start-Process $openUrl | Out-Null

    try {
        while ($listener.IsListening) {
            $context = $listener.GetContext()
            $requestPath = [Uri]::UnescapeDataString($context.Request.Url.AbsolutePath.TrimStart('/'))
            if ([string]::IsNullOrWhiteSpace($requestPath)) {
                $requestPath = "index.html"
            }

            $targetPath = Join-Path $webRoot $requestPath
            if (Test-Path $targetPath -PathType Container) {
                $targetPath = Join-Path $targetPath "index.html"
            }

            if (-not (Test-Path $targetPath -PathType Leaf)) {
                $context.Response.StatusCode = 404
                $buffer = [System.Text.Encoding]::UTF8.GetBytes("Not Found")
                $context.Response.OutputStream.Write($buffer, 0, $buffer.Length)
                $context.Response.OutputStream.Close()
                continue
            }

            $ext = [System.IO.Path]::GetExtension($targetPath).ToLowerInvariant()
            $context.Response.ContentType = $mimeTypes[$ext]
            if (-not $context.Response.ContentType) {
                $context.Response.ContentType = "application/octet-stream"
            }

            $bytes = [System.IO.File]::ReadAllBytes($targetPath)
            $context.Response.ContentLength64 = $bytes.Length
            $context.Response.OutputStream.Write($bytes, 0, $bytes.Length)
            $context.Response.OutputStream.Close()
        }
    } finally {
        $listener.Stop()
        $listener.Close()
    }
    """
).strip() + "\n"


MAC_SHARE_SCRIPT = textwrap.dedent(
    """
    #!/bin/zsh
    set -e

    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

    if command -v python3 >/dev/null 2>&1; then
      cd "$ROOT_DIR"
      exec python3 tools/serve.py --host 0.0.0.0 --open
    fi

    echo "未找到 python3，无法启动局域网分享。"
    exit 1
    """
).strip() + "\n"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def hex_color(value: str) -> tuple[int, int, int, int]:
    rgb = ImageColor.getrgb(value)
    return rgb[0], rgb[1], rgb[2], 255


def mix(a: tuple[int, int, int, int], b: tuple[int, int, int, int], t: float) -> tuple[int, int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


def vertical_gradient(size: int, top: tuple[int, int, int, int], bottom: tuple[int, int, int, int]) -> Image.Image:
    image = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(image)
    for y in range(size):
        t = y / max(size - 1, 1)
        draw.line((0, y, size, y), fill=mix(top, bottom, t))
    return image


def add_glow(base: Image.Image, bbox: tuple[int, int, int, int], color: tuple[int, int, int, int], blur: int = 80, alpha: int = 150) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    tinted = (color[0], color[1], color[2], alpha)
    draw.ellipse(bbox, fill=tinted)
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(blur)))


def rounded_mask(size: int, radius: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
    return mask


def draw_lemon(draw: ImageDraw.ImageDraw, size: int) -> None:
    center = size * 0.54
    r = size * 0.24
    draw.ellipse((center - r, size * 0.27, center + r, size * 0.75), fill=(255, 236, 148, 255), outline=(255, 248, 210, 255), width=18)
    inner_r = r * 0.8
    draw.ellipse((center - inner_r, size * 0.31, center + inner_r, size * 0.71), outline=(255, 248, 220, 200), width=16)
    for angle in range(-50, 70, 30):
        x = center + math.cos(math.radians(angle)) * inner_r
        y = size * 0.51 + math.sin(math.radians(angle)) * inner_r
        draw.line((center, size * 0.51, x, y), fill=(255, 249, 229, 235), width=10)
    draw.ellipse((size * 0.22, size * 0.18, size * 0.42, size * 0.34), fill=(124, 182, 63, 255))
    draw.ellipse((size * 0.34, size * 0.12, size * 0.54, size * 0.28), fill=(155, 209, 94, 255))


def draw_rose(draw: ImageDraw.ImageDraw, size: int) -> None:
    petals = [
        ((0.38, 0.24, 0.66, 0.56), (242, 162, 188, 255)),
        ((0.30, 0.34, 0.56, 0.68), (219, 112, 147, 255)),
        ((0.44, 0.34, 0.72, 0.68), (193, 86, 129, 255)),
        ((0.37, 0.42, 0.63, 0.77), (141, 68, 92, 255)),
    ]
    for box, fill in petals:
        draw.ellipse((size * box[0], size * box[1], size * box[2], size * box[3]), fill=fill)
    draw.arc((size * 0.39, size * 0.31, size * 0.61, size * 0.52), 190, 360, fill=(255, 232, 239, 220), width=12)
    draw.arc((size * 0.41, size * 0.41, size * 0.58, size * 0.60), 190, 360, fill=(255, 232, 239, 220), width=12)
    draw.arc((size * 0.25, size * 0.14, size * 0.79, size * 0.86), 20, 120, fill=(240, 210, 222, 80), width=20)
    draw.arc((size * 0.21, size * 0.18, size * 0.73, size * 0.90), 10, 110, fill=(240, 210, 222, 60), width=14)


def draw_cherry(draw: ImageDraw.ImageDraw, size: int) -> None:
    draw.line((size * 0.45, size * 0.26, size * 0.56, size * 0.45), fill=(88, 117, 48, 255), width=16)
    draw.line((size * 0.60, size * 0.22, size * 0.58, size * 0.46), fill=(88, 117, 48, 255), width=16)
    draw.line((size * 0.52, size * 0.22, size * 0.60, size * 0.18), fill=(88, 117, 48, 255), width=14)
    draw.ellipse((size * 0.26, size * 0.42, size * 0.56, size * 0.72), fill=(255, 86, 120, 255))
    draw.ellipse((size * 0.48, size * 0.40, size * 0.78, size * 0.70), fill=(215, 37, 94, 255))
    draw.ellipse((size * 0.34, size * 0.48, size * 0.42, size * 0.56), fill=(255, 210, 224, 180))
    draw.ellipse((size * 0.56, size * 0.46, size * 0.64, size * 0.54), fill=(255, 210, 224, 180))


def draw_sea(draw: ImageDraw.ImageDraw, size: int) -> None:
    draw.ellipse((size * 0.60, size * 0.15, size * 0.84, size * 0.39), fill=(255, 222, 118, 255))
    draw.pieslice((size * 0.18, size * 0.30, size * 0.78, size * 0.92), 200, 360, fill=(85, 194, 223, 255))
    draw.pieslice((size * 0.12, size * 0.42, size * 0.70, size * 0.98), 180, 340, fill=(37, 140, 168, 255))
    for x, y, scale in [(0.34, 0.22, 0.05), (0.46, 0.18, 0.04), (0.72, 0.50, 0.04)]:
        cx = size * x
        cy = size * y
        r = size * scale
        draw.line((cx - r, cy, cx + r, cy), fill=(255, 250, 240, 235), width=10)
        draw.line((cx, cy - r, cx, cy + r), fill=(255, 250, 240, 235), width=10)


def draw_shiba(draw: ImageDraw.ImageDraw, size: int) -> None:
    draw.polygon([(size * 0.30, size * 0.24), (size * 0.42, size * 0.08), (size * 0.46, size * 0.28)], fill=(216, 143, 77, 255))
    draw.polygon([(size * 0.54, size * 0.28), (size * 0.58, size * 0.08), (size * 0.70, size * 0.24)], fill=(216, 143, 77, 255))
    draw.ellipse((size * 0.22, size * 0.22, size * 0.78, size * 0.78), fill=(216, 143, 77, 255))
    draw.ellipse((size * 0.30, size * 0.38, size * 0.70, size * 0.78), fill=(255, 239, 220, 255))
    draw.ellipse((size * 0.36, size * 0.44, size * 0.44, size * 0.52), fill=(61, 42, 26, 255))
    draw.ellipse((size * 0.56, size * 0.44, size * 0.64, size * 0.52), fill=(61, 42, 26, 255))
    draw.ellipse((size * 0.46, size * 0.54, size * 0.54, size * 0.61), fill=(61, 42, 26, 255))
    draw.arc((size * 0.38, size * 0.53, size * 0.50, size * 0.70), 20, 160, fill=(61, 42, 26, 255), width=10)
    draw.arc((size * 0.50, size * 0.53, size * 0.62, size * 0.70), 20, 160, fill=(61, 42, 26, 255), width=10)
    draw.line((size * 0.33, size * 0.36, size * 0.42, size * 0.33), fill=(175, 175, 175, 255), width=10)
    draw.line((size * 0.58, size * 0.33, size * 0.67, size * 0.36), fill=(175, 175, 175, 255), width=10)


def draw_robot(draw: ImageDraw.ImageDraw, size: int) -> None:
    draw.rounded_rectangle((size * 0.25, size * 0.22, size * 0.75, size * 0.72), radius=int(size * 0.1), fill=(36, 72, 102, 255))
    draw.rounded_rectangle((size * 0.31, size * 0.28, size * 0.69, size * 0.60), radius=int(size * 0.07), fill=(97, 227, 255, 110))
    draw.ellipse((size * 0.37, size * 0.38, size * 0.46, size * 0.47), fill=(97, 227, 255, 255))
    draw.ellipse((size * 0.54, size * 0.38, size * 0.63, size * 0.47), fill=(97, 227, 255, 255))
    for idx in range(5):
        x = size * 0.38 + idx * size * 0.06
        draw.line((x, size * 0.56, x + size * 0.03, size * 0.56), fill=(243, 251, 255, 255), width=8)
    draw.line((size * 0.50, size * 0.12, size * 0.50, size * 0.22), fill=(97, 227, 255, 255), width=12)
    draw.ellipse((size * 0.45, size * 0.06, size * 0.55, size * 0.16), fill=(97, 227, 255, 255))
    draw.line((size * 0.29, size * 0.72, size * 0.24, size * 0.84), fill=(97, 227, 255, 255), width=12)
    draw.line((size * 0.71, size * 0.72, size * 0.76, size * 0.84), fill=(97, 227, 255, 255), width=12)


def build_icon(theme: dict, size: int = 1024) -> Image.Image:
    colors = theme["colors"]
    top = hex_color(colors["bgCream"])
    bottom = hex_color(colors["bgMint"])
    image = vertical_gradient(size, top, bottom)
    add_glow(image, (int(size * 0.54), int(size * 0.06), int(size * 1.03), int(size * 0.55)), hex_color(colors["lemon"]), blur=110, alpha=110)
    add_glow(image, (int(size * -0.08), int(size * 0.55), int(size * 0.42), int(size * 1.02)), hex_color(colors["lime"]), blur=90, alpha=95)

    symbol = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(symbol)
    kind = theme["icon_kind"]
    if kind == "lemon":
        draw_lemon(draw, size)
    elif kind == "rose":
        draw_rose(draw, size)
    elif kind == "cherry":
        draw_cherry(draw, size)
    elif kind == "sea":
        draw_sea(draw, size)
    elif kind == "shiba":
        draw_shiba(draw, size)
    elif kind == "robot":
        draw_robot(draw, size)
    else:
        raise ValueError(f"Unknown icon kind: {kind}")

    shadow = symbol.copy().filter(ImageFilter.GaussianBlur(36))
    shadow_alpha = shadow.getchannel("A").point(lambda value: min(160, value))
    shadow.putalpha(shadow_alpha)
    image.alpha_composite(shadow, (0, 32))
    image.alpha_composite(symbol)

    card = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    card_draw = ImageDraw.Draw(card)
    card_draw.rounded_rectangle((size * 0.06, size * 0.06, size * 0.94, size * 0.94), radius=int(size * 0.22), outline=(255, 255, 255, 70), width=4)
    image.alpha_composite(card)

    mask = rounded_mask(size, int(size * 0.23))
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(image, (0, 0), mask)
    return output


def render_cover(theme: dict, icon: Image.Image) -> Image.Image:
    width, height = 1600, 1000
    bg = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    top = hex_color(theme["colors"]["bgCream"])
    bottom = hex_color(theme["colors"]["bgMint"])
    for y in range(height):
        t = y / max(height - 1, 1)
        color = mix(top, bottom, t)
        ImageDraw.Draw(bg).line((0, y, width, y), fill=color)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.ellipse((1080, -100, 1680, 500), fill=hex_color(theme["colors"]["lemon"]))
    overlay_draw.ellipse((-180, 520, 380, 1120), fill=hex_color(theme["colors"]["lime"]))
    bg.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(120)))

    icon_large = icon.resize((560, 560), Image.LANCZOS)
    shadow = Image.new("RGBA", icon_large.size, (0, 0, 0, 0))
    shadow.alpha_composite(icon_large.filter(ImageFilter.GaussianBlur(28)))
    shadow_alpha = shadow.getchannel("A").point(lambda value: min(180, value))
    shadow.putalpha(shadow_alpha)
    bg.alpha_composite(shadow, (520, 210))
    bg.alpha_composite(icon_large, (520, 170))

    try:
        font_path = Path(ImageFont.__file__).resolve().parent / "fonts" / "DejaVuSans-Bold.ttf"
        font = ImageFont.truetype(str(font_path), 62)
    except Exception:
        font = ImageFont.load_default()

    text_draw = ImageDraw.Draw(bg)
    text_draw.rounded_rectangle((90, 812, 520, 908), radius=38, fill=(255, 255, 255, 180))
    text_draw.text((132, 838), "LEMON GRE", fill=(25, 36, 48, 230), font=font)
    return bg


def create_iconset(icon_png: Path, icon_icns: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="lemon-gre-iconset-") as tmp:
        iconset = Path(tmp) / "app.iconset"
        iconset.mkdir(parents=True, exist_ok=True)
        base = Image.open(icon_png).convert("RGBA")
        sizes = [16, 32, 128, 256, 512]
        for size in sizes:
            for scale in [1, 2]:
                actual = size * scale
                name = f"icon_{size}x{size}{'@2x' if scale == 2 else ''}.png"
                base.resize((actual, actual), Image.LANCZOS).save(iconset / name)

        run(["iconutil", "-c", "icns", str(iconset), "-o", str(icon_icns)])


def theme_config_script(theme: dict) -> str:
    payload = {
        "appName": "Lemon GRE",
        "themeName": theme["dir_name"],
        "displayName": theme["display_title"],
        "brandTag": "Lemon GRE",
        "brandCopy": theme["brand_copy"],
        "colors": theme["colors"],
        "voices": theme["voices"],
    }
    return f"window.LEMON_GRE_THEME = {json.dumps(payload, ensure_ascii=False, indent=4)};\n"


def write_web(theme: dict, theme_dir: Path) -> None:
    web_dir = theme_dir / "web"
    reset_dir(web_dir)
    (web_dir / "data").mkdir(parents=True, exist_ok=True)
    (web_dir / "icons").mkdir(parents=True, exist_ok=True)
    (web_dir / "vendor").mkdir(parents=True, exist_ok=True)

    index_html = (ROOT / "index.html").read_text(encoding="utf-8")
    index_html = index_html.replace("<title>Lemon GRE</title>", f"<title>{theme['display_title']}</title>")
    index_html = index_html.replace('href="./icons/app-icon.svg" type="image/svg+xml"', 'href="./icons/app-icon.png" type="image/png"')
    index_html = index_html.replace('href="./icons/app-icon.svg">', 'href="./icons/app-icon.png">')
    write_text(web_dir / "index.html", index_html)

    manifest = {
        "name": theme["display_name"],
        "short_name": "Lemon GRE",
        "description": f"{theme['display_title']}：顺序翻页背 GRE 单词，支持熟悉度调频、低频召回和今日音频。",
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": theme["colors"]["bgCream"],
        "theme_color": theme["colors"]["lime"],
        "lang": "zh-CN",
        "icons": [
            {
                "src": "./icons/app-icon.png",
                "sizes": "1024x1024",
                "type": "image/png",
                "purpose": "any maskable",
            }
        ],
    }
    write_text(web_dir / "manifest.webmanifest", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

    sw_text = (ROOT / "sw.js").read_text(encoding="utf-8").replace("./icons/app-icon.svg", "./icons/app-icon.png")
    write_text(web_dir / "sw.js", sw_text)
    write_text(web_dir / "theme.config.js", theme_config_script(theme))

    shutil.copy2(ROOT / "data" / "gre3000-bank.js", web_dir / "data" / "gre3000-bank.js")
    shutil.copy2(VENDOR_ROOT / "vue.global.prod.js", web_dir / "vendor" / "vue.global.prod.js")
    shutil.copy2(VENDOR_ROOT / "xlsx.full.min.js", web_dir / "vendor" / "xlsx.full.min.js")


def write_support_files(theme: dict, theme_dir: Path) -> None:
    tools_dir = theme_dir / "tools"
    windows_dir = theme_dir / "windows"
    mobile_dir = theme_dir / "mobile"
    for path in [tools_dir, windows_dir, mobile_dir]:
        reset_dir(path)

    write_text(tools_dir / "serve.py", SERVE_SCRIPT)
    write_text(windows_dir / "start-local.ps1", WINDOWS_PS1)
    write_text(windows_dir / "启动.bat", "@echo off\r\nPowerShell -ExecutionPolicy Bypass -File \"%~dp0start-local.ps1\"\r\n")
    write_text(windows_dir / "分享到手机.bat", "@echo off\r\nPowerShell -ExecutionPolicy Bypass -File \"%~dp0start-local.ps1\" -Share\r\n")
    write_text(theme_dir / "分享到手机.command", MAC_SHARE_SCRIPT)
    run(["chmod", "+x", str(theme_dir / "分享到手机.command")])

    install_doc = textwrap.dedent(
        f"""
        # {theme['display_title']}

        电脑和手机在同一个 Wi‑Fi 下时：

        1. Mac 运行 [分享到手机.command]({theme_dir / '分享到手机.command'})。
        2. Windows 运行 [分享到手机.bat]({windows_dir / '分享到手机.bat'})。
        3. 在手机浏览器打开终端里输出的 `LAN` 地址。
        4. iPhone 用 Safari 添加到主屏幕，Android 用 Chrome 安装应用。
        """
    ).strip() + "\n"
    write_text(mobile_dir / "安装到手机.md", install_doc)

    sample = VOICE_ROOT / f"{theme['dir_name']}.aiff"
    if sample.exists():
        shutil.copy2(sample, theme_dir / "voice-preview.aiff")

    readme = textwrap.dedent(
        f"""
        # {theme['display_title']}

        - 原生 Mac App：[{theme['display_name']}.app]({theme_dir / 'macOS' / (theme['display_name'] + '.app')})
        - Mac 安装镜像：[{theme['display_name']}.dmg]({theme_dir / 'macOS' / (theme['display_name'] + '.dmg')})
        - Web 资源目录：[{theme_dir / 'web'}]({theme_dir / 'web'})
        - 预设英文音色：{", ".join(theme['voices']['en'])}
        - 预设中文音色：{", ".join(theme['voices']['zh'])}
        """
    ).strip() + "\n"
    write_text(theme_dir / "README.md", readme)


def swift_source() -> str:
    return textwrap.dedent(
        """
        import Cocoa
        import WebKit

        final class AppDelegate: NSObject, NSApplicationDelegate {
            var window: NSWindow?

            func applicationDidFinishLaunching(_ notification: Notification) {
                let config = WKWebViewConfiguration()
                config.websiteDataStore = .default()

                let webView = WKWebView(frame: .zero, configuration: config)
                webView.setValue(false, forKey: "drawsBackground")

                let window = NSWindow(
                    contentRect: NSRect(x: 0, y: 0, width: 440, height: 860),
                    styleMask: [.titled, .closable, .miniaturizable, .resizable],
                    backing: .buffered,
                    defer: false
                )
                window.center()
                window.minSize = NSSize(width: 400, height: 740)
                window.title = Bundle.main.object(forInfoDictionaryKey: "CFBundleDisplayName") as? String ?? "Lemon GRE"
                window.contentView = webView
                window.makeKeyAndOrderFront(nil)
                self.window = window

                if let resourceURL = Bundle.main.resourceURL {
                    let webRoot = resourceURL.appendingPathComponent("release/web", isDirectory: true)
                    let indexURL = webRoot.appendingPathComponent("index.html")
                    webView.loadFileURL(indexURL, allowingReadAccessTo: webRoot)
                }

                NSApp.activate(ignoringOtherApps: true)
            }

            func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
                true
            }
        }

        let app = NSApplication.shared
        let delegate = AppDelegate()
        app.setActivationPolicy(.regular)
        app.delegate = delegate
        app.run()
        """
    ).strip() + "\n"


def build_macos(theme: dict, theme_dir: Path) -> None:
    mac_dir = theme_dir / "macOS"
    reset_dir(mac_dir)

    display_name = theme["display_name"]
    app_dir = mac_dir / f"{display_name}.app"
    contents = app_dir / "Contents"
    resources = contents / "Resources"
    macos_bin = contents / "MacOS"
    release_dir = resources / "release"
    web_dir = theme_dir / "web"

    resources.mkdir(parents=True, exist_ok=True)
    macos_bin.mkdir(parents=True, exist_ok=True)
    shutil.copytree(web_dir, release_dir / "web", dirs_exist_ok=True)

    executable_name = "LemonGRELauncher"
    swift_file = mac_dir / "LemonGRELauncher.swift"
    write_text(swift_file, swift_source())
    run([
        "swiftc",
        "-O",
        "-framework", "Cocoa",
        "-framework", "WebKit",
        str(swift_file),
        "-o",
        str(macos_bin / executable_name),
    ])

    icon_icns = resources / "app-icon.icns"
    create_iconset(theme_dir / "web" / "icons" / "app-icon.png", icon_icns)

    info = {
        "CFBundleDevelopmentRegion": "zh_CN",
        "CFBundleDisplayName": display_name,
        "CFBundleExecutable": executable_name,
        "CFBundleIconFile": "app-icon.icns",
        "CFBundleIdentifier": f"com.ouzhang.lemongre.{theme['slug']}",
        "CFBundleInfoDictionaryVersion": "6.0",
        "CFBundleName": display_name,
        "CFBundlePackageType": "APPL",
        "CFBundleShortVersionString": "1.0.0",
        "CFBundleVersion": "1",
        "LSMinimumSystemVersion": "11.0",
        "NSHighResolutionCapable": True,
    }
    with (contents / "Info.plist").open("wb") as fh:
        plistlib.dump(info, fh)
    write_text(contents / "PkgInfo", "APPL????")

    dmg_path = mac_dir / f"{display_name}.dmg"
    with tempfile.TemporaryDirectory(prefix=f"{theme['slug']}-dmg-") as tmp:
        stage = Path(tmp) / display_name
        stage.mkdir(parents=True, exist_ok=True)
        shutil.copytree(app_dir, stage / app_dir.name)
        (stage / "Applications").symlink_to("/Applications")
        run([
            "hdiutil",
            "create",
            "-volname", display_name,
            "-srcfolder", str(stage),
            "-ov",
            "-format", "UDZO",
            str(dmg_path),
        ])


def build_visual_assets(theme: dict, theme_dir: Path) -> None:
    icons_dir = theme_dir / "web" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    icon = build_icon(theme)
    icon.save(icons_dir / "app-icon.png")
    cover = render_cover(theme, icon)
    cover.save(theme_dir / "cover.png")


def build_theme(theme: dict) -> None:
    theme_dir = APPS_ROOT / theme["dir_name"]
    theme_dir.mkdir(parents=True, exist_ok=True)
    write_web(theme, theme_dir)
    build_visual_assets(theme, theme_dir)
    write_support_files(theme, theme_dir)
    build_macos(theme, theme_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build all Lemon GRE theme apps.")
    parser.add_argument("themes", nargs="*", help="Optional theme directory names to build")
    args = parser.parse_args()

    selected = {name for name in args.themes}
    themes = [theme for theme in THEMES if not selected or theme["dir_name"] in selected]
    if not themes:
        raise SystemExit("No matching themes.")

    required = [
        ROOT / "index.html",
        ROOT / "sw.js",
        ROOT / "data" / "gre3000-bank.js",
        VENDOR_ROOT / "vue.global.prod.js",
        VENDOR_ROOT / "xlsx.full.min.js",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"Missing required source files: {missing}")

    for theme in themes:
        print(f"Building {theme['display_title']} ...")
        build_theme(theme)
        print(f"Built {theme['display_name']}")


if __name__ == "__main__":
    main()
