"""Ảnh so sánh cho báo cáo.

compare_grid: mỗi hàng một ảnh test, cột = tham chiếu | cold start | các round đã train.
Trên cột model: xanh lá = khớp tham chiếu (TP), đỏ = thừa (FP), vàng = tham chiếu bị bỏ sót
(FN), ở ngưỡng conf của det_eval.

selection_sheet: lưới thumbnail các frame vừa được chọn, kèm thời điểm và score.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from det_eval import CONF_THR, IOU_THR, _is_tiny
from yolo_io import iou

GREEN, RED, YELLOW, CYAN, WHITE = (40, 220, 60), (240, 50, 50), (255, 210, 0), (0, 200, 255), (255, 255, 255)


def _rect(draw, box, w, h, color, width=2):
    x1, y1 = (box["cx"] - box["w"] / 2) * w, (box["cy"] - box["h"] / 2) * h
    x2, y2 = (box["cx"] + box["w"] / 2) * w, (box["cy"] + box["h"] / 2) * h
    draw.rectangle([x1, y1, x2, y2], outline=color, width=width)


def _panel(image_path: Path, ref: list[dict], preds: list[dict] | None, title: str, size: tuple[int, int]) -> Image.Image:
    im = Image.open(image_path).convert("RGB").resize(size)
    w, h = im.size
    dr = ImageDraw.Draw(im)
    if preds is None:
        for r in ref:
            _rect(dr, r, w, h, CYAN)
        caption = f"{title}: {len(ref)} box"
    else:
        keep = sorted((p for p in preds if p["conf"] >= CONF_THR), key=lambda p: -p["conf"])
        used = [False] * len(ref)
        tp = fp = 0
        for p in keep:
            best, best_j = 0.0, -1
            for j, r in enumerate(ref):
                if not used[j]:
                    s = iou(p, r)
                    if s > best:
                        best, best_j = s, j
            if best >= IOU_THR:
                used[best_j] = True
                tp += 1
                _rect(dr, p, w, h, GREEN)
            elif not _is_tiny(p):
                fp += 1
                _rect(dr, p, w, h, RED)
        fn = 0
        for r, u in zip(ref, used):
            if not u and not _is_tiny(r):
                fn += 1
                _rect(dr, r, w, h, YELLOW, width=1)
        caption = f"{title}: TP {tp}  FP {fp}  FN {fn}"
    dr.rectangle([0, 0, w, 20], fill=(0, 0, 0))
    dr.text((6, 4), caption, fill=WHITE)
    return im


def compare_grid(
    images: list[Path],
    ref_by_image: dict[str, list[dict]],
    columns: list[tuple[str, dict[str, list[dict]]]],
    out_path: Path,
    panel_size: tuple[int, int] = (640, 360),
) -> None:
    pw, ph = panel_size
    ncol = 1 + len(columns)
    sheet = Image.new("RGB", (pw * ncol, ph * len(images)), (0, 0, 0))
    for row, img in enumerate(images):
        ref = ref_by_image[img.name]
        sheet.paste(_panel(img, ref, None, f"reference {img.stem}", panel_size), (0, row * ph))
        for col, (title, preds) in enumerate(columns, start=1):
            sheet.paste(_panel(img, ref, preds.get(img.name, []), title, panel_size), (col * pw, row * ph))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, quality=88)


def selection_sheet(images_dir: Path, rows: list[dict], out_path: Path, cols: int = 6, thumb: tuple[int, int] = (320, 180)) -> None:
    tw, th = thumb
    nrows = (len(rows) + cols - 1) // cols
    sheet = Image.new("RGB", (tw * cols, th * nrows), (0, 0, 0))
    for k, r in enumerate(rows):
        im = Image.open(images_dir / r["file"]).convert("RGB").resize(thumb)
        dr = ImageDraw.Draw(im)
        dr.rectangle([0, 0, tw, 18], fill=(0, 0, 0))
        dr.text((4, 3), f"{r['file']} t={r['t_sec']:.1f}s s={r['score']:.2f}", fill=WHITE)
        sheet.paste(im, ((k % cols) * tw, (k // cols) * th))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, quality=85)
