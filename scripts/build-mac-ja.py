#!/usr/bin/env python3
"""Xfce のアプリの日本語の訳を、Mac 風の文言に差し替えた .mo を作る。

Xfce のデスクトップのメニューや Thunar の項目は、追加や並べ替えができないので、訳を差し替えて Mac に寄せる。
使い方: build-mac-ja.py ドメイン(xfdesktop / thunar / plank) 出力先.mo [--from 元の.mo]
        元は、初めはシステムの ja の .mo。"""
import gettext
import struct
import sys

SRC = "/usr/share/locale/ja/LC_MESSAGES/%s.mo"

XFDESKTOP = {
    "Create _Folder...": "新規フォルダ(_F)",
    "Create _Folder": "新規フォルダ(_F)",
    "Create _Document": "新規書類(_D)",
    "Create _Launcher...": "ランチャーを作成(_L)...",
    "Create _URL Link...": "Web リンクを作成(_U)...",
    "Arrange Desktop _Icons": "項目を整理(_I)",
    "_Next Background": "次の背景(_N)",
    "Desktop _Settings...": "デスクトップの背景を変更(_S)...",
    "_Paste": "ペースト(_P)",
    "_Properties...": "情報を見る(_I)",
    "_Properties": "情報を見る(_I)",
    "_Rename...": "名前を変更(_R)...",
    "_Rename": "名前を変更(_R)",
    "Mo_ve to Trash": "ゴミ箱に入れる(_T)",
    "_Empty Trash": "ゴミ箱を空にする(_E)",
    "_Empty File": "空のファイル(_E)",
    "New Folder": "名称未設定フォルダ",
}

THUNAR = {
    "Properties": "情報を見る",
    "_Properties...": "情報を見る(_I)",
    "%s - Properties": "%s の情報",
    "%s (%s) - Properties": "%s (%s) の情報",
    "Mo_ve to Trash": "ゴミ箱に入れる(_T)",
    "Move to Trash": "ゴミ箱に入れる",
    "_Paste": "ペースト(_P)",
    "_Paste Into Folder": "フォルダにペースト(_P)",
    "Create _Folder...": "新規フォルダ(_F)...",
    "Create Folder": "新規フォルダ",
    "New Folder": "名称未設定フォルダ",
    "_Open Location...": "フォルダへ移動(_G)...",
    "Open _Parent": "上のフォルダを開く(_P)",
    "_Icon View": "アイコンで表示(_I)",
    "_Compact View": "リストで表示(_L)",
    "Places": "よく使う項目",
    "Devices": "デバイス",
    "Network": "ネットワーク",
    "Computer": "コンピュータ",
    "_Computer": "コンピュータ(_C)",
    "Folder": "フォルダ",
}

# Dock (Plank) のゴミ箱。個数の言い方は単数・複数を持つ訳なので、「単数形\0複数形」の形も入れておく
PLANK = {
    "No items in Trash": "ゴミ箱は空です",
    "%u item in Trash": "ゴミ箱に %u 項目",
    "%u items in Trash": "ゴミ箱に %u 項目",
    "%u item in Trash\0%u items in Trash": "ゴミ箱に %u 項目",
    "Empty _Trash": "ゴミ箱を空にする(_E)",
    "_Open Trash": "ゴミ箱を開く(_O)",
    "Empty all items from Trash?": "ゴミ箱の中の項目を、すべて削除しますか?",
    "All items in the Trash will be permanently deleted.": "ゴミ箱の中の項目は、完全に削除されます。この操作は取り消せません。",
    "Drop to move to Trash": "ここに置くとゴミ箱に入れます",
}

TABLES = {"xfdesktop": XFDESKTOP, "thunar": THUNAR, "plank": PLANK}


def write_mo(catalog, path):
    keys = sorted(catalog)
    ids = b""
    strs = b""
    offsets = []
    for k in keys:
        kb, vb = k.encode(), catalog[k].encode()
        offsets.append((len(ids), len(kb), len(strs), len(vb)))
        ids += kb + b"\0"
        strs += vb + b"\0"
    n = len(keys)
    ktab = 7 * 4 + 16 * n
    vtab = ktab + len(ids)
    out = struct.pack("Iiiiiii", 0x950412DE, 0, n, 28, 28 + 8 * n, 0, 0)
    out += b"".join(struct.pack("ii", o[1], ktab + o[0]) for o in offsets)
    out += b"".join(struct.pack("ii", o[3], vtab + o[2]) for o in offsets)
    with open(path, "wb") as f:
        f.write(out + ids + strs)


def main():
    domain, out = sys.argv[1], sys.argv[2]
    src = sys.argv[sys.argv.index("--from") + 1] if "--from" in sys.argv else SRC % domain
    t = gettext.GNUTranslations(open(src, "rb"))
    cat = {k: v for k, v in t._catalog.items() if isinstance(k, str)}
    cat.update(TABLES[domain])
    if "Plural-Forms" not in cat.get("", ""):      # 日本語は単数・複数の区別がない (元の .mo に書かれていないことがある)
        cat[""] = cat.get("", "") + "Plural-Forms: nplurals=1; plural=0;\n"
    write_mo(cat, out)


main()
