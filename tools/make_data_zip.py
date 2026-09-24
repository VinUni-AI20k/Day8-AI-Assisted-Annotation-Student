#!/usr/bin/env python3
"""Đóng gói `day8_data.zip` để upload lên Colab ở mỗi lần chạy notebook.

Zip gồm: dữ liệu (pool + test + nhãn tham chiếu), tools/, mọi nhãn bạn đã sửa trong
labels/round*/, và lịch sử số đo outputs/metrics_round*.json. Notebook không nhớ gì giữa các
lần chạy — mọi thứ nó cần nằm trong zip này, nên Colab có ngắt kết nối cũng chỉ cần upload lại.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = [
    "data/frames.csv",
    "data/test/reference.json",
    "data/test/label_hashes.json",
    "data/pool/images/*.jpg",
    "data/test/images/*.jpg",
    "data/test/labels/*.txt",
    "tools/*.py",
    "labels/round*/*.txt",
    "labels/round*/batch.json",
    "outputs/metrics_round*.json",
]


def build(out: Path | None = None) -> Path:
    out = out or ROOT / "day8_data.zip"
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for pattern in INCLUDE:
            for f in sorted(ROOT.glob(pattern)):
                zf.write(f, f"day8/{f.relative_to(ROOT).as_posix()}")
                n += 1
    rounds = sorted({p.parent.name for p in ROOT.glob("labels/round*/batch.json")})
    print(f"{out.name}: {n} file, {out.stat().st_size / 2**20:.1f} MB, vòng đã gán: {', '.join(rounds) or '(chưa có)'}")
    return out


if __name__ == "__main__":
    build()
