#!/usr/bin/env python3
"""サウナイキタイ 定点観測: 都道府県別の登録施設数・条件別施設数・サ活数を集計して data/YYYY-MM-DD.json に保存する。

使い方: python3 collect.py            # 今日の日付で保存
        python3 collect.py --date 2026-11-16
標準ライブラリのみ。1リクエストごとに待機を入れ、サイトに負荷をかけない（全体で約20分）。
"""
import argparse, datetime, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

from prefs import PREFS  # (slug, 名前, 人口)

BASE = "https://sauna-ikitai.com/search"
CONDITIONS = {
    "swimwear": ("mixed_type#swimwear", "水着着用"),
    "private": ("facility_type#privatesauna", "プライベートサウナ"),
    "aufguss": ("loyly_service#has_loyly", "アウフグース"),
    "tattoo": ("rule#allow_tattoo", "タトゥーOK"),
}
WAIT = 1.0
UA = "Mozilla/5.0 (compatible; sauna-observation/1.0)"

COUNT_RE = re.compile(r"([0-9,]+)件")
NUM_RE = re.compile(r'class="p-saunaItem_action">\s*(イキタイ|サ活)\s*<span class="p-saunaItem_number">\s*([0-9,]+)', re.S)
ITEM_RE = re.compile(r'class="p-saunaItem p-saunaItem--list')


def fetch(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                html = r.read().decode("utf-8")
            time.sleep(WAIT)
            return html
        except Exception as e:  # noqa: BLE001
            print(f"  retry {attempt+1}: {e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"failed: {url}")


def count(params):
    m = COUNT_RE.search(fetch(params))
    return int(m.group(1).replace(",", "")) if m else 0


def sakatsu_sum(slug, total):
    """一覧を全ページ巡回して、サ活数・イキタイ数を合計する。"""
    sakatsu = ikitai = items = 0
    page = 1
    while True:
        html = fetch([("prefecture[]", slug), ("page", page)])
        n = len(ITEM_RE.findall(html))
        if n == 0:
            break
        items += n
        for kind, val in NUM_RE.findall(html):
            v = int(val.replace(",", ""))
            if kind == "サ活":
                sakatsu += v
            else:
                ikitai += v
        if items >= total:
            break
        page += 1
    return sakatsu, ikitai, items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--out", default=str(Path(__file__).parent / "data"))
    a = ap.parse_args()

    snap = {"date": a.date, "source": BASE, "conditions": {k: v[1] for k, v in CONDITIONS.items()},
            "national_total": count([]), "prefectures": {}}
    for slug, name, pop in PREFS:
        p = [("prefecture[]", slug)]
        total = count(p)
        cond = {k: count(p + [("conditions[]", c)]) for k, (c, _) in CONDITIONS.items()}
        sak, iki, items = sakatsu_sum(slug, total)
        snap["prefectures"][slug] = {"name": name, "population": pop, "facilities": total,
                                     "conditions": cond, "sakatsu": sak, "ikitai": iki, "listed": items}
        print(f"{name}: 施設{total} サ活{sak} {cond}", file=sys.stderr)

    out = Path(a.out) / f"{a.date}.json"
    out.write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
