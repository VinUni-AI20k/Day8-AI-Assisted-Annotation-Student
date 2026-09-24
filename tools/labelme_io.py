"""JSON kiểu LabelMe — định dạng AnyLabeling tự lưu cạnh mỗi ảnh (`<ảnh>.json`).

Notebook ghi sẵn pre-label thành file này để mở AnyLabeling là thấy box ngay. Sau khi bạn
sửa, `pack_labels.py` đọc lại file này và đổi về YOLO.
"""

from __future__ import annotations

import json
from pathlib import Path


def write_labelme(boxes: list[dict], image_path: Path, width: int, height: int, out_path: Path) -> None:
    shapes = []
    for b in boxes:
        x1 = (b["cx"] - b["w"] / 2) * width
        y1 = (b["cy"] - b["h"] / 2) * height
        x2 = (b["cx"] + b["w"] / 2) * width
        y2 = (b["cy"] + b["h"] / 2) * height
        shapes.append(
            {
                "label": "car",
                "points": [[round(x1, 1), round(y1, 1)], [round(x2, 1), round(y2, 1)]],
                "group_id": None,
                "shape_type": "rectangle",
                "flags": {},
            }
        )
    payload = {
        "version": "0.4.43",
        "flags": {},
        "shapes": shapes,
        "imagePath": image_path.name,
        "imageData": None,
        "imageHeight": height,
        "imageWidth": width,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_labelme(path: Path) -> tuple[list[dict], list[str]]:
    """Trả về (boxes, cảnh báo). Polygon được đổi thành box bao ngoài, kèm cảnh báo."""
    data = json.loads(path.read_text(encoding="utf-8"))
    width, height = float(data["imageWidth"]), float(data["imageHeight"])
    boxes, warnings = [], []
    for k, shape in enumerate(data.get("shapes", [])):
        label = str(shape.get("label", "")).strip().lower()
        if label != "car":
            warnings.append(f"{path.name}: shape {k} nhãn '{shape.get('label')}' không phải `car` — bỏ qua")
            continue
        pts = shape.get("points") or []
        if len(pts) < 2:
            warnings.append(f"{path.name}: shape {k} thiếu điểm — bỏ qua")
            continue
        kind = shape.get("shape_type", "rectangle")
        if kind not in ("rectangle", "polygon"):
            warnings.append(f"{path.name}: shape {k} kiểu '{kind}' — chỉ nhận rectangle/polygon, bỏ qua")
            continue
        if kind == "polygon":
            warnings.append(f"{path.name}: shape {k} là polygon — đã đổi thành box bao ngoài")
        xs = [float(p[0]) for p in pts]
        ys = [float(p[1]) for p in pts]
        x1, x2 = max(0.0, min(xs)), min(width, max(xs))
        y1, y2 = max(0.0, min(ys)), min(height, max(ys))
        if x2 - x1 < 1 or y2 - y1 < 1:
            warnings.append(f"{path.name}: shape {k} nhỏ hơn 1 px — bỏ qua")
            continue
        boxes.append(
            {
                "cls": 0,
                "cx": (x1 + x2) / 2 / width,
                "cy": (y1 + y2) / 2 / height,
                "w": (x2 - x1) / width,
                "h": (y2 - y1) / height,
            }
        )
    return boxes, warnings
