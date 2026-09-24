"""Đóng gói một lô ảnh cần gán nhãn (notebook gọi sau khi chọn frame).

Cấu trúc `to_label/roundN/` — mở được ngay bằng CVAT, AnyLabeling, hoặc sửa tay:

    batch.json            vòng mấy, model nào đề xuất, vì sao chọn từng frame (score)
    data.yaml, train.txt  đúng định dạng CVAT "Ultralytics YOLO Detection 1.0"
    images/train/*.jpg    ảnh cần gán
    images/train/*.json   pre-label dạng LabelMe — AnyLabeling mở là thấy box
    labels/train/*.txt    pre-label dạng YOLO — sửa ở đây nếu dùng CVAT / sửa tay
    prelabels/*.txt       bản gốc pre-label, KHÔNG sửa — dùng để đo bạn sửa bao nhiêu
    HUONG_DAN.txt         cách sửa nhãn
"""

from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path

from labelme_io import write_labelme
from yolo_io import image_size, write_yolo

GUIDE_TEXT = """LÔ ẢNH CẦN GÁN NHÃN, VÒNG {round}

Lab chỉ có một lớp `car`, gồm mọi phương tiện từ 4 bánh trở lên (xe con, SUV, bán tải,
xe van, xe tải, xe buýt). Mỗi xe được đánh dấu bằng một box chữ nhật ôm sát thân xe,
không tính vệt sáng của đèn pha trên mặt đường. Xe ở quá xa, chỉ còn hai chấm đèn (box cao
dưới khoảng 16 pixel), thì gán hay không đều được vì không được tính khi chấm điểm.

Các box có sẵn trong lô là nhãn gợi ý do mô hình đề xuất (độ tin cậy từ {conf}). Bạn cần:
  - xoá box sai: không phải xe, box trùng nhau, box ôm vệt đèn;
  - chỉnh lại box bị lệch;
  - thêm box cho xe mô hình bỏ sót, thường là xe nhỏ, xe màu tối hoặc xe bị che.

Công cụ gợi ý (không bắt buộc, dùng công cụ nào cũng được):
  AnyLabeling  https://github.com/vietanhdev/anylabeling
      Vào File > Open Dir, chọn thư mục images/train. Box gợi ý hiện sẵn từ file .json,
      bạn sửa trực tiếp, phần mềm tự lưu.
  CVAT         https://github.com/cvat-ai/cvat
      Tạo task với các ảnh trong images/train và nhãn `car`. Nén cả thư mục này thành
      file zip, rồi vào Upload annotations, chọn định dạng "Ultralytics YOLO Detection 1.0".
      Sửa xong, xuất lại cùng định dạng và lấy các file labels/train/*.txt.
  SAM, SAM 2   https://github.com/facebookresearch/segment-anything
               https://github.com/facebookresearch/sam2
      Có sẵn trong AnyLabeling (mục Auto) và CVAT (mục AI Tools), giúp kéo box sát thân
      xe nhanh hơn.

Sửa xong, chạy lệnh sau tại thư mục gốc của repo:
  python3 tools/pack_labels.py to_label/round{round}
Nếu sửa bằng CVAT, thêm tuỳ chọn --yolo-dir <thư mục labels/train do CVAT xuất ra>.
"""


def write_batch(
    round_no: int,
    selected: list[dict],
    scored: list[dict],
    pool_dir: Path,
    preds: dict[str, list[dict]],
    out_dir: Path,
    model_desc: str,
    strategy: str,
    k: int,
    min_gap_s: float,
    prelabel_conf: float,
) -> Path:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    img_dir = out_dir / "images" / "train"
    lbl_dir = out_dir / "labels" / "train"
    pre_dir = out_dir / "prelabels"
    for d in (img_dir, lbl_dir, pre_dir):
        d.mkdir(parents=True)

    files = [r["file"] for r in selected]
    for name in files:
        src = pool_dir / name
        shutil.copy2(src, img_dir / name)
        boxes = [b for b in preds.get(name, []) if b["conf"] >= prelabel_conf]
        stem = Path(name).stem
        write_yolo(boxes, lbl_dir / f"{stem}.txt")
        write_yolo(boxes, pre_dir / f"{stem}.txt")
        w, h = image_size(src)
        write_labelme(boxes, img_dir / name, w, h, img_dir / f"{stem}.json")

    (out_dir / "data.yaml").write_text("path: ./\ntrain: train.txt\nnames:\n  0: car\n", encoding="utf-8")
    (out_dir / "train.txt").write_text("".join(f"images/train/{n}\n" for n in files), encoding="utf-8")
    (out_dir / "HUONG_DAN.txt").write_text(GUIDE_TEXT.format(round=round_no, conf=prelabel_conf), encoding="utf-8")

    keep = ("file", "t_sec", "rank", "score", "U", "A", "D", "n_boxes", "n_ambiguous", "empty")
    manifest = {
        "round": round_no,
        "created": dt.datetime.now().isoformat(timespec="seconds"),
        "proposed_by": model_desc,
        "strategy": strategy,
        "k": k,
        "min_gap_s": min_gap_s,
        "prelabel_conf": prelabel_conf,
        "files": files,
        "selected": [{key: r[key] for key in keep} for r in selected],
        "pool_candidates": len(scored),
    }
    (out_dir / "batch.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_dir
