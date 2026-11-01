# アプリの整理 (案)

MX Linux には、メニューに出るアプリが 159 個ある (2026-11-01 時点)。使う目的 (ネット、YouTube、写真、書類) に合わせて、4 つに分ける。

- **アプリケーション**: 普段使う。Dock・アプリケーションフォルダに出す
- **ユーティリティ**: アプリケーションフォルダの中の「ユーティリティ」フォルダに入れる (Mac の /Applications/Utilities)
- **システム環境設定**: 設定の画面に統合する。単独のアプリとしてはメニューに出さない
- **消す**: 使わない。メニューから外す (最終的にはパッケージごと削除)

## アプリケーション

| 分類 | アプリ | メモ |
|---|---|---|
| ファイル | Thunar | Finder の役。Dock の左端 |
| インターネット | Firefox、Thunderbird | |
| オフィス | LibreOffice Writer / Calc / Impress / Draw | Base・Math・起動センターは消す |
| 写真 | nomacs (閲覧)、**PhotoCraft / LightCraft (追加予定。整理と編集)**、ドキュメントスキャナー | digiKam は重いので外す (決定) |
| PDF | qpdfview (閲覧)、PDF Arranger (ページの並べ替え) | Preview の役 |
| メディア | VLC、Strawberry (音楽) | 音楽プレーヤーは 1 つ残す (決定) |
| テキスト | FeatherPad | TextEdit の役 |
| 計算・予定 | Galculator、Orage カレンダー | |
| 開発 | VS Code | 標準で入れる (ライセンス要確認) |

## ユーティリティ

| 分類 | アプリ |
|---|---|
| システム | 端末、Htop、タスクマネージャー、センサー、dconf エディター、設定エディター |
| ディスク | GParted、ディスクマネージャ、QDiskInfo、ディスク使用量アナライザー、USB フォーマット、UEFI Manager |
| 情報 | Hardinfo2、クイックシステム情報 |
| バックアップ | Timeshift (Time Machine の役)、luckyBackup、MX スナップショット |
| パッケージ | Synaptic、MX パッケージインストーラ、Deb インストーラ、MX リポジトリマネージャ、ユーザインストール済みパッケージ、MX GPG キー修復 |
| MX ツール | MX Tools、MX ブートリペア、MX 起動設定ツール、MX Live USB メーカ、ライブ USB カーネル更新、MX クリーンアップ、MX サービスマネージャ、MX リマスター CC、Chroot レスキュースキャン、ISO Signature Verifier、MX Samba 設定、ファイアウォール設定ツール |
| その他 | スクリーンショット、Catfish (検索)、パスワードと鍵、Engrampa (書庫)、Xfburn (CD 書き込み)、名前を一括変更、gMTP、GtkHash、guvcview、メニューエディター、Alsamixer、Midnight Commander、Jar-Loader、Py-Loader |

## システム環境設定に統合 (単独のアプリとしては出さない)

ディスプレイ、キーボード、マウスとタッチパッド、外観、ウィンドウマネージャー (2 種類)、ワークスペース、デスクトップ、パネル、通知、電源管理、スクリーンセーバー、アクセシビリティ、セッションと起動、デフォルトアプリケーション、カラープロファイル、
Fcitx 設定、入力メソッド、Mozc の設定、キーボードの設定 (Qt)、MX 日付と時刻、MX ロケール、MX サウンドカードの選択、MX システム音、MX テーマカラー、音量調節、Bluetooth アダプター / マネージャー、高度なネットワーク設定、MX ネットワーク・アシスタント、印刷設定、Thunar の設定、リムーバブルドライブとメディア、Orage の設定、LightDM の設定、Papirus フォルダ色、MX Tweak、MX アップデータ (と設定)、Redshift (夜間の色温度)、Xfce 端末の設定、クリップボードマネージャー設定、Rofi のテーマ選択、設定マネージャー

## 消す

| 分類 | アプリ | 理由 |
|---|---|---|
| ゲーム | GNOME 上海、Swell Foop、Peg-E | 目的外 |
| 音楽 | Asunder (CD リッピング) | 目的外 |
| 電子書籍・ダウンロード | Foliate、Transmission | 目的外 |
| 開発 | Geany | VS Code を標準にする |
| 写真 | digiKam | 重い。軽いもの (nomacs、PhotoCraft / LightCraft) で代用する (決定) |
| アクセシビリティ | Magnus、Onboard (と設定) | 自動で前に出てくる。必要な人は設定から |
| 起動 | Rofi、アプリケーションファインダー、プログラムの実行 | Spotlight 役のランチャーに置き換える |
| MX の案内 | MX ウェルカム、MX Tour、MX ユーザマニュアル、FAQ、Help、MX Linux について、Xfce について、TeXInfo、ヘルプ (yelp) | SnowLinux 用に作り直す |
| Conky | MX Conky、Conky トグル | Mac にない |
| 内部用 | YAD settings、Icon Browser、Fcitx、Gxkb、LibreOffice Base / Math / 起動センター、xfce4-* のラッパー (ウェブブラウザー・ファイルマネージャー・メーラー・ターミナルエミュレーター) | 重複・内部用 |

## 決定したこと (2026-11-01)

- digiKam は外す (「キビキビ」を優先)
- 音楽プレーヤー (Strawberry) は残す
- Thunderbird は標準で入れる

## 実装の方針

- 「消す」グループは、`config/hidden-apps.txt` に一覧を持ち、`scripts/gen-hidden-apps.sh` で `config/skel/.local/share/applications/` に `NoDisplay=true` のファイルを作ってメニューから隠す (戻せる)
- 「システム環境設定に統合」のグループは、システム環境設定アプリを作るまで隠さない (隠すと Xfce の設定マネージャーの一覧からも消える可能性がある)

- まずは、`~/.local/share/applications/` に同名の `NoDisplay=true` のファイルを置いて、メニューから隠す (戻せる。`config/skel/` に入れる)
- 最終的な ISO では、パッケージごと削除する
- ユーティリティフォルダは、アプリケーションフォルダの中の仮想のフォルダにする (Thunar で開ける。.desktop ファイルの集まり)
