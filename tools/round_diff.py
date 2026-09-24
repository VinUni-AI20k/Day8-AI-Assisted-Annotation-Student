"""Đo bạn đã sửa pre-label của model bao nhiêu trong một vòng: accepted / edited / deleted / added.

Ghép box giữa pre-label (model đề xuất, file gốc trong `prelabels/` của lô) và nhãn bạn đã
sửa, bằng IoU — không có id nào giữ nguyên giữa hai file.

- IoU >= 0.85: accepted (giữ gần như nguyên)
- 0.50 <= IoU < 0.85: edited (kéo lại box)
- box model có, bạn xoá: deleted (false positive của model)
- box bạn thêm, model không có: added (false negative của model)

Accept rate = accepted / (accepted + edited + deleted). 100% accepted, 0 added trên một lô
xe đêm đông đúc thường là dấu hiệu chưa nhìn kỹ ảnh.
"""

from __future__ import annotations

from yolo_io import match_boxes

ACCEPT_IOU = 0.85
MATCH_IOU = 0.50


def diff_boxes(pre_by_image: dict[str, list[dict]], fixed_by_image: dict[str, list[dict]]) -> dict:
    totals = {"accepted": 0, "edited": 0, "deleted": 0, "added": 0}
    per_image = {}
    for name in sorted(fixed_by_image):
        pre = pre_by_image.get(name, [])
        fixed = fixed_by_image[name]
        matches = match_boxes(pre, fixed, MATCH_IOU)
        acc = sum(1 for _, _, s in matches if s >= ACCEPT_IOU)
        row = {
            "accepted": acc,
            "edited": len(matches) - acc,
            "deleted": len(pre) - len(matches),
            "added": len(fixed) - len(matches),
            "prelabel_boxes": len(pre),
            "final_boxes": len(fixed),
        }
        per_image[name] = row
        for k in totals:
            totals[k] += row[k]
    judged = totals["accepted"] + totals["edited"] + totals["deleted"]
    return {
        "images": len(fixed_by_image),
        "match_iou": MATCH_IOU,
        "accept_iou": ACCEPT_IOU,
        "totals": {
            **totals,
            "prelabel_boxes": sum(r["prelabel_boxes"] for r in per_image.values()),
            "final_boxes": sum(r["final_boxes"] for r in per_image.values()),
            "accept_rate": round(totals["accepted"] / judged, 4) if judged else None,
        },
        "per_image": per_image,
    }


def to_markdown(report: dict, round_no: int) -> str:
    t = report["totals"]
    rate = "—" if t["accept_rate"] is None else f"{t['accept_rate']:.0%}"
    lines = [
        f"# Vòng {round_no} — bạn đã sửa pre-label bao nhiêu",
        "",
        f"{report['images']} ảnh. Model đề xuất {t['prelabel_boxes']} box, sau khi sửa còn {t['final_boxes']} box.",
        "",
        "| accepted | edited | deleted (FP của model) | added (FN của model) | accept rate |",
        "| ---: | ---: | ---: | ---: | ---: |",
        f"| {t['accepted']} | {t['edited']} | {t['deleted']} | {t['added']} | {rate} |",
        "",
        "| ảnh | model đề xuất | sau khi sửa | accepted | edited | deleted | added |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, r in report["per_image"].items():
        lines.append(
            f"| {name} | {r['prelabel_boxes']} | {r['final_boxes']} | {r['accepted']} | {r['edited']} | {r['deleted']} | {r['added']} |"
        )
    lines.append("")
    return "\n".join(lines)
