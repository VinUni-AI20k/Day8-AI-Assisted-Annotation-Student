#!/usr/bin/env python3
"""Gom outputs/metrics_round*.json thành bảng so sánh cold start và các vòng active learning.

Ghi reports/rounds_table.md — dán (hoặc giữ nguyên link) vào báo cáo. Số trong bảng đọc
thẳng từ file JSON notebook ghi ra, không chép tay.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_rounds() -> list[dict]:
    rows = []
    for f in ROOT.glob("outputs/metrics_round*.json"):
        m = re.fullmatch(r"metrics_round(\d+)\.json", f.name)
        if m:
            rows.append(json.loads(f.read_text(encoding="utf-8")))
    return sorted(rows, key=lambda r: r["round"])


def fmt(v):
    return "—" if v is None else f"{v:.3f}"


def table(rows: list[dict]) -> str:
    base = rows[0]["test"]["ap50"] if rows and rows[0]["round"] == 0 else None
    lines = [
        "| vòng | model | ảnh train | box train | AP50 | Δ AP50 so cold start | P@0.25 | R@0.25 | F1 | R small | R medium | R large |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in rows:
        t = r["test"]
        size = t["recall_by_size"]
        delta = "—" if base is None or r["round"] == 0 else f"{t['ap50'] - base:+.3f}"
        lines.append(
            f"| {r['round']} | {r['model']} | {r['n_train_images']} | {r['n_train_boxes']} | {fmt(t['ap50'])} | {delta} | "
            f"{fmt(t['precision'])} | {fmt(t['recall'])} | {fmt(t['f1'])} | "
            f"{fmt(size['small']['recall'])} | {fmt(size['medium']['recall'])} | {fmt(size['large']['recall'])} |"
        )
    return "\n".join(lines)


def main() -> int:
    rows = load_rounds()
    if not rows:
        raise SystemExit("Chưa có outputs/metrics_round*.json. Hãy chạy notebook ít nhất một lần.")
    ref = rows[0]["test"]
    text = "\n".join(
        [
            "# Bảng so sánh các vòng",
            "",
            f"Tập kiểm thử: {ref['images']} ảnh, {ref['ref_boxes']} box tham chiếu (bỏ qua "
            f"{ref['ref_ignored_tiny']} box cao dưới 16 px). Ngưỡng IoU 0.5; P, R, F1 tính tại conf 0.25.",
            "",
            table(rows),
            "",
        ]
    )
    out = ROOT / "reports" / "rounds_table.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"-> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
