# Phạm vi sau khi bắt đầu lại — 20/10/2026

Nghĩa yêu cầu loại GT tracking cũ và toàn bộ phần paper cũ khỏi repo để làm lại.
Quyết định này thay thế các kế hoạch GT, ROI, C1/C2/C3, deadline và bản thảo cũ.

## Câu hỏi nghiên cứu (chốt 20/10/2026)

**Seed bias trong ground truth MOT được gán nhãn với trợ giúp của tracker.** Khi GT được tạo bằng cách
review output của một tracker, GT đó thiên vị tracker seed bao nhiêu (IDF1, HOTA@0.5)? Bias phụ thuộc
vào recall của reviewer như thế nào, và ở mức nào thì thứ hạng giữa các tracker bị đảo? Protocol rẻ nào
(union seeding, blind adjudication vùng bất đồng, bracket bound) loại được bias này?

- "Sự thật" là GT công khai của FastTrack (traffic CCTV), MOT17 và DanceTrack. GT seed-rồi-review được
  mô phỏng từ output tracker và GT công khai, sau đó hiệu chỉnh bằng một human mini-study nhỏ
  (2 người, khoảng 3–4 giờ mỗi người, trên clip công khai đã có GT).
- Không cần tạo GT tracking mới, không cần thắng SOTA, không đo latency.
- Phát hiện seed bias trong đợt nghiên cứu trước chỉ được nhắc định tính, như quan sát dẫn tới câu hỏi.
  Không trích số, không khôi phục GT hay bằng chứng từ backup.
- Venue: Q1 theo SJR (Scopus). Ứng viên và lý do nằm trong `CLAUDE.md`. Quartile phải kiểm lại trên
  scimagojr.com trước khi nộp.
- Protocol, giả thuyết và quy tắc dừng: `docs/PROTOCOL.md`. Protocol phải được Nghĩa duyệt và đóng
  băng trước khi chạy bất kỳ thí nghiệm nào.

## Trạng thái

- Không còn GT tracking, ROI, pre-label, review sessions hoặc kết quả cũ trong
  cây làm việc; backup nằm ngoài repo, không tự lấy lại làm nguồn đánh giá.
- Giữ video gốc, dataset/nhãn train detector, detector hiện tại và provenance train.
  Video gốc không rõ link nguồn nên không phải testbed chính của paper mới.
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
