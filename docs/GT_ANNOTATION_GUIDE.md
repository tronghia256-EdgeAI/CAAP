# Quy ước annotation đang dùng

Đọc [workflow hiện tại](GT_REVIEW_WORKFLOW.md) để mở đúng camera/phiên.
Trang này giữ quy ước gán nhãn, không dùng kết quả C2 cũ để hướng người review.

## Đối tượng và box

- Xe máy gồm xe và người ngồi trên xe, theo quy ước detector đã dùng.
- Giữ các class hiện có; không đổi thứ tự class ID hoặc thêm severity.
- Với vật thể còn quan sát được, sửa box theo quy ước thống nhất của phiên;
  không để box gộp hai xe hoặc trùng cùng một xe.
- Quy ước lịch sử NKKN bỏ vật thể nhỏ hơn khoảng 8 px hoặc không nhận dạng
  được class. Không tự thay ngưỡng này sau khi xem metric; ghi rõ phạm vi và
  quy tắc áp dụng cho GT mới trước khi chấm.
- Xe đỗ nhìn thấy trong vùng được gán nhãn theo cùng quy tắc membership.

## Identity và che khuất

- Cùng một xe giữ ID trong các frame nhìn thấy và khi tái xuất hiện nếu có
  bằng chứng nhận dạng đủ rõ. Không merge chỉ vì quỹ đạo ở gần nhau.
- Không tạo box đoán trong khoảng che khuất hoàn toàn.
- Quan hệ ID không quan sát được phải đánh dấu chưa chắc để adjudication;
  quy tắc xử lý ambiguity trong evaluation cần được chốt trước khi chấm.

## Rà đầy đủ

Queue chỉ gợi ý lỗi; không phải danh sách đầy đủ mọi xe. Rà toàn bộ window
trên video gốc, gồm lượt tắt box để tìm xe mà mọi proposal bỏ sót. Kiểm tra
class, geometry, duplicate và ID transitions; giữ các trường hợp chưa chắc.
Union nhiều nguồn hoặc agreement với tracker không chứng minh GT trung lập.

## ROI, frame và lưu trữ

Giữ full GT/provenance và ROI riêng. Membership dùng tâm đáy box nằm trong
polygon, bao gồm biên; GT và predictions phải dùng cùng scope. Không di chuyển
ROI để làm đẹp số. MOT frame và source frame có offset khác nhau; kiểm mapping
trước khi sửa hoặc xuất. Giữ source và các phiên export cũ; không ghi đè.

GT Dương Bá Trạc hiện chỉ được xuất annotation, chưa mở score test.
Nếu cần CVAT, tham khảo [hướng dẫn lịch sử](../archive/docs/CVAT_CHEATSHEET.md)
về thao tác; phần ưu tiên/claim/lịch cũ không còn là chỉ dẫn hiện hành. Đợt dọn
repo không upload dữ liệu hoặc tạo task trên dịch vụ ngoài.
