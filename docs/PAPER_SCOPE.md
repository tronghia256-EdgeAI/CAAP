# Phạm vi sau khi bắt đầu lại — 20/10/2026

Nghĩa yêu cầu loại GT tracking cũ và toàn bộ phần paper cũ khỏi repo để làm lại.
Quyết định này thay thế các kế hoạch GT, ROI, C1/C2/C3, deadline và bản thảo cũ.

## Trạng thái

- Chưa chốt câu hỏi nghiên cứu, phương pháp đóng góp, venue hoặc lịch nộp mới.
- Không còn GT tracking, ROI, pre-label, review sessions hoặc kết quả cũ trong
  cây làm việc; backup nằm ngoài repo, không tự lấy lại làm nguồn đánh giá.
- Giữ video gốc, dataset/nhãn train detector, detector hiện tại và provenance train.
- Giữ ByteTrack gốc và metrics như công cụ nền, không coi là contribution mới.
- Không còn pipeline C1/C2/C3, severity classifier, Telegram hoặc nhánh MAPPO.
- Severity vẫn ngoài phạm vi; giữ class detector `Accident` và canonical class IDs.

## Khi làm lại

Thiết kế mục tiêu, split camera/source, quy ước annotation và protocol trước
khi tạo GT/evaluation mới. Nguồn pre-label không phải ground truth; cần kiểm
tra completeness và identity độc lập với model được đánh giá. Chỉ việc dùng
model cũ tạo pre-label không tự chứng minh GT sai hoặc đúng.

Các metrics trong `training/detector/` mô tả lượt train/development cũ của detector,
không phải bằng chứng cho paper mới. Đợt reset chưa train, inference hay score mới.

Giới hạn công bố của đợt nghiên cứu trước vẫn giữ: commit local, chưa push hoặc
phát hành dữ liệu khi chưa có chỉ dẫn mới. Việc chuyển backup không rewrite Git history.
