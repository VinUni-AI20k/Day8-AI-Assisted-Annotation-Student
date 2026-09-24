# Hướng dẫn Day 8 theo từng bước

Mở file này cạnh [rubric](RUBRIC.md) và [quy tắc box](GUIDELINE_LABEL.md). Bài nộp là **của từng người**, kể cả khi bạn trao đổi với bạn học. AI và fine-tune chạy trên Colab; máy cá nhân chỉ cần trình duyệt, GitHub Desktop hoặc Git, và Python 3.9+ để kiểm/đóng gói file. Nếu dùng CVAT chương trình, bạn không phải cài CVAT trên máy.

## 0. Tạo repo và mở Colab (phút 0–25)

1. Từ repo mẫu chính thức của buổi học, chọn **Use this template → Create a new repository** với tài khoản của bạn và để repo bài làm **public**. Clone repo vừa tạo bằng GitHub Desktop hoặc `git clone`; đừng làm trên bản Download ZIP vì bản đó không push được.
2. Trong thư mục repo cá nhân, chạy `python3 tools/make_data_zip.py`. Windows có thể dùng `python`. Script chỉ dùng thư viện chuẩn và tạo `day8_data.zip` khoảng 17 MB. Đừng push ZIP này.
3. Mở [notebook Colab](notebooks/day8_active_learning.ipynb) bằng **File → Upload notebook**, chọn GPU nếu có. Ở ô cấu hình, điền `STUDENT_NAME`; giữ `AL_K = 12` và `STRATEGY = "uncertainty"` cho vòng bắt buộc. Chọn **Runtime → Run all** và tải `day8_data.zip` lên khi được hỏi.
4. Colab đánh giá model pretrained trên 20 ảnh test, chọn 12 ảnh từ pool rồi tải `day8_round0_out.zip`. Giải nén ZIP này vào **gốc repo cá nhân**; chọn merge thư mục `outputs/` và `to_label/`. Mở `outputs/compare_round0.jpg` và `outputs/selection_round1.jpg`.

Nếu không có GPU, Colab có thể chạy chậm; báo Lab Coach khi vượt mốc. [Google lưu ý GPU miễn phí không được bảo đảm](https://research.google.com/colaboratory/faq.html). Đừng sửa tham số hay chuyển kết quả của người khác thành bài mình để vượt mốc.

## 1. Nhìn ảnh trước khi xem nhãn AI (phút 25–40)

1. Chọn **một ảnh** trong `to_label/round1/images/train/`. Mở file `.jpg` trực tiếp bằng trình xem ảnh, **chưa mở nhãn `.txt`, `.json` hay task CVAT có pre-label**.
2. Chép `reports/BLIND_SCAN_TEMPLATE.md` thành `reports/BLIND_SCAN.md`. Ghi tên ảnh, số xe bạn thấy và hai vị trí dễ bỏ sót/vẽ sai. Đây là quan sát nhanh, không cần vẽ hết box.
3. Chạy `python3 tools/lock_blind.py`. File `reports/blind_lock.json` ghi mã hash. Giữ `BLIND_SCAN.md` nguyên vẹn từ đây. Nếu làm theo cặp, mỗi người khóa bản riêng trước khi trao đổi.

Bản quét không chứng minh bạn đúng hơn model; nó cho phép bạn đối chiếu quyết định độc lập với nhãn gợi ý sau đó.

## 2. Sửa pre-label trên 12 ảnh (phút 40–110)

Quy tắc chung: chỉ một class `car` cho xe từ 4 bánh trở lên. Với **từng ảnh**, tự kiểm theo thứ tự: thiếu xe → box sai class/không phải xe → box trùng → box lệch → trường hợp mơ hồ. Xem ví dụ trong [GUIDELINE_LABEL.md](GUIDELINE_LABEL.md). Đừng giữ nguyên toàn bộ nhãn AI chỉ vì box có confidence cao.

**CVAT local:** tạo task riêng với 12 ảnh trong `to_label/round1/images/train/`, label duy nhất `car`; upload annotations từ ZIP `to_label/round1/` ở định dạng **Ultralytics YOLO Detection 1.0**. **CVAT chương trình:** mở task riêng do Lab Coach cấp cho bạn; kiểm tra đủ 12 tên ảnh và pre-label trước khi sửa. Không dùng cùng một job để hai người ghi đè lên nhau. Nếu task chương trình chưa có sẵn, báo Lab Coach để cấp task/đường dự phòng.

Sau khi sửa, export task/job cùng định dạng **Ultralytics YOLO Detection 1.0**, không cần kèm ảnh. Giải nén ZIP export và tìm thư mục `labels/train/` (có thể là `train/labels/` tùy cấu trúc export). Mỗi ảnh phải có file `.txt` với class id `0` và năm cột `0 cx cy w h`. [CVAT ghi định dạng và cấu trúc này trong tài liệu chính thức](https://docs.cvat.ai/docs/dataset_management/formats/format-yolo-ultralytics/).

Nếu dùng AnyLabeling, mở `to_label/round1/images/train/`, sửa hình chữ nhật và lưu file `.json` cạnh ảnh. Nếu CVAT không vào được, báo Lab Coach rồi dùng đường này hoặc sửa YOLO `.txt` trực tiếp theo hướng dẫn, không bỏ lô.

Chép `reports/REVIEW_LOG_TEMPLATE.csv` thành `reports/REVIEW_LOG.csv`; thay dòng ví dụ bằng **ít nhất ba ca thật**. Ghi `round`, `frame_id`, mô tả vật, hành động `accepted`/`edited`/`deleted`/`added`, và lý do theo guideline. Ưu tiên ca cho thấy AI bỏ sót, box giả và một ca bạn giữ/sửa có căn cứ. Log dùng để giải thích bản nhãn cuối, không phải số điểm tự động theo số box bạn sửa.

## 3. Đóng gói nhãn và chạy lại Colab (phút 120–175)

Nếu sửa bằng CVAT:

```bash
python3 tools/pack_labels.py to_label/round1 --yolo-dir /duong/dan/cvat_export/labels/train
```

Nếu thư mục export là `train/labels`, trỏ `--yolo-dir` vào đúng thư mục ấy. Nếu sửa bằng AnyLabeling hoặc file YOLO trong `to_label/`, chạy `python3 tools/pack_labels.py to_label/round1`. Script kiểm tên ảnh, box và tạo `labels/round1/`, `outputs/round1_diff.json/.md`, rồi cập nhật `day8_data.zip`. Nếu báo lỗi, sửa file được nêu rồi chạy lại.

Trên Colab, chạy notebook lần thứ hai và tải **`day8_data.zip` mới** lên. Notebook nhận `labels/round1/`, fine-tune YOLO, đánh giá trên đúng 20 ảnh test và tải `day8_round1_out.zip`. Giải nén vào gốc repo cá nhân, **giữ lại các file `outputs/` vòng 0**, rồi mở `outputs/compare_round1.jpg`. Mức tăng AP50 không được bảo đảm với lô nhỏ; hãy quan sát ca nào tốt/xấu hơn.

Để làm vòng 2 khi còn thời gian, lặp lại bước 2–3 với `to_label/round2/`; không có điểm thưởng chỉ vì làm thêm vòng. Sau vòng sửa cuối, luôn chạy notebook lần nữa để tạo `metrics_roundN.json` tương ứng.

## 4. Giải thích và nộp (phút 175–225)

1. Chép `reports/SELECTION_TEMPLATE.md` thành `reports/SELECTION.md`. Xét 50 ứng viên đứng đầu trong `outputs/selection_round1.csv`, đề xuất top 5 nếu chỉ đủ công rà năm ảnh. Dùng CSV và contact sheet để giải thích ba frame model chọn và một frame khác; nêu tác động của điểm bất định, ảnh gần trùng và chi phí rà nhãn.
2. Chép `reports/REPORT_TEMPLATE.md` thành `reports/REPORT.md`; điền đủ năm mục. Phân biệt chất lượng **nhãn AI ban đầu**, **nhãn bạn đã sửa** và **model sau fine-tune**. Nhãn test do model khác tạo chưa được người rà; đừng gọi đó là chân lý tuyệt đối.
3. Notebook Colab đã tạo `reports/rounds_table.md` trong ZIP kết quả. Sau khi giải nén, chạy `python3 tools/check_submission.py` trên máy cá nhân; lệnh này chỉ kiểm gói nộp, không chấm điểm. Sửa mọi lỗi định dạng được báo.
4. Dùng GitHub Desktop **Commit to main → Push origin** hoặc Git CLI. Kiểm tra trên trình duyệt rằng repo bài làm đang **public** và các đường dẫn trong [gói nộp](README.md#gói-nộp-duy-nhất) xuất hiện. Tải kết quả từ Colab về máy trước khi phiên ngắt; Colab không phải chỗ lưu bài cuối cùng.

## Khi gặp sự cố

| Sự cố | Cách xử lý |
| --- | --- |
| CVAT chương trình chưa có task riêng | Báo Lab Coach; không sửa job chung. Có thể dùng CVAT local hoặc đường file YOLO khi được hướng dẫn. |
| CVAT export không thấy `labels/train` | Tìm `train/labels`; kiểm đúng **Ultralytics YOLO Detection 1.0**, không chọn Segmentation hoặc YOLO 1.1. |
| Colab mất phiên | Tải lại `day8_data.zip` mới nhất rồi chạy notebook; giữ ZIP và repo đã push trên máy. |
| `check_submission.py` báo thiếu metrics vòng cuối | Chạy notebook thêm một lần sau khi đóng gói nhãn vòng cuối. |
| Số đo thấp hoặc AP50 giảm | Kiểm ảnh, nhãn và log; giải thích bằng chứng. Không chỉnh test label hoặc file số đo. |
