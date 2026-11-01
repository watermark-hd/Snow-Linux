#!/usr/bin/env python3
"""SnowLinux の xfwm4 テーマ (信号機ボタン・タイトルバー・枠) の画像を生成する。

使い方: python3 -I themes/tools/gen_xfwm4.py
出力:   themes/SnowLinux/xfwm4/ (themerc と PNG)
"""
import io
import math
import os

import cairo
from PIL import Image

SS = 8                      # スーパーサンプリング倍率 (縁をなめらかにする)
TITLE_H = 22                # タイトルバーの高さ
BTN_W, BTN_H, BTN_D = 20, TITLE_H, 13   # ボタン画像の大きさと丸の直径
RADIUS = 6                  # ウィンドウ上部の角の丸み
OUT = os.path.join(os.path.dirname(__file__), "..", "SnowLinux", "xfwm4")


def hexc(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(c, t, k):
    """c を t に k の割合で近づける。"""
    return tuple(a + (b - a) * k for a, b in zip(c, t))


def lighten(c, k):
    return mix(c, (1, 1, 1), k)


def darken(c, k):
    return mix(c, (0, 0, 0), k)


def to_image(surface, w, h):
    buf = io.BytesIO()
    surface.write_to_png(buf)
    buf.seek(0)
    im = Image.open(buf).convert("RGBa")        # 透明部分に色がにじまないように
    return im.resize((w, h), Image.LANCZOS).convert("RGBA")


def new_canvas(w, h):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w * SS, h * SS)
    ctx = cairo.Context(surf)
    ctx.scale(SS, SS)
    return surf, ctx


# ---------- 信号機ボタン ----------

GEL = {
    "close": hexc("#f0473c"),
    "hide": hexc("#fbb91c"),
    "maximize": hexc("#27c53c"),
    "other": hexc("#6f9bd8"),
}
GRAY = hexc("#cdcdcd")


def draw_button(base, state, symbol):
    """state: active / inactive / prelight / pressed"""
    surf, ctx = new_canvas(BTN_W, BTN_H)
    cx, cy, r = BTN_W / 2, BTN_H / 2, BTN_D / 2
    inactive = state == "inactive"
    body = GRAY if inactive else base
    if state == "pressed":
        body = darken(body, 0.18)

    # 丸の本体: 上が明るく、下に反射光
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.save()
    ctx.clip_preserve()
    g = cairo.LinearGradient(0, cy - r, 0, cy + r)
    g.add_color_stop_rgb(0.0, *lighten(body, 0.30))
    g.add_color_stop_rgb(0.5, *body)
    g.add_color_stop_rgb(1.0, *lighten(body, 0.12))
    ctx.set_source(g)
    ctx.fill()
    # 下側の反射光
    glow = cairo.RadialGradient(cx, cy + r * 0.85, 0, cx, cy + r * 0.85, r * 1.05)
    glow.add_color_stop_rgba(0.0, *lighten(body, 0.65), 0.75 if not inactive else 0.35)
    glow.add_color_stop_rgba(1.0, *lighten(body, 0.65), 0.0)
    ctx.set_source(glow)
    ctx.paint()
    ctx.restore()

    # 上側のつや
    ctx.save()
    ctx.translate(cx, cy - r * 0.46)
    ctx.scale(r * 0.74, r * 0.46)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    gloss = cairo.LinearGradient(0, cy - r * 0.92, 0, cy - r * 0.02)
    gloss.add_color_stop_rgba(0.0, 1, 1, 1, 0.92 if not inactive else 0.55)
    gloss.add_color_stop_rgba(1.0, 1, 1, 1, 0.12)
    ctx.set_source(gloss)
    ctx.fill()

    # 縁
    ctx.arc(cx, cy, r - 0.35, 0, 2 * math.pi)
    ctx.set_line_width(0.8)
    ctx.set_source_rgba(*darken(body, 0.45), 0.95)
    ctx.stroke()

    # 記号 (ポインターを乗せたとき・押したとき)
    if symbol and state in ("prelight", "pressed"):
        ctx.set_source_rgba(*darken(body, 0.72), 0.95)
        ctx.set_line_width(1.5)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        k = 2.3
        if symbol == "x":
            ctx.move_to(cx - k, cy - k); ctx.line_to(cx + k, cy + k)
            ctx.move_to(cx + k, cy - k); ctx.line_to(cx - k, cy + k)
        elif symbol == "-":
            ctx.move_to(cx - k - 0.4, cy); ctx.line_to(cx + k + 0.4, cy)
        elif symbol == "+":
            ctx.move_to(cx - k - 0.2, cy); ctx.line_to(cx + k + 0.2, cy)
            ctx.move_to(cx, cy - k - 0.2); ctx.line_to(cx, cy + k + 0.2)
        ctx.stroke()
    return to_image(surf, BTN_W, BTN_H)


# ---------- タイトルバー・枠 ----------

def title_rows(active):
    """タイトルバーの各行 (上から) の色。"""
    rows = []
    if active:
        top, edge, hi, c0, c1, bottom = "#6a6a6a", "#6a6a6a", "#f8f8f8", "#e3e3e3", "#b6b6b6", "#686868"
    else:
        top, edge, hi, c0, c1, bottom = "#9c9c9c", "#9c9c9c", "#fcfcfc", "#eeeeee", "#d4d4d4", "#9d9d9d"
    rows.append(hexc(top))
    rows.append(hexc(hi))
    n = TITLE_H - 3
    for i in range(n):
        rows.append(mix(hexc(c0), hexc(c1), i / (n - 1)))
    rows.append(hexc(bottom))
    return rows


def side_color(active):
    return hexc("#6a6a6a" if active else "#9c9c9c")


def title_piece(active, w):
    """タイトルバーの横に並べる部品 (幅 w、高さ TITLE_H)。"""
    im = Image.new("RGBA", (w, TITLE_H))
    for y, c in enumerate(title_rows(active)):
        for x in range(w):
            im.putpixel((x, y), tuple(int(round(v * 255)) for v in c) + (255,))
    return im


def corner(active, right):
    """上の角 (幅 8)。外側を丸く切り抜く。"""
    w = 8
    surf, ctx = new_canvas(w, TITLE_H)
    ctx.save()
    if not right:
        ctx.move_to(0, TITLE_H)
        ctx.line_to(0, RADIUS)
        ctx.arc(RADIUS, RADIUS, RADIUS, math.pi, 1.5 * math.pi)
        ctx.line_to(w, 0)
        ctx.line_to(w, TITLE_H)
    else:
        ctx.move_to(w, TITLE_H)
        ctx.line_to(w, RADIUS)
        ctx.arc_negative(w - RADIUS, RADIUS, RADIUS, 0, -0.5 * math.pi)
        ctx.line_to(0, 0)
        ctx.line_to(0, TITLE_H)
    ctx.close_path()
    ctx.clip()
    for y, c in enumerate(title_rows(active)):
        ctx.rectangle(0, y, w, 1)
        ctx.set_source_rgb(*c)
        ctx.fill()
    ctx.restore()
    # 縁取り
    e = side_color(active)
    ctx.set_source_rgb(*e)
    ctx.set_line_width(1)
    h = 0.5
    if not right:
        ctx.move_to(h, TITLE_H)
        ctx.line_to(h, RADIUS)
        ctx.arc(RADIUS, RADIUS, RADIUS - h, math.pi, 1.5 * math.pi)
        ctx.line_to(w, h)
    else:
        ctx.move_to(w - h, TITLE_H)
        ctx.line_to(w - h, RADIUS)
        ctx.arc_negative(w - RADIUS, RADIUS, RADIUS - h, 0, -0.5 * math.pi)
        ctx.line_to(0, h)
    ctx.stroke()
    return to_image(surf, w, TITLE_H)


def solid(w, h, color):
    return Image.new("RGBA", (w, h), tuple(int(round(v * 255)) for v in color) + (255,))


THEMERC = """# SnowLinux xfwm4 テーマ (themes/tools/gen_xfwm4.py で画像を生成)
active_text_color=#3a3a3a
active_text_shadow_color=#f4f4f4
inactive_text_color=#999999
inactive_text_shadow_color=#f4f4f4
title_shadow_active=true
title_shadow_inactive=true
full_width_title=true
title_vertical_offset_active=0
title_vertical_offset_inactive=0
button_offset=5
button_spacing=0
shadow_delta_height=2
shadow_delta_width=0
shadow_delta_x=0
shadow_delta_y=-10
shadow_opacity=55
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    out = lambda name, im: im.save(os.path.join(OUT, name))

    buttons = {
        "close": ("close", "x"),
        "hide": ("hide", "-"),
        "maximize": ("maximize", "+"),
        "maximize-toggled": ("maximize", "+"),
        "menu": ("other", None),
        "shade": ("other", None),
        "shade-toggled": ("other", None),
        "stick": ("other", None),
        "stick-toggled": ("other", None),
    }
    for name, (kind, sym) in buttons.items():
        for state in ("active", "inactive", "prelight", "pressed"):
            out(f"{name}-{state}.png", draw_button(GEL[kind], state, sym))

    for act in (True, False):
        s = "active" if act else "inactive"
        for i in range(1, 6):
            out(f"title-{i}-{s}.png", title_piece(act, 2))
        out(f"top-left-{s}.png", corner(act, False))
        out(f"top-right-{s}.png", corner(act, True))
        c = side_color(act)
        out(f"left-{s}.png", solid(1, 1, c))
        out(f"right-{s}.png", solid(1, 1, c))
        out(f"bottom-{s}.png", solid(1, 1, c))
        out(f"bottom-left-{s}.png", solid(1, 1, c))
        out(f"bottom-right-{s}.png", solid(1, 1, c))

    with open(os.path.join(OUT, "themerc"), "w") as f:
        f.write(THEMERC)
    print("生成しました:", os.path.abspath(OUT), len(os.listdir(OUT)), "ファイル")


if __name__ == "__main__":
    main()
