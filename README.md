# Day 8 — kiểm nhãn AI và một vòng học chủ động

**Bản ghép thử nội bộ · 240 phút · bài nộp cá nhân, được trao đổi theo cặp.** Repo này là một luồng học viên duy nhất. Khi repo mẫu được công bố trong buổi học, mỗi học viên chọn **Use this template → Create a new repository**, để repo bài làm của mình **public** để hệ thống chấm đọc được.

## Bạn sẽ làm gì?

Trên video đường cao tốc ban đêm, mô hình YOLO đã huấn luyện sẵn bỏ sót một số xe. Bạn chạy mô hình trên Google Colab, xem vì sao nó chọn một lô ảnh từ pool chưa gán nhãn, **tự quan sát một ảnh trước khi xem nhãn AI**, sửa nhãn gợi ý, rồi dùng nhãn đã sửa để fine-tune. Cuối cùng bạn đánh giá trên cùng tập kiểm thử, so với lúc đầu và quyết định vòng sau nên làm gì.

Một vòng bắt buộc: **cold start → chọn 12 ảnh → kiểm/sửa pre-label → fine-tune → đánh giá → quyết định tiếp**. Làm thêm vòng chỉ là lựa chọn khi còn thời gian; số vòng và mức tăng AP50 không tự mang thêm điểm.

| Nơi làm | Công việc |
| --- | --- |
| **Colab** | Chạy YOLO, chọn ảnh, fine-tune và tạo số đo. Máy cá nhân không cần GPU. |
| **CVAT** | Máy thường dùng CVAT local; máy yếu dùng CVAT chương trình qua trình duyệt. Cả hai sửa cùng định dạng box `car` và xuất Ultralytics YOLO Detection 1.0. AnyLabeling hoặc sửa file YOLO là đường khác nếu cần. |
| **Máy cá nhân** | Chạy các script Python chỉ dùng thư viện chuẩn để khóa quan sát, kiểm và đóng gói nhãn; tải kết quả phân tích từ Colab về, commit rồi push repo public của mình. Không huấn luyện mô hình ở đây. |

Mọi người dùng cùng [quy tắc gán nhãn](GUIDELINE_LABEL.md), [hướng dẫn từng bước](GUIDE.md), [rubric 100 điểm](RUBRIC.md) và gói nộp. Làm cùng bạn được trao đổi sau khi mỗi người đã khóa bản quan sát độc lập; mỗi người vẫn tự sửa nhãn, phân tích và nộp repo riêng.

## Dữ liệu và giới hạn

- `data/pool/images/`: 268 ảnh chưa gán nhãn để chọn lô.
- `data/test/`: 20 ảnh và **nhãn tham chiếu do mô hình tạo**, dùng để minh họa phép so sánh. Chúng chưa được người rà từng box, vì vậy AP50 đo mức khớp với bộ tham chiếu này; nó không chứng minh chất lượng thực địa.
- Pool và test được tách theo thời gian với vùng đệm; xem [DATA.md](data/DATA.md). Không sửa nhãn test hoặc đưa ảnh test vào huấn luyện.
- Nguồn và quyền phân phối ảnh phải được người phụ trách dữ liệu xác nhận trước khi repo học viên được công bố public.

## Lộ trình 240 phút

| Phút | Việc | Bằng chứng |
| ---: | --- | --- |
| 0–25 | Tạo repo từ template, clone, đóng gói dữ liệu, mở Colab và chạy cold start | `outputs/metrics_round0.json`, `outputs/selection_round1.csv` |
| 25–40 | Xem một ảnh đã chọn khi chưa mở box AI; ghi và khóa quan sát | `reports/BLIND_SCAN.md`, `reports/blind_lock.json` |
| 40–110 | Sửa pre-label của 12 ảnh trên CVAT; ghi ít nhất 3 quyết định cụ thể | `reports/REVIEW_LOG.csv`, nhãn đã sửa |
| 110–120 | Nghỉ | |
| 120–145 | Export, đóng gói, kiểm định dạng và tải ZIP lên Colab | `labels/round1/`, `outputs/round1_diff.json` |
| 145–175 | Fine-tune, đo lại trên test, xem ảnh so sánh | `outputs/metrics_round1.json`, `outputs/compare_round1.jpg` |
| 175–205 | Giải thích chọn mẫu, kết quả và giới hạn; quyết định làm tiếp/dừng | `reports/SELECTION.md`, `reports/REPORT.md` |
| 205–225 | Kiểm gói nộp và push lên repo public của mình | `reports/rounds_table.md`, toàn bộ gói nộp |
| 225–240 | Dự phòng sự cố hoặc phân tích sâu hơn | Không bắt buộc vòng 2 |

Các mốc chỉ là kế hoạch cho bản ghép thử, cần được kiểm bằng thời gian thực của người mới và CVAT chương trình. Nếu Colab chưa cấp GPU hoặc CVAT không mở được, báo Lab Coach để dùng đường dự phòng; không sửa số đo hoặc bỏ qua nhãn để chạy kịp.

## Gói nộp duy nhất

Push các đường dẫn này lên repo public cá nhân:

1. `labels/round1/`: 8–16 ảnh pool có nhãn đã sửa và `batch.json` (mặc định 12 ảnh).
2. `outputs/metrics_round0.json`, `outputs/metrics_round1.json`, `outputs/selection_round1.csv`, `outputs/selection_round1.jpg`, `outputs/compare_round0.jpg`, `outputs/compare_round1.jpg`, `outputs/round1_diff.json` và `outputs/round1_diff.md`.
3. `reports/BLIND_SCAN.md`, `reports/blind_lock.json`, `reports/REVIEW_LOG.csv`, `reports/SELECTION.md`, `reports/rounds_table.md`, `reports/REPORT.md`.

`python3 tools/check_submission.py` kiểm **hình thức và tính nhất quán cơ bản**, không tự chấm điểm. Hệ thống chấm bài của chương trình sẽ đánh giá sau khi nhận repo. File `to_label/` và các ZIP trung gian không cần push; giữ chúng trên máy để khôi phục khi cần.
