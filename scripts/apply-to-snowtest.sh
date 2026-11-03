#!/bin/bash
# config/skel/ の内容をテスト用ユーザー snowtest のホームに反映する。
# 使い方: sudo scripts/apply-to-snowtest.sh [--reset]
#   --reset  先に snowtest の ~/.config と ~/.cache を消し、/etc/skel を入れ直して初回ログインの状態に戻す
# snowtest がログイン中だと、ログアウト時に設定が上書きされるので実行しない。
set -eu

user=snowtest
root="$(cd "$(dirname "$0")/.." && pwd)"
skel="$root/config/skel"
themes="$root/themes"

if [ "$(id -u)" -ne 0 ]; then
    echo "sudo で実行してください: sudo $0 [--reset]" >&2
    exit 1
fi
# デスクトップが動いている間は、ログアウト時に設定が上書きされるので実行しない
if pgrep -u "$user" -x 'xfce4-session|xfwm4|xfce4-panel' >/dev/null; then
    echo "$user がログイン中です。ログアウトしてから実行してください。" >&2
    exit 1
fi
# ログアウト後に dbus や gvfs などが残ることがあるので、片付ける
loginctl terminate-user "$user" 2>/dev/null || true

# 実際のインストールと同じく、MX Linux の初期設定 (/etc/skel) に SnowLinux の設定を重ねる
if [ "${1:-}" = "--reset" ]; then
    rm -rf "/home/$user/.config" "/home/$user/.cache"
    cp -a --no-preserve=ownership /etc/skel/. "/home/$user/"
fi

cp -a --no-preserve=ownership "$skel"/. "/home/$user/"

# テーマ: 実際のインストールでは /usr/share/themes に入れる。テストでは ~/.themes に置く
mkdir -p "/home/$user/.themes"
for t in "$themes"/*/; do
    [ -d "$t" ] && cp -a --no-preserve=ownership "$t" "/home/$user/.themes/"
done
# 通知デーモンは ~/.themes を見ないことがあるので、XDG の場所にも置く
mkdir -p "/home/$user/.local/share/themes"
cp -a --no-preserve=ownership "$themes/SnowLinux" "/home/$user/.local/share/themes/"

# アイコンテーマとロゴ (実際のインストールでは /usr/share/icons に入れる)
mkdir -p "/home/$user/.local/share/icons/hicolor/scalable/apps"
cp -a --no-preserve=ownership "$root/assets/icons/SnowLinux" "/home/$user/.local/share/icons/"
cp --no-preserve=ownership "$root/assets/logo/snowlinux-logo.svg" "/home/$user/.local/share/icons/hicolor/scalable/apps/"
cp --no-preserve=ownership "$root/assets/logo/snowlinux-logo-color.svg" "/home/$user/.local/share/icons/hicolor/scalable/apps/"

# 壁紙 (システム全体で共通。ユーザーごとの設定から /usr/share/backgrounds/SnowLinux/ を参照する)
mkdir -p /usr/share/backgrounds/SnowLinux
cp "$root"/assets/wallpapers/*.jpg /usr/share/backgrounds/SnowLinux/

chown -R "$user:$user" "/home/$user"
# skel をコピーすると、ホームフォルダ自体の権限も skel のものになってしまうので、元の (他人に読めない) 権限に戻す
chmod 700 "/home/$user"

# dconf の設定 (Plank など)。snowtest として、一時的な D-Bus セッションで書き込む
for f in "$root"/config/dconf/*.dconf; do
    [ -f "$f" ] && sudo -u "$user" -H dbus-run-session -- dconf load / < "$f"
done

# 起動ファイルを Thunar に信頼させる小さなスクリプト (ログインのたびに、自動起動から呼ばれる)
install -m 755 "$root/scripts/snowlinux-trust-applications" /usr/local/bin/snowlinux-trust-applications

# システム環境設定
install -m 755 "$root/scripts/snowlinux-system-preferences" /usr/local/bin/snowlinux-system-preferences
install -D -m 644 "$root/config/system/applications/snowlinux-system-preferences.desktop" /usr/local/share/applications/snowlinux-system-preferences.desktop

# ランチャー (Spotlight 風)。本体 (spotlightd) はログイン時に待機させる。GTK なので日本語入力が使える
install -m 755 "$root/scripts/snowlinux-spotlight" /usr/local/bin/snowlinux-spotlight
install -m 755 "$root/scripts/snowlinux-spotlightd" /usr/local/bin/snowlinux-spotlightd
rm -f /usr/local/bin/snowlinux-file-search          # rofi 版の残り (廃止)
install -m 755 "$root/scripts/snowlinux-screenshot" /usr/local/bin/snowlinux-screenshot
install -m 755 "$root/scripts/snowlinux-appmenu" /usr/local/bin/snowlinux-appmenu
install -m 755 "$root/scripts/snowlinux-switcher" /usr/local/bin/snowlinux-switcher
install -m 755 "$root/scripts/snowlinux-about" /usr/local/bin/snowlinux-about
install -m 755 "$root/scripts/snowlinux-software-update" /usr/local/bin/snowlinux-software-update
install -m 755 "$root/scripts/snowlinux-quicklook" /usr/local/bin/snowlinux-quicklook
install -m 755 "$root/scripts/snowlinux-display-calibrator" /usr/local/bin/snowlinux-display-calibrator
install -D -m 644 "$root/config/system/applications/snowlinux-display-calibrator.desktop" /usr/local/share/applications/snowlinux-display-calibrator.desktop
install -D -m 644 "$root/config/system/applications/snowlinux-software-update.desktop" /usr/local/share/applications/snowlinux-software-update.desktop

# デスクトップの右クリックメニューと Thunar を Mac 風の文言にする (日本語の訳を差し替える)。
# パッケージの更新で元に戻らないように、元のファイルを dpkg-divert で脇へ退けてから置く
for domain in xfdesktop thunar; do
    mo=/usr/share/locale/ja/LC_MESSAGES/$domain.mo
    if ! dpkg-divert --list "$mo" | grep -q .; then
        dpkg-divert --local --rename --divert "$mo.orig" --add "$mo" >/dev/null
    fi
    python3 "$root/scripts/build-mac-ja.py" "$domain" "$mo" --from "$mo.orig"
done

# 「アプリケーション」フォルダ (システム全体で共通。実際のインストールでは、パッケージの更新のたびに作り直す)
python3 "$root/scripts/gen-applications-folder.py" /Applications

echo "$skel、$themes、dconf の設定を /home/$user に反映しました。"
