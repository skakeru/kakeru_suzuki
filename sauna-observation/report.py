#!/usr/bin/env python3
"""data/*.json のスナップショットから、毎月のシェア文（reports/YYYY-MM-DD.txt）と
ベースページ（index.html）を生成する。

使い方: python3 report.py               # 最新と前回を比較
        python3 report.py --notes notes/2026-12-15.txt   # 手書きの考察段落を差し込む
"""
import argparse, datetime, html, json
from pathlib import Path

ROOT = Path(__file__).parent
COND_ORDER = ["swimwear", "private", "aufguss", "tattoo"]


def load_snapshots():
    snaps = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "data").glob("*.json"))]
    return sorted(snaps, key=lambda s: s["date"])


def days_between(a, b):
    return (datetime.date.fromisoformat(b["date"]) - datetime.date.fromisoformat(a["date"])).days


def total(s):
    return sum(p["facilities"] for p in s["prefectures"].values())


def activity(p):
    return p["sakatsu"] / p["population"] * 100000


def analyze(snaps):
    cur = snaps[-1]
    prev = snaps[-2] if len(snaps) >= 2 else None
    prev2 = snaps[-3] if len(snaps) >= 3 else None
    P = cur["prefectures"]
    a = {"date": cur["date"], "total": total(cur), "site_total": cur.get("national_total"),
         "cond_names": cur["conditions"], "prev_date": prev and prev["date"]}

    # 人口あたり活発度
    act = sorted(((s, activity(p)) for s, p in P.items()), key=lambda x: -x[1])
    a["activity"] = [{"slug": s, "name": P[s]["name"], "value": round(v)} for s, v in act]
    rank = {s: i + 1 for i, (s, _) in enumerate(act)}

    # 条件別
    nat = {k: sum(p["conditions"][k] for p in P.values()) for k in COND_ORDER}
    a["cond"] = {}
    for k in COND_ORDER:
        top_n = max(P, key=lambda s: P[s]["conditions"][k])
        top_r = max(P, key=lambda s: P[s]["conditions"][k] / P[s]["facilities"] if P[s]["facilities"] else 0)
        a["cond"][k] = {"name": cur["conditions"][k], "national": nat[k],
                        "national_share": nat[k] / a["total"] * 100,
                        "top_count": (P[top_n]["name"], P[top_n]["conditions"][k]),
                        "top_share": (P[top_r]["name"], P[top_r]["conditions"][k] / P[top_r]["facilities"] * 100)}

    rows = []
    for s, p in P.items():
        r = {"slug": s, "name": p["name"], "facilities": p["facilities"], "sakatsu": p["sakatsu"],
             "activity": round(activity(p)), "rank": rank[s], "cond": p["conditions"]}
        if prev and s in prev["prefectures"]:
            q = prev["prefectures"][s]
            r["d_fac"] = p["facilities"] - q["facilities"]
            r["d_sak"] = p["sakatsu"] - q["sakatsu"]
            r["d_cond"] = {k: p["conditions"][k] - q["conditions"][k] for k in COND_ORDER}
            r["prev_rank"] = sorted(prev["prefectures"], key=lambda x: -activity(prev["prefectures"][x])).index(s) + 1
        rows.append(r)
    a["rows"] = sorted(rows, key=lambda r: list(P).index(r["slug"]))

    if prev:
        d = days_between(prev, cur)
        a["diff"] = a["total"] - total(prev)
        a["days"] = d
        a["per_day"] = a["diff"] / d if d else 0
        if prev2:
            d2 = days_between(prev2, prev)
            a["prev_per_day"] = (total(prev) - total(prev2)) / d2 if d2 else 0
        a["risers"] = sorted(rows, key=lambda r: -r["d_fac"])[:4]
        a["decreased"] = [r for r in rows if r["d_fac"] < 0]
        a["cond_diff"] = {k: sum(r["d_cond"][k] for r in rows) for k in COND_ORDER}
        a["cond_sum_risers"] = sorted(rows, key=lambda r: -sum(r["d_cond"].values()))[:3]
        a["rank_moves"] = [r for r in rows if r["rank"] <= 10 and r["prev_rank"] != r["rank"]]
    a["history"] = [{"date": s["date"], "total": total(s),
                     "sakatsu": sum(p["sakatsu"] for p in s["prefectures"].values())} for s in snaps]
    return a


def fmt(n):
    return f"{n:,}"


def signed(n):
    return f"+{n:,}" if n >= 0 else f"{n:,}"


def short(name):
    return name if name == "北海道" else name[:-1]


def share_text(a, notes=""):
    L = [f"サウナイキタイの全国登録施設数は、{fmt(a['total'])}件となりました。", ""]
    if "diff" in a:
        s = f"施設数は前回（{a['prev_date']}）から{signed(a['diff'])}件。1日あたり{a['per_day']:.1f}件"
        if "prev_per_day" in a:
            s += f"と、前回（{a['prev_per_day']:.1f}件）を{'上回る' if a['per_day'] > a['prev_per_day'] else '下回る'}ペースです。"
        else:
            s += "のペースです。"
        L += [s, ""]
        ri = "、".join(f"{short(r['name'])}（{signed(r['d_fac'])}）" for r in a["risers"])
        decs = a["decreased"]
        if not decs:
            dec = "施設数が減った県はひとつもありませんでした。"
        elif len(decs) <= 3:
            dec = "施設数が減ったのは" + "、".join(f"{r['name']}（{signed(r['d_fac'])}）" for r in decs) + "でした。"
        else:
            dec = f"施設数が減ったのは{len(decs)}県でした。"
        L += [f"伸びが目立ったのは{ri}で、{dec}", ""]
    else:
        L += ["今回が観測開始です。次回から前回比・1日あたりの増加ペースを掲載します。", ""]
    ups = sorted((r for r in a.get("rank_moves", []) if r["rank"] < r["prev_rank"]), key=lambda r: r["rank"])
    if ups:
        L += ["人口あたり活発度では、" + "、".join(
            f"{r['name']}が{r['prev_rank']}位から{r['rank']}位に浮上（{fmt(r['activity'])}）" for r in ups[:3]) + "しました。", ""]
    if notes.strip():
        L += [notes.strip(), ""]
    if "cond_diff" in a:
        cd = a["cond_diff"]
        parts = "、".join(f"{a['cond_names'][k]}（{signed(cd[k])}件）" for k in sorted(COND_ORDER, key=lambda k: -cd[k]))
        top = "、".join(f"{r['name']}（{signed(sum(r['d_cond'].values()))}）" for r in a["cond_sum_risers"])
        L += [f"条件別の増加は{parts}。条件別合計の増加は{top}が上位でした。", ""]
    L += ["【人口あたり活発度 全国TOP5】", "※人口10万人あたりのサ活数。「サウナ熱の濃さ」を見るための指標です。", ""]
    L += [f"{r['name']}　{fmt(r['value'])}" for r in a["activity"][:5]]
    L += ["", "【条件別登録施設数 都道府県1位】", ""]
    L += [f"・{c['name']}：{c['top_count'][0]}（{fmt(c['top_count'][1])}件）" for c in a["cond"].values()]
    L += ["", "【条件別 構成比 都道府県1位】", "※その県の登録施設のうち何％がその条件か。括弧内は全国平均です。", ""]
    for i, c in enumerate(a["cond"].values()):
        avg = f"全国平均 {c['national_share']:.1f}％" if i == 0 else f"同 {c['national_share']:.1f}％"
        L.append(f"・{c['name']}：{c['top_share'][0]} {c['top_share'][1]:.1f}％（{avg}）")
    return "\n".join(L).rstrip() + "\n"


def render_html(a, text):
    e = html.escape
    has_prev = "diff" in a
    kpi_diff = f"{signed(a['diff'])}" if has_prev else "—"
    kpi_pd = f"{a['per_day']:.1f}" if has_prev else "—"
    kpi_sub = f"前回 {a['prev_date']} から {a['days']}日" if has_prev else "初回観測。次回から比較"
    maxact = a["activity"][0]["value"]
    bars = "".join(
        f'<li><span class="rk">{i+1}</span><span class="nm">{e(r["name"])}</span>'
        f'<span class="bar"><i style="width:{r["value"]/maxact*100:.1f}%"></i></span>'
        f'<span class="v">{fmt(r["value"])}</span></li>' for i, r in enumerate(a["activity"][:10]))
    cond_cards = "".join(
        f'<div class="cc"><h3>{e(c["name"])}</h3>'
        f'<dl><dt>施設数1位</dt><dd><b>{e(c["top_count"][0])}</b><span>{fmt(c["top_count"][1])}件</span></dd>'
        f'<dt>構成比1位</dt><dd><b>{e(c["top_share"][0])}</b><span>{c["top_share"][1]:.1f}%</span></dd>'
        f'<dt>全国</dt><dd><b>{fmt(c["national"])}件</b><span>平均 {c["national_share"]:.1f}%</span></dd></dl></div>'
        for c in a["cond"].values())

    def dcell(r, key):
        if not has_prev:
            return ""
        v = r[key]
        cls = "up" if v > 0 else "dn" if v < 0 else "z"
        return f'<td class="num {cls}">{signed(v)}</td>'

    head_d = '<th class="num" data-k="d_fac">増減</th>' if has_prev else ""
    trs = "".join(
        f'<tr><td>{e(r["name"])}</td><td class="num">{fmt(r["facilities"])}</td>{dcell(r, "d_fac")}'
        f'<td class="num">{fmt(r["sakatsu"])}</td><td class="num">{fmt(r["activity"])}</td><td class="num">{r["rank"]}</td>'
        + "".join(f'<td class="num">{fmt(r["cond"][k])}<small>{(r["cond"][k]/r["facilities"]*100 if r["facilities"] else 0):.1f}%</small></td>' for k in COND_ORDER)
        + "</tr>" for r in a["rows"])
    cond_th = "".join(f'<th class="num">{e(a["cond_names"][k])}</th>' for k in COND_ORDER)
    hist = json.dumps(a["history"], ensure_ascii=False)
    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    rep = {"{{DATE}}": a["date"], "{{TOTAL}}": fmt(a["total"]), "{{KPI_DIFF}}": kpi_diff, "{{KPI_PD}}": kpi_pd,
           "{{KPI_SUB}}": e(kpi_sub), "{{TEXT}}": e(text), "{{BARS}}": bars, "{{COND_CARDS}}": cond_cards,
           "{{HEAD_D}}": head_d, "{{COND_TH}}": cond_th, "{{ROWS}}": trs, "{{HISTORY}}": hist,
           "{{N_OBS}}": str(len(a["history"]))}
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    return tpl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--notes", help="考察段落（自由記述）を書いたテキストファイル")
    a_ = ap.parse_args()
    snaps = load_snapshots()
    a = analyze(snaps)
    notes = Path(a_.notes).read_text(encoding="utf-8") if a_.notes else ""
    text = share_text(a, notes)
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / f"{a['date']}.txt").write_text(text, encoding="utf-8")
    (ROOT / "index.html").write_text(render_html(a, text), encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
