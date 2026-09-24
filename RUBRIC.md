# Rubric Day 8 — 100 điểm

**Bản ghép thử cho học viên.** Hệ thống chấm của chương trình sẽ dùng bằng chứng trong repo public cá nhân. `python3 tools/check_submission.py` chỉ kiểm file và định dạng cơ bản; lệnh này không chấm điểm và không bảo đảm nhãn đúng. Lab Coach hỗ trợ thao tác, không tự cho điểm.

| Tiêu chí | Bằng chứng và cách phân điểm | Tối đa |
| --- | --- | ---: |
| **1. Cold start và chọn mẫu** | `metrics_round0.json` và `selection_round1.csv/.jpg` cho thấy đã chạy model trên pool/test đúng vai trò: **6**. `SELECTION.md` xét 50 ứng viên đầu, đề xuất top 5 theo ngân sách giả định năm ảnh, phân tích ba ảnh model chọn và một ảnh cân nhắc khác bằng điểm bất định, trùng cảnh, lý do: **9**. | **15** |
| **2. Rà và sửa nhãn AI** | `BLIND_SCAN.md` ghi quan sát độc lập có vật/vị trí cụ thể, khớp một ảnh trong lô và không đổi sau khi khóa: **5**. `labels/round1/` có đủ ảnh, box `car` đúng phạm vi và guideline; không giữ nguyên box sai hoặc bỏ sót xe rõ: **15**. `REVIEW_LOG.csv` truy được ít nhất ba ca giữ/sửa/xóa/thêm với lý do theo luật, đối chiếu được với `round1_diff.json`: **10**. | **30** |
| **3. Fine-tune và so sánh** | `metrics_round1.json` chứng minh đã train trên đúng lô đã sửa: **8**. `compare_round1.jpg` và `rounds_table.md` cho phép so trên cùng tập test, không lấy số train làm số test: **8**. Báo cáo giải thích một thay đổi hoặc không thay đổi có bằng chứng: **4**. | **20** |
| **4. Quyết định vòng tiếp theo** | Báo cáo chỉ ra hai ca còn yếu hoặc bất định, đề xuất chọn/không chọn tiếp và lý do: **8**. Nêu tác động của chi phí gán nhãn, ảnh gần trùng, tập test nhỏ và nhãn tham chiếu do model tạo: **7**. | **15** |
| **5. Báo cáo có nguồn** | `REPORT.md` đủ năm mục, số đo truy về file trong `outputs/`: **12**. Phân biệt lỗi nhãn AI ban đầu, nhãn đã sửa và chất lượng mô hình sau train; nêu giới hạn và tự QC: **8**. | **20** |
| **Tổng** | | **100** |

Điểm không tăng chỉ vì AP50 tăng, làm nhiều vòng hơn hoặc dùng GPU mạnh hơn. Với 8–16 ảnh train và 20 ảnh test, điểm AP50 có thể không tăng; việc đọc đúng kết quả vẫn có điểm. Người làm cá nhân và người trao đổi theo cặp có cùng rubric và nộp riêng.

`blind_lock.json` phát hiện nội dung `BLIND_SCAN.md` bị đổi sau lúc khóa trên máy, nhưng thời điểm trong file do học viên tạo; nó không tự chứng minh học viên chưa xem pre-label. Việc làm đúng thứ tự là yêu cầu tự khai của bài thực hành, không là kết luận kỹ thuật từ mã hash.

Ảnh test chỉ dùng để đánh giá. Nếu test xuất hiện trong `labels/round*/` hoặc nhãn test bị thay đổi, hệ thống chấm cần xử lý tính hợp lệ của phần so sánh. Bản chấm cuối cùng phải dựa trên cấu hình hệ thống do người phụ trách chấm triển khai; repo này chưa chứa bộ chấm điểm.
