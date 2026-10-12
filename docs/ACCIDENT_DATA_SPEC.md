# Spec dữ liệu tai nạn — phạm vi paper hiện tại

Cập nhật theo quyết định của Nghĩa ngày **12/10/2026**:
**bỏ phân loại mức độ minor/severe khỏi paper**.
Xem [phạm vi được lưu](PAPER_SCOPE.md).

## Mục đích

Dữ liệu dưới đây chỉ cần nếu tiếp tục kiểm chứng ứng dụng phát hiện/cảnh báo
tai nạn nhị phân và nhánh precision của C3. GT tracking vẫn là ưu tiên trước.
Dataset ảnh detection 5 class không thay thế GT sự kiện video.
Không yêu cầu nhãn mức độ, classifier severity hoặc confusion matrix 3 class.

Lưu video trong `data/raw/accidents/`, annotation trong
`data/annotations/accidents/`; cả hai được gitignore, không commit ảnh/nhãn.

## Clip có tai nạn

- Giữ video gốc và fps, ưu tiên CCTV giao thông đô thị VN; ghi rõ domain
  `cctv/dashcam/web` thay vì trộn các domain không có protocol.
- Bao gồm đoạn trước và sau sự kiện, ưu tiên ít nhất 5 giây mỗi phía.
- Ghi camera, clip nguồn và event ID để nhận diện cùng một vụ quay nhiều góc.
- Gán nhãn sự kiện xác minh được; trường hợp không rõ ghi `uncertain` và lý do,
  không tự ép thành positive hoặc negative.

Annotation sự kiện:

```csv
clip_id,event_id,label,start_frame,end_frame,note
```

`label`: `accident`, `no_accident` hoặc `uncertain` (không đưa uncertain vào
scoring chính khi chưa phân xử). Frame đánh số từ 1, start/end inclusive;
ghi onset khi sự kiện thực sự bắt đầu, không dùng toàn bộ clip làm onset.
Chốt convention kết thúc sự kiện và matching predicted/GT event trước khi
chấm; kiểm tra độ lệch frame và fps.

Nếu đánh giá localization/track vùng tai nạn, thêm box theo frame và track ID
theo MOT như [hướng dẫn GT](GT_ANNOTATION_GUIDE.md). Detector có class Accident
không đồng nghĩa mọi nhãn video đã đúng hoặc đầy đủ.

## Clip không tai nạn

Cần video bình thường để đo cảnh báo sai trên giờ video. Lấy hard negatives:
xe dừng đèn đỏ, chen lấn, rẽ cắt nhau, dắt xe, tắc đường; có điều kiện ánh sáng
khác nhau và đủ thời lượng. Ghi `no_accident` sau khi người xác minh đã xem
clip. Không suy ra negative chỉ vì detector không thấy class Accident.

## Metadata và chia tập

```csv
clip_id,event_id,camera_id,location,date,time_of_day,weather,width,height,fps,duration_s,source,domain,split,label
```

Chia theo nguồn/clip/event/camera, không chia ngẫu nhiên theo frame. Cùng vụ
ở nhiều camera hoặc các biến thể augmentation phải cùng split. Chốt
`splits.csv` trước training và tuning. Tỷ lệ tham khảo 70/15/15 chỉ dùng khi
số nhóm độc lập đủ hỗ trợ; báo tỷ lệ và số sự kiện thực tế theo class/domain.
Nguồn chưa xác minh không tự coi là evaluation độc lập. Kiểm tra overlap với
benchmark và dữ liệu training checkpoint trước khi báo số cho paper.

## Protocol đánh giá nếu giữ nhánh cảnh báo

- Precision/recall/F1 theo sự kiện với quy tắc temporal matching đã chốt.
- Cảnh báo sai/giờ video trên các clip âm tính có thời lượng xác minh.
- Độ trễ phát hiện so với onset, đồng thời báo các sự kiện bị bỏ sót.
- Ablation có/không C3 với cùng detector, dữ liệu, rule tạo sự kiện và alert
  cooldown. Chốt tham số trên val, không tuning trên test.
- Latency bao gồm detector và logic event thực sự chạy, không gửi Telegram
  thật trong benchmark.

Code runtime hiện vẫn có classifier severity legacy và điều kiện gating alert;
chưa có kết quả binary alert chỉ từ việc bỏ yêu cầu nhãn mức độ. Cần triển khai
và kiểm chứng riêng trước khi claim. Nếu chưa đủ dữ liệu/implementation,
giữ nhánh này là untested/future work và không điền số giả.

## Detector

Giữ 5 class `Accident, bus, car, motorcycle, truck`, ưu tiên checkpoint
`task=detect` vì pipeline sử dụng box. Lưu training config, phiên bản phần mềm,
dataset hash và provenance. Notebook Kaggle hiện dùng development split;
metric của nó không tự trở thành test độc lập.
