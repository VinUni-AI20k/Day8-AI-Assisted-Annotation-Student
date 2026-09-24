#!/usr/bin/env python3
"""Kiểm bài nộp Day 08 trước khi push lên GitHub. Thoát 0 = đủ điều kiện chấm."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from yolo_io import read_yolo  # noqa: E402
from lock_blind import valid_lock  # noqa: E402

K_MIN, K_MAX = 8, 16
REPORT_HEADINGS = ("## 1.", "## 2.", "## 3.", "## 4.", "## 5.")


def main() -> int:
    errors: list[str] = []
    rows = list(csv.DictReader(open(ROOT / "data" / "frames.csv", encoding="utf-8")))
    pool = {r["file"] for r in rows if r["split"] == "pool"}
    test = {r["file"] for r in rows if r["split"] == "test"}

    ref_meta = json.loads((ROOT / "data" / "test" / "reference.json").read_text(encoding="utf-8"))
    hash_path = ROOT / "data" / "test" / "label_hashes.json"
    if hash_path.exists():
        ref_hashes = json.loads(hash_path.read_text(encoding="utf-8"))
    else:
        ref_hashes = {}
        errors.append("thiếu data/test/label_hashes.json của bản phát hành")
    for name, n in ref_meta["boxes_per_image"].items():
        label_path = ROOT / "data" / "test" / "labels" / f"{Path(name).stem}.txt"
        try:
            got = len(read_yolo(label_path))
        except ValueError as exc:
            got = None
            errors.append(str(exc))
        if got is not None and got != n:
            errors.append(f"data/test/labels/{Path(name).stem}.txt có {got} box, bản gốc có {n} box. Không được sửa nhãn của tập kiểm thử")
        if not label_path.exists() or hashlib.sha256(label_path.read_bytes()).hexdigest() != ref_hashes.get(label_path.name):
            errors.append(f"data/test/labels/{label_path.name} khác bản phát hành; không sửa nhãn tập kiểm thử")

    rounds = sorted(
        int(m.group(1)) for d in (ROOT / "labels").glob("round*") if (m := re.fullmatch(r"round(\d+)", d.name))
    )
    if not rounds:
        errors.append("chưa có labels/round1/, tức là chưa hoàn thành vòng học chủ động nào")
    elif rounds != list(range(1, len(rounds) + 1)):
        errors.append(f"labels/ có các vòng {rounds}, nhưng các vòng phải liên tục từ vòng 1")

    seen: set[str] = set()
    cumulative = 0
    for r in rounds:
        d = ROOT / "labels" / f"round{r}"
        bj = d / "batch.json"
        if not bj.exists():
            errors.append(f"thiếu labels/round{r}/batch.json, hãy tạo bằng tools/pack_labels.py")
            continue
        files = json.loads(bj.read_text(encoding="utf-8"))["files"]
        if not K_MIN <= len(files) <= K_MAX:
            errors.append(f"vòng {r}: {len(files)} ảnh, cần {K_MIN}-{K_MAX}")
        boxes = 0
        for name in files:
            if name in test or name not in pool:
                errors.append(f"vòng {r}: {name} không phải ảnh pool")
            if name in seen:
                errors.append(f"vòng {r}: {name} đã gán ở vòng trước")
            seen.add(name)
            txt = d / f"{Path(name).stem}.txt"
            if not txt.exists():
                errors.append(f"vòng {r}: thiếu {txt.relative_to(ROOT)}")
                continue
            try:
                boxes += len(read_yolo(txt))
            except ValueError as exc:
                errors.append(str(exc))
        if boxes == 0:
            errors.append(f"vòng {r}: 0 box")
        cumulative += len(files)

        if r == 1:
            scan = ROOT / "reports" / "BLIND_SCAN.md"
            if not valid_lock():
                errors.append("thiếu khóa bản quét độc lập hoặc BLIND_SCAN.md đã đổi sau khi khóa")
            elif not any(name in scan.read_text(encoding="utf-8") for name in files):
                errors.append("BLIND_SCAN.md phải nêu một frame trong lô vòng 1")

        for need in (f"outputs/selection_round{r}.csv", f"outputs/round{r}_diff.json",
                     f"outputs/metrics_round{r}.json", f"outputs/compare_round{r}.jpg"):
            if not (ROOT / need).exists():
                hint = " (chạy notebook thêm một lần sau khi sửa nhãn vòng này)" if "metrics" in need or "compare" in need else ""
                errors.append(f"thiếu {need}{hint}")
        mpath = ROOT / "outputs" / f"metrics_round{r}.json"
        if mpath.exists():
            m = json.loads(mpath.read_text(encoding="utf-8"))
            if m.get("n_train_images") != cumulative:
                errors.append(
                    f"metrics_round{r}.json train trên {m.get('n_train_images')} ảnh, nhưng vòng 1..{r} có {cumulative} ảnh"
                )

    if not (ROOT / "outputs" / "metrics_round0.json").exists():
        errors.append("thiếu outputs/metrics_round0.json (cold start)")
    for need in ("outputs/selection_round1.jpg", "outputs/compare_round0.jpg", "outputs/round1_diff.md"):
        if not (ROOT / need).exists():
            errors.append(f"thiếu {need}")

    review = ROOT / "reports" / "REVIEW_LOG.csv"
    if not review.exists():
        errors.append("thiếu reports/REVIEW_LOG.csv (chép từ REVIEW_LOG_TEMPLATE.csv rồi ghi ca của bạn)")
    else:
        with review.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        names = {p.name for d in (ROOT / "labels").glob("round*") for p in d.glob("*.txt")}
        useful = [
            row for row in rows
            if row.get("frame_id", "") in {f"{Path(n).stem}.jpg" for n in names}
            and row.get("object", "").strip()
            and row.get("action", "") in {"accepted", "edited", "deleted", "added"}
            and row.get("rule_or_reason", "").strip()
        ]
        if len(useful) < 3:
            errors.append("REVIEW_LOG.csv cần ít nhất 3 ca truy được frame, vật, hành động và lý do")

    rationale = ROOT / "reports" / "SELECTION.md"
    if not rationale.exists() or "ĐIỀN" in rationale.read_text(encoding="utf-8"):
        errors.append("thiếu hoặc chưa điền reports/SELECTION.md")
    if not (ROOT / "reports" / "rounds_table.md").exists():
        errors.append("thiếu reports/rounds_table.md, hãy chạy python3 tools/summarize_rounds.py")

    report = ROOT / "reports" / "REPORT.md"
    if not report.exists():
        errors.append("thiếu reports/REPORT.md (chép từ reports/REPORT_TEMPLATE.md)")
    else:
        text = report.read_text(encoding="utf-8")
        if "ĐIỀN" in text:
            errors.append(f"REPORT.md còn {text.count('ĐIỀN')} chỗ ĐIỀN chưa điền")
        for h in REPORT_HEADINGS:
            if h not in text:
                errors.append(f"REPORT.md thiếu mục bắt đầu bằng '{h}'")

    if errors:
        print(f"{len(errors)} lỗi:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"Đủ định dạng: {len(rounds)} vòng, {cumulative} ảnh đã sửa nhãn. Lệnh này không chấm điểm.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
