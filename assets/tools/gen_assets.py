#!/usr/bin/env python3
"""SnowLinux の自作素材 (壁紙・ロゴ・アイコン) を生成する。Apple の素材は使わない。

使い方: python3 -I assets/tools/gen_assets.py
出力:   assets/wallpapers/  assets/logo/  assets/icons/SnowLinux/
"""
import math
import os
import random

import cairo
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.abspath(os.path.join(HERE, ".."))


def out(*parts):
    p = os.path.join(ASSETS, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


# ======================================================================
# ロゴ: 雪の結晶
# ======================================================================

def snowflake_paths(cx, cy, r, arm_w):
    """6 本の腕と枝からなる雪の結晶を、SVG の path にする。"""
    d = []
    for k in range(6):
        a = math.radians(90 + 60 * k)
        ux, uy = math.cos(a), math.sin(a)
        tip = (cx + ux * r, cy - uy * r)
        d.append(f"M{cx:.2f} {cy:.2f}L{tip[0]:.2f} {tip[1]:.2f}")
        for frac, blen in ((0.52, 0.36), (0.78, 0.22)):
            bx, by = cx + ux * r * frac, cy - uy * r * frac
            for s in (-1, 1):
                b = a + s * math.radians(60)
                d.append(f"M{bx:.2f} {by:.2f}L{bx + math.cos(b) * r * blen:.2f} {by - math.sin(b) * r * blen:.2f}")
    return "".join(d)


def logo_mono(color="#2b2b2b"):
    p = snowflake_paths(32, 32, 28, 3)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
            f'<path d="{p}" fill="none" stroke="{color}" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/></svg>\n')


def logo_color():
    p = snowflake_paths(64, 64, 44, 3)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8dc0ff"/><stop offset="0.55" stop-color="#3f84e6"/><stop offset="1" stop-color="#1c55b8"/></linearGradient>
<linearGradient id="gl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0.85"/><stop offset="1" stop-color="#fff" stop-opacity="0.05"/></linearGradient>
</defs>
<circle cx="64" cy="64" r="60" fill="url(#bg)" stroke="#173f86" stroke-width="2"/>
<ellipse cx="64" cy="38" rx="46" ry="30" fill="url(#gl)"/>
<path d="{p}" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''


# ======================================================================
# 壁紙: 夕暮れの雪原
# ======================================================================

def ridge(x, seed, amp, base, rough):
    """なだらかな稜線 (正弦波の重ね合わせ)。"""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(5)]
    fr = [1.0, 2.3, 4.1, 7.7, 13.0]
    am = [1.0, 0.55, 0.28, 0.12 * rough, 0.05 * rough]
    return base + amp * sum(a * math.sin(f * x * 2 * math.pi + p) for a, f, p in zip(am, fr, ph))


def wallpaper(w=2560, h=1600):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    c = cairo.Context(s)
    # 空
    g = cairo.LinearGradient(0, 0, 0, h)
    for off, col in ((0.0, "#081d46"), (0.30, "#1a4688"), (0.55, "#5b92cf"), (0.72, "#a9cbea"), (0.86, "#dcebf8"), (1.0, "#f3f8fd")):
        c.set_source_rgb  # noqa
        g.add_color_stop_rgb(off, *[int(col[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    c.set_source(g)
    c.paint()
    # 星 (上のほうだけ、ほんの少し)
    rnd = random.Random(7)
    for _ in range(260):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h * 0.34)
        a = (1 - y / (h * 0.34)) * rnd.uniform(0.15, 0.7)
        c.arc(x, y, rnd.choice((0.8, 0.9, 1.1, 1.5)), 0, 6.28)
        c.set_source_rgba(1, 1, 1, a)
        c.fill()
    # 地平線のあたりの光
    glow = cairo.RadialGradient(w * 0.70, h * 0.66, 0, w * 0.70, h * 0.66, h * 0.62)
    glow.add_color_stop_rgba(0, 1.0, 0.96, 0.88, 0.60)
    glow.add_color_stop_rgba(0.5, 0.85, 0.92, 1.0, 0.22)
    glow.add_color_stop_rgba(1, 0.8, 0.9, 1.0, 0.0)
    c.set_source(glow)
    c.paint()

    # 空の部分を画像にしておく (山と雪原は、輪郭をぼかして重ねる)
    base = Image.frombuffer("RGBA", (w, h), bytes(s.get_data()), "raw", "BGRA", 0, 1).convert("RGB")

    # 山と雪原を、遠くから近くへ重ねる。遠いほど輪郭を強くぼかす (空気の遠近感。昔のアクア風のなめらかさ)
    layers = [
        # (種, 振幅, 基準の高さ, 起伏, 上の色, 下の色, ぼかし)
        (11, 0.060, 0.60, 1.0, "#9bbbe0", "#c7dcf0", 20),
        (23, 0.055, 0.66, 0.9, "#7da6d4", "#b8d1ea", 15),
        (37, 0.045, 0.73, 0.7, "#c4d9ee", "#e9f2fb", 11),
        (53, 0.035, 0.82, 0.5, "#e2edf8", "#f8fbff", 8),
        (71, 0.028, 0.91, 0.4, "#f3f8fd", "#ffffff", 5),
    ]
    rgb = lambda col: [int(col[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    for seed, amp, base_y, rough, top, bottom, blur in layers:
        n = 240
        pts = [(i / n * w, ridge(i / n, seed, amp, base_y, rough) * h) for i in range(n + 1)]
        top_y = min(y for _, y in pts)
        # 形 (輪郭) だけを白黒で描き、ぼかす
        m = cairo.ImageSurface(cairo.FORMAT_A8, w, h)
        mc = cairo.Context(m)
        mc.move_to(0, h)
        for px, py in pts:
            mc.line_to(px, py)
        mc.line_to(w, h)
        mc.close_path()
        mc.set_source_rgba(0, 0, 0, 1)
        mc.fill()
        mask = Image.frombuffer("L", (w, h), bytes(m.get_data()), "raw", "L", m.get_stride(), 1)
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
        # 色 (全面をグラデーションで塗る。透明部分の色が混ざって縁が暗くならないように)
        gs = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
        gc = cairo.Context(gs)
        lg = cairo.LinearGradient(0, top_y, 0, h)
        lg.add_color_stop_rgb(0, *rgb(top))
        lg.add_color_stop_rgb(1, *rgb(bottom))
        gc.set_source(lg)
        gc.paint()
        grad = Image.frombuffer("RGBA", (w, h), bytes(gs.get_data()), "raw", "BGRA", 0, 1).convert("RGB")
        base.paste(grad, (0, 0), mask)

    # 手前に、ごく薄い影を落として奥行きを出す
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shade = Image.linear_gradient("L").resize((w, h // 6)).point(lambda v: int(v * 0.35))
    sh.paste((153, 184, 230, 255), (0, h - h // 6), shade)
    base = Image.alpha_composite(base.convert("RGBA"), sh).convert("RGB")

    im = base
    # 階調の段差 (バンディング) を消すため、ごく弱いノイズを足す
    noise = Image.effect_noise((w, h), 7).convert("L")
    noise = noise.point(lambda v: v)  # 0..255
    base = Image.merge("RGB", (noise, noise, noise))
    from PIL import ImageChops
    im = ImageChops.add(im, ImageChops.subtract(base, Image.new("RGB", (w, h), (128, 128, 128))), scale=1.0, offset=0)
    return im


# ======================================================================
# アイコン (SVG)
# ======================================================================

def svg(body, defs="", size=128):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 128 128">'
            f"<defs>{defs}</defs>{body}</svg>\n")


def lin(id_, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{id_}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


BLUE_BACK = lin("fb", [(0, "#6ea8ec"), (1, "#3b72c8")])
BLUE_FRONT = lin("ff", [(0, "#9ccbfb"), (0.5, "#5a9be6"), (1, "#3f7fd8")])


def folder(glyph=""):
    defs = BLUE_BACK + BLUE_FRONT
    body = (
        '<path d="M12 34q0-6 6-6h28q5 0 8 4l5 6h51q6 0 6 6v58q0 6-6 6H18q-6 0-6-6z" fill="url(#fb)" stroke="#2c62b6" stroke-width="2"/>'
        '<rect x="20" y="46" width="88" height="46" rx="2" fill="#f7f7f7" stroke="#c9c9c9"/>'
        '<path d="M10 64q0-8 8-8h92q8 0 8 8v40q0 8-8 8H18q-8 0-8-8z" fill="url(#ff)" stroke="#2c62b6" stroke-width="2"/>'
        '<path d="M12 64q0-6 6-6h92q6 0 6 6" fill="none" stroke="#fff" stroke-opacity="0.7" stroke-width="2"/>'
        + (f'<g transform="translate(64 86)" fill="#fff" fill-opacity="0.9" stroke="none">{glyph}</g>' if glyph else "")
    )
    return svg(body, defs)


G_HOME = '<path d="M0-16L-18 0h6v14h8V4h8v10h8V0h6z"/>'
G_DOC = '<path d="M-11-16h14l8 8v24h-22z M3-16v8h8" fill-rule="evenodd"/>'
G_DOWN = '<path d="M-5-15h10v14h8L0 14-13-1h8z"/>'
G_MUSIC = '<path d="M-3-15l16-4v24a8 7 0 1 1-4-6v-14l-8 2v24a8 7 0 1 1-4-6z" transform="scale(.85) translate(-4 3)"/>'
G_PIC = '<path d="M-17 13V-12h34V13z M-13 9h26l-9-14-6 8-4-4z" fill-rule="evenodd"/><circle cx="8" cy="-6" r="3" fill="#4b8de2"/>'
G_VIDEO = '<path d="M-16-12h32v24h-32z M-12-8v4h4v-4z M8-8v4h4v-4z M-12 4v4h4v-4z M8 4v4h4v-4z" fill-rule="evenodd"/>'
G_DESK = '<path d="M-17-13h34v22h-34z M-5 9h10l3 6h-16z" fill-rule="evenodd"/>'
G_APPS = '<path d="M0-16L-13 14h5l2.5-7h11L8 14h5zM-3.5 3L0-7l3.5 10z" fill-rule="evenodd"/>'
G_UTIL = '<path d="M-15-2a15 15 0 0 1 21-14l-9 9 4 4 9-9a15 15 0 0 1-14 21L-8 14l-7-7z"/>'


def trash(full=False):
    defs = lin("m", [(0, "#a9a9a9"), (0.25, "#f2f2f2"), (0.55, "#cfcfcf"), (1, "#8d8d8d")], 0, 0, 1, 0)
    paper = ('<path d="M44 38l8-14 12 8 10-12 12 14z" fill="#fff" stroke="#bbb"/>'
             '<path d="M50 34l14-6 14 8" fill="#f0f0f0" stroke="#bbb"/>') if full else ""
    mesh = "".join(f'<path d="M{x} 44L{x + 6} 108" stroke="#7e7e7e" stroke-opacity="0.55" stroke-width="2"/>' for x in range(50, 84, 9))
    mesh += "".join(f'<path d="M42 {y}H86" stroke="#7e7e7e" stroke-opacity="0.45" stroke-width="2"/>' for y in (60, 76, 92))
    body = (
        '<ellipse cx="64" cy="114" rx="30" ry="5" fill="#000" fill-opacity="0.18"/>'
        + paper +
        '<path d="M36 40h56l-4 70q-1 6-8 6H48q-7 0-8-6z" fill="url(#m)" stroke="#6d6d6d" stroke-width="2"/>'
        + mesh +
        '<ellipse cx="64" cy="40" rx="29" ry="7" fill="#e6e6e6" stroke="#6d6d6d" stroke-width="2"/>'
        '<ellipse cx="64" cy="40" rx="24" ry="4.5" fill="#8f8f8f" fill-opacity="0.5"/>'
    )
    return svg(body, defs)


def harddisk():
    defs = lin("d", [(0, "#f6f6f6"), (0.45, "#cfcfcf"), (1, "#9a9a9a")]) + lin("t", [(0, "#ffffff"), (1, "#e2e2e2")])
    body = (
        '<ellipse cx="64" cy="106" rx="50" ry="6" fill="#000" fill-opacity="0.2"/>'
        '<path d="M12 70L22 36q2-6 8-6h68q6 0 8 6l10 34z" fill="url(#t)" stroke="#8a8a8a" stroke-width="2"/>'
        '<path d="M12 70h104v26q0 6-6 6H18q-6 0-6-6z" fill="url(#d)" stroke="#6d6d6d" stroke-width="2"/>'
        '<rect x="22" y="86" width="40" height="4" rx="2" fill="#7a7a7a" fill-opacity="0.7"/>'
        '<circle cx="100" cy="88" r="4.5" fill="#5aa4ff" stroke="#2b6ad0"/><circle cx="99" cy="87" r="1.6" fill="#fff"/>'
    )
    return svg(body, defs)


def usbdrive():
    defs = lin("d", [(0, "#fafafa"), (0.5, "#cfcfcf"), (1, "#9c9c9c")], 0, 0, 1, 0) + lin("c", [(0, "#e8e8e8"), (1, "#a9a9a9")])
    body = (
        '<ellipse cx="64" cy="116" rx="26" ry="4" fill="#000" fill-opacity="0.2"/>'
        '<rect x="48" y="14" width="32" height="30" rx="2" fill="url(#c)" stroke="#6d6d6d" stroke-width="2"/>'
        '<rect x="56" y="20" width="6" height="8" fill="#555"/><rect x="66" y="20" width="6" height="8" fill="#555"/>'
        '<path d="M40 44h48v66q0 6-6 6H46q-6 0-6-6z" fill="url(#d)" stroke="#6d6d6d" stroke-width="2"/>'
        '<rect x="56" y="82" width="16" height="22" rx="3" fill="#4b8de2" stroke="#2b5ea8"/>'
    )
    return svg(body, defs)


def optical():
    defs = ('<radialGradient id="s" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff"/><stop offset="0.5" stop-color="#d6e6f5"/><stop offset="1" stop-color="#a9b9c9"/></radialGradient>'
            '<linearGradient id="r" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff9aa2" stop-opacity="0.5"/><stop offset="0.5" stop-color="#9affc5" stop-opacity="0.45"/><stop offset="1" stop-color="#9ac2ff" stop-opacity="0.5"/></linearGradient>')
    body = ('<circle cx="64" cy="64" r="52" fill="url(#s)" stroke="#7d8a97" stroke-width="2"/>'
            '<circle cx="64" cy="64" r="52" fill="url(#r)"/>'
            '<circle cx="64" cy="64" r="16" fill="#f4f4f4" stroke="#7d8a97" stroke-width="2"/>'
            '<circle cx="64" cy="64" r="6" fill="#8d98a4"/>')
    return svg(body, defs)


def page(kind="text"):
    defs = lin("p", [(0, "#ffffff"), (1, "#e9e9e9")])
    body = ('<path d="M26 12h50l26 26v78H26z" fill="url(#p)" stroke="#9a9a9a" stroke-width="2"/>'
            '<path d="M76 12v26h26" fill="#dcdcdc" stroke="#9a9a9a" stroke-width="2" stroke-linejoin="round"/>')
    if kind == "text":
        body += "".join(f'<path d="M38 {y}h52" stroke="#a8a8a8" stroke-width="3" stroke-linecap="round"/>' for y in (54, 66, 78, 90, 102))
    else:
        body += ('<rect x="36" y="52" width="56" height="50" fill="#9fcdf7" stroke="#6a9fcf"/>'
                 '<path d="M36 102V88l16-14 12 10 10-8 18 14v12z" fill="#6cae5a"/><circle cx="78" cy="64" r="5" fill="#fff6cc"/>')
    return svg(body, defs)


def filemanager():
    defs = (lin("t", [(0, "#ececec"), (1, "#bcbcbc")]) + lin("s", [(0, "#dbe5f0"), (1, "#bccbdc")]))
    body = ('<rect x="10" y="18" width="108" height="92" rx="9" fill="#fff" stroke="#6b6b6b" stroke-width="2"/>'
            '<path d="M10 27q0-9 9-9h90q9 0 9 9v7H10z" fill="url(#t)" stroke="#6b6b6b" stroke-width="2"/>'
            '<circle cx="22" cy="27" r="4" fill="#f0473c"/><circle cx="34" cy="27" r="4" fill="#fbb91c"/><circle cx="46" cy="27" r="4" fill="#27c53c"/>'
            '<path d="M11 36h32v73q0 1-1 1H20q-9 0-9-9z" fill="url(#s)" stroke="#6b6b6b" stroke-width="1"/>'
            '<g transform="translate(75 72) scale(.55)"><path d="M-46-34q0-6 6-6h28q5 0 8 4l5 6h51q6 0 6 6v58q0 6-6 6H-40q-6 0-6-6z" fill="#5a9be6" stroke="#2c62b6" stroke-width="3"/></g>'
            '<g stroke="#8a97a6" stroke-width="3" stroke-linecap="round"><path d="M18 50h18M18 62h14M18 74h18"/></g>')
    return svg(body, defs)


def generate_icons(root):
    files = {}
    # 場所
    for name, glyph in (("folder", ""), ("inode-directory", ""), ("folder-open", ""),
                        ("user-home", G_HOME), ("folder-documents", G_DOC), ("folder-download", G_DOWN),
                        ("folder-music", G_MUSIC), ("folder-pictures", G_PIC), ("folder-videos", G_VIDEO),
                        ("user-desktop", G_DESK), ("folder-applications", G_APPS), ("folder-utilities", G_UTIL)):
        files[f"scalable/places/{name}.svg"] = folder(glyph)
    files["scalable/places/user-trash.svg"] = trash(False)
    files["scalable/places/user-trash-full.svg"] = trash(True)
    # 機器
    files["scalable/devices/drive-harddisk.svg"] = harddisk()
    files["scalable/devices/drive-removable-media.svg"] = usbdrive()
    files["scalable/devices/media-optical.svg"] = optical()
    # ファイル
    files["scalable/mimetypes/text-x-generic.svg"] = page("text")
    files["scalable/mimetypes/image-x-generic.svg"] = page("image")
    # アプリ
    fm = filemanager()
    for name in ("org.xfce.filemanager", "system-file-manager", "org.xfce.thunar", "thunar"):
        files[f"scalable/apps/{name}.svg"] = fm
    for rel, content in files.items():
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(content)
    with open(os.path.join(root, "index.theme"), "w") as f:
        f.write("""[Icon Theme]
Name=SnowLinux
Comment=SnowLinux icons (original artwork)
Inherits=Papirus-mxblue,Papirus,hicolor
Directories=scalable/places,scalable/devices,scalable/mimetypes,scalable/apps

[scalable/places]
Size=64
MinSize=16
MaxSize=512
Type=Scalable
Context=Places

[scalable/devices]
Size=64
MinSize=16
MaxSize=512
Type=Scalable
Context=Devices

[scalable/mimetypes]
Size=64
MinSize=16
MaxSize=512
Type=Scalable
Context=MimeTypes

[scalable/apps]
Size=64
MinSize=16
MaxSize=512
Type=Scalable
Context=Applications
""")
    return len(files)


def main():
    with open(out("logo", "snowlinux-logo.svg"), "w") as f:
        f.write(logo_mono())
    with open(out("logo", "snowlinux-logo-color.svg"), "w") as f:
        f.write(logo_color())
    wallpaper().save(out("wallpapers", "SnowLinux-Dusk.jpg"), quality=92, optimize=True)
    n = generate_icons(out("icons", "SnowLinux", "x")[:-1].rstrip("/"))
    print("ロゴ 2、壁紙 1、アイコン", n)


if __name__ == "__main__":
    main()
