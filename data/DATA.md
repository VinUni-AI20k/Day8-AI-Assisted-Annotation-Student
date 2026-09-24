# Dữ liệu Lab Ngày 08

## Nguồn video

Dữ liệu lấy từ video YouTube "Cars driving at night" (mã `Ina7KMV2OEI`), độ phân giải 1920×1080,
30 khung hình mỗi giây, dài 160 giây. Camera đặt cố định trên cầu vượt, nhìn xuống đường cao tốc.
Toàn bộ video là một cảnh quay liên tục: công cụ ffmpeg không phát hiện lần cắt cảnh (scene cut)
nào, điểm thay đổi cảnh cao nhất chỉ là 0.08, trong khi một lần cắt cảnh thật thường trên 0.3. Nền
ảnh không đổi, chỉ có xe di chuyển qua.

**Trạng thái phân phối:** nguồn là video YouTube, nhưng việc một video xem công khai không tự xác
nhận quyền đưa các frame vào repo học viên public. Bản ghép này chỉ được công bố sau khi chủ sở hữu
dữ liệu/VinUni xác nhận quyền phân phối cho lớp.

## Trích xuất khung hình

Video được lấy mẫu 2.5 khung hình (frame) mỗi giây và thu nhỏ về 1280×720 bằng lệnh
`ffmpeg -vf fps=2.5,scale=1280:720`, thu được 400 ảnh từ `frame_0000.jpg` đến `frame_0399.jpg`.
Số thứ tự trong tên file cho biết vị trí của ảnh trên trục thời gian: ảnh thứ `i` nằm ở giây
`i / 2.5`. File `frames.csv` liệt kê đầy đủ thời điểm và tập dữ liệu của từng ảnh.

## Chia tập huấn luyện và tập kiểm thử theo thời gian

Vì camera đứng yên, hai ảnh cách nhau 0.4 giây gần như giống hệt nhau, và mỗi chiếc xe ở lại trong
khung hình vài giây. Nếu chia ngẫu nhiên, cùng một chiếc xe có thể nằm ở cả tập huấn luyện lẫn tập
kiểm thử. Khi đó mô hình được chấm trên những chiếc xe nó đã thấy, và số đo sẽ cao hơn thực tế. Đây
là hiện tượng rò rỉ dữ liệu (data leakage).

Để tránh điều này, dữ liệu được chia theo trục thời gian:

| Tập | Số ảnh | Cách lấy |
| --- | ---: | --- |
| Kiểm thử (test) | 20 | 4 đoạn có tâm ở giây 20, 60, 100 và 140; mỗi đoạn lấy 5 ảnh cách nhau 1.2 giây |
| Vùng đệm (buffer), bị loại bỏ | 112 | các ảnh trong khoảng 4 giây trước và sau mỗi đoạn kiểm thử, cùng các ảnh nằm xen giữa những ảnh kiểm thử |
| Chưa gán nhãn (pool) | 268 | toàn bộ các ảnh còn lại; học chủ động (active learning) chọn ảnh từ tập này |

Ảnh pool gần ảnh kiểm thử nhất vẫn cách nó 4.4 giây. Bạn có thể tự kiểm tra lại bằng `frames.csv`.

## Nhãn tham chiếu của tập kiểm thử

Các file `test/labels/*.txt` là nhãn tham chiếu dùng để chấm điểm, cùng định dạng YOLO với nhãn
bạn gán: mỗi dòng `0 cx cy w h`, toạ độ chuẩn hoá về khoảng 0 đến 1. Tập kiểm thử có 417 box trên
20 ảnh. Số box của từng ảnh được ghi trong `test/reference.json`.

Nhãn này do một mô hình phát hiện đối tượng tạo ra và **chưa được người rà từng box**. Vì vậy phép
đo cho biết mức khớp với bộ tham chiếu này; không phải thước đo tuyệt đối về nhãn đúng của con
người. Nếu ảnh so sánh cho thấy tham chiếu sai, ghi frame/vật/lý do trong báo cáo thay vì sửa
`test/labels/`.

Khi đọc số đo, cần lưu ý:

- Xe ở rất xa, sát đường chân trời, thường chỉ còn thấy hai chấm đèn nên rất khó gán nhãn nhất
  quán. Vì vậy, các box tham chiếu cao dưới 16 pixel (14 trên 417 box) được bỏ qua khi chấm. Dự
  đoán trùng với các box này không bị tính là phát hiện nhầm (false positive), bỏ sót chúng cũng
  không bị tính là bỏ sót (false negative). Dự đoán cao dưới 16 pixel mà không khớp với box nào
  cũng được bỏ qua. Xem chi tiết trong `tools/det_eval.py`.
- Tập kiểm thử chỉ có 20 ảnh, nên chênh lệch rất nhỏ giữa hai vòng (dưới khoảng 0.01 AP50) chưa đủ
  để kết luận mô hình tốt lên hay kém đi.

Không được chỉnh sửa `test/labels/`. Lệnh `check_submission.py` sẽ đối chiếu số box với
`test/reference.json`.
