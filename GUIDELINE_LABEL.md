# Quy tắc gán nhãn lớp `car`

Lab chỉ có một lớp, mã lớp (class id) là `0`. Mỗi chiếc xe được đánh dấu bằng một hộp giới hạn
(bounding box, gọi tắt là box) hình chữ nhật, cạnh song song với cạnh ảnh. Không dùng box xoay và
không dùng đa giác (polygon).

## Đối tượng được gán nhãn `car`

Mọi phương tiện từ 4 bánh trở lên: xe con (sedan, hatchback), SUV, bán tải, xe van, xe tải, xe
buýt, đầu kéo. Không gán nhãn cho xe máy, xe đạp hay người đi bộ (trong video này hầu như không có).

## Cách vẽ box trong từng tình huống

| Tình huống | Cách xử lý |
| --- | --- |
| Nhìn rõ thân xe | Vẽ box ôm sát thân xe, tính cả gương và đèn. Không tính vệt sáng của đèn pha chiếu xuống mặt đường phía trước xe. |
| Chỉ thấy đèn, thân xe tối nhưng vẫn đoán được đường viền | Vẽ box theo phần thân xe đoán được quanh cụm đèn, không chỉ khoanh hai chấm đèn. |
| Xe bị xe khác che một phần | Chỉ vẽ box cho phần nhìn thấy. |
| Xe bị cắt ở mép ảnh | Chỉ vẽ box cho phần nằm trong ảnh. |
| Hai xe đứng sát nhau | Vẽ hai box riêng, không gộp làm một. |
| Xe ở rất xa, chỉ còn hai chấm đèn, box cao dưới khoảng 16 pixel | Gán hay không đều được. Box cỡ này bị bỏ qua khi chấm điểm (xem `data/DATA.md`). |
| Ánh đèn phản chiếu trên mặt đường, biển báo phát sáng, đèn đường | Không gán nhãn. |
| Xe bị nhoè do chuyển động | Vẫn gán nhãn, box ôm vùng nhoè của thân xe. |

## Giữ cách gán nhất quán

Mô hình học trực tiếp từ các lô ảnh bạn sửa. Nếu cùng một kiểu xe mà ở ảnh này bạn vẽ box ôm cả
vệt đèn, ở ảnh khác lại không, mô hình sẽ học phải nhiễu. Khi gặp tình huống khó, hãy chọn một cách
xử lý, dùng cách đó cho mọi vòng, và ghi lại trong mục 4 của báo cáo.
