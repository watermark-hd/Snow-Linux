#!/usr/bin/env python3
"""デスクトップの右クリックメニューの文言を Mac 風にした xfdesktop.mo を作る。

Xfce のデスクトップのメニューは、項目の追加や並べ替えができないので、日本語の訳を差し替えて Mac に寄せる。
使い方: build-xfdesktop-ja.py 出力先.mo [--from 元の.mo]   (元は、初めはシステムの ja の xfdesktop.mo)"""
import gettext
import struct
import sys

SRC = "/usr/share/locale/ja/LC_MESSAGES/xfdesktop.mo"

MAC = {
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
    src = sys.argv[sys.argv.index("--from") + 1] if "--from" in sys.argv else SRC
    t = gettext.GNUTranslations(open(src, "rb"))
    cat = {k: v for k, v in t._catalog.items() if isinstance(k, str)}
    cat.update(MAC)
    write_mo(cat, sys.argv[1])


main()
