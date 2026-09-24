"""Chấm dự đoán `car` trên tập test so với nhãn tham chiếu.

Luật bỏ qua box nhỏ: xe ở sát chân trời chỉ còn hai chấm đèn nên khó gán nhãn nhất quán. Box
tham chiếu cao dưới MIN_BOX_H_PX (ảnh 1280x720) được đánh dấu "bỏ qua": dự đoán trùng vào nó
không bị tính FP, bỏ sót nó không bị tính FN. Dự đoán cao dưới ngưỡng mà không khớp gì cũng bị
bỏ qua.

- AP50: nội suy mọi điểm (VOC 2010+), IoU >= 0.5, dự đoán xếp theo conf giảm dần.
- P / R / F1 tại CONF_THR.
- Recall theo kích thước box tham chiếu (diện tích px): small < 32², medium < 96², large.
"""

from __future__ import annotations

from yolo_io import iou

IOU_THR = 0.5
CONF_THR = 0.25
MIN_BOX_H_PX = 16
IMG_W, IMG_H = 1280, 720


def _size_bucket(box: dict) -> str:
    area = box["w"] * IMG_W * box["h"] * IMG_H
    if area < 32 * 32:
        return "small"
    if area < 96 * 96:
        return "medium"
    return "large"


def _is_tiny(box: dict) -> bool:
    return box["h"] * IMG_H < MIN_BOX_H_PX


def match_image(ref: list[dict], preds: list[dict], conf_thr: float = 0.0):
    """Trả về (events, ref_hit). events: list (conf, is_tp) cho dự đoán không bị ignore."""
    valid = [r for r in ref if not _is_tiny(r)]
    ignore = [r for r in ref if _is_tiny(r)]
    used = [False] * len(valid)
    events = []
    for p in sorted((p for p in preds if p["conf"] >= conf_thr), key=lambda p: -p["conf"]):
        best, best_j = 0.0, -1
        for j, r in enumerate(valid):
            if used[j]:
                continue
            s = iou(p, r)
            if s > best:
                best, best_j = s, j
        if best >= IOU_THR:
            used[best_j] = True
            events.append((p["conf"], True))
        elif _is_tiny(p) or any(iou(p, r) >= IOU_THR for r in ignore):
            continue
        else:
            events.append((p["conf"], False))
    return events, list(zip(valid, used))


def average_precision(events: list[tuple[float, bool]], n_pos: int) -> float:
    if n_pos == 0:
        return 0.0
    events = sorted(events, key=lambda e: -e[0])
    tp = fp = 0
    precisions, recalls = [], []
    for _, is_tp in events:
        tp += is_tp
        fp += not is_tp
        precisions.append(tp / (tp + fp))
        recalls.append(tp / n_pos)
    mrec = [0.0] + recalls + [1.0]
    mpre = [0.0] + precisions + [0.0]
    for i in range(len(mpre) - 2, -1, -1):
        mpre[i] = max(mpre[i], mpre[i + 1])
    return sum((mrec[i + 1] - mrec[i]) * mpre[i + 1] for i in range(len(mrec) - 1))


def evaluate(ref_by_image: dict[str, list[dict]], pred_by_image: dict[str, list[dict]], conf_thr: float = CONF_THR) -> dict:
    all_events, n_pos, n_ignored = [], 0, 0
    tp = fp = 0
    size_hit = {"small": [0, 0], "medium": [0, 0], "large": [0, 0]}
    for name, ref in ref_by_image.items():
        preds = pred_by_image.get(name, [])
        n_ignored += sum(1 for r in ref if _is_tiny(r))
        ev, _ = match_image(ref, preds, 0.0)
        all_events += ev
        ev_thr, hits = match_image(ref, preds, conf_thr)
        n_pos += len(hits)
        tp += sum(1 for _, t in ev_thr if t)
        fp += sum(1 for _, t in ev_thr if not t)
        for box, hit in hits:
            bucket = size_hit[_size_bucket(box)]
            bucket[1] += 1
            bucket[0] += hit
    fn = n_pos - tp
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / n_pos if n_pos else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "images": len(ref_by_image),
        "ref_boxes": n_pos,
        "ref_ignored_tiny": n_ignored,
        "ap50": round(average_precision(all_events, n_pos), 4),
        "conf_thr": conf_thr,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "recall_by_size": {
            k: {"recall": round(h / n, 4) if n else None, "ref_boxes": n} for k, (h, n) in size_hit.items()
        },
    }
