"""Local learning dashboard (usability requirement H2, human eval 1).

Generates a single self-contained HTML file from the harness's local state:
per-KC accuracy, outcome history, recent prompts and their debt verdicts.
No external requests, no server; open the file in any browser.

Usage: python3 -m harness.dashboard  (writes learning/dashboard.html)
"""
from __future__ import annotations

import csv
import html
import json
from pathlib import Path

_STYLE = """
body{font-family:-apple-system,Segoe UI,sans-serif;margin:2rem;max-width:52rem}
h1{font-size:1.4rem} h2{font-size:1.05rem;margin-top:1.6rem}
table{border-collapse:collapse;width:100%} td,th{border:1px solid #ccc;padding:.4rem .6rem;text-align:left}
.bar{background:#4a7;color:#fff;padding:0 .3rem;border-radius:3px;display:inline-block}
.miss{background:#c66}
small{color:#666}
"""


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def build_dashboard(root: Path | str, out_path: Path | str | None = None) -> Path:
    root = Path(root)
    out = Path(out_path) if out_path else root / "learning" / "dashboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)

    prompts = _read_jsonl(root / "logs" / "prompts.jsonl")
    assessments = _read_jsonl(root / "logs" / "assessments.jsonl")
    seq_path = root / "kt" / "data" / "sequences.csv"
    rows = []
    if seq_path.exists():
        with seq_path.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

    parts = [f"<html><head><meta charset='utf-8'><title>oh-my-brain dashboard</title>"
             f"<style>{_STYLE}</style></head><body>",
             "<h1>oh-my-brain learning dashboard</h1>"]

    if not prompts and not rows:
        parts.append("<p>No data yet. Use the harness for a while and regenerate.</p>")
    else:
        # per-KC mastery table
        kc: dict[str, list[int]] = {}
        for r in rows:
            kc.setdefault(r["kc_id"], []).append(int(r["correct"]))
        if kc:
            parts.append("<h2>Knowledge components</h2><table>"
                         "<tr><th>KC</th><th>Attempts</th><th>Accuracy</th></tr>")
            for k in sorted(kc, key=int):
                v = kc[k]
                pct = round(100 * sum(v) / len(v))
                cls = "bar" if pct >= 50 else "bar miss"
                parts.append(f"<tr><td>KC {k}</td><td>{len(v)}</td>"
                             f"<td><span class='{cls}'>{pct}%</span></td></tr>")
            parts.append("</table>")
            parts.append("<h2>Outcome history</h2><p>" + " ".join(
                "&#9679;" if int(r["correct"]) else "&#9675;" for r in rows) +
                "<br><small>&#9679; correct &nbsp; &#9675; incorrect (chronological)</small></p>")
        if prompts:
            verdicts = {round(a.get("ts", 0), 1): a for a in assessments}
            parts.append("<h2>Recent prompts</h2><table>"
                         "<tr><th>Prompt</th><th>Debt score</th><th>Triggered</th></tr>")
            for p in prompts[-10:]:
                a = verdicts.get(round(p.get("ts", 0), 1), {})
                parts.append(
                    f"<tr><td>{html.escape(str(p.get('prompt',''))[:80])}</td>"
                    f"<td>{a.get('score','-')}</td><td>{a.get('trigger','-')}</td></tr>")
            parts.append("</table>")

    parts.append("<p><small>Generated locally by oh-my-brain; no data leaves this machine.</small></p>")
    parts.append("</body></html>")
    out.write_text("\n".join(parts), encoding="utf-8")
    return out


if __name__ == "__main__":
    print(build_dashboard(Path.cwd()))
