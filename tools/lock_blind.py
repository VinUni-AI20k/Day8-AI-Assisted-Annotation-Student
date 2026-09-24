#!/usr/bin/env python3
"""Freeze a learner's independent image scan before showing AI pre-labels."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN = ROOT / "reports" / "BLIND_SCAN.md"
LOCK = ROOT / "reports" / "blind_lock.json"


def scan_hash() -> str:
    return hashlib.sha256(SCAN.read_bytes()).hexdigest()


def valid_lock() -> bool:
    if not SCAN.exists() or not LOCK.exists():
        return False
    try:
        saved = json.loads(LOCK.read_text(encoding="utf-8"))
        return saved.get("sha256") == scan_hash()
    except (OSError, ValueError):
        return False


def main() -> int:
    if not SCAN.exists():
        print("Thiếu reports/BLIND_SCAN.md; chép từ reports/BLIND_SCAN_TEMPLATE.md trước.")
        return 1
    scan = SCAN.read_text(encoding="utf-8")
    if "ĐIỀN" in scan or "frame_" not in scan:
        print("Điền frame và quan sát trong BLIND_SCAN.md trước khi khóa.")
        return 1
    if LOCK.exists():
        print("Đã có blind_lock.json; giữ nguyên bản quét độc lập đã khóa.")
        return 1
    LOCK.write_text(
        json.dumps({"sha256": scan_hash(), "locked_at_utc": datetime.now(timezone.utc).isoformat()}, indent=2),
        encoding="utf-8",
    )
    print("Đã khóa bản quét độc lập. Bây giờ mở pre-label và sửa nhãn.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
