"""Chọn frame cho một vòng active learning — Uncertainty Sampling + đa dạng theo thời gian.

Với mỗi frame chưa gán trong pool, model hiện tại dự đoán box `car` (conf >= 0.05):

    u(c) = 1 - |2c - 1|          # 1 khi c = 0.5 (model phân vân nhất), 0 khi c gần 0 hoặc 1

    U = trung bình 5 giá trị u lớn nhất của frame      (bất định của các box khó nhất)
    A = số box "mập mờ" 0.15 <= c < 0.50, chia cho max trong pool
    D = khoảng cách thời gian tới frame đã gán gần nhất, chặn ở DIVERSITY_CAP_S, chia cho cap
        (vòng đầu chưa có frame nào đã gán -> D = 1 cho mọi frame)

    score = W_U * U + W_A * A + W_D * D        (mặc định 0.5 / 0.3 / 0.2)

Frame không có box nào: U = A = 0 — camera này luôn có xe, frame trống là model bỏ sót hết;
cộng thêm EMPTY_BONUS để frame đó được xét.

Chọn tham lam theo score giảm dần, bỏ frame cách một frame đã chọn trong lô dưới MIN_GAP_S
giây (camera cố định, 2 frame gần nhau gần như trùng nhau — gán cả hai tốn công mà model học
thêm rất ít). Không đủ K frame thì nới khoảng cách một nửa rồi chọn tiếp.

`strategy="random"` chọn ngẫu nhiên có seed, cùng luật khoảng cách — dùng làm đối chứng.
"""

from __future__ import annotations

import random

CONF_FLOOR = 0.05
AMBIG_LO, AMBIG_HI = 0.15, 0.50
TOP_N = 5
DIVERSITY_CAP_S = 10.0
EMPTY_BONUS = 0.5
W_U, W_A, W_D = 0.5, 0.3, 0.2


def box_uncertainty(conf: float) -> float:
    return 1.0 - abs(2.0 * float(conf) - 1.0)


def score_frames(
    preds: dict[str, list[dict]],
    times: dict[str, float],
    labeled_times: list[float],
) -> list[dict]:
    rows = []
    for name, boxes in preds.items():
        confs = [float(b["conf"]) for b in boxes if float(b["conf"]) >= CONF_FLOOR]
        us = sorted((box_uncertainty(c) for c in confs), reverse=True)[:TOP_N]
        u = sum(us) / len(us) if us else 0.0
        n_amb = sum(1 for c in confs if AMBIG_LO <= c < AMBIG_HI)
        if labeled_times:
            gap = min(abs(times[name] - t) for t in labeled_times)
            d = min(gap, DIVERSITY_CAP_S) / DIVERSITY_CAP_S
        else:
            d = 1.0
        rows.append(
            {
                "file": name,
                "t_sec": times[name],
                "n_boxes": len(confs),
                "n_ambiguous": n_amb,
                "U": round(u, 4),
                "D": round(d, 4),
                "empty": not confs,
            }
        )
    max_amb = max((r["n_ambiguous"] for r in rows), default=0) or 1
    for r in rows:
        r["A"] = round(r["n_ambiguous"] / max_amb, 4)
        s = W_U * r["U"] + W_A * r["A"] + W_D * r["D"]
        if r["empty"]:
            s += EMPTY_BONUS
        r["score"] = round(s, 4)
    rows.sort(key=lambda r: (-r["score"], r["file"]))
    for rank, r in enumerate(rows, start=1):
        r["rank"] = rank
    return rows


def _greedy(order: list[dict], k: int, min_gap_s: float) -> list[dict]:
    picked: list[dict] = []
    gap = min_gap_s
    while len(picked) < k and gap >= 0.05:
        for r in order:
            if len(picked) >= k:
                break
            if r in picked:
                continue
            if all(abs(r["t_sec"] - p["t_sec"]) >= gap for p in picked):
                picked.append(r)
        gap /= 2
    for r in order:
        if len(picked) >= k:
            break
        if r not in picked:
            picked.append(r)
    return picked


def select_batch(
    scored: list[dict], k: int, min_gap_s: float = 2.0, strategy: str = "uncertainty", seed: int = 8
) -> list[dict]:
    if not 1 <= k <= len(scored):
        raise ValueError(f"k={k} ngoài khoảng 1..{len(scored)} frame còn trong pool")
    if strategy == "uncertainty":
        order = scored
    elif strategy == "random":
        order = list(scored)
        random.Random(seed).shuffle(order)
    else:
        raise ValueError("strategy phải là 'uncertainty' hoặc 'random'")
    picked = _greedy(order, k, min_gap_s)
    for r in scored:
        r["selected"] = any(r is p for p in picked)
    return sorted(picked, key=lambda r: r["t_sec"])
