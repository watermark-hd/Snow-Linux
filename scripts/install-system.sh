#!/bin/bash
# この機械全体 (システム領域) に SnowLinux の見た目を入れる。ログイン画面や起動画面も変わる。
# 使い方:
#   sudo scripts/install-system.sh            テーマ・アイコン・壁紙・ログイン画面を入れる
#   sudo scripts/install-system.sh --plymouth 起動画面も入れる (initramfs の更新があり、少し時間がかかる)
#   sudo scripts/install-system.sh --restore  ログイン画面と起動画面を、入れる前の状態に戻す
# 元の設定は *.snowlinux-backup として残す。
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
greeter=/etc/lightdm/lightdm-gtk-greeter.conf
plyconf=/etc/plymouth/plymouthd.conf

if [ "$(id -u)" -ne 0 ]; then
    echo "sudo で実行してください: sudo $0 [--plymouth|--restore]" >&2
    exit 1
fi

if [ "${1:-}" = "--restore" ]; then
    [ -f "$greeter.snowlinux-backup" ] && cp -a "$greeter.snowlinux-backup" "$greeter" && echo "ログイン画面を元に戻しました。"
    if [ -f "$plyconf.snowlinux-backup" ]; then
        cp -a "$plyconf.snowlinux-backup" "$plyconf"
        update-initramfs -u && echo "起動画面を元に戻しました。"
    fi
    exit 0
fi

# テーマ・アイコン・ロゴ・壁紙
mkdir -p /usr/share/themes /usr/share/icons /usr/share/backgrounds/SnowLinux /usr/share/icons/hicolor/scalable/apps
rm -rf /usr/share/themes/SnowLinux /usr/share/icons/SnowLinux
cp -a "$root/themes/SnowLinux" /usr/share/themes/
cp -a "$root/assets/icons/SnowLinux" /usr/share/icons/
cp "$root"/assets/logo/*.svg /usr/share/icons/hicolor/scalable/apps/
cp "$root"/assets/wallpapers/*.jpg /usr/share/backgrounds/SnowLinux/
gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor 2>/dev/null || true
gtk-update-icon-cache -q -t -f /usr/share/icons/SnowLinux 2>/dev/null || true

# ログイン画面
[ -f "$greeter.snowlinux-backup" ] || cp -a "$greeter" "$greeter.snowlinux-backup"
cp "$root/config/system/lightdm/lightdm-gtk-greeter.conf" "$greeter"
echo "ログイン画面を SnowLinux にしました (元の設定: $greeter.snowlinux-backup)。"

# 起動画面
if [ "${1:-}" = "--plymouth" ]; then
    [ -f "$plyconf.snowlinux-backup" ] || cp -a "$plyconf" "$plyconf.snowlinux-backup"
    rm -rf /usr/share/plymouth/themes/SnowLinux
    cp -a "$root/assets/plymouth/SnowLinux" /usr/share/plymouth/themes/
    plymouth-set-default-theme -R SnowLinux
    echo "起動画面を SnowLinux にしました (元の設定: $plyconf.snowlinux-backup)。"
fi
