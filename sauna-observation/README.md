# サウナイキタイ定点観測

サウナイキタイ（sauna-ikitai.com）の公開検索結果を毎月1回集計し、シェア文とベースページを作る仕組み。

## 毎月の手順

```bash
cd sauna-observation
python3 collect.py                 # 約20〜30分。data/YYYY-MM-DD.json を保存
python3 report.py                  # reports/YYYY-MM-DD.txt と index.html を生成
# 考察段落（例：岐阜が神奈川を抜いた理由）を足す場合
python3 report.py --notes notes/YYYY-MM-DD.txt
```

その後、`index.html` を同じArtifact URLに再公開し、`reports/YYYY-MM-DD.txt` の本文を配信先に送る。

## 観測項目

| 項目 | 定義 |
|---|---|
| 登録施設数 | 都道府県で絞った検索結果の件数。全国は47都道府県の合計 |
| 前回比・1日あたり | 前回スナップショットとの差、差 ÷ 観測間隔日数 |
| 人口あたり活発度 | 県内の登録施設のサ活数合計 ÷ 人口 × 10万（人口は令和2年国勢調査で固定） |
| 条件別施設数 | 水着着用 / プライベートサウナ（施設タイプ） / アウフグース（ロウリュサービス） / タトゥーOK |
| 条件別構成比 | 条件該当件数 ÷ その県の登録施設数。全国平均は全国合計どうしの比 |

## ファイル

- `collect.py` 取得（標準ライブラリのみ、1秒間隔）
- `prefs.py` 都道府県slugと人口
- `report.py` 比較・文章化・ページ生成
- `template.html` ベースページのテンプレート
- `data/` 毎回のスナップショット（比較の元データなので消さない）
- `reports/` 毎回のシェア文
