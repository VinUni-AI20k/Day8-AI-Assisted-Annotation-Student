#!/usr/bin/env python3
"""Thu nhãn bạn vừa sửa trong một lô, kiểm, lưu vào repo, rồi đóng gói lại để upload Colab.

    python3 tools/pack_labels.py to_label/round1
    python3 tools/pack_labels.py to_label/round1 --yolo-dir ~/Downloads/cvat_export/labels/train

Nguồn nhãn cho từng ảnh (`--source auto`, mặc định):
  - có `--yolo-dir`  -> lấy `<yolo-dir>/<ảnh>.txt` (ví dụ CVAT export)
  - file AnyLabeling `images/train/<ảnh>.json` mới hơn `labels/train/<ảnh>.txt` -> lấy JSON
  - còn lại -> `labels/train/<ảnh>.txt`

Kết quả:
  labels/roundN/*.txt, labels/roundN/batch.json    nhãn đã sửa — nộp lên GitHub
  outputs/roundN_diff.json, .md                    bạn sửa pre-label bao nhiêu
  day8_data.zip                                    upload file này lên Colab
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from labelme_io import read_labelme  # noqa: E402
from make_data_zip import build as build_zip  # noqa: E402
from round_diff import to_markdown, diff_boxes  # noqa: E402
from yolo_io import read_yolo, write_yolo  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def load_fixed(batch: Path, name: str, source: str, yolo_dir: Path | None):
    stem = Path(name).stem
    txt = batch / "labels" / "train" / f"{stem}.txt"
    js = batch / "images" / "train" / f"{stem}.json"
    if yolo_dir is not None:
        return read_yolo(yolo_dir / f"{stem}.txt"), [], "yolo-dir", (yolo_dir / f"{stem}.txt").exists()
    use_json = source == "labelme" or (
        source == "auto" and js.exists() and (not txt.exists() or js.stat().st_mtime > txt.stat().st_mtime + 1.0)
    )
    if use_json:
        boxes, warns = read_labelme(js)
        return boxes, warns, "anylabeling-json", True
    return read_yolo(txt), [], "yolo-txt", txt.exists()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("batch", type=Path, help="thư mục lô, ví dụ to_label/round1")
    p.add_argument("--source", choices=["auto", "yolo", "labelme"], default="auto")
    p.add_argument("--yolo-dir", type=Path, default=None)
    p.add_argument("--allow-empty", action="store_true", help="cho phép ảnh 0 box (camera này gần như luôn có xe)")
    args = p.parse_args()

    manifest = json.loads((args.batch / "batch.json").read_text(encoding="utf-8"))
    round_no = manifest["round"]
    files = manifest["files"]
    pool = {f.name for f in (ROOT / "data" / "pool" / "images").glob("*.jpg")}
    test = {f.name for f in (ROOT / "data" / "test" / "images").glob("*.jpg")}

    errors, warnings, fixed, pre, sources = [], [], {}, {}, {}
    for name in files:
        if name in test or name not in pool:
            errors.append(f"{name}: không phải ảnh pool (ảnh test không được gán để train)")
            continue
        try:
            boxes, warns, src, exists = load_fixed(args.batch, name, args.source, args.yolo_dir)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not exists:
            errors.append(f"{name}: không tìm thấy file nhãn")
            continue
        if not boxes and not args.allow_empty:
            errors.append(f"{name}: ảnh có 0 box, có thể chưa được gán nhãn (thêm --allow-empty nếu ảnh thật sự không có xe)")
        warnings += warns
        fixed[name] = boxes
        sources[name] = src
        pre[name] = read_yolo(args.batch / "prelabels" / f"{Path(name).stem}.txt")

    for w in warnings:
        print(f"  cảnh báo: {w}")
    if errors:
        print(f"Có {len(errors)} lỗi, chưa lưu gì:")
        for e in errors:
            print(f"  - {e}")
        return 1

    out_dir = ROOT / "labels" / f"round{round_no}"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    for name, boxes in fixed.items():
        write_yolo(boxes, out_dir / f"{Path(name).stem}.txt")
    manifest["label_sources"] = sources
    (out_dir / "batch.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    report = diff_boxes(pre, fixed)
    outputs = ROOT / "outputs"
    outputs.mkdir(exist_ok=True)
    (outputs / f"round{round_no}_diff.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (outputs / f"round{round_no}_diff.md").write_text(to_markdown(report, round_no), encoding="utf-8")

    t = report["totals"]
    print(
        f"vòng {round_no}: {len(fixed)} ảnh, {t['final_boxes']} box "
        f"(model đề xuất {t['prelabel_boxes']}: accepted {t['accepted']}, edited {t['edited']}, "
        f"deleted {t['deleted']}, added {t['added']})"
    )
    if t["prelabel_boxes"] and t["edited"] == 0 and t["deleted"] == 0 and t["added"] == 0:
        print("  CẢNH BÁO: bạn chưa sửa box nào so với nhãn gợi ý. Hãy mở lại ảnh và kiểm tra kỹ trước khi tải lên.")
    print(f"-> {out_dir.relative_to(ROOT)}/")
    build_zip()
    print(f"Tải day8_data.zip lên Colab rồi chạy notebook; notebook sẽ tự nhận ra đã có vòng 1 đến {round_no}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
