"""Đọc / ghi nhãn YOLO detection một lớp `car`: `0 cx cy w h`, toạ độ chuẩn hoá 0..1.

Một box ở khắp nơi trong lab là một dict: cls, cx, cy, w, h (chuẩn hoá), cộng thêm
"conf" nếu box do model sinh.
"""

from __future__ import annotations

import math
from pathlib import Path

NAMES = ("car",)
IMAGE_EXTS = (".jpg", ".jpeg", ".png")


def image_size(path: Path) -> tuple[int, int]:
    from PIL import Image

    with Image.open(path) as im:
        return im.size


def read_yolo(path: Path) -> list[dict]:
    boxes = []
    if not path.exists():
        return boxes
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 5:
            raise ValueError(
                f"{path}:{lineno}: cần đúng 5 cột `0 cx cy w h`, gặp {len(parts)} "
                "(lab này không dùng polygon hay segmentation, hãy vẽ box chữ nhật)"
            )
        try:
            cls_id = int(parts[0])
            cx, cy, w, h = (float(v) for v in parts[1:])
        except ValueError as exc:
            raise ValueError(f"{path}:{lineno}: không phải số") from exc
        if cls_id != 0:
            raise ValueError(f"{path}:{lineno}: class id {cls_id} không hợp lệ, lab chỉ có một lớp `car` (id 0)")
        if not all(math.isfinite(v) for v in (cx, cy, w, h)):
            raise ValueError(f"{path}:{lineno}: toạ độ box phải là số hữu hạn")
        if w <= 0 or h <= 0:
            raise ValueError(f"{path}:{lineno}: box rộng/cao <= 0")
        eps = 1e-3
        if cx - w / 2 < -eps or cy - h / 2 < -eps or cx + w / 2 > 1 + eps or cy + h / 2 > 1 + eps:
            raise ValueError(f"{path}:{lineno}: box tràn ra ngoài ảnh")
        boxes.append({"cls": 0, "cx": cx, "cy": cy, "w": w, "h": h})
    return boxes


def write_yolo(boxes: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"0 {b['cx']:.6f} {b['cy']:.6f} {b['w']:.6f} {b['h']:.6f}" for b in boxes]
    path.write_text(("\n".join(lines) + "\n") if lines else "", encoding="utf-8")


def xyxy(box: dict) -> tuple[float, float, float, float]:
    return (box["cx"] - box["w"] / 2, box["cy"] - box["h"] / 2, box["cx"] + box["w"] / 2, box["cy"] + box["h"] / 2)


def iou(a: dict, b: dict) -> float:
    ax1, ay1, ax2, ay2 = xyxy(a)
    bx1, by1, bx2, by2 = xyxy(b)
    iw = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    ih = max(0.0, min(ay2, by2) - max(ay1, by1))
    inter = iw * ih
    if inter <= 0:
        return 0.0
    union = a["w"] * a["h"] + b["w"] * b["h"] - inter
    return inter / union if union > 0 else 0.0


def match_boxes(left: list[dict], right: list[dict], min_iou: float = 0.5):
    """Ghép 1-1 theo IoU giảm dần. Trả về list (i_left, i_right, iou)."""
    pairs = sorted(
        ((iou(a, b), i, j) for i, a in enumerate(left) for j, b in enumerate(right)),
        reverse=True,
    )
    used_l, used_r, matches = set(), set(), []
    for score, i, j in pairs:
        if score < min_iou:
            break
        if i in used_l or j in used_r:
            continue
        used_l.add(i)
        used_r.add(j)
        matches.append((i, j, score))
    return matches


def list_images(folder: Path) -> list[Path]:
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS)
