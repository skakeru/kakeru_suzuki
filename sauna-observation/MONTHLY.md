# 毎月の実行手順（スケジュール実行のClaudeセッション用）

毎月1日 9:47 JST に新しいセッションが起動し、この手順に従う。

1. `git fetch origin claude/adoring-hamilton-b4ihku && git checkout claude/adoring-hamilton-b4ihku && git pull`
2. `cd sauna-observation && python3 collect.py`（約60分。バックグラウンドで実行して完了を待つ）
   - 失敗した県があればログを確認し、そのまま再実行してよい（同日のファイルは上書き）。
   - 47都道府県合計が前回より大きく減っている（-3%超）場合は、サイト構造の変更を疑い、Slackに投稿せず原因を報告する。
3. 考察段落を `notes/YYYY-MM-DD.txt` に2〜4文で書く（任意）。`report.py` の出力を見て、数字だけでは伝わらない動き（順位の入れ替わりの理由、人口が小さい県は1件のサ活で数値が動く、など）を説明する。数字は data/ と reports/ の値だけを使い、推測で数字を作らない。
4. `python3 report.py --notes notes/YYYY-MM-DD.txt`
5. `index.html` を Artifact URL（下記）に再公開する。
6. Slack #全社-情報共有（C0BS756Q1DJ）に `reports/YYYY-MM-DD.txt` の本文を投稿する。先頭に1行「サウナイキタイ定点観測（YYYY年M月）」、末尾にベースページのURLを付ける。
7. `data/`, `reports/`, `notes/`, `index.html` をコミットして `claude/adoring-hamilton-b4ihku` にpushする。

Artifact URL: （初回公開後に記入）
