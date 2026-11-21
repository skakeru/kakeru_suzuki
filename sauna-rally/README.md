# サウナスタンプラリー（プロトタイプ）

JR東日本「エキタグ」を参考に、サウナ施設を巡ってデジタルスタンプを集めるWebアプリ。
デザインはサウコレ！（sauna-collection.vercel.app）の紺×水色・Noto Sans JPに合わせている。

- 公開URL（GitHub Pages）：https://skakeru.github.io/kakeru_suzuki/sauna-rally/
- デモで試す：https://skakeru.github.io/kakeru_suzuki/sauna-rally/?demo=1 （施設を選ぶとその場所にいることにできる）

## エキタグとの違い

| | エキタグ | このアプリ |
|---|---|---|
| 押し方 | 駅のNFCタグにスマホをタッチ | 施設の半径150m以内で現在地を取得して押す（タグ設置なし） |
| スタンプ | 駅ごとのデザイン | 施設ごとに自動生成（地方ごとにインク色が違う） |
| 集め方 | 路線・エリアごとのスタンプ帳 | 地方ごとのスタンプ帳、施設数で特典の段階 |

## 押せる条件（不正対策）

`index.html` の `RULES` と `supabase/schema.sql` の `stamp_checkin()` で同じルールを持つ。

- 施設から半径150m以内（位置の誤差は最大50mまで考慮）
- 位置の精度が±150m以内、取得から2分以内
- 同じ施設は1日1回（別の日なら再訪スタンプ）
- 1日10個まで
- 前回の押印地点から時速250kmを超える移動は無効

## ファイル

- `index.html` … アプリ本体（ビルド不要の1ファイル）
- `facilities.json` … 参加施設99件。ブレインスリープサウナMAP（Googleマイマップ）の座標を2026-11-21に取得
- `supabase/schema.sql` … サーバー側の押印判定（テーブル・RLS・`stamp_checkin` 関数）
- `supabase/seed.sql` … 施設データの投入
- `config.example.js` … Supabaseを使うときの設定例

## 2つの動き方

1. **config.js なし（いまの状態）**：判定も記録もブラウザ内。動きとデザインを確かめるためのモード。
2. **config.js あり**：Supabaseの匿名ログインでユーザーを作り、押印の判定と記録をサーバー（`stamp_checkin`）で行う。
   Supabaseで `schema.sql` → `seed.sql` を実行し、Authentication で Anonymous sign-ins を有効にしてから、
   `config.example.js` を `config.js` にコピーしてURLとanon keyを入れる。

## 次の候補

- 日替わりQR（受付のQR POP）との併用で、位置偽装への耐性を上げる
- 施設ごとのスタンプデザイン差し替え（画像を指定できるようにする）
- 地図表示、特典の応募フォーム、管理画面（施設追加・半径調整・試行ログの確認）
